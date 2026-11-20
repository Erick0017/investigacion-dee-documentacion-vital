"""Bounded post-first-use adaptation, existing C2 file model and frozen codecs.

New diagnostic forks only. Prepared independent tasks are external environment,
not E1 actions; native emissions choose the actual verifying worker. A failed
real receipt returns the SAME generic zero A-contact, never the right action.
"""
from __future__ import annotations
import base64,gc,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema'
sys.path.insert(0,str(LAB/'transferencia_b'))
import frontend_b01_r2 as f
OUT=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/adaptacion_b14'
KEY='MUFI01.B14.EXTERNAL_TASK_STATE.v1'
SOURCES={
 'T':('FI01_BT_TWO_T','estado/checkpoints/FI01_BT_TWO_T.T31631.53dde5ad70d4.deetsnap.gz','ccc8022c6ba7f9edcea09243eaa6f48a4302cd3c756e73c647cccab9fee5e99b'),
 'U':('FI01_BT_TWO_U','estado/checkpoints/FI01_BT_TWO_U.T31631.3ee7154fb854.deetsnap.gz','7a95b7f9cee23fbe17239aff987cf60da37b10a0901675f11cb0303f2d2ec637'),
 'H':('FI01_BT_TWO_H','estado/checkpoints/FI01_BT_TWO_H.T31631.b9820a75203a.deetsnap.gz','f50aaa61c3d8bafdbc3ef76b2dfb4b3854964bc9cef099a6848b1466a526d724')}
FAMILIES=['quantitative','gamma','quantitative','gamma','quantitative','gamma','quantitative','gamma']

def refs(a,ni):return [ni[7].obs(a,p)for p in[(14,14,15),(16,14,15)]]
def schedule(j):
    start=31631+1564*j;qs=start+8;qa=(start//67+1)*67
    k=(max(qs+8,qa+7)+15)//391+1;ret=(k if k%2 else k+1)*391
    return {'index':j+1,'start_tick':start,'family':FAMILIES[j],'scalar_query_tick':qs,'association_query_tick':qa,'possible_failure_arrival_tick':ret,'common_end_tick':ret+2}

def worker(data):
    cmd=[sys.executable,'-I','-B','-X','utf8',str(SYSTEM/'capacidades/eo02_trabajador_local.py')]
    p=subprocess.run(cmd,input=json.dumps(data),encoding='utf-8',text=True,capture_output=True,timeout=15)
    if p.returncode:raise RuntimeError('Actual external process failure, not cognitive failure; do not auto-retry: '+p.stderr)
    r=json.loads(p.stdout);path=Path(data['output_directory'])/r['output_name'];b=path.read_bytes()
    if f.digest(path)!=r['output_sha256']or len(b)!=r['output_bytes']:raise ValueError('Real worker readback mismatch')
    return {'request':data,'receipt':r,'argv':cmd,'readback_hex':b.hex(),'readback_sha256':f.digest(path)}

def opportunity(a,arm,j,ni):
    from capacidades import selector_acrecion_nativo as sel
    from capacidades import mente_acumulativa_r02 as ma
    from dee_thinking.persistence import encode_metadata,decode_metadata
    sc=schedule(j);a.run_until(sc['start_tick']);pre=ni[6](a.world,occupation=True);before=refs(a,ni)
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    env=decode_metadata(entries[KEY])if KEY in entries else {'tasks':[],'format':'Independent fixed C2 opportunities; failed task states remain archived, no DEE reset.'}
    folder=OUT/'archivos_reales'/arm/('op_'+str(j+1));folder.mkdir(parents=True,exist_ok=True)
    # Each task is fixed before the native response. This is environmental
    # preparation, not an action attributed to E1 or a correct-route teacher.
    data={'domain':'transaccion','executed_worker':1,'raw_observations':[7,7],'capacity_credit':0,'pending_transaction':None,'attempt':1,'native_tick':a.tick,'output_directory':str(folder.resolve())}
    fixture=worker(data);pending=fixture['receipt']['pending_transaction']
    if not pending or not fixture['receipt']['accepted']:raise ValueError('Fixed real C2 fixture could not be prepared')
    n=len(bytes.fromhex(fixture['readback_hex']))
    if n!=12:raise ValueError('Frozen existing fixture changed; no adaptive codec adjustment')
    if sc['family']=='quantitative':
        native=f.trial(a,'B14.current.bytecount.'+str(j+1),n,ni);choice=native['reader']['choice']
    else:
        native=ma.query(a,'gamma',detail=True);choice=native['reader']['formed_native_command']
    action=None
    if choice in(-1,1):
        actual={**data,'executed_worker':choice,'pending_transaction':pending,'attempt':2,'native_tick':a.tick}
        action=worker(actual)
    accepted=bool(action and action['receipt']['accepted']);ret=None
    if not accepted:
        r=sel.experience(a.world,'A',sc['possible_failure_arrival_tick'],'MU.selector')
        a.run_until(sc['possible_failure_arrival_tick']-1);rp=refs(a,ni)
        a.run_until(sc['possible_failure_arrival_tick']+2)
        ret={'codec':'Actual C2 failed/noncompleted opportunity -> SAME zero A-contact. No right worker, expected sign, task ID or target is native input.',
             'arrival':sc['possible_failure_arrival_tick'],'request':sel.receipt(a.world,r),'pre':rp,'post':refs(a,ni)}
    a.run_until(sc['common_end_tick']);f.memory_guard()
    task={'index':j+1,'family':sc['family'],'pending_before':pending,'pending_after':action['receipt']['pending_transaction']if action else pending,
          'actual_accepted':accepted,'actual_native_choice':choice,'prepare_was_environment_not_ente':True}
    env['tasks'].append(task);a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(env))
    return {'arm':arm,'schedule':sc,'physical_before':pre,'references_before':before,'fixture':fixture,'native':native,'native_choice':choice,'actual_action':action,
      'actual_accepted':accepted,'actual_transaction_completed':bool(action and action['receipt']['transaction_completed']),
      'counterlaw_analytic_only':{'useful':choice==1,'not_worker_acceptance':True,'no_counterlaw_feedback':True},
      'failure_return':ret,'references_after':refs(a,ni),'physical_after':ni[6](a.world,occupation=True),'external_task_state':task,
      'attribution':'Fixed prepared interfaces and typed gamma request. Physical choice is DEE; environmental task, operation schedule, transduction and postfailure contact are external. No autonomous bank or strategy selection asserted.'}

def main():
    authorization,ni=f.bootstrap();store=ni[3]();code=f.digest(__file__)
    for _,path,sha in SOURCES.values():
        if f.digest(SYSTEM/path)!=sha:raise ValueError('Actual final B02 source changed; no historical rewind/substitution')
    f.dump(OUT/'PROTOCOLO.json',{'schema':'MUFI01.B14.C2.postfirstuse.R1','before_first_new_tick':ni[5](),'authorization':authorization,'source_sha256':code,
      'frontend_sha256':f.digest(f.__file__),'worker_sha256':f.digest(SYSTEM/'capacidades/eo02_trabajador_local.py'),'sources':SOURCES,'schedule':[schedule(j)for j in range(8)],
      'fixed_budget_per_arm':8,'families':'Four quantitative bytecount and four gamma signed-association opportunities, interleaved in one continuous fork per arm.',
      'environment':'Eight independent real C2 compressed-file verification tasks, each prepared beforehand by fixed environmental worker+ from[7,7]. Real12byte readback. Failed independent tasks remain archived; no brain reset, no hidden repair.',
      'codec':'Original identity actual-bytecount→S and original prepared gamma query; original fixed six/pureZ readers. Native sign directly chooses existing actual C2 worker.',
      'return':'Only actual C2 nonacceptance/deadline triggers generic0A at a predeclared odd391 opportunity; success advances passively to the identical windowend. No correct action/route/content provided.',
      'counterlaw':'Analytic inversion of utility on the same actual actions ONLY; C2 worker receipt/law is not altered, no opposite-law adaptive branch or false receipt.',
      'cost_criterion_before_results':'First postsource opportunity is prereward. Stable useful adaptation = earliest four consecutive actually completed opportunities through the fixed end; absent criterion is right-censored beyond8 total opportunities (only4 per relationfamily). Also report each first response, all failures, references and every denominator.',
      'limits':'No dose/criterion change after negative results; omitted-return source-control data are existing A/B fronts, not a new matched adaptation control. Three histories are not independent population replicates; local acquired reference changes are not general R2.'})
    summaries=[]
    for arm,(parent,path,sha)in SOURCES.items():
        life='FI01_B14_ADAPTACION_'+arm
        if store.life_dir(life).exists():raise FileExistsError(life)
        store.fork(parent,life,kind='B14_EXACT_POST_FIRST_USE_CONTINUATION',checkpoint=path);gc.collect();f.memory_guard();rows=[]
        for j in range(8):
            result=store.mutate(life,'B14_C2_OPPORTUNITY_'+str(j+1),lambda a:opportunity(a,arm,j,ni),{'code_sha256':code,'fixed_schedule':schedule(j),'no_correct_action_in_return':True})
            f.dump(OUT/(arm+'_OP_'+str(j+1)+'.json.gz'),result);r=result['result'];rows.append({'index':j+1,'family':r['schedule']['family'],'native_choice':r['native_choice'],'accepted':r['actual_accepted'],'reference_s_reg':[x['s_reg']for x in r['references_after']],
              'end_tick':result['physical']['tick'],'snapshot':store.record(life)['snapshot'],'snapshot_sha256':result['INSTRUMENTO']['snapshot_sha256']});del result;gc.collect();f.memory_guard()
        summaries.append({'arm':arm,'life':life,'opportunities':rows});print(json.dumps(summaries[-1]),flush=True)
    f.dump(OUT/'RESUMEN.json',{'arms':summaries,'sources_unchanged':all(f.digest(SYSTEM/p)==h for _,p,h in SOURCES.values()),'peak_RSS_bytes':f.memory_guard()})
if __name__=='__main__':main()
