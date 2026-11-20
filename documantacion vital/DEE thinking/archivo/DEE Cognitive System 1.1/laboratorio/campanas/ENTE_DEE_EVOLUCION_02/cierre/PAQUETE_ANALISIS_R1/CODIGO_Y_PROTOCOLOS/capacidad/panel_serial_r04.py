"""Fixed finite information/rate/serial-access screen on the same EO01 body.

16 and32 count distinct raw observations in2/4 complete frames, not a joint
16/32-argument decision. The external fixed fixture is not used for feedback.
"""
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
import fanin_r03 as fanin

W1=[3,18,0,0,6,0,0,0];W2=[6,15,0,0,0,6,0,0]
W3=[4,6,2,4,1,3,5,13];W4=[7,9,3,4,2,7,6,7]
CASES={'INFO2':{'relevant_family':2,'frames':[[3,18,0,0,0,0,0,0]]},
       'INFO4':{'relevant_family':4,'frames':[W1]},
       'INFO8':{'relevant_family':8,'frames':[W3]},
       'SERIAL16':{'relevant_family':16,'frames':[W1,W2]},
       'SERIAL32':{'relevant_family':32,'frames':[W1,W2,W3,W4]},
       'BURST16_PLUS1':{'relevant_family':16,'frames':[W1,W2],'burst_shift':1},
       'CONCURRENT16':{'relevant_family':16,'frames':[W1,W2],'burst_shift':0},
       'OBSERVACION_SIN_AMPLIAR':{'relevant_family':8,'frames':[[3,18,0,0,0,0,0,0]],'passive_extra':False}}
SITES={'targets':[(5,13,15),(7,13,15)],'sources':[list(v[1])for v in fanin.SPECS]}

def peak_ram():
    class Counters(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong),
          ('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),
          ('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),
          ('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),
          ('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t)]
    c=Counters();c.cb=ctypes.sizeof(c)
    handle=ctypes.windll.kernel32.GetCurrentProcess()
    good=ctypes.windll.psapi.GetProcessMemoryInfo(handle,ctypes.byref(c),c.cb)
    return {'peak_working_set_bytes':int(c.PeakWorkingSetSize),'working_set_bytes':int(c.WorkingSetSize)}if good else{'unavailable':True}

def secondary(a,values,shift):
    critical=core._plan(a)['critical_tick'];rows=[]
    for name,value in zip(('sin','cos'),values[:2]):
        s=next(s for s in body.get(a)['external_sensors']if s['name']==name)
        rows.append(body.send(a,'EO02.rate.secondary.'+name,s['origin'],s['direction'],critical-22+shift,value))
    for name,site,v,index in fanin.SPECS:
        rows.append(body.send(a,'EO02.rate.secondary.'+name,site,v,critical-18+shift,values[index]))
    return rows

def one_frame(a,values,second=None,shift=None,passive_extra=True):
    extra=fanin.submit_extra(a,values);requests=[]
    if second is not None:requests=secondary(a,second,shift)
    before=cf.witness(a);old=core._sample
    def passive(a,plan,detailed):
        q=old(a,plan,detailed);q['fanin']={k:[body.obs(a,p)for p in sites]for k,sites in SITES.items()};return q
    if passive_extra:core._sample=passive
    try:r=core.external_episode(a,public=values[:2],reference=12,actuator='nulled',feedback='omit',trace=True)
    finally:core._sample=old
    L=sum(values[::2]);R=sum(values[1::2]);want=1 if L+12>=R else-1
    arrival=next(f for f in r['frames']if f['tick']==extra['expected_arrival'])
    targets=arrival.get('fanin',{}).get('targets',[])
    return{'values':values,'second_values':second,'secondary_shift':shift,'before':before,'native':r,
      'extra':extra,'extra_receipts':body.receipts(a,extra['requests']),
      'secondary_requests':body.receipts(a,requests),'after':cf.witness(a),
      'auditor_only':{'L':L,'R':R,'target':want,'command':r['formed_native_command'],
         'matches':r['formed_native_command']==want,'targets':targets,
         'loads_equal_sums':None if not targets else[q['s_reg']for q in targets]==[L,R]},
      'rate_scope':'Two frames sharing ports with0/1tick spacing'if second is not None else'One8-port frame per782ticks'}

def experiment(a,case):
    start=physical(a.world);rows=[];frames=case['frames'];burst='burst_shift'in case
    if burst:rows.append(one_frame(a,frames[0],frames[1],case['burst_shift']))
    else:
        for values in frames:rows.append(one_frame(a,values,passive_extra=case.get('passive_extra',True)))
    return{'revision':'EO02.capacity.r04.serial_and_rate','case':case,'physical_before':start,'rows':rows,
       'physical_after':physical(a.world,occupation=True),'memory_after':cf.witness(a),
       'assistance':'Fixed peripheral codec/schedule and audit-only sums; native reducer and output decide. No action feedback in this diagnostic screen.',
       'joint_arity':8,'sequential_distinct_observations':len(frames)*8,
       'not_joint_16_or32':case['relevant_family']>8,'no_native_memory_reset_between_frames':True}

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',choices=CASES,required=True);args=p.parse_args()
    dest=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02/capacidad'/('PANEL_R04_'+args.case+'.json.gz')
    if dest.exists():raise FileExistsError(dest)
    sources={str(f):digest_file(f)for f in(HERE/'fanin_r03.py',Path(__file__))};archive=HERE/'revisiones/R04';archive.mkdir(parents=True,exist_ok=True)
    for f in(HERE/'fanin_r03.py',Path(__file__)):
        d=archive/f.name
        if d.exists()and digest_file(d)!=digest_file(f):raise ValueError('Source revision conflict')
        if not d.exists():d.write_bytes(f.read_bytes())
    store=Store();life='AUX_EO02_CAP_R04_'+args.case;fork=store.fork('EO01_MAIN',life,kind='EO02_CAPACITY_DIAGNOSTIC_EXACT_FORK');beg=time.monotonic()
    result=store.mutate(life,'EO02_CAPACITY_R04',lambda a:experiment(a,CASES[args.case]),details={'predeclared_case':CASES[args.case],'feedback':'omit','actuator':'nulled'})
    record=store.record(life)
    out={'case':args.case,'life_id':life,'parent':fork['parent'],'sources':sources,'elapsed_seconds':time.monotonic()-beg,'ram':peak_ram(),
         'snapshot':record['snapshot'],'snapshot_bytes':record['storage']['encoded_bytes'],'result':result}
    with gzip.open(dest,'wt',encoding='utf8',compresslevel=6)as f:json.dump(out,f,ensure_ascii=False,allow_nan=False)
    q=result['result'];print(json.dumps({'case':args.case,'primary':str(dest),'elapsed_seconds':out['elapsed_seconds'],'ram':out['ram'],'tick':result['INSTRUMENTO']['tick'],
      'rows':[r['auditor_only']for r in q['rows']],'input_receipts':[v['receipt']['status']for r in q['rows']for v in r['extra_receipts']+r['secondary_requests']],
      'own':[q['memory_after']['own'][i]['s_reg']for i in(0,1)]},ensure_ascii=False))
if __name__=='__main__':main()
