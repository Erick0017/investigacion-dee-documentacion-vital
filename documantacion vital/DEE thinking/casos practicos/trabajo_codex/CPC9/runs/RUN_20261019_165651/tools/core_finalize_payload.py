"""Final Core payload assembly from completed proofs; no native transitions."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE'
p=argparse.ArgumentParser();p.add_argument('--core06',type=Path,required=True);p.add_argument('--core07',type=Path,required=True);p.add_argument('--initial',type=Path,required=True);p.add_argument('--clean03',type=Path,required=True);a=p.parse_args()
legacy=RUN/'front_semantics/core06_07'
def sha(f):
 with Path(f).open('rb')as s:return hashlib.file_digest(s,'sha256').hexdigest()
def put(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for label,folder in(('CORE06',a.core06),('CORE07',a.core07),('INITIAL_CPC8',a.initial)):
 report=json.loads((folder/'RECOVERY.json').read_text(encoding='utf8'));assert report['status']=='PASS',(label,report['status']);shutil.copyfile(folder/'RECOVERY.json',CORE/'verificaciones'/(label+'_RECOVERY.json'))
 if label.startswith('CORE0'):
  assert report['family']==label.lower();assert not report.get('historical_reads_denied',[]);assert report['cases']==(134 if label=='CORE06'else 144)
  for name in('PRIMARY_TRANSITIONS.json','OBSERVED.json','IDENTITY.json'):shutil.copyfile(folder/name,CORE/'verificaciones'/(label+'_'+name))
assert sha(legacy/'worker_recover.py')=='7d1ea228fff920c61de1e1e1dd164ef152eb285e95d558134622f8201185086b'
shutil.copyfile(legacy/'worker_recover.py',CORE/'reproduccion/worker_legacy_core.py')
for original,name in(('NUMPY_DEPENDENCIA.json','NUMPY_DEPENDENCIA.json'),('REGISTRO_CORRECCIONES.json','CORE06_07_CORRECCIONES.json'),('LEEME.md','CORE06_07_NOTAS_CONSTRUCCION.md')):shutil.copyfile(legacy/original,CORE/'documentacion'/name)
failed=legacy/'worker_recover_v1_failed_export.py'
if failed.exists():shutil.copyfile(failed,CORE/'documentacion/CORE06_07_EXPORTACION_V1_INERTE.py.txt')
clean=json.loads((a.clean03/'PRUEBA_RECUPERACION_DESDE_CERO.json').read_text(encoding='utf8'));assert clean['status']=='PASS'and len(clean['family_results'])==31;assert clean['artifact_sha256']=='3e2b8a69f4265363f36465bd00444de1682828d184a309a254c47a19041a9a68'
shutil.copyfile(a.clean03/'PRUEBA_RECUPERACION_DESDE_CERO.json',CORE/'verificaciones/CANDIDATO_03_PRUEBA_PREVIA.json')
index=json.loads((CORE/'documentacion/INDICE_MIEMBROS.json').read_text(encoding='utf8'))
put(CORE/'PROVENANCE.json',{'schema':'DEE_CORE.provenance.final.v1','assembled_utc':datetime.now(timezone.utc).isoformat(),'purpose':'Recovery of bounded scientific contracts, not new cognitive claims','official_wheel_sha256':'09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c','official_pyd_sha256':'17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d','kernel_source_sha256':'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31','source_identity_index':'documentacion/INDICE_MIEMBROS.json','source_identity_index_sha256':sha(CORE/'documentacion/INDICE_MIEMBROS.json'),'content_store_sha256':index['content_store_sha256'],'logical_members':len(index['paths']),'native_transition_adapter_sha256':sha(CORE/'reproduccion/worker_legacy_core.py'),'prior_31_family_exact_ZIP_sha256':clean['artifact_sha256'],'final_verification':'Outside this ZIP; no current ZIP self-hash inside','historical_archives_required_at_recovery':False,'external_dependencies':'DEPENDENCIAS.json; optional NumPy2.2.6 for CORE06/07 only','originals_modified':False,'core_functions_automatically_attributed_to_CPC9_E1':False})
put(CORE/'REANUDACION.json',{'schema':'DEE_CORE.manual_recovery.v1','status':'SEALED_RECOVERY_PROTOCOL_FINAL_VERIFICATION_EXTERNAL','no_background_execution':True,'resume_requires_explicit_human_invocation':True,'fresh_monotonic_budget_per_invocation_seconds':3600,'full_optional_panel_recommended_seconds':5400,'campaign_original_deadline_is_not_a_future_runtime_dependency':True,'next_authorized_action':'Read README, extract to a new location, invoke reproduccion/desde_cero.py with a new output directory and optional explicit NumPy dependency','historical_snapshots':'Essential declared original parents only; no living CPC9 E1 is stored in this package','CPC9_experimental_continuity':'Separate CPC9 results package; not silently merged with historical worlds'})
provenance=CORE/'PROVENANCE.json';record=json.loads(provenance.read_text(encoding='utf8'));record.update(project='DEE Universe / INVESTIGACION DEE',project_author='Ivan Erick Tlaltecatl Morales',recovery_campaign='CPC9',distribution='Private reconstructive artifact; no external publication');put(provenance,record)
print(json.dumps({'final_payload_assembled':True,'logical_members':len(index['paths']),'legacy_worker_sha256':sha(CORE/'reproduccion/worker_legacy_core.py')}))
