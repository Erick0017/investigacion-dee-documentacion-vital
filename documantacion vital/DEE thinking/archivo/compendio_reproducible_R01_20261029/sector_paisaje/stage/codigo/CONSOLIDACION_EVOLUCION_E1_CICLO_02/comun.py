from pathlib import Path
import hashlib,json,subprocess,sys,time
LAB=Path(__file__).resolve().parent
ROOT=LAB.parents[2]
SYSTEM=ROOT/'sistema'
EV=ROOT/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
EV.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(SYSTEM))
from app.lives import Store
from app.native_tools import atomic_json,physical,observe,digest_file
from app.process_control import protect_current
protect_current()

def budget(closure=False):
    b=json.loads((LAB/'PRESUPUESTO.json').read_text(encoding='utf8'))
    if time.monotonic()>b['monotonic_deadline']-(0 if closure else b['reserved_closure_seconds']):
        raise TimeoutError('Corte único de CICLO02; no reiniciar reloj')
    return b

def command(name,argv,timeout=240):
    budget()
    p=EV/(name+'.json')
    if p.exists():raise FileExistsError('No repetir operación '+name)
    cmd=[sys.executable,'-I','-B','-X','utf8',str(SYSTEM/'gestionar.py'),*argv]
    t=time.monotonic();r=subprocess.run(cmd,cwd=SYSTEM,text=True,encoding='utf8',capture_output=True,timeout=timeout)
    try:data=json.loads(r.stdout)
    except Exception:data={'unparsed_stdout':r.stdout}
    out={'id':name,'argv':cmd,'returncode':r.returncode,'wall_seconds':time.monotonic()-t,'result':data,'stderr':r.stderr}
    atomic_json(p,out)
    if r.returncode:raise RuntimeError('Operación retenida con error: '+name+' '+r.stderr[-1000:])
    print(name+' completed',flush=True)
    return data

def fork(parent,life,checkpoint=None,kind='DIAGNOSTIC_COPY'):
    s=Store()
    if s.life_dir(life).exists():raise FileExistsError('No reanudar ni repetir implícitamente '+life)
    return s.fork(parent,life,kind=kind,checkpoint=checkpoint)

def run(life,experiment,fn,details=None):
    budget();s=Store();before=s.record(life)
    p=EV/(experiment+'.json')
    if p.exists():raise FileExistsError(experiment)
    code={str(f.relative_to(LAB)):digest_file(f) for f in LAB.glob('*.py')}
    try:r=s.mutate(life,experiment,fn,{**(details or{}),'code':code})
    except Exception as e:
        atomic_json(p,{'id':experiment,'life':life,'before':before,'after':s.record(life),'error':{'type':type(e).__name__,'detail':str(e)},'code':code})
        raise
    atomic_json(p,{'id':experiment,'life':life,'before':before,'after':s.record(life),'data':r,'code':code})
    print(experiment+' '+str(r['physical']['tick']),flush=True)
    return r
