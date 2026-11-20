"""Pure summary of the fixed D evaluation. No output before actual three6 closures.

The six prepared future opportunities are reported separately. This script
does not deploy, approve or infer counterfactual utility for unexecuted rules.
"""
from pathlib import Path
import argparse,hashlib,json
P=Path(__file__).resolve().parents[1]
def require(ok,why):
    if not ok:raise ValueError(why)
def evaluate(r):
    require(r.get('schema')=='DEE.PI09.D.recalculated_persistent_environment.R02'and r.get('integrity_passed')is True and r.get('Native_executed')is False,'Actual verified documentary D result required')
    groups={}
    for role in('real','none','yoked'):
        found=[g for g in r['groups']if g['arm']==role]
        if len(found)!=1 or found[0]['evaluation_completed']!=6:return {'status':'WAIT','reason':'Three actual evaluated6 histories not yet available','missing_or_incomplete_arm':role,'output_written':False,'Native_executed':False}
        groups[role]=found[0]
    real=groups['real'];greater=all(real['evaluation_useful']>groups[role]['evaluation_useful']for role in('none','yoked'))
    own_revision=[x for x in real['revision_after_failure_descriptors']if x['failed_valence_actually_returned']and x['changed_case_useful']and x['at_least_two_later_actual_useful']]
    evalrows={role:sorted([x for x in r['rows']if x['arm']==role and x['ordinal']<6],key=lambda x:x['ordinal'])for role in groups}
    timing={}
    for role,rr in evalrows.items():
        require([x['ordinal']for x in rr]==list(range(6)),'All six actual opportunities without omissions')
        # Report an actual changed absolute phase/window. A skipped391/782
        # window is distinct from changing the within-window contact phase.
        timing[role]={'q1':[x['q1']for x in rr],'q2':[x['q2']for x in rr],'Native_ticks':[x['Native_ticks']for x in rr],'wait400_at3':rr[3]['prepared_wait_ticks']==400,'actual_q1_deltas':[rr[i]['q1']-rr[i-1]['q1']for i in range(1,6)],'actual_q2_deltas':[rr[i]['q2']-rr[i-1]['q2']for i in range(1,6)],'q1_phases':[x['q1_phase67_391_782']for x in rr],'q2_phases':[x['q2_phase67_391_782']for x in rr],'not_a_claim_of_independent391_or782_contact_phase':True}
    allclosed=all(c['error']is None and c['status']=='CLOSED_FINITE_PHASE'for c in r['closures']if c['arm']in groups)
    return {'schema':'DEE.PI09.D.fixed_actual_comparison.R02','Native_executed':False,'DEE_imported':False,'approval':False,'all_three_evaluation_arms_closed6':True,'actual_counts':{role:{k:g[k]for k in('evaluation_completed','evaluation_useful','future_completed','future_useful','Native_ticks_opportunities','questions_applied','messages_offered','messages_delivered','actual_failed','returned_failed','actual_second_motors','Native_inputs_unique_included_preparation','Native_status_counts')}for role,g in groups.items()},'actual_pairwise_differences':r['paired_observations'],'actual_timing_and_phase':timing,'revision_after_own_returned_failure_descriptors':own_revision,'bounded_readaptation_evidence':{'all_closed_without_transport_error':allclosed,'actual_Real_useful_exceeds_each_control':greater,'Native_changed_after_own_returned_failure_with_later_useful_cases':bool(own_revision),'all_fixed_descriptive_conditions_present':allclosed and greater and bool(own_revision),'not_an_adoption_decision':True},'all_preserved_adverse_attempts':r['failed_preserved_attempts'],'scope':'One fixed new physical contingency in an intact acquired lineage, Native two-stage decisions and one shared bank. Environmental SEM4 support is prepared P0. Actual failure/returned signal and material query cost are distinct. Future6 are excluded from the first6 contrast.','limits':['A query1-specific credit assignment has not been isolated.','None is a constant nonfailure signal; it does not match negative-valence dose. Yoked uses the prespecified real6 permutation and its residual coincidences must remain visible.','No offline utility is attributed to always/never/WSLS without material execution.','A phase/window variation is reported from actual clocks, never inferred from nominal waits alone.','If no error precedes a useful change, or controls do as well, useful function can remain without demonstrated acquired readaptation.']}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--recalculo',required=True);ap.add_argument('--salida',required=True);a=ap.parse_args();source=Path(a.recalculo)
    if not source.is_file():print(json.dumps({'status':'WAIT','missing_closed_input':str(source),'output_written':False,'Native_executed':False}));raise SystemExit(0)
    r=evaluate(json.loads(source.read_text('utf-8-sig')))
    if r.get('status')=='WAIT':print(json.dumps(r));raise SystemExit(0)
    r['source_recalculation']={'path':str(source.resolve()),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()};out=Path(a.salida).absolute();require(out.parent in((P/'control').resolve(),(P/'fuentes').resolve())and not out.exists(),'Fresh PI09 control/fuentes result only')
    with out.open('x',encoding='utf8')as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'output':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bounded_readaptation_evidence':r['bounded_readaptation_evidence'],'approval':False,'Native_executed':False}))
