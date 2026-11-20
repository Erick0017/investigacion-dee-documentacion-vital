"""Second opaque form, paired later with a renewed order-history expression.

Both candidate directions receive equal physical teaching/query pulses. This
tests an order-history function distinct from the received-data FORM_01.
No general temporal predicate or human deictic semantics is assumed.
"""
from common import interface,record
from order_memory import add

def prepare_geometry(body):
    r=add(body['center'],(0,0,-1));ports=[];items={}
    for h in (-1,1):
        key='negative' if h<0 else 'positive'
        hub=add(r,(10,10*h,-10));query=add(r,(10,20*h,-20))
        name='order_form.teach.'+key;read='order_form.query.'+key
        ports.append(interface(name,add(hub,(3,0,0)),(-1,0,0)))
        ports.append(interface(read,add(query,(-3,0,0)),(1,0,0)))
        items[key]={'teach_port':name,'query_port':read,'teach_site':list(hub),'query_site':list(query),'history_direction':h}
    return {'interfaces':ports,'geometry':{'schema':'CPC6.order_form.v1','items':items,'alias':'FORMA_02',
        'prepared_reader_tick':69,'native_history_emission_tick':70,'teach_request_tick':77,'teach_tick':80,
        'query_request_tick':87,'query_tick':90,
        'scope':'Fixed directional expression of distributed A/B event-order history, renewed before the second sign; not arbitrary ANTES/DESPUES or speaker roles.'}}

def teach(g,mode='paired'):
    if mode not in ('paired','unpaired','omitted'):raise ValueError('Unknown second-form teaching mode')
    if mode=='omitted':return []
    return [{'port':p['teach_port'],'payload':5,'tick':77+int(mode=='unpaired'),'kind':'submit',
              'origin':'LATER_SECOND_OPAQUE_SIGN_PAIRED_WITH_NATIVE_HISTORY_EXPRESSION'} for p in g['items'].values()]

def query(g,delay=0,payload=7):
    return [{'port':p['query_port'],'payload':payload,'tick':87+delay,'kind':'probe',
             'origin':'SECOND_SIGN_ONLY_EQUAL_BRANCH_PHYSICAL_QUERY'} for p in g['items'].values()]

def capture(world,g):
    return {'teaching':{k:record(world,p['teach_site']) for k,p in g['items'].items()},
            'queries':{k:record(world,p['query_site']) for k,p in g['items'].items()}}

def decode(observed):
    return [{'location':k,'physical':r,'history_direction':r['direction'][1],'provenance':'ENTE',
              'translation':'FORMA_02 reexpresa una dirección histórica '+str(r['direction'][1])}
            for k,r in observed['queries'].items() if r['active'] and r['semantic']==1 and
            r['direction'][0]==1 and r['direction'][1] in (-1,1) and r['direction'][2]==-1]
