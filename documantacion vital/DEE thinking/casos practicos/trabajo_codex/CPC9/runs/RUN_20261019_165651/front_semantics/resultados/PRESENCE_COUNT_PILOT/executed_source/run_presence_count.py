"""Record actual native presence normalization; no labels in participant."""
import argparse,json,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from run_count_access import put,physical,sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf8'));a.out.mkdir(parents=True,exist_ok=False);frozen=a.out/'executed_source'
    for source in('src/presence_count.py','src/count_sign/session.py','src/relaciones/contact_cardinality.py','src/integracion/quantity_core.py','run_presence_count.py','run_count_access.py'):
        dst=frozen/source;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/source,dst)
    sys.path.insert(0,str(frozen/'src'))
    from presence_count import PresenceCountSession
    from relaciones.contact_cardinality import move
    rows=[]
    for case in cfg['cases']:
        out=a.out/case['id'];out.mkdir();start=time.monotonic();s=PresenceCountSession.create(case);s.curriculum(case.get('normalize',True),case.get('guard',True));m={'schema':'CPC9.presence_count.primary.v1','case':case,'configuration_sha256':sha(a.config),'source_sha256':{str(p.relative_to(frozen)):sha(p)for p in frozen.rglob('*.py')},'preparations':1,'forks':0,'continuations':0,'geometry':s.geometry,'frames':[],'snapshots':[],'status':'RUNNING','host_RAW_clock_edits':[]}
        for t in(0,3,4,5,6,7,8,9,10,11,12,13,76,77,78,100,103,143,144,145,167,170,171):
            f=s.run_until(t);f['physical']=physical(s.world)
            if t in(7,8,9,10,76,77,143,144):
                centers=[n['center8']for n in s.geometry['normalizers']]+[s.geometry['collector']]
                f['Moore27']=[{'center':q,'readings':[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}for q in centers]
            m['frames'].append(f)
            if t in(0,8,10,77,171):
                path=out/('T'+str(t)+'.deetsnap.gz');m['snapshots'].append({'path':path.name,'storage':s.save(path),'sha256':sha(path),'physical':physical(s.world)})
            m['last_complete_tick']=t;m['requests']=s.receipts();put(out/'MEASUREMENTS.json',m)
        m.update(status='MEASURED',elapsed_seconds=time.monotonic()-start);put(out/'MEASUREMENTS.json',m)
        summary={'id':case['id'],'sha256':sha(out/'MEASUREMENTS.json'),'collector':{str(f['tick']):f['collector']for f in m['frames']if f['tick']in(10,77,144)},'emitters8':next(f['normalizers']for f in m['frames']if f['tick']==8)};rows.append(summary);put(a.out/'INDEX.json',{'cases':rows});print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
