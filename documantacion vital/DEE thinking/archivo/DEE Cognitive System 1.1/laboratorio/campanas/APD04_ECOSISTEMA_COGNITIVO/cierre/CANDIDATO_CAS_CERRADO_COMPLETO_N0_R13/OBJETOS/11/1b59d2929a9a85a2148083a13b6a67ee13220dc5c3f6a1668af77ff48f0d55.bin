"""Declared R04 protocol repair: resume SAME owner/queued advance ID, no PUT.

R03 paused-control timeout and unchanged T605522 remain preserved. This script
never resubmits the advance or imports/restores a world. Only3original probes.
"""
from pathlib import Path
import hashlib,importlib.util,json,shutil,time
HERE=Path(__file__).resolve().parent
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    base=load('unchanged_original_control_driver',HERE/'ejecutar_controles_lexico_referencia_apd04_r01.py')
    original=base.ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/CONTROLES_REFERENCIAS_RESTANTES_AUX_R02/REF_OMIT'
    prior=original/'CONTINUACION_MISMA_VIDA_R03';out=original/'CONTINUACION_MISMA_VIDA_R04'
    if out.exists():raise FileExistsError('No repeat of the reached R04 future')
    revision=json.loads((prior/'REVISION_DOCUMENTAL_EXPLICITA.json').read_bytes())
    for r in revision['current_revision_members']:
        if sha(base.S/r['file'])!=r['sha256']:raise ValueError('Frozen R03 actor/document revision changed')
    ui=load('existing_resume_control_UI',base.S/'app/usar_dee.py')
    config=dict(json.loads((original.parent/'PLAN_CERRADO_ANTES_NATIVE.json').read_bytes())['config_local_not_installed'])
    config.update(owner_max_seconds=900,material_wait_seconds=300)
    backend=ui.OriginalBackend(base.ROOT,config);life='APD04_REF_OMIT_AUX_R01';session=ui.Supervisor(base.ROOT,life,backend,config)
    rid='apd04_ctrl_ref_omit_r03_explicit_age_605663';queued=backend.manager(['mente-unificada-resultado','--vida',life,'--id',rid])
    if queued['request']['status']!='queued'or queued['request']['started_utc']is not None:raise ValueError('The queued-only protocol diagnosis changed; no automatic new advance')
    initial=backend.record(life)
    if initial['physical']['tick']!=605522:raise ValueError('Unexpected reached state; no forced rollback')
    out.mkdir();shutil.copy2(Path(__file__),out/Path(__file__).name)
    pc=load('existing_own_resume_Job',base.S/'app/process_control.py');pc.protect_current(output=out/'RECURSOS_DRIVER.json',memory_limit=536870912)
    base.write(out/'PLAN_CERRADO_ANTES_REANUDAR.json',{'schema':'APD04.same_REF_OMIT.queued_ID_resume.R04','authorization':'Root GO:reopen SAMElife/fullstate with existing queued141tick ID; resume owner; read sameID only;3authorizedprobes;STOP/seal.',
        'initial_record':initial,'existing_age_id':queued,'no_age_PUT':True,'R03_timeout_was_paused_queue_not_Native_compute':True,
        'source_revision':revision,'planned_age_target':605663,'plans':base.plans('ref',None)[1:],
        'timing_scope':'R04 technical resume introduces documented idle intervals; no retroactive claim of exact A/B matching.'})
    error=None;events=[];started=time.perf_counter()
    with ui.SessionLock(backend.protocol_home/life/'SUPERVISOR.lock'):
        try:
            opened=session.open(new=False);base.write(out/'MISMA_VIDA_ABIERTA.json',opened)
            if opened['world_id']!=initial['world_id']:raise ValueError('World identity changed')
            base.write(out/'START_PAUSED.json',session.start());base.write(out/'REANUDAR_EXISTENTE.json',session.control('reanudar'))
            deadline=time.perf_counter()+300;poll=0
            while True:
                poll+=1;r=backend.manager(['mente-unificada-resultado','--vida',life,'--id',rid])
                base.write(out/('01_EDAD_MISMO_ID_LECTURA_'+str(poll).zfill(3)+'.json'),r)
                status=r['request']['status']
                if status=='completed':break
                if status not in('queued','processing')or time.perf_counter()>deadline:raise RuntimeError('Same age future remains unresolved; no requeue/probes')
                time.sleep(1)
            for serial,(event,row)in enumerate(base.plans('ref',None)[1:],2):
                qid='apd04_ctrl_ref_omit_r04_'+str(serial)+'_'+event.lower()
                r=session.material([row],feedback='omit',actuator='closed',request_id=qid[:90]);base.write(out/(str(serial).zfill(2)+'_'+event+'.json'),r)
                entry={'serial':serial,'event':event,'request_id':qid[:90],'status':ui.row_of(r).get('status'),'metrics':base.summary(r)}
                events.append(entry);print(json.dumps(entry,ensure_ascii=False),flush=True)
                if entry['status']!='completed':raise RuntimeError('Probe future unresolved; no repeat')
            base.write(out/'GUARDAR.json',session.control('guardar'));base.write(out/'STOP.json',session.control('detener'))
        except BaseException as exc:
            error={'type':type(exc).__name__,'message':str(exc),'no_rewind_or_new_age_PUT':True};base.write(out/'ERROR_PRESERVADO.json',error)
        finally:session.close()
    final=backend.record(life);sealer=load('existing_postSTOP_pair_sealer',base.ROOT/'laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/main/ejecutar_main_integrado_apd03_r01.py')
    target=base.S/'estado/fuentes_emparejadas'/(life+'_T'+str(final['physical']['tick'])+'_R04')
    paired=sealer.stopped_pair(base.ROOT,ui,life,target,allow_queued=False,scope='Same REF_OMIT life after preserved interface error, paused-only queued ageID and technical R04 resumption;3originalprobes. No recreation/rewind or memory transfer.')
    changed=[r['file']for r in revision['current_revision_members']if sha(base.S/r['file'])!=r['sha256']]
    closure={'label':'REF_OMIT','life':life,'kind':'ref','condition':None,'prefix_snapshot_sha256':base.SNAPSHOT_SHA,
        'initial_tick':605522,'declared_age_target':605663,'final_tick':final['physical']['tick'],'snapshot_sha256':final['snapshot_sha256'],
        'elapsed_seconds':time.perf_counter()-started,'events':events,'error':error,'paired':paired,'source_changed':changed,
        'declared_documentary_revision':revision['changes'],'continued_same_world_id':initial['world_id']==final['world_id'],
        'original_interface_error_preserved':True,'R03_paused_queue_timeout_preserved':True,'not_exact_A_B_timing_or_dose_match':True}
    base.write(out/'CIERRE_CONTINUACION.json',closure)
    print(json.dumps({'REF_OMIT_SAME_LIFE_R04_CLOSED':True,'tick':final['physical']['tick'],'error':error,'source_changed':changed},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
