"""Finish only the exact known R03 partial registration; default read-only.

R03's accidental one-line for suite wrote the correct new recipe once, then
its second iteration rejected its own old-recipe CAS. No Native failure and
no external concurrency is inferred. R04 verifies the ENTIRE first-write
recipe and immutable run/evidence/backups, then only finishes README/proof.
Never re-runs Native or the existing registrar, and never changes variants.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,importlib.util,json,os,shutil,sys
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';RID='pi10_consulta12_familia_desde_P02_R02';OLD='163b0a9aac0aec4d980173b4c35c0bbbdc3755728861548100f85563b35d9ae5';TRANSACTION=P/'control/REGISTRO_REPLAY_NATIVE_ESTABLE_PI10_R02';EVIDENCE=RP/'evidencia/PI10_R02_REPLAY_VERIFICADO'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encoded(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def put(p,v):
 with p.open('xb')as f:f.write(encoded(v))
def expected_recipe(old,result,registry,criteria):
 new=copy.deepcopy(old)
 new['verification']={'state':'ACTUAL_NATIVE_ACQUISITION12_VERIFIED_BOUNDED','Native_replay_verified':True,'registered_run_product_relative':registry.relative_to(C).as_posix(),'registered_run_sha256':sha(registry),'evidence_product_relative':EVIDENCE.relative_to(C).as_posix(),'evidence_manifest_sha256':sha(EVIDENCE/'MANIFIESTO_SHA256.json'),'recipe_sha256_at_run':OLD,'recipe_at_run_preserved':str(TRANSACTION/'receta_AL_EJECUTAR.json'),'new_Native_ticks_in_run':18762,'new_current_call_inputs':2269,'physical_equal':True,**criteria,'scope':'One actual fresh diagnostic acquisition12 from the same complete neutral P02, all failures/initial NULL preserved. Shared past, not independent individuals or general reproducibility. Current main use/adoption is separate.'}
 new['modalities']['B']='Actual cold Native replay verified in one fresh diagnostic family; new IDs/destinations remain reusable'
 new['modalities']['C']='Actual acquisition12 from complete pre-learning P02 verified under frozen evaluation code,4+8'
 new['stable_registration']['Native_replay_verified']=True
 return new
def expected_readme(text,life):
 old='Esta incorporación conserva los medios, no acredita todavía el replay Native ni la adopción.'
 need(text.count(old)==1,'Exact original README statement required before writing')
 text=text.replace(old,'La reproducción Native acotada de adquisición12 quedó comprobada en un clon nuevo, con correspondencia física/Native y metadatos controlados. La adopción del principal se decide por separado.')
 text=text.replace('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RPF2_20261111A --destino D:', 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RPF2_NUEVO01 --destino D:')
 text+='\n\nVerificación Native PI10 R02: '+life+';12episodios en4+8;18762ticks nuevos y2269/2269entradas aplicadas. El NULL inicial se conservó. El IDdebe ser nuevo y el destino no usado: el replay no está limitado al IDde esta comprobación. El contexto/receta originales de esta ejecución siguen intactos y su hash163b está conservado; la nueva ficha sólo registra evidencia para usos posteriores. Recálculo archivado, reproducción Native y uso/adopción del principal son modalidades distintas.\n'
 return text
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');a=ap.parse_args();intent=read(TRANSACTION/'INTENT.json');before=intent['sources_before'];need(intent['old_recipe_sha256']==OLD and all(sha(Path(k))==v for k,v in before.items()),'Exact immutable run/comparison/context/import/guard/binder sources must remain unchanged');oldfile=TRANSACTION/'receta_AL_EJECUTAR.json';need(sha(oldfile)==OLD,'Actual original recipe backup required');old=read(oldfile);recipefile=RP/'recetas'/(RID+'.json');readme=RP/'LEER_PRIMERO.md';backup_readme=TRANSACTION/'LEER_PRIMERO_ANTES.md';need(sha(backup_readme)==intent['old_readme_sha256']==sha(readme),'Current README must still be its literal pre-write backup')
 resultfile=P/'estados/RPF2/RESULTADO_REPRODUCCION.json';result=read(resultfile);context=read(resultfile.parent/'CONTEXTO_EJECUCION.json');comparisonfile=P/'control/COMPARACION_REPRODUCCION_PI10_R03.json';comparison=read(comparisonfile);need(sha(comparisonfile)=='16107b948b7f03fd5e35b586ebb9be61ed21a743264edc17270b048af55e0d27'and result['status']=='COMPLETED'and result['owner_closed_coherently']is True and result['criteria_met']is True and result['last_tick']==941139,'Exact actual completed cold12 and fixed comparison');need(context['recipe_sha256']==OLD and context['fixed_recipe']==old and context['life']==result['life']and result['recipe']==RID,'Never rewrite completed replay context or original recipe');adopter=H/'incorporar_PI10_misma_identidad_R03.py';need(sha(adopter)=='b5c36b075fec1f3a9675c863b22368c078263ca71fa3778a3ef89e8a92ac7504','Prospective strict comparison contract unchanged');criteria=load('PI10_R04_fixed_pre_replay_comparison',adopter).replay_comparison_admissible(comparison)
 registered_call=read(TRANSACTION/'REGISTRADOR_EXISTENTE.json');need(registered_call['returncode']==0,'Original existing registrar must already have completed0; do not rerun it');registry=RP/'verificaciones'/RID/(result['life']+'.json');record=read(registry);need(record['recipe']==RID and record['life']==result['life']and record['recipe_sha256_at_run']==OLD and record['actual_native_execution_completed']is True and record['fixed_local_criteria_met']is True,'Existing actual Native verification record required')
 manifest=read(EVIDENCE/'MANIFIESTO_SHA256.json')
 for row in manifest['files']:
  file=EVIDENCE/row['file']
  need(Path(row['file']).name==row['file']and file.stat().st_size==row['bytes']and sha(file)==row['sha256'],'Literal stable small verification evidence changed')
 new=expected_recipe(old,result,registry,criteria)
 for key in('variants','material_supervisor','diagnostic_identity_binding','prefix','code_capsule_key','requires_explicit_material','reproduction_enabled','sources','analysis'):
  need(new[key]==old[key],'No scientific/material recipe field may change')
 # R03 used Path.write_text(newline=None): Windows translates formatting LF
 # to CRLF. Verify those exact physical bytes rather than changing the file.
 expected_physical=encoded(new).replace(b'\n',os.linesep.encode())
 need(read(recipefile)==new and recipefile.read_bytes()==expected_physical,'Current recipe must equal the ENTIRE deterministic first R03 write, no other changes');newtext=expected_readme(backup_readme.read_text('utf-8-sig'),result['life']);recipe_sha=sha(recipefile);final=TRANSACTION/'REGISTRO_COMPLETADO.json';recovery=TRANSACTION/'RECUPERACION_R04_INTENT.json';need(not final.exists()and not recovery.exists(),'Never repeat a completed/partial recovery')
 if not a.aplicar:print(json.dumps({'mode':'EXACT_PARTIAL_RECOVERY_PLAN_ONLY_NO_NATIVE','actual_recipe_sha256':recipe_sha,'old_recipe_sha256':OLD,'entire_first_recipe_write_verified':True,'registrar_already_completed_not_repeated':True,'will_write':['README exact completion','recovery intent','final proof'],'will_not_write':['recipe','context','result','Native state','registrar'],'Native':0}));return
 need(Path(sys.executable).resolve()==(C/'motor/python313/python.exe').resolve(),'Root official Python only');need(not(P/'PI10_ROOT_NATIVE_WRITER.lock').exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'Wait until unrelated Root/RP material writers close');current=C/'sistema/estado/ACTIVO.json';life=read(current)['life_id'];card=C/'sistema/estado/vidas'/life/'VIDA.json';protected=[current,card,C/'sistema'/read(card)['snapshot']];protected_before={str(f):sha(f)for f in protected};put(recovery,{'schema':'DEE.PI10.host_only_registration_recovery.R04','recorded_utc':datetime.now(timezone.utc).isoformat(),'cause':'R03 semicolon placed old-CAS and recipe write inside the for suite; second iteration rejected its own first write. No external concurrency or cognitive failure inferred.','original_R03_script_sha256':sha(H/'registrar_replay_Native_estable_PI10_R03.py'),'recipe_current_exact_first_write_sha256':recipe_sha,'old_recipe_sha256':OLD,'README_before_sha256':sha(readme),'sources_before':before,'protected_before':protected_before,'Native_imports':0,'Native_ticks':0});firstcopy=TRANSACTION/'RECETA_PRIMER_WRITE_R03.json';need(not firstcopy.exists(),'Preserve prior first-write capture');shutil.copyfile(recipefile,firstcopy);need(sha(firstcopy)==recipe_sha,'Literal partial recipe backup');readme.write_text(newtext,'utf8');need(sha(recipefile)==recipe_sha and before=={k:sha(Path(k))for k in before},'No completed run/recipe rewrite allowed');protected_after={str(f):sha(f)for f in protected};need(protected_before==protected_after,'Principal changed during document-only closure');put(final,{'schema':'DEE.PI10.actual_Native12.stable_registration.R02','completion_revision':'R04_EXACT_PARTIAL_DOCUMENT_RECOVERY','Native_imports_during_registration':0,'Native_ticks_during_registration':0,'recipe_sha256_at_run':OLD,'recipe_sha256_after_evidence_update':recipe_sha,'readme_sha256_after':sha(readme),'original_replay_sources_unchanged':True,'existing_registrar_record':str(registry),'existing_registrar_record_sha256':sha(registry),'evidence':str(EVIDENCE),'evidence_manifest_sha256':sha(EVIDENCE/'MANIFIESTO_SHA256.json'),'not_adoption':True,'reusable_new_ID_family_preserved':True,'original_failed_transaction_and_backup_preserved':True,'known_R03_host_bug_not_cognitive_failure':True,'recipe_not_rewritten_during_recovery':True,'recovery_intent_sha256':sha(recovery),'protected_before':protected_before,'protected_after':protected_after});print(json.dumps({'proof':str(final),'sha256':sha(final),'Native':0,'recipe_unchanged_from_verified_first_write':True}))
if __name__=='__main__':main()
