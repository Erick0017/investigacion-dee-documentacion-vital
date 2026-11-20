"""Read-only continuation locating the second F2 output's local antecedents."""
import argparse,json,sys,hashlib
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(a.parent/'executed_source/src'))
    from relaciones.temporal_roles import TemporalSession,physical,move
    s=TemporalSession.load(a.parent/'T100.deetsnap.gz');start=physical(s.world);frames=[]
    for t in(136,142,159,160,161,162):
        s.run_until(t);frame={'tick':t,'emission':s.observe(s.geometry['body']['emission']),'lanes':{}}
        for k,p in s.geometry['lanes'].items():
            frame['lanes'][k]={'query':s.observe(p['query_site']),'neighborhood':[s.observe(move(p['query_site'],(x,y,z))) for x in(-1,0,1) for y in(-1,0,1) for z in(-1,0,1)],
                'teaching_hub':s.observe(p['teaching_hub']),'nominal_unused_cue':s.observe(move(p['teaching_hub'],(0,0,1),t-s.geometry['ticks']['teach']))}
        frames.append(frame)
    result={'schema':'CPC8.temporal.local_antecedent_observer.v1','parent_snapshot':'TMP_P22_BA_PRESERVING/T100.deetsnap.gz','parent_sha256':hashlib.sha256((a.parent/'T100.deetsnap.gz').read_bytes()).hexdigest(),'start_physical':start,'continuations':1,'preparations':0,'new_participant_inputs':[],'frames':frames,'final_physical':physical(s.world),'coverage':'LocalMoore26+center around declared queries and fixed nominal paths; no inferred unique genealogy beyond recorded points.'}
    (a.out/'MEASUREMENTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Observer completed; no new participant inputs.')
if __name__=='__main__':main()
