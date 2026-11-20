"""Prospectively fixed references over closed RAW-case records, never actors.

Not a Native replay or physical counterfactual world: uses the observed cue
STATE and the same prepared environmental law on a frozen case schedule.
The real FI oldq+6 outcome is yoked, not re-simulated. No external reference
controls any DEE life or returns a policy to a bridge.
"""
from pathlib import Path
import argparse,hashlib,json

def run(rows,horizon):
    if horizon not in(12,18):raise ValueError('Explicit prospective horizon')
    rr=sorted([r for r in rows if not r['calibration']and r['arm']=='real'and r['trace_control']=='none'and r['ordinal']<horizon],key=lambda r:r['ordinal'])
    if [r['ordinal']for r in rr]!=list(range(horizon)):raise ValueError('Closed actual complete horizon required; no cherry-picked prefix')
    references={}
    for policy in('always_query','never_query','global_keep_success_switch_failure','STATE_keep_success_switch_failure','STATE_keep_switch_presence_initial'):
        last=True;bank={};out=[]
        for r in rr:
            # Choice sees present STATE and its own past actual-law outcomes.
            # It does not see regime, preview direction or bin before acting.
            state=r['q1_STATE']
            query=True if policy=='always_query'else False if policy=='never_query'else last if policy=='global_keep_success_switch_failure'else bank.get(state,state>0 if policy=='STATE_keep_switch_presence_initial'else True)
            # Only after the fixed reference query may its direction be read.
            route=r['actual_preview_bit']if query else 0
            # Environmental/evaluator calculation, never participant input.
            available=0 if r['regime']=='bypass'else r['actual_preview_bit']
            useful=route==available and r['FI_choice_old_q6']==1
            if policy=='global_keep_success_switch_failure':last=query if useful else not query
            if policy in('STATE_keep_success_switch_failure','STATE_keep_switch_presence_initial'):bank[state]=query if useful else not query
            out.append({'ordinal':r['ordinal'],'observed_STATE':state,'query':query,'route':route,'useful_in_fixed_case_law':useful,'reserved':r['reserved']})
        references[policy]={'offered':horizon,'useful':sum(r['useful_in_fixed_case_law']for r in out),
          'reserved_offered':sum(r['reserved']for r in out),'reserved_useful':sum(r['reserved']and r['useful_in_fixed_case_law']for r in out),
          'questions':sum(r['query']for r in out),'rows':out}
    return {'schema':'DEE.PI10.prospective_offline_references.R02','Native_executed':False,'controlled_DEE':False,
      'references':references,'input_information':'Present measured STATE only at choice; own prior action/outcome. After Query only, the measured RAW direction is available. Regime/availability/answer are evaluator-only.',
      'qualification':'Case-level reference, not a second motor or Native experiment. Fixed compatible q2 codec assumed, no Native NULL or reader rejection modeled. Real FI outputs yoked. Alternative actions would change Native physical history; therefore these scores do not establish a full-world performance comparison.',
      'query_cost_units':'Count of questions, not converted into resource64B/energy or a common currency. No outcome-based scoring weights.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--recalculo',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    v=json.loads(a.recalculo.read_text('utf-8-sig'))
    if v['schema']!='DEE.PI10.independent_RAW_recalc.R03':raise ValueError('Only independently checked closed primary projection R03')
    out=run(v['rows'],v['evaluation_horizon']);out['source_sha256']=hashlib.sha256(a.recalculo.read_bytes()).hexdigest()
    if a.salida.exists():raise ValueError('Never overwrite an earlier reference result')
    with a.salida.open('x',encoding='utf8')as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'file':str(a.salida),'sha256':hashlib.sha256(a.salida.read_bytes()).hexdigest(),'Native_executed':False}))
if __name__=='__main__':main()
