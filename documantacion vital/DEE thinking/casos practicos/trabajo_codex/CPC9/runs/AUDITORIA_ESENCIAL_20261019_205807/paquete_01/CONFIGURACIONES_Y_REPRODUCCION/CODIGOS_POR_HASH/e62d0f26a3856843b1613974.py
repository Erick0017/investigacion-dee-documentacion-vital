"""Runner records before evaluating; participant never reads targets/reports."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from run_count_access import physical,put,sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    cfg=json.loads(a.config.read_text(encoding='utf8'));a.out.mkdir(parents=True,exist_ok=False);frozen=a.out/'executed_source'
    for source in ('src/two_memory.py','src/integracion/quantity_core.py','run_two_memory.py','run_count_access.py'):
        dst=frozen/source;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/source,dst)
    sys.path.insert(0,str(frozen/'src'))
    from two_memory import TwoMemorySession
    index=[]
    for case in cfg['cases']:
        out=a.out/case['id'];out.mkdir();start=time.monotonic();s=TwoMemorySession.create(center=case.get('center',(30,30,30)),absorber=case.get('absorber','off_path'))
        s.curriculum(case['reference'],case['remembered_object'],case.get('omit'),case.get('unpaired',False),case.get('order','O_first'))
        m={'schema':'CPC9.two_memory.primary.v1','case':case,'configuration_sha256':sha(a.config),
           'source_sha256':{str(p.relative_to(frozen)):sha(p)for p in frozen.rglob('*.py')},'geometry':s.geometry,
           'preparations':1,'forks':0,'continuations':0,'frames':[],'snapshots':[],'host_RAW_clock_edits':[],
           'scope':'Auxiliary two acquired operands, preparedcomparisonnotlearnedgeneralrule; noNSMpromotionautomatic','status':'RUNNING'}
        readers=s.geometry['protocol']['readers']
        boundaries={0,1,2,3,4,5,6,7,8,65,66,67,110,113,177,180,207}
        for reader in readers:boundaries.update((reader-2,reader-1,reader,reader+1,reader+2))
        for tick in sorted(boundaries):
            s.run_until(tick);m['frames'].append(s.capture())
            if tick in (0,5,readers[0]+1,207):
                path=out/('T'+str(tick)+'.deetsnap.gz');m['snapshots'].append({'path':path.name,'sha256':None,'storage':s.save(path),'physical':physical(s.world)});m['snapshots'][-1]['sha256']=sha(path)
            m['last_complete_tick']=tick;m['requests']=s.receipts();put(out/'MEASUREMENTS.json',m)
        m.update(status='MEASURED',elapsed_seconds=time.monotonic()-start);put(out/'MEASUREMENTS.json',m)
        summary={'id':case['id'],'sha256':sha(out/'MEASUREMENTS.json'),'responses':{str(f['tick']):{'reference':f['reference'],'object':f['object'],'center':f['center']}for f in m['frames']if f['tick']in{t for r in readers for t in (r,r+1)}}}
        index.append(summary);put(a.out/'INDEX.json',{'cases':index});print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
