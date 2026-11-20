"""Finite physical use of a requested native return, with no read-act callback.

This is an optional new experimental preparation, not a mutation of an already
running participant. Both receiving resources are fixed before any outcome.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,shutil,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from iniciativa_accion.solicitud import InitiativeSession,prepare_gradient_tap,interface,move,phys
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def prepare_return_use(g,*,delay=3,load=13):
 """Inert extra ports/geometry for all physical return directions.

 The receiver does not inspect a payload or choose its input after reading the
 result. Both resources are programmed before evolution in every intact case.
 """
 if delay!=3 or load!=13:raise ValueError('Only the frozen short receiving contact is offered in this extension')
 ports=[];items=[]
 for b in g['branches']:
  for p,e in b['effects'].items():
   v=e['return_direction'];meeting=move(e['return_site'],v,delay);rv=(-int(p),1,0);name=g['prefix']+'return_use.'+str(b['reference_candidate'])+'.'+p
   site=move(meeting,rv,-3);ports.append(interface(name,site,rv));g['signatures'][name]={'site':site,'direction':list(rv),'state':1,'semantic':1}
   items.append({'source_value_candidate':int(p),'port':name,'input_site':site,'input_direction':list(rv),'load':load,'requested_tick':g['ticks']['return']+delay-3,
    'meeting_site':meeting,'meeting_tick':g['ticks']['return']+delay,'emission_site':move(meeting,(0,0,-1)),'emission_tick':g['ticks']['return']+delay+1,
    'expected_format_not_payload':[0,0,-1]})
 return ports,{'schema':'CPC8R.initiative.return_use.geometry.v1','items':items,'prepared':'Two symmetric receiving resources, same schedule/load regardless of reference, source or upstream output.','scope':'A contact using a returned physical product; not a learned receptor policy or unbounded reusable organ.'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 cfg=json.loads(a.config.read_text(encoding='utf-8'));case=next(c for c in cfg['cases']if c['id']==a.case);a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'executed_source';bundle.mkdir();put(a.out/'CONFIG.json',cfg)
 for src in(Path(__file__),ROOT/'src/iniciativa_accion/solicitud.py',ROOT/'src/cantidad_renovable.py'):shutil.copyfile(src,bundle/src.name)
 spec=importlib.util.spec_from_file_location('quantity_frozen_for_return_use',bundle/'cantidad_renovable.py');qmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(qmod)
 recipe,qg=qmod.prepare(center=(50,35,35),profile='transient');ports,g=prepare_gradient_tap();rxports,rxg=prepare_return_use(g);g['return_use']=rxg
 recipe.interfaces=list(recipe.interfaces)+ports+rxports
 if len(set(x.name for x in recipe.interfaces))!=len(recipe.interfaces):raise ValueError('Interface overlap')
 world=d.OrganizationalWorld.create(recipe);q=qmod.QuantitySession(world,qg);s=InitiativeSession(world,g)
 q.experience_reference(case['reference_quantity'])
 for i,value in enumerate(case['objects']):q.present_object(value,round_index=i)
 q.reader_opportunity();q.acquire_other();s.acquire_source(case['source_sign'],case.get('source_mode','paired'));s.opportunities(case.get('question_opportunity',True))
 for rx in rxg['items']:s.submit(rx['port'],rx['load'],rx['requested_tick'],'FIXED_SYMMETRIC_RETURN_RECEIVER_RESOURCE')
 m={'schema':'CPC8R.initiative.return_use.measurements.v1','case':case,'source_sha256':{x.name:sha(x)for x in bundle.iterdir()},'configuration_sha256':sha(a.config),
  'geometry':g,'quantity_geometry':qg,'preparations':1,'runtime_owners':1,'same_world':q.world is s.world,'host_RAW_clock_edits_on_MAIN':[],
  'frames':[],'quantity':[],'snapshots':[],'status':'RUNNING'};start=time.monotonic();cpu=time.process_time()
 def capture():
  return{'tick':s.tick,'initiative':s.capture(),'return_use':[{'physical_at_contact':s.observe(rx['meeting_site']),'physical_after_contact':s.observe(rx['emission_site'])}for rx in rxg['items']]}
 def save():
  world.runtime.set_snapshot_metadata(qmod.KEY,encode_metadata({'geometry':q.geometry,'state':q.state,'tick':s.tick,'channels':sorted(world.runtime.channel_names)}))
  path=a.out/('T'+str(s.tick)+'.deetsnap.gz');m['snapshots'].append({'path':path.name,'physical':phys(world),'storage':s.save(path)})
 save()
 try:
  for t in(69,70,72,73,77,81,86,87,88,89,90,91,136,137,180,203,204,214):
   s.run_until(t);m['frames'].append(capture())
   if t in(69,70,136,137,180,203,204):m['quantity'].append(q.capture())
   if t in(73,86,87,90,214):save()
   put(a.out/'INCREMENTAL.json',m)
  m['receiving_readouts']=[{'physical':o['physical_at_contact'],'covered':o['physical_at_contact']['active']and o['physical_at_contact']['semantic']==1 and o['physical_at_contact']['direction']==[0,0,-1]and o['physical_at_contact']['s_reg']>13}for f in m['frames']if f['tick']==89 for o in f['return_use']]
  m.update(status='MEASURED',final_physical=phys(world),quantity_receipts=q.receipts(),initiative_receipts=s.receipts())
 finally:m.update(elapsed_seconds=time.monotonic()-start,cpu_seconds=time.process_time()-cpu);put(a.out/'MEASUREMENTS.json',m)
 print(json.dumps({'case':case['id'],'used_native_return':[r['physical']for r in m.get('receiving_readouts',[])if r['covered']]}))
if __name__=='__main__':main()
