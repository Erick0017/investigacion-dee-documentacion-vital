"""Load/use/save an already acquired selector life, no T0 or hidden reset.

Candidate lab procedure, not a second manager. Root may expose the same helper
through Cognitive's admitted life/profile. This CLI preserves a full nativeworld.
"""
import argparse,gzip,hashlib,importlib.util,json,re
from pathlib import Path
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation
from dee_thinking.persistence import load_world_snapshot,save_world_snapshot,encode_metadata
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];OUT=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/seleccion'
def module(name,file):
    s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
a=module('accretion','selector_acrecion_base.py');worker=module('worker','worker_fuente_utilizada.py')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):
    if p.exists():raise FileExistsError(p)
    b=json.dumps(x,ensure_ascii=False,sort_keys=True).encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',type=Path,required=True);p.add_argument('--identificador',required=True);p.add_argument('--observaciones',default='7,13');p.add_argument('--q',type=int);z=p.parse_args()
    if not re.fullmatch('[A-Za-z0-9_]+',z.identificador):raise ValueError('Bounded local identifier')
    target=OUT/(z.identificador+'.json.gz')
    if target.exists():raise FileExistsError(target)
    w,proof=load_world_snapshot(z.snapshot);before=int(w.runtime.current_tick);q=z.q if z.q is not None else before+10
    if q<before+1 or (q+3)%391==0:raise ValueError('Outside declared genericqueryphase; no state advancement or silent reschedule')
    observe=lambda pos:exact_observation(w.runtime.observe(d.Coordinate(*pos)))
    pre={'tick':before,'A':observe((32,32,33)),'B':observe((34,32,33))}
    a.declare(w,prefix='operational');requests=a.query(w,q,5,prefix='operational');rows=[]
    for t in range(q,q+7):
        w.run_until(t);rows.append({'tick':t,'A':observe((32,32,33)),'B':observe((34,32,33)),'E':observe((33,33,33)),'reader':a.read(w)})
    read=next(x['reader']for x in rows if x['tick']==q+6);choice=read['choice'];folder=OUT/(z.identificador+'.worker');folder.mkdir(exist_ok=False);receipt=None;request=None;actual=None
    if choice in(-1,1):
        request={'executed_worker':choice,'raw_observations':[int(v)for v in z.observaciones.split(',')],'capacity_credit':0,'domain':'trabajadores','pending_transaction':None,'attempt':1,'native_tick':q+6,'output_directory':str(folder)}
        receipt=worker.process(request);out=folder/receipt['output_name']
        import base64
        actual={'name':out.name,'sha256':sha(out),'bytes':out.stat().st_size,'base64':base64.b64encode(out.read_bytes()).decode()}
    operation={'native_read':read,'physical_decision':choice,'executed':choice in(-1,1),'worker_request':request,'worker_receipt':receipt,'actual_output':actual,'opportunity_success':bool(receipt and receipt['accepted']),'deadline_or_worker_failure':not bool(receipt and receipt['accepted'])}
    for t in range(q+7,q+11):
        w.run_until(t);rows.append({'tick':t,'A':observe((32,32,33)),'B':observe((34,32,33)),'E':observe((33,33,33)),'reader':a.read(w)})
    meta={'identity':z.identificador,'parent_sha256':sha(z.snapshot),'parent_tick':before,'tick':int(w.runtime.current_tick),'requests':requests,'last_operation':operation,'scope':'Exact acquiredworldcontinuation; nofeedback/reteaching inthisoneusage. Sensorandactuatormapping unchanged.'}
    w.runtime.set_snapshot_metadata('MUFI01.selector.operational.v1',encode_metadata(meta));final=OUT/(z.identificador+'.T'+str(w.runtime.current_tick)+'.deetsnap.gz');save_world_snapshot(w,final,compress=True)
    result={'schema':'MUFI01.selector.operational.v1','identifier':z.identificador,'parent':{'path':str(z.snapshot.resolve()),'sha256':sha(z.snapshot),'tick':before,'load_proof':proof},'mode':'operational','before':pre,'rows':rows,'operation':operation,'requests':[a.receipt(w,r)for r in requests],'snapshot':{'path':str(final),'sha256':sha(final),'tick':int(w.runtime.current_tick)},'source_sha256':sha(Path(__file__)),'scope':'Sameexistingacquiredworld, newquery, actualworker, fullsave. No initialrecipe orcorrectchoice input.'}
    put(target,result);print(json.dumps({'identifier':z.identificador,'before':before,'after':int(w.runtime.current_tick),'choice':choice,'worker_accepted':operation['opportunity_success'],'snapshot':str(final),'sha256':sha(final)}),flush=True)
if __name__=='__main__':main()
