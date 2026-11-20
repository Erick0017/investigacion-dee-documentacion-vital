"""Finite missing-actual path, added without changing the validated v1 source.

An expectation unmodified by an actual report remains in z=origin.z. A
predeclared directional mediator meets it at t19. An on-time actual instead
transduces the comparison into z+4 and avoids this fallback. No timeout or
host-read state selects the branch.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import interface
import comparison_need as base
from comparison_need import moved,actual_protocol,source_protocol,use_protocol,capture


def prepare_geometry(n=67,origin=(33,24,33),emission_tick=5,distance=10,prefix='need'):
    import dee_thinking as d
    result=base.prepare_geometry(n=n,origin=origin,emission_tick=emission_tick,distance=distance,prefix=prefix)
    placements=result['placements'];ports=result['interfaces'];g=result['geometry']
    occupied={(p.site.x,p.site.y,p.site.z) for p in placements}
    request=g['ticks']['question'];information=g['ticks']['information'];use=g['ticks']['use']
    for sign,lane in ((-1,'left'),(1,'right')):
        hub=g['comparison_hubs'][lane];expected_direction=(sign,-1,0)
        site=moved(hub,expected_direction,4,n);normalizer=(0,1,0)
        start=moved(site,normalizer,-request,n)
        if start in occupied:raise ValueError('Fallback source preparation overlaps')
        occupied.add(start);p=d.InitialPlacement();p.site=d.Coordinate(*start)
        p.raw=d.pack_record(1,13,*normalizer,1);p.clock=0;p.role='Finite internal missing-actual opportunity '+lane;placements.append(p)
        contact=moved(site,(sign,0,0),5,n);key=lane+'.missing_actual'
        g['branches'][key]={'lane':lane,'dx':sign,'request_site':site,'source_contact':contact,
            'comparison_direction':list(expected_direction),'trigger':'Expected carrier remains in original z plane only without current actual-induced transduction'}
        for value in (-1,1):
            dr=(0,value,0);data_hub=moved(contact,dr,-(information-3),n)
            source=f'{prefix}.source.{lane}.missing_actual.{value}'
            for label,direction in zip(('cue','event'),((1,0,0),(-1,value,0))):
                ports.append(interface(source+'.'+label,moved(data_hub,direction,-3,n),direction))
            g['source_codecs'][source]={'lane':lane,'value':value,'hub':data_hub,'direction':list(dr),'loads':[5,18],
                'source_contact':contact,'scope':'Extra separately experienced source ray, not a clone or correct answer'}
            target=moved(contact,(sign,value,0),5,n);name=f'{prefix}.use.{lane}.missing_actual.{value}'
            ports.append(interface(name,moved(target,(0,0,1),-3,n),(0,0,1)))
            g['later_queries'][name]={'site':target,'request_tick':use-3,'read_tick':use,'lane':lane,'value':value,
                'scope':'Common physical probe on every possible data route'}
    g['schema']='CPC7.native_need.comparison.v2'
    g['fallback']={'missing_actual':True,'criterion':'A represented expectation without the finite on-time actual report follows original-z route into the request opportunity.',
                   'timing':'Report is encoded at11 to arrive15. The branch tests this aperture, not all earlier/later events or unbounded absence.',
                   'extra_cost':'Two additional prepared mediators, two extra source cue/event pairs per current value, four later probes; inputs are explicitly enumerated.'}
    return result
