"""PreT0 physical guards for unused negative-Z opportunity mediators.

Guard placement is fixed for every possible branch, never selected from a
later result. A normalizer trajectory is a prediction until its local records
are checked; the guard is not presumed to absorb anything by its name.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parent))
import comparison_need as base


def prepare_geometry(need_geometry,mode='barrier',intercept_tick=22):
    import dee_thinking as d
    if mode not in ('none','counterflow','counterflow_sham','barrier','barrier_sham'):raise ValueError('Declared finite guard mode')
    g=need_geometry;n=g['N'];norm=(0,1,-1);placements=[];guards={};occupied=set()
    if n!=67 or intercept_tick!=22:raise ValueError('First regulation cut N67 and counterflow interception22')
    for key,b in g['branches'].items():
        # v2 missing-actual mediators have Z=0 and never descend into the
        # lexical planes; this guard covers only the four original branches.
        if b['comparison_direction'][2]!=1:continue
        q=b['request_site'];query_tick=g['ticks']['question']
        if mode.startswith('counterflow'):
            meet=base.moved(q,norm,intercept_tick-query_tick,n)
            direction=(0,-1,1);site=base.moved(meet,direction,-intercept_tick,n)
            semantic=1;state=1;meeting_tick=intercept_tick
        else:
            meet=base.moved(q,norm,4,n);site=meet;direction=(0,0,0);semantic=4;state=6100;meeting_tick=query_tick+4
        if mode.endswith('_sham'):site=base.moved(site,(0,0,1),9,n)
        if mode!='none':
            if site in occupied:raise ValueError('Guard placements overlap')
            occupied.add(site);p=d.InitialPlacement();p.site=d.Coordinate(*site)
            p.raw=d.pack_record(state,0,*direction,semantic);p.clock=0;p.role='Fixed preT0 unused-normalizer guard '+key+' '+mode;placements.append(p)
        guards[key]={'normalizer_direction':list(norm),'question_site':q,'nominal_interception_site':meet,
            'nominal_interception_tick':meeting_tick,'guard_initial_site':site if mode!='none' else None,
            'guard_direction':list(direction),'semantic':semantic if mode!='none' else None,
            'scope':'Current coordinates are declared; outcome and off-path status must be checked, not assumed.'}
    return {'placements':placements,'interfaces':[],'geometry':{'schema':'CPC7.need_regulation.v1','mode':mode,'N':n,'guards':guards,
        'guards_count':len(placements),'modality':'Fixed initial physical resources; no learned attention attribution',
        'known_geometry_risk':'Counterflow ballistic initial Z is21 for bodyZ42 and can cross lexical planes before interception. Local barrier initialZ42 has no moving prepared emitter.'}}
