"""Read-only post-STOP cut, no Runtime, worker or new physical request.

Creates the logical paired manifest from current durable files, not an earlier
pre-STOP export. The full collaboration archive materializes those exact bytes.
"""
import argparse, hashlib, importlib.util, json, shutil, sqlite3
from pathlib import Path


def load(p): return json.loads(p.read_bytes())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, x): p.write_text(json.dumps(x, sort_keys=True, ensure_ascii=False, indent=2)+'\n', encoding='utf8')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sistema',type=Path,required=True);p.add_argument('--ensayo',type=Path,required=True)
    p.add_argument('--presupuesto',type=Path,required=True);p.add_argument('--reutilizar-par-verificado',action='store_true',help='Reuse the same exact post-STOP bytes only after checksum equality; never recopy/replace a different future.');a=p.parse_args()
    system=a.sistema.resolve();trial=a.ensayo.resolve();result=load(trial/'RESULTADO.json')
    calc=load(trial/'RECALCULO_FASE_R3.json');functions=load(trial/'PANELES_Y_FUNCIONES.json');times=load(trial/'RECALCULO_TIEMPO_FASE_R3.json')
    if result.get('error'): raise ValueError('Trial has an error; preserve it and inspect rather than label a complete release')
    life=result['final']['life_id'];state=system/'estado';card=state/'vidas'/life/'VIDA.json';record=load(card);card_initial_sha=sha(card)
    if any(record[k]!=result['final'][k] for k in('life_id','world_id','parent','snapshot','snapshot_sha256','physical')):raise ValueError('Current life moved after the recorded final cut')
    if(state/'locks'/(record['world_id']+'.lock')).exists():raise ValueError('Owner still holds the world; never hash a moving cut')
    snap=system/record['snapshot'];side=state/'servicios_persistentes'/life;db=side/'cola.sqlite3'
    wal=side/'cola.sqlite3-wal'
    if wal.exists()and wal.stat().st_size:raise ValueError('Uncheckpointed WAL is operational data; do not omit or delete it')
    with sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)as con:
        integrity=con.execute('PRAGMA integrity_check').fetchone()[0]
        owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
        outstanding=[dict(zip(('id','status'),r))for r in con.execute("SELECT id,status FROM requests WHERE status IN('queued','processing','uncertain')")]
    if integrity!='ok'or owner.get('running')is not False:raise ValueError('Stopped durable journal required')
    spec=importlib.util.spec_from_file_location('pure_snapshot_cut',system/'capacidades/observador_causal_retrospectivo_01.py');obs=importlib.util.module_from_spec(spec);spec.loader.exec_module(obs)
    snapshot=obs.Snapshot(snap)
    if snapshot.encoded_sha256!=record['snapshot_sha256']or not snapshot.checksum_valid:raise ValueError('Current complete snapshot checksum does not match its life')
    native_physical={'N':snapshot.N,'tick':snapshot.tick,'RAW_sha256':obs.sha(obs.pbytes(snapshot.raw)),'clocks_sha256':obs.sha(obs.pbytes(snapshot.clocks))}
    if any(record['physical'][k]!=v for k,v in native_physical.items()):raise ValueError('Current record does not describe the actual complete RAW/clocks')
    protocol=json.loads(snapshot.metadata['DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'])
    unified=json.loads(snapshot.metadata['DEE.Cognitive.System.1.1.MENTE_UNIFICADA_01.v1'])
    memory=json.loads(snapshot.metadata['DEE.Cognitive.System.1.1.MENTE_ACUMULATIVA_R02.v1'])
    pending={k:unified.get(k)for k in('external_pending','cascade_pending','external_uncertain')}
    pending['memory_external_pending']=memory.get('external_pending')
    pending_or_uncertain=bool(outstanding or any(pending.values())or owner.get('uncertain_external_result'))
    if pending_or_uncertain:raise ValueError('Unresolved state remains; retain and report it rather than emit a clean continuation')
    sources=[(snap,'VIDA.deetsnap.gz'),(db,'cola.sqlite3')]
    for source,prefix in((side/'resultados','resultados'),(state/'servicios_locales'/life,'artefactos_trabajador')):
        for f in sorted(source.rglob('*')):
            if f.is_file():
                if f.is_symlink()or not f.resolve().is_relative_to(source.resolve()):raise ValueError('Unexpected external operational dependency')
                sources.append((f,prefix+'/'+f.relative_to(source).as_posix()))
    package=trial/'PAQUETE_FINAL_POSTSTOP';already=package.exists()
    if already and not a.reutilizar_par_verificado:raise FileExistsError('Existing pair preserved; explicit checksum-verified reuse is required')
    if not already:package.mkdir()
    members=[]
    for f,name in sources:
        dest=package/name
        if not already:
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dest)
        digest=sha(f)
        if sha(dest)!=digest:raise ValueError('Moving source or copied operational member differs')
        members.append({'file':name,'source_system_relative':f.relative_to(system).as_posix(),'bytes':f.stat().st_size,'sha256':digest})
    manifest={'schema':'DEE.persistent_service.paired_export.v1','life_id':life,'world_id':record['world_id'],'profile':record['profile'],'backend':'mente_unificada','native_snapshot':'VIDA.deetsnap.gz','snapshot_sha256':record['snapshot_sha256'],'physical':record['physical'],'members':members,'queue_journal_required':True,'source_record':{'life_id':life,'world_id':record['world_id'],'parent':record.get('parent')},'no_engine_or_WHL':True,'not_a_new_cognitive_acquisition':True,'scope':'Exact current post-STOP native checkpoint plus durable journal, outbox and actual worker files. No files regenerated; copied read-only from the final stopped state. Complete files remain local, while reduced scientific analysis retains this manifest only. The collaboration updater stores a canonical native checkpoint once.'}
    manifest_path=package/'EXPORTACION_SERVICIO.json'
    if already:
        old_manifest=load(manifest_path)
        if old_manifest['members']!=members or old_manifest['snapshot_sha256']!=record['snapshot_sha256']:raise ValueError('Existing pair is not this exact current source cut; do not replace it')
        manifest=old_manifest
    else:write(manifest_path,manifest)
    spec=importlib.util.spec_from_file_location('pure_pair_validator',system/'app/importacion_emparejada.py');validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
    _,_,verification=validator.verify_export(package)
    if sha(card)!=card_initial_sha or sha(db)!=next(r['sha256']for r in members if r['file']=='cola.sqlite3'):raise ValueError('Operational current cut changed during read-only copying')
    old_export=result['final_paired_export']['paired_export'];export_manifest=Path(old_export['directory'])/'EXPORTACION_SERVICIO.json';old=load(export_manifest)
    budget=load(a.presupuesto);protected=[]
    for name,row in budget['protected'].items():
        for kind,expected in(('record',row['record_sha256']),('snapshot',row['snapshot_sha256'])):
            f=Path(row[kind]);actual=sha(f);protected.append({'life':name,'kind':kind,'file':str(f),'expected_sha256':expected,'actual_sha256':actual,'unchanged':actual==expected})
    active=state/'ACTIVO.json';protected.append({'kind':'active','file':str(active),'expected_sha256':budget['active_record_sha256'],'actual_sha256':sha(active),'unchanged':sha(active)==budget['active_record_sha256']})
    # The earlier R11 trajectory is separately protected, not one of the new R3 inputs.
    for f,expected in((state/'vidas/MU_MAIN/VIDA.json','822ebb37615f7f38b73dce531861696ddd6c02a36e0f2df2807ff1f6c6e67351'),(state/'servicios_persistentes/MU_MAIN/cola.sqlite3','700a1f997b32e66d3462e036d44503241b08c0a1797781cc812ed587126b046c')):
        actual=sha(f);protected.append({'life':'MU_MAIN_R11','file':str(f),'expected_sha256':expected,'actual_sha256':actual,'unchanged':actual==expected})
    if not all(r['unchanged']for r in protected):raise ValueError('Protected source changed; no silent acceptance')
    transport=calc['material_request_outcomes'];native=calc['native_receipts'];work=functions['individual_work'];chains=functions['chains'];raw=functions['raw128'];memory_rows=functions['memory_uses'];teaching=functions['explicit_teaching']
    raw_good=sum(x['matches_expected']for x in raw);memory_good=sum(x['matches_expected']for x in memory_rows)
    text=(f"R17/R04: {times['unpaused_operational_seconds_lower_estimate']:.6f} s reales en modo de evolución, descontando pausas y recarga; "
      f"{transport.get('completed',0)} peticiones materiales completadas; {native.get('requested',0)} entradas nativas solicitadas, {native.get('applied',0)} aplicadas. "
      f"Memoria: {memory_good}/{len(memory_rows)} lecturas coinciden con la historia explícita; beta se revisó de + a − mediante enseñanza del operador ({len(teaching)} evento), no regulación autónoma. "
      f"Sensor crudo128: {raw_good}/{len(raw)} coincide con criterio reservado; conservar todas las salidas ausentes o erróneas. "
      f"Cadenas: {chains['transaction_commits']}/{chains['nominal_finish']} oportunidades nominales terminaron commit real, {chains['actual_preparations']} preparaciones/{chains['actual_verifications']} verificaciones ejecutadas. "
      f"Trabajo individual: {work['useful_under_declared_environmental_law']}/{work['actual_executions']} ejecuciones útiles, {work['not_useful_under_declared_environmental_law']} no útiles. "
      "La temporización R3 es protección P0 preparada, no selección aprendida. El panel observado final precede al tramo ocioso final y no certifica acceso ilimitado después de éste.")
    out={'schema':'DEE.unified.R17.manual_and_continuation_cut.v1','main':{'life_id':life,'world_id':record['world_id'],'parent':record.get('parent'),'tick':record['physical']['tick'],'N':record['physical']['N'],'snapshot':record['snapshot'],'snapshot_sha256':record['snapshot_sha256'],'physical':record['physical'],'record':card.relative_to(system).as_posix(),'record_sha256':sha(card)},
      'persistent_service':{'world_evolving_wall_seconds':times['unpaused_operational_seconds_lower_estimate'],'completed_operations':transport.get('completed',0),'idle_ticks':owner['idle_ticks']-result['initial_owner']['idle_ticks'],'idle_ticks_cumulative':owner['idle_ticks'],'owner_stopped':True,'pending_or_uncertain':False,'queue':outstanding,'pending':pending,'epoch_closed':bool(protocol.get('closed_epoch')),'epoch':protocol['epoch'],'owner':owner,'protocol':protocol,'manual_results_text':text,'paired_manifest':str(manifest_path),'paired_manifest_sha256':sha(manifest_path),'journal':str(db),'journal_sha256':sha(db),'continuation_requires_complete_paired_state':True},
      'paired_export':{'manifest':str(manifest_path),'manifest_sha256':sha(manifest_path),'verification':verification,'same_cut_after_STOP':True},
      'preSTOP_explicit_export':{'manifest':str(export_manifest),'manifest_sha256':sha(export_manifest),'snapshot_sha256':old['snapshot_sha256'],'physical':old['physical'],'same_RAW_clocks_as_current':all(old['physical'][k]==record['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')),'full_snapshot_byte_identity_claimed':False},
      'functional_results':{'last_observed_memory_panel':calc['last_memory_uses'],'regimes':functions['regimes'],'explicit_teaching':teaching,'raw128':raw,'chains':chains,'individual_work':work,'native_receipts':native,'transport_denominators':calc['transport_admission_denominators']},
      'protected_sources':protected,'issues':calc['issues']+times['issues'],'new_ticks_for_this_extraction':0,'no_Runtime_restored':True,'scope':'Read-only final cut inspection; complete operational members are hashed, not copied into this small analysis. Protocol journal is infrastructure and is not a cognitive answer store. No promotion or release decision is implied.'}
    out['persistent_service']['native_pending']=snapshot.pending
    out['persistent_service']['native_pending_count']=len(snapshot.pending)
    out['persistent_service']['transport_pending_definition']='pending_or_uncertain refers to literal transport and external/cascade action state; native future entries, if any, are listed separately and remain in the complete snapshot.'
    write(trial/'CORTE_PARA_MANUAL.json',out)
    print(json.dumps({'cut':str(trial/'CORTE_PARA_MANUAL.json'),'life_id':life,'tick':record['physical']['tick'],'snapshot_sha256':record['snapshot_sha256'],'members':len(members),'protected_unchanged':len(protected),'manual_results_text':text}))


if __name__=='__main__':main()
