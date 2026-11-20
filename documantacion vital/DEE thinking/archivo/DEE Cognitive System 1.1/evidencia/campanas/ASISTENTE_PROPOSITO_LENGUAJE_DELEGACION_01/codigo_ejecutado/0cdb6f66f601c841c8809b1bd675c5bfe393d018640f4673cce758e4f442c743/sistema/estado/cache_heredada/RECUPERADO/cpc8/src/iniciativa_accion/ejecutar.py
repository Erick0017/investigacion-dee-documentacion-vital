"""Finite supervised trajectory of the native initiative component."""
from pathlib import Path
import argparse,gc,hashlib,json,shutil,sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from iniciativa_accion.solicitud import InitiativeSession,phys,move
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);q=p.with_name(p.name+'.pending');q.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');q.replace(p)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--config',type=Path,required=True);parser.add_argument('--case',required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
 cfg=json.loads(args.config.read_text(encoding='utf-8'));case=next(x for x in cfg['cases']if x['id']==args.case)
 args.out.mkdir(parents=True,exist_ok=False);put(args.out/'CONFIG.json',cfg)
 bundle=args.out/'executed_source';bundle.mkdir()
 for p in(Path(__file__),ROOT/'src/iniciativa_accion/solicitud.py'):shutil.copyfile(p,bundle/p.name)
 started=time.monotonic();cpu=time.process_time()
 import dee_thinking as dee
 assert dee.__version__=='4.5.0'and Path(dee.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
 assert sha(d.__file__)=='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
 s=InitiativeSession.create(origin=tuple(case.get('origin',[8,50,5])),backend=case.get('backend','LAZY'))
 s.acquire_reference(case['reference_sign'],case.get('reference_mode','paired'),case.get('reference_load',11))
 s.acquire_source(case['source_sign'],case.get('source_mode','paired'),case.get('source_cue',5),case.get('source_load',11))
 s.present_object(case['object_sign'],case.get('object_load',7));s.opportunities(case.get('request_opportunity',True),case.get('effect_load',7),case.get('effect_opportunity',True))
 m={'schema':'CPC8R.initiative.measurements.v1','case':case,'status':'RUNNING','preparations':1,'diagnostic_forks':0,
  'instrument':{'version':dee.__version__,'module':dee.__file__,'PYD_sha256':sha(d.__file__),'WHL_sha256':'09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'},
  'source_sha256':{p.name:sha(p)for p in bundle.iterdir()},'configuration_sha256':sha(args.config),
  'geometry':s.geometry,'frames':[],'snapshots':[],'candidate_route_observations':[],'host_RAW_clock_edits_on_MAIN':[]}
 path=args.out/'INITIAL_T0.deetsnap.gz';m['snapshots'].append({'path':path.name,'physical':phys(s.world),'storage':s.save(path)})
 try:
  capture_ticks={3,66,67,69,70,71,72,73,74,77,78,79,81,82,83,86,87,88,94}
  for tick in range(1,case.get('horizon',94)+1):
   s.run_until(tick)
   if 3<=tick<=78:
    traced=[]
    for branch in s.geometry['branches']:
     for p,source in branch['sources'].items():
      traced.append({'candidate':'provider'+str(branch['reference_candidate'])+'.'+p,
       'route_rule':'declared hub+(tick-3)*direction modulo67; a candidate route, not ancestry assigned by proximity',
       'physical':s.observe(move(source['hub'],source['direction'],tick-3))})
    m['candidate_route_observations'].append({'tick':tick,'observations':traced})
   if tick not in capture_ticks:continue
   frame=s.capture()
   if tick in(69,72,77,81):
    key={69:'comparison_site',72:'request_site',77:'source_site',81:'effect'}[tick]
    sites=[e['site']for b in s.geometry['branches']for e in b['effects'].values()]if key=='effect'else[b[key]for b in s.geometry['branches']]
    frame['local_Moore27']=[{'center':q,'observations':[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]}for q in sites]
   m['frames'].append(frame)
   if tick in(70,74,78,82,87):
    path=args.out/('T'+str(tick)+'.deetsnap.gz');m['snapshots'].append({'path':path.name,'physical':phys(s.world),'storage':s.save(path)})
   put(args.out/'INCREMENTAL.json',{'tick':tick,'captures':m['frames'],'receipts':s.receipts()})
  m.update(status='MEASURED',final_physical=phys(s.world),receipts=s.receipts())
  returns=[o for f in m['frames']if f['tick']==87 for b in f['branches']for o in b['return'].values()]
  m['return_readouts']=[{'physical':o,'covered':o['active']and o['semantic']==1 and o['direction'][0]in(-1,1)and o['direction'][1:]==[-1,-1]and o['s_reg']>case.get('effect_load',7),
   'value':o['direction'][0]if o['active']and o['direction'][0]in(-1,1)and o['direction'][1:]==[-1,-1]and o['s_reg']>case.get('effect_load',7)else None,
   'provenance':'ENTE_NATIVE_RETURN; fixed physical decoder reads no teacher map, reference sign or source target'}for o in returns]
  # Evaluation starts only after the complete physical trajectory above.
  m['auditor_evaluation']={'expected_question_from_reference_mismatch':case['reference_sign']!=case['object_sign'],
   'return_values_observed':[r['value']for r in m['return_readouts']if r['covered']],
   'scope':'Expectation is auditor-only; no expectation was submitted to the participant.'}
 finally:
  m.update(elapsed_seconds=time.monotonic()-started,cpu_seconds=time.process_time()-cpu);put(args.out/'MEASUREMENTS.json',m)
 print(json.dumps({'id':case['id'],'status':m['status'],'return':m.get('auditor_evaluation')}))
if __name__=='__main__':main()
