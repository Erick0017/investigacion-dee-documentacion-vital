"""Brief exact causal replay of the inherited basal order mechanism."""
import argparse,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,identity,put,digest,record,receipt,sha,operational
import integrated,order_memory

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);engine=identity();rows=[];started=time.monotonic()
    for h in ('AB','BA'):
        s=integrated.create(adapter=False);s.stimulate(order_memory.experience(h))
        s.stimulate([{'port':'order.read','payload':7,'tick':2,'kind':'probe','origin':'COMMON_REFERENCE_READER'}])
        observations=[]
        for tick in range(8):
            s.advance_to(tick);observations.append({'tick':tick,'body':order_memory.observations(s.world,s.geometry['body'])})
        before=digest(s.world)
        for _ in range(3):s.observe()
        assert digest(s.world)==before
        at5=observations[5]['body'];rows.append({'history':h,'observations':observations,'requests':s.receipts(),'emission_at5':at5['emission'],'delta_at5':at5['delta'],'passive_observation_unchanged':True})
    assert rows[0]['emission_at5']['direction']==[1,-1,0] and rows[1]['emission_at5']['direction']==[-1,-1,0]
    assert rows[0]['delta_at5']==-1 and rows[1]['delta_at5']==1
    result={'schema':'CPC7.reference.order.v1','status':'VERIFIED','type':'TECHNICAL_REFERENCE_REPRODUCTION','engine':engine,
        'code_sha256':sha(__file__),'historical_source':'CPC6 integrated/order_memory, unchanged copies identified by genealogy manifest',
        'not_new_scientific_replicates':True,'trajectories':rows,'elapsed_seconds':time.monotonic()-started}
    put(out/'REFERENCE.json',result);print(json.dumps({'reference':'CPC6 basal order AB/BA','status':'VERIFIED','trajectories':2}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.out)
