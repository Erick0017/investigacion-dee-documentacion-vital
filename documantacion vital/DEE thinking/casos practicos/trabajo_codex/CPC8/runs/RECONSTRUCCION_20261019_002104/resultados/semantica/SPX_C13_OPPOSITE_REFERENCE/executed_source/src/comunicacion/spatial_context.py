"""Third actual spatial object supplies context through native gradients, not a sign sensor."""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from comunicacion.spatial_communication import prepare_spatial_social_geometry,SpatialCommunicationSession
from relaciones.spatial_gradient import sensor
from relaciones.mode_reference import move
def prepare_spatial_context_geometry(**options):
 recipe,g=prepare_spatial_social_geometry(**options);initial=list(recipe.placements);interfaces=list(recipe.interfaces);contexts=[];prefix=options.get('port_prefix','')+'actual_context.'
 def port(name,q,v,state):
  name=prefix+name;c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*q);c.direction=d.Direction(*v);c.state=state;c.semantic=1;c.allow_experience=True;c.allow_probe=True
  p=d.InterfaceSpec();p.name=name;p.channel=c;interfaces.append(p);return name
 for r in g['communication']['receivers']:
  for candidate in(-1,1):
   center=move(r['context_site'],(0,candidate,0),-9);center=move(center,(0,candidate,1),-2);initial+=sensor(center,[[0,-1,-1],[0,1,-1]])
   fmt=move(center,(0,candidate,1),2);name=r['id']+'.c'+str(candidate)
   objects={str(c):port(name+'.object.'+str(c),move(center,(0,-c,-1)),(0,0,-1),233)for c in(-1,1)}
   formatter=port(name+'.formatter',move(fmt,(0,0,-1),-1),(0,0,-1),1)
   contexts.append({'receiver':r['id'],'candidate':candidate,'center':center,'object_ports':objects,'object_tick':228,'gradient_tick':229,'formatter_site':fmt,'formatter_tick':231,'formatter_port':formatter,'arrival_site':r['context_site'],'arrival_tick':240})
 unique={};placements=[]
 for p in initial:
  key=(p.site.x,p.site.y,p.site.z)
  if key in unique:
   if (int(p.raw),int(p.clock))!=unique[key]:raise ValueError('Conflicting native context supports '+str(key))
  else:unique[key]=(int(p.raw),int(p.clock));placements.append(p)
 g['native_context']={'sensors':contexts,'scope':'Actual objects share the same Z− direction. Their actual Y/Z position creates a local native gradient. A fixed Z− formatter transports only Y to a context encounter. No program converts objectside into desired action.','object_copies':len(contexts),'old_external_context_ports':'Present but never stimulated in this candidate.'}
 g['resources']['initial_material']=len(placements);g['resources']['interfaces']=len(interfaces);g['resources']['sensor_count']+=len(contexts);recipe.placements=placements;recipe.interfaces=interfaces;recipe.options={'CPC8R.spatial_reference.geometry':encode_metadata(g)};return recipe,g
class SpatialContextSession(SpatialCommunicationSession):
 @classmethod
 def create(cls,**options):r,g=prepare_spatial_context_geometry(**options);return cls(d.OrganizationalWorld.create(r),g)
 def context_curriculum(self,a,b1,b2,context,*,reference='paired',loads=(11,11,19),form='paired',query=True,context_objects=True,current_stages=(1,2)):
  if context not in(-1,1):raise ValueError('Actual object position domain')
  super().social_curriculum(a,b1,b2,reference,loads,current_stages,form,None,query)
  for p in self.geometry['native_context']['sensors']:
   self.input(p['formatter_port'],0,p['formatter_tick']-1,'FIXED_ALL_CANDIDATE_Z_FORMATTER_NOT_SELECTED_BY_OBJECT_OR_RESPONSE')
   if context_objects:self.input(p['object_ports'][str(context)],11,p['object_tick'],'ACTUAL_THIRD_OBJECT_AT_POSITION_ALL_DIRECTIONS_Z_MINUS')
 def critical_ticks(self):return sorted(set(super().critical_ticks())|{229,231})
