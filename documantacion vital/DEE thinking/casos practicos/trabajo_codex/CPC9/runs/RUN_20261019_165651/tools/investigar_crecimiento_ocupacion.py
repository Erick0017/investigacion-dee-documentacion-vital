"""Diagnostic replay of an unexpected occupation wave, never E1 cognition.

Find first semantic7 birth after a saved frontier, preserve exact Moore27
before/after, reconstruct the bounded native branch, then cut one neighbour
only in an auditor fork. No predictions from this branch return to MAIN.
"""
from pathlib import Path
from copy import deepcopy
from collections import Counter
import argparse,gc,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
from vida_repertorio_extension import MainWithRepertoire
from integracion.relational_pair import physical
from audit_primary import one_step
from ejecutar_retorno import write
def coordinate(i):return[i//(67*67),(i//67)%67,i%67]
def decode(raw,clock,q,tick):
    v=[(raw>>shift)&15 for shift in(48,52,56)];v=[x-16 if x>=8 else x for x in v]
    return{'tick':tick,'site':q,'raw':str(raw),'clock':str(clock),'state':raw&0xffffffff,'s_reg':(raw>>32)&65535,'semantic':(raw>>60)&15,'direction':v,'active':bool(raw&0xffffffff)}
def neighbours(raw,clocks,q,t):
    out=[]
    for x in(-1,0,1):
        for y in(-1,0,1):
            for z in(-1,0,1):
                pos=[(q[0]+x)%67,(q[1]+y)%67,(q[2]+z)%67];i=(pos[0]*67+pos[1])*67+pos[2]
                out.append(decode(raw[i],clocks[i],pos,t))
    return out
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    source=ROOT/'resultados/continuacion/E1_MAIN_K65_1907_2353';original=json.loads((source/'MEDICIONES.json').read_text())
    parent_path=source/'T2219.deetsnap.gz';s=MainWithRepertoire.load(parent_path)
    result={'schema':'CPC9.occupation_wave.diagnostic.v1','preparations':0,'technical_replays':1,'diagnostic_forks':2,
      'parent':str(parent_path.relative_to(ROOT)),'parent_sha256':hashlib.sha256(parent_path.read_bytes()).hexdigest(),
      'predictions_before_evolution':'Replay actual2353; locate onset of new semantic7, not a memory-cap or electrical-energy claim. Cutting one actual opposite-neighbour symmetry member should prevent that local XNOR birth; global outcome is not assumed.',
      'profile':[],'first_birth':None,'rows':[],'status':'PREDICTED'}
    write(a.out/'MEDICIONES.json',result);pre_raw=s.world.runtime.raw_copy();pre_clock=s.world.runtime.clock_copy();saved=False;parent=None
    if any(((v>>60)&15)==7 for v in pre_raw):raise ValueError('Declared start already contains semantic7; choose earlier documented frontier')
    for tick in range(2220,2354):
        if not saved:
            # A cheap in-memory physical fork is delayed until the candidate
            # empty-cell symmetry can be located from current RAW. This copy
            # has no effect on the main replay and is never returned to it.
            candidates=[]
            # Only sources of an actual upcoming semantic7 can be confirmed
            # retrospectively, so preserve one bounded pre-tick world fork.
            candidate=s.world.fork()
        s.run_until(tick);raw=s.world.runtime.raw_copy();clock=s.world.runtime.clock_copy()
        sem=Counter((v>>60)&15 for v in raw);occupied=sum(bool(v&0xffffffff)for v in raw)
        result['profile'].append({'tick':tick,'occupied_state_gt0':occupied,'semantic7':sem.get(7,0),'max_s_reg':max((v>>32)&65535 for v in raw)})
        if not saved and sem.get(7,0):
            index=next(i for i,v in enumerate(raw)if((v>>60)&15)==7 and((pre_raw[i]>>60)&15)!=7);q=coordinate(index)
            before=neighbours(pre_raw,pre_clock,q,tick-1);post=decode(raw[index],clock[index],q,tick);pred=one_step(before)
            result['first_birth']={'pre_tick':tick-1,'tick':tick,'site':q,'pre_Moore27':before,'post':post,'reconstructed':pred,
              'exact_local_match':pred['raw']==post['raw']and pred['clock']==post['clock']}
            parent=MainWithRepertoire(candidate,deepcopy(s.geometry),deepcopy(s.state),s.identifier)
            # State only keeps operative requests/aliases; no future result is
            # inserted. The fork's physical tick/queue remain the pre-tick state.
            checkpoint=a.out/f'T{tick-1}_PRE_FIRST_BIRTH.deetsnap.gz';parent.save(checkpoint)
            result['first_birth']['checkpoint']=checkpoint.name;saved=True
            if not result['first_birth']['exact_local_match']:raise AssertionError('First-birth local reconstruction mismatch')
        elif not saved:del candidate
        pre_raw,pre_clock=raw,clock
        if tick%10==0 or tick==2353:write(a.out/'MEDICIONES.json',result)
    result['replay_final_physical']=physical(s.world);result['replay_exact2353']=physical(s.world)==original['final_physical']
    if not result['replay_exact2353']:raise AssertionError('Pure passive replay changed original future')
    del s,pre_raw,pre_clock;gc.collect()
    if parent is not None:
        first=result['first_birth'];victim=next(q for q in first['pre_Moore27']if q['site']!=first['site']and q['active']and q['semantic']!=5)
        for condition in('cut_symmetry_member','sham_symmetry_member'):
            edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*victim['site']);edit.raw=0 if condition.startswith('cut')else int(victim['raw']);edit.clock=None;edit.label=condition
            world=parent.world.diagnostic_fork([edit],True);child=MainWithRepertoire(world,parent.geometry,parent.state,parent.identifier)
            child.run_until(first['tick']);actual=child.observe(first['site']);first_stats={'birth_prevented':actual['semantic']!=7,'actual':actual}
            child.run_until(2353);raw=world.runtime.raw_copy();counts={'occupied_state_gt0':sum(bool(v&0xffffffff)for v in raw),'semantic7':sum(((v>>60)&15)==7 for v in raw)}
            row={'condition':condition,'victim':victim,'first_target':first_stats,'final2353':counts,'physical':physical(world),'full_original_equal':physical(world)==original['final_physical']}
            result['rows'].append(row);write(a.out/'MEDICIONES.json',result);del child,world,raw;gc.collect()
        if not result['rows'][1]['full_original_equal']:raise AssertionError('Sham failed exact native future')
    result['status']='MEASURED';write(a.out/'MEDICIONES.json',result)
    print(json.dumps({'status':result['status'],'first_birth':None if not saved else(result['first_birth']['tick'],result['first_birth']['reconstructed']['branch']),
        'exact2353':result['replay_exact2353'],'cut_and_sham':[(x['condition'],x['first_target']['birth_prevented'],x['final2353'])for x in result['rows']]}))
if __name__=='__main__':main()
