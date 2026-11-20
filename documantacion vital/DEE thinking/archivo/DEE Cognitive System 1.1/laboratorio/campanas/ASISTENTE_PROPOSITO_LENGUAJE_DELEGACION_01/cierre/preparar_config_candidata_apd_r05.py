"""Add the approved cost stage to a fresh still-pending CAS configuration, N0."""
import argparse,hashlib,json
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def emit(p,v):
 if p.exists():raise FileExistsError('Preserve earlier template revisions')
 p.write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--close',type=Path,required=True);a=ap.parse_args();c=a.close
 previous=c/'CONFIG_ANALISIS_CANDIDATA_APD01_R04.json';cfg=load(previous);stage=c/'COSTE_ACUMULADOR_APD01_N0';mp=stage/'MANIFIESTO.json'
 wanted='5fd5a1effdaf1ca2eb09ebbdbcf2aa63003838195a857f4623ce98065f2e764a'
 if sha(mp)!=wanted:raise ValueError('Approved cost stage manifest differs')
 members=load(mp)['members'];actual={p.relative_to(stage).as_posix():p for p in stage.rglob('*')if p.is_file()and p!=mp};expected={r['file']:r for r in members}
 if set(actual)!=set(expected):raise ValueError('Approved stage membership differs')
 for name,p in actual.items():
  if sha(p)!=expected[name]['sha256']or p.stat().st_size!=expected[name]['bytes']:raise ValueError('Approved source bytes differ')
 plan=load(stage/'PLAN_RECALCULO.json')
 if len(plan['jobs'])!=1:raise ValueError('One existing cost extraction expected')
 cfg['previous_configuration_sha256']=sha(previous);cfg['configuration_revision']='R05_with_approved_accumulator_cost_stage; no campaign CLOSED or ZIP seal'
 cfg['stages'].append({'namespace':'COSTE_ACUMULADOR','source':str(stage),'manifest':'MANIFIESTO.json','plan':'PLAN_RECALCULO.json'})
 for slot in cfg['candidate_stage_slots']:
  if slot['namespace']=='POST_RESERVA_APD01':
   slot['status']='UNEXECUTED_PROPOSAL_SUPERSEDED_BY_PROSPECTIVE_R04'
   slot['scope']='The earlier two-request proposal remains historical preparation, not an executed result. Root selected a prospective one-owner R04 window with final panels. No new R04 outcome is assumed.'
 cfg['candidate_stage_slots'].append({'namespace':'SERVICIO_APD01_R04_UN_OWNER','source':None,'status':'WAIT_FOR_ROOT_GO_ACTUAL_R03_REACHED_CUT_AND_CLOSED_R04_BYTES','expected_jobs':None,'scope':'Prospective at this preparation only. Do not combine R01/R02/R03 minutes to claim one uninterrupted owner. The real final cut follows actual R04 and any final material panels.'})
 for item in cfg['pending_components']:
  if item['id']=='PANEL_POST_RESERVA_Y_CORTE_REAL_FINAL':
   item['status']='WAIT_FOR_ACTUAL_ROOT_APPROVED_R04_AND_FINAL_MATERIAL_PANELS'
   item['scope']='Previous R1 two-request draft was not executed. Bind docs to the actual final reached cut, not a prospectively selected tick or the earlier R03 STOP if later actions occurred.'
 emit(c/'CONFIG_ANALISIS_CANDIDATA_APD01_R05.json',cfg)
 old_index=c/'INDICE_FUENTES_Y_OMISIONES_CANDIDATO_APD01_R01.json';index=load(old_index);index['schema']='APD01.final_sources_and_omissions.template.v2';index['previous_template_sha256']=sha(old_index)
 index['closed_sources_exact'].append({'namespace':'COSTE_ACUMULADOR','source_local_locator':str(stage),'manifest_relative':'MANIFIESTO.json','manifest_sha256':wanted,'manifest_members_without_self':len(members),'selected_cases':1,'new_archived_recalculation_repeated_by_this_preparation':False,'check_scope':'Approved immutable manifest membership and source hashes checked; existing byte-exact cost recalculation not repeated.'})
 row=expected['INDICE_FUENTES.json'];index['original_omission_indexes_to_preserve'].append({'namespace':'COSTE_ACUMULADOR','relative_path':'INDICE_FUENTES.json','bytes':row['bytes'],'sha256':row['sha256'],'scope':'Exact P16/P17/control/source local locators, not a new native experiment or operational snapshot package.'})
 index['currently_closed_recalculation_cases']=14;index['prospective_cases_after_service_before_postpanel_or_fullproof']=24
 index['prospective_case_count_scope']='14 closed plus10 proposed consolidated service cases. Actual R04 and FullZIP proofs can add cases only after closed bytes exist; no fixed final count asserted.'
 index['future_sources_not_yet_closed'].append({'namespace':'SERVICIO_APD01_R04_UN_OWNER','source_local_locator':None,'status':'WAIT_FOR_ACTUAL_SINGLE_OWNER_RESERVE_AND_FINAL_PANELS','expected_cases':None})
 for row in index['future_sources_not_yet_closed']:
  if row['namespace']=='POST_RESERVA_APD01':row['status']='UNEXECUTED_PROPOSAL_SUPERSEDED_BY_PROSPECTIVE_R04'
 emit(c/'INDICE_FUENTES_Y_OMISIONES_CANDIDATO_APD01_R02.json',index)
 emit(c/'VALIDACION_CONFIG_CANDIDATA_APD01_R05_N0.json',{'native_ticks':0,'closed_source_stages':len(cfg['stages']),'closed_cases':14,'provisional_consolidated_service_cases':10,'provisional_sum_before_actual_R04_or_Fullproof':24,'cost_stage_manifest_sha256':wanted,'recalculations_repeated':False,'ZIP_created':False,'S_or_MAIN_changed':False,'status':'PREPARACION_NO_FINAL'})
 print(json.dumps({'stages':len(cfg['stages']),'closed_cases':14,'provisional_with_service':24,'new_native_ticks':0,'recalculations_repeated':False,'ZIP_created':False}))
if __name__=='__main__':main()

