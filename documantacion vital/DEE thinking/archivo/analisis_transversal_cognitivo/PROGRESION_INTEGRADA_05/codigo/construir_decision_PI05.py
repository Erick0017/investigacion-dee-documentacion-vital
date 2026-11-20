"""Read-only by default. Seal a reasoned PI05 decision only after actual gates.
No DEE import, Native run, product deployment, selection or promotion here.
"""
from pathlib import Path
import argparse,ast,datetime,hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';CS=P/'estados/candidato/sistema';RP=C/'reproducibilidad'
SOURCE='ECI02_PI03_REPRO_PI04_PI05_GUARD_01';TARGET='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
KEY='DEE.Cognitive.PI04.C2C.coordination.R01';FINAL_T=824911
FINAL_SHA='a63805765aaff9a1de938fd70181771f6f7b784bd19784472b895ab341ec1c31'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return{'path':str(Path(p).resolve()),'sha256':sha(p)}
def need(x,s):
 if not x:raise ValueError(s)
def load(p,n):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def phase(name):
 p=P/'control'/name
 if not p.is_file():return None,p
 j=read(p);ok=j.get('status')=='COMPLETED_PHASE'and j.get('owner_closed_coherently')is True and not j.get('error')and not j.get('scientific_stop')
 return (j if ok else None),p
def evidence(paths):return[info(x)for x in dict.fromkeys(paths)if Path(x).is_file()]
def proposed_code():
 # Follow literal local dependencies and module names. Only these scientific
 # roots and app hooks seed the closure; no state/runtime/manual copy occurs.
 seeds=['app/cola_local.py','app/mundo_genesis_apd05.py','app/pi05_identidad_c2c.py','capacidades/pi04_dispatcher.py','capacidades/pi05_transito_causal_R01.py','capacidades/pi05_guardia_transito_R01.py','capacidades/pi05_c2c_ofertas_R01.py','capacidades/pi05_permiso_principal_R01.py']
 canonical={x.relative_to(CS).as_posix().casefold():x.relative_to(CS).as_posix()for family in('app','capacidades')for x in(CS/family).iterdir()if x.is_file()}
 todo=list(seeds);seen=set();literal_files=[]
 while todo:
  rel=todo.pop();rel=canonical.get(rel.casefold(),rel);file=CS/rel
  if rel in seen:continue
  need(file.is_file(),'Missing local required source '+rel);seen.add(rel)
  if file.suffix=='.py':
   tree=ast.parse(file.read_text(encoding='utf-8-sig'));strings=[n.value for n in ast.walk(tree)if isinstance(n,ast.Constant)and isinstance(n.value,str)]
   for n in ast.walk(tree):
    if isinstance(n,ast.ImportFrom)and n.module in('app','capacidades'):
     strings.extend(x.name for x in n.names)
  else:
   obj=read(file);strings=[]
   def walk(v):
    if isinstance(v,str):strings.append(v)
    elif isinstance(v,dict):
     for k,x in v.items():strings.append(k);walk(x)
    elif isinstance(v,list):
     for x in v:walk(x)
   walk(obj)
  for value in strings:
   if not value or Path(value).name!=value:continue
   names=[value]if value.endswith(('.py','.json'))else[value+'.py']
   for name in names:
    for family in('capacidades','app'):
     q=CS/family/name
     if q.is_file()and name!='CATALOGO_CAPACIDADES.json':todo.append(family+'/'+name)
  literal_files.append(rel)
 items=[]
 for rel in sorted(seen):
  if rel=='gestionar.py' or not rel.endswith(('.py','.json')):continue
  src=CS/rel;target=S/rel
  if target.exists()and sha(src)==sha(target):continue
  items.append({'file':rel,'sha256':sha(src),'product_before_sha256':sha(target)if target.exists()else None})
 need(not any(x['file']=='gestionar.py'for x in items),'Never deploy old S5 gateway')
 return items,sorted(seen)
def recovery():
 rows={};paths=[]
 for p in sorted((P/'control').glob('PI05_*.json')):
  # Only bounded actual recovery result filenames are parsed; protocol/docs
  # do not become executions because they contain matching words.
  try:j=read(p)
  except (json.JSONDecodeError,UnicodeError,OSError):continue
  if j.get('schema')!='DEE.PI05.P0_recovery_matched_diagnosis.R02'or j.get('legal_wait_first_ticks')!=3:continue
  if j.get('status')=='COMPLETED_RECOVERY_DIAG_RECORDED'and j.get('owner_closed_coherently')is True and j.get('condition')in('guardia','sham'):
   need(j['condition']not in rows,'Duplicate recovery result: review explicitly');rows[j['condition']]=j;paths.append(p)
 return rows,paths
def build(process_path):
 helper=load(P/'codigo/incorporar_PI05.py','pi05_reasoned_incorporator_readonly')
 old=helper.protect_parent();engine=helper.frozen_engine()
 pairs={};paths={}
 names={'panel':'PI05_INTEGRACION_PANEL_R01.json','comparaciones':'PI05_INTEGRACION_COMPARACIONES_R01.json','reserva':'PI05_INTEGRACION_RESERVA_R01.json','retencion':'PI05_INTEGRACION_RETENCION_R01.json','reapertura':'PI05_INTEGRACION_REAPERTURA_R01.json','final':'PI05_INTEGRACION_FINAL_R01.json','ordA':'PI05_ORD_A_R01.json','ordB':'PI05_ORD_B_R01.json'}
 for k,n in names.items():pairs[k],paths[k]=phase(n)
 guard_path=P/'control/PI05_GUARD_FI_GLOBAL_R01.json';sham_path=P/'control/PI05_SHAM_FI_GLOBAL_R01.json';rp_path=P/'control/FISICA_RP_GUARDIA_REPRODUCIDA_PI05_R01.json'
 guard=read(guard_path);sham=read(sham_path);replay=read(rp_path);rec,recpaths=recovery();missing=[]
 def gate(name,ok,criterion,result,refs):
  if not ok:missing.append(name)
  return{'satisfied':bool(ok),'criterion':criterion,'result':result,'evidence':evidence(refs)}
 main=[pairs[k]for k in('panel','comparaciones','reserva','retencion','reapertura','final')]
 allmain=all(main);baseok=all(j.get('Native_inputs',{}).get('rejected_or_other')==0 and j.get('guard_injections_by_this_runner')==0 and j.get('guard_after',{}).get('RAW')==str(4<<60)for j in main if j)
 matching=guard.get('owner_closed_coherently')is True and sham.get('owner_closed_coherently')is True and guard['summary']['early_physical_choice']==1 and sham['summary']['early_physical_choice']==-1 and guard['summary']['Native_inputs']['applied']==sham['summary']['Native_inputs']['applied']==177
 orderok=all(pairs[k]and pairs[k]['old_correct']==3 and pairs[k]['C2C_products']==2 and pairs[k]['Native_inputs']['applied']==900 for k in('ordA','ordB'))
 recok=set(rec)=={'guardia','sham'}and all(x.get('summary',{}).get('Native_inputs',{}).get('applied')==176 for x in rec.values())
 # The runner summary covers176oldFI; the fixed extra support is separately
 # checked in its own applied request. Do not miscount it as an alias.
 if set(rec)=={'guardia','sham'}:
  recok=recok and all(x.get('new_Native_ticks')==201 and x.get('error')is None and x.get('all177_input_denominators',{}).get('unique_requested')==177 and x.get('all177_input_denominators',{}).get('applied')==177 and x.get('support_receipt_after_saved_snapshot',{}).get('status')=='applied' for x in rec.values())
  recok=recok and rec['guardia'].get('source_physical')==rec['sham'].get('source_physical')and rec['guardia'].get('source_causal_prefix_sha256')==rec['sham'].get('source_causal_prefix_sha256')and rec['guardia'].get('calendar_preregistered_from_old_contract')==rec['sham'].get('calendar_preregistered_from_old_contract')
 g={}
 g['functional_gain']=gate('functional_gain',matching,'Fixed preFI prefix: guard+1 versus matched sham−1 with177applied and unchanged q4/q6.',{'guard':guard['summary']['early_physical_choice'],'sham':sham['summary']['early_physical_choice'],'classification':'prepared preventive P0; not acquired self-repair'},[guard_path,sham_path,P/'control/CONTRASTE_CAUSAL_GUARD_SHAM_PI05_R01.json'])
 g['conservation']=gate('conservation',allmain and baseok and pairs['panel']['old_correct']==12 and pairs['final']['old_correct']==3,'Historical12uses atT819484 and final3uses atT824911, no reteaching/guard reinjection.',{'full_panel_cut':819484,'full_panel':None if not pairs['panel']else pairs['panel']['old_correct'],'last_cut_panel_is_only3':True},[paths['panel'],paths['final']])
 g['reserved_comparisons']=gate('reserved_comparisons',pairs['comparaciones']and pairs['comparaciones']['old_correct']==3 and [x['observed']for x in pairs['comparaciones']['rows']if x['kind']=='OLD_FUNCTION']==[1,-1,0],'Three prespecified new operand pairs20/7,4/16,13/13; NULL is not zero.',{'correct':None if not pairs['comparaciones']else pairs['comparaciones']['old_correct'],'inputs':528},[paths['comparaciones']])
 six=all(pairs[k]and pairs[k]['C2C_products']==2 and pairs[k]['Native_inputs']['applied']==372 for k in('reserva','retencion','reapertura'))
 g['combined_function_and_reopening']=gate('combined_function_and_reopening',six,'Six same-life actual64Bproducts across3processes, actual Native number drives second Native use.',{'products':6 if six else None,'Native_inputs':1116 if six else None,'sequence':'hostprepared; no learned plan'},[paths[k]for k in('reserva','retencion','reapertura')])
 g['phase_order_controls']=gate('phase_order_controls',orderok and recok,'Two order/11-start-offset controls each5correct/900, and both matched postfailure wait3diagnostics closed; report actual recovery difference rather than require a chosen answer.',{'order_A_complete':bool(pairs['ordA']),'order_B_complete':bool(pairs['ordB']),'recovery_conditions_closed':sorted(rec),'C2C_effective_calendar_realigned':'q818869/read818875 inbothORD; no independent phase-transfer claim'},[paths['ordA'],paths['ordB'],*recpaths])
 g['source_reopening']=gate('source_reopening',allmain and all(j['owner_closed_coherently']for j in main),'Same life reopened between phases with prior physical cut checked, no restored/reset environmental progress.',{'phase_processes':6,'same_life':SOURCE,'product_reopen0_still_required_before_adopt':True},[paths[k]for k in('reserva','retencion','reapertura','final')])
 g['new_function_at_final_cut']=gate('new_function_at_final_cut',six and pairs['final']and pairs['final']['old_correct']==3 and pairs['final']['after_tick']==FINAL_T,'Final declared protocol window: C2C lastused atT824621 then3olduses throughT824911, persistent guard and closed complete state. No additional C2C material use atlasttick claimed.',{'C2C_last_material_cut':824621,'final_old3_cut':FINAL_T,'no_full_panel_atlastcut':True},[paths['reapertura'],paths['final']])
 rpok=replay.get('actual_replay_status')=='COMPLETED'and replay.get('actual_fixed_local_criteria')is True and replay.get('all_physical_and_input_equalities_hold')is True and replay.get('actual_replay_Native_ticks')==198 and replay.get('actual_replay_inputs',{}).get('applied')==177
 g['decisive_recipe_replay']=gate('decisive_recipe_replay',rpok,'Actual Cognitive RP guard198ticks/177inputs, full causal/physical prefix and69frames exact; documentary comparison adds0ticks.',{'cold_Native_ticks':198,'all_equalities':replay.get('all_physical_and_input_equalities_hold'),'not_full_chain_cold_replay':True},[rp_path])
 card=read(CS/'estado/vidas'/SOURCE/'VIDA.json');need(card['physical']['N']==67 and card['physical']['tick']==FINAL_T and card['snapshot_sha256']==FINAL_SHA,'Final source advanced/changed; do not seal olderfuture')
 pair=RP/'materiales'/('PI03_PI05_FINAL_GUARD_T'+str(FINAL_T));manifest=pair/'EXPORTACION_SERVICIO.json';pres=pair.parent/(pair.name+'_PRESERVACION.json');pm=read(manifest);need(pm['snapshot_sha256']==FINAL_SHA and pm['physical']==card['physical'],'Stablepair not final source')
 approved,closure=proposed_code();cas=[{'file':n,'sha256':sha(C/n)}for n in sorted(helper.CAS_REQUIRED)]
 chain=[P/'fuentes/PI04_MAIN02_IMPORTACION_LITERAL.json',P/'control/IMPORTACION_ECI02_PI03_REPRO_PI04_PI05_REAL_PRE_01.json',P/'control/IMPORTACION_ECI02_PI03_REPRO_PI04_PI05_GUARD_01.json',P/'fuentes/CONTRASTE_PREFIJOS_C2C_816019_PI05.json']
 need(all(x.is_file()for x in chain),'Missing preserved genealogy source')
 genealogy={'schema':'DEE.PI05.continuous_candidate_genealogy.v1','source_life_id':SOURCE,'source_final_cut':{'N':67,'tick':FINAL_T,'snapshot_sha256':FINAL_SHA},'physical_parent':{'life_id':helper.PARENT,'tick':helper.PARENT_T,'snapshot_sha256':helper.PARENT_SHA},'continuous_acquisitions_not_merged':True,'chain':evidence(chain),'branch_scope':'Inherited PI03→PI04REAL/C2C→realRET2and5words817876→GUARDprevention→same-lifeconservation/integration. Failed818074,ORD,recovery,NONE/YOKE are separate futures, never source memories.','whole_final_pair':str(pair),'final_manifest_sha256':sha(manifest)}
 gp=P/'control/GENEALOGIA_CANDIDATA_PI05_PARA_ADOPCION.json';gb=(json.dumps(genealogy,ensure_ascii=False,indent=2)+'\n').encode('utf8')
 result={'approved_for_adoption':not missing,'life_id':TARGET,'source_life_id':SOURCE,'desired_cut':{'N':67,'tick':FINAL_T,'snapshot_sha256':FINAL_SHA},'pair':{'directory':str(pair),'manifest_sha256':sha(manifest)},'stable_pair_relative_to_product':pair.relative_to(C).as_posix(),'direct_preservation':info(pres),'approved_code_files':approved,'gates':g,'product_cas_baselines':cas,'genealogy_proof':{'path':str(gp),'sha256':hashlib.sha256(gb).hexdigest()},'scope':'Local preventive P0 support preserving inherited associations, comparison, arithmetic and assisted two-Native C2C chain in one real descendant; no general autonomy or learned guard selection.','gains':['FI14/3 recovers correct+1 in prevention versus matchedsham−1','12historicaluses+3reserved comparisons+6actualC2Cproducts+3finaluses coexist inonecontinuation','One legal support birth persists; no periodiccleanup/retaughtreferences','Exact complete finalpair preserved directlyinRP; reproducible guardinstrument available from Cognitive'],'losses':['No new material loss observed in declared finalprotocol; adverse oldPI04/REAL/NONE/YOKE/SHAM kept','NOT tested: complete12panel atT824911, unrestricted lifetime/cadence/generalpolicy'],'uncertainties':['Historical origin/uniqueidentity of oldzeroZ is not fullytraced','Postguard failure-dependent newlearning not tested: sixC2Coutcomes are nonfailure','ORD C2C calendars normalize tosameeffectivephase;11tickstartoffset not independentphase transfer','Recoverywait0 andB4 were omitted prospectively for6GB; notfailed','Coldguard Native replay had no complete original-filesystemfence; staticlocal-runtime review and actualproduct0reopen are separate'],'assistance':['OperatorpreparedSEM4supportP0','Hostinitiates opportunities and fixed query→Nativefunction→actualresult→Nativeuse sequence','Context/operandfixtures/resources and device law are external; actualoperation,number,route come from Native'],'evidence':evidence([*paths.values(),guard_path,sham_path,rp_path,*recpaths]),'regression_coverage':{'historical_panel':{'uses':12,'through_tick':819484},'newcomparison_reserve':{'uses':3,'through_tick':820078},'C2C':{'uses':6,'through_tick':824621},'final_old_uses':{'uses':3,'through_tick':FINAL_T},'no_material_retest_after_target_import':True},'process_proof':str(process_path.resolve()),'catalog_entry':{'id':'PI05_GUARDIA_LOCAL_Y_COORDINACION_C2C_01','name':'Protección física preparada y continuidad C2C asistida','kind':'vida_con_capacidades_adquiridas_y_soporte_P0_preparado','status':'OPERATIVE_WITH_DECLARED_LIMITS','domain':'Sparse independent comparison0..20, bounded inherited associations/arithmetic and fixedcontextC2Cprotocol','not_claimed':['guardlearned','autonomousrecovery','autogeneratedplan','generalagency']},'new_contract':{'file':'contratos/PI05_C2C_USO_PRINCIPAL_01.json','product_before_sha256':sha(S/'contratos/PI05_C2C_USO_PRINCIPAL_01.json')if(S/'contratos/PI05_C2C_USO_PRINCIPAL_01.json').exists()else None,'document':{'schema':'DEE.PI05.C2C.exact_adopted_permission.v1','life_id':TARGET,'profile':'fisica_directa','requires_environment30':True,'allowed_modes':['eci01-pi04-c2c-oportunidad','eci01-pi04-c2c-estado'],'preparation_or_readmission_forbidden':True,'source_physical_parent':genealogy['physical_parent'],'scope':'Prepared P0 support plus acquired C2Cstate, not autonomous sequence orguard choice'}},'affected_contract_updates':[],'decision_id':'PI05_ADOPCION_OPERATIVA_01','source_code_dependency_closure':closure,'current_gateway_preserved':{'file':'sistema/gestionar.py','sha256':helper.GATEWAY_SHA},'engine_checks_readonly':engine,'recovery_actual_outcomes':{k:None if not v.get('summary')else{'q4':v['summary'].get('early_physical_choice'),'q6':v['summary'].get('old_q6_choice')}for k,v in rec.items()}}
 return result,genealogy,gb,missing,helper
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--sellar',action='store_true');ap.add_argument('--process-proof',type=Path,default=P/'control/PROCESOS_CERRADOS_ANTES_INCORPORAR_PI05.json');a=ap.parse_args();d,g,gb,missing,helper=build(a.process_proof)
 print(json.dumps({'mode':'SEAL_REQUESTED'if a.sellar else'READ_ONLY_NO_WRITES','eight_empirical_gates_satisfied':not missing,'missing_gates':missing,'approved_code_deltas':len(d['approved_code_files']),'source':d['source_life_id'],'desired_cut':d['desired_cut'],'target':d['life_id'],'process_proof_exists':a.process_proof.is_file(),'Native_ticks':0},ensure_ascii=False,indent=2),flush=True)
 if not a.sellar:return
 need(not missing,'Empirical gates still pending/adverse; no positive decision written');need(a.process_proof.is_file(),'Fresh writer proof required');helper.check_selector_CAS(d);helper.no_writers(d);helper.approved_code(d);helper.check_json_plans(d);helper.stable_pair(d)
 gp=Path(d['genealogy_proof']['path']);out=P/'control/DECISION_FINAL_PI05.json';need(not gp.exists()and not out.exists(),'Existing sealed decision/genealogy preserved; never overwrite')
 with gp.open('xb')as f:f.write(gb)
 try:helper.source_state(d,helper.passive_parser())
 except Exception:raise # Preserve attempted genealogy; never delete evidence.
 with out.open('x',encoding='utf8')as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
 helper.load_decision(out);print(json.dumps({'decision':info(out),'genealogy':info(gp),'approved_for_adoption':True,'Native_ticks':0,'product_modified':False},ensure_ascii=False))
if __name__=='__main__':main()
