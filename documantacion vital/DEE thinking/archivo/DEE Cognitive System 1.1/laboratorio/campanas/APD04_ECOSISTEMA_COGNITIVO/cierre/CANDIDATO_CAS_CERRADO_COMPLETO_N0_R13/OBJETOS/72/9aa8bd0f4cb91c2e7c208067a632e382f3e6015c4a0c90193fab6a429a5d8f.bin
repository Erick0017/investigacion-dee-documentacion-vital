"""Only three previously authorized probes on the SAME failed-interface AUX.

The rejected read-only row remains intact. No import, recreation, restoration,
teacher, clock edit or additional Native family. Explicit age advancement uses
the existing persistent owner's continuar operation, never Runtime directly.
"""
from pathlib import Path
import importlib.util,json,hashlib,shutil,time
HERE=Path(__file__).resolve().parent
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    base=load('apd04_original_control_driver',HERE/'ejecutar_controles_lexico_referencia_apd04_r01.py')
    original=base.ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/CONTROLES_REFERENCIAS_RESTANTES_AUX_R02/REF_OMIT'
    out=original/'CONTINUACION_MISMA_VIDA_R03'
    if out.exists():raise FileExistsError('Never repeat this reached future')
    closed=json.loads((original/'CIERRE.json').read_bytes())
    if not closed.get('error')or closed['events'][0]['status']!='rejected_invalid':raise ValueError('Expected preserved interface failure missing')
    source_manifest=json.loads((HERE/'FUENTES_CONTROLES_EJECUTADO_R01/MANIFEST_FUENTES.json').read_bytes())
    documentary=[];revision=[]
    for r in source_manifest['members']:
        now=sha(base.S/r['file'])
        if now!=r['sha256']:
            if r['file']!='contratos/APD04_TALLER_SITUADO.json':raise ValueError('Actor code or undeclared source changed before continuation')
            documentary.append({'file':r['file'],'original_sha256':r['sha256'],'R03_sha256':now,
                'authorization':'Root explicitly authorized only declarative contract update for reached CONTINUABLE cut and adverse MAIN; no actor/code/physics/ACTIVO edits.',
                'source_graph_check':'No sistema .py references APD04_TALLER_SITUADO; owner uses unchanged Python plus frozen local UI config.'})
        revision.append({**r,'sha256':now})
    out.mkdir();shutil.copy2(Path(__file__),out/Path(__file__).name)
    for row in documentary:
        old=HERE/'FUENTES_CONTROLES_EJECUTADO_R01/sistema'/row['file'];new=base.S/row['file']
        shutil.copy2(old,out/'CONTRATO_DECLARATIVO_ANTERIOR.json');shutil.copy2(new,out/'CONTRATO_DECLARATIVO_R03.json')
        a=json.loads(old.read_bytes());b=json.loads(new.read_bytes());row['changed_top_level_fields']=[k for k in sorted(set(a)|set(b))if a.get(k)!=b.get(k)]
    base.write(out/'REVISION_DOCUMENTAL_EXPLICITA.json',{'changes':documentary,'unchanged_actor_python_files':sum(r['file'].endswith('.py')for r in revision),
        'original_closure_source_changed_preserved':closed['source_changed'],'current_revision_members':revision})
    pc=load('owned_omit_continuation_process',base.S/'app/process_control.py');pc.protect_current(output=out/'RECURSOS_DRIVER.json',memory_limit=536870912)
    ui=load('existing_omit_continuation_UI',base.S/'app/usar_dee.py')
    original_plan=json.loads((original.parent/'PLAN_CERRADO_ANTES_NATIVE.json').read_bytes())
    config=dict(original_plan['config_local_not_installed']);config.update(owner_max_seconds=900,material_wait_seconds=240)
    backend=ui.OriginalBackend(base.ROOT,config);life='APD04_REF_OMIT_AUX_R01';session=ui.Supervisor(base.ROOT,life,backend,config)
    record=backend.record(life);initial_tick=record['physical']['tick'];target=605663
    base.write(out/'PLAN_CERRADO_ANTES_CONTINUACION.json',{'schema':'APD04.same_REF_OMIT_future.continuation.R03',
        'authorization':'Root GO same AUX without recreation/restore; omit invalid read row; explicit Native aging to605663 if current is earlier; never rewind; then exactly3original probes.',
        'initial_record':record,'preserved_original_closure':closed,'target_age_tick':target,
        'owner_mode':'Start paused; explicit evolution and material requests remain owned. No automatic idle between requests, unlike original resumed A/B arms. Exact age mismatch declared.',
        'instrument_curriculum_revision_not_retroactive_history_match':True,
        'plan':base.plans('ref',None)[1:],'sources_manifest_sha256':sha(HERE/'FUENTES_CONTROLES_EJECUTADO_R01/MANIFEST_FUENTES.json'),
        'declared_documentary_revision':documentary})
    error=None;events=[];began=time.perf_counter()
    with ui.SessionLock(backend.protocol_home/life/'SUPERVISOR.lock'):
        try:
            opened=session.open(new=False);base.write(out/'MISMA_VIDA_ABIERTA.json',opened)
            if opened['world_id']!=record['world_id']:raise ValueError('Identity changed; no substitute allowed')
            base.write(out/'START_PAUSED.json',session.start())
            if initial_tick<target:
                rid='apd04_ctrl_ref_omit_r03_explicit_age_605663'
                age=backend.manager(['mente-unificada-continuar','--vida',life,'--ticks',str(target-initial_tick),'--id',rid,'--esperar','240'],timeout=270)
                base.write(out/'01_EDAD_NATIVA_EXPLICITA.json',age)
                if ui.row_of(age).get('status')!='completed':raise RuntimeError('Explicit age future unconfirmed; no requeue')
            else:base.write(out/'01_EDAD_NO_REBOBINADA.json',{'initial_tick':initial_tick,'target_tick':target,'mismatch':initial_tick!=target,'no_ticks_changed_externally':True})
            for serial,(event,row)in enumerate(base.plans('ref',None)[1:],2):
                rid='apd04_ctrl_ref_omit_r03_'+str(serial)+'_'+event.lower()
                r=session.material([row],feedback='omit',actuator='closed',request_id=rid[:90]);base.write(out/(str(serial).zfill(2)+'_'+event+'.json'),r)
                entry={'serial':serial,'event':event,'request_id':rid[:90],'status':ui.row_of(r).get('status'),'metrics':base.summary(r)}
                events.append(entry);print(json.dumps(entry,ensure_ascii=False),flush=True)
                if entry['status']!='completed':raise RuntimeError('Material future unconfirmed; preserve same ID')
            base.write(out/'GUARDAR.json',session.control('guardar'));base.write(out/'STOP.json',session.control('detener'))
        except BaseException as exc:
            error={'type':type(exc).__name__,'message':str(exc),'no_rewind_or_retry':True};base.write(out/'ERROR_PRESERVADO.json',error)
        finally:session.close()
    final=backend.record(life);sealer=load('original_complete_pair_sealer',base.ROOT/'laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/main/ejecutar_main_integrado_apd03_r01.py')
    target_pair=base.S/'estado/fuentes_emparejadas'/(life+'_T'+str(final['physical']['tick'])+'_R03')
    paired=sealer.stopped_pair(base.ROOT,ui,life,target_pair,allow_queued=False,scope='Exact reached SAME REF_OMIT future after preserved interface rejection and declared age/probe continuation, not a recreated P0 clone.')
    changed=[r['file']for r in revision if sha(base.S/r['file'])!=r['sha256']]
    base.write(out/'CIERRE_CONTINUACION.json',{'label':'REF_OMIT','life':life,'kind':'ref','condition':None,
        'prefix_snapshot_sha256':base.SNAPSHOT_SHA,'initial_tick':initial_tick,'declared_age_target':target,
        'final_tick':final['physical']['tick'],'snapshot_sha256':final['snapshot_sha256'],'elapsed_seconds':time.perf_counter()-began,
        'events':events,'error':error,'paired':paired,'source_changed':changed,'declared_documentary_revision':documentary,'continued_same_world_id':record['world_id']==final['world_id'],
        'original_interface_error_preserved':True,'source_revision':str(Path(__file__)),'not_exact_A_B_timing_or_dose_match':True})
    print(json.dumps({'REF_OMIT_SAME_LIFE_CLOSED':True,'tick':final['physical']['tick'],'error':error,'source_changed':changed},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
