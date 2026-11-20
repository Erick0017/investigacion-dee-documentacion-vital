"""Zero-tick lossless RAW/clock export of complete B06 diagnostic snapshots.

These fields are NOT a replacement for a complete continuable snapshot.
The final files include the old-six material panel after passive17038.
"""
import gc,gzip,hashlib,json,os
from array import array
from pathlib import Path
from ensayar_arbol_b05_r1 import ROOT,LAB,sha,dump,native_imports,internal_A_close,memory_guard

def main():
    authorization=internal_A_close(LAB/'CIERRE_INTERNO_A.json');os.environ.update(OMP_NUM_THREADS='1')
    ni=native_imports();Store=ni[3];s=Store()
    from dee_thinking.persistence import load_world_snapshot
    source=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/escalamiento/B06_CADENCE_NOISE_R1'
    out=source/'CAMPOS_COMPLETOS_0_TICKS';out.mkdir(parents=True,exist_ok=True);rows=[]
    def write_array(values,label):
        v=array('Q',values)
        if __import__('sys').byteorder!='little':v.byteswap()
        raw=v.tobytes();h=hashlib.sha256(raw).hexdigest();p=out/(h+'.uint64le.bin.gz')
        if not p.exists():
            with p.open('xb')as f:
                with gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0)as z:z.write(raw)
        return {'file':p.name,'sha256_uncompressed':h,'sha256_compressed':sha(p),'entries':len(v),
          'uncompressed_bytes':len(raw),'compressed_bytes':p.stat().st_size,'format':'Exact uint64 little-endian; engine raw_copy/clock_copy order'}
    for delta in(2,16):
        record=s.record('FI01_B06_R1_cadence_'+str(delta))
        for label,p in[('before_both_frames',source/('cadence_'+str(delta)+'.ALL_PENDING.T16640.deetsnap.gz')),
                        ('after_material_old_six',s.snapshot(record))]:
            w,_=load_world_snapshot(p);rt=w.runtime;tick=int(rt.current_tick);memory_guard()
            raw=list(rt.raw_copy());clocks=list(rt.clock_copy());occupied=sum(bool(x&0xffffffff)for x in raw)
            rows.append({'delta':delta,'label':label,'tick':tick,'N':int(rt.dimension),'sites':len(raw),'occupied':occupied,
              'raw':write_array(raw,'RAW'),'clocks':write_array(clocks,'clocks'),
              'complete_snapshot_source':str(p),'complete_snapshot_sha256':sha(p),
              'channels':list(rt.channel_names),'snapshot_metadata_keys':list(dict(rt.snapshot_metadata_entries)),
              'scope':'No native tick advanced. Fields are exact but omit interfaces, queued events and operational progress; complete source remains local.'})
            print(json.dumps({'delta':delta,'label':label,'tick':tick,'occupied':occupied}),flush=True)
            del raw,clocks,w,rt;gc.collect();memory_guard()
    dump(out/'INDICE_CAMPOS.json',{'authorization':authorization,'native_ticks':0,'rows':rows,'script_sha256':sha(__file__),
      'coverage_limit':'Passive-horizon17038 was measured but not snapshotted; final17427 follows six real queries. Never label these arrays as17038 or as a full continuable state.'})
if __name__=='__main__':main()
