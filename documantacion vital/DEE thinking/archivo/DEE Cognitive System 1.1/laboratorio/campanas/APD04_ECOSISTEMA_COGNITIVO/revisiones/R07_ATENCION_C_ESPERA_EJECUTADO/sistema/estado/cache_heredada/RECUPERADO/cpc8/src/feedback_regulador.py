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
 # Identified F1 failure: secondary direction71 pointed into a fixed observer,
 # so it was a field but NOT an emitted traveling record. Reposition the four
 # zero-load supports in the initial preparation only, preserving their count,
 # RAW/clocks and the first comparison gradient. No edit is applied to MAIN.
 placements=list(r.placements)
 for p in placements:
  q=[p.site.x,p.site.y,p.site.z];off=[((q[i]-c[i]+33)%67)-33 for i in range(3)]
  if abs(off[0])==1 and abs(off[1])==1 and off[1]==off[2]:
   p.site=d.Coordinate(q[0],q[1],(2*c[2]-q[2])%67);p.role='Prepared anti-diagonal zero-load support; permits secondary comparison transport'
 r.placements=placements;g['support_revision']='F2 four zero-load supports reflected acrossZ atT0. F1secondary field71 was blocked at72 by occupiedobserver, all F1states preserved.'
 if route not in('onpath','offpath'):raise ValueError('Frozen route control')
 for sign in(-1,1):
  # Second justified revision: F2's(+X)feedback reached28,30,30 at136,
  # but its intended destination29,30,30 was occupied by learnedreference36.
  # Passive F2diagnostic shows exact firstmiss137. Seven real Z-only steps
  # change the material flight phase; no clock is reset or edited.
  for index,(tick,offset,v)in enumerate(((75,(4*sign,-4,-4),(-sign,1,0)),(82,(4*sign,-4,-11),(sign,1,1)),(86,(8*sign,0,-11),(0,-1,1)),(97,(19*sign,0,0),(0,0,-1)))):
   q=move(c,offset)
   if route=='offpath':q=move(q,(0,7,0))
   ch=d.ChannelSpec();name='feedback.'+str(sign)+'.'+str(index);ch.name=name;ch.injection_site=d.Coordinate(*move(q,v,-3));ch.direction=d.Direction(*v);ch.state=1;ch.semantic=1;ch.allow_probe=True;ch.allow_experience=True
   p=d.InterfaceSpec();p.name=name;p.channel=ch;ports.append(p);g['feedback_relays'].append({'sign_candidate':sign,'index':index,'target':q,'tick':tick,'port':name,'payload':0,'direction':list(v)})
 r.interfaces=ports;g['schema']='CPC8R.native_comparison_feedback.geometry.v3';g['route']=route;g['interfaces']=len(ports);g['feedback_scope']='Fixed allcandidate relay with seven realZsteps changes flightphase; a secondary comparisonproduct71 is transformed, not an externally injected correct regulation direction. No learned policy by utility claimed.'
 return r,g
class FeedbackSession(RegulatedQuantitySession):
 @classmethod
 def create(cls,**kw):r,g=prepare_feedback(**kw);return cls(d.OrganizationalWorld.create(r),g)
 def feedback_opportunities(self,enabled=True):
  if enabled:
   for r in self.geometry['feedback_relays']:self.input(r['port'],r['payload'],r['tick']-3)
 def first_regulation_experience(self):
  r=self.geometry['regulators'][0];self.input(r['cue_port'],5,0);self.input(r['event_ports']['-1'],11,0)
