"""Read-only fullRAW/clocks extraction of existing complete snapshots, zero ticks."""
import gzip,hashlib,json,struct
from pathlib import Path
from dee_thinking.persistence import load_world_snapshot
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/seleccion'
PAIRS=[('MUFI_S06_TOUCH_A.T392','MUFI_S06_TOUCH_B.T392'),('MUFI_S06_TOUCH_A.T910','MUFI_S06_TOUCH_B.T910'),('MUFI_S08_REAL_MINUS.T1000','MUFI_S08_OMITTED_MINUS.T1000'),('MUFI_S08_REAL_MINUS.T1000','MUFI_S08_PHASE1_MINUS.T1000'),('MUFI_S08_REAL_MINUS.T1174','MUFI_S08_OMITTED_MINUS.T1174'),('MUFI_S08_REAL_MINUS.T1956','MUFI_S08_OMITTED_MINUS.T1956'),('MUFI_S08_REAL_MINUS.T2660','MUFI_S08_NULLED_PLUS.T2660')]
def digest(xs):return hashlib.sha256(b''.join(struct.pack('<Q',int(x))for x in xs)).hexdigest()
def main():
    dst=OUT/'MUFI_G01_ARRAYS.json.gz'
    if dst.exists():raise FileExistsError(dst)
    worlds={}
    for name in sorted({x for pair in PAIRS for x in pair}):
        p=OUT/(name+'.deetsnap.gz');w,proof=load_world_snapshot(p);t=int(w.runtime.current_tick);raw=[str(int(v))for v in w.runtime.raw_copy()];clock=[str(int(v))for v in w.runtime.clock_copy()]
        worlds[name]={'N':67,'tick_before':t,'tick_after':int(w.runtime.current_tick),'snapshot_path':str(p),'snapshot_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'load_proof':proof,'raw':raw,'clock':clock,'raw_le_uint64_sha256':digest(raw),'clock_le_uint64_sha256':digest(clock),'all_material_receipts':None}
        del w
    pairs=[]
    for x,y in PAIRS:
        u,v=worlds[x],worlds[y];ri=[i for i,(a,b)in enumerate(zip(u['raw'],v['raw']))if a!=b];ci=[i for i,(a,b)in enumerate(zip(u['clock'],v['clock']))if a!=b]
        pairs.append({'left':x,'right':y,'raw_differences':[{'index':i,'site':[i//(67*67),(i//67)%67,i%67],'left_raw':u['raw'][i],'right_raw':v['raw'][i]}for i in ri],'clock_differences':[{'index':i,'left_clock':u['clock'][i],'right_clock':v['clock'][i]}for i in ci]})
    result={'schema':'MUFI01.full_arrays.read_only.v1','identifier':'MUFI_G01_ARRAYS','native_ticks_executed':0,'worlds':worlds,'comparisons':pairs,'scope':'Complete physicalRAWandclock arrays, not all causaloperationalmetadata. Fullsnapshots indexedandretained; environment/queues not declaredidentical fromarrayequality alone.'}
    b=json.dumps(result,sort_keys=True,ensure_ascii=False).encode();dst.write_bytes(gzip.compress(b,mtime=0));print(json.dumps({'worlds':len(worlds),'pairs':[(p['left'],p['right'],len(p['raw_differences']),len(p['clock_differences']))for p in pairs],'bytes':dst.stat().st_size,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()}),flush=True)
if __name__=='__main__':main()
