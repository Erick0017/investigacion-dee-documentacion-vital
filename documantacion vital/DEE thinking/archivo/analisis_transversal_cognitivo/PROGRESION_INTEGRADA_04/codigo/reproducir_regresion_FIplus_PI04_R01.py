"""Known-negative technical replay, not a blind reserve or favourable search.

PLAN by default. Root alone may use --ejecutar after its other owners close.
Exactly one new full-pair clone, the two already executed retention uses and
the unchanged historical panel stopping at its first discrepancy are allowed.
No repair, teaching, new reader, metric or trial substitution is introduced.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,runpy,subprocess,sys
P4=Path(__file__).resolve().parents[1];C=P4.parents[2]/'DEE Cognitive 2.0';S2=P4/'estados/candidato_R02/sistema'
PY=C/'motor/python313/python.exe';CODE=P4/'codigo';LIFE='ECI02_PI03_REPRO_PI04_C2C_REGRESION_01'
ALIAS='PI03_PI04_C2C_POST_RES_T816019';RET='PI04_REGRESION_RET2_R01';PANEL='PI04_REGRESION_PANEL12_R01'
PROTOCOL=P4/'control/REGRESION_FIPLUS_PROTOCOLO_PRE_REPLICA_R01.json';OUT=P4/'control/REGRESION_FIPLUS_REPLICA_CERRADA_R01.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def info(p):return {'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def primary(p):
    d=read(p);return json.loads(d['result'])if isinstance(d.get('result'),str)else d
def get(value,path):
    for key in path:value=value[key]
    return value
def material_specs():
    recipe=read(C/'reproducibilidad/recetas/panel_12.json')
    return [s for batch in recipe['variants']['principal']['batches']for s in batch if'read_path'in s][:6]
def commands():
    base=[str(PY),'-I','-B','-X','utf8']
    return [base+[str(CODE/'clonar_PI04_R02.py'),'--par',str(C/'reproducibilidad/materiales'/ALIAS),'--vida',LIFE],
      base+[str(CODE/'ejecutar_C2C_R01.py'),'--vida',LIFE,'--brazo','real','--hasta','22','--tag',RET],
      base+[str(CODE/'ejecutar_panel_PI04.py'),'--vida',LIFE,'--tag',PANEL]]
def summarize_panel(tag):
    rows=[];receipts={}
    for spec in material_specs():
        file=P4/'ensayos'/(tag+'_'+spec['label']+'.json');d=primary(file)
        observed=get(d,spec['read_path']);local={}
        for path in spec.get('receipt_paths',[]):
            for request in get(d,path):
                r=request.get('receipt',request);identifier=int(request['id'])
                if identifier!=r['id']or not d['before_tick']<=r['requested_tick']<=d['after_tick']:raise ValueError('Panel receipt outside actual current-use window')
                if identifier in receipts and receipts[identifier]!=r:raise ValueError('Contradictory Native receipt alias')
                receipts[identifier]=r;local[identifier]=r
        rows.append({'label':spec['label'],'expected_evaluator_only':spec['expected'],'observed':observed,'correct':observed==spec['expected'],'before_tick':d['before_tick'],'after_tick':d['after_tick'],'requested':len(local),'applied':sum(r['status']=='applied'for r in local.values()),'primary':info(file)})
    return rows,receipts
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--ejecutar',action='store_true');ap.add_argument('--analizar-cerrado',action='store_true');a=ap.parse_args()
    if not PROTOCOL.is_file():raise FileNotFoundError('Root-reviewed sealed known-negative expectation required')
    sealed=read(PROTOCOL)
    if sealed['mode']!='KNOWN_NEGATIVE_TECHNICAL_REPLAY_NOT_RESERVE'or sealed['new_trial_design']is not False:raise ValueError('Exact sealed known-negative protocol required')
    if not(a.ejecutar or a.analizar_cerrado):
        print(json.dumps({'mode':'PLAN_NO_NATIVE_NO_WRITES','commands':commands(),'source_alias':ALIAS,'new_life':LIFE,'expected_partial_Native_ticks':2055,'expectation':'Known5/6 panel with FIplus−1, not a successful12-panel. Any different result remains evidence.','scientific_status':'TECHNICAL_REPLICA_SHARED_PREFIX_NOT_INDEPENDENT_RESERVE'},ensure_ascii=False,indent=2));return
    if OUT.exists():raise FileExistsError('Closed replay proof protected; do not repeat')
    child_results=[]
    if a.ejecutar:
        if Path(sys.executable).resolve()!=PY.resolve():raise ValueError('Existing official CPython3.13 executable required')
        for family in('vidas','servicios_persistentes','servicios_locales'):
            if(S2/'estado'/family/LIFE).exists():raise FileExistsError('Explicit replay identity already used')
        if(S2/'estado/ACTIVO.json').exists():raise ValueError('Isolated system must have no selected principal')
        locks=list((S2/'estado/locks').glob('*.lock'))
        if locks:raise ValueError('Another source-system writer is present; wait, do not remove:'+str(locks))
        for i,command in enumerate(commands()):
            stdout=P4/'ensayos'/('REGRESION_FIPLUS_R01_CHILD'+str(i)+'.stdout.txt');stderr=stdout.with_suffix('.stderr.txt')
            with stdout.open('x',encoding='utf-8')as out,stderr.open('x',encoding='utf-8')as err:result=subprocess.run(command,cwd=P4,stdout=out,stderr=err,check=False)
            child_results.append({'stage':i,'command':command,'returncode':result.returncode,'stdout':info(stdout),'stderr':info(stderr)})
            if i<2 and result.returncode!=0:raise RuntimeError('Replay preparation/retention failed; preserve clone/IDs, no automatic retry')
            if i==2 and result.returncode not in(0,1):raise RuntimeError('Unexpected panel process failure; preserve all evidence')
    ret=read(P4/'control'/(RET+'.json'))
    if ret['owner_closed']is not True or ret['completed']!=2 or ret['new_native_ticks']!=1564:raise ValueError('Actual closed two-use retention prefix missing')
    original_rows,original_receipts=summarize_panel('PI04_MAIN_PANEL12_OP2');replayed_rows,replayed_receipts=summarize_panel(PANEL)
    last_original=primary(P4/'ensayos/PI04_MAIN_PANEL12_OP2_FIplus.json');last_replay=primary(P4/'ensayos'/(PANEL+'_FIplus.json'))
    if last_replay['committed_snapshot']['life_id']!=LIFE:raise ValueError('Another life cannot be counted as this technical replay')
    parse=runpy.run_path(str(CODE/'contrastar_finales_E3_pasivo.py'),run_name='passive_negative_replay_parser')['parse']
    def frozen(d):
        cut=d['committed_snapshot'];return parse(S2/cut['snapshot'],cut['snapshot_sha256'])
    left=frozen(last_original);right=frozen(last_replay)
    paired_rows=[{'label':x['label'],'same_observed':x['observed']==y['observed'],'same_age':(x['before_tick'],x['after_tick'])==(y['before_tick'],y['after_tick']),'same_input_counts':(x['requested'],x['applied'])==(y['requested'],y['applied'])}for x,y in zip(original_rows,replayed_rows)]
    matches={'GLOBAL_RAW_bytes_exact':left[7]==right[7],'GLOBAL_clocks_bytes_exact':left[8]==right[8],'whole_Native_receipt_history_exact':left[5]==right[5],'interfaces_exact':left[3]==right[3],'Native_agenda_exact':left[4]==right[4],
      'all6_observables_age_dose_exact':len(paired_rows)==6 and all(all(v for k,v in r.items()if k!='label')for r in paired_rows),'partial_panel_receipt_dict_exact':original_receipts==replayed_receipts}
    proof={'schema':'DEE.PI04.known_negative.FIplus.technical_replay.R01','inspection_local':datetime.datetime.now().astimezone().isoformat(),'sealed_protocol':info(PROTOCOL),'life_id':LIFE,'parent_full_alias':ALIAS,'Native_execution_by_Root':a.ejecutar,'new_Native_ticks_by_passive_recalculation':0,
      'actual_replay_retention':{'proof':info(P4/'control'/(RET+'.json')),'completed':ret['completed'],'products':ret['products'],'Native_ticks':ret['new_native_ticks']},'original_panel_rows':original_rows,'replay_panel_rows':replayed_rows,
      'panel_denominators':{'opportunities_tested':6,'correct':sum(r['correct']for r in replayed_rows),'planned_full_panel':12,'remaining6_not_executed':True,'unique_Native_inputs':len(replayed_receipts),'applied':sum(r['status']=='applied'for r in replayed_receipts.values()),'FIplus_inputs':replayed_rows[-1]['requested']},
      'original_final':left[0],'replay_final':right[0],'paired_row_checks':paired_rows,'matches':matches,'known_failure_reproduced':all(matches.values())and sum(r['correct']for r in replayed_rows)==5 and replayed_rows[-1]['observed']==-1,
      'actual_total_Native_ticks':ret['new_native_ticks']+replayed_rows[-1]['after_tick']-replayed_rows[0]['before_tick'],'child_processes':child_results,
      'scope':'Technical deterministic reproduction of a known adverse observation from the exact post-reserve full prefix, including both actual retention uses and the same frozen panel. Shared prefix, no independent reserve or intervention that identifies the causal origin. No repair, promotion, teaching or favourable branch search.'}
    with OUT.open('x',encoding='utf-8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':info(OUT),'known_failure_reproduced':proof['known_failure_reproduced'],'matches':matches,'denominators':proof['panel_denominators'],'actual_Native_ticks':proof['actual_total_Native_ticks']},ensure_ascii=False))
if __name__=='__main__':main()
