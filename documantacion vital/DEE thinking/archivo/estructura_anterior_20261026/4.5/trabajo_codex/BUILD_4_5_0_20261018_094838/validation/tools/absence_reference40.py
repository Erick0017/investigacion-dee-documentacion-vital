"""Original CPC7 preparation, official installed4.0, passive finite telemetry.

Only the constructor sources are imported, not a historical runner. Inputs are
the predeclared frozen panel; all comparisons belong to a later instrument.
"""
from array import array
import argparse
import hashlib
import json
from pathlib import Path
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(world):
    r=world.runtime
    return {"tick":int(r.current_tick),
        "raw_sha256":hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),
        "clock_sha256":hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True)
    p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    import dee_thinking as d
    assert d.__version__=='4.0.0' and Path(d.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    sys.path.insert(0,str(a.source.resolve()));sys.path.insert(0,str((a.source/'endogenous').resolve()))
    import order_memory
    import comparison_need_v2 as apparatus
    import common
    config=json.loads(a.config.read_text(encoding='utf8'))
    result={"schema":"DEE4.5.absence-baseline40.v1","version":d.__version__,"module":d.__file__,
        "native_sha256":sha(d._native.__file__),"config_sha256":sha(a.config),"source_hashes":{
            str(x.relative_to(a.source)):sha(x) for x in (a.source/'order_memory.py',a.source/'common.py',
                a.source/'endogenous/comparison_need.py',a.source/'endogenous/comparison_need_v2.py')},"cases":[]}
    for case in config['cases']:
        body=order_memory.prepare_geometry(center=(33,25,33))
        adapter=apparatus.prepare_geometry(origin=body['geometry']['emission_site'])
        recipe=d.OrganizationRecipe.research(67,body['placements']+adapter['placements'],0)
        recipe.interfaces=body['interfaces']+adapter['interfaces'];recipe.execution=d.TickOptions(d.Backend.LAZY,1)
        world=d.OrganizationalWorld.create(recipe);requests=[];frames=[];rows=[]
        def stimulate(entries):
            for q in entries:
                r=getattr(world,q.get('kind','submit'))(q['port'],q['payload'],q['tick'])
                requests.append({**q,'kind':q.get('kind','submit'),'id':int(r.id)})
        stimulate(order_memory.experience(case['history']))
        stimulate([{'port':'order.read','payload':7,'tick':2,'kind':'probe'}])
        stimulate(apparatus.source_protocol(adapter['geometry'],case['source_value'],case['source_mode']))
        stimulate(apparatus.use_protocol(adapter['geometry']))
        for tick in (0,5,15,19,24,29,35):
            world.run_until(tick)
            if tick==5 and case['actual'] is not None:stimulate(apparatus.actual_protocol(adapter['geometry'],case['actual']))
            frames.append(digest(world));rows.append(apparatus.capture(world,adapter['geometry']))
        receipts=[]
        for q in requests:
            r=world.runtime.receipt(q['id']);receipts.append({"port":q['port'],"payload":q['payload'],"tick":q['tick'],"kind":q['kind'],
                "status":str(r.status),"effective_tick":None if r.effective_tick is None else int(r.effective_tick),"reason":r.reason})
        item={"case":case,"frames":frames,"rows":rows,"requests":sorted(receipts,key=lambda q:(q['tick'],q['port'],q['kind']))}
        result['cases'].append(item)
        (a.out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    result['status']='EXECUTED';(a.out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'status':'EXECUTED','cases':len(result['cases'])}))


if __name__=='__main__':main()
