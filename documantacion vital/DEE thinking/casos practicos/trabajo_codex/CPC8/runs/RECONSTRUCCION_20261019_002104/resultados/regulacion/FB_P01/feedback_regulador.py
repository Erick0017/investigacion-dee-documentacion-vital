"""Candidate: a native secondary comparison product becomes a later counterflow.

This is a fixed physical feedback path, not an optimizer or learned utility.
Its pulse content is not supplied by Python. The initial reference and first
counterflow still require declared experience. All three relay opportunities
are installed for both possible signs before any comparison.
"""
from dee_thinking import _native as d
from regulacion_adquirida import RegulatedQuantitySession,prepare_regulation
from cantidad_renovable import move
def prepare_feedback(center=(30,30,30),route='onpath'):
 r,g=prepare_regulation(center=center);ports=list(r.interfaces);c=g['center'];g['feedback_relays']=[]
 if route not in('onpath','offpath'):raise ValueError('Frozen route control')
 for sign in(-1,1):
  for index,(tick,offset,v)in enumerate(((75,(4*sign,-4,-4),(0,1,1)),(79,(8*sign,-4,-4),(0,1,1)),(83,(12*sign,0,0),(0,-1,-1)))):
   q=move(c,offset)
   if route=='offpath':q=move(q,(0,7,0))
   ch=d.ChannelSpec();name='feedback.'+str(sign)+'.'+str(index);ch.name=name;ch.injection_site=d.Coordinate(*move(q,v,-3));ch.direction=d.Direction(*v);ch.state=1;ch.semantic=1;ch.allow_probe=True;ch.allow_experience=True
   p=d.InterfaceSpec();p.name=name;p.channel=ch;ports.append(p);g['feedback_relays'].append({'sign_candidate':sign,'index':index,'target':q,'tick':tick,'port':name,'payload':0,'direction':list(v)})
 r.interfaces=ports;g['schema']='CPC8R.native_comparison_feedback.geometry.v1';g['route']=route;g['interfaces']=len(ports);g['feedback_scope']='Fixed allcandidate relay; a secondary comparisonproduct71 is transformed, not an externally injected correct regulation direction. No learned policy by utility claimed.'
 return r,g
class FeedbackSession(RegulatedQuantitySession):
 @classmethod
 def create(cls,**kw):r,g=prepare_feedback(**kw);return cls(d.OrganizationalWorld.create(r),g)
 def feedback_opportunities(self,enabled=True):
  if enabled:
   for r in self.geometry['feedback_relays']:self.input(r['port'],r['payload'],r['tick']-3)
 def first_regulation_experience(self):
  r=self.geometry['regulators'][0];self.input(r['cue_port'],5,0);self.input(r['event_ports']['-1'],11,0)
