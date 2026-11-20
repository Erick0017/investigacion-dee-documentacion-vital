"""Directed archival replay plus a reserved inverse-history contrast at saturation."""
from array import array
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import dee_thinking as d
from laboratorio import *
from sesion import Session


def main(root):
    e=CaseEvidence(root,'SATURATION_OBSERVERS',{'recorded_before_run':True,'references':[[12,16],[16,12]],'common_inputs':[4000]*6,'future_common_input':0,
        'modalities':['NATIVE_EVOLUTION','EXPERIENCE_PROTOCOL','PASSIVE_OBSERVATION'],'scope':'complete-state distinction is scientist-only, not privileged access for the organization',
        'first_history_replay_is_not_new_replicate':True})
    worlds=[];rows=[]
    for refs in [(12,16),(16,12)]:
        s=Session.create(slots=16);s.experience(0,*refs);s.advance_to(6)
        for k in range(6):s.schedule(4000,k,'environment_experience');s.advance_to(11+5*k)
        s.save(e.folder/('SATURATED_'+str(refs[0])+'.deetsnap'));rows.append({'references':refs,'primary_outputs':s.state['frames'][-1]['outputs'],'frames':s.state['frames'],'physical':physical(s.world)});worlds.append(s)
    raw=[s.world.runtime.raw_copy() for s in worlds];clk=[s.world.runtime.clock_copy() for s in worlds];diff=[i for i,(a,b) in enumerate(zip(*raw)) if a!=b]
    samples=[]
    for i in diff[:32]:
        n=34;q=d.Coordinate(i//(n*n),(i//n)%n,i%n);samples.append({'site':coord(q),'history12':reading(worlds[0].world.runtime.observe(q)),'history16':reading(worlds[1].world.runtime.observe(q))})
    for s in worlds:s.schedule(0,6,'signal');s.advance_to(41)
    future={'primary':[s.state['frames'][-1]['outputs'] for s in worlds],'complete_physical':[physical(s.world) for s in worlds]}
    return e.finish({'histories':rows,'different_RAW_sites':len(diff),'different_clocks':sum(a!=b for a,b in zip(*clk)),
        'local_examples_of_distinction':samples,'future_common_query':future,
        'interpretation_scope':'equal primary output does not imply complete physical convergence; native accessibility beyond the declared panel remains to be tested'})

if __name__=='__main__':print(json.dumps({'status':main(sys.argv[1])['status']},indent=2))
