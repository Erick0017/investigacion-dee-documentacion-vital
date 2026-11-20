"""Acquired material reference and a new quantity, compared by v27 gradient.

No comparison bit is an input. The occupied reader and zero-load supporting
neighborhood are prepared; the reference magnitude is acquired after T0.
"""
import argparse,hashlib,json,shutil,sys,time
from array import array
from pathlib import Path
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import save_world_snapshot
ROOT=Path(__file__).resolve().parents[1]
def shift(q,v,k=1):return[(q[i]+v[i]*k)%67 for i in range(3)]
def build():
 center=[30,30,30];ref=[29,31,30];obj=[31,27,30];initial=[];ports=[]
 for x in(-1,1):
  for y,z in((-1,-1),(-1,1),(1,1)):
   p=d.InitialPlacement();p.site=d.Coordinate(*shift(center,(x,y,z)));p.raw=d.pack_record(1,0,0,0,0,4);p.clock=0;p.role='Prepared zero-load support for native gradient reader';initial.append(p)
 def port(name,q,v):
  c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*q);c.direction=d.Direction(*v);c.state=1;c.semantic=1;c.allow_probe=True;c.allow_experience=True
  i=d.InterfaceSpec();i.name=name;i.channel=c;ports.append(i)
 for name,q in(('reference',ref),('object',obj)):
  port(name+'.cue',shift(q,(-1,0,0),-3),(-1,0,0));port(name+'.resource',shift(q,(1,1,0),-3),(1,1,0))
 port('reader',center,(0,0,1))
 recipe=d.OrganizationRecipe.research(67,initial,0);recipe.interfaces=ports;recipe.execution=d.TickOptions(d.Backend.LAZY,1)
 return recipe,{'N':67,'center':center,'reference_hub':ref,'object_hub':obj,'reference_at69':[29,30,30],'object_at69':[31,30,30],
  'initial_material':len(initial),'basic_buffer_bytes':32*67**3,'prepared':'Six semantic4 zero-load supports and a common occupied reader; v27 gradient unchanged',
  'acquired':'Reference carrier cue5 + previous actual resource; current object receives same physical format without a computed comparison label'}
def phys(w):
 r=w.runtime;return{'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}
def observe(w,q):return exact_observation(w.runtime.observe(d.Coordinate(*q)))
def savejson(p,r):p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def run(case,out):
 out.mkdir(parents=True,exist_ok=False);recipe,g=build()
 config={'schema':'CPC8R.quantity.frozen.v1','case_id':case['id'],'environment':case,'geometry':g,'frozen_before_constructor':True,
  'expected_operation_not_input':'Audit after evolution: sign(previous reference magnitude - current object magnitude), if the intended material relation reached the reader. Equality is a valid state, not silence.',
  'protocol':'Reference pairing0→3, new object pairing63→66, common zero-load reader69→70; no labels, targets or future rollout imported by world.'}
 savejson(out/'CONFIG.json',config);shutil.copyfile(Path(__file__),out/'EXECUTED_SOURCE.py');w=d.OrganizationalWorld.create(recipe);requests=[]
 def inp(port,payload,tick,probe=False):
  r=getattr(w,'probe'if probe else'submit')(port,payload,tick);requests.append({'id':int(r.id),'port':port,'payload':payload,'tick':tick,'kind':'probe'if probe else'submit'})
 if case['history']!='no_cue':inp('reference.cue',5,int(case['history']=='unpaired'))
 inp('reference.resource',case['reference'],0)
 inp('object.cue',5,63);inp('object.resource',case['object'],63)
 inp('reader',0,69,True)
 frames=[]
 for tick in(0,3,4,65,66,68,69,70,71,74):
  w.run_until(tick);c=g['center'];sites={'center':c,'reference69':g['reference_at69'],'object69':g['object_at69'],
   'reference_expected':shift(g['reference_hub'],(0,1,0),tick-3),'object_expected':shift(g['object_hub'],(0,1,0),tick-66)}
  frames.append({'tick':tick,'physical':phys(w),'sites':{k:observe(w,q)for k,q in sites.items()},
   'Moore27':[observe(w,shift(c,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
  if tick in(0,3,69,70):save_world_snapshot(w,out/f'T{tick}.deetsnap.gz',compress=True)
 receipts=[{**r,'receipt':exact_receipt(w.runtime.receipt(r['id']))}for r in requests]
 result={'schema':'CPC8R.quantity.measurements.v1','case_id':case['id'],'kind':'EXPLORATORY_INDEPENDENT_PREPARATION_NOT_E1','geometry':g,'inputs':receipts,'frames':frames,
  'host_RAW_clock_edits':[],'reader70':frames[7]['sites']['center'],'prepared_vs_acquired':config['geometry'],'final':phys(w)}
 savejson(out/'MEASUREMENTS.json',result);print(json.dumps({'case_id':case['id'],'reader70':result['reader70'],'receipts':[r['receipt']['status']for r in receipts]},ensure_ascii=False))
if __name__=='__main__':
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True,choices=('Q_P01','Q_H01','Q_N01','Q_N02','Q_R01','Q_EQUAL'));a=p.parse_args()
 cases={'Q_P01':(11,17,'paired'),'Q_H01':(31,17,'paired'),'Q_N01':(31,17,'no_cue'),'Q_N02':(31,17,'unpaired'),'Q_R01':(31,47,'paired'),'Q_EQUAL':(17,17,'paired')}
 r,s,h=cases[a.case];run({'id':a.case,'reference':r,'object':s,'history':h},a.out)
