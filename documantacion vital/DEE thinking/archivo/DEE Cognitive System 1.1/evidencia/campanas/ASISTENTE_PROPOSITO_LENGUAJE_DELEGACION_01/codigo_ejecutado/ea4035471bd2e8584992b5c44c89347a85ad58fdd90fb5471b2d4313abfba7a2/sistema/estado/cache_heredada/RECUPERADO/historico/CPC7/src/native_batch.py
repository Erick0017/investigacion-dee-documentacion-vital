"""One supervisor for finite native comparator workers; no participant logic."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha
from supervisor import run

def main():
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['pilot','reserve'],required=True);a=p.parse_args()
    jobs=[]
    if a.phase=='pilot':
        plans=[('PILOT','DIR_23_paired',m) for m in ('double_teacher','symmetric_counterflow')]
    else:plans=[('RESERVED',f'DIR_{seed}_{mode}',m) for seed in (101,211) for mode in ('paired','unpaired','virgin') for m in (None,'double_teacher','symmetric_counterflow')]
    for phase,cid,method in plans:
        spec=ROOT/'configuraciones/comparadores/fixtures_v1'/phase/cid/'STREAM.json'
        tag=method or 'ordinary';out=ROOT/'resultados/native_direct'/(tag+'_'+cid)
        jobs.append({'phase':phase,'case_id':cid,'revision_method':method,'input_sha256':sha(spec),'output':str(out.relative_to(ROOT))})
    plan=ROOT/'configuraciones'/('native_'+a.phase+'_frozen.json')
    assert not plan.exists();put(plan,{'schema':'CPC7.native.stream.plan.v1','code_sha256':sha(ROOT/'src/plasticity.py'),
        'jobs':jobs,'shared_limits':{'timeout_seconds_per_worker':120,'max_peak_working_set_bytes_acceptance':256*1024**2},
        'scope':'Same observable information; revision methods add explicitly counted physical maintenance inputs, not free resources.'})
    completed=[]
    for j in jobs:
        spec=ROOT/'configuraciones/comparadores/fixtures_v1'/j['phase']/j['case_id']/'STREAM.json';out=ROOT/j['output']
        command=[sys.executable,'-I','-B','-X','utf8',ROOT/'src/plasticity.py','--stream',spec,'--out',out]
        if j['revision_method']:command+=['--revision-method',j['revision_method']]
        record=run('native_'+a.phase+'_'+(j['revision_method'] or 'ordinary')+'_'+j['case_id'],command,120)
        completed.append({'job':j,'command':record});put(ROOT/'resultados/native_direct'/('BATCH_'+a.phase+'.json'),completed)
        if record['exit_code']!=0:print('FAILED_RECORDED_CONTINUING',j['case_id'],flush=True)
if __name__=='__main__':main()
