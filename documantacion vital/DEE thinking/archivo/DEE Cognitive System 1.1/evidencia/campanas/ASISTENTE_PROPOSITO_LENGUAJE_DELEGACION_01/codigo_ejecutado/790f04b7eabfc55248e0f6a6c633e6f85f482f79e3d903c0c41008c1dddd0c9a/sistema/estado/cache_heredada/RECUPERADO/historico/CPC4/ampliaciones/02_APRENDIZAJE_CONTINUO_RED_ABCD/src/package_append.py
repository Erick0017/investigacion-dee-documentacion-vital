"""Append-only CPC4 sealing; never invokes experiments or old finalizers."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, os, shutil, sys, time, zipfile,ctypes
from datetime import datetime,timezone
from campaign import ROOT,PARENT,CANONICAL,PARENT_SHA,sha,put

SECTION='CPC4/ampliaciones/'+ROOT.name+'/'
EXCLUDED={'__pycache__','.venv','repro','staging'}

def payload():
    return sorted(p for p in ROOT.rglob('*') if p.is_file()
                  and not any(x in EXCLUDED for x in p.relative_to(ROOT).parts)
                  and not (len(p.relative_to(ROOT).parts)>1 and p.relative_to(ROOT).parts[0]=='jobs' and p.relative_to(ROOT).parts[1].startswith('publication_'))
                  and p.name not in {'MANIFEST.json','HASHES.sha256','DELIVERY.json'}
                  and not p.name.endswith(('.tmp','.pyc','.pyd','.whl')))

def seal():
    files=payload()
    rows=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
    put(ROOT/'MANIFEST.json',{'schema':'CPC4.A02.MANIFEST.v1','parent_zip_sha256':PARENT_SHA,
        'scope':SECTION,'excludes':['MANIFEST.json','HASHES.sha256'],
        'rule':'Manifest hashes payload; HASHES hashes payload and manifest; ZIP SHA outside ZIP.',
        'files':rows})
    files.append(ROOT/'MANIFEST.json')
    (ROOT/'HASHES.sha256').write_text(''.join(sha(p)+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in files),encoding='utf-8')
    return files+[ROOT/'HASHES.sha256']

def build(candidate):
    candidate=Path(candidate).resolve()
    if sha(CANONICAL)!=PARENT_SHA:raise RuntimeError('Concurrent parent update; refusing build against another cut')
    if candidate==CANONICAL.resolve():raise ValueError('Must build a distinct temporary candidate')
    files=seal()
    guide=('CPC4 — ampliación acumulativa02\n\n'
           'El informe y los manifiestos históricos se conservan sin cambios.\n'
           'La síntesis vigente, ejecución, demostrador y evidencias nuevas están en:\n\n'
           'ampliaciones/'+ROOT.name+'/LEEME.md\n'
           'ampliaciones/'+ROOT.name+'/INFORME.md\n\n'
           'Inicio: entrar en esa carpeta y ejecutar iniciar_cpc4.ps1.\n'
           'No se sustituyó el instrumento DEE thinking4.0.0 ni kernel v27.\n')
    index={'schema':'CPC4.extension_index.02','parent_sha256':PARENT_SHA,
           'historical_report':'INFORME.md','historical_manifest':'MANIFEST.json',
           'current_extension':'ampliaciones/'+ROOT.name,
           'current_report':'ampliaciones/'+ROOT.name+'/INFORME.md',
           'current_capabilities':'ampliaciones/'+ROOT.name+'/CAPACIDADES.json',
           'new_hash_scope':'HASHES_AMPLIACION_02.sha256'}
    extras={'CPC4/ACTUALIZACION_02.md':guide.encode('utf-8'),
            'CPC4/INDICE_AMPLIACIONES_02.json':json.dumps(index,ensure_ascii=False,indent=2).encode('utf-8')}
    extra_hashes=[sha(p)+'  '+(SECTION+p.relative_to(ROOT).as_posix()).removeprefix('CPC4/') for p in files]
    extra_hashes += [hashlib.sha256(b).hexdigest()+'  '+n.removeprefix('CPC4/') for n,b in extras.items()]
    extras['CPC4/HASHES_AMPLIACION_02.sha256']=('\n'.join(extra_hashes)+'\n').encode('utf-8')
    with zipfile.ZipFile(CANONICAL) as old,zipfile.ZipFile(candidate,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True) as new:
        for i in old.infolist():
            if i.filename.startswith(SECTION):raise RuntimeError('Extension already exists in parent')
            with old.open(i) as source,new.open(i,'w',force_zip64=True) as target:shutil.copyfileobj(source,target,1024*1024)
        for p in files:new.write(p,SECTION+p.relative_to(ROOT).as_posix())
        for name,content in extras.items():
            if name in old.namelist():raise RuntimeError('Refusing to overwrite an inherited root member: '+name)
            new.writestr(name,content)
    return verify(candidate)

def verify(candidate):
    candidate=Path(candidate)
    inventory=json.loads((ROOT/'PARENT_MEMBERS.json').read_text(encoding='utf-8'))
    parent={r['path']:r for r in inventory['files']}
    with zipfile.ZipFile(candidate) as z:
        assert z.testzip() is None,'CRC'
        names=z.namelist();assert len(names)==len(set(names)),'duplicate members'
        for name in names:
            p=PurePosixPath(name);assert not p.is_absolute() and '..' not in p.parts,'unsafe member'
        for name,row in parent.items():
            h=hashlib.sha256()
            with z.open(name) as f:
                for b in iter(lambda:f.read(1048576),b''):h.update(b)
            assert h.hexdigest()==row['sha256'],name
        hashes=z.read(SECTION+'HASHES.sha256').decode('utf-8').splitlines()
        for line in hashes:
            expected,name=line.split('  ',1)
            assert hashlib.sha256(z.read(SECTION+name)).hexdigest()==expected,name
        manifest=json.loads(z.read(SECTION+'MANIFEST.json'))
        for row in manifest['files']:
            assert hashlib.sha256(z.read(SECTION+row['path'])).hexdigest()==row['sha256'],row['path']
        root_hashes=z.read('CPC4/HASHES_AMPLIACION_02.sha256').decode('utf-8').splitlines()
        for line in root_hashes:
            expected,name=line.split('  ',1)
            assert hashlib.sha256(z.read('CPC4/'+name)).hexdigest()==expected,name
        covered={'CPC4/'+line.split('  ',1)[1] for line in root_hashes}|{'CPC4/HASHES_AMPLIACION_02.sha256'}
        assert set(names)-set(parent)==covered,'Uncovered new member'
        for required in ['ejecutar.py','demostracion.py','INFORME.md','CAPACIDADES.json','REANUDACION.json','PROVENANCE.json']:
            assert SECTION+required in names,required
        snapshots=[n for n in names if n.startswith(SECTION) and n.endswith('.deetsnap')]
        assert snapshots,'No new checkpoints'
        result={'candidate':str(candidate),'zip_sha256':sha(candidate),'compressed_bytes':candidate.stat().st_size,
                'expanded_bytes':sum(i.file_size for i in z.infolist()),'members':len(names),
                'inherited_members_preserved_byte_exact':len(parent),'new_members':len(names)-len(parent),
                'crc_verified':True,'new_hashes_verified':len(hashes),'root_new_hashes_verified':len(root_hashes),'new_checkpoint_members':len(snapshots)}
    return result

def publish(candidate):
    result=verify(candidate)
    if sha(CANONICAL)!=PARENT_SHA:raise RuntimeError('Concurrent update detected; candidate retained, no overwrite')
    os.replace(candidate,CANONICAL)
    assert sha(CANONICAL)==result['zip_sha256']
    result['published']=str(CANONICAL)
    counter=ctypes.windll.kernel32.GetTickCount64;counter.restype=ctypes.c_ulonglong
    budget=json.loads((ROOT/'BUDGET.json').read_text(encoding='utf-8-sig'))
    result['total_elapsed_seconds']=(int(counter())-budget['monotonic_start_ms'])/1000
    result['publication_utc']=datetime.now(timezone.utc).isoformat()
    result['publication_control_logs']='Workspace jobs/publication_* are finalizer controls outside the frozen payload; no scientific attempt is excluded by this rule.'
    put(ROOT/'DELIVERY.json',result)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['build','verify','publish']);p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
    result={'build':build,'verify':verify,'publish':publish}[a.mode](a.candidate)
    print(json.dumps(result,ensure_ascii=False))
