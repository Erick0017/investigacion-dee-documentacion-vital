"""Explicit preparation compiler, NOT a participant memory/controller.

The invalid multi-opportunity R3 submitted identical fixtures simultaneously;
the official admission rule rejected ALL colliding copies. This new revision
requests each identical physical packet once and records logical aliases.
Non-identical collisions are NOT resolved. No expected response is available.
The proxy exists only while preparing, never during native execution.
"""
from . import saved,put

class SharedPreparation:
    def __init__(self,world):self.original=world;self.cache={};self.aliases=[];self.request_count=0
    def __getattr__(self,name):return getattr(self.original,name)
    def send(self,kind,port,payload,tick):
        spec=next(p.channel for p in self.original.interfaces if p.name==port)
        key=(kind,int(tick),spec.injection_site.x,spec.injection_site.y,spec.injection_site.z,int(spec.state),spec.direction.dx,spec.direction.dy,spec.direction.dz,int(spec.semantic),int(payload))
        self.request_count+=1
        if key in self.cache:
            rec,original_port=self.cache[key];self.aliases.append({'logical_port':port,'canonical_port':original_port,'id':int(rec.id),'tick':int(tick),'physical_key':list(key),'scope':'Identical physical preparation packet only; not a selected answer or a learner memory'});return rec
        rec=getattr(self.original,kind)(port,payload,tick);self.cache[key]=(rec,port);return rec
    def submit(self,port,payload,tick):return self.send('submit',port,payload,tick)
    def probe(self,port,payload,tick):return self.send('probe',port,payload,tick)

def prepare(a,*,builder='native_body',b_tail_guard='none',**options):
    if builder=='native_body':
        from .habitat_nativo import prepare as factory
    elif builder=='direct_failure':
        from .fallo_y_consulta import prepare as factory
    else:raise ValueError('Explicit candidate architecture, not host answer-selected builder')
    original=a.world;tick=a.tick;proxy=SharedPreparation(original)
    try:
        a.world=proxy;tail=None
        if b_tail_guard not in('none','native','sham'):raise ValueError('Explicit B query-tail preparation only')
        if b_tail_guard!='none':
            from capacidades.integracion_situada_01 import ic_native_core as n
            B=list(a.transferred_quantity.geometry['center']);site=n.move(B,(0,0,1),4)
            if b_tail_guard=='sham':site=n.move(site,(1,0,0),19)
            before=n.obs(a,site)
            if before['state']==1 and before['semantic']==4 and before['direction']==[0,0,0]:tail={'site':site,'existing_support':True,'pre':before}
            else:tail={'site':site,'pre':before,'request':n.submit(a,'MI01.compile.'+options['name']+'.B_tail_guard',site,(0,0,0),a.tick,0,4)}
        result=factory(a,**options)
        if a.tick!=tick:raise AssertionError('Preparation compiler must not evolve a life')
    finally:a.world=original
    record={'revision':'MI01.shared_preparation.r2','logical_requests':proxy.request_count,'unique_physical_requests':len(proxy.cache),'identical_aliases':proxy.aliases,'native_ticks_during_compilation':0,'b_tail_guard':b_tail_guard,'tail_preparation':tail,
       'not_claimed':'This is an external correction of duplicate physical requests. It is not learned regulation, filtering by usefulness, modified kernel admission, exact reproduction of invalid R3, or zero-cost material copying.'}
    cfg=saved(a);cfg['native_habitats'][options['name']]['input_compilation']=record;put(a,cfg);result['input_compilation']=record;return result
