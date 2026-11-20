"""Fixed guards for residual mediators AND uncombined duplicated sensors.

This version adds four resources to v2. It does not promise to contain later
legitimate query products or every toroidal return; those are scanned separately.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import need_regulation_v2
from comparison_need import moved


def prepare_geometry(need_geometry,mode='barrier',intercept_tick=22):
    import dee_thinking as d
    if mode not in ('barrier','barrier_sham'):raise ValueError('V3 publishes local material guard and matched off-plane sham')
    prep=need_regulation_v2.prepare_geometry(need_geometry,mode=mode,intercept_tick=intercept_tick)
    g=prep['geometry'];n=need_geometry['N'];used={(p.site.x,p.site.y,p.site.z) for p in prep['placements']}
    for lane,hub in need_geometry['comparison_hubs'].items():
        for actual in (-1,1):
            direction=(-actual,0,1);target=moved(hub,direction,8,n)
            site=moved(target,(0,0,1),9,n) if mode.endswith('_sham') else target
            if site in used:raise ValueError('Guard resources overlap')
            used.add(site);p=d.InitialPlacement();p.site=d.Coordinate(*site)
            p.raw=d.pack_record(6100,0,0,0,0,4);p.clock=0;p.role='PreT0 unused actual-report absorber '+lane+'.'+str(actual);prep['placements'].append(p)
            key=lane+'.actual.'+str(actual)
            # Treat tick19 as the common replay origin: the report that never
            # encountered an expectation has already travelled four steps.
            replay_origin=moved(hub,direction,4,n)
            g['guards'][key]={'normalizer_direction':list(direction),'question_site':replay_origin,
                'nominal_interception_site':target,'nominal_interception_tick':need_geometry['ticks']['comparison']+8,
                'guard_initial_site':site,'guard_direction':[0,0,0],'semantic':4,'kind':'uncombined_current_actual_report',
                'scope':'Guard exists for both actual alternatives in both lanes, not selected from actual or hidden target.'}
    g.update({'schema':'CPC7.need_regulation.v3','guards_count':len(prep['placements']),
        'extension':'Four extra fixed absorbers on possible uncombined actual-report paths at comparison+8.',
        'residual_limits':'Later physical probes/products with nonzero Z may still wrap into lexical planes. Global unpacked records at35..100 test remaining traffic.'})
    return prep
