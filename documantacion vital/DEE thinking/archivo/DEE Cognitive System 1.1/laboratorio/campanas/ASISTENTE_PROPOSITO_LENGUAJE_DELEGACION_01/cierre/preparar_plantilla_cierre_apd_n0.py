"""Prepare exact closed-source/omission and delta templates, without final closure, ZIP or Runtime."""
import argparse,ast,hashlib,json
from pathlib import Path
EXPECTED_HELPERS={
 'ensamblar_analisis_apd_cas_R03.py':'817e1c433e4e908c8ce67d171ab8390ad610fd1d9fe482c33b2409f4c9ce5a09',
 'repetir_todo_apd_cas.py':'117b76c8f532b390043d590154b545022a0f5ecd3f9e0c5cccd3e2dc0ffaa0b0',
}
EXPECTED_DESCRIPTORS={
 'app/access_guard.py':'6e9e159a9623ec0ecbc71bd00223b33f94cf4ec66455d4df92f5fe216fbaa682',
 'app/servicio_persistente.py':'7f68f9f2726f8063d46aa0a5d21b3f05c887a795db0dff3777d0280a6626d25d',
 'gestionar.py':'c69786e1b0d37087ac32f0d82e455e3cb5184b19c8c0ca99562fa6c76c32bdcc',
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def emit(p,v):
 if p.exists():raise FileExistsError('Keep earlier preparation: '+str(p))
 p.write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--close',type=Path,required=True);ap.add_argument('--system',type=Path,required=True);a=ap.parse_args();close=a.close
 config_path=close/'CONFIG_ANALISIS_CANDIDATA_APD01_R03.json';cfg=read(config_path)
 helper_rows=[]
 for name,wanted in EXPECTED_HELPERS.items():
  p=close/name
  if sha(p)!=wanted:raise ValueError('Selected helper changed: '+name)
  ast.parse(p.read_text(encoding='utf8'));helper_rows.append({'file':name,'sha256':wanted,'bytes':p.stat().st_size})
 previous_checks=read(close/'VALIDACION_CONFIG_CANDIDATA_APD01_R02.json')['closed_stage_checks']
 expected_manifests={r['namespace']:r['manifest_sha256']for r in previous_checks};expected_manifests['PERIMETRO_METADATA']='bcd670b6ab50bf2f15ae20b384c3824c596c62f995da8a95339030991663ebc4'
 stages=[];indexes=[];total=0
 for spec in cfg['stages']:
  root=Path(spec['source']);manifest=root/spec['manifest'];digest=sha(manifest)
  if digest!=expected_manifests[spec['namespace']]:raise ValueError('Previously closed manifest changed: '+spec['namespace'])
  m=read(manifest);members=m['members'];names=[r.get('file',r.get('path'))for r in members]
  if len(names)!=len(set(names)):raise ValueError('Repeated closed member name')
  if any(not(root/n).is_file()for n in names):raise ValueError('Closed member absent')
  plan=read(root/spec['plan']);jobs=plan.get('jobs',plan.get('cases'))
  if not isinstance(jobs,list):raise ValueError('Plan shape')
  count=len(jobs)+len(spec.get('extra_cases',[]));total+=count
  stages.append({'namespace':spec['namespace'],'source_local_locator':str(root),'manifest_relative':spec['manifest'],'manifest_sha256':digest,'manifest_members_without_self':len(members),'selected_cases':count,'new_archived_recalculation_repeated_by_this_preparation':False,'check_scope':'Previously verified closed manifest hash and named-member existence only; no native replay and no repeat of byte-exact scientific recalculations.'})
  for row in members:
   name=row.get('file',row.get('path'));upper=name.upper()
   if ('OMISION' in upper or 'OMITT' in upper or upper.startswith('INDICE') or 'COMPLETE_STATE_LOCAL' in upper) and name.lower().endswith(('.json','.csv','.txt','.md')):
    indexes.append({'namespace':spec['namespace'],'relative_path':name,'bytes':row['bytes'],'sha256':row['sha256'],'scope':'Preserve the original index and all local locators exactly; do not infer that its excluded complete operational states are included in analysis.'})
 if total!=13:raise ValueError('Closed subset count changed unexpectedly')
 for name,wanted in EXPECTED_DESCRIPTORS.items():
  if sha(a.system/name)!=wanted:raise ValueError('Descriptive source byte mismatch: '+name)
 old_delta=read(close/'PLAN_DELTA_CANDIDATO_APD01_R01.json');delta=old_delta.copy();rows=[]
 for item in old_delta['files_observed']:
  name=item['relative_system_path'];p=a.system/name;ast.parse(p.read_text(encoding='utf-8-sig'))
  rows.append({**item,'bytes_observed':p.stat().st_size,'sha256_observed_not_final_freeze':sha(p),'final_selection_status':'WAIT_FOR_ROOT_POST_SERVICE_FREEZE_CONFIRMATION'})
 name='app/access_guard.py';p=a.system/name
 rows.append({'relative_system_path':name,'group':'DESCRIPTIVE_GUARD_METADATA_CORRECTION_ONLY','bytes_observed':p.stat().st_size,'sha256_observed_not_final_freeze':sha(p),'final_selection_status':'WAIT_FOR_ROOT_POST_SERVICE_FREEZE_CONFIRMATION','analysis_target':'DELTA_OPERATIVO/sistema/'+name})
 delta.update({'schema':'APD01.system_delta_candidate.v2','status':'PREPARACION_NO_FINAL','files_observed':rows,'source_system_local_locator':str(a.system),'actor_write_performed':False,'new_native_ticks':0,'candidate_contract_source_not_captured_yet':True,'candidate_contract_delta_gloss':'Five scheduled uses were observed and consumed in that protocol; neither physical erasure nor a universal five-use limit is established. Sixth use not tested. Final root contract bytes remain pending.'})
 emit(close/'PLAN_DELTA_CANDIDATO_APD01_R02.json',delta)
 cfg['configuration_revision']='R04_templates_only_after_R03_reserve_start; no closed campaign claim'
 cfg['previous_configuration_sha256']=sha(config_path)
 for slot in cfg['candidate_stage_slots']:
  if slot['namespace']=='SERVICIO_APD01':
   slot['expected_jobs']=10;slot['scope']='Await CLOSED notice. Includes interrupted R01 and R02, their preserved pending/future, actual R03 and pilot once. Failed prior minutes are not counted toward R03.'
 cfg['candidate_stage_slots'].append({'namespace':'POST_RESERVA_APD01','status':'WAIT_FOR_ACTUAL_R03_STOP_AND_ROOT_GO_AND_CLOSED_POST_PANEL','source':None,'expected_jobs':None,'scope':'Two prospectively fixed actual same-life requests, separate from 4500s reserve. No current final cut or success assumed.'})
 cfg['pending_components'].append({'id':'PANEL_POST_RESERVA_Y_CORTE_REAL_FINAL','status':'WAIT_FOR_R03_FREE_THEN_GO','scope':'Post-panel changes the real final cut. Do not bind docs/Word/VIDA to the earlier R03 STOP cut as if nothing happened.'})
 emit(close/'CONFIG_ANALISIS_CANDIDATA_APD01_R04.json',cfg)
 template={'schema':'APD01.final_sources_and_omissions.template.v1','status':'PREPARACION_NO_FINAL','new_native_ticks':0,'final_campaign_cut':None,'final_paired_state_locator':None,'analysis_not_operational_backup':True,'closed_sources_exact':stages,'original_omission_indexes_to_preserve':indexes,'helpers_exact':helper_rows,'future_sources_not_yet_closed':[{'namespace':'SERVICIO_APD01','source_local_locator':str(close/'SERVICIO_APD01_R01'),'status':'WAIT_FOR_R01_R02_NEGATIVE_AND_ACTUAL_R03_CLOSED_BYTES','expected_cases':10},{'namespace':'POST_RESERVA_APD01','source_local_locator':None,'status':'WAIT_FOR_ROOT_GO_AND_ACTUAL_POST_PANEL'},{'namespace':'DELTA_OPERATIVO','source_local_locator':None,'status':'WAIT_FOR_FINAL_S_FREEZE_AND_ROOT_CONTRACT_GUIDE_METADATA'},{'namespace':'PRUEBA_FULL_EXACTO','source_local_locator':None,'status':'WAIT_FOR_EXACT_FULL_PACKAGE_AND_EXECUTED_PROOF'}],'public_document_slots':[{'id':x['id'],'analysis_target':x['to'],'source_local_locator':None,'bytes':None,'sha256':None,'status':x['status']}for x in cfg['candidate_public_file_slots']],'omission_policy':[{'category':'Complete native and paired operational states','included_in_analysis':False,'record_required':'Exact local locator, full snapshot SHA256, tick, owning life, protocol/queue/outbox dependency locator; never replace with RAW-only arrays or recipe.'},{'category':'Official engine, wheel, previous large ZIPs','included_in_analysis':False,'record_required':'Use installed product/operational collaboration package; no confidentiality or completeness inference from omission.'},{'category':'Deep telemetry and compact lossless projections','included_in_analysis':'Only selected exact primary/projection files named by closed manifests','record_required':'Preserve original byte-vs-JSON-value distinction and regeneration proof. No removal of unique negative cases.'},{'category':'R01/R02 technical service failures','included_in_analysis':True,'record_required':'Preserve their primary outcomes and queued/pending identities; distinguish interrupted instrumentation from physical loss. Do not add elapsed minutes to R03.'}],'dependency_order_avoiding_self_hash_cycles':['1. Close service and actual post-panel; preserve final world+paired protocol and local locators.','2. Freeze actual S delta, root scientific report, contract/guide, continuity and Word bytes. Final ZIP hash remains an external field, never a source inside that same ZIP.','3. Complete any independent operational FullZIP proof, then include that proof and its tested FullZIP hash in analysis only if FullZIP does not include this later analysis ZIP.','4. Assemble final CAS from immutable closed namespaces plus exact public document bytes. Embedded manifests exclude themselves; all scientific references remain unchanged.','5. Seal one analysis ZIP only after Root GO, extract those exact bytes elsewhere, restore all CAS aliases and run stdlib global cases with outputs outside extraction.','6. Write VERIFICACION_FINAL_EXTERNA outside analysis ZIP with its SHA256, commands and limitations. Never add the verification ZIP hash back to itself. A changed member requires a new candidate and affected verification.'],'currently_closed_recalculation_cases':total,'prospective_cases_after_service_before_postpanel_or_fullproof':total+10,'no_scientific_case_recalculated_by_this_template':True,'final_seal_authorized':False}
 emit(close/'INDICE_FUENTES_Y_OMISIONES_CANDIDATO_APD01_R01.json',template)
 emit(close/'VERIFICACION_PLANTILLA_CIERRE_APD01_N0.json',{'native_ticks':0,'helpers_exact':helper_rows,'closed_stage_manifests_exact':len(stages),'closed_member_existence_checks':sum(x['manifest_members_without_self']for x in stages),'existing_closed_cases':total,'expected_service_cases':10,'expected_cases_before_postpanel_or_fullproof':23,'actor_source_candidates':len(rows),'S_writes':False,'ZIP_created':False,'final_document_bytes_captured':False,'no_omission_decision_finalized_by_template':True})
 print(json.dumps({'closed_stages':len(stages),'closed_cases':total,'expected_before_postpanel_or_fullproof':23,'source_candidates':len(rows),'omission_index_locators':len(indexes),'native_ticks':0,'ZIP_created':False}))
if __name__=='__main__':main()

