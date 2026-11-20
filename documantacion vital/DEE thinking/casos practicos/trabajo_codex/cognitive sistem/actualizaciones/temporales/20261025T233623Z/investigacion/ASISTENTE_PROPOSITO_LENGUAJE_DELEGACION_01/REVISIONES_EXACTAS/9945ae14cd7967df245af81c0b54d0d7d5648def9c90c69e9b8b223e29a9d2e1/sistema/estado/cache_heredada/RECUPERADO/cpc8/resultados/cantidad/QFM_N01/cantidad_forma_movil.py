"""Declared remote-reader revision of QF; tracks a physically shifted support.

The first normalization removes the Zdirection but not its spatial displacement.
Thus the previous query at the old z-plane misses the surviving moving memory.
All remote interfaces and all sign candidates exist atT0. No observation, target
or stored answer selects a port. This is instrumented renewed access, not learned
selection of where to read.
"""
from cantidad_forma import NamedQuantitySession,prepare_named
from cantidad_renovable import move
from dee_thinking import _native as d

def prepare_mobile_form(**options):
 r,g=prepare_named(**options);ports=list(r.interfaces)
 for b in g['form_banks']:
  b['remote_readers']=[]
  for k in(1,2):
   site=move(b['normalized_bank'],(0,0,1),k);renewal=move(site,(0,1,1));qname='quantity.mobile.word.'+b['tag']+'.'+str(k);rname=qname+'.renew'
   for name,target,v in((qname,site,(0,0,1)),(rname,renewal,(0,0,-1))):
    c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*move(target,v,-3));c.direction=d.Direction(*v);c.state=1;c.semantic=1;c.allow_probe=True;c.allow_experience=True;p=d.InterfaceSpec();p.name=name;p.channel=c;ports.append(p)
   b['remote_readers'].append({'round':k,'site':site,'renewal_site':renewal,'query':qname,'renew':rname})
 r.interfaces=ports;g['interfaces']=len(ports);g['schema']='CPC8R.quantity.named.remote_plane.v2';g['access_revision']='First word140 atbank is normalized141 oneZstep away; next wordreader207 must reachbank+Z, third274bank+2Z. Prepared instrument access, not E1selection.';return r,g
class MobileNamedQuantitySession(NamedQuantitySession):
 @classmethod
 def create(cls,**options):r,g=prepare_mobile_form(**options);return cls(d.OrganizationalWorld.create(r),g)
 def query_form(self,load=9,round_index=0,renew=True):
  if round_index==0:return super().query_form(load,round_index,renew)
  if round_index not in(1,2):raise ValueError('Finite three-reader access domain')
  for b in self.geometry['form_banks']:
   r=next(x for x in b['remote_readers']if x['round']==round_index);t=137+67*round_index;self.input(r['query'],load,t,True)
   if renew:self.input(r['renew'],0,t+1)
 def observe_words_at_query(self,round_index):
  return[{'sign':b['sign'],'reading':self.observe(move(b['normalized_bank'],(0,0,1),round_index))}for b in self.geometry['form_banks']]
