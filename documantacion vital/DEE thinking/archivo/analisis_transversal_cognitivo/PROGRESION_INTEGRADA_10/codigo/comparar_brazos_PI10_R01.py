"""Prospective paired-arm checks over independently recalculated closed records.

No DEE, simulation or actor policy. Never merge IDs or histories across lives.
The fixed+5/18 yoke and the unchanged actual input information are audited,
not assumed from arm labels. A difference is reported, not repaired.
"""
from pathlib import Path
import argparse,hashlib,json

ARMS=('real','nonfailure','yoked')
def need(ok,why):
    if not ok:raise ValueError(why)

def compare(value):
    need(value['schema']=='DEE.PI10.independent_RAW_recalc.R02','Independent RAW/receipt/resource recalc R02 required')
    groups={arm:sorted([r for r in value['rows']if not r['calibration']and r['arm']==arm and r['trace_control']=='none'and r['ordinal']<18],key=lambda r:r['ordinal'])for arm in ARMS}
    complete=all([r['ordinal']for r in groups[arm]]==list(range(18))for arm in ARMS)
    if not complete:return {'schema':'DEE.PI10.paired_arm_comparison.R01','complete':False,'observed':{a:len(r)for a,r in groups.items()},'gain':None,'Native_executed':False,'automatic_adoption':False}
    summaries={}
    for arm,rows in groups.items():
        need(len({r['life_id']for r in rows})==1,'One actual continuous life per arm')
        ids={}
        for r in rows:
            for ident,status in r['receipt_id_status'].items():
                if ident in ids:need(ids[ident]==status,'Incompatible repeated receipt within a life')
                ids[ident]=status
        sensitive=[r for r in rows if r['q1_STATE']==1 and r['actual_preview_bit']==1]
        local_correct=[r for r in sensitive if r['q1_valid']and r['q1_actual_motor']==(-1 if r['regime']=='bypass'else 1)]
        summaries[arm]={'life_id':rows[0]['life_id'],'start_tick':rows[0]['before_tick'],'end_tick':rows[-1]['after_tick'],
          'Native_ticks':sum(r['Native_ticks']for r in rows),'opportunities':18,'reserved12':sum(r['reserved']for r in rows),
          'formed_q1':sum(r['q1_Native_choice']is not None for r in rows),'q1_NULL':sum(r['q1_Native_choice']is None for r in rows),
          'q1_zero_valid':sum(r['q1_Native_zero']for r in rows),'queries_requested':sum(r['query_requested']for r in rows),
          'questions_released':sum(r['query_released']for r in rows),'physical_resources':sum(r['physical_delivered']for r in rows),
          'attributed_resources':sum(r['attributed_useful']for r in rows),'reserved_resources':sum(r['reserved']and r['attributed_useful']for r in rows),
          'reserved_physical_resources':sum(r['reserved']and r['physical_delivered']for r in rows),
          'physical_delivery_not_attributed':sum(r['physical_delivered']and not r['attributed_useful']for r in rows),
          'Native_requested_unique':len(ids),'Native_applied_unique':sum(s=='applied'for s in ids.values()),
          'Native_rejected_unique':sum(s!='applied'for s in ids.values()),
          'receipt_aliases_across_episodes':sum(r['unique_Native_requested']for r in rows)-len(ids),
          'material_negative_returns':sum(r['returned_failed']for r in rows),'generic_returns_total':18,
          'same_STATE1_Z_sensitive_opportunities':len(sensitive),'same_STATE1_Z_pertinent_selections':len(local_correct),
          'all_actual_FI_plus':all(r['FI_choice_old_q6']==1 for r in rows),
          'q2_bank_always_minus1':all(r['q2_before']==-1 and r['q2_after']==-1 for r in rows),
          'actual_preview_bits':[r['actual_preview_bit']for r in rows],'actual_preview_STATEs':[r['q1_STATE']for r in rows]}
    real=groups['real'];non=groups['nonfailure'];yoke=groups['yoked']
    permutation=[(i+5)%18 for i in range(18)]
    yoke_rows=[{'ordinal':i,'source_actual_real_ordinal':source,'actual_yoked_return':yoke[i]['returned_failed'],'source_actual_failure':real[source]['actual_failed'],
      'matches':yoke[i]['returned_failed']is real[source]['actual_failed']}for i,source in enumerate(permutation)]
    # A wrong yoke is scientifically a different control, not quietly repaired.
    yoke_matches=all(r['matches']for r in yoke_rows)
    simultaneous=[]
    for i in range(18):
        rows=[groups[a][i]for a in ARMS]
        simultaneous.append({'ordinal':i,'regime':real[i]['regime'],'STATEs':[r['q1_STATE']for r in rows],
          'actual_bits':[r['actual_preview_bit']for r in rows],'q1_choices':[r['q1_Native_choice']for r in rows],
          'actual_queries':[r['query_requested']for r in rows],'resources':[r['attributed_useful']for r in rows],
          'generic_returns':[r['returned_failed']for r in rows],
          'query1_tick_differences_vs_real':[r['query1_tick']-real[i]['query1_tick']for r in rows],
          'query2_tick_differences_vs_real':[r['query2_tick']-real[i]['query2_tick']for r in rows],
          'same_observed_STATE_and_bit':len({(r['q1_STATE'],r['actual_preview_bit'])for r in rows})==1})
    gain=summaries['real']['reserved_resources']-summaries['nonfailure']['reserved_resources']
    gain_yoke=summaries['real']['reserved_resources']-summaries['yoked']['reserved_resources']
    physical_gain=summaries['real']['reserved_physical_resources']-summaries['nonfailure']['reserved_physical_resources']
    physical_gain_yoke=summaries['real']['reserved_physical_resources']-summaries['yoked']['reserved_physical_resources']
    return {'schema':'DEE.PI10.paired_arm_comparison.R01','complete':True,'Native_executed':False,'summaries':summaries,
      'reserved_gain_vs_nonfailure':gain,'reserved_gain_vs_yoked':gain_yoke,
      'reserved_physical_resource_gain_vs_nonfailure':physical_gain,'reserved_physical_resource_gain_vs_yoked':physical_gain_yoke,
      'fixed_yoke_permutation':permutation,
      'yoke_matches_actual_real_sequence':yoke_matches,'yoke_rows':yoke_rows,'paired_cases':simultaneous,
      'all_paired_samples_same_STATE_and_bit':all(r['same_observed_STATE_and_bit']for r in simultaneous),
      'interpretation_gates':{'gain_at_least2':gain>=2,'additional_positive_physical_resource_gain':physical_gain>0,
        'actual_FI_and_q2_stable':all(v['all_actual_FI_plus']and v['q2_bank_always_minus1']for v in summaries.values()),
        'true_contingency_vs_same_negative_dose':yoke_matches and summaries['real']['material_negative_returns']==summaries['yoked']['material_negative_returns'],
        'general_autonomy_or_automatic_adoption':False},
      'qualification':'Paired branches share a prefix; not independent individuals. All labels, Native0, NULL and physical versus attributed products remain separate. Whole-task actual_failed includes a NULLq1 even if64B were physically delivered; it is not necessarily missing material or environmental damage. Positive physical resource gain is an additional prospective Root adoption requirement; improved reader-validity counts alone do not satisfy it. If actual sample contents diverge, the resource contrast includes those sensory/history differences and does not alone isolate question utility. Conservation, reopening and selective trace controls remain separate.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--recalculo',type=Path,required=True);parser.add_argument('--salida',type=Path,required=True);a=parser.parse_args()
    need(not a.salida.exists(),'Never overwrite a prior causal comparison');b=a.recalculo.read_bytes();out=compare(json.loads(b));out['source_sha256']=hashlib.sha256(b).hexdigest()
    with a.salida.open('x',encoding='utf8')as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'file':str(a.salida),'sha256':hashlib.sha256(a.salida.read_bytes()).hexdigest(),'complete':out['complete'],'Native_executed':False}))
if __name__=='__main__':main()
