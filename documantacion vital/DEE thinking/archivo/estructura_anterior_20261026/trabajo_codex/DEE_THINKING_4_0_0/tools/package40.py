"""Idempotent packaging of the sealed cut; never reruns experiments."""
import argparse,hashlib,json,os,shutil,sys,time,uuid,zipfile
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify40 import verify,sha
DIRS={'wheel','source','install_cpp','app','experiments','results','checkpoints','evidence','docs','tools','validation'}
ROOTS={'README.md','PRODUCT_CONTRACT.json','BUILD_PROVENANCE.json','VALIDATION_REPORT.json','EXPERIMENT_REPORT.md','PHENOMENA_AND_LANGUAGE.json','PARENTS.json','BUDGET.json','RESUMPTION_BUDGET.json','ACTIVE_BUDGET.json','supervise40.py','iniciar_mente.ps1'}
def files(root):
    for p in sorted(root.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(root)
        if any(x in {'__pycache__','.git','.venv','venv','build','dist','.pytest_cache'} or x.endswith('.egg-info') for x in rel.parts):continue
        if p.suffix in {'.pyc','.obj','.pdb','.ilk','.tmp'}:continue
        if rel.parts[0] in DIRS or rel.as_posix() in ROOTS:yield p
def seal(root):
    inventory=[{'path':p.relative_to(root).as_posix(),'size':p.stat().st_size,'sha256':sha(p)} for p in files(root) if not(p.parent==root and p.name in {'MANIFEST.json','HASHES.sha256'})]
    data={'schema':'DEE4.release.v1','generated_utc':datetime.now(timezone.utc).isoformat(),'scope':'all delivered files except MANIFEST.json and HASHES.sha256','files':inventory}
    (root/'MANIFEST.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=[x['sha256']+'  '+x['path'] for x in inventory]+[sha(root/'MANIFEST.json')+'  MANIFEST.json']
    (root/'HASHES.sha256').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return inventory
def package(root,destination,publish=False):
    inventory=seal(root);verify(root);destination.parent.mkdir(parents=True,exist_ok=True)
    temp=destination.with_name(destination.stem+'.'+uuid.uuid4().hex+'.temporary.zip')
    names=[x['path'] for x in inventory]+['MANIFEST.json','HASHES.sha256']
    try:
        with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
            for name in names:z.write(root/name,'DEE_thinking_4_0_0/'+name)
        with zipfile.ZipFile(temp) as z:
            assert z.testzip() is None
            for row in inventory:assert hashlib.sha256(z.read('DEE_thinking_4_0_0/'+row['path'])).hexdigest()==row['sha256'],row['path']
        digest=sha(temp);os.replace(temp,destination)
        return {'path':str(destination.resolve()),'sha256':digest,'size':destination.stat().st_size,'members':len(names),'CRC':True,'HASHES':True,'atomic_publish':True}
    except Exception:
        # Preserve the staging and diagnostic temporary for a bounded repackage.
        raise
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--destination',type=Path,required=True);a=p.parse_args();print(json.dumps(package(a.root,a.destination),indent=2))
