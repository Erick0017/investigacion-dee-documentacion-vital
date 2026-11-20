"""Read-only continuation of a saved experiment; no remedial input is added."""
import argparse,hashlib,json,sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    sys.path.insert(0,str(a.parent.parent/'executed_source/src'))
    from comunicacion.social_channel import SocialSession
    from integracion.shared_world import move,physical
    from dee_thinking import _native as d
    from dee_thinking.consolidated import exact_observation
    s=SocialSession.load(a.parent);start=physical(s.world);rows=[]
    for t in(286,287,288):
        s.run_until(t);sites={}
        for k,q in s.geometry['social']['parts'].items():
            for c in(-1,1):
                # A separate fixed candidate for each possible first context;
                # no actual RAW content chooses the observation coordinates.
                site=move(q['query_site'],(-c,0,0),4,131)
                sites[k+'.previous_context'+str(c)]=exact_observation(s.world.runtime.observe(d.Coordinate(*site)))
        rows.append({'tick':t,'all_context_candidates':sites,'original_query_sites':s.social_view()['query_targets']})
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps({'schema':'CPC8.social.access.observer-continuation.v1',
        'parent':str(a.parent),'parent_sha256':hashlib.sha256(a.parent.read_bytes()).hexdigest(),
        'start':start,'rows':rows,'new_physical_inputs':[],'modality':'PASSIVE_INSTRUMENTAL_CONTINUATION_NOT_MAIN_REPAIR'},ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
