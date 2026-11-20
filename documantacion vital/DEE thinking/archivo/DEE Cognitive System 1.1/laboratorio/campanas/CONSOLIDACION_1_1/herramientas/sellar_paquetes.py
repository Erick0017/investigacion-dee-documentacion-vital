"""Private packages. Originals are read-only; manifests have no self-hash."""
from pathlib import Path,PurePosixPath
from collections import Counter
from datetime import datetime,timezone
import argparse,hashlib,json,os,zipfile
ROOT=Path(__file__).resolve().parents[4]
PREFIX='DEE_COGNITIVE_SYSTEM_1_1'
SYSTEM='DEE_COGNITIVE_SYSTEM_1_1_SISTEMA.zip'
AUDIT='DEE_COGNITIVE_SYSTEM_1_1_AUDITORIA_ESENCIAL.zip'
SELECTED=['E1_SOCIAL_11','E1_11_ESTABLE','E1_CPC9_1907','E1_CPC9_884','E1_RECONSTRUIDO_11','R65_45_VIVIDO','R65_REVISION_11','R65_N67_VIVIDO','U0_14_VIVIDO']

def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def walk(root):
    for directory,dirs,files in os.walk(root,followlinks=False):
        dirs[:]=[x for x in dirs if x not in('__pycache__','node_modules','.entorno')and not(Path(directory)/x).is_junction()]
        for name in files:
            p=Path(directory)/name
            if p.suffix not in('.pyc','.lock'):yield p

def system_files(r):
    system=r/'sistema';snapshots=set();selected=set(SELECTED)
    for life in selected:
        d=read(system/'estado/vidas'/life/'VIDA.json');snapshots.add(str(d['snapshot']).replace('\\','/'))
        for p in(system/'estado/checkpoints').glob(life+'.*.gz'):snapshots.add(p.relative_to(system).as_posix())
        for p in(system/'estado/checkpoints').glob('import.'+life+'.*.gz'):snapshots.add(p.relative_to(system).as_posix())
    result=[]
    for p in walk(system):
        rel=p.relative_to(system);parts=rel.parts
        if 'cache_heredada'in parts or 'locks'in parts:continue
        if parts[:2]==('estado','vidas')and parts[2]not in selected:continue
        if parts[:2]==('estado','checkpoints')and rel.as_posix()not in snapshots:continue
        if rel.as_posix()=='capacidades/core/reproduccion/desde_cero.py':continue
        result.append(p)
    for name in('LEER_PRIMERO.md','USO_PRIVADO.md','PROVENANCE.json','PROYECTO.json','REANUDACION.json'):
        result.append(r/name)
    return sorted(set(result))

def audit_files(r):
    result=[];excluded=[]
    for directory in('evidencia','laboratorio'):
        for p in walk(r/directory):
            rel=p.relative_to(r).as_posix();keep=True;reason=None
            if p.suffix.lower()in('.whl','.pyd','.dll','.exe','.zip'):
                keep=False;reason='Motor/binary/toolchain not duplicated in audit'
            elif 'evidencia/verificaciones/HERENCIA_01/'in rel:
                # Original primaries, recovery reports and native transition
                # hashes remain. Large generated worlds stay deep in evidence.
                if p.suffix.lower()in('.deetsnap','.gz','.py'):
                    keep=False;reason='Regenerable auxiliary full state/source copy; original report and exact recovery route retained; see final regeneration comparison'
            elif 'evidencia/verificaciones/PERFILES_'in rel and '/Sistema limpio 'in rel:
                keep=False;reason='Disposable validation system copy, not primary scientific evidence'
            elif p.name=='TABLAS_PARA_EXPORTAR.json':keep=False;reason='Intermediate CSV authoring matrix; final CSV included'
            if keep:result.append(p)
            else:excluded.append({'file':rel,'bytes':p.stat().st_size,'sha256':digest(p),'reason':reason,'deleted':False})
    for name in('LEER_PRIMERO.md','USO_PRIVADO.md','PROVENANCE.json','PROYECTO.json','REANUDACION.json'):
        result.append(r/name)
    for p in(r/'sistema/documentacion').glob('*'):
        if p.is_file():result.append(p)
    for name in('NSM65_CATALOGO_OFICIAL.json','NSM65_ALCANCE_45.json'):
        result.append(r/'sistema/capacidades'/name)
    # Auxiliary complete states are evidence/laboratory resources. They are
    # never silently installed into the active operational store.
    return sorted(set(result)),excluded

def build(r,kind,output):
    files=system_files(r)if kind=='system'else audit_files(r)[0]
    if output.exists():raise FileExistsError('Sealed archive already exists; create another identified candidate')
    output.parent.mkdir(parents=True,exist_ok=True)
    if kind=='audit':
        _,excluded=audit_files(r);p=r/'evidencia/informes/EXCLUSIONES_DEL_PAQUETE.json';put(p,{'schema':'DCS1.1.audit.exclusions.v1','files':excluded,'bytes_excluded':sum(x['bytes']for x in excluded),'all_originals_remain':True,'coverage':'Essential primary JSON/JSONL, controls, failed cases, source identities, local RAW/clocks and all new diagnostic states retained; generated dense heritage outputs not claimed byte-for-byte included.'});files.append(p);files=sorted(set(files))
    rows=[{'path':p.relative_to(r).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)}for p in files]
    manifest_name='MANIFEST.json'if kind=='system'else'MANIFEST_AUDITORIA.json';hashes_name='HASHES.sha256'if kind=='system'else'HASHES_AUDITORIA.sha256'
    manifest={'schema':'DCS1.1.archive.manifest.v1','kind':kind,'version':'1.1.0','files':rows,'self_reference_rule':manifest_name+' and '+hashes_name+' excluded from their own member hash list; ZIP hash is external','expanded_payload_bytes':sum(x['bytes']for x in rows),'private':True}
    mb=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf8');hb=''.join(x['sha256']+'  '+x['path']+'\n'for x in rows).encode('utf8')
    before={x['path']:x['sha256']for x in rows}
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True)as z:
        for p in files:z.write(p,PREFIX+'/'+p.relative_to(r).as_posix())
        z.writestr(PREFIX+'/'+manifest_name,mb);z.writestr(PREFIX+'/'+hashes_name,hb)
    if any(digest(r/name)!=h for name,h in before.items()):raise ValueError('Payload changed while sealing archive')
    report={'file':output.name,'path':str(output),'sha256':digest(output),'bytes':output.stat().st_size,'members':len(rows)+2,'expanded_bytes':sum(x['bytes']for x in rows)+len(mb)+len(hb),'kind':kind}
    put(output.parent/(output.stem+'.SELLADO.json'),report);print(json.dumps(report));return report

def extract_verify(archive,out):
    if out.exists():raise FileExistsError('Clean extraction target already exists')
    out.mkdir(parents=True)
    with zipfile.ZipFile(archive)as z:
        names=z.namelist()
        if len(names)!=len(set(x.casefold()for x in names)):raise ValueError('Duplicate archive names')
        for name in names:
            q=PurePosixPath(name)
            if q.is_absolute()or'..'in q.parts or':'in name or not name.startswith(PREFIX+'/'):raise ValueError('Unsafe archive member')
        if z.testzip():raise ValueError('ZIP CRC failed')
        z.extractall(out)
    root=out/PREFIX;manifest_name='MANIFEST.json'if(root/'MANIFEST.json').exists()else'MANIFEST_AUDITORIA.json';hashes_name='HASHES.sha256'if manifest_name=='MANIFEST.json'else'HASHES_AUDITORIA.sha256';m=read(root/manifest_name);expected={x['path']for x in m['files']}|{manifest_name,hashes_name}
    actual={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}
    if actual!=expected:raise ValueError('Extraction inventory differs')
    for row in m['files']:
        p=root/row['path']
        if p.stat().st_size!=row['bytes']or digest(p)!=row['sha256']:raise ValueError('Extraction byte identity failed: '+row['path'])
    result={'archive':str(archive),'archive_sha256':digest(archive),'extracted_root':str(root),'files':len(actual),'all_member_hashes_equal':True,'CRC':'PASS'};put(out/'INTEGRIDAD_EXTRACCION.json',result);print(json.dumps(result));return result

def split(archive,limit=15999999):
    archive=Path(archive);parts=[]
    with archive.open('rb')as f:
        i=1
        while True:
            b=f.read(limit)
            if not b:break
            target=archive.with_name(archive.name+'.%03d'%i)
            with target.open('xb')as g:g.write(b)
            parts.append({'order':i,'name':target.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()});i+=1
    h=hashlib.sha256()
    for row in parts:
        with(archive.parent/row['name']).open('rb')as f:
            for b in iter(lambda:f.read(1048576),b''):h.update(b)
    if h.hexdigest()!=digest(archive):raise ValueError('Sequential reconstruction hash differs')
    return{'archive':archive.name,'sha256':digest(archive),'bytes':archive.stat().st_size,'parts':parts,'max_part_bytes_exclusive':16000000,'sequential_reconstruction_hash_equal':True}

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    q=sub.add_parser('build');q.add_argument('kind',choices=['system','audit']);q.add_argument('--root',type=Path,default=ROOT);q.add_argument('--out',type=Path)
    q=sub.add_parser('verify');q.add_argument('archive',type=Path);q.add_argument('--out',type=Path,required=True)
    q=sub.add_parser('parts');q.add_argument('archives',type=Path,nargs='+');q.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.command=='build':build(a.root,a.kind,a.out or a.root/'entregas'/(SYSTEM if a.kind=='system'else AUDIT))
    elif a.command=='verify':extract_verify(a.archive,a.out)
    else:put(a.out,{'schema':'DCS1.1.transport.parts.v1','archives':[split(x)for x in a.archives]})
if __name__=='__main__':main()
