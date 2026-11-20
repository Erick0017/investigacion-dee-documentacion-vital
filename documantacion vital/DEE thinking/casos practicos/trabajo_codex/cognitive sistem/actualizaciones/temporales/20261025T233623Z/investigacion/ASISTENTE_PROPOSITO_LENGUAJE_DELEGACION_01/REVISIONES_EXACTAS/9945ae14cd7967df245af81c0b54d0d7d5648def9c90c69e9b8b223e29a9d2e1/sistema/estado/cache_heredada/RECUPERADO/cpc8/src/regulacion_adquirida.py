"""Native learned-direction counterflows, not a consequence-learning policy.

No on-path permanent output interceptors. Two mobile counterflows are acquired
by actual post-T0 contacts. Correct histories can annihilate the two products
that would return into quantity data. Their schedule/geometry is prepared.
"""
from copy import deepcopy
from dee_thinking import _native as d
from cantidad_renovable import QuantitySession,prepare,move
def prepare_regulation(center=(30,30,30)):
 r,g=prepare(center=center,guards='off_path');ports=list(r.interfaces);c=g['center'];g['regulators']=[]
 def port(name,q,v):
  ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*q);ch.direction=d.Direction(*v);ch.state=1;ch.semantic=1;ch.allow_probe=True;ch.allow_experience=True
  p=d.InterfaceSpec();p.name=name;p.channel=ch;ports.append(p)
 for i,(offset,t)in enumerate(((8,0),(25,100))):
  hub=move(c,(1,0,0),offset);prefix='regulator.'+str(i)
  port(prefix+'.cue',move(hub,(0,0,1),-3),(0,0,1))
  for sign,label in((-1,'minus'),(1,'plus')):port(prefix+'.event.'+label,move(hub,(sign,0,-1),-3),(sign,0,-1))
  g['regulators'].append({'id':i,'hub':hub,'teaching_tick':t,'first_memory_tick':t+3,'cue_port':prefix+'.cue','event_ports':{'-1':prefix+'.event.minus','1':prefix+'.event.plus'},'neutralization_site':move(c,(1 if i==0 else -1,0,0),4),'neutralization_tick':74+67*i})
 r.interfaces=ports;g['schema']='CPC8R.quantity.acquired_counterflows.geometry.v1';g['interfaces']=len(ports);g['regulation_scope']='R1: pulse direction acquired by experience, geometry/schedule prepared. Not R2strategy selected by consequences.'
 return r,g
class RegulatedQuantitySession(QuantitySession):
 @classmethod
 def create(cls,**kw):r,g=prepare_regulation(**kw);return cls(d.OrganizationalWorld.create(r),g)
 def regulation_experience(self,directions=(-1,1),mode='paired'):
  if len(directions)!=2 or any(v not in(-1,1)for v in directions)or mode not in('paired','unpaired','omitted'):raise ValueError('Declared regulation history')
  if mode=='omitted':return
  for r,sign in zip(self.geometry['regulators'],directions):
   t=r['teaching_tick'];self.input(r['cue_port'],5,t+int(mode=='unpaired'));self.input(r['event_ports'][str(sign)],11,t)
 def regulation_view(self):
  return[{'id':r['id'],'predicted_uninteracted_site':move(r['hub'],(s,0,0),self.tick-r['first_memory_tick']),'sign_candidate':s,'physical':self.observe(move(r['hub'],(s,0,0),self.tick-r['first_memory_tick']))}for r in self.geometry['regulators']for s in(-1,1)]
