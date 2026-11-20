"""New same-Runtime coupling: acquired quantity -> physical information request.

The quantity source is copied byte-exactly before import. No result from any
previous case supplies a participant response. No externally read direction is
used to decide whether to inject a question, a source or an effect resource.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,shutil,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from iniciativa_accion.solicitud import InitiativeSession,prepare_gradient_tap,phys,move
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(path,x):
 path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+'.pending');temp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(path)
def main():
 a=argparse.ArgumentParser();a.add_argument('--config',type=Path,required=True);a.add_argument('--case',required=True);a.add_argument('--out',type=Path,required=True);args=a.parse_args()
 cfg=json.loads(args.config.read_text(encoding='utf-8'));case=next(c for c in cfg['cases']if c['id']==args.case)
 args.out.mkdir(parents=True,exist_ok=False);bundle=args.out/'executed_source';bundle.mkdir();put(args.out/'CONFIG.json',cfg)
 for p in(Path(__file__),ROOT/'src/iniciativa_accion/solicitud.py',ROOT/'src/cantidad_renovable.py'):shutil.copyfile(p,bundle/p.name)
 spec=importlib.util.spec_from_file_location('quantity_frozen_for_initiative',bundle/'cantidad_renovable.py');quantity=importlib.util.module_from_spec(spec);spec.loader.exec_module(quantity)
 r,qg=quantity.prepare(center=(50,35,35),profile='transient')
 ports,g=prepare_gradient_tap(question_direction=tuple(case.get('question_direction',[0,1,1])))
 if set(p.name for p in r.interfaces)&set(p.name for p in ports):raise ValueError('Duplicate shared-world interface')
 r.interfaces=list(r.interfaces)+ports;r.options={**dict(r.options),'CPC8R.initiative.gradient.geometry':encode_metadata(g)}
 world=d.OrganizationalWorld.create(r);q=quantity.QuantitySession(world,qg);s=InitiativeSession(world,g)
 q.experience_reference(case['reference_quantity'],mode=case.get('reference_mode','paired'))
 for index,value in enumerate(case.get('objects',[16,42,16])):q.present_object(value,round_index=index)
 q.reader_opportunity();q.acquire_other()
 s.acquire_source(case.get('source_sign',1),case.get('source_mode','paired'));s.opportunities(case.get('question_opportunity',True),7,case.get('effect_opportunity',True))
 m={'schema':'CPC8R.initiative.gradient.measurements.v1','case':case,'configuration_sha256':sha(args.config),
  'source_sha256':{p.name:sha(p)for p in bundle.iterdir()},'preparations':1,'runtime_owners':1,'q_and_s_share_same_world':q.world is s.world,
  'geometry':g,'quantity_geometry':qg,'status':'RUNNING','frames':[],'quantity_observations':[],'snapshots':[],'host_RAW_clock_edits_on_MAIN':[]}
 start=time.monotonic();cpu=time.process_time()
 def save(tick):
  # Inert operative metadata for both facades, same physical world owner.
  world.runtime.set_snapshot_metadata(quantity.KEY,encode_metadata({'geometry':q.geometry,'state':q.state,'tick':s.tick,'channels':sorted(world.runtime.channel_names)}))
  path=args.out/('T'+str(tick)+'.deetsnap.gz');m['snapshots'].append({'path':path.name,'physical':phys(world),'storage':s.save(path)})
 save(0)
 try:
  for tick in(3,68,69,70,71,72,73,74,76,77,78,80,81,82,85,86,87,94,110,136,137,177,180,203,204,214):
   if tick>case.get('horizon',214):continue
   q.run_until(tick);m['frames'].append(s.capture())
   if tick in(3,68,69,70,71,72,73,74,77,81,86,110,136,137,180,203,204,214):m['quantity_observations'].append(q.capture())
   if tick in(70,73,77,81,86,137,204):save(tick)
   put(args.out/'INCREMENTAL.json',{'last_tick':s.tick,'quantity':m['quantity_observations'],'request':m['frames'],'receipts':q.receipts()+s.receipts()})
  m.update(status='MEASURED',final_physical=phys(world),quantity_receipts=q.receipts(),initiative_receipts=s.receipts())
  returns=[o for f in m['frames']if f['tick']==g['ticks']['return']for b in f['branches']for o in b['return'].values()]
  m['return_readouts']=[{'physical':o,'covered':o['active']and o['semantic']==1 and o['direction'][0]in(-1,1)and o['direction'][1:]==[-1,-1]and o['s_reg']>7,
   'scope':'Current exact native return fields; no reference/object magnitude is used by decoder.'}for o in returns]
  m['observed_quantity_outputs']=[{'tick':o['tick'],'center':o['center'],'reference':o['reference'],'object':o['object']}for o in m['quantity_observations']if o['tick']in(70,137,204)]
 finally:m.update(elapsed_seconds=time.monotonic()-start,cpu_seconds=time.process_time()-cpu);put(args.out/'MEASUREMENTS.json',m)
 print(json.dumps({'case':case['id'],'status':m['status'],'quantity_outputs':m.get('observed_quantity_outputs'),'return':[x['physical']for x in m.get('return_readouts',[])if x['covered']]}))
if __name__=='__main__':main()
