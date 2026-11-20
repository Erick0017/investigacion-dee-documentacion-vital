"""Read-only APD post-STOP continuity cut and exact paired package.

No Runtime is restored and no queued/native request is submitted. A pre-STOP
export is not relabeled as the current exact journal/snapshot pair.
"""
import argparse,ctypes,hashlib,importlib.util,json,shutil,sqlite3
from pathlib import Path

def load(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,value):
    with p.open('x',encoding='utf8')as f:json.dump(value,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--ensayo',type=Path,required=True);p.add_argument('--presupuesto',type=Path,required=True);p.add_argument('--reutilizar-par-verificado',action='store_true');a=p.parse_args()
    system=a.sistema.resolve();trial=a.ensayo.resolve();result=load(trial/'RESULTADO.json');calc=load(trial/'RECALCULO_SERVICIO_APD.json');functions=load(trial/'PANELES_Y_FUNCIONES.json');times=load(trial/'RECALCULO_TIEMPO_APD.json')
    if not result.get('final'):raise ValueError('No durable final pointer: preserve interrupted trial; never substitute another future')
    life=result['final']['life_id'];state=system/'estado';card=state/'vidas'/life/'VIDA.json';record=load(card);card_sha=sha(card)
    if any(record[k]!=result['final'][k]for k in('life_id','world_id','parent','snapshot','snapshot_sha256','physical')):raise ValueError('Life moved after the recorded trial cut')
    if(state/'locks'/(record['world_id']+'.lock')).exists():raise ValueError('A world writer remains; never certify a moving cut')
    side=state/'servicios_persistentes'/record['world_id'];db=side/'cola.sqlite3';wal=db.with_name(db.name+'-wal')
    if wal.exists()and wal.stat().st_size:raise ValueError('Unsettled WAL is operational data; do not omit/delete/checkpoint it secretly')
    with sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)as con:
        integrity=con.execute('PRAGMA integrity_check').fetchone()[0];owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0]);outstanding=[dict(zip(('id','status'),row))for row in con.execute("SELECT id,status FROM requests WHERE status IN('queued','processing','uncertain')")]
    if integrity!='ok'or owner.get('running')is not False:raise ValueError('A stopped, complete durable journal is required')
    events=[json.loads(line)for line in(trial/'ADMISIONES_Y_EVENTOS.jsonl').read_text(encoding='utf8').splitlines()if line];known_pids=set()
    for event in events:
        if event['kind']in('owner_process_ready','owner_ready'):
            if event.get('launcher_pid'):known_pids.add(event['launcher_pid'])
            if event.get('status',{}).get('pid'):known_pids.add(event['status']['pid'])
    kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong];kernel.OpenProcess.restype=ctypes.c_void_p;kernel.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_ulong)];kernel.CloseHandle.argtypes=[ctypes.c_void_p];pid_checks=[]
    for pid in sorted(known_pids):
        handle=kernel.OpenProcess(0x1000,False,pid)
        if not handle:
            error=ctypes.get_last_error();pid_checks.append({'pid':pid,'open_process_error':error,'not_present':error==87,'scope':'Only this recorded owner/launcher PID, never a system-wide search or process termination.'})
            if error!=87:raise ValueError('Own recorded PID absence cannot be established; preserve unknown status: '+str(pid))
        else:
            code=ctypes.c_ulong();queried=kernel.GetExitCodeProcess(handle,ctypes.byref(code));kernel.CloseHandle(handle);pid_checks.append({'pid':pid,'exit_code':code.value if queried else None,'not_present':bool(queried and code.value!=259),'possible_PID_reuse_not_terminated':True})
            if not queried or code.value==259:raise ValueError('A recorded PID is still present/unknown; never kill or substitute it: '+str(pid))
    obs=module('APD_poststop_snapshot_only',system/'capacidades/observador_causal_retrospectivo_01.py');snap=system/record['snapshot'];snapshot=obs.Snapshot(snap)
    physical={'N':snapshot.N,'tick':snapshot.tick,'RAW_sha256':obs.sha(obs.pbytes(snapshot.raw)),'clocks_sha256':obs.sha(obs.pbytes(snapshot.clocks))}
    if snapshot.encoded_sha256!=record['snapshot_sha256']or not snapshot.checksum_valid or any(record['physical'][k]!=v for k,v in physical.items()):raise ValueError('Complete physical checkpoint differs from current life')
    def meta(key):return json.loads(snapshot.metadata[key])if key in snapshot.metadata else{}
    protocol=meta('DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1');unified=meta('DEE.Cognitive.System.1.1.MENTE_UNIFICADA_01.v1');memory=meta('DEE.Cognitive.System.1.1.MENTE_ACUMULATIVA_R02.v1');assistant=meta('DEE.Cognitive.System.1.1.APD01.assistant.R01')
    pending={k:unified.get(k)for k in('external_pending','cascade_pending','external_uncertain')};pending['memory_external_pending']=memory.get('external_pending');pending['APD_external_uncertain']=assistant.get('external_uncertain')
    unresolved=bool(outstanding or any(pending.values())or owner.get('uncertain_external_result'))
    sources=[(snap,'VIDA.deetsnap.gz'),(db,'cola.sqlite3')]
    for source,prefix in((side/'resultados','resultados'),(state/'servicios_locales'/life,'artefactos_trabajador')):
        for f in sorted(source.rglob('*')):
            if f.is_file():
                if f.is_symlink()or not f.resolve().is_relative_to(source.resolve()):raise ValueError('Unexpected external operational dependency')
                sources.append((f,prefix+'/'+f.relative_to(source).as_posix()))
    package=trial/'PAQUETE_FINAL_POSTSTOP';already=package.exists()
    if already and not a.reutilizar_par_verificado:raise FileExistsError('Existing pair preserved; explicit exact-hash reuse required')
    if not already:package.mkdir()
    members=[]
    for f,name in sources:
        target=package/name
        if not already:target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,target)
        digest=sha(f)
        if sha(target)!=digest:raise ValueError('Moving or different paired member: '+name)
        members.append({'file':name,'source_system_relative':f.relative_to(system).as_posix(),'bytes':f.stat().st_size,'sha256':digest})
    manifest={'schema':'DEE.persistent_service.paired_export.v1','life_id':life,'world_id':record['world_id'],'profile':record['profile'],'backend':'mente_unificada','native_snapshot':'VIDA.deetsnap.gz','snapshot_sha256':record['snapshot_sha256'],'physical':record['physical'],'members':members,'queue_journal_required':True,'source_record':{'life_id':life,'world_id':record['world_id'],'parent':record.get('parent')},'no_engine_or_WHL':True,'not_a_new_cognitive_acquisition':True,'scope':'Exact read-only post-STOP checkpoint, SQLite, outbox and actual worker/APD files. The full collaboration package stores the native snapshot once. Analysis retains a manifest, not a replacement operational backup.'}
    manifest_path=package/'EXPORTACION_SERVICIO.json'
    if already:
        old=load(manifest_path)
        if old['members']!=members or old['snapshot_sha256']!=record['snapshot_sha256']:raise ValueError('Existing pair belongs to another cut; never replace it')
        manifest=old
    else:write(manifest_path,manifest)
    validator=module('APD_exact_standalone_pair_validator',system/'app/importacion_emparejada.py');_,_,verification=validator.verify_export(package)
    if sha(card)!=card_sha or sha(db)!=next(r['sha256']for r in members if r['file']=='cola.sqlite3'):raise ValueError('Current durable state changed while inspected')
    budget=load(a.presupuesto);protected=[]
    for label,row in budget['parent_and_protected'].items():
        if not isinstance(row,dict)or'path'not in row or'sha256'not in row:continue
        f=Path(row['path']);digest=sha(f);protected.append({'name':label,'file':str(f),'expected_sha256':row['sha256'],'actual_sha256':digest,'unchanged':digest==row['sha256']})
    if not all(r['unchanged']for r in protected):raise ValueError('A protected source changed; no silent acceptance')
    pre=result['final_paired_export']['paired_export'];pre_manifest=Path(pre['directory'])/'EXPORTACION_SERVICIO.json';prior=load(pre_manifest)
    material=calc['material_request_outcomes'];native=calc['native_receipts'];primitive=functions['APD_primitive_uses_including_composition_stages'];memory_rows=functions['memory_uses'];raw=functions['raw128'];lessons=functions['explicit_teaching']
    text=(f"APD01: {times.get('unpaused_operational_seconds')} s reales en modo de evolución, descontadas pausas y recarga; {material.get('completed',0)} peticiones materiales completadas. "
          f"Entradas nativas: {native.get('requested',0)} solicitadas, {native.get('applied',0)} aplicadas, {native.get('rejected',0)} rechazadas. "
          f"Memoria anterior: {sum(r['matches_expected']for r in memory_rows)}/{len(memory_rows)} lecturas coinciden con historia explícita. "
          f"Pasos APD: {sum(r['word_matches_history']for r in primitive)}/{len(primitive)} códigos léxicos coinciden con historia, {sum(r['correct_given_actual_operator']is True for r in primitive)}/{len(primitive)} resultados numéricos correctos dada la operación emitida, {sum(r['real_artifact_completed']for r in primitive)} artefactos reales. "
          f"COUNT: {functions['native_count']['numeric_correct_given_actual_operator']}/{functions['native_count']['scheduled']} oportunidades nominales; composiciones numéricas completas: {functions['composition']['numeric_correct_given_actual_operator']}/{functions['composition']['scheduled']}. "
          f"Crudos128: {sum(r['matches_expected']for r in raw)}/{len(raw)} conforme al criterio reservado. "
          f"Docencias explícitas archivadas en esta ventana: {len(lessons)}; su admisión y uso se describen por separado, sin suponer adquisición a partir del calendario. Retención, precio modelado, competencia numérica y decisión de ruta se mantienen separados. El último panel observado precede al ocio posterior.")
    cut={'schema':'DEE.APD01.actual_service_manual_cut.v1','main':{'life_id':life,'world_id':record['world_id'],'parent':record.get('parent'),'tick':record['physical']['tick'],'N':record['physical']['N'],'snapshot':record['snapshot'],'snapshot_sha256':record['snapshot_sha256'],'physical':record['physical'],'record':card.relative_to(system).as_posix(),'record_sha256':sha(card)},
         'persistent_service':{'world_evolving_wall_seconds':times.get('unpaused_operational_seconds'),'sixty_unpaused_minutes_reached':times['checks'].get('at_least_sixty_unpaused_operational_minutes',False),'completed_operations':material.get('completed',0),'idle_ticks':owner['idle_ticks']-result['initial_owner']['idle_ticks'],'idle_ticks_cumulative_inherited_not_new_trials':owner['idle_ticks'],'owner_stopped':True,'pending_or_uncertain':unresolved,'queue':outstanding,'pending':pending,'epoch_closed':bool(protocol.get('closed_epoch')),'epoch':protocol.get('epoch'),'owner':owner,'protocol':protocol,'APD_environment':assistant.get('environment'),'manual_results_text':text,'paired_manifest':str(manifest_path),'paired_manifest_sha256':sha(manifest_path),'journal':str(db),'journal_sha256':sha(db),'continuation_requires_complete_paired_state':True,'native_pending':snapshot.pending,'native_pending_count':len(snapshot.pending),'native_pending_separate_from_transport':True},
         'paired_export':{'manifest':str(manifest_path),'manifest_sha256':sha(manifest_path),'verification':verification,'same_cut_after_STOP':True},
         'preSTOP_export':{'manifest':str(pre_manifest),'manifest_sha256':sha(pre_manifest),'snapshot_sha256':prior['snapshot_sha256'],'physical':prior['physical'],'same_RAW_clocks_as_current':all(prior['physical'][k]==record['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')),'full_snapshot_or_journal_byte_identity_claimed':False},
         'functional_results':{'last_memory_observations':functions['last_memory_observations'],'regimes':functions['regimes'],'explicit_teaching':lessons,'APD_direct':functions['APD_direct'],'native_count':functions['native_count'],'composition':functions['composition'],'chains':functions['chains'],'individual_work':functions['individual_work'],'native_receipts':native,'transport_denominators':calc['transport_admission_denominators']},'protected_sources':protected,'issues':calc['issues']+times['issues'],'new_ticks_for_this_extraction':0,'no_Runtime_restored':True,'scope':'No promotion implied. Epoch remains honestly open unless explicitly closed by its existing protocol. Full journal is infrastructure, not an actor answer memory. Real-time success and functional success are distinct.'}
    cut['source_capture_scope']=calc.get('source_capture_scope');cut['operational_issues']=times.get('operational_issues',[]);cut['known_owner_PID_checks_after_STOP']=pid_checks;cut['persistent_service']['sixty_unpaused_minutes_reached']=times.get('operational_criteria',{}).get('sixty_minutes_one_native_owner_proved',cut['persistent_service']['sixty_unpaused_minutes_reached']);cut['persistent_service']['one_owner_proof']=times.get('operational_criteria');cut['persistent_service']['clean_closure']=times.get('clean_closure',not unresolved and not cut['issues']);cut['persistent_service']['last_panel_scope']='Actual last observations in this window, followed by the recorded remaining idle interval; no indefinite future access is inferred.'
    write(trial/'CORTE_PARA_MANUAL.json',cut);print(json.dumps({'cut':str(trial/'CORTE_PARA_MANUAL.json'),'tick':record['physical']['tick'],'snapshot_sha256':record['snapshot_sha256'],'members':len(members),'pending_or_uncertain':unresolved,'issues':cut['issues'],'manual_results_text':text}))
    return bool(unresolved or cut['issues'])
if __name__=='__main__':raise SystemExit(main())
