"""Passive, post-trajectory access diagnosis; no edits, no native advances."""
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;sys.path.insert(0,str(HERE))
from common import identity,sha,put,record,digest,local_context,operational


def main():
    import dee_thinking as d
    identity();root=ROOT/'resultados/architectures_order_extension';rows=[]
    for path in sorted(root.glob('ARCH_*/CONTINUATION.json')):
        m=json.loads(path.read_text(encoding='utf-8'));w=d.OrganizationalWorld.load_snapshot(str(path.parent/m['checkpoint']['file']))
        state=json.loads(w.runtime.snapshot_metadata('cpc5.extension.architectures.v1'));spec=state['geometry'];n=spec['N'];start=spec['stages'][0]['meeting'];last=spec['stages'][-1]
        # These positions are predictions from declared routes, not assignments
        # of genealogy. Exact observed fields can contradict the prediction.
        query_first=m['input']['requested_tick']+5;end=int(w.runtime.current_tick)
        query_site=tuple((start[i]+(-1,0,0)[i]*(end-query_first))%n for i in range(3))
        contact_tick=last['meeting_tick']+((query_first-11)//n-1)*n+3
        aggregate_site=tuple((spec['consequence_site_round1'][i]+(0,1,0)[i]*(end-contact_tick))%n for i in range(3))
        before=digest(w);op_before=operational(w)
        query=record(w,query_site);aggregate=record(w,aggregate_site)
        rows.append({'case_id':m['case']['id'],'continuation_file':path.relative_to(ROOT).as_posix(),'continuation_sha256':sha(path),
           'snapshot_sha256':sha(path.parent/m['checkpoint']['file']),'query_receipt':m['receipt'],'query_route_hypothesis':[-1,0,0],
           'query_predicted_site':query_site,'query_actual_record':query,'query_context':local_context(w,query_site),
           'aggregate_route_hypothesis':[0,1,0],'aggregate_predicted_site':aggregate_site,'aggregate_actual_record':aggregate,
           'aggregate_context':local_context(w,aggregate_site),'observation_passive_no_mutation':digest(w)==before and operational(w)==op_before,
           'physical_after':before,'coverage':'Known declared query route and observed previous contact; actual terminal records corroborate modes. Interior transformations not certified by proximity.'})
    result={'schema':'CPC5.extension.passive_access_diagnosis.v1','source_sha256':sha(__file__),'rows':rows,
       'all_snapshot_states_equal':len(rows)==2 and rows[0]['physical_after']==rows[1]['physical_after'],
       'interpretation':'New input is admitted; scalar aggregate309 can persist while the original cascade interface fails to express it. A separate query9 remains on its undeviated incoming direction, rather than reaching the post-contact aggregate. This is lost routing/access in this apparatus, not proof of destroyed aggregate memory or a global kernel limit.',
       'scope':'External passive diagnosis; no participant reads these calculations, snapshots, expected values, or reports.'}
    put(root/'PASSIVE_ACCESS_DIAGNOSIS.json',result);print(json.dumps({'rows':len(rows),'physical_equal':result['all_snapshot_states_equal'],
        'observed':[(r['query_actual_record']['s_reg'],r['query_actual_record']['direction'],r['aggregate_actual_record']['s_reg'],r['aggregate_actual_record']['direction'])for r in rows]}),flush=True)


if __name__=='__main__':main()
