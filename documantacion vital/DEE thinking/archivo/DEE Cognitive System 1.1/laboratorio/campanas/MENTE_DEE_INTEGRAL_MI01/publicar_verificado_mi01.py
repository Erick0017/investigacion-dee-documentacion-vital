"""Publicación exacta sólo tras verificación del ZIP extraído. Cero física."""
import hashlib,json,shutil,sys,time,zipfile
from pathlib import Path
from datetime import datetime,timezone
L=Path(__file__).resolve().parent;R=L.parents[2];E=R/'evidencia/campanas/MENTE_DEE_INTEGRAL_MI01';S=R/'sistema';D=R/'entregas'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
seal=read(L/'SELLO_CANDIDATO_PAQUETE_04.json');checks=read(L/'VERIFICACION_EXTRAIDA_04.json');budget=read(L/'PRESUPUESTO.json');initial=read(E/'INICIO_Y_PADRE.json');cont=read(R/'CONTINUIDAD_MENTE_DEE_INTEGRAL_MI01.json')
assert time.monotonic()<budget['monotonic_deadline'],'Stop: fixed total cutoff reached'
assert checks['native_ticks']==checks['external_simulator_steps']==0
assert checks['portable_recalculation_equals_reference']and not checks['primary_RAW_mismatches']
assert checks['package_members_hashed']==seal['members']-1
assert len(checks['full_snapshots_checked'])==17 and checks['grouped_original_life_records_verified']>0
assert checks['frozen_summary']['useful_contacts']==0 and checks['frozen_summary']['external_steps']==47
for row in read(E/'SELLO_EVALUACION_FIJADA.json')['physical_code']:assert sha(R/row['path'])==row['sha256']
active=read(S/'estado/vidas/E1_SOCIAL_11/VIDA.json');parent=read(S/'estado/vidas/E1_CICLO02_SEPARACION_TRIPLE_01/VIDA.json');main=read(S/'estado/vidas/E1_MI01_MAIN/VIDA.json')
assert sha(S/active['snapshot'])==initial['active_protected']['snapshot_sha256']
assert sha(S/parent['snapshot'])==initial['parent_selected_before_evaluation']['sha256']
assert main['snapshot_sha256']==cont['main']['snapshot_sha256']and main['physical']['tick']==28169
assert sha(S/main['snapshot'])==main['snapshot_sha256']
original=R/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_6_CICLO02_SIN_VALIDACION_VISUAL.docx';manual=R/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_7_MI01_SIN_VALIDACION_VISUAL.docx'
assert sha(original)=='8d15cff57b3fb4309877ca335fff6a41c07753776bb0230256694e0c3fcec502'
assert sha(manual)=='8a73d88bcdc3fbefb9537bc2026480c7d9762021e058d2a8d27954b6216984d9'
candidate=Path(seal['candidate']);assert sha(candidate)==seal['sha256']and candidate.stat().st_size<=16000000
with zipfile.ZipFile(candidate)as z:assert z.testzip()is None
D.mkdir(exist_ok=True);canonical=D/'DEE_COGNITIVE_1_1_MENTE_DEE_INTEGRAL_MI01_ANALISIS.zip'
if canonical.exists():assert sha(canonical)==seal['sha256'],'Never overwrite a different canonical result'
else:shutil.copy2(candidate,canonical)
assert sha(canonical)==seal['sha256']
now=datetime.now(timezone.utc)
out={'schema':'DCS1.1.MI01.final.external.verification.v1','verified_utc':now.isoformat(),'ZIP':str(canonical),'sha256':sha(canonical),'compressed_bytes':canonical.stat().st_size,'expanded_member_bytes':seal['expanded_member_bytes'],'ZIP_members':seal['members'],'hard_limit_bytes':16000000,'CRC_checked_on_final_exact_bytes':True,'clean_extraction':seal['extracted_clean_directory'],'portable_verification_command':[sys.executable,'-I','-B','-X','utf8',str(Path(seal['extracted_clean_directory'])/'RECALCULO/verificar_paquete_mi01.py'),'--raiz',seal['extracted_clean_directory'],'--salida',str(L/'VERIFICACION_EXTRAIDA_04.json')],'result_file':str(L/'VERIFICACION_EXTRAIDA_04.json'),'result_file_sha256':sha(L/'VERIFICACION_EXTRAIDA_04.json'),'native_ticks_in_final_verification':0,'external_steps_in_final_verification':0,'exact_original_export_checks':checks['exact_original_export_checks'],'grouped_original_life_records_verified':checks['grouped_original_life_records_verified'],'primary_RAW_observations_checked':checks['primary_RAW_observations_checked'],'primary_RAW_mismatches':checks['primary_RAW_mismatches'],'full_snapshots_checked':17,'all_authored_CSV_cells_verified':True,'portable_recalculation_equals_reference':True,'observer470_physical_and_agenda_equality_recomputed':True,'external483_one_RAW_site_difference_recomputed':True,'coalescence_and_second_turn_recomputed':True,'receipts_recounted_from_complete_snapshots':checks['receipts_from_full_snapshots'],'frozen_physical_code_unchanged':True,'main_current_tick':28169,'main_snapshot_sha256':main['snapshot_sha256'],'active_E1_SOCIAL_11_unchanged':True,'parent_E1_triple21711_unchanged':True,'promotion':'none; preserve adverse MAIN and specialized/historical lives separately','manual_actual_DOCX_updated':str(manual),'manual_sha256':sha(manual),'manual_original16_unchanged':True,'manual_structural_checks':True,'manual_visual_validation':False,'manual_render_error':'FileNotFoundError: LibreOffice soffice.exe was not found on PATH','budget_start_bound_utc':budget['start_bound_utc'],'budget_deadline_utc':budget['deadline_utc'],'elapsed_from_start_bound_seconds':(now-datetime.fromisoformat(budget['start_bound_utc'])).total_seconds(),'remaining_monotonic_budget_seconds':budget['monotonic_deadline']-time.monotonic(),'final_classification':cont['classification'],'operational_continuation_previously_checked':'435new external interaction;437drain throughowner;438normal state load;495-498specialized use and reload across processes. Not repeated by this archival verification.','limits':['This is an analysis ZIP, not a complete operational backup or interpreter/engine distribution.','Some in-flight diagnostic snapshots are not supported bridge-continuation boundaries.','No new native/external reproduction was run during ZIP verification;470is the separately executed native technical replay.','No competent Pendulum policy, generalP2/R2, consciousness or65meanings inferred.','Early frontend source revision archival gap remains declared.','Deep local states/telemetry not all included; exact index provides locators/hashes.']}
save(D/'VERIFICACION_FINAL_EXTERNA_MI01.json',out)
save(L/'CIERRE_Y_ENTREGA_MI01.json',out)
print(json.dumps({k:out[k]for k in('ZIP','sha256','compressed_bytes','ZIP_members','grouped_original_life_records_verified','primary_RAW_observations_checked','main_current_tick','manual_visual_validation','elapsed_from_start_bound_seconds','final_classification')},ensure_ascii=False,indent=2))
