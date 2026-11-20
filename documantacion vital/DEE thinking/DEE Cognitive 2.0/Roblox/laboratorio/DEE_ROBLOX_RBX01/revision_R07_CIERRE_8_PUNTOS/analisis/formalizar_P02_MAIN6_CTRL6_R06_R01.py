"""Serialize the already calculated closed P02 result; no new phase calculation."""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'P02_MAIN6_CTRL6_RECALCULO_R06_R01'
facts=json.loads((OUT/'HECHOS_CIERRE8_R07.json').read_text('utf-8'))
main,ctrl=facts['arms'];rows=[]
for m,c in zip(main['rows'],ctrl['rows']):
    assert m['cycle']==c['cycle']
    rows.append({'cycle':m['cycle'],'main_tag':m['submitted_contact_tag'],'control_tag':c['submitted_contact_tag'],
        'main_datum_from_fixed_contract':m['q2_datum_recalculated_from_frozen_contract'],
        'control_datum_from_fixed_contract':c['q2_datum_recalculated_from_frozen_contract'],
        'main_selected':m['selected_route'],'control_selected':c['selected_route'],
        'main_destination':m['destination'],'control_destination':c['destination']})
summary={'schema':'DEE.R07.P02.ClosedSixMatchedInterpretation.R01','mode':'PASSIVE_EXISTING_RESULTS_ONLY',
    'reused_main_not_recalculated':facts['reused_main'],
    'matched_global_cycles':facts['common_observed_cycles'],'denominators':{'MAIN':6,'CTRL':6,'unoffered_not_scored':True},
    'criterion_before_evaluation':'At least2 destinations outside{2,3} in the final3 of the first6 new opportunities',
    'result':{'MAIN':main['first6_P02'],'CTRL':ctrl['first6_P02'],
        'new_resources':[main['delta']['resourceCount'],ctrl['delta']['resourceCount']],
        'new_deliveries':[main['delta']['delivered'],ctrl['delta']['delivered']],
        'B_numeric_invocations':[sum(n['slot']=='B'for n in main['numeric']),sum(n['slot']=='B'for n in ctrl['numeric'])]},
    'luma_actual_uses':{'MAIN':main['numeric'],'CTRL':ctrl['numeric'],
        'scope':'Three recorded luma+ readings/arithmetic outputsA11 in each arm. No teaching or12/12 historical panel is inferred.'},
    'recorded_public_fields_and_fixed_transduction':rows,
    'input_scope':'Datums are computed by the frozen encoder from recorded observations and declared sensor arm. This analysis does not turn them into a new material consultation or prove every input admission/microtrajectory.',
    'closed_physical_witness':facts['physical_comparison'],
    'interpretation':[
        'The changed/constant local-tag transduction did not produce a sustained escape or resource gain in these six paired opportunities.',
        'Identical finalN/T/RAW/clocks is equality of that recorded physical projection at this cut, not proof of identical paths, complete organization, environment metadata or global causal state.',
        'Life/session identities, capacities/roles, administrative lease metadata and World histories remain distinct. Clones share the same earlier prefix and are not independent organisms.',
        'No semantic decoding of the price/tag bits is established by supplying a larger scalar or by an equal outcome.',
        'Luma was accessible in the fixed recorded use in both arms; a general loss of luma is not supported. Nara/B or other inherited capabilities were not newly tested here.',
        'This passive result neither reproduces Native nor tests material reopen of the final cut; such claims require their own closed primaries.'
    ],
    'issues':facts['issues_total'],'Native_MCP_World_SQLite_model_solver_executions':0,
    'originals_modified':False,'Main_live35_to46_read':False}
target=OUT/'INTERPRETACION_P02_CERRADA_R06_R01.json'
with target.open('x',encoding='utf-8')as f:json.dump(summary,f,ensure_ascii=False,indent=2);f.write('\n')
for file in('HECHOS_CIERRE8_R07.json','HUELLAS_FISICAS_Y_LIMITES_R07.json','INTERPRETACION_P02_CERRADA_R06_R01.json'):
    p=OUT/file;raw=p.read_bytes();print(json.dumps({'file':str(p),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}))
