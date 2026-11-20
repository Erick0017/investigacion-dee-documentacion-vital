"""Pending final assembly plan from closed subsets and actual R03 records, N0 only."""
import argparse,collections,hashlib,json,zlib
from pathlib import Path
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,x):
 if p.exists():raise FileExistsError('Preserve prior preparation')
 p.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--close',type=Path,required=True);ap.add_argument('--service-root',type=Path,required=True);ap.add_argument('--cas',type=Path,required=True);a=ap.parse_args();c=a.close
 r3=a.service_root/'SERVICIO_60MIN_APD_R03';cutpath=r3/'CORTE_PARA_MANUAL.json'
 wanted='1d89d1feca09958682cf784199c1270ae3c590d458a2fec15c74b30f24ab6dd9'
 if sha(cutpath)!=wanted:raise ValueError('Actual R03 cut changed')
 cut=read(cutpath);time=read(r3/'RECALCULO_TIEMPO_APD.json');tables=read(r3/'PANELES_Y_FUNCIONES.json')
 fresh=[r for r in tables['APD_primitive_uses_including_composition_stages']if r['id'].startswith('apd62_')]
 old=[r for r in tables['APD_primitive_uses_including_composition_stages']if not r['id'].startswith('apd62_')]
 memory=[r for r in tables['memory_uses']if r['id'].startswith('apd62_')]
 fact={'schema':'APD01.R03.closed_actual_observation_for_pending_final_assembly.v1','native_ticks_for_this_extraction':0,'source_cut':{'file':str(cutpath),'sha256':wanted},'sources':[{'file':str(r3/n),'sha256':sha(r3/n)}for n in('RECALCULO_TIEMPO_APD.json','PANELES_Y_FUNCIONES.json')],'actual_R03_cut':cut['main'],'post_STOP_pair_manifest':cut['paired_export']['manifest'],'post_STOP_pair_manifest_sha256':cut['paired_export']['manifest_sha256'],'R03_world_enabled_seconds_after_discounts':time['unpaused_operational_seconds'],'R03_not_single_owner_or_uninterrupted_session':True,'R03_clean_closure':cut['persistent_service']['clean_closure'],'original_job_active1_negative_preserved':cut['operational_issues'],'later_recorded_process_absence_is_not_retroactive_clean_close':cut['late_recorded_own_PIDs']if 'late_recorded_own_PIDs'in cut else 'See original cut PID observations; no historical job criterion is rewritten.','source_capture_scope':cut['source_capture_scope'],'fresh_APD_primitive_uses':len(fresh),'inherited_APD_primitive_uses_completed_now_but_not_new_R03_inputs':len(old),'fresh_APD_numeric_correct_given_emitted_operator':sum(r['correct_given_actual_operator']for r in fresh),'fresh_APD_within_prepared_modelled_budget2':sum(r['completed_within_prepared_modeled_budget2']for r in fresh),'fresh_APD_route_histogram':dict(collections.Counter(str(r['route'])for r in fresh)),'fresh_old_memory_uses':len(memory),'fresh_old_memory_matches_explicit_history':sum(r['matches_expected']for r in memory),'R04_is_a_new_prospective_window_same_life_not_minutes_added_to_R03':True,'current_or_final_R04_cut':None}
 if len(fresh)!=61 or len(old)!=4 or len(memory)!=36 or fact['fresh_APD_within_prepared_modelled_budget2']!=42 or fact['R03_clean_closure']is not False:raise ValueError('Recorded R03 scope differs')
 emit(c/'LECTURA_ARCHIVADA_R03_PARA_CIERRE_N0.json',fact)
 previous=c/'CONFIG_ANALISIS_CANDIDATA_APD01_R05.json';cfg=read(previous)
 cfg['previous_configuration_sha256']=sha(previous);cfg['configuration_revision']='R06_pending_final_with_closed_R03_facts_and_single_owner_R04_running; no final campaign seal'
 for slot in cfg['candidate_stage_slots']:
  if slot['namespace']=='SERVICIO_APD01':
   slot['expected_jobs']=13;slot['scope']='One final immutable stage will include R01/R02 negatives, actual R03 with clean=false and partial utility, one pilot, actual R04 only after STOP, plus N0 instrumentation failures and unexecuted pre-poll source revisions.'
  if slot['namespace']=='SERVICIO_APD01_R04_UN_OWNER':
   slot['status']='RUNNING_WAIT_FOR_ACTUAL_STOP_AND_CLOSED_BYTES_INCLUDED_INSIDE_SERVICIO_APD01_NOT_DUPLICATED'
  if slot['namespace']=='PRUEBA_PAQUETE_EXACTO':
   slot['expected_jobs']=1;slot['scope']='One prospective archived FullZIP proof case only after exact package execution. Do not count it as executed yet or as another native capability.'
 cfg['known_closed_cases']=14;cfg['provisional_final_cases_if_expected_service_and_fullproof_close']=28;cfg['R04_final_state_not_captured']=True
 emit(c/'CONFIG_ANALISIS_CANDIDATA_APD01_R06.json',cfg)
 preserved=[]
 for label in('JOB_ACCOUNTING_N0_R01','JOB_ACCOUNTING_N0_R02'):
  for p in sorted((a.service_root/label).rglob('*')):
   if p.is_file():preserved.append({'type':'N0_plain_CPython_fixture_no_DEE_Runtime','file':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'analysis_target':'SERVICIO_APD01/EVIDENCIA/INSTRUMENTACION/'+label+'/'+p.relative_to(a.service_root/label).as_posix()})
 source_names=[c.parent/'servicio/ensayo_servicio_apd_r04_R1_PRE_POLL_NO_EJECUTADO.py',c.parent/'servicio/ensayo_servicio_apd_r04_un_owner.py',c.parent/'servicio/distribucion/probar_servicio_distribuido_PRE_POLL_NO_EJECUTADO.py',c.parent/'servicio/distribucion/probar_servicio_distribuido.py']
 for p in source_names:
  preserved.append({'type':'UNEXECUTED_pre_poll_source_revision'if'NO_EJECUTADO'in p.name else 'SELECTED_source_wait_for_actual_execution_and_proof','file':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'analysis_target':'SERVICIO_APD01/CODIGO_CIERRE/'+p.relative_to(c.parent/'servicio').as_posix()})
 emit(c/'FUENTES_ADVERSAS_Y_NO_EJECUTADAS_PARA_CAS_N0.json',{'native_ticks':0,'files':preserved,'scope':'Keep Win267 fixture failures, later successful technical fixture, and both source revisions. A successful plain CPython fixture does not establish why historical R03 reported Jobactive1. No source labelled unexecuted becomes an actual DEE trial.'})
 objects=read(a.cas/'INDICE_OBJETOS_Y_ALIASES.json')['objects'];known=set(objects);additional={};selected=[]
 for label in('SERVICIO_60MIN_APD_R01','SERVICIO_60MIN_APD_R02','SERVICIO_60MIN_APD_R03'):
  root=a.service_root/label;paths=[p for p in root.iterdir()if p.is_file()and p.name not in('REGISTROS_TRANSPORTE.json.gz','REGISTROS_TRANSPORTE_POSTSTOP.json.gz')and not p.name.endswith('.deetsnap.gz')]
  for folder in root.iterdir():
   if folder.is_dir()and(folder.name in('codigo','artefactos','PILOTO_CODIGO')or folder.name.startswith('CODIGO_RECALCULO')):
    paths.extend(p for p in folder.rglob('*')if p.is_file())
  for name in('CORTE_INTERRUMPIDO_POSTSTOP/EXPORTACION_SERVICIO.json','PAQUETE_FINAL_POSTSTOP/EXPORTACION_SERVICIO.json'):
   if(root/name).is_file():paths.append(root/name)
  for p in paths:
   digest=sha(p);selected.append({'file':str(p),'bytes':p.stat().st_size,'sha256':digest})
   if digest not in known and digest not in additional:
    data=p.read_bytes();additional[digest]={'bytes':len(data),'zlib_deflate_estimate':len(zlib.compress(data,9))}
 # This is a measured known-subset estimate, not a guessed final R04/manual size.
 base=5011586;extra=sum(v['zlib_deflate_estimate']for v in additional.values())
 emit(c/'PLAN_TAMANOS_CAS_PENDIENTE_APD01_N0.json',{'native_ticks':0,'ZIP_generated':False,'six_closed_namespaces':{'logical_files':506,'unique_objects':386,'logical_original_bytes':32885066,'stored_unique_original_bytes':30330935,'stage_expanded_bytes':30623866,'measured_deflate_estimate_including_current_CAS_metadata':base,'recalculation_cases':14,'separate_copy_proof_file':'PRUEBA_PREPARACION_CAS_SEIS_R05.json','separate_copy_proof_sha256':sha(c/'PRUEBA_PREPARACION_CAS_SEIS_R05.json')},'closed_service_R01_R02_R03_known_subset':{'selection_scope':'All top-level files except full inherited transport and native snapshots, selected archived source/artifact/code folders and paired manifests. May be a superset of the final builder selection; excludes active R04 entirely.','source_files':len(selected),'additional_unique_contents_after_existing_CAS':len(additional),'additional_deflate_estimate':extra,'known_subset_total_estimate':base+extra,'sources':selected},'limit_bytes':16000000,'headroom_for_unknown_R04_fullproof_manual_delta_and_final_metadata_against_known_subset':16000000-base-extra,'unknown_not_measured':['R04 active records and final real-time/functional outcomes','future exact FullZIP proof','final root report/Word/continuity/contract/guide/delta bytes','final CAS/ZIP metadata and central-directory overhead'],'plan':'Keep every decisive negative and exact source revision; rely first on exact-content deduplication. Measure the actual complete candidate before deciding whether lossless solid fallback is needed. No claim that this known-subset estimate is a final ZIP size.'})
 print(json.dumps({'R03_fresh_APD':len(fresh),'within_budget2':fact['fresh_APD_within_prepared_modelled_budget2'],'R03_clean':fact['R03_clean_closure'],'closed_cases':14,'prospective_total':28,'known_subset_deflate_estimate':base+extra,'unmeasured_headroom':16000000-base-extra,'native_ticks':0,'ZIP_generated':False}))
if __name__=='__main__':main()

