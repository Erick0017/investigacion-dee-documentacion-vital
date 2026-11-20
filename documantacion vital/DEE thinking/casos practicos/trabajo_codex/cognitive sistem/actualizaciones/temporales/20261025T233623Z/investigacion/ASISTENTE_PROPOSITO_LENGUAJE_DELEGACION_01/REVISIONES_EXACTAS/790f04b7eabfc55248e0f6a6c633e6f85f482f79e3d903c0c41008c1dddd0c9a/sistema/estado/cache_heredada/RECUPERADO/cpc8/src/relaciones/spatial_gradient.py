"""Prepared local spatial-gradient sensor, actual position is not a sign label.

The readout direction is produced by the unmodified matter-gradient branch.
Object events carry the same outward-Z direction irrespective of their Y side.
This initial calibration alone is not an acquired semantic relation.
"""
import argparse,hashlib,json,os,shutil,sys,time
from pathlib import Path
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
def move(q,v,k=1):return[(q[i]+v[i]*k)%67 for i in range(3)]
def sensor(center,object_offsets):
 initial=[]
 def put(q,v=(0,0,0),load=0,sem=4):
  p=d.InitialPlacement();p.site=d.Coordinate(*q);p.raw=d.pack_record(1,load,*v,sem);p.clock=0;p.role='Prepared local sensor support' if sem==4 else 'Prepared renewable local probe';initial.append(p)
 for axis in range(3):
  for sign in(-1,1):
   v=[0,0,0];v[axis]=sign;put(move(center,v),load=int(axis==2 and sign==-1))
 put(center,(0,0,1),0,1)
 for offset in object_offsets:put(move(move(center,offset),(0,0,-1),4))
 return initial
def prepare_gradient_geometry(center=(25,25,25),state=99):
 offsets=[[-1,-1,0],[1,1,0],[0,-1,-1],[0,1,-1],[-1,-1,-1],[1,1,-1],[-1,1,-1],[1,-1,-1]];initial=sensor(center,offsets);ports=[]
 for i,v in enumerate(offsets):
  c=d.ChannelSpec();c.name='object.'+str(i);c.injection_site=d.Coordinate(*move(center,v));c.direction=d.Direction(0,0,-1);c.state=state;c.semantic=1;c.allow_experience=True;c.allow_probe=True;p=d.InterfaceSpec();p.name=c.name;p.channel=c;ports.append(p)
 recipe=d.OrganizationRecipe.research(67,initial,0);recipe.interfaces=ports;recipe.execution=d.TickOptions(d.Backend.LAZY,1);return recipe,{'center':list(center),'offsets':offsets,'interfaces':len(ports),'initial_material':len(initial),'state':state,'scope':'Native local gradient readout; no association or learned spatial meaning is asserted by this calibration.'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--offset-index',type=int,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);src=a.out/'executed_source';src.mkdir();shutil.copyfile(__file__,src/Path(__file__).name);start=time.monotonic();recipe,g=prepare_gradient_geometry();w=d.OrganizationalWorld.create(recipe);receipt=w.submit('object.'+str(a.offset_index),11,0);frames=[]
 for t in range(13):
  w.run_until(t);frame={'tick':t,'probe':exact_observation(w.runtime.observe(d.Coordinate(*g['center']))),'local':[]}
  for x in range(-3,4):
   for y in range(-3,4):
    for z in range(-3,4):
     o=exact_observation(w.runtime.observe(d.Coordinate(*move(g['center'],(x,y,z)))))
     if o['active']and o['semantic']!=4:frame['local'].append(o)
  frames.append(frame)
 m={'schema':'CPC8R.spatial_gradient.calibration.v1','case':{'id':a.out.name,'actual_object_offset':g['offsets'][a.offset_index]},'preparations':1,'diagnostic_forks':0,'continuations':0,'status':'EXECUTED','source_sha256':sha(src/Path(__file__).name),'geometry':g,'request':{'id':int(receipt.id),'port':'object.'+str(a.offset_index),'payload':11,'tick':0,'direction':[0,0,-1],'receipt':exact_receipt(w.runtime.receipt(receipt.id))},'frames':frames,'elapsed_seconds':time.monotonic()-start,'interpretation':'Prepared sensor only; no learned meaning.'}
 (a.out/'MEASUREMENTS.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'offset':g['offsets'][a.offset_index],'probe':[(f['tick'],f['probe']['direction'])for f in frames[:5]]}))
if __name__=='__main__':main()
