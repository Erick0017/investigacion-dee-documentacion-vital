"""Third/final access family: parallel native count readers, no host selection.

All fixed X-route candidates receive their own physical comparator and readers.
This spends three comparator copies; it is not an equal-resource advantage.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from count_sign.session import CountSignSession,port,move
from relaciones.contact_cardinality import prepare as prepare_count
from integracion.quantity_core import prepare as prepare_quantity

def prepare_branch(case):
 opts={k:case[k]for k in('contacts','actor_state','medium_state','actor_load','unit_load')if k in case};opts['regulation']='branch_onpath'
 readout=case.get('readout','permanent');transient=readout=='transient_gap'
 if readout not in('permanent','transient_gap'):raise ValueError('Explicit readout family')
 if transient and opts.get('unit_load',1)!=2:raise ValueError('Transient gap readout explicitly calibrates each contact medium to2, not F3unit1')
 r,cg=prepare_count(opts);ports=list(r.interfaces);placements=list(r.placements);branches=[];names=[];c=cg['collector']
 if case.get('bridge_guard')in('onpath','offpath'):
  guard=[25,35,57]if case['bridge_guard']=='onpath'else[25,47,57]
  p=d.InitialPlacement();p.site=d.Coordinate(*guard);p.raw=d.pack_record(1,0,0,0,0,4);p.clock=0;p.role='Fixed interception of unused formatter return before reference encounter87';placements.append(p)
 for axis in(-1,0,1):
  turn=move(c,(axis,1,1),10);v=(-axis,0,-1);fmt='count.branch.'+str(axis)+'.turn';ports.append(port(fmt,move(turn,v,-3),v))
  refhub=move(turn,(0,1,0),4);center=move(refhub,(1,-1,0));qr,qg=prepare_quantity(center=center,profile='transient'if transient else'permanent',guards='on_path');prefix='count.branch.'+str(axis)+'.'
  placements+=list(qr.placements)
  for p in qr.interfaces:p.name=prefix+p.name;ch=p.channel;ch.name=prefix+ch.name;p.channel=ch;ports.append(p)
  branches.append({'route_axis_candidate':axis,'turn20':turn,'reference_hub24':refhub,'formatter_port':fmt,'quantity':qg,'prefix':prefix})
  for value in((-1,1)if transient else(0,1)):
   if transient:
    meeting=move(center,(value,0,0),2);q=move(center,(3*value,1,0));q1=move(q,(0,1,0),20);q2=move(q1,(0,1,1),34);tag=prefix+'form.'+str(value)
    ports.extend((port(tag+'.record',move(meeting,(0,1,0),-3),(0,1,0),77),port(tag+'.normalize',move(q,(-value,0,0),-3),(-value,0,0),77),port(tag+'.read1',move(q1,(0,0,1),-3),(0,0,1),77),port(tag+'.read2',move(q2,(0,0,-1),-3),(0,0,-1),77)))
    names.append({'route_axis_candidate':axis,'candidate_comparator_x':value,'teaching_site93':meeting,'memory_site':q,'query1_site':q1,'query2_site':q2,'record_port':tag+'.record','normalizer_port':tag+'.normalize','query1_port':tag+'.read1','query2_port':tag+'.read2','expected_query1':[0,1,1],'expected_query2':[0,1,0]})
    continue
   q=move(center,(value,0,1),3);cue=(-1,1,-1);mv=(value-1,1,0);q1=move(q,mv,20);q2=move(q1,(value-1,1,1),34);tag=prefix+'form.'+str(value)
   ports.extend((port(tag+'.record',move(q,cue,-3),cue,77),port(tag+'.read1',move(q1,(0,0,1),-3),(0,0,1),77),port(tag+'.read2',move(q2,(0,0,-1),-3),(0,0,-1),77)))
   names.append({'route_axis_candidate':axis,'candidate_comparator_x':value,'memory_site':q,'query1_site':q1,'query2_site':q2,'record_port':tag+'.record','query1_port':tag+'.read1','query2_port':tag+'.read2','expected_query1':[value-1,1,1],'expected_query2':[value-1,1,0]})
 sites=[(p.site.x,p.site.y,p.site.z)for p in placements]
 if len(sites)!=len(set(sites)):raise ValueError('Branch count initial material overlap')
 if len({p.name for p in ports})!=len(ports):raise ValueError('Branch count interface overlap')
 r.placements=placements;r.interfaces=ports
 g={'schema':'CPC8R.count_sign.parallel.geometry.v2'if transient else'CPC8R.count_sign.parallel.geometry.v1','readout':readout,'bridge_guard':case.get('bridge_guard'),'threshold_object_payload':3 if transient else 1,'N':67,'count':cg,'branches':branches,'names':names,'ticks':{'count':10,'route':20,'reference':24,'comparison':91,'form':94,'queries':[114,148],'extra_query':170},
  'resources':{'initial_material_sites':len(placements),'interfaces':len(ports),'threshold_comparators':3,'extra_supports':len(placements)-len(cg['branches'])*3,'basic_buffer_bytes':32*67**3},
  'prepared':'Three routes/comparators, all post-count formatters and form banks fixedT0. No choosing which branch knows a result. Each native comparator uses actual count-derived reference versus material6.',
  'scope':'Finite parallel count-to-form apparatus; sensor-normalized contact count, not general cardinality or a learned comparative rule.'}
 r.options={'CPC8R.count_sign.geometry':encode_metadata(g)};r.domain=g['scope'];return r,g

class BranchCountSignSession(CountSignSession):
 @classmethod
 def create(cls,case):r,g=prepare_branch(case);return cls(d.OrganizationalWorld.create(r),g,identifier=case['id'])
 def curriculum(self,form='paired',route=True,query=True):
  if self.tick!=0 or form not in('paired','unpaired','omitted'):raise ValueError('Fresh branch protocol')
  self.input('counter.cue',5,7)
  for name in('A','B'):self.input('counter.free.guard.'+name,0,6)
  for b in self.geometry['branches']:
   if route:self.input(b['formatter_port'],0,17)
   for suffix,load,t in(('quantity.object.cue',5,86),('quantity.object.resource',self.geometry['threshold_object_payload'],86),('quantity.reader',7,90)):self.input(b['prefix']+suffix,load,t,suffix.endswith('reader'))
  for p in self.geometry['names']:
   if form!='omitted':self.input(p['record_port'],5,(90 if self.geometry['readout']=='transient_gap'else 91)+(5 if form=='unpaired'else 0))
   if 'normalizer_port'in p:self.input(p['normalizer_port'],0,91)
   if query:self.input(p['query1_port'],7,111,True);self.input(p['query2_port'],7,145,True)
  self.input('extra.cue',5,100);self.input('extra.event',11,100);self.input('extra.query',9,167,True)
 def view(self):
  g=self.geometry;return{'tick':self.tick,'counter':self.observe(g['count']['collector']),'extra':self.observe(g['count']['extra']),
   'branches':[{'route_axis_candidate':b['route_axis_candidate'],'turn20':self.observe(b['turn20']),'reference_hub24':self.observe(b['reference_hub24']),
    'quantity':{k:self.observe(b['quantity'][k])for k in('center','reference_site','object_site')}}for b in g['branches']],
   'names':[{'route_axis_candidate':p['route_axis_candidate'],'candidate_comparator_x':p['candidate_comparator_x'],'memory':self.observe(p['memory_site']),'query1':self.observe(p['query1_site']),'query2':self.observe(p['query2_site'])}for p in g['names']]}
