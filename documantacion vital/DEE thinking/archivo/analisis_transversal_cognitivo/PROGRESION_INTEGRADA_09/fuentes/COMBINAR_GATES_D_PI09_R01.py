"""Pure actual six-gate D combiner; missing/unclosed witnesses => WAIT.

Explicit closed JSON/primaries only. No Native/DEE/Owner/SQLite/world access,
deployment or approval. Representative RP6 is distinguished from the mature
source's additional panel and last real use. Existing readers remain frozen.
"""
from pathlib import Path
import argparse,ast,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def checked(item):
    file=Path(item['path']).resolve(strict=True);need(file.is_relative_to(P.resolve())and not file.is_symlink()and sha(file)==item['sha256'],'Exact current closed local reference/hash required');return read(file)
def imported(name,file):
    s=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def panel_actual(proof,proofref):
    need(proof.get('closed')is True and proof.get('error')is None and proof.get('status')=='CLOSED_FINITE_PHASE'and proof['life_id']==LIFE,'Actual complete same-life conservation panel required')
    source=H/'validar_paneles_hito1_PI09_R01.py';need(sha(source)=='e1686fbe4f8572d45613a92e5cf1a9e59687e28cb094c3b78af6484965e02e09','Frozen pure panel validator changed')
    m=imported('D_same_frozen_retention_readers',source);text=source.read_text('utf-8-sig');node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name=='phase');fn=ast.get_source_segment(text,node)
    edits=[("proof.get('schema')=='DEE.PI09.actual.finite_owner_plan.R02'","proof.get('schema')=='DEE.PI09.actual.finite_owner_plan.R03'"),("len(plan['steps'])==18","len(plan['steps'])==13"),("literal['modo']=='eci01-pi07-fi-regulada'","literal['modo']in('eci01-pi07-fi-regulada','eci01-pi09-fi-lote-consultar')"),("'fresh_denominator':5","'fresh_denominator':0")]
    for old,new in edits:need(fn.count(old)==1,'Exact technical panel adapter anchor changed');fn=fn.replace(old,new)
    fn=fn.replace('903603',"plan['initial_tick']");exec(compile(fn,str(source)+':D_dynamic_start_and_FI8_only','exec'),m.__dict__)
    planfile=Path(proof['plan']).resolve(strict=True);need(planfile.is_relative_to(H.resolve())and sha(planfile)==proof['plan_sha256'],'Original fixed post-D panel plan required');plan=read(planfile)
    need(plan['initial_tick']==917679 and len(plan['steps'])==13 and[step['label']for step in plan['steps']][1:]==['luma','nara','clasifica','suma','alfa','FIplus','FIminus','FIzero','number13','number8','alfa_after','luma_after'],'Twelve retained-domain tests after actual D6; no substitute favourable panel')
    numeric,numeric_ref=m.frozen_numeric();need(numeric_ref['sha256']==read(P/'control/PANELES_HITO1_VERIFICADOS_PI09_R01.json')['numeric_reader_source']['sha256'],'Same frozen numeric RAW decoder as hito1')
    result=m.phase(Path(proofref['path']),planfile,numeric,None)
    return {**result,'criteria_met':result['published_correct']==12,'numeric_reader_source':numeric_ref,'technical_adapter_scope':'Only dynamic initial tick,13records and same FI reader through explicit lot8. No scientific decoder/expected result changed.'}
def last_actual(proof,source0):
    need(proof.get('schema')in('DEE.PI09.D.actual.finite_owner_phase.R02','DEE.PI09.D.actual.finite_owner_phase.R03')and proof.get('closed')is True and proof.get('error')is None and proof['life_id']==LIFE and proof['arm']=='real','Actual coherent post-panel D real use required')
    planfile=Path(proof['plan']).resolve(strict=True);need(planfile.is_relative_to(H.resolve())and sha(planfile)==proof['plan_sha256'],'Actual fixed last-use plan required');plan=read(planfile)
    selected=[]
    for rec in proof['records']:
        if rec['literal'].get('modo')!='eci01-pi09-d-episodio':continue
        file=Path(rec['primary']).resolve(strict=True);need(file.parent==(P/'ensayos').resolve()and sha(file)==rec['sha256'],'Actual last-function primary hash differs');primary=read(file);need(primary['status']=='completed','Completed last-function primary required')
        raw=primary['result'];raw=json.loads(raw)if isinstance(raw,str)else raw;rr=raw.get('result',raw)['rows'];need(len(rr)==1,'One actual D row');row=rr[0]
        expected_step=plan['steps'][rec['index']];need(expected_step['literal']==rec['literal']and row['life_id']==LIFE and row['version']=='DEE.PI09.persistent_environment.D.R02'and row['ordinal']==expected_step['ordinal'],'Explicit material identity/version/ordinal from fixed plan; never STATE-derived')
        selected.append((rec,row))
    need(selected,'An actual new D opportunity is required; zero reopening alone is insufficient');rec,row=selected[-1];i=row['ordinal'];need(6<=i<=10 and proof['final_tick']==row['after_tick']==source0['initial_tick']==source0['final_tick'],'Actual last useful D cut must equal mature Source0; leave at least one of12 opportunities')
    module=imported('D_last_actual_pure_RAW',H/'RECALCULAR_D_PI09_R03.py');shared,old,m,adapter=module.parsers();old.VERSION=row['version'];choice1=old.reader(row['first_stage']['reader'],m);need(choice1 is not None,'NULL first selection is not valid NoQuery')
    first=row['first_stage'];reg=first['sample_register'];sample=m.observation(reg['actual_preview_observation']);motor1=shared.motor(choice1);need(first['native_motor']==first['actual_query_motor']==motor1,'Actual first Native motor required')
    question=first['question_request'];question_status=m.request_status(question);observed=m.observation(first['question_observation']);signature=observed['state']>0 and observed['semantic']==1 and observed['direction']==[1,0,0];released=question_status=='applied'and signature
    need((question is not None)==(motor1==1)and reg['question_applied_and_signature']is released,'Actual material asking/release differs');bit=shared.extra(m,reg['actual_preview_observation'])if released else 0;need(bit is not None and bit==reg['released_bit']==row['extra_bit_entered_second_TC'],'Actual gated extra bit or declared NoQuery0 required')
    s=row['second_stage'];reader2=old.reader(s['reader'],m);need(reader2 is not None and s['native_motor']==s['actual_motor']==shared.motor(reader2)and s['operator_forced_action']is None,'Native second selection, no host reference action')
    early=m.early_choice(s['FI']['legacy_result']['early_observation']);late=m.late_FI_choice(s['FI']['legacy_result']['original_result']['native_trial']['reader']);need((early,late)==(s['FI']['early_physical_choice'],s['FI']['old_q6_choice']),'Frozen actual FI readers differ')
    msg=s['message'];ob=m.observation(msg['observation']);required=read(H/'PROTOCOLO_PI09_D_R02.json')['schedule'][i]['message_payload'];valid=ob['state']>0 and ob['semantic']==1 and ob['direction']==[1,0,0];delivered=m.request_status(msg['request'])=='applied'and valid and ob['s_reg']==required
    need(msg['delivered_exact']is delivered and msg['actual_payload']==(ob['s_reg']if valid else None),'Actual Native message predicate differs');artifact=msg['artifact']
    if delivered:need(artifact is not None and artifact['bytes']==64 and artifact['sha256']==hashlib.sha256(int(ob['s_reg']).to_bytes(8,'little')*8).hexdigest(),'Artifact pointer must encode the observed Native value, never a desired answer')
    failed=late!=1 or not delivered;need(row['actual_failed']is s['actual_failed']is failed and row['returned_failed']is s['returned_failed']is failed,'Actual real consequence differs from the generic return')
    direct,counts,aliases=old.summary(row['requests'],row['Native_inputs'],m)
    return {'ordinal':i,'final_tick':row['after_tick'],'actual_useful':not failed,'first_Native_choice':choice1,'first_actual_query_motor':motor1,'second_Native_choice':reader2,'second_actual_motor':s['actual_motor'],'FI_q4':early,'FI_q6':late,'message_delivered':delivered,'actual_failed':failed,'Native_inputs':{'requested':len(direct),'status_counts':dict(counts)},'primary':{'path':rec['primary'],'sha256':rec['sha256']},'full_artifact_file_integrity_scope':'Existing actual Source0 Owner operational_dependencies plus separate final portable bundle; this combiner reads actual RAW/value/hash, not a live home','not_a_material_query_requirement_when_valid_NoQuery':True}
def gate(ok,criterion,result,evidence):return {'satisfied':bool(ok),'criterion':criterion,'result':result,'evidence':evidence}
def combine(science,refs):
    needed=['first_milestone_adoption','D_actual_closed_arms','D_conservation_proof','D_source_reopening_function_proof','D_source_zero_reopening_proof','D_reproduction_result','D_reproduction_comparison','D_generic_family_registration']
    need(all(k in refs for k in needed),'I4 actual-reference schema required');adopt=checked(refs['first_milestone_adoption']);need(adopt['phase']=='COMMITTED','Actual hito1 first milestone')
    arms={k:checked(refs['D_actual_closed_arms'][k])for k in('real','none','yoked')}
    for role,value in arms.items():need(value.get('closed')is True and value.get('error')is None and value.get('arm')==role and value['final_tick']==917679 and value['initial_tick']==907543,'Three actual fixed D6 controls, never a future continuation substituted as evaluation')
    need(science.get('schema')=='DEE.PI09.D.fixed_actual_comparison.R03'and science.get('all_three_evaluation_arms_closed6')is True and science.get('approval')is False,'Actual scientific comparison, not approval')
    recalculated=checked(science['source_recalculation']);need(recalculated.get('integrity_passed')is True and recalculated.get('Native_executed')is False,'Actual raw-verified scientific source required')
    for role in arms:need(any(c['arm']==role and c['sha256']==refs['D_actual_closed_arms'][role]['sha256']for c in recalculated['closures']),'Scientific source must contain these exact three actual closed histories')
    bound=science['bounded_readaptation_evidence'];gain=bound['all_fixed_descriptive_conditions_present']is True
    rawpanel=checked(refs['D_conservation_proof']);panel=panel_actual(rawpanel,refs['D_conservation_proof']);source0=checked(refs['D_source_zero_reopening_proof'])
    need(source0.get('schema')=='DEE.PI09.D.mature_source.public_reopening0.R01'and source0.get('closed')is True and source0.get('owner_closed')is True and source0.get('life_id')==LIFE and source0.get('new_ticks')==source0.get('new_Native_inputs')==0,'Actual mature same-identity source reopening0')
    flags=('physical_unchanged','stock_unchanged','causal_prefix_equal','all_scientific_metadata_literal_unchanged','source_code_unchanged','current_principal_unchanged','operational_state_valid','pending_reconciled')
    keys={'physical','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase'};need(set(source0['Native_field_equalities'])==keys,'Six declared Native/causal checks required');source_good=all(source0.get(k)is True for k in flags)and all(v is True for v in source0['Native_field_equalities'].values())
    need(source0['stock_before']==source0['stock_after']and source0['stock_after']['R02']=={'ordinal':12,'total':18,'remaining':6},'OldR02history/stock must remain literal12/18')
    finalproof=checked(refs['D_source_reopening_function_proof']);last=last_actual(finalproof,source0);need(finalproof['initial_tick']==rawpanel['final_tick']and source0['stock_after']['D']['ordinal']==last['ordinal']+1 and source0['stock_after']['D']['total']==12 and source0['stock_after']['D']['remaining']>=1,'Same panel successor and finite dynamic stock, no reset')
    rp=checked(refs['D_reproduction_result']);comparison=checked(refs['D_reproduction_comparison']);registration=checked(refs['D_generic_family_registration'])
    reproduced=rp.get('status')=='COMPLETED'and rp.get('owner_closed_coherently')is True and rp.get('criteria_met')is True and rp.get('last_tick')==917679 and comparison.get('overall')is True and comparison.get('physical_equal')is True and comparison.get('causal_prefix_equal')is True and comparison.get('unexpected_metadata_changes')==[]and comparison.get('family_binding',{}).get('three_administrative_bindings_verified')is True
    registered=registration.get('schema')=='DEE.PI09.D.RP.family6.additive_registration.R01'and registration.get('registered')is True and registration.get('recipe_and_capsule_literal_unchanged')is True and registration.get('actual_prior_native_replay_ticks')==10136 and registration.get('new_native_ticks_in_registration')==0 and registration.get('Native_executed_by_registration')is False and registration['actual_result']['sha256']==refs['D_reproduction_result']['sha256']and registration['full_passive_comparison']['sha256']==refs['D_reproduction_comparison']['sha256']
    E=lambda *names:[refs[n]for n in names]
    scientific_evidence=[refs['D_actual_closed_arms'][k]for k in('real','none','yoked')]
    gates={'functional_gain':gate(gain,'Fixed D6 Real improves useful function over actual NoFail/Yoke with Native chain change after own failed experience and later useful cases',{'comparison':science['actual_counts'],'readaptation':bound,'query_specific_credit_not_isolated':True},scientific_evidence),'conservation':gate(panel['criteria_met'],'Same-life fixed previous12 retained-domain witnesses, RAW/receipt checked',panel,E('D_conservation_proof')),'causal_controls':gate(gain and all(p['same_q1_q2']and p['same_age']for p in science['actual_pairwise_differences'])and sum(science['actual_counts']['real']['returned_failed'])==sum(science['actual_counts']['yoked']['returned_failed']),'Same source and actual paired ages/calendars; prespecified valence-dose matched Yoke, endogenous total input differences reported',{'pairs':science['actual_pairwise_differences'],'same_negative_signal_count_real_yoked':True,'fixed_permutation':[2,0,4,1,5,3],'total_Native_input_isodose_claim':False,'guard_is_external_P0':True},scientific_evidence),'source_reopening':gate(source_good,'Actual public STATE/save/close0 preserves same-life Native causal fields, code, parent and finite stock',{'tick':source0['final_tick'],'snapshot_sha256':source0['snapshot_sha256'],'Native_fields':source0['Native_field_equalities'],'stocks':source0['stock_after']},E('D_source_zero_reopening_proof')),'new_function_at_final_cut':gate(last['actual_useful']and source_good,'Actual new D use after reopening/panel, with valid Native decisions and Native function at the exact mature cut',last,E('D_source_reopening_function_proof','D_source_zero_reopening_proof')),'decisive_recipe_replay':gate(reproduced and registered and refs.get('D_new_frontdoor_CLI_replay_verified')is True,'Actual generic-family RP D6 with strict full Native comparison and additive registration; representative acquisition, not replay of later panel/use',{'actual_replay_ticks':10136,'episodes':6,'requests':8,'useful_acquisition_cases':5,'first_failure_and_two_conflicts_preserved':True,'strict_overall':comparison.get('overall'),'registered':registration.get('registered'),'later_mature_history_not_claimed_replayed':True},E('D_reproduction_result','D_reproduction_comparison','D_generic_family_registration'))}
    return {'schema':'DEE.PI09.D.combined_actual_gates.R01','life_id':LIFE,'N':67,'T':source0['final_tick'],'current_snapshot_sha256':source0['snapshot_sha256'],'Native_executed':False,'DEE_imported':False,'approval':False,'all_fixed_evidence_gates_met':all(g['satisfied']for g in gates.values()),'gates':gates,**{k:v for k,v in refs.items()if k.startswith('D_')or k in('scope','gains','losses','uncertainties','assistance','regression_coverage','catalog_entry')},'scope':'Bounded D shared-bank chain readaptation under one fixed prepared environmental change; no isolated first-query credit, learned sequence or general agency.','actual_main_D_adoption_performed':False,'actual_conservation_validation':panel,'actual_last_function':last,'actual_source0':refs['D_source_zero_reopening_proof']}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--evaluacion-cientifica',type=Path,default=P/'control/EVALUACION_D_TRES_CONTROLES_PI09_R03.json');ap.add_argument('--refs',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args()
    if not a.refs.is_file()or not a.evaluacion_cientifica.is_file():print(json.dumps({'status':'WAIT','output_written':False,'Native_executed':False}));raise SystemExit(0)
    refs=read(a.refs);missing=[]
    def scan(x):
        if isinstance(x,dict):
            if 'path'in x and'sha256'in x and not Path(x['path']).is_file():missing.append(x['path'])
            for v in x.values():scan(v)
        elif isinstance(x,list):
            for v in x:scan(v)
    scan(refs)
    if missing:print(json.dumps({'status':'WAIT','missing_closed_inputs':missing,'output_written':False,'Native_executed':False}));raise SystemExit(0)
    result=combine(read(a.evaluacion_cientifica),refs);result['scientific_evaluation']={'path':str(a.evaluacion_cientifica.resolve()),'sha256':sha(a.evaluacion_cientifica)};out=a.salida.absolute();need(out.parent==(P/'control').resolve()and not out.exists(),'Fresh combined actual result only')
    with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'file':str(out),'sha256':sha(out),'all_fixed_evidence_gates_met':result['all_fixed_evidence_gates_met'],'gates':{k:v['satisfied']for k,v in result['gates'].items()},'approval':False,'Native_executed':False}))
