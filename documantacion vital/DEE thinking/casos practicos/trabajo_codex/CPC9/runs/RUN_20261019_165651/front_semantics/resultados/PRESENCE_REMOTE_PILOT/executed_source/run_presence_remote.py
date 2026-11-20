"""Remote acquisition runner; all causal events executed in one Runtime."""
import argparse,json,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from run_count_access import put,physical,sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf8'));a.out.mkdir(parents=True,exist_ok=False);frozen=a.out/'executed_source'
    for source in('src/presence_remote.py','src/presence_count.py','src/count_sign/session.py','src/relaciones/contact_cardinality.py','src/integracion/quantity_core.py','run_presence_remote.py','run_count_access.py'):
        dst=frozen/source;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/source,dst)
    sys.path.insert(0,str(frozen/'src'))
    from presence_remote import RemotePresenceSession
    from count_sign.session import move
    rows=[]
    for case in cfg['cases']:
        out=a.out/case['id'];out.mkdir();start=time.monotonic();s=RemotePresenceSession.create(case);s.curriculum(case.get('normalize',True),case.get('guard',True),case.get('transfer',True));m={'schema':'CPC9.presence_remote.primary.v1','case':case,'configuration_sha256':sha(a.config),'source_sha256':{str(p.relative_to(frozen)):sha(p)for p in frozen.rglob('*.py')},'preparations':1,'forks':0,'continuations':0,'geometry':s.geometry,'frames':[],'snapshots':[],'status':'RUNNING','host_RAW_clock_edits':[]}
        for t in(0,6,7,8,9,10,11,12,13,14,15,16,22,23,24,77,88,89,90,91,100,103,144,155,156,157,158,167,170,222,223,224,225):
            f=s.run_until(t);f['physical']=physical(s.world)
            if t in(11,12,14,15,22,23,88,89,90,155,156,157,222,223,224):
                centers=[b['capture12']if t<14 else b['spread15']if t<22 else b['reference_hub23']if t<88 else b['quantity']['center']for b in s.geometry['branches']]
                f['Moore27']=[{'center':q,'readings':[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}for q in centers]
            m['frames'].append(f)
            if t in(0,12,23,90,225):
                path=out/('T'+str(t)+'.deetsnap.gz');m['snapshots'].append({'path':path.name,'storage':s.save(path),'sha256':sha(path),'physical':physical(s.world)})
            m['last_complete_tick']=t;m['requests']=s.receipts();put(out/'MEASUREMENTS.json',m)
        m.update(status='MEASURED',elapsed_seconds=time.monotonic()-start);put(out/'MEASUREMENTS.json',m)
        summary={'id':case['id'],'sha256':sha(out/'MEASUREMENTS.json'),'comparisons':{str(f['tick']):f['remote']for f in m['frames']if f['tick']in(23,89,90,156,157,223,224)}};rows.append(summary);put(a.out/'INDEX.json',{'cases':rows});print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
