"""Position-derived comparison teaches another region by native traveling product."""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from relaciones.spatial_reference import prepare_spatial_geometry,SpatialReferenceSession
from relaciones.mode_reference import move
def prepare_spatial_social_geometry(**options):
 recipe,g=prepare_spatial_geometry(**options);interfaces=list(recipe.interfaces);receivers=[]
 prefix=options.get('port_prefix','')+'spatial_receiver.'
 def port(name,q,v,state):
  name=prefix+name;c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*q);c.direction=d.Direction(*v);c.state=state;c.semantic=1;c.allow_experience=True;c.allow_probe=True
  p=d.InterfaceSpec();p.name=name;p.channel=c;interfaces.append(p);return name
 for label,mg in g['modes'].items():
  for q in mg['queries']:
   if q['stage']!=2:continue
   a=q['parent']['a'];hub=q['parent']['hub']
   for y in(0,a):
    tag=label+'.'+q['parent']['id']+'.y'+str(y);r=move(hub,(a,y,1),3);cue=port(tag+'.opaque',move(r,(0,0,-1),-1),(0,0,-1),59)
    cp=move(r,(a,y,-1),5);contextports={str(c):port(tag+'.context.'+str(c),move(cp,(0,c,0),-1),(0,c,0),61)for c in(-1,1)}
    deliveries={str(c):{'site':move(cp,(a,(y+c>0)-(y+c<0),-1),3),'direction':[a,(y+c>0)-(y+c<0),-1]}for c in(-1,1)}
    receivers.append({'id':tag,'reference_axis':a,'comparison_y':y,'memory_site':r,'teach_tick':168,'query_tick':235,'cue_port':cue,'context_tick':240,'context_site':cp,'context_ports':contextports,'delivery_tick':243,'deliveries':deliveries})
 g['communication']={'receivers':receivers,'participants':{'A':'Prepared spatial sensor array and physically acquired traveling reference.','B':'Eight initially unassociated receiving opportunities; only native message-dependent transformed memory is credited.'},'message':'Native comparison of experienced reference position with new current-object position; A output travels3ticks without a host read/write link.','word_scope':'Opaque request re-expressing acquired positional comparison profile; no free-language meaning or arbitrary dictionary claim.','query_effect':'B query consumes its Z0 acquired support into Z−1 packet; only finite published use, not unlimited conversation.'}
 g['resources']['interfaces']=len(interfaces);recipe.interfaces=interfaces;recipe.options={'CPC8R.spatial_reference.geometry':encode_metadata(g)};return recipe,g
class SpatialCommunicationSession(SpatialReferenceSession):
 @classmethod
 def create(cls,**options):r,g=prepare_spatial_social_geometry(**options);return cls(d.OrganizationalWorld.create(r),g)
 def social_curriculum(self,a,b1,b2,reference='paired',loads=(11,11,19),current_stages=(1,2),form='paired',context=1,query=True):
  super().curriculum(a,b1,b2,reference,loads,current_stages,normalization_stages=(1,))
  if form not in('paired','unpaired','omitted')or context not in(-1,1):raise ValueError('Frozen social modes')
  for r in self.geometry['communication']['receivers']:
   if form!='omitted':self.input(r['cue_port'],5,r['teach_tick']-1+(5 if form=='unpaired'else 0),'OPAQUE_FORM_AFTER_NATIVE_POSITIONAL_COMPARISON_NOT_A_CLASSIFICATION')
   if query:
    x=self.world.probe(r['cue_port'],7,r['query_tick']-1);self.state['requests'].append({'id':int(x.id),'port':r['cue_port'],'payload':7,'tick':r['query_tick']-1,'origin':'SAME_OPAQUE_REQUEST_TO_ALL_FIXED_RECEIVING_OPPORTUNITIES','kind':'probe'})
   self.input(r['context_ports'][str(context)],11,r['context_tick']-1,'CURRENT_CONTEXT_NOT_DESIRED_ACTION')
 def critical_ticks(self):return sorted(set(super().critical_ticks())|{168,235,240,243})
 def capture(self,tick):
  super().capture(tick);self.state.setdefault('social_captures',[])
  for r in self.geometry['communication']['receivers']:
   if tick==r['query_tick']:
    p=self.observe(r['memory_site']);v=p['direction'];requests=[x for x in self.state['requests']if x['port']==r['cue_port']and x['kind']=='probe'and x['tick']==tick-1]
    receipt=self.world.runtime.receipt(requests[-1]['id'])if requests else None;applied=receipt is not None and str(receipt.status)=='applied'
    covered=applied and p['active']and v[0]in(-1,1)and v[2]==-1 and v[1]in(0,v[0])
    self.state['social_captures'].append({'tick':tick,'receiver':r['id'],'phase':'FORM_QUERY','physical':p,'request_id':int(receipt.id)if receipt is not None else None,'request_applied':applied,'covered':covered,'relation':('DIFFERENT_Y_SIDE'if v[1]==0 else'LIKE_REFERENCE_Y_SIDE')if covered else None,'origin':'ENTE_NATIVE_RESPONSE'})
   if tick==r['context_tick']:self.state['social_captures'].append({'tick':tick,'receiver':r['id'],'phase':'CONTEXT_CONTACT','physical':self.observe(r['context_site']),'origin':'INSTRUMENTO_EXACT_STATE'})
   if tick==r['delivery_tick']:
    for c,target in r['deliveries'].items():self.state['social_captures'].append({'tick':tick,'receiver':r['id'],'phase':'DELIVERY','context_candidate':int(c),'physical':self.observe(target['site']),'origin':'INSTRUMENTO_EXACT_STATE'})
