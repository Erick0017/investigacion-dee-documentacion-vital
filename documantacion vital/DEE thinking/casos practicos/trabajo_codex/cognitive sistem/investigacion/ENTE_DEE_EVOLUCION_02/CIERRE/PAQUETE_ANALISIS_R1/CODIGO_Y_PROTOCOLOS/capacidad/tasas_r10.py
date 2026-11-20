"""Separate information from rate on R10; no main-world advancement.

INFO2/4/8 keep14 sensor carriers and12 generic downstream resources per frame.
SERIAL/BURST/CONCURRENT keep52 requested carriers and2cycles. In fast arms the
second native window has resources only; it is never relabeled a data answer.
"""
from pathlib import Path
import argparse,gzip,json,os,sys,time
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'sistema'));sys.path.insert(0,str(HERE))
from app.lives import Store
from app.native_tools import digest_file,physical
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import cierre_funcional_cf01 as cf
from capacidades import ente_evolucion_02_core as core
from piloto_sensorial_r10 import Gate
from serie_cuatro_r05 import ram
from validacion_final_r10 import BASE
import sensorial_r10 as sensor
A=[4,5,6,7,2,3,4,5];B=[5,7,1,2,3,4,5,6]
CASES={'INFO2':[[2,7,0,0,0,0,0,0]],'INFO4':[[2,7,2,1,0,0,0,0]],'INFO8':[[1,3,2,4,3,2,4,6]],
       'SERIAL16':[A,B],'BURST16':[A,B],'CONCURRENT16':[A,B]}
def one(a,values,second=None,shift=None,resource_only=False):
    inputs=None if resource_only else sensor.submit(a,values);secondary=None
    if second is not None:
        original_plan=core._plan
        def shifted(a):
            p=original_plan(a);p['critical_tick']+=shift;return p
        core._plan=shifted
        try:secondary=sensor.submit(a,second)
        finally:core._plan=original_plan
    original_sample=core._sample
    def passive(a,p,d):
        q=original_sample(a,p,d);q['r10']={'targets':[body.obs(a,p)for p in[(5,13,15),(7,13,15)]]};return q
    core._sample=passive
    try:r=core.external_episode(a,public=[0,0],reference=4,actuator='nulled',feedback='omit',trace=True,environment=None if resource_only else Gate(values))
    finally:core._sample=original_sample
    return{'values':None if resource_only else values,'second_values':second,'secondary_shift':shift,'resource_only_not_a_data_answer':resource_only,
      'inputs':inputs,'input_receipts':[]if inputs is None else body.receipts(a,inputs['requests']),
      'secondary':secondary,'secondary_requests':[]if secondary is None else body.receipts(a,secondary['requests']),'native':r}
def run(a,case):
    before=physical(a.world);frames=CASES[case]
    if case in('BURST16','CONCURRENT16'):
        rows=[one(a,frames[0],frames[1],1 if case=='BURST16'else 0),one(a,[0]*8,resource_only=True)]
    else:rows=[one(a,v)for v in frames]
    return{'case':case,'rows':rows,'physical_before':before,'physical_after':physical(a.world,occupation=True),'memory_after':cf.witness(a),
      'assistance':'Same fixed R10geometry, ports, output reader and2-cycle age/resource exposure. No targets/sums enter DEE; resource-only output excluded from data response counts.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--case',choices=CASES,required=True);args=p.parse_args()
    dest=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02/capacidad'/('R10_TASA_'+args.case+'.json.gz')
    if dest.exists():raise FileExistsError(dest)
    files=[Path(__file__),HERE/'sensorial_r10.py',HERE/'piloto_sensorial_r10.py',ROOT/'sistema/capacidades/ente_evolucion_02_core.py'];archive=HERE/'revisiones/R10_TASA';archive.mkdir(parents=True,exist_ok=True)
    for f in files:
        t=archive/f.name
        if t.exists()and digest_file(t)!=digest_file(f):raise ValueError('Source changed')
        if not t.exists():t.write_bytes(f.read_bytes())
    store=Store();life='AUX_EO02_CAP_R10_TASA_'+args.case;fork=store.fork(BASE,life,kind='R10_RATE_AND_INFORMATION_CONTRAST');beg=time.monotonic()
    r=store.mutate(life,'R10_RATE_'+args.case,lambda a:run(a,args.case),details={'predefined_case':CASES[args.case],'phase_offset':1 if args.case=='BURST16'else 0,'resource_equalization':True})
    out={'case':args.case,'life_id':life,'parent':fork['parent'],'sources':{str(f):digest_file(f)for f in files},'elapsed_seconds':time.monotonic()-beg,'ram':ram(),'result':r}
    with gzip.open(dest,'wt',encoding='utf8',compresslevel=6)as f:json.dump(out,f,ensure_ascii=False,allow_nan=False)
    rows=[]
    for q in r['result']['rows']:
        n=q['native'];c=n['row']['critical_tick'];f=next(f for f in n['frames']if f['tick']==c-17)
        rows.append({'values':q['values'],'second_values':q['second_values'],'resource_only':q['resource_only_not_a_data_answer'],'cmd':n['formed_native_command'],
          'targets':[v['s_reg']for v in f['r10']['targets']],'requests':len(n['requests'])+len(q['input_receipts'])+len(q['secondary_requests']),
          'statuses':[v['receipt']['status']for v in n['requests']+q['input_receipts']+q['secondary_requests']]})
    print(json.dumps({'case':args.case,'path':str(dest),'tick':r['INSTRUMENTO']['tick'],'ram':out['ram'],'rows':rows},ensure_ascii=False))
if __name__=='__main__':main()
