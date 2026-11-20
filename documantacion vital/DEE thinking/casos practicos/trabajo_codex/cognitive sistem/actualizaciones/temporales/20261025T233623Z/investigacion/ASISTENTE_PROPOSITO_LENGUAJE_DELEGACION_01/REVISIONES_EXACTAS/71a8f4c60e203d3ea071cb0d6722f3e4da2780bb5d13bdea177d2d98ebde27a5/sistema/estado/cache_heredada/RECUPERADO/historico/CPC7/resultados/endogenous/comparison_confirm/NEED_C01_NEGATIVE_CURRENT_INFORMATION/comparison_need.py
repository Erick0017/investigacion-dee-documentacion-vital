"""Physical discrepancy emits a request; equal comparison emits no X request.

Preparation is adapted from CPC3 reflected comparison/information access.
Expectation is the actual learned order-body emission, not a computed answer.
This is an alternative adapter, not additive to CPC6 policy normalizers.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import interface,record


def moved(q,direction,count=1,n=67):
    return tuple((q[i]+direction[i]*count)%n for i in range(3))


def prepare_geometry(n=67,origin=(33,24,33),emission_tick=5,distance=10,prefix='need'):
    import dee_thinking as d
    if n!=67 or emission_tick!=5 or distance!=10:raise ValueError('Finite CPC7 first contract N67, emission5, distance10')
    placements=[];ports=[];hubs={};branches={};source_codecs={};later={};occupied=set()
    comparison=emission_tick+distance;request=comparison+4;information=request+5;use=information+5
    def place(q,load,direction,role):
        q=tuple(q)
        if q in occupied:raise ValueError('Overlapping need-adapter preparation '+str(q))
        occupied.add(q);p=d.InitialPlacement();p.site=d.Coordinate(*q)
        p.raw=d.pack_record(1,load,*direction,1);p.clock=0;p.role=role;placements.append(p)
    for sign in (-1,1):
        lane='left' if sign<0 else 'right';hub=moved(origin,(sign,-1,0),distance,n);hubs[lane]=hub
        for actual in (-1,1):
            direction=(-actual,0,1);name=f'{prefix}.actual.{lane}.{actual}'
            ports.append(interface(name,moved(hub,direction,-4,n),direction))
        for dx in (0,sign):
            key=lane+'.'+('equal' if dx==0 else 'different');direction=(dx,-1,1)
            site=moved(hub,direction,4,n);normalizer=(0,1,-1)
            place(moved(site,normalizer,-request,n),13,normalizer,'Prepared common request opportunity '+key)
            branch={'lane':lane,'dx':dx,'request_site':site,'comparison_direction':list(direction)}
            if dx:
                contact=moved(site,(sign,0,0),5,n);branch['source_contact']=contact
                for value in (-1,1):
                    data_direction=(0,value,0);data_hub=moved(contact,data_direction,-(information-3),n)
                    base=f'{prefix}.source.{lane}.{value}'
                    pair=((1,0,0),(-1,value,0))
                    for label,dr in zip(('cue','event'),pair):
                        ports.append(interface(base+'.'+label,moved(data_hub,dr,-3,n),dr))
                    source_codecs[base]={'lane':lane,'value':value,'hub':data_hub,'direction':list(data_direction),
                        'loads':[5,18],'source_contact':contact,'scope':'A current data carrier acquired by two real experience inputs'}
                    target=moved(contact,(sign,value,0),5,n);query_name=f'{prefix}.use.{lane}.{value}'
                    ports.append(interface(query_name,moved(target,(0,0,1),-3,n),(0,0,1)))
                    later[query_name]={'site':target,'request_tick':use-3,'read_tick':use,
                        'lane':lane,'value':value,'scope':'All alternatives receive the same later physical probe; no host routing by selected branch'}
            branches[key]=branch
    return {'placements':placements,'interfaces':ports,'geometry':{
        'schema':'CPC7.native_need.comparison.v1','N':n,'prefix':prefix,'origin':list(origin),
        'ticks':{'emission':emission_tick,'comparison':comparison,'question':request,'information':information,'use':use},
        'comparison_hubs':hubs,'branches':branches,'source_codecs':source_codecs,'later_queries':later,
        'incoming_contract':'Actual learned order-body carrier (s,-1,0) at origin5; never a predicted answer calculated here',
        'mechanism':'Comparison (dx,-1,1) + common opportunity(0,1,-1) produces (dx,0,0). Equal cancels X; discrepancy emits native horizontal request.',
        'limits':'Finite prepared opportunities. Missing represented expectation or missing actual report is outside singleton-comparison domain; no generic uncertainty detector.'}}


def actual_protocol(g,actual,payload=17):
    if actual not in (-1,1):raise ValueError('Current binary consequence required')
    return [{'port':f'{g["prefix"]}.actual.{lane}.{actual}','payload':payload,
             'tick':g['ticks']['comparison']-4,'kind':'submit','origin':'CURRENT_ACTUAL_EVENT_FIXED_CODEC'} for lane in ('left','right')]


def source_protocol(g,value=1,mode='paired'):
    if value not in (-1,1) or mode not in ('paired','unpaired','none'):raise ValueError('Finite actual-data source protocol')
    entries=[]
    if mode=='none':return entries
    for base,p in g['source_codecs'].items():
        if p['value']!=value:continue
        entries += [{'port':base+'.cue','payload':5,'tick':int(mode=='unpaired'),'kind':'submit','origin':'OPAQUE_DATA_SOURCE_CUE'},
                    {'port':base+'.event','payload':18,'tick':0,'kind':'submit','origin':'CURRENT_DIRECTIONAL_SOURCE_EVENT'}]
    return entries


def use_protocol(g,payload=7):
    return [{'port':name,'payload':payload,'tick':item['request_tick'],'kind':'probe','origin':'COMMON_PHYSICAL_USE_AFTER_INFORMATION'} for name,item in g['later_queries'].items()]


def capture(world,g):
    return {'tick':world.runtime.current_tick,
        'comparison':{k:record(world,q) for k,q in g['comparison_hubs'].items()},
        'questions':{k:record(world,b['request_site']) for k,b in g['branches'].items()},
        'source_contacts':{k:record(world,b['source_contact']) for k,b in g['branches'].items() if 'source_contact' in b},
        'later_use':{k:record(world,q['site']) for k,q in g['later_queries'].items()}}
