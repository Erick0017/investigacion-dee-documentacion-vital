"""Supervisor finito reutilizado para A+B; registra, no selecciona respuestas."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,gzip,hashlib,json,os,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--caso',required=True);p.add_argument('--fase',choices=['A','B'],default='A');p.add_argument('--limite',type=int,default=600);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    if not a.command or not a.caso.replace('_','').replace('-','').isalnum():raise ValueError('Explicit case and command required')
    budget=json.loads((HERE/'PRESUPUESTO.json').read_bytes())
    if a.fase=='B' and not(HERE/'CIERRE_INTERNO_A.json').exists():raise ValueError('Close actual block A before native B')
    limit=budget['block_A_deadline_monotonic']if a.fase=='A'else min(budget['total_deadline_monotonic'],json.loads((HERE/'CIERRE_INTERNO_A.json').read_bytes())['block_B_deadline_monotonic'])
    remaining=limit-time.monotonic()
    if remaining<=0:raise TimeoutError('Authorized block budget exhausted; do not reset')
    dest=EV/(a.caso+'.json.gz');EV.mkdir(parents=True,exist_ok=True)
    if dest.exists():raise FileExistsError('Existing primary protected')
    files=[ROOT/'sistema/gestionar.py',*sorted((ROOT/'sistema/app').rglob('*.py')),*sorted((ROOT/'sistema/capacidades').rglob('*.py'))]
    signatures={f.relative_to(ROOT).as_posix():sha(f)for f in files};version=hashlib.sha256(json.dumps(signatures,sort_keys=True).encode()).hexdigest()
    archive=EV/'codigo_ejecutado'/version
    if not archive.exists():
        for f in files:
            target=archive/f.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(f.read_bytes())
        (archive/'INDICE.json').write_text(json.dumps(signatures,indent=2)+'\n',encoding='utf8')
    argv=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'sistema/gestionar.py'),*a.command]
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1');env.pop('PYTHONPATH',None)
    start=time.monotonic()
    try:
        r=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf8',timeout=min(a.limite,max(1,int(remaining))));code,out,err=r.returncode,r.stdout,r.stderr;timed=False
    except subprocess.TimeoutExpired as e:
        code=124;out=e.stdout or'';err=e.stderr or'';timed=True
        if isinstance(out,bytes):out=out.decode('utf8','replace')
        if isinstance(err,bytes):err=err.decode('utf8','replace')
    result={'case':a.caso,'phase':a.fase,'started_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,'argv':argv,'code_revision_sha256':version,'returncode':code,'stdout':out,'stderr':err,'timed_out':timed,'supervisor_not_actor':True}
    try:result['result']=json.loads(out)
    except json.JSONDecodeError:result['output_is_not_one_JSON']=True
    dest.write_bytes(gzip.compress(json.dumps(result,ensure_ascii=False,allow_nan=False).encode(),mtime=0))
    print(json.dumps({k:result[k]for k in('case','phase','returncode','elapsed_seconds','code_revision_sha256')}));return code
if __name__=='__main__':raise SystemExit(main())
