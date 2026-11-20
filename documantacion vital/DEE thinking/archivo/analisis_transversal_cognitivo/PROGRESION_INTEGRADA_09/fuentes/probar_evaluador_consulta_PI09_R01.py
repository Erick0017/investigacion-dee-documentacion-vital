"""Pure synthetic checks of prospective causal matching; no real PI09 reads."""
from pathlib import Path
import copy,importlib.util,json,sys
H=Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('p9_evaluator_fake',H/'EVALUAR_CRITERIOS_CONSULTA_PI09_R01.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
checks=[]
def check(name,ok):
    if not ok:raise AssertionError(name)
    checks.append(name)
def obs(payload,t):
    return {'raw':str((1<<60)|(payload<<32)|1),'state':1,'semantic':1,'s_reg':payload,'direction':[0,0,0],'clock':str(t),'tick':t,'site':[7,39,50]}
def request(i,t,payload,channel):return {'id':i,'requested_tick':t,'payload':payload,'channel':channel,'receipt':{'id':i,'status':'applied','effective_tick':t}}
def row(i,bit,motor,failed,info):
    q1=100+1564*i;q2=q1+782;base=4*i;a=request(base+1,q1,0,'query1');question=request(base+2,q1+7,0,'question');question.update(site=[33,40,30],direction=[1,0,0]);b=request(base+3,q2,0,'query2');datum=request(base+4,q2+3,bit,'PI07.TC.R01.datum')
    return {'ordinal':i,'before_tick':1564*i,'after_tick':q2+412,'query_control':'always','information_control':info,'requests':[a,question,b,datum],'first_stage':{'query_tick':q1,'question_request':question,'sample_register':{'question_applied_and_signature':True}},'second_stage':{'calendar':{'query_tick':q2},'sensor':{'submitted_state_datum':bit},'requests':[b,datum],'reference_before':[obs(50,q2-16),obs(50,q2-16)],'environment_spec':{'fixture':'same_public_inputs'},'reader':{'choice':motor},'actual_motor':motor,'actual_failed':failed,'returned_failed':failed}}
left=[row(i,1,1,False,'real')for i in range(12)];right=[row(i,0,-1,True,'desynchronized')for i in range(12)]
r=m.first_content_disagreement(left,right);check('first0_local_matched_content_useful',r['ordinal']==0 and r['causal_useful_witness'])
check('whole_history_contrast_material_success',m.content_history_contrast(left,right,r,True)['causal_useful_history_witness'])
bad=copy.deepcopy(right);bad[0]['requests'][0]['payload']=99;r=m.first_content_disagreement(left,bad);check('prior_input_difference_not_local_isolation',not r['same_material_input_prefix_until_second_datum']and not r['causal_useful_witness'])
check('different_prior_inputs_block_history_witness',not m.content_history_contrast(left,bad,r,True)['causal_useful_history_witness'])
bad=copy.deepcopy(right);bad[0]['second_stage']['reference_before'][0]=obs(51,866);r=m.first_content_disagreement(left,bad);check('observed_bank_difference_is_declared',not r['same_observed_banks_before_second_query']and not r['causal_useful_witness'])
same=copy.deepcopy(left)
for x in same:x['information_control']='desynchronized'
r=m.first_content_disagreement(left,same);check('no_bit_difference_is_nonresolutive',r['status']=='NO_DIFFERENT_SUBMITTED_BIT_IN12'and not r['causal_useful_witness'])
mediated=copy.deepcopy(right);mediated[0]['second_stage'].update(reader={'choice':1},actual_motor=1,actual_failed=False,returned_failed=False)
r=m.first_content_disagreement(left,mediated);check('first_different_bit_not_forced_positive',r['ordinal']==0 and not r['causal_useful_witness'])
h=m.content_history_contrast(left,mediated,r,True);check('later_mediated_content_benefit_separate_from_local',h['causal_useful_history_witness']and 0 not in h['actual_real_content_benefit_ordinals']and 1 in h['actual_real_content_benefit_ordinals'])
check('initial_physical_mismatch_blocks_content_claim',not m.content_history_contrast(left,right,m.first_content_disagreement(left,right),False)['causal_useful_history_witness'])
ids=copy.deepcopy(right)
for x in ids:
    for req in x['requests']:req['id']+=1000;req['receipt']['id']+=1000
# Same objects appear in second.requests; deepcopy retained aliases, so nativeIDs
# shift together without changing actual physical arguments or observed banks.
r=m.first_content_disagreement(left,ids);check('Native_ID_difference_exposed_without_hiding_physical_match',r['same_material_input_prefix_until_second_datum']and not r['literal_Native_ids_equal'])
bad=copy.deepcopy(right);bad[2]['second_stage']['environment_spec']={'fixture':'changed_public_input'}
r=m.first_content_disagreement(left,bad);check('different_environment_not_pure_history_content',not m.content_history_contrast(left,bad,r,True)['causal_useful_history_witness'])
check('no_DEE_import',not any(k=='dee_thinking'or k.startswith('dee_thinking.')for k in sys.modules))
proof={'schema':'DEE.PI09.consultation.criteria_evaluator.pure_tests.v1','passed':True,'Native_executed':False,'DEE_imported':False,'fixture_MOCK_ONLY_NOT_NATIVE':True,'no_active_or_actual_PI09_results_read':True,'checks':checks,'count':len(checks),'evaluator_sha256':m.sha((H/'EVALUAR_CRITERIOS_CONSULTA_PI09_R01.py').read_bytes())}
out=H/'PRUEBAS_EVALUADOR_CONSULTA_PI09_R02.json'
with out.open('x',encoding='utf8')as f:json.dump(proof,f,indent=2);f.write('\n')
print(json.dumps({'passed':True,'checks':len(checks),'sha256':m.sha(out.read_bytes())}))
