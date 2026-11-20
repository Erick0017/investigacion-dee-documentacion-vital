"""SEM01: freeze, execute/reanudar, or reproduce one finite physical case.

The controller launches isolated owned processes; it never evolves DEE. Each
native child owns one mutable Runtime. Completed cases are verified and skipped.
"""
import argparse,concurrent.futures,json,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from src.common import sha,put,append,identity
from supervise import run,remaining

SOURCES=['ejecutar.py','src/common.py','src/memory.py','src/habitat.py','src/participant.py','src/experiment.py']
def freeze():
    path=ROOT/'configuraciones/EXPERIMENT_CONFIG.json'
    if path.exists():
        x=json.loads(path.read_text(encoding='utf-8'));assert all(sha(ROOT/p)==h for p,h in x['source_hashes'].items());return x
    A={'S1':'U','S2':'V'};B={'S1':'V','S2':'U'};cases=[]
    for name,history in [('A',A),('B',B)]:
        for label,future in [('UV',A),('VU',B)]:cases.append({'id':name+'_future_'+label,'pairing':history,'future_events':future,'type':'CONFIRMATORY_REFERENCE_KNOWN_APPARATUS'})
    for mode in ('unpaired','signals_only','outcomes_only','empty'):
        cases.append({'id':mode+'_UV','mode':mode,'pairing':A,'future_events':A,'type':'CAUSAL_HISTORY_CONTROL'})
    for name,history in [('A',A),('B',B)]:
        for control in ('no_action','always_protect'):
            cases.append({'id':name+'_'+control,'pairing':history,'future_events':history,'control':control,'type':'EXPLICIT_DIAGNOSTIC_ACTION_CONTROL'})
    cases += [
      {'id':'RESERVED_A_codec7_shift','pairing':A,'future_events':A,'translation':[5,3,2],'signal_payload':7,'type':'RESERVED_PHYSICAL_VARIANT'},
      {'id':'RESERVED_B_codec7_order_shift','pairing':B,'future_events':B,'translation':[9,-4,7],'signal_payload':7,'signal_order':['S2','S1'],'type':'RESERVED_PHYSICAL_VARIANT'}]
    x={'schema':1,'campaign':'CPC3 SEM01 SIGNIFICADO_ADQUIRIDO','instrument':'DEE thinking4.0.0','kernel':'v27 frozen','frozen_utc':datetime.now(timezone.utc).isoformat(),'source_hashes':{p:sha(ROOT/p) for p in SOURCES},
      'method_families_used':['M1 specific directional mobile relations with physically identical signal at train/test','Temporal supply access coupling v2, fixed across histories'],
      'preparation':{'N':67,'initial_memory':'empty RAW, clocks0; same fixed declared sensory and habitat interfaces, not a prelearned AB/BA preset','hubs':{'S1':[30,30,12],'S2':[30,30,44]},'prepared_period':67,'signal_encoding':'same channel, payload5 (reserved7), state1 semantic1 direction(-1,0,0) at every presentation','outcome_encoding':'fixed broadcast11 direction(1,+1,0) or(1,-1,0) from actual current local delivery','correspondence_chosen_after_prepare':True},
      'protocol':{'training_world_launches':[3,31],'observed_effect_and_signals':[17,45],'writing_encounters':[20,48],'signal_only_inputs':[84,112],'native_emissions':[87,115],'world_threat_inputs':[88,116],'physical_function_reads':[101,129],'native_initial_pending_future_events_at_queries':0,'max_case_horizon':129},
      'fixed_decoder':{'active_dx-1_dy+1_dz0':'U','active_dx-1_dy-1_dz0':'V','other_or_absent':'UNRESOLVED_NOT_ZERO'},
      'use_panel':{'primary_function':'load7 direction+y at F atemission+14','optional_resource':'load3 direction+x at R atemission+7','auditor_utility':'2*primary+optional; never feedback to body','baseline_never_protect_balanced_U_V':4,'baseline_always_protect_balanced_U_V':4,'predicted_complete_matched_profile_utility':5},
      'denominators':'Two signals per case; rejected/absent/ambiguous count as not-resolved, not correct; deterministic replays not independent samples',
      'modalities':{'world_events_and_teaching':'EXPERIENCE_PROTOCOL','absence_classification':'EXTERNAL_CURRENT_SENSOR','acquired_direction_and_action':'NATIVE_EVOLUTION','utility_and_causal_edits':'EXTERNAL_EVALUATOR_OR_DIAGNOSTIC_FORK'},
      'cases':cases,'workers':2,'native_threads':1,'per_case_timeout_seconds':180,'maximum_repairs_same_technical_error':2,'worlds_not_merged':True,'maximum_deep_extensions':2}
    put(path,x);return x

def child(args):
    from src.experiment import run_case
    case=json.loads(args.child.read_text(encoding='utf-8'));gate=freeze();assert case in gate['cases'] or case.get('type')=='DIRECTED_REPRODUCTION'
    args.output.mkdir(parents=True,exist_ok=False);stamp=time.monotonic();ident=identity(args.wheel)
    result=run_case(case,args.output);result.update(identity=ident,config_sha256=sha(ROOT/'configuraciones/EXPERIMENT_CONFIG.json'),source_hashes=gate['source_hashes'],elapsed_seconds=time.monotonic()-stamp)
    put(args.output/'MEASUREMENTS.json',result);print(json.dumps({'id':case['id'],'predictions':[u['anticipation']['emission']['anticipated_class'] for u in result['uses']],'profiles':[u['evaluation']['profile'] for u in result['uses']]}))

def main():
    p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');p.add_argument('--run',action='store_true');p.add_argument('--case');p.add_argument('--python',type=Path);p.add_argument('--wheel',type=Path,default=ROOT/'runtime/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl');p.add_argument('--child',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.child:child(a);return
    config=freeze()
    if a.freeze and not a.run:print('CONFIGURATION_FROZEN',sha(ROOT/'configuraciones/EXPERIMENT_CONFIG.json'));return
    if not a.run:p.error('--run or --freeze required')
    if not a.python:p.error('--python must identify isolated official4.0 installation')
    selected=[x for x in config['cases'] if a.case is None or x['id']==a.case]
    if not selected:p.error('Unknown frozen case ID')
    def job(case):
        folder=ROOT/'resultados/confirmacion'/case['id'];measurement=folder/'MEASUREMENTS.json'
        if measurement.exists():
            result=json.loads(measurement.read_text(encoding='utf-8'));assert result['source_hashes']==config['source_hashes'];return {'id':case['id'],'status':'REUSED_COMPLETE','path':str(measurement)}
        if remaining(ROOT)<1200:return {'id':case['id'],'status':'NO_EJECUTADO_POR_PRESUPUESTO'}
        recipe=ROOT/'configuraciones/casos'/(case['id']+'.json');put(recipe,case)
        base='confirm_'+case['id'];names=[base]+[base+'_repair'+str(i) for i in (1,2)]
        name=next((n for n in names if not (ROOT/'jobs'/n).exists()),None)
        if name is None:return {'id':case['id'],'status':'TECHNICAL_REPAIR_LIMIT'}
        if folder.exists():return {'id':case['id'],'status':'PRESERVED_PARTIAL_REQUIRES_EXPLICIT_NEW_ATTEMPT','path':str(folder)}
        record=run(ROOT,name,[str(a.python),'-I','-B',str(Path(__file__).resolve()),'--child',str(recipe),'--output',str(folder),'--wheel',str(a.wheel)],180)
        return {'id':case['id'],'status':'MEASURED' if record['exit_code']==0 else 'TECHNICAL_ERROR','job':record,'path':str(measurement)}
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for future in concurrent.futures.as_completed([pool.submit(job,x) for x in selected]):
            row=future.result();results.append(row);append(ROOT/'resultados/CASE_LEDGER.jsonl',row);put(ROOT/'resultados/LAST_RUN.json',results)
    print(json.dumps(results,indent=2))
if __name__=='__main__':main()
