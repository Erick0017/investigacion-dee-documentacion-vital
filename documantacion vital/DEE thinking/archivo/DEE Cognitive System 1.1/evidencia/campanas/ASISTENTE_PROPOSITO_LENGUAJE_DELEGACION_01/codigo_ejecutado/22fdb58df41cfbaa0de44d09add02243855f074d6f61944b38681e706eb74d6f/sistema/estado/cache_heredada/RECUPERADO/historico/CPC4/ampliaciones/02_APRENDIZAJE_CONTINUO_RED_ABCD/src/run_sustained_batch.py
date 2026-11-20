"""Finite resumable component confirmation; no outcomes feed a participant."""
from pathlib import Path
import json,sys,time
from campaign import ROOT,put,sha
from supervision import run

def main():
    config=ROOT/'configuraciones/DUAL_SUSTAINED_CONFIRMATION.json';c=json.loads(config.read_text(encoding='utf-8'))
    folder=ROOT/'resultados/regulacion/DUAL_CONFIRMATION';folder.mkdir(parents=True,exist_ok=True)
    rows=[]
    for v in c['cases']:
        case={'second_phase':0,'horizon':520,'second_queries':[262,400],**v}
        cp=folder/(case['id']+'.json');cp_exists=cp.exists()
        if cp_exists:
            assert json.loads(cp.read_text(encoding='utf-8'))==case
        else:put(cp,case)
        out=folder/case['id'];measurement=out/'MEASUREMENTS.json'
        if measurement.exists():
            value=json.loads(measurement.read_text(encoding='utf-8'))
            assert value['case']==case and sha(out/'EXECUTED_SOURCE.py')==value['source_sha256']
            status='SKIPPED_VERIFIED_COMPLETED'
        else:
            job=run(ROOT,'sustained_'+case['id']+'_'+str(time.monotonic_ns()),[sys.executable,str(ROOT/'src/dual_sustained.py'),'--case',str(cp),'--output',str(out)],90,cwd=str(ROOT))
            if job['exit_code']!=0:
                rows.append({'id':case['id'],'status':'TECHNICAL_ERROR','job':job});put(folder/'RUN_SUMMARY.json',{'cases':rows});continue
            value=json.loads(measurement.read_text(encoding='utf-8'));status='MEASURED'
        rows.append({'id':case['id'],'status':status,'final_deltas':{k:r['delta'] for k,r in value['final']['memories'].items()},
                     'final_directions':{k:r['physical']['comparator']['direction'] for k,r in value['final']['memories'].items()},
                     'receipts':value['receipts'],'measurement':measurement.relative_to(ROOT).as_posix(),'sha256':sha(measurement)})
        put(folder/'RUN_SUMMARY.json',{'configuration_sha256':sha(config),'cases':rows,'scope':'8 worlds; repeated ticks are not independent replicas'})
    print(json.dumps({'cases':len(rows),'summary':str(folder/'RUN_SUMMARY.json')}))

if __name__=='__main__':main()
