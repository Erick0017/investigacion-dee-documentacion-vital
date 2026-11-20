"""Later opaque sign exposures, with fixed symmetric physical encoding.

Words are interface aliases only. No history -> meaning dictionary is consulted.
The retained direction has to arrive through U0's received native information.
"""
from common import interface,record
from action_feedback import moved

def prepare_geometry(g):
    ports=[];items={};n=g['N'];t=g['ticks']['late_read']
    for late,p in g['late_queries'].items():
        v=p['value_direction'];start=p['site']
        hub=moved(start,(v,0,1),10,n)
        query=moved(hub,(v,-1,1),10,n)
        key=late.removeprefix('feedback.late.')
        name='language.teach.'+key;read='language.query.'+key
        ports.append(interface(name,moved(hub,(0,-1,0),-3,n),(0,-1,0)))
        ports.append(interface(read,moved(query,(0,1,0),-3,n),(0,1,0)))
        items[key]={'teach_port':name,'query_port':read,'teach_site':hub,'query_site':query,
                    'teach_request_tick':t+7,'teach_tick':t+10,'query_request_tick':t+17,
                    'query_tick':t+20,'value_direction':v,'native_information_path':late}
    return {'placements':[],'interfaces':ports,'geometry':{'schema':'CPC6.language.v1','items':items,
          'alias':'FORMA_01','encoding':'Simultaneous equal-dose pulses on every predeclared candidate lane; no lane chosen using history or decoder.',
          'scope':'Later opaque-sign association with a received directional relation, not a dictionary or 65 semantic meanings.'}}

def teaching(g,*,mode='paired',payload=5):
    if mode not in ('paired','unpaired','omitted'):raise ValueError('Unknown teaching mode')
    if mode=='omitted':return []
    return [{'port':p['teach_port'],'payload':payload,'tick':p['teach_request_tick']+int(mode=='unpaired'),
             'kind':'submit','origin':'LATER_OPAQUE_FORM_EQUAL_LANE_EXPERIENCE'} for p in g['items'].values()]

def query(g,*,payload=7,delay=0):
    return [{'port':p['query_port'],'payload':payload,'tick':p['query_request_tick']+delay,
             'kind':'probe','origin':'SIGN_ALONE_FIXED_CODEC_PHYSICAL_QUERY'} for p in g['items'].values()]

def capture(world,g):
    return {'teaching':{k:record(world,p['teach_site']) for k,p in g['items'].items()},
            'queries':{k:record(world,p['query_site']) for k,p in g['items'].items()}}

def decode(observed):
    # Physical decoder frozen before reserves; no known answer used to choose branch.
    return [{'location':k,'physical':r,'directional_relation':r['direction'][0],
             'provenance':'ENTE','translation':'FORMA_01 reexpresa una relación direccional '+str(r['direction'][0])}
            for k,r in observed['queries'].items()
            if r['active'] and r['semantic']==1 and r['direction'][0] in (-1,1) and r['direction'][1:]==[0,1]]
