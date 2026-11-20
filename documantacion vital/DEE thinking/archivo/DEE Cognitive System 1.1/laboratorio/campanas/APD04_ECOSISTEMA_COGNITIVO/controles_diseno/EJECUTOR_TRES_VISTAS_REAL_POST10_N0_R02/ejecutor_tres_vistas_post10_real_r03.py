"""N0 assembly; future explicit Root-gated FULL preparation / one-arm execution.

Reuses OriginalBackend/Supervisor, paired importer, literal R04 Job wrapper and
existing exact postSTOP sealer. No actor policy or new Native runtime manager.
Never substitutes post10OMIT or a favorable earlier prefix for post10REAL.
"""
import argparse
import ast
from contextlib import contextmanager
from collections import Counter
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

ROOT=next(p for p in Path(__file__).resolve().parents if(p/'sistema/gestionar.py').is_file())
S=ROOT/'sistema';LAB=ROOT/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
EV=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
CTRL=LAB/'controles_diseno'
DESIGN=CTRL/'PROPUESTA_TRES_BRAZOS_VISTA_REAL_POST10_N0_R02'
DSHA='e074cfb8b1ae630a365f9ab25eae1970653618df27c4022f92d6c8681088b539'
SOURCE=LAB/'native_candidates/EJECUTOR_WAIT_R03_SAFE_R03'
PATCH=LAB/'native_candidates/PROPUESTA_VISTA_INSPECCION_PERSISTENTE_N0_R01'
PSHA='d746f0612f1ede4dea72e00a8ac4941d56540833670b52cab3cbc0d86b3ea53c'
BUNDLE=CTRL/'EJECUTOR_TRES_VISTAS_REAL_POST10_N0_R02'
PREP=EV/'VISTA_POST10_PREPARACION_N0_R02'
ORIGINAL=EV/'WAIT_R03_REAL_ORIGINAL_R03'
REAL='APD04_WAIT_R03_REAL_AUX_R05'
ARMS=('CIRCULAR_REAL','PERSISTENTE_REAL','PERSISTENTE_OMIT')
SEALER=LAB/'ejecucion/sellar_corte_poststop_apd04_n0_r01.py'


def read(p):return json.loads(Path(p).read_bytes())
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def emit(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m
def request_rows(p):
    p=Path(p);wal=p.with_name(p.name+'-wal')
    if wal.exists()and wal.stat().st_size:raise ValueError('Nonempty live WAL; no immutable shortcut')
    with sqlite3.connect(p.as_uri()+'?mode=ro&immutable=1',uri=True)as con:
        return con.execute('SELECT id,payload,payload_sha,status,result FROM requests ORDER BY id').fetchall()
def verify_inputs(installed=False):
    if sha(DESIGN/'MANIFIESTO.json')!=DSHA or sha(PATCH/'MANIFIESTO_PROPUESTA_N0.json')!=PSHA:raise ValueError('Prospective design/source changed')
    for x in read(DESIGN/'MANIFIESTO.json')['members']:
        if sha(DESIGN/x['file'])!=x['sha256']:raise ValueError('Literal design member changed')
    for x in read(PATCH/'MANIFIESTO_PROPUESTA_N0.json')['members']:
        if sha(PATCH/x['file'])!=x['proposed_sha256']:raise ValueError('Proposed body bytes changed')
        if installed and sha(ROOT/x['file'])!=x['proposed_sha256']:raise ValueError('Root exact joint source patch not installed; no Native')
def bundle_verified():
    for x in read(BUNDLE/'MANIFIESTO_N0.json')['members']:
        if sha(BUNDLE/x['file'])!=x['sha256']:raise ValueError('Prepared executor bytes changed')
def work_ids(plan):return{e['request_id']for e in plan['events']if e.get('situations',[{}])[0].get('modo')=='apd04-vivir'}
def completed_work(events,ids):
    return[e for e in events if e.get('kind')=='scheduled_material_result'and e.get('requested_id')in ids
        and e['result'].get('request',e['result']).get('status')=='completed']


def assemble_n0():
    verify_inputs()
    if BUNDLE.exists():raise FileExistsError('Preserve executor revision')
    BUNDLE.mkdir()
    copies=[(Path(__file__),'ejecutor_tres_vistas_post10_real_r03.py'),
        (SOURCE/'ejecutar_plan_apd04_r04.py','ejecutar_plan_apd04_r04.py'),
        (SOURCE/'supervisar_plan_apd04_r04.py','supervisar_plan_apd04_r04.py'),
        (SEALER,'FUENTES_EXISTENTES/sellar_corte_poststop_apd04_n0_r01.py'),
        (ROOT/'laboratorio/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION/main/ejecutar_main_integrado_apd03_r01.py','FUENTES_EXISTENTES/sealer_APD03.py')]
    for p in DESIGN.iterdir():
        if p.is_file():copies.append((p,'DISENO_R02/'+p.name))
    # Exact relevant current sources, not a new inventory of all historical S.
    first=read(DESIGN/'PLAN_CIRCULAR_REAL_DRAFT_R02.json')
    source_paths=list(dict.fromkeys(first['freeze_source_paths']+['sistema/app/importacion_emparejada.py','sistema/app/process_control.py']))
    for rel in source_paths:copies.append((ROOT/rel,'FUENTES_S_CONGELADAS/'+rel.removeprefix('sistema/')))
    provenance=[]
    for src,rel in copies:
        dst=BUNDLE/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
        if sha(src)!=sha(dst):raise ValueError('Source copy differs')
        provenance.append({'original':str(src),'copy':rel,'sha256':sha(src)})
    driver=load('vista_R04_static_validator_only',BUNDLE/'ejecutar_plan_apd04_r04.py')
    ui=load('vista_proposed_UI_parser_only',PATCH/'sistema/app/usar_dee.py')
    proto=load('vista_proposed_protocol_only',PATCH/'sistema/app/protocolo_apd04.py')
    checks=[]
    for arm in ARMS:
        p=read(DESIGN/('PLAN_'+arm+'_DRAFT_R02.json'));t=copy.deepcopy(p)
        t.update(status='CLOSED_FOR_EXECUTION',initial_snapshot_sha256='0'*64,initial_tick=0);driver.validate_plan(t)
        for e in p['events']:
            if e['kind']=='command':ui.literal_rows(ui.command_parser().parse_args(e['argv']))
            elif e['kind']=='material':
                for r in e['situations']:proto.validate_literal(r)
        checks.append({'arm':arm,'work':len(work_ids(p)),'actual_parent_not_read_or_invented':True,'static_literals_valid':True})
    emit(BUNDLE/'VALIDACION_Y_COMANDOS_N0.json',{'schema':'APD04.three_views.executor.N0.R02','Native_ticks':0,
        'owners_started':0,'lives_created_or_imported':0,'shared_S_edited':False,'checks':checks,'exact_sources':provenance,
        'future_commands':{
            'prepare_actual_FULL_only':'motor/python313/python.exe -I -B EJECUTOR/ejecutor_tres_vistas_post10_real_r03.py --prepare-after-go ROOT_GO_VIEW_POST10_REAL_FULL_N0',
            'execute_ONE_explicit_arm':'motor/python313/python.exe -I -B EJECUTOR/ejecutor_tres_vistas_post10_real_r03.py --execute-after-go ROOT_GO_VIEW_POST10_SIX_NATIVE_R02 --arm PERSISTENTE_REAL'},
        'commands_are_not_execution_authorization':True,
        'concurrency':'One new view owner per invocation, at most TWO view slots under existing SessionLock OS file locks. Before Native, count live WorldLock PIDs conservatively, require<=1 other active/unknown owner. Root explicitly schedules PERSISTENTE_REAL plus CIRCULAR_REAL first, OMIT later, with Native panel waiting. Root must coordinate any other independent launches so total<=2; never terminate other owners.',
        'actual_parent_required':'Only ORIGINAL REAL R03 post10 clean FULL seal; actual hash/tick are read later, never SAFE/OMIT/favorable future. Circular original must still equal that cut.',
        'guard':'Existing LABR04 min240/local600/hard900/closing300 and fixed absolute deadline03:30:51UTC. Adverse outputs and guard cuts remain preserved; no replay.'})
    emit(BUNDLE/'MANIFIESTO_N0.json',{'self_hash_excluded':True,'members':[{'file':p.relative_to(BUNDLE).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(BUNDLE.rglob('*'))if p.is_file()]})
    if any(k.startswith('dee_thinking')for k in sys.modules):raise RuntimeError('N0 imported Native')
    print(json.dumps({'bundle':str(BUNDLE),'manifest_sha256':sha(BUNDLE/'MANIFIESTO_N0.json'),'Native_ticks':0,'actual_parent_not_accessed':True}))


def actual_real_parent():
    final=read(ORIGINAL/'TRAYECTORIA/RESULTADO.json')
    if(final['error']or not final['owner_stop_confirmed']or not final['frozen_sources_unchanged']
        or final['final_protocol'].get('pending_material')or final['final_protocol'].get('uncertain_preserved')):
        raise ValueError('REAL actual future not clean/utilizable; no OMIT or earlier-prefix replacement')
    plan=read(SOURCE/'PLAN_WAIT_R03_REAL_ORIGINAL_CERRADO_R03.json')
    events=[json.loads(x)for x in(ORIGINAL/'TRAYECTORIA/EVENTOS.jsonl').read_text(encoding='utf8').splitlines()]
    if len(completed_work(events,work_ids(plan)))!=10:raise ValueError('Actual REAL did not complete ten work IDs')
    seal_path=ORIGINAL/'SELLO_POST10_N0/CORTE_COMPLETO_POSTSTOP.json';seal=read(seal_path)
    if seal['new_native_ticks']!=0 or seal['new_owner_started']is not False:raise ValueError('Unexpected post10 seal')
    pair=Path(seal['pair']['directory']).resolve(strict=True)
    if not pair.is_relative_to((S/'estado/fuentes_emparejadas').resolve()):raise ValueError('Unexpected pair repository')
    if sha(pair/'EXPORTACION_SERVICIO.json')!=seal['pair']['manifest_sha256']:raise ValueError('Actual paired manifest changed')
    verifier=load('vista_existing_full_pair_verifier',S/'app/importacion_emparejada.py')
    _,m,v=verifier.verify_export(pair)
    if(m['life_id']!=REAL or m['snapshot_sha256']!=final['final_record']['snapshot_sha256']
        or m['physical']['tick']!=final['final_record']['physical']['tick']):raise ValueError('Not exact actual REAL post10')
    ui=load('vista_existing_UI_only',S/'app/usar_dee.py')
    observer=load('vista_offline_snapshot_only',S/'capacidades/observador_causal_retrospectivo_01.py')
    parent=observer.Snapshot(pair/'VIDA.deetsnap.gz',verify_checksum=False)
    env=json.loads(parent.metadata['DEE.Cognitive.System.1.1.APD04.ecosystem.R01'])
    if(parent.pending or env['in_progress']is not None or len(env['objects'])!=2 or env.get('action_codec')!='R03'
        or env.get('view_policy','circular_R01')!='circular_R01'):
        raise ValueError('Actual parent lacks declared quiescent R03 circular two-source domain')
    return final,seal_path,pair,m,v,ui,observer,parent


def prepare_after_go():
    verify_inputs(installed=True);bundle_verified()
    if PREP.exists():raise FileExistsError('Prior preparation preserved; never silently reimport')
    final,sealpath,pair,manifest,verified,ui,observer,parent=actual_real_parent()
    current=read(S/'estado/vidas'/REAL/'VIDA.json')
    if current['snapshot_sha256']!=manifest['snapshot_sha256']or current['physical']['tick']!=parent.tick:
        raise ValueError('Circular original advanced after post10; no rewind/favorable substitution')
    if(S/'estado/locks'/(REAL+'.lock')).exists():raise ValueError('REAL owner not stopped')
    parent_requests=request_rows(pair/'cola.sqlite3')
    if request_rows(S/'estado/servicios_persistentes'/REAL/'cola.sqlite3')!=parent_requests:
        raise ValueError('Original transport differs from exact post10 cut')
    config=dict(ui.read(ui.selected_config_path(ROOT)))
    config.update(source_alias='APD04_VIEW_EXACT_REAL_POST10',source_life=REAL,source_tick=parent.tick,
        source_snapshot_sha256=manifest['snapshot_sha256'],paired_export_manifest_sha256=sha(pair/'EXPORTACION_SERVICIO.json'),
        source_paired_export_manifest=(pair/'EXPORTACION_SERVICIO.json').relative_to(ROOT).as_posix())
    first=read(DESIGN/'PLAN_CIRCULAR_REAL_DRAFT_R02.json')
    frozen={str(ROOT/p):sha(ROOT/p)for p in first['freeze_source_paths']}
    protected={str(S/'estado/ACTIVO.json'):sha(S/'estado/ACTIVO.json'),str(pair/'EXPORTACION_SERVICIO.json'):sha(pair/'EXPORTACION_SERVICIO.json'),
        str(pair/'VIDA.deetsnap.gz'):sha(pair/'VIDA.deetsnap.gz')}
    PREP.mkdir();emit(PREP/'ANTES_N0.json',{'actual_REAL_post10_pair':str(pair),'parent_snapshot_SHA':parent.encoded_sha256,'parent_tick':parent.tick,
        'pair_manifest_SHA':sha(pair/'EXPORTACION_SERVICIO.json'),'seal_source_SHA':sha(sealpath),'verification':verified,
        'local_config_not_installed':config,'frozen_sources':frozen,'protected':protected,'Native_ticks':0,'owners_started':0})
    driver=load('vista_existing_R04_validate',BUNDLE/'ejecutar_plan_apd04_r04.py');cards=[]
    # Both persistent forks use this immutable pair, never a later circular cut.
    for arm in ARMS:
        p=read(DESIGN/('PLAN_'+arm+'_DRAFT_R02.json'));life=p['life']
        backend=ui.OriginalBackend(ROOT,dict(config));session=ui.Supervisor(ROOT,life,backend,dict(config))
        with ui.SessionLock(backend.protocol_home/life/'SUPERVISOR.lock'):
            if arm=='CIRCULAR_REAL':card=backend.record(life)
            else:
                if(S/'estado/vidas'/life).exists():raise FileExistsError('Future identity already exists; no reimport')
                card=session.open(new=True)
        child=observer.Snapshot(S/card['snapshot'],verify_checksum=False)
        equal=parent.raw==child.raw and parent.clocks==child.clocks and parent.channels==child.channels and parent.pending==child.pending and parent.receipts==child.receipts
        env_equal=parent.metadata['DEE.Cognitive.System.1.1.APD04.ecosystem.R01']==child.metadata['DEE.Cognitive.System.1.1.APD04.ecosystem.R01']
        if not equal or not env_equal or child.tick!=parent.tick:raise ValueError('Physical/operational parent mismatch')
        if request_rows(S/'estado/servicios_persistentes'/life/'cola.sqlite3')!=parent_requests:raise ValueError('Exact inherited request rows differ')
        if session.state.get('pending_material')or session.state.get('uncertain_preserved'):raise ValueError('Unresolved imported protocol')
        if backend.process is not None or backend.job is not None or session.owned:raise ValueError('N0 started owner')
        proof={'arm':arm,'record':card,'protocol':session.state,'actual_parent_pair':str(pair),'parent_snapshot_SHA':parent.encoded_sha256,
            'parent_tick':parent.tick,'RAW_clocks_channels_pending_receipts_equal':True,'environment_equal':True,'transport_rows_equal':True,
            'Native_ticks':0,'owner_started':False,'knowledge_inherited_not_new_learning':True}
        emit(PREP/(arm+'_PREPARACION_N0.json'),proof)
        p.update(status='CLOSED_FOR_EXECUTION',initial_snapshot_sha256=card['snapshot_sha256'],initial_tick=card['physical']['tick'],world_id=card['world_id'],
            n0_import_proof=(PREP/(arm+'_PREPARACION_N0.json')).relative_to(ROOT).as_posix(),native_GO_still_required=True)
        p['required_actual_parent'].update(snapshot_sha256=parent.encoded_sha256,tick=parent.tick,
            complete_pair_manifest_sha256=sha(pair/'EXPORTACION_SERVICIO.json'),pair_local_path=str(pair),not_yet_exists_as_post10=False)
        driver.validate_plan(p);emit(PREP/('PLAN_'+arm+'_CERRADO_R02.json'),p);cards.append(proof)
    if not all(sha(p)==h for p,h in protected.items())or not all(sha(p)==h for p,h in frozen.items()):raise ValueError('N0 modified protected/source files')
    emit(PREP/'CIERRE_PREPARACION_N0.json',{'arms':cards,'Native_ticks':0,'owners_started':0,'protected_unchanged':True,
        'sources_unchanged':True,'no_execution_authorization':True,'same_actual_REAL_parent_for_all':True})
    if any(k.startswith('dee_thinking')for k in sys.modules):raise RuntimeError('N0 imported Native')
    print(json.dumps({'prepared':str(PREP),'Native_ticks':0,'parent_tick_actual':parent.tick,'arms':list(ARMS)}))


def passive_live_world_locks():
    """Read-only OS liveness; stale/unknown files are NEVER deleted or killed."""
    import ctypes
    from ctypes import wintypes
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];k.OpenProcess.restype=wintypes.HANDLE
    k.GetExitCodeProcess.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)];k.CloseHandle.argtypes=[wintypes.HANDLE]
    k.GetProcessTimes.argtypes=[wintypes.HANDLE]+[ctypes.POINTER(wintypes.FILETIME)]*4
    rows=[]
    for p in sorted((S/'estado/locks').glob('*.lock')):
        try:
            value=read(p);pid=int(value['pid']);handle=k.OpenProcess(0x1000,False,pid)
            if not handle:
                error=ctypes.get_last_error();state='dead'if error in(87,1168)else'unknown'
            else:
                code=wintypes.DWORD();ok=k.GetExitCodeProcess(handle,ctypes.byref(code))
                created,exited,kernel,user=[wintypes.FILETIME()for _ in range(4)]
                timeok=k.GetProcessTimes(handle,*[ctypes.byref(x)for x in(created,exited,kernel,user)])
                k.CloseHandle(handle);state=('alive'if code.value==259 else'dead')if ok else'unknown';error=None
                if state=='alive'and timeok:
                    born_ns=(((created.dwHighDateTime<<32)|created.dwLowDateTime)-116444736000000000)*100
                    if born_ns>p.stat().st_mtime_ns:state='pid_reused_not_lock_owner'
            rows.append({'world':p.stem,'pid':pid,'state':state,'OS_error':error})
        except Exception as exc:rows.append({'world':p.stem,'state':'unknown','error':str(exc)})
    return rows


def walk(v):
    yield v
    if isinstance(v,dict):
        for key,x in v.items():
            if key in('result','result_json')and isinstance(x,str):
                try:x=json.loads(x)
                except json.JSONDecodeError:pass
            yield from walk(x)
    elif isinstance(v,list):
        for x in v:yield from walk(x)
def raw_sign(reader):
    obs=reader['observations'];expected={(25+2*x,15,53):(x,[x,1,0])for x in(-1,0,1)}
    if len(obs)!=3 or{tuple(o['site'])for o in obs}!=set(expected):raise ValueError('Selector gate coverage changed')
    candidates=[]
    for o in obs:
        raw=int(o['raw'])
        if not 0<=raw<2**64:raise ValueError('Invalid uint64 RAW')
        st=raw&0xffffffff;sem=(raw>>60)&15
        direction=[((raw>>b)&15)-(16 if((raw>>b)&15)>=8 else 0)for b in(48,52,56)]
        sign,d=expected[tuple(o['site'])]
        if st and sem==1 and direction==d:candidates.append(sign)
    return candidates[0]if len(candidates)==1 else None
def archived_summary(journal):
    rows={};issues=[]
    if not journal.exists():return{'rows':[],'opportunities_completed':None,'actions':{},
        'issues':['No journal published; process failure is not a cognitive outcome.']}
    for line,b in enumerate(journal.read_bytes().splitlines(),1):
        try:top=json.loads(b)
        except json.JSONDecodeError:
            issues.append('Incomplete preserved final JSONL line'+str(line));continue
        for n in walk(top):
            if not isinstance(n,dict)or not{'public_before','committed_effect','selection'}<=set(n):continue
            key=(n['episode'],n['selection'].get('query_tick'))
            if key in rows:continue
            reader=n['selection']['reader'];sign=raw_sign(reader);action={-1:'INSPECT',0:'WAIT',1:'USE'}.get(sign)
            if sign!=n['selection']['physical_choice']or action!=n['physical_action']:issues.append({'episode':n['episode'],'RAW_selector_mismatch':True})
            q=n.get('posteffect_quality');e=n['committed_effect']
            if q and action=='WAIT':
                expected=sign==0 and n['public_before']['tag']!=n['public_before']['goal_tag']and q['task_env_before']==q['task_env_after']
                if expected!=q['new_quality']:issues.append({'episode':n['episode'],'WAITquality_mismatch':True})
            rows[key]={'episode':n['episode'],'query_tick':key[1],'RAW_sign':sign,'action':action,'public':n['public_before'],
                'effect':e,'posteffect_quality':q,'view_policy':n.get('view_policy','circular_R01'),
                'cursor_before':n.get('cursor_before'),'cursor_after':n.get('cursor_after'),'feedback':n['feedback'],
                'primary_journal_line':line,'not_a_complete_causal_autopsy':True}
    rr=list(rows.values())
    return{'rows':rr,'issues':issues,'Native_queries_requested_in_plan':6,'opportunities_completed':len(rr),
        'actions':dict(Counter(str(x['action'])for x in rr)),'old_gain_reported':sum(bool(x['effect'].get('old_work_gain',x['effect']['useful']))for x in rr),
        'new_WAITquality_reported':sum(bool(x['effect'].get('new_quality'))for x in rr),
        'scope':'N0 RAW selection check plus preserved metric witnesses. Final FULL receipt union and fresh/correct/maintenance analyses remain separate. P0 view improvement alone is not learning.'}


@contextmanager
def existing_two_view_slots(ui):
    """Only orchestration locks, not actor state or target-aware scheduling."""
    for i in(0,1):
        lock=ui.SessionLock(EV/('VISTA_POST10_NATIVE_SLOT_'+str(i)+'_R02.lock'))
        try:lock.__enter__()
        except RuntimeError:continue
        try:yield i
        finally:lock.__exit__(None,None,None)
        return
    raise RuntimeError('Both authorized view Native slots occupied; no third owner launched')


def execute_one_after_go(arm):
    if sys.version_info[:2]!=(3,13):raise ValueError('Use existing compatible motor/python313/python.exe')
    verify_inputs(installed=True);bundle_verified();prepared=read(PREP/'CIERRE_PREPARACION_N0.json')
    if not prepared['same_actual_REAL_parent_for_all']:raise ValueError('Wrong parent preparation')
    ppath=PREP/('PLAN_'+arm+'_CERRADO_R02.json');p=read(ppath);life=p['life']
    card=read(S/'estado/vidas'/life/'VIDA.json')
    if(card['snapshot_sha256']!=p['initial_snapshot_sha256']or card['physical']['tick']!=p['initial_tick']):raise ValueError('Prepared life already changed; no rewind/replay')
    frozen=read(PREP/'ANTES_N0.json')['frozen_sources']
    if not all(sha(path)==h for path,h in frozen.items()):raise ValueError('Prepared shared source changed; no Native')
    out=EV/('VISTA_POST10_'+arm+'_R02')
    if out.exists():raise FileExistsError('Attempted future preserved; no rerun')
    ui=load('vista_existing_group_exclusion',S/'app/usar_dee.py')
    with existing_two_view_slots(ui)as slot:
        locks=passive_live_world_locks();active=[x for x in locks if x['state']not in('dead','pid_reused_not_lock_owner')]
        if any(x['world']==life for x in active)or len(active)>1:
            raise RuntimeError('No Native launch: live/unknown other-world locks exceed one: '+str(active))
        gate=EV/('VISTA_POST10_'+arm+'_ANTES_NATIVE_R02.json')
        emit(gate,{'plan_SHA':sha(ppath),'life':life,'exact_snapshot_SHA':card['snapshot_sha256'],'OS_lock_liveness':locks,
            'one_new_owner_only':True,'view_slot':slot,'global_max2_requires_Root_coordination':True,'frozen_source_hashes':frozen,
            'no_responses_or_targets_used_for_scheduling':True})
        cmd=[sys.executable,'-I','-B','-X','utf8',str(BUNDLE/'supervisar_plan_apd04_r04.py'),
            '--root',str(ROOT),'--plan',str(ppath),'--out',str(out),'--root-go','APD04_LITERAL_PLAN_CLOSED']
        env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
        code=subprocess.run(cmd,cwd=Path(sys.executable).parent,env=env).returncode
        supervision=read(out/'RESULTADO_SUPERVISION.json')if(out/'RESULTADO_SUPERVISION.json').exists()else None
        final=read(out/'TRAYECTORIA/RESULTADO.json')if(out/'TRAYECTORIA/RESULTADO.json').exists()else None
        try:summary=archived_summary(out/'TRAYECTORIA/EVENTOS.jsonl')
        except Exception as exc:summary={'rows':[],'opportunities_completed':None,'issues':[{'N0_summary_error':type(exc).__name__,'message':str(exc)}],
            'no_inference_of_Native_failure_from_this_instrument_error':True}
        seal=None;seal_error=None
        if(final and final['owner_stop_confirmed']and supervision and supervision['final_total_job'].get('job_active_processes')==0):
            reached=final['final_record'];name=life+'_T'+str(reached['physical']['tick'])+'_POST6_VISTA_R02'
            scmd=[sys.executable,'-I','-B','-X','utf8',str(SEALER),'--root',str(ROOT),'--life',life,
                '--tick',str(reached['physical']['tick']),'--snapshot-sha256',reached['snapshot_sha256'],
                '--target-name',name,'--out',str(out/'SELLO_POST6_N0'),'--scope','Actual six-op view future, including failures; no material old22 panel. Not a promotion certificate.',
                '--root-go','APD04_EXACT_CURRENT_POSTSTOP_PAIR_N0']
            try:
                subprocess.run(scmd,cwd=Path(sys.executable).parent,check=True)
                seal=read(out/'SELLO_POST6_N0/CORTE_COMPLETO_POSTSTOP.json')
            except Exception as exc:seal_error={'type':type(exc).__name__,'message':str(exc),'actual_partial_future_preserved':True}
        else:seal_error={'scope':'No confirmed complete STOP/job closure. Preserve uncertainty and current full files; no favorable substitute or automatic retry.'}
        emit(out/'CIERRE_BRAZO_Y_RESUMEN_N0.json',{'arm':arm,'wrapper_returncode':code,'supervision':supervision,'actual_final':final,
            'summary_N0':summary,'postSTOP_seal':seal,'seal_error':seal_error,'no_extra_queries_or_replay':True,
            'same_REAL_parent_snapshot_SHA':p['required_actual_parent']['snapshot_sha256'],
            'source_hashes_unchanged':all(sha(path)==h for path,h in frozen.items())})
        print(json.dumps({'arm':arm,'wrapper_exit':code,'completed':summary['opportunities_completed'],'actions':summary.get('actions'),
            'old_gain_reported':summary.get('old_gain_reported'),'new_quality_reported':summary.get('new_WAITquality_reported'),
            'seal_complete':seal is not None,'extra_Native_queries':0},ensure_ascii=False))
        return code


def main():
    a=argparse.ArgumentParser(description=__doc__);g=a.add_mutually_exclusive_group(required=True)
    g.add_argument('--assemble-n0',action='store_true');g.add_argument('--validate-n0',action='store_true')
    g.add_argument('--prepare-after-go',choices=('ROOT_GO_VIEW_POST10_REAL_FULL_N0',))
    g.add_argument('--execute-after-go',choices=('ROOT_GO_VIEW_POST10_SIX_NATIVE_R02',))
    a.add_argument('--arm',choices=ARMS);a=a.parse_args()
    if a.assemble_n0:assemble_n0()
    elif a.validate_n0:
        ast.parse(Path(__file__).read_text(encoding='utf8'));verify_inputs();bundle_verified()
        print(json.dumps({'AST_valid':True,'actual_parent_not_accessed':True,'Native_ticks':0,'owners_started':0,'sourceSHA':sha(__file__)}))
    elif a.prepare_after_go:prepare_after_go()
    else:
        if a.arm is None:raise ValueError('Select one explicit arm; never choose by score')
        raise SystemExit(execute_one_after_go(a.arm))


if __name__=='__main__':main()
