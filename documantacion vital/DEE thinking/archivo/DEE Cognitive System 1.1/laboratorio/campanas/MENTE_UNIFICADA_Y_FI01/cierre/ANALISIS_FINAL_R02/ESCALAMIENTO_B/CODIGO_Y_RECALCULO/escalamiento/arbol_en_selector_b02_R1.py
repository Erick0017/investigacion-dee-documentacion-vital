"""Prospective B02 coupling: raw tree to the EXISTING A selector's E-X.

No native import occurs at module level. No world is created, cleared, resized,
or trained here. enqueue() is gated by the real block-A closure. The host never
sums components, chooses a bank, or supplies an expected response. This file is
an unvalidated transport candidate, not a claim of functional native scaling.
"""
from __future__ import annotations
import argparse, gzip, hashlib, json
from pathlib import Path
from arbol_umbral_adquirido_b01 import plan as auxiliary_plan,internal_A_close,native_imports,memory_guard

HERE=Path(__file__).resolve().parent
REVISION='FI01.B02.shared_A_selector.raw_tree.r1'

def plan(level=128,E=(15,15,15),N=67):
    if N!=67:raise ValueError('This exact transport candidate is declared for N67 only; never resize a lived world')
    old=auxiliary_plan(level,N);D=tuple((E[i]+(-1,0,0)[i])%N for i in range(3))
    od=old['datum_site'];shift=[(D[i]-(od[1],od[2],od[0])[i])%N for i in range(3)]
    def xyz(q):return [(v+shift[i])%N for i,v in enumerate((q[1],q[2],q[0]))]
    def vector(v):return[v[1],v[2],v[0]]
    # Delete only obsolete OFFLINE geometry markers from the auxiliary plan.
    # This operation NEVER deletes physical material or edits any world.
    obsolete={tuple(old['Q']),*map(tuple,old['memories'])}
    obsolete.update(tuple((old['Q'][i]+(s,-1,-1)[i])%N for i in range(3))for s in(-1,0,1))
    opened={tuple(xyz(p))for p in old['opened']if tuple(p)not in obsolete}
    def src(q):
        r={**q,'site':xyz(q['site']),'direction':vector(q['direction'])}
        if 'head'in r:r['head']=xyz(r['head'])
        return r
    raw=[src(q)for q in old['raw_sources']];resources=[src(q)for q in old['generic_sources']]
    nodes=[{**q,'site':xyz(q['site'])}for q in old['nodes']]
    frame={(-1,-1,0),(1,-1,0),(0,1,1),(0,1,-1),(0,0,1),(-1,-3,0),(1,-3,0),(-1,-2,1),(1,-2,1),(2,1,2),(-2,0,0),(-3,3,0),(3,3,0)}
    frame.update((x,y,z)for x in(-2,2)for y in(-2,-1)for z in(-1,0,1))
    frame_sites={tuple((E[i]+v[i])%N for i in range(3))for v in frame}
    conflicts=opened&frame_sites
    if conflicts or tuple(E)in opened:raise ValueError('Direct path overlaps known selector frame/E: '+repr(sorted(conflicts)))
    return {'revision':REVISION,'level':level,'N':N,'E':list(E),'datum_site':list(D),
      'raw_sources':raw,'generic_sources':resources,'nodes':nodes,'opened':list(map(list,sorted(opened))),
      'raw_relative_tick':old['leaf_relative_tick'],'datum_relative_tick':36,
      'input_to_datum_ticks':old['planned_input_to_datum_ticks'],
      'fixed_final_approaches':[[0,0,1],[0,0,-1]],'known_frame_direct_conflicts':[],
      'learned_reference_sites':[[E[0]-1,E[1]-1,E[2]],[E[0]+1,E[1]-1,E[2]]],
      'classification':'OFFLINE_PLAN_ONLY_NO_NATIVE_TICKS',
      'caveat':'No route is deemed free from state=0. Existing full RAW/clocks/history and peripheral columns must be inspected without clearing. Neighbour coupling and toroidal returns remain unvalidated.'}

def enqueue(adapter,components,*,level=128,E=(15,15,15),leaf_tick=None,close_path=None,prefix='FI01.B02'):
    """Enqueue only: parent supplies its existing, fixed common selector query.

    Does not run_until/read a choice. Its admission, timing and frame effects
    belong to the parent's complete one-writer protocol and must be preserved.
    """
    authorization=internal_A_close(Path(close_path)if close_path else HERE.parent/'CIERRE_INTERNO_A.json')
    ni=native_imports();body=ni[-2]
    N=int(adapter.world.runtime.dimension);g=plan(level,E,N)
    if len(components)!=level or any(type(v)is not int or not 0<=v<=32 for v in components):raise ValueError('One actual raw scalar0..32 per physical component')
    if leaf_tick is None:leaf_tick=adapter.tick+2
    if leaf_tick<=adapter.tick:raise ValueError('Inputs must be strictly future environmental events')
    root_tick=leaf_tick-g['raw_relative_tick'];requests=[]
    for s in g['raw_sources']:
        requests.append(body.send(adapter,prefix+'.'+s['id'],s['site'],s['direction'],root_tick+s['injection_tick_relative'],components[s['component_index']]))
    for s in g['generic_sources']:
        requests.append(body.send(adapter,prefix+'.'+s['id'],s['site'],s['direction'],root_tick+s['injection_tick_relative'],0))
    memory_guard()
    return {'revision':REVISION,'authorization':authorization,'geometry':g,'leaf_tick':leaf_tick,
      'root_tick':root_tick,'datum_tick':root_tick+36,'requests':requests,
      'raw_components':components,'host_assistance':'Fixed spatial codec and zero-load turning resources. No aggregate value, expected action, bank selection, field clearing, reference write, or new Runtime.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--level',type=int,choices=(8,16,32,64,128),default=128);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    result={'classification':'OFFLINE_PREPARATION_ONLY','native_ticks':0,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'plan':plan(a.level)}
    data=json.dumps(result,ensure_ascii=False,indent=2).encode()
    if a.out.suffix=='.gz':
        with a.out.open('wb')as f:
            with gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0)as z:z.write(data)
    else:a.out.write_bytes(data)
    print(json.dumps({'out':str(a.out),'bytes':a.out.stat().st_size,'native_ticks':0,'sha256':hashlib.sha256(a.out.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
