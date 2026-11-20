"""Recalculate fixed observations. Never supplies outcomes to participants."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'resultados/regulacion';rev=ROOT/'revision';rev.mkdir(exist_ok=True)
rows=[]
for folder in sorted(source.iterdir()):
 p=folder/'RESULT.json'
 if not p.exists():continue
 r=json.loads(p.read_text(encoding='utf-8'));c=json.loads((folder/'CONFIG.json').read_text(encoding='utf-8'))
 f=json.loads((folder/'OBSERVACIONES.json').read_text(encoding='utf-8'))
 policies=next(q['panel'] for q in f if q['tick']==9)
 values=[v['s_reg'] for k,v in policies.items() if k.startswith('policy.')]
 rows.append({'case_id':r['case_id'],'modality':'INDEPENDENT_INITIAL_PREPARATION',
   'medium':c['geometry']['medium'],'mode':c['geometry']['mode'],'N':c['geometry']['N'],
   'context_auditor_only':c['evaluation_context_not_given_to_participant'],
   'requested':r['requested_deliveries'],'other':r['other_deliveries'],
   'policy_max_scalar_load':max(values),'policy_sum_scalar_load':sum(values),
   'policy_directional_records':{k:v for k,v in policies.items() if k.startswith('policy.')},
   'horizon_ticks':18,'data':str(p.relative_to(ROOT)).replace('\\','/'),
   'causal_frames':str((folder/'OBSERVACIONES.json').relative_to(ROOT)).replace('\\','/')+'#/tick=4,5,8,9,11,12,15'})
by={r['case_id']:r for r in rows}
rescue=source/'REG_V2_DIAGNOSTIC_ACTUATOR_R1/OBSERVACIONES.json'
diagnostics=json.loads(rescue.read_text(encoding='utf-8')) if rescue.exists() else []
report={'schema':'CPC8.regulation.analysis.v1','data':rows,
 'formulas':{'delivered':'count of delivery ports at exact tick15 with state>0, semantic!=5, s_reg=3 and direction=(1,0,0); requested class only',
 'opportunity_cost':'exact useful packets delivered in the other class while requested class has0; no penalty is fed to controller',
 'policy_scalar':'max/sum s_reg over the two predeclared policy sites atT9, not a search over world'},
 'bounded_contrast':{'intact_matching':[by[k]['requested'] for k in('REG_V2_P21','REG_V2_H21')],
   'return_cut':[by[k]['requested'] for k in('REG_V2_D21','REG_V2_D22')],
   'opposite_context':[by[k]['requested'] for k in('REG_V2_X21','REG_V2_X22')],
   'reserved_newN':[by[k]['requested'] for k in('REG_V2_R21','REG_V2_R22')],
   'denominators':'Two declared directions per named contrast, one preparation per direction; deterministic technical repeats are not extra independent evidence.'},
 'diagnostic_rescues':[{'parent':r['parent'],'intervention':r['intervention'],'delivery':r['delivery'],
   'scope':r['scope']} for r in diagnostics],
 'physical_mechanism':['T2: zero-load state1 actuator contacts current world medium; native carrier1 acquires current direction.',
 'T3/T4: fixed zero-load turns route both possible directions to a common comparison site.',
 'T5: current native carrier and prepared expectation interact; T9 normalizer transforms mismatch into P/Q state.',
 'T10: identical query opportunities read that state; T12 resulting route intercepts a threat; T15 load3 delivery survives.'],
 'levels':{'A':{'state':'POSITIVE_FINITE','description':'Prepared normalizers, opportunities, interference and routes'},
  'B':{'state':'POSITIVE_FINITE','description':'Regulatory direction differs with the physically received consequence and subsequent acquired policy state'},
  'C':{'state':'PARTIAL_NOT_LONGITUDINAL_STRATEGY_LEARNING','description':'Physical action consequence changes the next regulatory state through a fixed retain/switch mechanism. No learned utility rule, autonomous choice of timing, or sustained consequence-optimized strategy was demonstrated.'}},
 'identity':'Independent regulatory cohorts; not causally integrated into selected E1 at this cut.',
 'adverse_results':{'v1':'Extra inactive comparison lane prevented opposite-medium use. Its original source and all measurements retained. Removed before v2 design freeze; new reservations used.',
 'sham_actuator':'Moving the actual contact actuator off path is a lesion, not an inert sham; reported as such.',
 'first_diagnostic_attempt':'Exact-uint64 string assigned to native integer setter caused TypeError; convert explicitly to int. Partial artifact/log retained; corrected diagnostics are forks, never new individuals.'}}
(rev/'REGULACION_ADQUIRIDA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
atlas={'schema':'CPC8.additional.native.relations.v1','entries':[
 {'id':'NR_REG_SCALAR_ALIAS','mechanism':'Equal max/sum scalar policy readings, different direction and useful delivery',
  'cases':['REG_V2_P21','REG_V2_H21'],'observed_scalars':[by[k]['policy_max_scalar_load'] for k in('REG_V2_P21','REG_V2_H21')],
  'evidence':'revision/REGULACION_ADQUIRIDA.json#/data','scope':'Observational distinction in a finite controller, not a new semantic concept.'},
 {'id':'NR_ZERO_LOAD_CONTACT','mechanism':'state1 load0 material still contributes a direction to the current-world contact and permits later consequence routing',
  'controls':['REG_V2_C21','REG_V2_C22','REG_V2_D21','REG_V2_D22','REG_V2_S21','REG_V2_S22'],
  'scope':'Functional role of known v27 dynamics in a new preparation; not discovery of a new kernel law.'},
 {'id':'NR_UNUSED_LANE_INTERFERENCE','mechanism':'Two prepared zero-load turners from different comparison lanes point into the same EMPTY target atT1. Direction sum(0,-2,2) produces(0,-1,+1), rather than the intended surviving(+1,-1,+1) turner in the one-lane preparation.',
  'cases':['REG_V1_H11','REG_V2_DISCOVERY_NEGATIVE'],
  'causal_evidence':'resultados/regulacion/NR_PREMATURE_ZERO_JOIN/OBSERVACIONES.json: T0 Moore27, exact incoming directions, T1 posttarget, two native snapshots per preparation',
  'scope':'The covered join is reconstructed from actual directed contributors, not proximity. The two preparations differ in resources; no global architecture superiority inferred.'}]}
(rev/'RELACIONES_NATIVAS_ADICIONALES_REGULACION.json').write_text(json.dumps(atlas,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report['bounded_contrast']))
