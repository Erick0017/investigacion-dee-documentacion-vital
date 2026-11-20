"""Factual single-trajectory summary from closed primary records, not adoption."""
from pathlib import Path
import argparse,hashlib,importlib.util,json
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('primary',H/'recalcular_primarios_PI10_R03.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--indice',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);args=p.parse_args()
    a.need(not args.salida.exists(),'No overwrite of a previous trajectory conclusion')
    rec=a.bundle(args.indice);horizon=rec['evaluation_horizon'];rows=sorted([r for r in rec['rows']if not r['calibration']and r['arm']=='real'and r['trace_control']=='none'and r['ordinal']<horizon],key=lambda r:r['ordinal'])
    a.need(len({r['life_id']for r in rows})==1 and [r['ordinal']for r in rows]==list(range(horizon)),'One full actual evaluation lineage; no mixed positive branches')
    idx=a.read(args.indice);witnesses=[]
    for entry in idx['episodes']:
        path=a.safe_file(args.indice.parent,entry['witness']['file']);v=a.read(path)
        if v['life_id']==rows[0]['life_id']and not v['operator_calibration']and v['ordinal']<horizon:witnesses.append(v)
    witnesses=sorted(witnesses,key=lambda v:v['ordinal']);ids={ident:status for r in rows for ident,status in r['receipt_id_status'].items()}
    changed=[{'ordinal':r['ordinal'],'regime':r['regime'],'q1_before':r['q1_before'],'q1_after':r['q1_after'],'actual_motor':r['q1_actual_motor'],
      'actual_failed':r['actual_failed'],'returned_failed':r['returned_failed'],'physical_delivered':r['physical_delivered'],'attributed_useful':r['attributed_useful']}for r in rows if r['q1_before']!=r['q1_after']]
    comparable=[{'ordinal':r['ordinal'],'regime':r['regime'],'STATE':r['q1_STATE'],'bit':r['actual_preview_bit'],'Native_choice':r['q1_Native_choice'],'query':r['query_requested'],'useful':r['attributed_useful'],'q1_delta':r['q1_before']}for r in rows if r['q1_STATE']==1 and r['actual_preview_bit']==1]
    out={'schema':'DEE.PI10.single_actual_trajectory_summary.R02','Native_executed':False,'DEE_imported':False,'selected_principal_or_adoption_not_asserted':True,
      'source_index_sha256':a.sha(args.indice.read_bytes()),'life_id':rows[0]['life_id'],'N':67,'first_tick':rows[0]['before_tick'],'last_tick':rows[-1]['after_tick'],
      'Native_ticks_in_evaluation':sum(r['Native_ticks']for r in rows),'offered':horizon,'completed':len(rows),'reserved':sum(r['reserved']for r in rows),
      'physical_resources':sum(r['physical_delivered']for r in rows),'attributed_resources':sum(r['attributed_useful']for r in rows),
      'reserved_physical_resources':sum(r['reserved']and r['physical_delivered']for r in rows),'reserved_attributed_resources':sum(r['reserved']and r['attributed_useful']for r in rows),
      'queries_requested':sum(r['query_requested']for r in rows),'queries_released':sum(r['query_released']for r in rows),
      'Native_q1_NULL_ordinals':[r['ordinal']for r in rows if r['q1_Native_choice']is None],
      'Native_requested_unique':len(ids),'Native_applied_unique':sum(s=='applied'for s in ids.values()),'Native_rejected_unique':sum(s!='applied'for s in ids.values()),
      'all_actual_FI_plus':all(r['FI_choice_old_q6']==1 for r in rows),'all_actual_q2_delta_minus1':all(r['q2_before']==-1 and r['q2_after']==-1 for r in rows),
      'q1_reference_changes':changed,'same_STATE1_plusZ_history_witnesses':comparable,
      'inherited_metadata_literal_equality':{'actor_assertions_true':sum(v['inherited_metadata_literal_unchanged']is True for v in witnesses),
        'actor_assertions_total':len(witnesses),'includes_neutral_R01_parent_key_by_pinned_R02_actor':True,
        'independent_full_snapshot_metadata_comparison_performed_here':False,
        'meaning':'Literal metadata includes the untouched neutral R01 preparation history; it does not assert unchanged physical q1 banks, which genuinely evolve.'},
      'physical_q1_references_final':{side:a.raw_observation(witnesses[-1]['references_after']['q1'][side])for side in('A','B')},
      'what_changed':'Actual generic task consequences changed the new q1 physical reference. For identical measured STATE1/+Z, the actual Native question choice changed across utility conditions and later returned. Outcomes and reference transitions are recorded, not inferred from a Python policy.',
      'what_remained_prepared':'Two physical postread guards, q1/q2 anatomy and codecs, the opportunity schedule, technical RAW register, conditional question service, q2/FI execution order, motor-to-bin transduction, resource law and generic return wiring.',
      'pending_scientific_checks':['Paired nonfailure/yoked resource gain and valence interpretation','Selective formed-trace controls if executed','Representative previous functions at the declared cut','Actual useful use after coherent save/reopen','Cold Native acquisition replay','Root adoption decision and coherent product selection'],
      'scope':'Descriptive evidence for this candidate only; not a causal comparative conclusion, a claim that the old principal was updated, general agency, or a claim that every former ability remained intact.'}
    with args.salida.open('x',encoding='utf8')as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'file':str(args.salida),'sha256':a.sha(args.salida.read_bytes()),'Native_executed':False}))
if __name__=='__main__':main()
