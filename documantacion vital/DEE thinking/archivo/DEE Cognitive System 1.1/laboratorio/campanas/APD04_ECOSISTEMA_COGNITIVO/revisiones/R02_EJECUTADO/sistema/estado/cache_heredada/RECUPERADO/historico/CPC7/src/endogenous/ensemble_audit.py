"""Recalculate ensemble panels and check a pending-input continuation in a new process."""
from pathlib import Path
import argparse,json,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha,digest,operational
from integrated import Session
from ensemble import readout


def main():
    p=argparse.ArgumentParser();p.add_argument('--results',type=Path,required=True);a=p.parse_args()
    index=json.loads((a.results/'INDEX.json').read_text(encoding='utf-8'));worlds=[];units=[];statuses={}
    for item in index['cases']:
        evidence=ROOT/item['evidence'];r=json.loads(evidence.read_text(encoding='utf-8'))
        statuses[r['status']]=statuses.get(r['status'],0)+1
        if r['status']!='MEASURED':continue
        recs=r['requests'];admission={}
        for request in recs:
            key=request['receipt']['status'];admission[key]=admission.get(key,0)+1
        worlds.append({'case':r['case']['id'],'split':r['case']['split'],'upperlevel_units':r['upperlevel_units'],
            'preparations':1,'resources':r['resources'],'admission':admission,'elapsed_seconds':r['elapsed_seconds'],
            'evidence':item['evidence'],'sha256':sha(evidence)})
        for unit in r['case']['units']:
            panel=readout(r['rows'],unit['id'])
            if panel!=r['panels'][unit['id']]:raise AssertionError('Recalculation differs from saved panel')
            emitted=panel['order_emission5'];physical_discrepancy=(emitted['direction'][0]!=unit['actual'])
            sources=[x['record']['direction'][1] for x in panel['information24']]
            used=[x['record']['direction'][1] for x in panel['use29']]
            units.append({'case':r['case']['id'],'unit':unit['id'],'split':r['case']['split'],
                'history':unit['history'],'actual':unit['actual'],'source_value':unit['source_value'],
                'emission_direction5':emitted['direction'],'physical_discrepancy':physical_discrepancy,
                'counts':panel['counts'],'observed_source_information':sources,'observed_used_information':used,
                'source_content_conserved':all(x==unit['source_value'] for x in sources+used) if sources else None,
                'delta5':panel['relational_delta5'],'delta72':panel['relational_delta72'],
                'relation_retained_passively':panel['relational_delta5'] is not None and panel['passive_relation_retained5_to72']})
    mismatch=[u for u in units if u['physical_discrepancy']];matched=[u for u in units if not u['physical_discrepancy']]
    counts={'independent_preparations':len(worlds),'upperlevel_units_observed':len(units),'distinct_worlds':len(worlds),
        'discrepancy_units':len(mismatch),'discrepancy_with_question_information_use':sum(u['counts']=={'q':1,'information':1,'use':1} for u in mismatch),
        'matched_units':len(matched),'matched_with_no_X_question_info_use':sum(u['counts']=={'q':0,'information':0,'use':0} for u in matched),
        'passively_retained_relations5_to72':sum(u['relation_retained_passively'] for u in units),
        'queries_after29':0,'cross_unit_communication_demonstrations':0,'integrated_cooperation_demonstrations':0}
    summary={'schema':'CPC7.reference_specialist_ensemble.audit.v1','classification':'REFERENCE_SPECIALIST_ENSEMBLE',
        'statuses':statuses,'counts':counts,'worlds':worlds,'units':units,
        'formula':'Discrepancy is auditor comparison of measured emission.dx@5 with actual event sign. Native mechanism makes the request; this calculation is only posterior evaluation.',
        'denominators':'Six distinct world preparations; fourteen simultaneous units in nested ensemble sizes, not fourteen independent world replicas. Each is deterministic; no inference of population-level architecture advantage.',
        'scope':'One-, two-, and four-unit layouts preserve the local comparison→question→information→use mechanism in this aperture. Memory differential is passively retained through72; repeated access after72 is not tested. More units introduce 2x/4x initial components and experience budget at fixed N; they are not integrated cooperating agents.'}
    put(a.results/'ENSEMBLE_SUMMARY.json',summary)
    target=a.results/'E_H03_4';r=json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf-8'))
    s=Session.load(target/'T19.deetsnap');before=digest(s.world);s.advance_to(72)
    physical=digest(s.world);op=operational(s.world);ref=r['final_operative']
    # Snapshot metadata carries the serialization frontier19 until explicitly
    # updated; compare the operational fields independent of that timestamp.
    compared_fields=['tick','channels','receipts','external_operations','protocols']
    equal_physical=physical==r['final_physical'];equal_operational=all(op[k]==ref[k] for k in compared_fields)
    if not equal_physical or not equal_operational:raise AssertionError('Ensemble continuation differs from primary trajectory')
    put(a.results/'RESTORE_CHECK.json',{'schema':'CPC7.reference_specialist_ensemble.restore.v1',
        'case':'E_H03_4','source_checkpoint':'E_H03_4/T19.deetsnap','checkpoint_sha256':sha(target/'T19.deetsnap'),
        'start_physical':before,'continued_to':72,'full_RAW_clocks_tick_equal':equal_physical,
        'pending_inputs_and_operational_fields_equal':equal_operational,'operative_fields':compared_fields,
        'metadata_exception':'Serialized frontier remains19 until next save; no discrepancy in physical state, receipts, queues or protocol progress.',
        'before':before,'after':physical,'new_preparations':0,'new_experiences_added':0})
    print(json.dumps({'counts':counts,'restore_raw_clocks_tick_equal':equal_physical,'restore_operative_equal':equal_operational}),flush=True)

if __name__=='__main__':main()
