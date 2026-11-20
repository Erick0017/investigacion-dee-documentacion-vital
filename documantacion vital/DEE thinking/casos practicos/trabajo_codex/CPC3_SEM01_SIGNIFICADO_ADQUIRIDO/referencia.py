"""Two short published 4.0 witnesses. Not new association/use evidence."""
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from src.common import identity,digest,put
def main():
    p=argparse.ArgumentParser();p.add_argument('--wheel',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    import dee_thinking as d
    report={'identity':identity(a.wheel),'modality':'PUBLISHED4_REFERENCE_NOT_NEW_SCIENCE','cases':[]}
    for teachers in ([7,11],[11,7]):
        s=d.NativeAssociationSession.create();initial=digest(s.world);acquisition=s.train(teachers,5,'paired');s.save_snapshot(str(a.output/('acquired_'+str(teachers[0])+'.deetsnap')))
        s=d.NativeAssociationSession.load_snapshot(str(a.output/('acquired_'+str(teachers[0])+'.deetsnap')))
        before=digest(s.world)
        for j in range(10):s.observe()
        assert before==digest(s.world)
        response=s.query_panel(13);report['cases'].append({'initial':initial,'teachers':teachers,'acquisition':acquisition,'response':response,'final':digest(s.world),'passive_observation_unchanged':True})
    assert report['cases'][0]['initial']==report['cases'][1]['initial']
    assert report['cases'][0]['response']['decoded']=={'q0':25,'q1':29}
    assert report['cases'][1]['response']['decoded']=={'q0':29,'q1':25}
    put(a.output/'REFERENCE.json',report);print('REFERENCE_4_0_PAYLOAD_AND_NATIVE_CONTINUATION_CHECKED')
if __name__=='__main__':main()
