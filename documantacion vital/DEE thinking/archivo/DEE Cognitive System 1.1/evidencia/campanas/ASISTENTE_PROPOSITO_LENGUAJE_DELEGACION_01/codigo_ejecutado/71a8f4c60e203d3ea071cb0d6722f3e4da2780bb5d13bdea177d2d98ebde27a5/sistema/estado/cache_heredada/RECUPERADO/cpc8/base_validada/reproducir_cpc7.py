"""Preserved CPC7 N67 scientific constructors on official installed4.5.

Only instrument identity and lossless gzip snapshot storage are adapted before
importing the original modules. No physical recipe, input, decoder, expected
answer or native branch is changed. Historical comparison occurs after native
trajectory completion. This is reference reproduction, not E1 integration.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'genealogia/CPC7/src'
sys.path.insert(0,str(SOURCE));sys.path.insert(0,str(SOURCE/'endogenous'))
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def put(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def identity45():
 import dee_thinking as d
 assert d.__version__=='4.5.0' and d.kernel_identity()['kernel_version']==27
 assert sha(d._native.__file__)=='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
 assert sha(ROOT/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl')=='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
 assert Path(d.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
 return {'library':d.__version__,'kernel':d.kernel_identity(),'native_sha256':sha(d._native.__file__),
   'wheel_sha256':'09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c','module':d.__file__,'python':sys.executable,
   'scope':'Original CPC7 source4.0 identity assertion adapted explicitly to installed4.5; no legacy binary used'}
def save_gzip(self,path):
 from dee_thinking.persistence import save_world_snapshot
 import common,integrated
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 value={'schema':1,'identity':self.identity,'geometry':self.geometry,'requests':self.requests,'tick':int(self.world.runtime.current_tick)}
 self.world.runtime.set_snapshot_metadata(integrated.KEY,json.dumps(value,separators=(',',':')))
 storage=save_world_snapshot(self.world,path.with_name(path.name+'.gz'))
 return {'path':str(path),'sha256':storage['decoded_sha256'],'physical':common.digest(self.world),
     'operative':common.operational(self.world),'lossless_gzip_storage':storage}
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve()
 out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
 import common
 common.identity=identity45
 import integrated
 integrated.Session.save=save_gzip
 import integrated_public,integrated_revision
 config=ROOT/'genealogia/CPC7/configuraciones/integrated_revision.json'
 cfg=json.loads(config.read_text(encoding='utf-8'))
 source_hashes={p.relative_to(ROOT).as_posix():sha(p) for p in SOURCE.rglob('*.py')}
 frozen={'schema':'CPC8R.CPC7.frozen.v1','frozen_utc':datetime.now(timezone.utc).isoformat(),'instrument':identity45(),
  'n':67,'horizon':472,'cases':cfg['cases'],'original_config_sha256':sha(config),'source_hashes':source_hashes,
  'adapter_sha256':sha(Path(__file__)),'changed_operations':['common.identity assertion only','Session.save lossless gzip storage only'],
  'unchanged':'Recipes, history, opportunities, inputs, clocks, output decoder, controls, reserve and native dynamics',
  'criterion':'Compare full initial/final RAW/clocks/tick plus actual lower panels, revised form and13other responses; metadata/version/path differences isolated',
  'counting':'Four historical cases on current instrument; not four newly held-out worlds or E1 integration'}
 put(out/'FROZEN.json',frozen)
 mechanical=integrated_public.verify_geometry();put(out/'GEOMETRY_CHECK.json',mechanical)
 rows=[]
 from dee_thinking.persistence import load_world_snapshot
 for case in cfg['cases']:
  target=out/case['id'];result=integrated_revision.execute(case,target,sha(config))
  historical=ROOT/'genealogia/CPC7/resultados/integrated_revision'/case['id']/'MEASUREMENTS.json'
  old=json.loads(historical.read_text(encoding='utf-8'))
  actual=result['calculations'];expected=old['calculations']
  comparison={'case_id':case['id'],'historical_primary_sha256':sha(historical),'full_final_physical_equal':result['final_physical']==old['final_physical'],
    'post_revision_calculations_equal':actual==expected,
    'base338_physical_equal':result['base338']['final_physical']==old['base338']['final_physical'],
    'base338_calculations_equal':result['base338']['calculations']==old['base338']['calculations'],
    'receipt_entries_equal':result['final_operational']['receipts']==old['final_operational']['receipts'],
    'metadata_scope':'Native/operational container version and snapshot paths can differ; physical and receipt equivalence compared separately',
    'actual':actual,'expected':expected}
  if case['id']=='IR_P01_GUARDED_M1':
   pairs=[]
   for tick in (0,338,472):
    original=ROOT/'genealogia/CPC7/resultados/integrated_revision/IR_P01_GUARDED_M1'/f'T{tick}.deetsnap.gz'
    new=target/f'T{tick}.deetsnap.gz'
    ow,_=load_world_snapshot(original);nw,_=load_world_snapshot(new)
    pairs.append({'tick':tick,'full_RAW_clocks_tick_equal':common.digest(ow)==common.digest(nw),'historical':common.digest(ow),'current':common.digest(nw)})
    del ow,nw
   comparison['full_checkpoint_physical_pairs']=pairs
  comparison['status']='PASS' if all(comparison[k] for k in ('full_final_physical_equal','post_revision_calculations_equal','base338_physical_equal','base338_calculations_equal','receipt_entries_equal')) and all(q['full_RAW_clocks_tick_equal'] for q in comparison.get('full_checkpoint_physical_pairs',[])) else'FAIL'
  put(target/'HISTORICAL_PARITY.json',comparison);rows.append(comparison)
  put(out/'SUMMARY.json',{'status':'RUNNING','completed':rows})
  if comparison['status']!='PASS':raise AssertionError('Historical comparison failed; preserved actual data: '+case['id'])
 final={'status':'PASS','cases':rows,'mechanical_geometry':mechanical,'elapsed_seconds':time.monotonic()-started,
  'scope':'Four CPC7 N67 reference trajectories; guard contrast14vs6responses, revised L03 and13other retained, opposite-history reserve; not integration into reconstruction MAIN'}
 put(out/'SUMMARY.json',final);print(json.dumps({'status':'PASS','cases':len(rows),'seconds':final['elapsed_seconds']}))
if __name__=='__main__':main()
