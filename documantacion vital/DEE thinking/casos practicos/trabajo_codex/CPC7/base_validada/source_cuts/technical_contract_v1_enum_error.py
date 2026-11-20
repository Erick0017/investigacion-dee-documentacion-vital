"""Bounded technical regression; no semantic success targets are learned here."""
import argparse,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,identity,put,sha,digest,operational,record,receipt
from integrated import Session
import selective_native,order_memory

def run(backend,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);engine=identity();started=time.monotonic()
    s=selective_native.create({'id':'TECH_'+backend,'backend':backend});w=s.world;g=s.geometry
    initial=digest(w);checks=[]
    for bad in ({'port':'L03.signal','payload':True,'tick':0},{'port':'L03.signal','payload':5,'tick':-1},{'port':'L03.signal','payload':65536,'tick':0}):
        try:s.stimulate([bad]);raise AssertionError('Invalid input accepted')
        except (TypeError,ValueError):checks.append(True)
    assert digest(w)==initial and len(s.requests)==0
    s.stimulate(order_memory.experience('AB'));s.stimulate([{'port':'order.read','payload':7,'tick':2,'kind':'probe'}])
    s.stimulate(selective_native.stimulus_for_forms(g,[1,-1,1,-1,1,-1,1,-1]+[1]*8,range(8),0))
    s.stimulate([{'port':'need.actual.left.-1','payload':17,'tick':11,'kind':'submit'},{'port':'need.actual.right.-1','payload':17,'tick':11,'kind':'submit'}])
    s.stimulate([{'port':k,'payload':7,'tick':69,'kind':'probe'} for k in g['action_inputs']])
    s.stimulate([{'port':p['teach_port'],'payload':5,'tick':72,'kind':'submit'} for p in g['names'].values()])
    states=[]
    for t in (5,19,70,72,75):
        s.advance_to(t);states.append(digest(w))
        before=digest(w)
        for _ in range(3):selective_native.capture(s)
        assert digest(w)==before
    path=out/'TECH75.deetsnap';cp=s.save(path);loaded=Session.load(path)
    assert digest(loaded.world)==digest(w)
    op=operational(w);lop=operational(loaded.world)
    for a in (op,lop):a['metadata']={k:v for k,v in a['metadata'].items() if not k.startswith('dee_thinking.organizational.')}
    assert op==lop
    s.advance_to(76);loaded.advance_to(76);assert digest(w)==digest(loaded.world)
    result={'schema':'CPC7.technical_contract.v1','status':'VERIFIED','backend':backend,'engine':engine,'states':states,
        'invalid_inputs_rejected_before_evolution':len(checks),'passive_observation_preserves_physics':True,
        'snapshot_physical_operational_equal':True,'continued_after_restore_equal':True,'checkpoint':cp,
        'requests':s.receipts(),'final':digest(w),'code_sha256':sha(__file__),'elapsed_seconds':time.monotonic()-started}
    put(out/'CONTRACT.json',result);print(json.dumps({'backend':backend,'status':'VERIFIED','seconds':result['elapsed_seconds']}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--backend',choices=['LAZY','DENSE','DENSE_PARALLEL'],required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.backend,a.out)
