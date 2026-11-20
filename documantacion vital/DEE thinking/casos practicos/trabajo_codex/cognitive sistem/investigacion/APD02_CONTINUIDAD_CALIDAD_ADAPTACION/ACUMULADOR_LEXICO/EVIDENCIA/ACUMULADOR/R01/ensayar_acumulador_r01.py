"""Three physical diagnostic copies, not cloned services or MAIN memories."""
import argparse
import gc
import gzip
import hashlib
import json
import os
import sys
import time
from datetime import datetime,timezone
from pathlib import Path
os.environ['OMP_NUM_THREADS']='1'
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];SYSTEM=ROOT/'sistema'
SOURCE=SYSTEM/'estado/checkpoints/APD02_MAIN.T361114.97439697e3b9.deetsnap.gz'
SOURCE_SHA='c93a93c0fcddf3814cba18dd11f5a9d24fb70cb981986dbdad0783cba1efcf1d'
DEADLINE=datetime(2026,10,26,11,17,43,tzinfo=timezone.utc)
INCREMENTS=[1,4,0,7,2,3,1,0]
DELAYS=[0,0,1,0,2,0,1,0]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):
    blob=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    if p.suffix=='.gz':blob=gzip.compress(blob,mtime=0)
    with p.open('xb')as f:f.write(blob)
def main():
    q=argparse.ArgumentParser();q.add_argument('--out',type=Path,required=True);args=q.parse_args()
    sys.path.insert(0,str(SYSTEM));sys.path.insert(0,str(HERE))
    from app.process_control import protect_current,current_resources
    protect_current(output=args.out/'RECURSOS_TRABAJADOR.json',memory_limit=536870912)
    from app.lives import load_adapter
    from app.native_tools import physical
    import acumulador_recirculante_r01 as candidate
    from capacidades import acumulador_adquirido_apd_01 as legacy
    if sha(SOURCE)!=SOURCE_SHA:raise ValueError('Immutable source checkpoint differs')
    if args.out.exists():raise FileExistsError('No overwrite or automatic native rerun')
    args.out.mkdir(parents=True)
    files=[Path(__file__),HERE/'acumulador_recirculante_r01.py',HERE/'PROTOCOLO_PROSPECTIVO_R01.json',
        SYSTEM/'capacidades/acumulador_adquirido_apd_01.py']
    for f in files:
        with(args.out/f.name).open('xb')as o:o.write(f.read_bytes())
    write(args.out/'PROTOCOLO_CONGELADO.json',{'status':'FROZEN_BEFORE_FIRST_NATIVE_TICK',
        'source_snapshot':str(SOURCE),'sha256':SOURCE_SHA,'source_tick':361114,
        'diagnostic_copy_not_service_clone':True,'source_epoch_not_closed':True,
        'source_native_queues_and_metadata_preserved':True,
        'cases':['real','omit','sham'],'increments':INCREMENTS,'delay_periods':DELAYS,
        'source_code':{str(f):sha(f)for f in files},'deadline_utc':DEADLINE.isoformat(),
        'one_Runtime_at_a_time':True,'memory_limit_bytes':536870912,
        'new_teaching_or_tool_calls':False,'no_expected_numeric_answer_in_actor':True})
    summaries=[];start=time.monotonic()
    for case in('real','omit','sham'):
        a=load_adapter('fisica_directa',SOURCE)
        if a.tick!=361114:raise ValueError('Not actual frozen source')
        before=physical(a.world,occupation=True)
        source_protocol=legacy.get(a)
        if source_protocol['uses']!=5:raise ValueError('Legacy cursor is not actually exhausted5')
        original=a.run_until
        def guarded(tick):
            if time.monotonic()-start>580 or datetime.now(timezone.utc)>=DEADLINE:
                raise TimeoutError('Initial bounded test budget; preserve current physical future')
            return original(tick)
        a.run_until=guarded
        rows=[];error=None;prep=None
        try:
            # All67Y values are passive, external diagnostic coverage only.
            # The actor still uses its fixed phase, ports and two-gate reader.
            initial_carrier_column=[legacy.obs(a,(25,y,30))for y in range(67)]
            prep=candidate.admit(a)
            for value,delay in zip(INCREMENTS,DELAYS):
                rows.append(candidate.accumulate(a,value,delay_periods=delay,maintenance=case))
        except BaseException as e:
            error={'type':type(e).__name__,'detail':str(e),'failed_future_preserved':True}
        finally:
            a.run_until=original
            final=physical(a.world,occupation=True)
            full=args.out/(case+'_FINAL.deetsnap.gz');storage=a.save(full)
        result={'case':case,'diagnostic_identity':'APD02_ACC_R01_'+case,
            'not_a_registered_service_continuation':True,'no_experience_transferred_to_MAIN':True,
            'source_sha256':SOURCE_SHA,'before':before,'legacy_before':source_protocol,
            'initial_column25_z30':initial_carrier_column,'preparation':prep,'uses':rows,
            'legacy_after':legacy.get(a),'after':final,'full_snapshot':full.name,
            'full_snapshot_sha256':sha(full),'storage':storage,'error':error,
            'actual_worker_resources':current_resources()}
        write(args.out/(case+'_PRIMARY.json.gz'),result)
        requests=[r for row in rows for r in row['requests']]
        summary={'case':case,'tick':final['tick'],'numbers':[r['numeric_result']for r in rows],
            'abstentions':sum(r['abstention']for r in rows),'attempts':len(rows),
            'legacy_uses_before':source_protocol['uses'],'legacy_uses_after':result['legacy_after']['uses'],
            'requested':len(requests),'applied':sum(r['receipt']['status']=='applied'for r in requests),
            'rejected_or_other':sum(r['receipt']['status']!='applied'for r in requests),
            'snapshot_sha256':result['full_snapshot_sha256'],'error':error}
        summaries.append(summary);write(args.out/(case+'_SUMMARY.json'),summary)
        print(json.dumps(summary,ensure_ascii=False),flush=True)
        del a;gc.collect()
    assert sha(SOURCE)==SOURCE_SHA
    write(args.out/'RESULTADO.json',{'cases':summaries,'source_snapshot_unchanged':True,
        'host_seconds':time.monotonic()-start,'source_epoch_not_closed':True,
        'all_experiences_attributed_to_separate_physical_diagnostic_copies':True})
if __name__=='__main__':main()
