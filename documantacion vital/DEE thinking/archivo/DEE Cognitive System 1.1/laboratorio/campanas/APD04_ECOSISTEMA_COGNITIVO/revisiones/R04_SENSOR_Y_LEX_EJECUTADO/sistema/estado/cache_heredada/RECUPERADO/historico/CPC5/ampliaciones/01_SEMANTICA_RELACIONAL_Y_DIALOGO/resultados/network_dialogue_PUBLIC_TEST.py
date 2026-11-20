"""External public API installation/continuation check, not participant logic."""
from pathlib import Path
import argparse
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from network_session import NetworkSession,operative_without_framework_cache
from common import put,digest,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['create','continue']);p.add_argument('--out',type=Path,required=True);p.add_argument('--parent',type=Path);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    if a.mode=='create':
        s=NetworkSession.create(3)
        for actor in (1,2,3):
            s.experience(actor,'context',(5,11),-1 if actor%2 else 1,0)
            s.experience(actor,'memory',(3,9+2*(actor-1)),1,0)
            s.relay(actor,1,0);s.relay(actor,2,0)
            s.request(actor,13,50);s.resource(actor,7,72)
            s.support(actor,'memory',5,201);s.support(actor,'context',5,201)
        s.run_until(55);pre=s.save(a.out/'T55.deetsnap')
        s.run_until(75);banks=s.observe();s.save(a.out/'T75.deetsnap')
        s.run_until(204);final=s.save(a.out/'T204.deetsnap')
        expected=ROOT/'resultados/network_dialogue_screen/RING_A3/MEASUREMENTS.json'
        golden=json.loads(expected.read_text(encoding='utf-8'))
        equal=digest(s.world)==golden['final_physical']
        if not equal:raise AssertionError('Public interface changed native reference physics')
        ordinary,cache=operative_without_framework_cache(s.world)
        put(a.out/'PUBLIC_API.json',{'mode':'create','pre':pre,'banks':banks,'final':final,'observed':s.observe(),
               'reference_sha256':sha(expected),'whole_RAW_clocks_tick_equal_to_scientific_RingA3':equal,
               'operative_without_framework_cache':ordinary,'framework_cache':cache,
               'scope':'Technical reproduction via public methods, not an additional independent scientific preparation.'})
    else:
        s=NetworkSession.load(a.parent/'T55.deetsnap');s.run_until(204);final=s.save(a.out/'RESTORED_T204.deetsnap')
        golden=json.loads((a.parent/'PUBLIC_API.json').read_text(encoding='utf-8'))
        ordinary,cache=operative_without_framework_cache(s.world)
        equal=digest(s.world)==golden['final']['physical'];op_equal=ordinary==golden['operative_without_framework_cache']
        if not equal or not op_equal:raise AssertionError('Public network continuation changed physics/operative state')
        put(a.out/'CONTINUATION.json',{'mode':'other_process_continue','parent_sha256':sha(a.parent/'T55.deetsnap'),
                'whole_RAW_clocks_tick_equal':equal,'operative_except_opaque_framework_cache_equal':op_equal,
                'opaque_framework_cache_equal':cache==golden['framework_cache'],'final':final,'observed':s.observe(),
                'scope':'Comparison separates cached encoded framework envelope from complete physical state, channels, receipts, custom metadata and pending protocol state.'})

if __name__=='__main__':main()
