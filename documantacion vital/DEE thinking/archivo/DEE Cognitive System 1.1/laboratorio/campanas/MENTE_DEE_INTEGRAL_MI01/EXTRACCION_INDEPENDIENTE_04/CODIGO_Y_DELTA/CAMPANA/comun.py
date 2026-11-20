"""MI01 experimental receipts around the SAME Cognitive Store/manager.
Not a new participant/controller. A single native writer per invocation.
"""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
L=Path(__file__).resolve().parent;R=L.parents[2];S=R/'sistema';E=R/'evidencia/campanas/MENTE_DEE_INTEGRAL_MI01'
sys.path.insert(0,str(S))
from app.lives import Store
from app.native_tools import atomic_json,physical,observe
from app.process_control import protect_current
protect_current()
def budget(closure=False):
    b=json.loads((L/'PRESUPUESTO.json').read_bytes())
    if time.monotonic()>b['monotonic_deadline']-(0 if closure else b['reserved_closure_seconds']):raise TimeoutError('MI01 fixed cutoff; no restarted budget')
    return b
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def source_bytes():
    records=[];out=E/'FUENTES_POR_SHA256';out.mkdir(exist_ok=True)
    paths=set()
    for m in list(sys.modules.values()):
        p=getattr(m,'__file__',None)
        if p:
            p=Path(p).resolve()
            if p.suffix=='.py'and(p.is_relative_to(S)or p.is_relative_to(L)):paths.add(p)
    for p in sorted(paths):
        h=sha(p);target=out/(h+'.py')
        if not target.exists():shutil.copy2(p,target)
        records.append({'path':str(p.relative_to(R)),'sha256':h,'exact_bytes':str(target.relative_to(R))})
    return records
def fork(parent,name,checkpoint=None,kind='DIAGNOSTIC_COPY'):
    budget();s=Store()
    if s.life_dir(name).exists():raise FileExistsError('No silent restart '+name)
    return s.fork(parent,name,kind=kind,checkpoint=checkpoint)
def command(id,argv,timeout=240):
    budget();p=E/(id+'.json')
    if p.exists():raise FileExistsError('Do not repeat completed operation '+id)
    cmd=[sys.executable,'-I','-B','-X','utf8',str(S/'gestionar.py'),*argv];t=time.monotonic()
    r=subprocess.run(cmd,cwd=S,text=True,encoding='utf8',capture_output=True,timeout=timeout)
    try:data=json.loads(r.stdout)
    except Exception:data={'unparsed_stdout':r.stdout}
    atomic_json(p,{'id':id,'argv':cmd,'returncode':r.returncode,'wall_seconds':time.monotonic()-t,'result':data,'stderr':r.stderr})
    print(id+' code='+str(r.returncode),flush=True)
    if r.returncode:raise RuntimeError('Preserved error '+id+' '+r.stderr[-1200:])
    return data
def run(life,id,fn,details=None):
    budget();p=E/(id+'.json')
    if p.exists():raise FileExistsError('No repeated trajectory '+id)
    s=Store();before=s.record(life);sources=source_bytes();atomic_json(E/(id+'.PRE_REGISTRO.json'),{'id':id,'before_snapshot_sha256':before['snapshot_sha256'],'details':details,'sources_loaded_at_start':sources})
    try:r=s.mutate(life,id,fn,details or{})
    except Exception as ex:
        atomic_json(p,{'id':id,'life':life,'before':before,'after':s.record(life),'error':{'type':type(ex).__name__,'detail':str(ex)},'sources':sources});raise
    atomic_json(p,{'id':id,'life':life,'before':before,'after':s.record(life),'data':r,'sources':sources})
    print(id+' T'+str(r['physical']['tick']),flush=True);return r
