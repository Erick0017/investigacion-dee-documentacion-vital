from pathlib import Path
import json,math
import recalcular as rc
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=LAB.parent/'EVIDENCIA_ESENCIAL'if(LAB.parent/'EVIDENCIA_ESENCIAL').exists()else ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
def rows(name):return rc.extrows(rc.read(EV/name))
sources=['COST_NATIVE_73_PREFIX3.json','COST_NATIVE_73_CONTINUATION.json','INTEGRATED_COST_SOCIAL_132_FIRST3.json','INTEGRATED_COST_SOCIAL_132_CONTINUE9.json','INTERLEAVE_NATIVE_EXTERNAL_141.json','STRESS_MATCHED_144.json','STRESS_MATCHED_144_WITHDRAW6.json','SYSTEM_CONTINUATION_1_161.json','SYSTEM_CONTINUATION_3_161.json']+['LONG_SYSTEM_CONTINUATION_'+str(i)+'_162.json'for i in range(1,9)]+['FINAL_OPERATIONAL_2_165.json']
line=[dict(x,source=f)for f in sources for x in rows(f)]
assert len(line)==193 and[x['index']for x in line]==list(range(193))
extra=['OPERATIONAL_RECOVERY_AGED_2_170.json','OPERATIONAL_RECOVERY_AGED_4_170.json','OPERATIONAL_RECOVERY_AGED_5_170.json','OPERATIONAL_RECOVERY_AGED_7_170.json']
continued=line+[dict(x,source=f)for f in extra for x in rows(f)]
assert len(continued)==202
refs=rc.read(EV/'EXTERNAL_REFERENCES_93.json')['trials'];more=rc.read(EV/'EXTERNAL_REFERENCES_EXTEND193_168.json')['trials'];reference=[]
for first,last in zip(refs,more):
    assert(first['seed'],first['mode'])==(last['seed'],last['mode']);rr=first['rows']+last['rows'];assert len(rr)==193
    reference.append({'seed':first['seed'],'mode':first['mode'],'steps':193,'reward_sum':math.fsum(r['response']['reward']for r in rr),'DEE_life':None})
matched={
 'no_noise':['STRESS_MATCHED_144.json','STRESS_MATCHED_144_WITHDRAW6.json'],
 'nominal':['STRESS_NOMINAL_MAIN_145.json','STRESS_NOMINAL_MAIN_145_WITHDRAW6.json','STRESS_NOMINAL_MAIN_145_WITHDRAW_REMAINING5.json','TRUE_WITHDRAWAL_NOMINAL_173.json'],
 'severe':['STRESS_SEVERE_146.json','STRESS_SEVERE_146_WITHDRAW6.json','STRESS_SEVERE_146_WITHDRAW_REMAINING5.json','TRUE_WITHDRAWAL_SEVERE_173.json']}
stress={}
for label,files in matched.items():
    rr=[x for f in files for x in rows(f)];assert len(rr)==18 and len(set(x['tick']for x in rr))==18;clean=[x for x in rr if x['tick']>=7105]
    stress[label]={'sources':files,'all18':rc.nums(rr),'clean6':rc.nums(clean),'interpretation':'Accepted output code, not automatically recovered magnitude function. See severe175 content-sensitivity controls.'}
old=[]
for name in('INITIAL_PANEL_05.json','MAIN_OLD_FUNCTIONS_INTERLEAVED_41.json','SYSTEM_CONTINUATION_2_161.json','FINAL_OPERATIONAL_1_165.json','OPERATIONAL_RECOVERY_AGED_6_170.json'):
    old.append(rc.metric(rc.read(EV/name),name))
recovery={}
for sign in('PLUS','MINUS'):
    for mode in('RECOVER','SHAM','NONE'):
        name='GENERIC_RECOVERY_R2_'+sign+'_'+mode+'_167.json';r=rc.read(EV/name)['result'];post=r['external']['rows'];recovery[sign+'_'+mode]={'source':name,'post4':rc.nums(post)}
noBfiles=['NO_PARTNER_LONG_NATIVE6_164.json','NO_PARTNER_LONG_NO_NOISE12_164.json','NO_PARTNER_LONG_NO_NOISE6_164.json','NO_PARTNER_LONG_BEFORE_PANEL2_164.json','NO_PARTNER_LONG_AFTER_PANEL1_164.json']+['NO_PARTNER_LONG_LONG'+str(i)+'_164.json'for i in range(1,9)]
noB=[x for f in noBfiles for x in rows(f)]
out={'scope':'Auditor summaries, not information available to E1 and not a global capability score','primary_continuable_lineage':{'sources':sources,'motor_steps':193,'simulated_seconds':'9.65','summary':rc.nums(line),'episode_seed':81017,'DEE_end_tick':16485},'recovered_lineage':{'additional_sources':extra,'total_motor_steps_across_two_explicit_episodes':202,'simulated_seconds_total':'10.10','second_episode_steps':3,'second_episode_seed':81031,'DEE_end_tick':17155,'summary':rc.nums(continued)},'same_initial_external_references':reference,'stress_comparable_endpoints':stress,'old_function_panels':old,'generic_recovery_post_opportunities':recovery,'long_no_current_partner_control':{'sources':noBfiles,'post_source_steps':len(noB),'social_qualified':sum(any(r.get('qualified')for r in x['social_reads'])for x in noB),'end_tick':16284,'scope':'Same curriculum/horizon after no-current-B branch at5698; preceding12step no-B condition in134 is retained separately. Not an independent learner.'},'replica_limit':'All native branches share one inherited E1 prefix. Two external seeds are not independent native biographies. No p-value or general stability claim.'}
(EV/'LECTURA_CIENTIFICA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8');print(json.dumps({k:out[k]for k in('same_initial_external_references','long_no_current_partner_control')},ensure_ascii=False));print(json.dumps({'selected_steps':len(line),'recovered_steps':len(continued),'selected_reward':out['primary_continuable_lineage']['summary']['reward_sum'],'selected_nonzero_actions':out['primary_continuable_lineage']['summary']['nonzero_executed_actions'],'selected_social_uses':out['primary_continuable_lineage']['summary']['received_relation_used_at_motor'],'clean_stress':{k:v['clean6']['qualified_native_actuator_readings']for k,v in stress.items()},'panels':[{k:m.get(k)for k in('file','old_social_forms_with_response','old_social_forms_with_residual_trace_not_automatically_functional')}for m in old]}))
