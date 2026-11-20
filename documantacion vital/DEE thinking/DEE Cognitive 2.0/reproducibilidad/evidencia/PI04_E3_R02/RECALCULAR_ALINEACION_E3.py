"""Describe E3 signal/reversal alignment and a matched-information reference.

Post-result explanatory recalculation, not another Native test or a revised
success criterion. The reference receives only the preceding delivered signal
when selecting its next action; environment connection is evaluation only.
"""
from pathlib import Path
import argparse,hashlib,json
def analyze(report):
    result={}
    for arm,case in report['cases'].items():
        rows=case['rows'];reversals=[i for i in range(1,len(rows))if rows[i]['connected_motor_evaluator_only']!=rows[i-1]['connected_motor_evaluator_only']]
        false=[r['ordinal']for r in rows if r['returned_failed']and not r['actual_failed']]
        missed=[r['ordinal']for r in rows if r['actual_failed']and not r['returned_failed']]
        reference=1;reference_rows=[]
        for r in rows:
            # No later context/connection/signal is used in this choice.
            action=reference;success=action==r['connected_motor_evaluator_only']
            reference_rows.append({'ordinal':r['ordinal'],'action':action,'matches_actual_Native':action==r['motor'],'useful_under_real_connection':success,'delivered_failed_after_action':r['returned_failed']})
            if r['returned_failed']:reference=-reference
        preparatory=[i for i in false if i+1 in reversals]
        result[arm]={'false_failure_ordinals_zero_based':false,'true_failures_without_failure_signal':missed,'connection_reversal_ordinals_zero_based':reversals,
                     'false_failure_one_opportunity_before_reversal':preparatory,
                     'Native_motor_changes_immediately_after_these_signals':sum(rows[i+1]['motor']!=rows[i]['motor']for i in preparatory),
                     'received_signal_reference':{'name':'Maintain after delivered nonfailure, switch after delivered failure; initial+1','products':sum(r['useful_under_real_connection']for r in reference_rows),'matches_Native_actions':sum(r['matches_actual_Native']for r in reference_rows),'opportunities':len(rows),'rows':reference_rows,
                       'scope':'Descriptive replay of the actual delivered signal stream. The permuted stream is a fixed experimental input, so this reference has the same signal information. For the real arm this is not an arbitrary counterfactual: its validity is conditional on the verified identical actions.'}}
    return {'schema':'DEE.PI04.E3.signal_alignment.post_result_description.v1','mode':'PASSIVE_DESCRIPTIVE_RECALCULATION_NOT_NEW_EXPERIMENT','new_native_ticks':0,
            'cases':result,'conclusion':'The permuted control receives false failure signals one opportunity before each environmental reversal. Switching after those signals prepares the next route and explains18/18 with a simple matched-signal rule. This does not establish autonomous anticipation, planning, or superiority of true contingency; real contingent feedback scored14/18 in this finite task.',
            'limits':['This explanatory alignment/reference was calculated after observing the outcomes; it changes no frozen success criterion.','The control schedule was a predeclared permutation of a recorded real trajectory, not an autonomous warning discovered by E1.','These branches share a physical prefix; two scores are not independent organism replicates.','The generic signal can affect Native selection without truthfully describing the present outcome. No global claim of necessity/irrelevance of contingency follows.']}
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--recalculo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    if a.out.exists():raise FileExistsError('Fresh output file required')
    b=a.recalculo.read_bytes();report=json.loads(b);result=analyze(report);result['input_recalculation_sha256']=hashlib.sha256(b).hexdigest()
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'mode':result['mode'],'new_native_ticks':0,'cases':{k:{'false_failure_before_reversal':v['false_failure_one_opportunity_before_reversal'],'matched_signal_reference_products':v['received_signal_reference']['products'],'matched_Native_actions':v['received_signal_reference']['matches_Native_actions']}for k,v in result['cases'].items()}},ensure_ascii=False))
if __name__=='__main__':main()
