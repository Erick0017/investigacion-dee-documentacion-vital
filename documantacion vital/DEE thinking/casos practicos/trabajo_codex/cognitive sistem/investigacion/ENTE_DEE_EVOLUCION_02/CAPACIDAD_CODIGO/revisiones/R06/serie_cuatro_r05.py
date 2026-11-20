"""Finite repeated4-input use, no renewal of memory or input sites."""
from pathlib import Path
import argparse,ctypes,gzip,json,os,sys,time
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'sistema'));sys.path.insert(0,str(HERE))
from app.lives import Store
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import cierre_funcional_cf01 as cf
from capacidades import ente_operativo_01_core as core
from app.native_tools import digest_file,physical
import fanin_r01 as fanin
FRAMES=[[3,18,6,0],[6,15,0,6],[4,15,2,3],[7,23,3,2],
        [10,19,1,5],[8,17,4,2],[9,24,1,1],[5,14,3,2]]
CASES={'SERIAL16':FRAMES[:4],'SERIAL32':FRAMES}
def ram():
    class PMC(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong)]+[(v,ctypes.c_size_t)for v in('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]
    k=ctypes.WinDLL('kernel32',use_last_error=True);p=ctypes.WinDLL('psapi',use_last_error=True)
    k.GetCurrentProcess.restype=ctypes.c_void_p;p.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.POINTER(PMC),ctypes.c_ulong];p.GetProcessMemoryInfo.restype=ctypes.c_int
    c=PMC();c.cb=ctypes.sizeof(c);okay=p.GetProcessMemoryInfo(k.GetCurrentProcess(),ctypes.byref(c),c.cb)
    return{'peak_working_set_bytes':int(c.PeakWorkingSetSize),'working_set_bytes':int(c.WorkingSetSize)}if okay else{'unavailable':True,'winerror':ctypes.get_last_error()}
def experiment(a,frames):
    initial=physical(a.world);rows=[];old=core._sample
    def passive(a,plan,detailed):
        r=old(a,plan,detailed);r['fanin']={'targets':[body.obs(a,p)for p in[(5,13,15),(7,13,15)]],
          'extra_sites':[body.obs(a,p)for p in[(4,13,16),(8,13,16),(6,13,15),(6,13,16)]]};return r
    core._sample=passive
    try:
        for values in frames:
            extra=fanin.submit_extra(a,values);r=core.external_episode(a,public=values[:2],reference=12,actuator='nulled',feedback='omit',trace=True)
            L=values[0]+values[2];R=values[1]+values[3];target=1 if L+12>=R else-1
            f=next(f for f in r['frames']if f['tick']==extra['expected_arrival']);targets=f['fanin']['targets']
            rows.append({'values':values,'native':r,'extra':extra,'extra_receipts':body.receipts(a,extra['requests']),
              'auditor_only':{'L':L,'R':R,'target':target,'command':r['formed_native_command'],
                 'matches':r['formed_native_command']==target,'targets':targets,'loads_equal_sums':[q['s_reg']for q in targets]==[L,R]}})
    finally:core._sample=old
    return{'revision':'EO02.fanin4.continuity.r05','rows':rows,'physical_before':initial,'physical_after':physical(a.world,occupation=True),'memory_after':cf.witness(a),
       'scope':'4 variables jointly per action,16/32 observations serially in4/8frames. Not16/32joint capacity; no feedback used for these diagnostic pulses.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--case',choices=CASES,required=True);args=p.parse_args()
    dest=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02/capacidad'/('SERIE_R05_'+args.case+'.json.gz')
    if dest.exists():raise FileExistsError(dest)
    sources={str(f):digest_file(f)for f in(HERE/'fanin_r01.py',Path(__file__))};archive=HERE/'revisiones/R05';archive.mkdir(parents=True,exist_ok=True)
    for f in(HERE/'fanin_r01.py',Path(__file__)):
        d=archive/f.name
        if d.exists()and digest_file(d)!=digest_file(f):raise ValueError('Source revision conflict')
        if not d.exists():d.write_bytes(f.read_bytes())
    store=Store();life='AUX_EO02_CAP_R05_'+args.case;fork=store.fork('EO01_MAIN',life,kind='EO02_CAPACITY_DIAGNOSTIC_EXACT_FORK');beg=time.monotonic()
    result=store.mutate(life,'EO02_CAPACITY4_R05',lambda a:experiment(a,CASES[args.case]),details={'frames':CASES[args.case],'no_native_reset':True})
    rec=store.record(life);out={'case':args.case,'life_id':life,'parent':fork['parent'],'sources':sources,'elapsed_seconds':time.monotonic()-beg,'ram':ram(),
       'snapshot':rec['snapshot'],'snapshot_bytes':rec['storage']['encoded_bytes'],'result':result}
    with gzip.open(dest,'wt',encoding='utf8',compresslevel=6)as f:json.dump(out,f,ensure_ascii=False,allow_nan=False)
    q=result['result'];print(json.dumps({'case':args.case,'path':str(dest),'tick':result['INSTRUMENTO']['tick'],'elapsed_seconds':out['elapsed_seconds'],'ram':out['ram'],
      'rows':[r['auditor_only']for r in q['rows']],'extra_status':[v['receipt']['status']for r in q['rows']for v in r['extra_receipts']],
      'own':[q['memory_after']['own'][i]['s_reg']for i in(0,1)]},ensure_ascii=False))
if __name__=='__main__':main()
