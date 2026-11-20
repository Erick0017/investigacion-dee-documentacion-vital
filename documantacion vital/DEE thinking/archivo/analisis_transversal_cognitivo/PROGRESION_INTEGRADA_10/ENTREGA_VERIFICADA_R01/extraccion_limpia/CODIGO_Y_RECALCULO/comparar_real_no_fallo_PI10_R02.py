"""Predeclared real/nonfailure utility contrast; other causal gates remain separate."""
from pathlib import Path
import argparse,hashlib,json
def need(ok,why):
    if not ok:raise ValueError(why)
def compare(v):
    need(v['schema']=='DEE.PI10.independent_RAW_recalc.R03','Independent complete primary RAW projection')
    horizon=v['evaluation_horizon'];reserve=v['reserved_horizon'];groups={};sets={}
    for arm in('real','nonfailure'):
        rows=sorted([r for r in v['rows']if not r['calibration']and r['arm']==arm and r['trace_control']=='none'and r['ordinal']<horizon],key=lambda r:r['ordinal'])
        need([r['ordinal']for r in rows]==list(range(horizon))and len({r['life_id']for r in rows})==1,'Both full actual paired lineages, failures retained')
        ids={ident:status for r in rows for ident,status in r['receipt_id_status'].items()}
        groups[arm]={'life_id':rows[0]['life_id'],'opportunities':horizon,'reserved':sum(r['reserved']for r in rows),
          'physical':sum(r['physical_delivered']for r in rows),'attributed':sum(r['attributed_useful']for r in rows),
          'reserved_physical':sum(r['reserved']and r['physical_delivered']for r in rows),'reserved_attributed':sum(r['reserved']and r['attributed_useful']for r in rows),
          'queries':sum(r['query_requested']for r in rows),'Native_q1_NULL':sum(r['q1_Native_choice']is None for r in rows),
          'all_actual_FI_plus':all(r['FI_choice_old_q6']==1 for r in rows),'q2_delta_always_minus1':all(r['q2_before']==-1 and r['q2_after']==-1 for r in rows),
          'Native_requested':len(ids),'Native_applied':sum(s=='applied'for s in ids.values()),'Native_rejected':sum(s!='applied'for s in ids.values()),
          'first_tick':rows[0]['before_tick'],'last_tick':rows[-1]['after_tick']};sets[arm]=rows
    a=groups['real'];b=groups['nonfailure'];atr=a['reserved_attributed']-b['reserved_attributed'];phy=a['reserved_physical']-b['reserved_physical']
    paired=[{'ordinal':i,'same_STATE_bit':(sets['real'][i]['q1_STATE'],sets['real'][i]['actual_preview_bit'])==(sets['nonfailure'][i]['q1_STATE'],sets['nonfailure'][i]['actual_preview_bit']),
      'same_query_ticks':sets['real'][i]['query1_tick']==sets['nonfailure'][i]['query1_tick']and sets['real'][i]['query2_tick']==sets['nonfailure'][i]['query2_tick']}for i in range(horizon)]
    return {'schema':'DEE.PI10.real_nonfailure_utility_comparison.R02','Native_executed':False,'groups':groups,'reserved_planned':reserve,
      'reserved_attributed_gain':atr,'reserved_physical_gain':phy,'whole_attributed_gain':a['attributed']-b['attributed'],'whole_physical_gain':a['physical']-b['physical'],
      'paired_samples_and_clocks':paired,'all_paired_STATE_bit_same':all(r['same_STATE_bit']for r in paired),'all_paired_query_ticks_same':all(r['same_query_ticks']for r in paired),
      'predeclared_utility_gate':atr>=2 and phy>=1,'automatic_adoption':False,
      'not_closed_by_this_contrast':['Contingent truth versus matched negative valence/yoked control','Selective formed-trace control if used','Legacy12 conservation and actual useful use after reopening','Cold Native replay and product adoption'],
      'qualification':'Same-prefix paired controls, not independent individuals. The predeclared utility gate is a local contrast and is insufficient by itself for scientific attribution, conservation or promotion. Physical and attributed products are separate; NULLq1 is not selected NoQuery.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--recalculo',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);args=p.parse_args()
    need(not args.salida.exists(),'No overwrite of an earlier contrast');b=args.recalculo.read_bytes();out=compare(json.loads(b));out['source_sha256']=hashlib.sha256(b).hexdigest()
    with args.salida.open('x',encoding='utf8')as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'file':str(args.salida),'sha256':hashlib.sha256(args.salida.read_bytes()).hexdigest(),'groups':out['groups'],'utility_gate':out['predeclared_utility_gate'],'Native_executed':False},ensure_ascii=False))
if __name__=='__main__':main()
