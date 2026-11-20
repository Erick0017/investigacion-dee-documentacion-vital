"""Prepared opportunities for one longitudinal U0, never a trained body."""
from integrated import create
from common import interface,record,digest
from order_memory import add

def new_individual(backend='LAZY'):
    s=create(backend=backend,consolidation='open')
    before=digest(s.world)
    for name,body in (('original',s.geometry['body']),('consolidated',s.geometry['consolidation'])):
        site=add(body['center'],(0,0,-1))
        port='renewed.'+name
        s.world.declare_interface(interface(port,site,(0,0,-1)))
        s.geometry.setdefault('renewed_interfaces',{})[name]={'port':port,'site':list(site),'direction':[0,0,-1],
           'mode':'Predeclared T0 inert access, physical consumable probe, not an automatic phase repair'}
    assert digest(s.world)==before
    return s

def query(s,name,tick,payload=11):
    item=s.geometry['renewed_interfaces'][name]
    return [{'port':item['port'],'payload':payload,'tick':tick,'kind':'probe','origin':'RENEWED_PHYSICAL_QUERY_NO_RETEACHING'}]

def capture(s):
    return {k:record(s.world,p['site']) for k,p in s.geometry.get('renewed_interfaces',{}).items()}
