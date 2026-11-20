"""Research: fixed remote reader supply rather than clearing an occupied port.

Every FORM_01 request stimulates the SAME two remote interfaces, independent of
history/value. Native propagation takes44ticks to reach the two Q-store readers.
This is an explicit additional physical query resource, not an inferred answer.
"""
from common import interface,record,digest
from order_memory import add

def prepare(s):
    if 'left' not in s.geometry['consolidation']:raise ValueError('Bilateral receiver required')
    w=s.world;before=digest(w);parts={}
    for name,body in (('right',s.geometry['consolidation']),('left',s.geometry['consolidation']['left'])):
        target=add(body['center'],(0,0,-1));site=add(target,(0,0,-44));port='word_bus.'+name
        w.declare_interface(interface(port,site,(0,0,1)))
        parts[name]={'port':port,'source':list(site),'target':list(target),'direction':[0,0,1],
                     'native_delay':44,'center':body['center']}
    assert digest(w)==before
    s.geometry['word_bus']={'schema':'CPC6.remote-reader.v1','parts':parts,
        'scope':'Fixed additional long-latency physical supply for both candidate memories. Native field response and admission must be measured; no renewable-language claim assumed.'}

def protocol(s,delay=0,payload=7):
    return [{'port':p['port'],'payload':payload,'tick':50+delay,'kind':'probe',
             'origin':'FIXED_FORM01_REMOTE_READER_SUPPLY_NATIVE_DELAY44'} for p in s.geometry['word_bus']['parts'].values()]

def capture(s):
    return {name:{'source':record(s.world,p['source']),'target':record(s.world,p['target'])}
            for name,p in s.geometry['word_bus']['parts'].items()}

def decode(observed):
    return [{'location':name,'physical':p['target'],'directional_relation':-p['target']['direction'][0],
              'provenance':'ENTE','interpretation':'Fixed polarity read of a native basal response; compare no-repeat and unpaired controls.'}
            for name,p in observed.items() if p['target']['active'] and p['target']['semantic']==1 and
            p['target']['direction'][0] in (-1,1) and p['target']['direction'][2]==-1]
