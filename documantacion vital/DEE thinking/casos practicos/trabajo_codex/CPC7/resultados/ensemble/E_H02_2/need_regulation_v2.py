"""Deduced local guard correction: intercept after eight residual steps.

Version1's equal-branch four-step location equals the comparison hub itself.
That adverse result remains. This version moves only the fixed barrier farther
down the unused ray, before it reaches lower lexical planes.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import need_regulation as previous
from comparison_need import moved


def prepare_geometry(need_geometry,mode='barrier',intercept_tick=22):
    import dee_thinking as d
    if mode not in ('barrier','barrier_sham'):
        return previous.prepare_geometry(need_geometry,mode=mode,intercept_tick=intercept_tick)
    n=need_geometry['N'];placements=[];guards={};norm=(0,1,-1);distance=8
    for key,b in need_geometry['branches'].items():
        if b['comparison_direction'][2]!=1:continue
        meet=moved(b['request_site'],norm,distance,n);site=moved(meet,(0,0,1),9,n) if mode.endswith('_sham') else meet
        p=d.InitialPlacement();p.site=d.Coordinate(*site);p.raw=d.pack_record(6100,0,0,0,0,4);p.clock=0
        p.role='PreT0 local residual absorber v2 '+key+' '+mode;placements.append(p)
        guards[key]={'normalizer_direction':list(norm),'question_site':b['request_site'],
            'nominal_interception_site':meet,'nominal_interception_tick':need_geometry['ticks']['question']+distance,
            'guard_initial_site':site,'guard_direction':[0,0,0],'semantic':4,
            'scope':'Fixed barrier at residual step8; does not mean the kernel must absorb its carrier.'}
    return {'placements':placements,'interfaces':[],'geometry':{'schema':'CPC7.need_regulation.v2','mode':mode,'N':n,
        'guards':guards,'guards_count':len(placements),'barrier_residual_steps':distance,
        'modality':'Fixed initial physical resources; no learned attention attribution',
        'correction':'The v1 equal branch barrier at+4 coincided with its comparison hub. At+8 it is four Chebyshev sites beyond that hub and intercepts at27.',
        'known_geometry_risk':'A local barrier can still affect other routes/guards. Compare actual native request/source/use and later integrated repertoire, not only disappearance on the nominal ray.'}}
