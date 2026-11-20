"""Finite paired full-fork calibration BEFORE raw-tree scaling. Exact revision1.

No parent mutation, no memory writes/clear, no adaptive reader or fallback.
This is diagnostic direct-datum transduction, never a128-input result.
"""
from __future__ import annotations
import gc,gzip,hashlib,json,os,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from arbol_umbral_adquirido_b01 import internal_A_close,native_imports,memory_guard
LAB=HERE.parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema'
OUT=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/escalamiento/B02_ENDPOINT_R1'
PARENT='MU_MAIN';CUT='estado/checkpoints/MU_MAIN.T16634.ba61eac94a01.deetsnap.gz'
EXPECTED='b6c02df2e804b167b85f9e8fd849e091227b81ccfd7a49e442f67156944c71ad'
E=(15,15,15);D=(14,15,15)
ARMS=[('query_only',None,3,True,D),('datum0_qplus3',0,3,True,D),('datum2_qplus3',2,3,True,D),
 ('datum0_qplus2',0,2,True,D),('datum2_qplus2',2,2,True,D),('datum0_qplus4',0,4,True,D),
 ('datum2_qplus4',2,4,True,D),('datum2_no_query',2,3,False,D),
 ('sham2_qplus3',2,3,True,(14,15,23)),('background',None,3,False,D)]

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,o):
    if p.exists():raise FileExistsError(p)
    p.parent.mkdir(parents=True,exist_ok=True)
    data=json.dumps(o,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
    if p.suffix=='.gz':
        with p.open('xb')as f:
            with gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0)as z:z.write(data)
    else:p.write_bytes(data)

def execute(a,arm,ni,sel):
    d,encode,decode,Store,Adapter,now,physical,body,ep=ni
    label,load,offset,query,site=arm;q=a.tick+8;requests=[]
    pre=physical(a.world,occupation=True);pre_data=body.obs(a,site)
    # Direct legal input, not a forced write. Occupied/raw0 admission stays native.
    if load is not None:requests.append(body.send(a,'FI01.B02.direct.'+label,site,(0,0,0),q+offset,load))
    if query:requests.extend(sel.query(a.world,q,5,'MU.selector'))
    points={tuple((E[i]+v[i])%67 for i in range(3))for v in((x,y,z)for x in range(-3,4)for y in range(-3,5)for z in range(-4,5))}
    points.update((site,D));rows=[];answer=None
    for t in range(q-1,q+9):
        memory_guard();a.run_until(t)
        rows.append({'tick':a.tick,'sites':[body.obs(a,p)for p in sorted(points)]})
        if t==q+6:answer=sel.read(a.world,E,67)
    after_read=physical(a.world,occupation=True)
    # Two torus crossing scales, no material retention probes added.
    a.run_until(q+8+2*67);memory_guard()
    result={'label':label,'initial':pre,'direct_datum_pre':pre_data,'load':load,'site':site,'query_present':query,'query_tick':q,
      'datum_tick':q+offset if load is not None else None,'fixed_reader_tick':q+6,'reader':answer,'frames':rows,
      'requests':[sel.receipt(a.world,r)if 'site'not in r else {**r,'receipt':sel.exact_receipt(a.world.runtime.receipt(r['id']))}for r in requests],
      'after_read':after_read,'after_2N_passive':physical(a.world,occupation=True),
      'final_references':[body.obs(a,sel.at(E,v))for v in[(-1,-1,0),(1,-1,0)]],
      'scope':'Direct legal datum/reader calibration in exact own fork. NOT raw-tree success, learned policy, new meaning, or parent improvement.'}
    return result

def main():
    authorization=internal_A_close(LAB/'CIERRE_INTERNO_A.json')
    if digest(SYSTEM/CUT)!=EXPECTED:raise ValueError('Explicit source snapshot differs; no fallback')
    os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    ni=native_imports();d,encode,decode,Store,Adapter,now,physical,body,ep=ni
    from capacidades import selector_acrecion_nativo as sel
    store=Store();before_record=digest(store.life_dir(PARENT)/'VIDA.json');before_active=digest(SYSTEM/'estado/ACTIVO.json')
    dump(OUT/'PROTOCOLO.json',{'schema':'FI01.B02.direct_endpoint.R1','before_first_tick':now(),'authorization':authorization,
      'source':CUT,'source_sha256':EXPECTED,'source_tick':16634,'script_sha256':digest(__file__),'arms':ARMS,
      'fixed_codec':'Direct load0/2 atE-X via legal SEM1state1 direction0; native admissions. Query same3pulses5,0,0, all atq. Read same3actuator sites atq+6.',
      'predictions_not_actor_inputs':'Baseline acquiredD<0; adding material atE-X may alter its context. This is a hypothesis, not expected-answer injection.',
      'sample_scope':'10exact-prefix branches, not10independent learning histories. One Runtime at a time. No parent mutation.'})
    summary=[]
    for arm in ARMS:
        label=arm[0];life='FI01_B02_EP_R1_'+label
        if store.life_dir(life).exists():raise FileExistsError('No repeat/rebuild of existing diagnostic life: '+life)
        fork=store.fork(PARENT,life,kind='B02_PAIRED_ENDPOINT_DIAGNOSTIC',checkpoint=CUT);gc.collect();memory_guard()
        result=store.mutate(life,'B02_DIRECT_ENDPOINT_R1',lambda a:execute(a,arm,ni,sel),{'source_sha256':EXPECTED,'frozen_arm':arm,'source_revision':digest(__file__)})
        dump(OUT/(label+'.json.gz'),result)
        row={'label':label,'life':life,'choice':result['result']['reader']['choice'],'end_tick':result['physical']['tick'],
          'receipts':[{k:r[k]for k in('id','receipt')}for r in result['result']['requests']],
          'snapshot_sha256':result['INSTRUMENTO']['snapshot_sha256'],'output_sha256':digest(OUT/(label+'.json.gz'))}
        summary.append(row);print(json.dumps(row),flush=True);del result;gc.collect();memory_guard()
    integrity={'original_record_unchanged':before_record==digest(store.life_dir(PARENT)/'VIDA.json'),
      'original_snapshot_unchanged':EXPECTED==digest(SYSTEM/CUT),'active_unchanged':before_active==digest(SYSTEM/'estado/ACTIVO.json')}
    dump(OUT/'RESUMEN.json',{'arms':summary,'integrity':integrity,'peak_process_bytes':memory_guard(),'finished_utc':now()})
    if not all(integrity.values()):raise AssertionError('Protected original identity changed externally; do not certify protection')
if __name__=='__main__':main()
