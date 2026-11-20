"""Explicit diagnostic rescue of AS03 occupied-destination interference.

Never used by MAIN or by the architecture candidate. It localizes access loss.
"""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha,identity,record,digest,operational,local_context,until
from action_feedback import moved


def main():
    import dee_thinking as d
    folder=ROOT/'resultados/ARCHITECTURE_SCREEN_01/AS03_FOUR_COMPOUNDS';out=ROOT/'resultados/ARCHITECTURE_U4_RESCUE_01';out.mkdir(parents=True,exist_ok=False)
    primary=json.loads((folder/'MEASUREMENTS.json').read_text(encoding='utf-8'));g=primary['geometry']['units']['U4']['adapter']
    info=g['branches']['left.mismatch']['sources']['Q']['information_site'];victim=moved(info,(-1,-1,0),8);target=g['late_queries']['feedback.late.left.mismatch.Q.negative']['site']
    parent=d.OrganizationalWorld.load_snapshot(str(folder/'T23.deetsnap'));until(parent,30);pre=digest(parent);op=operational(parent);pre_record=record(parent,victim)
    rows=[]
    for label,value in (('CUT_OCCUPIED_DESTINATION',0),('EXACT_SHAM',int(pre_record['raw']))):
        edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*victim);edit.raw=value;edit.label=label
        fork=parent.diagnostic_fork([edit],True);frames=[]
        for tick in range(30,34):
            until(fork,tick);frames.append({'tick':tick,'victim':record(fork,victim),'target':record(fork,target),
              'projected_data':record(fork,moved(info,(-1,-1,0),tick-23)),
              'next_data_destination_local':local_context(fork,moved(info,(-1,-1,0),tick+1-23))})
        path=out/(label+'_T33.deetsnap');fork.save_snapshot(str(path));rows.append({'label':label,'raw_written':str(value),'clock_written':None,
          'frames':frames,'final_physical':digest(fork),'snapshot':path.name,'snapshot_sha256':sha(path)})
    assert digest(parent)==pre and operational(parent)==op,'Diagnosticforkmutatedparent'
    result={'schema':'CPC6.architecture_u4_rescue.v1','engine':identity(),'source_sha256':sha(__file__),
       'parent_snapshot':str((folder/'T23.deetsnap').relative_to(ROOT)),'parent_snapshot_sha256':sha(folder/'T23.deetsnap'),
       'target':target,'intervention_site':victim,'pre_record':pre_record,'pre_Moore27':local_context(parent,victim),
       'parent_physical_unchanged':True,'parent_operative_unchanged':True,'diagnostic_forks':2,'new_preparations':0,
       'results':rows,'scope':'Assisteddiagnosticremovalofonespecificoccupieddestination. Notnativeinterferenceregulationorrecovery. Nooriginassignedto23payloadwithoutcompletegenealogy.'}
    put(out/'MEASUREMENTS.json',result);print(json.dumps({'pre_record':pre_record,'results':[{'label':r['label'],'late33':r['frames'][-1]['target']} for r in rows]}),flush=True)


if __name__=='__main__':main()
