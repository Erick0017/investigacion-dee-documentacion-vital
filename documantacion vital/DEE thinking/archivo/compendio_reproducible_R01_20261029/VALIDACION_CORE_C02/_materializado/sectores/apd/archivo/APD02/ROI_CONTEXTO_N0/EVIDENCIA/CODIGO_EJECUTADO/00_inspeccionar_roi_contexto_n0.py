"""One-at-a-time passive full-field/ROI export from four already saved AUX snapshots, zero ticks."""
import argparse,gc,gzip,hashlib,itertools,json,shutil,sys
from array import array
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
 with p.open('xb')as f:f.write(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def coord(index,order,n):
 v={axis:(index//(n**i))%n for i,axis in enumerate(order)};return[v['x'],v['y'],v['z']]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--system',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 if a.out.exists():raise FileExistsError('Fresh passive analysis only')
 a.out.mkdir(parents=True);sys.path.insert(0,str(a.system.resolve()))
 from app.lives import load_adapter
 from app.native_tools import physical,observe
 from app.process_control import protect_current,current_resources
 protect_current(output=a.out/'RECURSOS.json',memory_limit=512*1024*1024)
 protocol=json.loads((a.evidence/'ANTES_DEL_PRIMER_TICK.json').read_bytes())['protocol'];origin=protocol['origin'];sources=[];states=[]
 files=[Path(__file__),a.evidence/'ANTES_DEL_PRIMER_TICK.json',a.system/'app/native_tools.py',a.system/'app/lives.py']
 for i,f in enumerate(files):
  dst=a.out/'CODIGO_EJECUTADO'/(str(i).zfill(2)+'_'+f.name);dst.parent.mkdir(exist_ok=True);shutil.copyfile(f,dst);sources.append({'source':str(f),'file':dst.relative_to(a.out).as_posix(),'sha256':sha(dst),'bytes':dst.stat().st_size})
 emit(a.out/'PROTOCOLO_ANTES_DE_CARGAR_N0.json',{'scope':'Zero calls to run/step/update; every full snapshot is an already reached original q+6 state. One Runtime loaded at once. ROIfixed E+[-4..4]x[-3..4]x[-4..4] and exact global sparse RAW+clockRLE are an auditor tool, never an actor reader or operational state replacement.','sources':sources,'input_snapshot_rows':[{'family':family,'bit':arm,'file':str(a.evidence/family/('ARM'+str(arm))/'LECTURA_0_COMPLETO.deetsnap.gz'),'sha256':sha(a.evidence/family/('ARM'+str(arm))/'LECTURA_0_COMPLETO.deetsnap.gz')}for family in('plane','above')for arm in(0,1)],'native_ticks_to_advance':0})
 for family in('plane','above'):
  for bit in(0,1):
   path=a.evidence/family/('ARM'+str(bit))/'LECTURA_0_COMPLETO.deetsnap.gz';adapter=load_adapter('fisica_directa',path)
   try:
    before=physical(adapter.world);n=int(adapter.world.runtime.dimension);raw=array('Q',adapter.world.runtime.raw_copy());clocks=array('Q',adapter.world.runtime.clock_copy());nonzero=[i for i,v in enumerate(raw)if v]
    orders=[]
    for order in itertools.permutations('xyz'):
     if all(int(observe(adapter.world,coord(i,order,n))['raw'])==raw[i]for i in nonzero):orders.append(order)
    if len(orders)!=1:raise ValueError('Coordinate ABI not uniquely verified on all nonzero RAW cells: '+str(orders))
    order=orders[0];runs=[]
    for i,value in enumerate(clocks):
     if runs and runs[-1]['clock']==str(value):runs[-1]['count']+=1
     else:runs.append({'start':i,'count':1,'clock':str(value)})
    roi=[]
    for x in range(-4,5):
     for y in range(-3,5):
      for z in range(-4,5):roi.append(observe(adapter.world,[(origin[j]+(x,y,z)[j])%n for j in range(3)]))
    after=physical(adapter.world)
    if after!=before:raise ValueError('Passive inspection changed exact RAW/clocks/tick')
    state={'family':family,'raw_missing_bit':bit,'source_snapshot':str(path),'source_snapshot_sha256':sha(path),'physical_before':before,'physical_after':after,'tick_unchanged':True,'coordinate_ABI_fast_to_slow':list(order),'ABI_validation':'Every nonzero RAW index checked against official coordinate observe; unique among six axis permutations. ROI includes RAW0 and inactive fields.','complete_sparse_RAW':[{'index':i,'raw':str(raw[i]),'site':coord(i,order,n)}for i in nonzero],'complete_clock_RLE':runs,'full_field_size':len(raw),'roi':roi,'native_ticks_advanced':0,'scope':'Complete RAW/clocks only are reconstructible, not operational interfaces/queues/environment/progress. The complete native snapshot remains at its exact local locator; do not restore a life from these analysis arrays.'}
    file=a.out/(family+'_BIT'+str(bit)+'_N0.json.gz');emit(file,state);states.append({'family':family,'bit':bit,'file':file.name,'sha256':sha(file),'snapshot_sha256':sha(path),'physical':before,'nonzero_RAW':len(nonzero),'clock_runs':len(runs),'new_native_ticks':0})
   finally:del adapter;gc.collect()
 emit(a.out/'RESULTADO_N0.json',{'states':states,'sources':sources,'new_native_ticks':0,'resources':current_resources(),'no_new_actor_reader_or_environment_action':True});print(json.dumps({'states':states,'native_ticks':0},sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
