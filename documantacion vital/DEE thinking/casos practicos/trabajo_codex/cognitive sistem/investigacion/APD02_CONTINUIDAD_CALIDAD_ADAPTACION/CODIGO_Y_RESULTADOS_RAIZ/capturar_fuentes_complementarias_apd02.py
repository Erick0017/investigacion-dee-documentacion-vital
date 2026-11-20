"""Read-only source preservation, not a new physics test or startup attestation."""
import argparse,hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--sistema',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    s=a.sistema.resolve();out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False)
    files=[s/'gestionar.py']
    for name in ('app','capacidades'):files.extend(sorted((s/name).rglob('*.py')))
    rows=[]
    for f in files:
        if f.is_symlink():raise ValueError('No external links')
        relative=f.relative_to(s);target=out/'codigo'/relative;target.parent.mkdir(parents=True,exist_ok=True)
        digest=sha(f);shutil.copyfile(f,target)
        if sha(f)!=digest or sha(target)!=digest:raise ValueError('Source moved during capture')
        rows.append({'file':relative.as_posix(),'bytes':f.stat().st_size,'sha256':digest})
    report={'schema':'APD02.complementary_source_capture.v1','utc':datetime.now(timezone.utc).isoformat(),'files':rows,'native_ticks':0,
      'scope':'Exact current plain Python coordinator and dependencies. The ongoing controller startup capture checked only its declared file set, not every source in sistema. This complementary capture happened after owner load, and is NOT relabeled a startup hash. Root editing record has no actor-source change during this owner window. Final Full includes the complete exact source layer. No snapshots, databases, engine binaries or memories read/changed.'}
    (out/'MANIFIESTO.json').write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'files':len(rows),'bytes':sum(r['bytes']for r in rows),'manifest_sha256':sha(out/'MANIFIESTO.json'),'native_ticks':0}))
if __name__=='__main__':main()

