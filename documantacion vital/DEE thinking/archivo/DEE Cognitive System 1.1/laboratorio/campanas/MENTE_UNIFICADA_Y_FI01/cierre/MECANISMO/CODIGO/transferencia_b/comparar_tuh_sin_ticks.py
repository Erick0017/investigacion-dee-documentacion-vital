"""Zero-tick exact full-world comparison at the shared post-lesson19 age.

One full base plus exact sparse deltas are a lossless export, not a summary of
selected ports. Public operation histories are retained separately from RAW.
"""
import gc,gzip,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import frontend_b01_r2 as f
OUT=f.OUT.parent/'B02'
def digest_array(a):
    h=hashlib.sha256()
    for v in a:h.update(struct.pack('<Q',int(v)))
    return h.hexdigest()
def public(x,depth=0):
    if x is None or isinstance(x,(str,int,float,bool)):return x
    if isinstance(x,bytes):return {'bytes_hex':x.hex()}
    if isinstance(x,dict):return {str(k):public(v,depth+1)for k,v in sorted(x.items(),key=lambda z:str(z[0]))}
    if isinstance(x,(tuple,list)):return [public(v,depth+1)for v in x]
    if hasattr(x,'name')and hasattr(x,'value')and isinstance(x.name,str)and isinstance(x.value,int):return {'type':type(x).__name__,'enum_name':x.name,'enum_value':int(x.value)}
    if depth>7:return {'type':type(x).__name__,'not_exported':'depthlimit'}
    return {'type':type(x).__name__,'fields':{k:public(getattr(x,k),depth+1)for k in dir(x)if not k.startswith('_')and not callable(getattr(x,k))}}

def main():
    authorization,ni=f.bootstrap()
    from dee_thinking.persistence import load_world_snapshot
    from dee_thinking.consolidated import exact_receipt
    data={};base_raw=base_clock=None
    for arm in('U','T','H'):
        p=OUT/(arm+'_LESSONS_2.json.gz');primary=json.loads(gzip.decompress(p.read_bytes()));ins=primary['INSTRUMENTO'];tick=ins['tick'];expected=ins['snapshot_sha256']
        candidates=list((f.SYSTEM/'estado/checkpoints').glob(ins['life_id']+'.T'+str(tick)+'.*.deetsnap.gz'))
        found=[p for p in candidates if f.digest(p)==expected]
        if len(found)!=1:raise ValueError('No unique exact original complete checkpoint for'+arm)
        cp=found[0];f.memory_guard();w,proof=load_world_snapshot(cp);before=int(w.runtime.current_tick)
        if before!=30891:raise ValueError('No clock equalization permitted')
        raw=[str(int(v))for v in w.runtime.raw_copy()];clock=[str(int(v))for v in w.runtime.clock_copy()]
        receipts=[exact_receipt(r)for r in w.runtime.receipts()]
        row={'snapshot_path':str(cp),'snapshot_sha256':expected,'snapshot_bytes':cp.stat().st_size,'primary':p.name,'primary_sha256':f.digest(p),'tick_before':before,'tick_after':int(w.runtime.current_tick),'N':67,
          'raw_sha256':digest_array(raw),'clock_sha256':digest_array(clock),'interfaces':[public(i)for i in w.interfaces],'protocols':[public(i)for i in w.protocols],
          'channel_names':sorted(w.runtime.channel_names),'receipts':receipts,'receipt_status_counts':dict(Counter(r['status']for r in receipts)),
          'unfinished_receipts':[r for r in receipts if r['status']not in('applied','cancelled','failed')and not r['status'].startswith('rejected')],
          'snapshot_metadata_entries_exact':dict(w.runtime.snapshot_metadata_entries),'load_proof':proof}
        if arm=='U':
            base_raw,base_clock=raw,clock;row['raw']=raw;row['clock']=clock
        else:
            row['base']='U';row['raw_delta']=[{'index':j,'site':[j//4489,(j//67)%67,j%67],'base_raw':base_raw[j],'raw':v}for j,v in enumerate(raw)if v!=base_raw[j]]
            row['clock_delta']=[{'index':j,'base_clock':base_clock[j],'clock':v}for j,v in enumerate(clock)if v!=base_clock[j]]
        data[arm]=row;del w,raw,clock,receipts;gc.collect();f.memory_guard()
    comparisons=[]
    for arm in('T','H'):
        r=data[arm];u=data['U'];comparisons.append({'other':arm,'base':'U','tick':30891,'raw_differences':len(r['raw_delta']),'clock_differences':len(r['clock_delta']),
          'raw_locations':[x['site']for x in r['raw_delta']],'interfaces_equal':r['interfaces']==u['interfaces'],'protocols_equal':r['protocols']==u['protocols'],
          'unfinished_receipts_equal':r['unfinished_receipts']==u['unfinished_receipts'],
          'scope':'Physical full-field comparison only; interface declarations, terminal receipts and biography metadata can differ. Not total causal-state identity.'})
    result={'schema':'MUFI01.BT.TUH.full_arrays.lossless.v1','authorization':authorization,'code_sha256':f.digest(__file__),'native_ticks_executed':0,
      'worlds':data,'comparisons':comparisons,'lossless_reconstruction':'U contains every exact uint64 RAW/clock as decimal strings. T/H replace only the listed indices; unchanged indices are U. Hashes verify all reconstructed little-endian uint64 arrays.',
      'max_simultaneous_loaded_worlds':1,'peak_RSS_bytes':f.memory_guard()}
    f.dump(OUT/'T_U_H_COMPLETO_T30891.json.gz',result);print(json.dumps({'comparisons':comparisons,'sha256':f.digest(OUT/'T_U_H_COMPLETO_T30891.json.gz')}))
if __name__=='__main__':main()
