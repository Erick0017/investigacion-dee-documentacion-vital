"""Native comparison from A teaches initially unassociated receiver B.

A's actually compared object marker travels3ticks to B. Fixed opaque cue Z-1
captures it into (a,y,0). The SAME cue later queries B. Context enters by a
declared fixed sensor before a physical delivery. No host output->input copy.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from relaciones.mode_reference import prepare_geometry,ModeReferenceSession,move
def prepare_social_geometry(**kw):
 kw['cleanup']=True;recipe,g=prepare_geometry(**kw);n=g['N'];ports=list(recipe.interfaces);signatures=g['signatures'];receivers=[]
 prefix=g.get('port_prefix','')
 def port(name,q,v,state=1):
  name=prefix+name;c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*q);c.direction=d.Direction(*v);c.state=state;c.semantic=1;c.allow_experience=True;c.allow_probe=True
  p=d.InterfaceSpec();p.name=name;p.channel=c;ports.append(p);signatures[name]=[list(q),list(v),state,1];return name
 for q in g['queries']:
  if q['stage']!=2:continue
  a=q['parent']['a'];hub=q['parent']['hub']
  for y in(0,a):
   tag='receiver.a'+str(a)+'.y'+str(y);r=move(hub,(a,y,1),3,n);cue=port(tag+'.opaque',move(r,(0,0,-1),-1,n),(0,0,-1),59)
   cp=move(r,(a,y,-1),5,n);contexts={str(c):port(tag+'.context.'+str(c),move(cp,(0,c,0),-1,n),(0,c,0),61) for c in(-1,1)}
   deliveries={str(c):{'site':move(cp,(a,(y+c>0)-(y+c<0),-1),3,n),'direction':[a,(y+c>0)-(y+c<0),-1]} for c in(-1,1)}
   receivers.append({'id':tag,'reference_axis':a,'compared_y':y,'memory_site':r,'teach_tick':160,'query_tick':227,'cue_port':cue,'context_tick':232,'context_site':cp,'context_ports':contexts,'delivery_tick':235,'deliveries':deliveries})
 g['communication']={'schema':'CPC8R.mode_communication.geometry.v1','receivers':receivers,'participants':{'A':'Acquired native reference and comparator; product leavesA after second comparison157.','B':'Initially unassociated fixed receiving opportunities. Physical product A is paired with an opaque cue160, queried227 and used with accessible context232.'},'payload_origin':'Native product of acquired reference plus current novel object; never host classified.','word_scope':'Opaque request for the physically retained comparison profile; not arbitrary universal synonym dictionary.','query_effect':'Query consumes Z0 memory into a moving Z-1 response; no indefinite reusable B claim.'}
 g['resources']['interfaces']=len(ports);recipe.interfaces=ports;recipe.options={'CPC8R.mode_reference.geometry':encode_metadata(g)}
 return recipe,g
class ModeCommunicationSession(ModeReferenceSession):
 @classmethod
 def create(cls,**kw):
  recipe,g=prepare_social_geometry(**kw);return cls(d.OrganizationalWorld.create(recipe),g)
 def prepare_normalizers(self):
  full=self.geometry['branches'];self.geometry['branches']=[b for b in full if b['stage']==1]
  try:super().prepare_normalizers()
  finally:self.geometry['branches']=full
 def teach_form(self,mode='paired',payload=5):
  if mode not in('paired','unpaired','omitted'):raise ValueError('Teaching mode')
  if mode!='omitted':
   for r in self.geometry['communication']['receivers']:self.input(r['cue_port'],payload,r['teach_tick']-1+(5 if mode=='unpaired' else 0),'OPAQUE_FORM_AFTER_NATIVE_COMPARISON_NOT_HOST_CLASS')
 def query_receiver(self,payload=7,enabled=True):
  if enabled:
   for r in self.geometry['communication']['receivers']:self.input(r['cue_port'],payload,r['query_tick']-1,'SAME_OPAQUE_FORM_QUERY_TO_ALL_FIXED_RECEIVING_OPPORTUNITIES','probe')
 def present_context(self,c,payload=11):
  if c not in(-1,1):raise ValueError('Actual finite context')
  for r in self.geometry['communication']['receivers']:self.input(r['context_ports'][str(c)],payload,r['context_tick']-1,'CURRENT_CONTEXT_SENSOR_NOT_CORRECT_ACTION')
 def capture(self,tick):
  super().capture(tick)
  if 'social_captures' not in self.state:self.state['social_captures']=[]
  for r in self.geometry['communication']['receivers']:
   if tick==r['query_tick']:
    p=self.observe(r['memory_site']);v=p['direction'];covered=p['active'] and v[0] in(-1,1) and v[2]==-1 and v[1] in(0,v[0])
    self.state['social_captures'].append({'tick':tick,'receiver':r['id'],'phase':'FORM_QUERY','physical':p,'covered':covered,'relation':('DIFFERENT_MODE' if v[1]==0 else 'LIKE_REFERENCE_MODE') if covered else None,'origin':'ENTE_NATIVE_RESPONSE'})
   if tick==r['context_tick']:self.state['social_captures'].append({'tick':tick,'receiver':r['id'],'phase':'CONTEXT_CONTACT','physical':self.observe(r['context_site']),'origin':'INSTRUMENTO_EXACT_STATE'})
   if tick==r['delivery_tick']:
    for c,target in r['deliveries'].items():self.state['social_captures'].append({'tick':tick,'receiver':r['id'],'phase':'DELIVERY','context_candidate':int(c),'physical':self.observe(target['site']),'origin':'INSTRUMENTO_EXACT_STATE'})
 def run_until(self,tick):
  critical={160,227,232,235};critical.update(q['parent']['query_tick'] for q in self.geometry['queries']);critical.update(b[k] for b in self.geometry['branches'] for k in('first_tick','second_tick'))
  for t in sorted(x for x in critical if self.tick<x<=tick):self.world.run_until(t);self.capture(t)
  self.world.run_until(tick)
