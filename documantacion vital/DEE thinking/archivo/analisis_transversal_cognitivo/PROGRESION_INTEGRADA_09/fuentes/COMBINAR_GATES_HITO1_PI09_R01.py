"""Pure six-gate combiner. Missing/nonclosed inputs => WAIT, no output file.

Only explicitly supplied CLOSED JSON witnesses are read. No world/card/SQLite,
Native/DEE import, product write, deployment, publication or approval occurs.
"""
from pathlib import Path
import argparse,hashlib,json
P=Path(__file__).resolve().parents[1]
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01'
REPRO='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_REPRO_01'
def require(ok,why):
    if not ok:raise ValueError(why)
def sha(file):return hashlib.sha256(Path(file).read_bytes()).hexdigest()
def load(file):
    file=Path(file).resolve(strict=True);require(file.is_file()and not file.is_symlink(),'Literal JSON input only');return json.loads(file.read_text('utf-8-sig')),{'path':str(file),'sha256':sha(file)}
def physical4(value):return {k:value[k]for k in('N','tick','RAW_sha256','clocks_sha256')}
def gate(satisfied,criterion,result,evidence):return {'satisfied':bool(satisfied),'criterion':criterion,'result':result,'evidence':evidence}
def combine(science,panels,source0,rp,rpreg,refs):
    require(science.get('schema')=='DEE.PI09.consultation.compact_actual_criteria_evaluation.R01'and science.get('Native_executed_by_evaluation')is False and science.get('approval')is False,'Actual four-arm C2 evaluation required; no approval inferred')
    require(panels.get('schema')=='DEE.PI09.closed_panels_and_prospective_P0_gate.validation.R01'and panels.get('closed')is True and panels.get('error')is None and panels.get('Native_executed')is False,'Closed raw-checked I4 panel validation required')
    require(source0.get('schema')=='DEE.PI09.mature_source.public_reopening0.R01'and source0.get('closed')is True and source0.get('owner_closed')is True,'Actual closed mature-source public reopening required')
    require(source0.get('life_id')==LIFE and source0.get('initial_tick')==source0.get('final_tick')==903603 and source0.get('new_ticks')==source0.get('new_Native_inputs')==0,'Same mature identity/boundary, no extra Native input or advance')
    require(rp.get('schema')=='DEE.PI09.RP.canonical12.full_passive_comparison.R01'and rp.get('overall')is True and rp.get('physical_equal')is True and rp.get('causal_prefix_equal')is True and rp.get('unexpected_metadata_changes')==[]and rp.get('recipe_actual_criteria_met')is True,'Strict actual RP comparison required; never relax an unsuccessful comparator')
    journals=rp.get('PI09_journals',{});require(journals.get('normalized_equal')is True and journals.get('other_different_paths')==[],'Only explicitly permitted identity/own-journal transport normalization')
    require(rpreg.get('schema')=='DEE.PI09.RP.actual_cold12.additive_registration.R01'and rpreg.get('registered')is True and rpreg.get('life_id')==REPRO and rpreg.get('actual_prior_native_replay_ticks')==18768 and rpreg.get('new_native_ticks_in_registration')==0 and rpreg.get('Native_executed_by_registration')is False and rpreg.get('recipe_and_capsule_literal_unchanged')is True,'Actual registered material replay, not a prepared recipe or documentary recalculation')
    require(rpreg['full_passive_comparison']['sha256']==refs['rp_compare']['sha256']and rpreg['actual_result']['sha256']==rp['replay_result']['sha256'],'Registration must refer to this strict comparator and material run')
    fieldnames={'physical','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase'}
    require(set(source0.get('Native_field_equalities',{}))==fieldnames and all(source0['Native_field_equalities'].values()),'All six current Native/causal/interface/receipt/agenda/phase fields must remain equal')
    properties=('operational_state_valid','pending_reconciled','physical_unchanged','causal_prefix_equal','stock_unchanged','all_scientific_metadata_literal_unchanged','source_code_unchanged','current_principal_unchanged','same_life_and_world_no_clone')
    source_good=all(source0.get(k)is True for k in properties)
    expected_stock={'PI09':{'ordinal':12,'total':18,'remaining':6},'C2C':{'ordinal':31,'total':32,'remaining':1},'FI':{'ordinal':4,'total':8,'remaining':4}}
    require(source0['stock_before']==source0['stock_after']==expected_stock,'Actual finite resources must remain, never reset')
    current=source0['source_record_after'];current_physical=physical4(current['physical']);require(current_physical==rp['source_physical']==rp['replay_physical'],'Reopened current source must retain actual replayed Native physics')
    require(current['life_id']==LIFE and current['snapshot_sha256']==source0['snapshot_sha256']==source0['after_snapshot']['sha256'],'Actual encoded current source pointer must agree')
    g=science['gates'];scientific=all(g[k].get('result')is True for k in('four_closed_arms','candidate_floor','bounded_Native_access','causal_content_witness'))
    legacy=panels['legacy'];guard=panels['guard'];require(legacy.get('closed')and guard.get('closed'),'Both actual panel continuations must close')
    legacy_core=legacy['words_context_correct']==7 and legacy['signed_FI_correct']==3
    substitute_core=guard['words_context_correct']==7 and guard['signed_FI_correct']==3 and panels['P0_public_access_gate']['satisfied']is True
    conserved=legacy_core or substitute_core;chosen=legacy if legacy_core else guard
    numeric_loss=chosen['published_correct']<12
    accepted_loss=numeric_loss and scientific and chosen['arithmetic_causal_chain']['second_input_is_first_actual']is True
    require(not numeric_loss or accepted_loss,'Partial numeric loss is acceptable only under the actual prespecified information gain and actual-result transport')
    native=[r for r in science['material_comparison_table']if r['arm']=='native_real'and r['life_id']==LIFE];require(len(native)==1,'Unique actual mature Native candidate')
    phases=science['closures']['native_real'];require(phases['final_tick']==903603,'New-feature final phase must end at actual current source cut')
    trace=native[0]['bank_and_phase_trace'];require(len(trace)==12 and trace[-1]['ordinal']==11,'Full actual last new-flow opportunity required')
    # EP11 is a valid Native NoQuery case, not a requirement to force another
    # material question. The complete actual flow is already preserved at903603.
    last_valid=trace[-1]['first_native_choice']is not None and native[0]['FI_q6_choices'][-1]==1 and trace[-1]['actual_failed']is False
    last_good=last_valid and source_good and source0['stock_after']['PI09']['ordinal']==12
    gates={
      'functional_gain':gate(scientific,'At least8/12 useful and4/6 reserved; applied conditional Native access with both direction codes, valid distinct actions and causal useful information contribution',{'source_tick':903603,'candidate_floor':g['candidate_floor'],'bounded_access':g['bounded_Native_access'],'content':g['causal_content_witness'],'query_specific_learning_not_isolated':True},[refs['science']]),
      'conservation':gate(conserved,'Seven learned-word/context and three signed FI witnesses under an existing or prospectively validated substitute access; disclosed accepted partial numeric loss only',{'access':'existing_literal'if legacy_core else'prospectively_validated_P0_substitute','legacy_published':legacy['published_correct'],'legacy_denominator':12,'chosen_word_context':chosen['words_context_correct'],'chosen_signed_FI':chosen['signed_FI_correct'],'partial_numeric_loss':numeric_loss,'partial_loss_accepted_by_fixed_rule':accepted_loss,'arithmetic_chain':chosen['arithmetic_causal_chain'],'optional_P0_access_gate':panels['P0_public_access_gate'],'not_newly_learned_P0':True},[refs['panels'],refs['science']]),
      'causal_controls':gate(g['four_closed_arms']['result']is True and g['causal_content_witness']['result']is True,'Four material12-op histories; strict first-content contrast and declared input/time/return differences, no offline utility',{'first_content':science['first_content_disagreement'],'content_history':science['fixed_content_history_contrast'],'same_initial_physical_states':science['initial_physical_states_equal'],'query_credit':'Not isolated; one shared bank, only second trace has established return'},[refs['science']]),
      'source_reopening':gate(source_good,'Same identity public STATE/save/close at zero advance; Native causal fields, stock and scientific metadata preserved',{'life_id':LIFE,'tick':903603,'snapshot_sha256':source0['snapshot_sha256'],'Native_fields':source0['Native_field_equalities'],'stocks':source0['stock_after'],'public_state_rows':source0['public_STATE_rows'],'material_public_use_executed':False},[refs['source0']]),
      'new_function_at_final_cut':gate(last_good,'Actual EP11 completes the new two-stage Native flow at the final candidate cut; current Source0 is causally/physically equivalent. No forced postcommit material test',{'last_evaluated_ordinal':11,'last_first_Native_choice':trace[-1]['first_native_choice'],'last_FI_q6':native[0]['FI_q6_choices'][-1],'Native_combined_useful':native[0]['useful'],'reserved_useful':native[0]['reserved_useful'],'current_tick':903603,'current_snapshot_sha256':source0['snapshot_sha256'],'new_material_ticks_in_reopening':0,'last_NoQuery_is_valid_material_zero_not_NULL':trace[-1]['first_native_choice']==0},[refs['science'],refs['source0']]),
      'decisive_recipe_replay':gate(True,'Actual material cold12 through RP from complete C884835, strict Native/causal comparison and additive verification registration',{'recipe':rpreg['recipe'],'life_id':REPRO,'material_replay_ticks':18768,'strict_overall':True,'full_Native_equal':True,'only_documented_transport_metadata_differences':rp['metadata_changes_all_listed'],'registered':True,'documentary_registration_ticks':0,'not_independent_replication':True},[refs['rp_compare'],refs['rp_registration']])
    }
    return {'schema':'DEE.PI09.consultation.combined_actual_gates.R01','Native_executed':False,'DEE_imported':False,'life_id':LIFE,'N':67,'T':903603,'current_snapshot_sha256':source0['snapshot_sha256'],'current_source_record':current,'gates':gates,'all_fixed_evidence_gates_met':all(v['satisfied']for v in gates.values()),'approval':False,'adoption_not_performed':True,'actual_closed_arms':{role:science['source_evidence'][role]for role in('native_real','always_real','never','always_desacoplado')},'actual_panel_validation':refs['panels'],'actual_source_reopening':refs['source0'],'actual_material_replay':refs['rp_compare'],'registered_replay':refs['rp_registration'],'scope':'Bounded Native-controlled registered-information access in one intact C/B continuation. Prepared two-stage sequence and transducer; no isolated learned value of asking or general agency.','gains':'Native12/12 with8material questions; Always12/12 with12; Never3/12 and desynchronized-content6/12. First content contrast changes Native action and utility under matched prior inputs/banks.','losses':{'chosen_conservation_partial_numeric_loss':numeric_loss,'numeric_chain':chosen['arithmetic_causal_chain'],'domain_claim_only':True},'uncertainties':['First-stage query credit is not isolated from shared-bank second-stage return.','The technical sample register is not acquired Native memory or a fresh late observation.','Nominal3/11waits were absorbed; do not claim independent transfer across391/782phases.','D remains prepared/conditional, not an achieved or adopted result.'],'assistance':'External environment, fixed sensor codec, conditional technical register, host serial ordering, finite supplies and exact transport permissions. No host arithmetic answer or bank reset.','regression_coverage':{'actual_closed_panels':True,'source_reopened':True,'new_function_replayed':True,'universal_legacy_or_arithmetic_perfection_claim':False},'evidence':list(refs.values())}
def main(a):
    paths={'science':a.science,'panels':a.paneles,'source0':a.source0,'rp_compare':a.rp_contraste,'rp_registration':a.rp_registro}
    missing=[{'input':k,'path':str(v)}for k,v in paths.items()if not Path(v).is_file()]
    if missing:print(json.dumps({'status':'WAIT','missing_closed_inputs':missing,'output_written':False,'Native_executed':False}));return
    values={};refs={}
    for name,path in paths.items():values[name],refs[name]=load(path)
    result=combine(values['science'],values['panels'],values['source0'],values['rp_compare'],values['rp_registration'],refs)
    out=Path(a.salida).absolute();require(out.parent in((P/'control').resolve(),(P/'fuentes').resolve())and not out.exists(),'Fresh output in PI09/control or fuentes only')
    with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'output':str(out),'sha256':sha(out),'all_fixed_evidence_gates_met':result['all_fixed_evidence_gates_met'],'approval':False,'Native_executed':False}))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--science',type=Path,default=P/'fuentes/EVALUACION_CUATRO_CIERRES_PI09_R01.json');ap.add_argument('--paneles',type=Path,required=True);ap.add_argument('--source0',type=Path,default=P/'control/REAPERTURA_SOURCE_NATIVE_PI09_R01.json');ap.add_argument('--rp-contraste',type=Path,default=P/'control/CONTRASTE_RP_NATIVE12_PI09_R01.json');ap.add_argument('--rp-registro',type=Path,default=P/'control/RP_NATIVE12_REGISTRADA_PI09_R01.json');ap.add_argument('--salida',type=Path,required=True);main(ap.parse_args())
