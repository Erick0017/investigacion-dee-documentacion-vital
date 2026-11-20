"""Post-function arbitrary-form association, entirely through v27 encounters.

Both possible class ports receive the same cue. Only the actual comparison
product can participate in its teaching encounter. The interface never selects
the class bank from an answer. The comparator itself is prepared, not learned.
"""
from cantidad_renovable import QuantitySession,prepare,move
from dee_thinking import _native as d

def prepare_named(center=(30,30,30),guards='on_path'):
 r,g=prepare(center=center,guards=guards);c=g['center'];interfaces=list(r.interfaces)
 def port(name,site,direction):
  q=d.ChannelSpec();q.name=name;q.injection_site=d.Coordinate(*site);q.direction=d.Direction(*direction);q.state=1;q.semantic=1;q.allow_probe=True;q.allow_experience=True
  p=d.InterfaceSpec();p.name=name;p.channel=q;interfaces.append(p)
 g['form_banks']=[]
 for s in(-1,1):
  tag='minus'if s<0 else'plus';meeting=move(c,(2*s,0,0));bank=move(c,(3*s,1,0))
  port('quantity.form.'+tag,move(meeting,(0,1,0),-3),(0,1,0))
  port('quantity.form.normalize.'+tag,move(bank,(-s,0,0),-3),(-s,0,0))
  port('quantity.word.'+tag,move(bank,(0,0,1),-3),(0,0,1))
  renewal=move(bank,(0,1,1));port('quantity.word.renew.'+tag,move(renewal,(0,0,-1),-3),(0,0,-1))
  g['form_banks'].append({'sign':s,'tag':tag,'teaching_contact':meeting,'normalized_bank':bank})
 r.interfaces=interfaces;g['schema']='CPC8R.quantity.named.geometry.v1';g['form_prepared']='Both sign banks, same arbitrary form, fixed normalization and externally supplied renewal; no class map in participant'
 g['interfaces']=len(interfaces);return r,g

class NamedQuantitySession(QuantitySession):
 @classmethod
 def create(cls,**kwargs):
  r,g=prepare_named(**kwargs);return cls(d.OrganizationalWorld.create(r),g)
 def associate_form(self,load=5,mode='paired'):
  if mode not in('paired','omit','unpaired'):raise ValueError('Declared teaching control')
  for b in self.geometry['form_banks']:
   if mode!='omit':self.input('quantity.form.'+b['tag'],load,69+int(mode=='unpaired'))
   self.input('quantity.form.normalize.'+b['tag'],0,70)
 def query_form(self,load=9,round_index=0,renew=True):
  t=137+67*round_index
  for b in self.geometry['form_banks']:
   self.input('quantity.word.'+b['tag'],load,t,True)
   if renew:self.input('quantity.word.renew.'+b['tag'],0,t+1)
 def observe_words(self):
  return[{'sign':b['sign'],'reading':self.observe(move(b['normalized_bank'],(0,1,0),self.tick-140))}for b in self.geometry['form_banks']]
