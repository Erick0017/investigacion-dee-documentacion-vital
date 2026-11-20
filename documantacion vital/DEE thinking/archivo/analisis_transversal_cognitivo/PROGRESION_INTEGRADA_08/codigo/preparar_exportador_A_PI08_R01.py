"""Version the reviewed closed paired exporter for actual committed A.
Only the pinned, coherently preserved PI08 precommit control failure is allowed.
No Native execution, product/state modification or export is performed here.
"""
from pathlib import Path
import ast,hashlib
H=Path(__file__).resolve().parent;P=H.parent;source=P.parent/'PROGRESION_INTEGRADA_07/codigo/exportar_corte_aislado_PI07_R01.py';target=H/'exportar_A_consolidada_PI08_R01.py'
if target.exists():raise FileExistsError('Prepared exporter revision preserved')
s=source.read_text('utf8')
s=s.replace("SOURCE_LIFE='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'","SOURCE_LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'")
s=s.replace("r'PI07_[A-Za-z0-9_]{1,43}_T'","r'PI08_A_[A-Za-z0-9_]{1,35}_T'")
s=s.replace("s5=(CAMPAIGN/'estados/candidato/sistema').resolve(strict=True)\n    if s!=s5 or not re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI07_[A-Za-z0-9_]{1,24}',ar.vida):raise ValueError('Only exact isolated S7 PI07 diagnostic source; never current product Main')", "s5=(PRODUCT/'sistema').resolve(strict=True)\n    if s!=s5 or ar.vida!=SOURCE_LIFE or json.loads((s/'estado/ACTIVO.json').read_text('utf-8-sig')).get('life_id')!=SOURCE_LIFE:raise ValueError('Only actual selected complete PI08 A product source')\n    profile=json.loads((s/'contratos/PI08_USO_OPERATIVO_R01.json').read_text('utf-8-sig'))\n    if profile.get('status')!='COMMITTED'or profile.get('life_id')!=SOURCE_LIFE:raise ValueError('Actual committed A profile required before preserving B source')")
s=s.replace("if any(Path(str(db)+x).exists()for x in('-wal','-shm','-journal')):raise ValueError('Source SQLite auxiliaries exist; no incoherent copy')", "if any(Path(str(db)+x).exists()and Path(str(db)+x).stat().st_size for x in('-wal','-journal')):raise ValueError('Nonempty SQLite WAL/journal; no incoherent copy')\n    sqlite_auxiliaries={x:Path(str(db)+x).stat().st_size if Path(str(db)+x).exists()else 0 for x in('-wal','-shm','-journal')}")
s=s.replace("or view['physical']['tick']!=ar.tick or view['pending_native']:","or view['physical']['tick']!=ar.tick:")
old="        if owner['running']or owner['tick']!=ar.tick or owner.get('uncertain_external_result')or any(counts.get(x,0)for x in('queued','processing','uncertain','failed_preserved')):\n            raise ValueError('No live/ambiguous/unfinished source transport')"
new="""        if owner['running']or owner['tick']!=ar.tick or owner.get('uncertain_external_result')or any(counts.get(x,0)for x in('queued','processing','uncertain')):
            raise ValueError('No live/ambiguous/unfinished source transport')
        expected_failures=verify_declared_precommit_failure(con,service)"""
if old not in s:raise ValueError('Exact historical export queue policy required')
s=s.replace(old,new)
s=s.replace("'empty_directories_preserved':sorted(directories),", "'empty_directories_preserved':sorted(directories),'expected_preserved_terminal_failure':expected_failures,'pending_Native_agenda_preserved':view['pending_native'],")
s=s.replace("'queue_status_counts':counts,'source_files_all_unchanged':before==after,", "'queue_status_counts':counts,'expected_preserved_terminal_failure':expected_failures,'SQLite_auxiliary_bytes_before_closed_copy':sqlite_auxiliaries,'source_files_all_unchanged':before==after,")
s=s.replace("'DEE.PI07.isolated_closed_paired_preservation.R02'","'DEE.PI08.committed_A_closed_paired_preservation.R01'").replace("'PI07_R02_exact_S7_diagnostic_only'","'PI08_R01_exact_committed_product_A_expected_failure_preserved'")
anchor='def main():'
function='''def verify_declared_precommit_failure(con,service):
    proof_file=CAMPAIGN/'control/PI08_A1_PRECONTROL_REAL_R01.json'
    if sha(proof_file)!='53889171a1835a1523d3e8da51481b269f7f417a0c8a36f352784a96b8d9214d':raise ValueError('Pinned actual PREcontrol proof differs')
    proof=json.loads(proof_file.read_text('utf-8-sig'))
    if proof.get('closed')is not True or proof.get('criteria_met')is not True or proof.get('new_Native_ticks')!=0 or not all(proof['full_Native_field_equalities'].values())or not all(proof['invariants'].values()):raise ValueError('Actual coherent0Native precommit control required')
    rows=con.execute("SELECT * FROM requests WHERE status='failed_preserved' ORDER BY seq").fetchall()
    if len(rows)!=1:raise ValueError('Exactly the one known precommit control failure must remain; no other failure is whitelisted')
    row=dict(rows[0]);payload=json.loads(row['payload']);error=json.loads(row['error'])
    literal={'modo':'eci01-pi08-c2c-prueba-precommit','token':proof['token']}
    if row['id']!='PI08_A1_PRE_INTERRUPT_R01'or payload!={'operacion':'sesion','situaciones':[literal],'actuador':'closed','retorno':'omit'}or row['is_control']!=0 or row['result']is not None:raise ValueError('Only the exact preserved interruption request is allowed')
    expected_prefix='PI08_DECLARED_PRECOMMIT_INTERRUPTION: preparation preserved; no life/device/Native write occurred'
    if error.get('type')!='RuntimeError'or error.get('detail')!=expected_prefix or error.get('external_execution_may_be_uncertain')is not False or error.get('native_tick_after_attempt')!=proof['initial_tick']or error.get('checkpoint_error')or error.get('no_retry_or_rollback')is not True:raise ValueError('Another/uncertain failure cannot inherit this exception')
    if hashlib.sha256(canon(payload).encode()).hexdigest()!=row['payload_sha']:raise ValueError('Expected failed payload checksum differs')
    primary=CAMPAIGN/'ensayos/PI08_A1_PRE_INTERRUPT_R01.json';recorded=json.loads(primary.read_text('utf-8-sig'))
    if any(recorded[k]!=row[k]for k in('id','payload','payload_sha','status','error','result','started_utc','finished_utc')):raise ValueError('Expected failed transport row differs from its original complete primary')
    outbox=service/'resultados'/(row['id']+'.json')
    return {'id':row['id'],'status':'failed_preserved','payload_sha256':row['payload_sha'],'error_sha256':hashlib.sha256(row['error'].encode()).hexdigest(),'original_primary':{'path':str(primary),'sha256':sha(primary)},'proof':{'path':str(proof_file),'sha256':sha(proof_file)},'outbox_present':outbox.is_file(),'outbox_sha256':sha(outbox)if outbox.is_file()else None,'exception_scope':'Known declared0Native precommit interruption, coherent checkpoint and unchanged scientific fields; preserve the row/error/outbox exactly. No purge or replay. Other failures remain blocked.'}

'''
if s.count(anchor)!=1:raise ValueError('Exact exporter function anchor required')
s=s.replace(anchor,function+anchor);ast.parse(s);target.write_text(s,encoding='utf8');print(str(target));print(hashlib.sha256(target.read_bytes()).hexdigest())
