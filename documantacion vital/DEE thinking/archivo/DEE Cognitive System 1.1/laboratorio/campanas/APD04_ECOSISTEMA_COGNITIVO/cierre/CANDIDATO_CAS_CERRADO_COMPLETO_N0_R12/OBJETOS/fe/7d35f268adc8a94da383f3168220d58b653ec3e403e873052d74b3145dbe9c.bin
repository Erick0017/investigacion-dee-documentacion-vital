"""Declared R02 actuator AUX driver. Default is N0 preparation, never Native.

Execution requires a later explicit --execute-after-go ROOT_GO_ACTUADOR_R02.
Uses existing full-pair importer, OriginalBackend, Supervisor and owned Jobs.
It does not decide an action, select a favorable reader or resubmit material.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import ast
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import threading
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
S = ROOT / 'sistema'
LAB = ROOT / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
EV = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
PROPOSAL = HERE / 'PROPUESTA_ACTUADOR_R02_R01'
PLAN = PROPOSAL / 'PLAN_DOS_AUX_CONGELADO_N0.json'
PLAN_SHA = '4839416a235cd82c51b237f6fc618da0c51f3c9c51eaa765d64fb4349c71dfbf'
PAIR = S / 'estado/fuentes_emparejadas/APD04_MAIN_T639374_EXPLORACION_R01'
PAIR_SHA = '5d938d56497571fb4af8ac814eac0cde59214814afb7f3d9280543ea074ca6db'
SNAPSHOT_SHA = '771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8'
MAX_NATIVE_OWNER_WALL_SECONDS = 900
BEGIN_CLOSING_AT_SECONDS = 740
MEMORY_LIMIT = 536870912


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_n0():
    if sha(PLAN) != PLAN_SHA:
        raise ValueError('Frozen plan bytes changed; no other plan is selected')
    plan = read(PLAN)
    protocol = load('actuator_proposal_literal_only_n0', PROPOSAL/'sistema/app/protocolo_apd04.py')
    for branch in plan['branches']:
        count = 0
        for event in branch['steps']:
            protocol.validate_literal(event['literal'])
            if event['literal']['modo']=='apd04-vivir':
                assert event['literal']=={'modo':'apd04-vivir','oportunidades':1,'sensor':'independent_balanced','lexico':True}
                count += 1
        assert count==10
    assert [branch['feedback'] for branch in plan['branches']]==['real','omit']
    assert sha(PAIR/'EXPORTACION_SERVICIO.json')==PAIR_SHA
    assert plan['parent_snapshot_sha256']==SNAPSHOT_SHA
    ast.parse(Path(__file__).read_text(encoding='utf8'))
    return plan


def prepare_only():
    plan = validate_n0()
    folder = EV/'ACTUADOR_R02_PREPARACION_N0_R01'
    if folder.exists():
        raise FileExistsError('N0 preparation already exists; no rewrite')
    folder.mkdir()
    shutil.copy2(Path(__file__),folder/Path(__file__).name)
    shutil.copy2(PLAN,folder/PLAN.name)
    proof = {
        'schema':'APD04.actuator_R02.driver.N0.preparation.v1',
        'created_utc':now(), 'source_sha256':sha(Path(__file__)), 'plan_sha256':sha(PLAN),
        'AUX_identities':[branch['life'] for branch in plan['branches']],
        'ten_individual_opportunities_each':True,'sensor':'R03 independent_balanced',
        'new_native_ticks':0,'Runtime_created':False,'shared_system_modified':False,
        'full_pair_manifest_sha256':sha(PAIR/'EXPORTACION_SERVICIO.json'),
        'native_execution_guard':'Requires later Root GO and installed proposal hashes exactly',
        'Native_owner_wall_limit_per_AUX_seconds':MAX_NATIVE_OWNER_WALL_SECONDS,
        'start_STOP_by_owner_wall_seconds':BEGIN_CLOSING_AT_SECONDS,
        'memory_limit_bytes':MEMORY_LIMIT,'threads':1,
        'stop_rules':['10 opportunities completed then old16+6 only if no pending and budget remains',
                      'transport terminal non-completion or uncertain state: preserve, no next material',
                      'unexpected owner exit or source mutation: preserve, no replacement',
                      'budget stop: one STOP, at900s terminate only own Job if needed'],
        'not_stop_rules':['wrong/unhelpful action alone','NULL emission alone','favorable/unfavorable branch score'],
        'scope':'Software preparation only. No guarantee that the two Native histories will finish within the limit.'}
    write(folder/'PREPARACION_N0.json',proof)
    print(json.dumps(proof,ensure_ascii=False,indent=2))


def freeze_sources(folder):
    members=[]
    for path in sorted(set(list(S.rglob('*.py'))+list((S/'contratos').glob('*.json')))):
        if '__pycache__'in path.parts:continue
        relative=path.relative_to(S)
        target=folder/'sistema'/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        before=sha(path);shutil.copy2(path,target)
        if sha(path)!=before or sha(target)!=before:raise ValueError('Sources changed while freezing; no owner launched')
        members.append({'file':relative.as_posix(),'sha256':before,'bytes':path.stat().st_size})
    shutil.copy2(Path(__file__),folder/Path(__file__).name)
    shutil.copy2(PLAN,folder/PLAN.name)
    write(folder/'MANIFIESTO_FUENTES.json',{'captured_before_native':True,'members':members,
        'driver_sha256':sha(Path(__file__)),'plan_sha256':PLAN_SHA})
    return members


def primary_summary(result):
    """Post-result bookkeeping only; never used to choose an action or reader."""
    actual=result.get('result',result)
    while isinstance(actual,dict) and 'result'in actual and 'rows'not in actual:
        actual=actual['result']
    return {'top_keys':list(actual) if isinstance(actual,dict)else type(actual).__name__}


def run_branch(ui, branch, config, frozen, revision):
    life=branch['life'];folder=EV/'ACTUADOR_R02_AUX_R01'/life
    if folder.exists() or(S/'estado/vidas'/life).exists():raise FileExistsError('Named AUX exists; never repeat/import over its future')
    folder.mkdir(parents=True)
    write(folder/'PLAN_ANTES_NATIVE.json',{'branch':branch,'parent_snapshot_sha256':SNAPSHOT_SHA,
        'max_native_owner_wall_seconds':MAX_NATIVE_OWNER_WALL_SECONDS,'close_begin_seconds':BEGIN_CLOSING_AT_SECONDS,
        'no_T0_or_cache_reset':True,'new_source_revision':revision.name})
    backend=ui.OriginalBackend(ROOT,dict(config));session=ui.Supervisor(ROOT,life,backend,dict(config))
    owner_started=None;watcher_stop=threading.Event();watcher=None;stop_attempted=False
    material_results=[];termination_reason='not_started';closed=None

    def observe_owned_host():
        # Host-only sampling. This thread never queries a DEE state or submits an input.
        with(folder/'HOST_RESOURCES.jsonl').open('x',encoding='utf8')as stream:
            while not watcher_stop.is_set():
                process,job=backend.process,backend.job
                if process is not None and job is not None:
                    elapsed=time.monotonic()-owner_started
                    row={'wall_utc':now(),'owner_elapsed_seconds':elapsed,'pid':process.pid,
                         'exit_code':process.poll(),'resources':backend.pc.job_resources(job)}
                    stream.write(json.dumps(row,separators=(',',':'))+'\n');stream.flush()
                    if elapsed>=MAX_NATIVE_OWNER_WALL_SECONDS and process.poll()is None:
                        write(folder/'CIERRE_HARD_BUDGET_OWN_JOB.json',{
                            'wall_utc':now(),'elapsed_seconds':elapsed,'resources':row['resources'],
                            'pending_transport_id':(session.state.get('pending_material')or{}).get('id'),
                            'reason':'Declared900s own-Native budget; not a cognitive failure criterion',
                            'one_STOP_was_attempted':stop_attempted})
                        backend.pc.terminate_job(job,124)
                        return
                    if process.poll()is not None:return
                watcher_stop.wait(.5)

    def request_once(label, row, feedback):
        # material() submits once; all following reads use the exact same id.
        if time.monotonic()-owner_started>=BEGIN_CLOSING_AT_SECONDS:
            raise TimeoutError('Declared owner budget reserved for closure; no new material submitted')
        request_id='apd04_actuator_'+('real'if branch['feedback']=='real'else'omit')+'_'+label
        intent={'id':request_id,'row':row,'feedback':feedback,'actuator':'closed','utc':now()}
        write(folder/('INTENCION_'+label+'.json'),intent)
        try:
            value=session.material([row],feedback=feedback,actuator='closed',request_id=request_id)
        except subprocess.TimeoutExpired as error:
            write(folder/('CLIENT_TIMEOUT_'+label+'.json'),{'id':request_id,'error':repr(error),
                 'only_follow_up_read_same_id':True,'new_material_retry':False})
            value=session.result(request_id)
        while ui.row_of(value).get('status')not in ui.TERMINAL:
            write_once=folder/('PRIMER_RESULTADO_PENDIENTE_'+label+'.json')
            if not write_once.exists():write(write_once,value)
            if time.monotonic()-owner_started>=BEGIN_CLOSING_AT_SECONDS:
                write(folder/('PENDIENTE_PRESERVADO_'+label+'.json'),{'id':request_id,'result':value,'utc':now(),
                    'scope':'Budget cutoff, not a wrong action, replay or failed Native experiment verdict'})
                raise TimeoutError('Same material id remains pending at the declared closing window')
            if backend.process.poll()is not None:
                raise RuntimeError('Own owner exited; preserve exact pending id, no replacement')
            time.sleep(2)
            value=session.result(request_id)
        write(folder/('RESULTADO_'+label+'.json'),value)
        material_results.append({'id':request_id,'label':label,'status':ui.row_of(value).get('status'),
                                 'summary':primary_summary(value)})
        if ui.row_of(value).get('status')!='completed':
            raise RuntimeError('Terminal material non-completion; preserve and stop without another opportunity')
        return value

    with ui.SessionLock(backend.protocol_home/life/'SUPERVISOR.lock'):
        try:
            card=session.open(new=True)
            if card['parent']['encoded_sha256']!=SNAPSHOT_SHA:raise ValueError('Imported identity differs from exact complete prefix')
            write(folder/'IMPORTACION_COMPLETA.json',card)
            owner_started=time.monotonic()
            watcher=threading.Thread(target=observe_owned_host,name='own-host-budget-only',daemon=True);watcher.start()
            write(folder/'START.json',session.start())
            write(folder/'REANUDAR.json',session.control('reanudar'))
            for number,event in enumerate(branch['steps'],1):
                request_once(str(number).zfill(2),event['literal'],event['feedback'])
            termination_reason='ten_opportunities_completed'
            # This is an explicit material diagnostic, not a passive assertion of retention.
            if not session.state.get('pending_material') and time.monotonic()-owner_started<BEGIN_CLOSING_AT_SECONDS-160:
                request_once('old16_MA6',{'modo':'apd03-panel','nuevas':True,'memorias':True},'omit')
            else:
                write(folder/'OLD_PANEL_NO_ENVIADO.json',{'reason':'Pending state or declared time reserve for closing',
                    'not_a_retention_failure':True,'utc':now()})
            if not session.state.get('pending_material') and time.monotonic()-owner_started<BEGIN_CLOSING_AT_SECONDS:
                write(folder/'GUARDAR.json',session.control('guardar'))
        except BaseException as error:
            termination_reason=type(error).__name__+': '+str(error)
            write(folder/'ESTADO_AL_DETENER_PLAN.json',{'error':repr(error),'traceback':traceback.format_exc(),
                'utc':now(),'pending_protocol':session.state.get('pending_material'),
                'no_reimport_no_requeue_no_restore':True})
        finally:
            if session.owned and backend.process is not None:
                stop_attempted=True
                write(folder/'INTENCION_STOP_UNICO.json',{'utc':now(),'reason':termination_reason,
                    'owner_elapsed_seconds':time.monotonic()-owner_started,
                    'pending_transport':session.state.get('pending_material'),
                    'resources':backend.pc.job_resources(backend.job)})
                try:
                    write(folder/'STOP.json',session.control('detener'))
                    closed={'confirmed_by_standard_protocol':True}
                except BaseException as error:
                    write(folder/'STOP_NO_CONFIRMADO.json',{'utc':now(),'error':repr(error),
                        'one_STOP_only':True,'do_not_call_session_close_again':True})
                    # Wait only inside the already fixed own-owner900s horizon.
                    while backend.process is not None and backend.process.poll()is None and time.monotonic()-owner_started<MAX_NATIVE_OWNER_WALL_SECONDS:
                        time.sleep(.5)
                    if backend.process is not None and backend.process.poll()is None:
                        backend.pc.terminate_job(backend.job,124)
                    if backend.process is not None:
                        try:closed=backend.finish_owned(10)
                        except BaseException as finish_error:closed={'confirmed':False,'error':repr(finish_error)}
                    session.owned=False
            watcher_stop.set()
            if watcher is not None:watcher.join(timeout=2)
    record=backend.record(life)
    result={'life':life,'feedback':branch['feedback'],'termination_reason':termination_reason,
        'material_results':material_results,'stop_attempted_once':stop_attempted,'closed':closed,
        'owner_elapsed_seconds':None if owner_started is None else time.monotonic()-owner_started,
        'final_committed_tick':record['physical']['tick'],'snapshot_sha256':record['snapshot_sha256'],
        'final_VIDA_record':record,'pending_protocol':session.state.get('pending_material'),
        'sources_changed':[row['file']for row in frozen if sha(S/row['file'])!=row['sha256']],
        'Native_learning_not_implied_by_P0_codec':True}
    write(folder/'CIERRE.json',result)
    return result


def execute(branch_selector):
    plan=validate_n0()
    for row in read(PROPOSAL/'MANIFIESTO_PROPUESTA_N0.json')['source_and_proposed']:
        if sha(ROOT/row['file'])!=row['proposed']['sha256']:
            raise ValueError('Root has not installed exact accepted proposal; no Native owner starts: '+row['file'])
    chosen=[branch for branch in plan['branches']if branch_selector=='both'or branch['feedback']==branch_selector]
    for branch in chosen:
        if(S/'estado/vidas'/branch['life']).exists():raise FileExistsError('The chosen AUX already exists; no repeat')
    folder=EV/'ACTUADOR_R02_AUX_R01'
    if folder.exists():raise FileExistsError('Driver output already exists; preserve it')
    folder.mkdir()
    revision=LAB/'revisiones/ACTUADOR_R02_AUX_R01_EJECUTADO'
    if revision.exists():raise FileExistsError('Source revision already exists; no overwrite')
    revision.mkdir(parents=True)
    frozen=freeze_sources(revision)
    verifier=load('actuator_existing_pair_verifier',S/'app/importacion_emparejada.py')
    _,manifest,proof=verifier.verify_export(PAIR)
    if manifest['snapshot_sha256']!=SNAPSHOT_SHA or manifest['physical']['tick']!=639374:
        raise ValueError('Full-pair verification differs from predefined parent')
    write(folder/'PREFIJO_VERIFICADO.json',proof)
    ui=load('actuator_existing_single_entry',S/'app/usar_dee.py')
    config=ui.read(S/'contratos/ENTRADA_SENCILLA_APD03.json')
    config.update(source_alias='APD04_EXPLORACION_T639374',source_life='APD04_MAIN',source_tick=639374,
        source_snapshot_sha256=SNAPSHOT_SHA,paired_export_manifest_sha256=PAIR_SHA,
        source_paired_export_manifest=(PAIR/'EXPORTACION_SERVICIO.json').relative_to(ROOT).as_posix(),
        material_wait_seconds=20,control_wait_seconds=120,owner_max_seconds=900,
        memory_limit_bytes=MEMORY_LIMIT)
    write(folder/'CONFIGURACION_LOCAL_NO_INSTALADA.json',config)
    control=load('actuator_existing_owned_process_control',S/'app/process_control.py')
    control.protect_current(output=folder/'RECURSOS_DRIVER.json',memory_limit=MEMORY_LIMIT)
    results=[]
    for branch in chosen:
        result=run_branch(ui,branch,config,frozen,revision);results.append(result)
        if result['sources_changed']:raise ValueError('Shared sources changed; no next Native branch')
        if result['closed']is None or result['closed'].get('confirmed')is False:
            raise RuntimeError('Owner closure not confirmed; do not start another branch')
    write(folder/'CIERRE_DOS_AUX.json',{'branches':results,'one_common_prefix_not_independent':True,
        'MAIN_or_ACTIVO_modified':False,'no_aggregate_mind_claim':True})
    print(json.dumps([{'life':r['life'],'tick':r['final_committed_tick'],'closure':r['closed'],
        'termination':r['termination_reason']}for r in results],ensure_ascii=False,indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute-after-go',choices=('ROOT_GO_ACTUADOR_R02',))
    parser.add_argument('--branch',choices=('real','omit','both'),default='both')
    options=parser.parse_args()
    if options.execute_after_go is None:prepare_only()
    else:execute(options.branch)


if __name__=='__main__':main()
