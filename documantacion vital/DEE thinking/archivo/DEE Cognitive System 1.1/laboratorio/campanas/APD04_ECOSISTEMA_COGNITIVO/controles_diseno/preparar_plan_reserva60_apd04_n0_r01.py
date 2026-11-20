"""N0 literal plan assembler only. Never launches a driver, Native or a Runtime.

Default output is DRAFT and the real executor must reject it. Root may close
one fresh plan only after the current R04 life has stopped consistently, passing
its actual life/hash/tick. No source edits, snapshot edits, world/cache reset,
host action selector or answer lookup. Every event is precommitted here.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,shutil

ROOT=Path(__file__).resolve().parents[4]
DEADLINE='2026-10-27T03:30:51+00:00'
LATEST_START='2026-10-27T00:50:00+00:00'
LIFE='APD04_CONTINUABLE_R01'
FREEZE=[
    'sistema/app/protocolo_apd04.py','sistema/app/cola_local.py','sistema/app/servicio_persistente.py',
    'sistema/capacidades/mente_unificada_01.py','sistema/capacidades/ecosistema_apd04.py',
    'sistema/capacidades/acciones_nativas_apd04.py','sistema/capacidades/lexico_compartido_apd04.py',
    'sistema/capacidades/sensor_componentes_apd04.py','sistema/capacidades/sensor_balanceado_apd04.py',
    'sistema/capacidades/sensor_dos_pares_apd04.py','sistema/capacidades/ruta_adaptativa_apd02_04.py',
    'sistema/capacidades/mente_acumulativa_r02.py','sistema/capacidades/lexico_generico_apd03_r02.py',
    'sistema/capacidades/percepcion_cruda_fi01.py']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def event(t,label,row,feedback='omit'):
    return {'at_seconds':t,'kind':'material','request_id':'apd04_reserve_r01_'+label,
        'situations':[row],'feedback':feedback,'actuator':'closed'}
def change(t,label,**fields):return event(t,label,{'modo':'apd04-cambio',**fields})
def work(t,label):
    return event(t,label,{'modo':'apd04-vivir','oportunidades':1,'sensor':'independent_two_pairs','lexico':True,'desacoplado':False},'real')
def build(life=LIFE,snapshot=None,tick=None,pending=None,closed=False):
    if life!=LIFE:raise ValueError('Only the same declared CONTINUABLE life; no silent alternative')
    events=[change(0,'environment_open',etiqueta_objetivo=0,palabra='clasifica',cargas=[10,4],criterio=20,
        mutaciones=[{'fuente':0,'valor':16},{'fuente':1,'valor':25}])]
    for i in range(5):events.append(work(15+75*i,'level2_work'+str(i+1).zfill(2)))
    for n,at,seed in((5,400,40515),(10,800,40510),(20,1200,40520)):
        events.append(event(at,'expand'+str(n),{'modo':'apd04-ampliar','fuentes':n,'semilla':seed}))
        for i in range(20 if n==20 else 5):events.append(work(at+20+75*i,'level'+str(n)+'_work'+str(i+1).zfill(2)))
    events.extend([
        change(1800,'goal1_only',etiqueta_objetivo=1),
        change(2100,'word_balance_load2_10',palabra='equilibra',cargas=[2,10]),
        change(2375,'goal0_only',etiqueta_objetivo=0),
        change(2650,'word_classify_only',palabra='clasifica'),
        event(2700,'reference_A',{'modo':'apd04-leccion-referencia','lado':'A'}),
        change(2720,'criterion21_auditor_only',criterio=21),
        event(2740,'classify20_22_after_A',{'modo':'apd04-calibrar','casos':[{'tipo':'clasifica','valor':20},{'tipo':'clasifica','valor':22}]}),
        work(2800,'use_after_A'),
        change(2870,'equal_loads_after_A',palabra='equilibra',cargas=[5,5]),
        work(2880,'equal_load_negative_transfer_opportunity'),
        event(2980,'reference_B',{'modo':'apd04-leccion-referencia','lado':'B'}),
        change(3000,'criterion20_word_classify',criterio=20,palabra='clasifica'),
        change(3040,'new_source_values16_17',mutaciones=[{'fuente':16,'valor':13},{'fuente':17,'valor':28}]),
        *[work(t,'increased_demand_work'+str(i+1))for i,t in enumerate((3050,3085,3120,3155))],
        {'at_seconds':3240,'kind':'command','request_id':'apd04_reserve_r01_old16_MA6_panel',
            'argv':['panel','--nuevas','--memorias','--retorno','omit']},
        event(3340,'retained_clasifica',{'modo':'apd04-palabra','texto':'clasifica'}),
        event(3370,'retained_equilibra',{'modo':'apd04-palabra','texto':'equilibra'}),
        change(3420,'late_balance_load9_3',palabra='equilibra',cargas=[9,3]),
        work(3430,'late_balance_use'),
        change(3510,'late_class_goal1_mutate0_1',palabra='clasifica',etiqueta_objetivo=1,
            mutaciones=[{'fuente':0,'valor':14},{'fuente':1,'valor':31}]),
        work(3520,'late_class_use'),
        {'at_seconds':3570,'kind':'checkpoint','tag':'actual_end_of_reserved_experiences'}])
    events.sort(key=lambda e:e['at_seconds'])
    plan={'schema':'APD04.literal_supervisor_schedule.v1','status':'CLOSED_FOR_EXECUTION'if closed else'DRAFT_NOT_AUTHORIZED_FOR_NATIVE',
        'life':life,'world_id':life,'initial_snapshot_sha256':snapshot,'initial_tick':tick,
        'deadline_utc':DEADLINE,'reserve_start_latest_utc':LATEST_START,'duration_seconds':3600,'closing_reserve_seconds':180,
        'material_wait_seconds':30,'result_limit_seconds':1200,'poll_heartbeat_seconds':5,'heartbeat_seconds':30,
        'stop_control_wait_seconds':120,'stop_process_wait_seconds':120,'supervision_wall_limit_seconds':5400,
        'outer_guard_requires_existing_supervision_wrapper':True,'freeze_source_paths':FREEZE,'events':events,
        'after_window_pending':{'request_id':'apd04_reserve_exact_pending_r01',
            'situations':[{'modo':'apd04-calibrar','casos':[{'tipo':'clasifica','valor':43}]}],'feedback':'omit','actuator':'closed'},
        'queueing_wait_seconds':0.25,
        'scope':'One same lived CONTINUABLE world, no reset/import/T0, no cache/cursor clearing, no source retargeting or action policy in host. Fixed prospective calendar and stimuli; context, goals, word, supply and explicit reference experiences are operator/environment preparation.',
        'coverage_and_criteria':{
            'first_five_core_at_each_level':'Same supplied clasifica word,goal0,criterion20 and inherited reference expected20; actual physical reference must be observed, not forced. Trajectory history changes, so not a causal head-to-head source-count experiment.',
            'source_counts':'2→5→10→20 incrementally, sequential two-bit source/goal view, not20simultaneous complete records. Expand preserves old objects, versions, bins, cursor and cache.',
            'dose_separation':'First5opportunities per level share nominal selector opportunity count. Later20-source exposures and late35second nominal cadence increase traffic. Record every requested/admitted/rejected material input and actual time/lateness; do not claim realized rate from this schedule.',
            'quality':'Existing frozen post-action evaluator and raw-bit feedback only. Criterion fields belong to evaluator, not Native input. Numerical NULL remains unformed, never substituted with Native HOLD.',
            'reference_prediction_auditor_only':'If actual initial reference is20, experienceA is predicted to produce21 and laterB20. No RAW/clock/reference editing if this fails. Freeze prior criteria and retain contrary results.',
            'negative_transfer':'The2880opportunity permits testing equal-load behavior afterA. If Native chooses INSPECT or produces no USE/numeric emission, do not claim that an unfavorable balance action was actually tested.',
            'retention':'Material panel16forms+6MA, then two new lexical queries are separate real queries which can change state, not passive proof of all-time stability.',
            'integration':'Consecutive use in one actual life. No AUX memories, alternative snapshots, teacher answers or favorable future imported.',
            'continuation':'After the full real window, pause and leave one NEW exact calibration43ID queued, then save/STOP. Future reopening consumes that sameID; no second PUT.',
            'deadline':'No new budget clock. Root must launch before00:50UTC and existing driver checks the fixed final deadline. Proposed read-only observation instruments are not installed by this plan.'}}
    if pending:plan['resume_pending_id']=pending
    return plan

def validate_n0(plan,driver):
    spec=importlib.util.spec_from_file_location('existing_R03_plan_validator_only',driver);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    # Validation of a copy proves schema only and cannot authorize the DRAFT.
    copy=dict(plan);copy['status']='CLOSED_FOR_EXECUTION';copy['initial_snapshot_sha256']=copy['initial_snapshot_sha256']or'0'*64;copy['initial_tick']=copy['initial_tick']if copy['initial_tick']is not None else 0
    m.validate_plan(copy)
    return {'literal_events':len(plan['events']),'work_opportunities':sum(e['kind']=='material'and e['situations'][0]['modo']=='apd04-vivir'for e in plan['events']),
        'static_schema_valid':True,'plan_remains_DRAFT_unless_Root_GO':plan['status']!='CLOSED_FOR_EXECUTION',
        'Native_ticks':0,'does_not_validate_future_outcomes_or_actor_admission':True}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',required=True,type=Path);ap.add_argument('--life',default=LIFE)
    ap.add_argument('--snapshot-sha256');ap.add_argument('--tick',type=int);ap.add_argument('--resume-pending-id')
    ap.add_argument('--root-go',choices=['APD04_RESERVA60_PLAN_CLOSED']);a=ap.parse_args();closed=bool(a.root_go)
    if a.out.exists():raise FileExistsError('Never replace a prior prepared or closed plan')
    if closed:
        if a.tick is None or a.tick<0 or not a.snapshot_sha256 or len(a.snapshot_sha256)!=64 or any(c not in'0123456789abcdef'for c in a.snapshot_sha256):raise ValueError('Actual reached compatible current tick and lowercase SHA256 required')
        if datetime.now(timezone.utc)>=datetime.fromisoformat(LATEST_START):raise TimeoutError('Declared reserve start cut-off passed; no reset of budget')
    elif a.snapshot_sha256 is not None or a.tick is not None:raise ValueError('Keep future identity unset in DRAFT; assemble actual values only on RootGO')
    plan=build(a.life,a.snapshot_sha256,a.tick,a.resume_pending_id,closed)
    driver=ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/ejecucion/ejecutar_plan_apd04_r03.py'
    check=validate_n0(plan,driver)
    # Prepare exact bytes for provenance. The real driver independently freezes
    # the actual sources again immediately before any later Native execution.
    provenance={'assembler_sha256':sha(Path(__file__)),'executor_R03_sha256':sha(driver),'checks':check,
        'source_hashes_at_N0_assembly_not_a_future_freeze':[{'file':p,'sha256':sha(ROOT/p),'bytes':(ROOT/p).stat().st_size}for p in FREEZE],
        'no_driver_run_no_Native_import_no_tick':True,'preparation_does_not_launch_or_authorize_Native':True}
    dump(a.out,plan);prov=a.out.parent/(a.out.stem+'_PREPARACION_N0.json');dump(prov,provenance)
    copies=a.out.parent/(a.out.stem+'_FUENTES_PREPARATORIAS');copies.mkdir(exist_ok=False)
    shutil.copy2(Path(__file__),copies/Path(__file__).name);shutil.copy2(driver,copies/driver.name)
    dump(copies/'HASHES.json',{'members':[{'file':p.name,'sha256':sha(p),'bytes':p.stat().st_size}for p in copies.iterdir()if p.is_file()]})
    print(json.dumps({'plan':str(a.out),'status':plan['status'],**check},ensure_ascii=False))
if __name__=='__main__':main()
