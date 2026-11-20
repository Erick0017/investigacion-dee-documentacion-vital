"""Directed passive continuation of AS03's nonexpressed U4 latequery.

Projected paths are candidate coordinates, not inferred unique genealogies.
No edits and no additional inputs are made to the loaded physical world.
"""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha,identity,record,digest,local_context,until
from action_feedback import moved


def main():
    import dee_thinking as d
    folder=ROOT/'resultados/ARCHITECTURE_SCREEN_01/AS03_FOUR_COMPOUNDS'
    physical=d.OrganizationalWorld.load_snapshot(str(folder/'T23.deetsnap'))
    primary=json.loads((folder/'MEASUREMENTS.json').read_text(encoding='utf-8'))
    g=primary['geometry']['units']['U4']['adapter'];key='feedback.late.left.mismatch.Q.negative'
    target=g['late_queries'][key]['site'];info=g['branches']['left.mismatch']['sources']['Q']['information_site']
    rows=[]
    for tick in range(23,34):
        until(physical,tick)
        data_site=moved(info,(-1,-1,0),tick-23)
        query_site=moved(target,(0,1,1),tick-33)
        rows.append({'tick':tick,'projected_information_site':record(physical,data_site),
              'projected_query_site':record(physical,query_site),'target':record(physical,target),
              'data_local':local_context(physical,data_site),'query_local':local_context(physical,query_site),
              'target_local':local_context(physical,target)})
    expected=d.OrganizationalWorld.load_snapshot(str(folder/'T33.deetsnap'))
    assert digest(physical)==digest(expected),'DirectedcontinuationdifferentfromsavedphysicalT33'
    out={'schema':'CPC6.architecture_inspection.v1','engine':identity(),'source_sha256':sha(__file__),
         'parent_snapshot':str((folder/'T23.deetsnap').relative_to(ROOT)),'parent_snapshot_sha256':sha(folder/'T23.deetsnap'),
         'scope':'No intervention, no newinputs, candidateU4data/querypaths selected fromdeclaredgeometrybeforecontinuation. Moore27 neighborhoods saved. Notuniquegenealogybyproximity.',
         'rows':rows,'final_physical':digest(physical),'matches_original_T33_RAW_clocks':True,
         'preparations':0,'technical_reproductions':1,'new_scientific_histories':0}
    put(ROOT/'resultados/ARCHITECTURE_U4_INSPECTION_01.json',out)
    print([{k:r[k] for k in ('tick','projected_information_site','projected_query_site','target')} for r in rows],flush=True)


if __name__=='__main__':main()
