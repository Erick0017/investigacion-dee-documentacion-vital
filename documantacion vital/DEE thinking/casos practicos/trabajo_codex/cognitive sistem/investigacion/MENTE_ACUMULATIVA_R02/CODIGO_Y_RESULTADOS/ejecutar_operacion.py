"""EO02 finite supervisor. It records programs and receipts, never selects actions."""
from pathlib import Path
import argparse,gzip,hashlib,json,os,subprocess,sys,time
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
EV=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA_R02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--caso',required=True);p.add_argument('--limite',type=int,default=900);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    if not a.command or not a.caso.replace('_','').replace('-','').isalnum():raise ValueError('Case and real command required')
    remaining=json.loads((HERE/'PRESUPUESTO.json').read_bytes())['deadline_monotonic']-time.monotonic()
    if remaining<=0:raise TimeoutError('EO02 budget exhausted, never restart')
    EV.mkdir(parents=True,exist_ok=True);dest=EV/(a.caso+'.json.gz')
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
    start=time.monotonic();wall=datetime.now(timezone.utc).isoformat()
    try:
        r=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf8',timeout=min(a.limite,max(1,int(remaining))));code,out,err=r.returncode,r.stdout,r.stderr;timeout=False
    except subprocess.TimeoutExpired as e:
        code=124;out=e.stdout or'';err=e.stderr or'';timeout=True
        if isinstance(out,bytes):out=out.decode('utf8','replace')
        if isinstance(err,bytes):err=err.decode('utf8','replace')
    result={'case':a.caso,'started_utc':wall,'elapsed_seconds':time.monotonic()-start,'argv':argv,'code_revision_sha256':version,'returncode':code,'stdout':out,'stderr':err,'timed_out':timeout,'supervisor_never_selects_a_response':True}
    if out.strip():
        try:result['result']=json.loads(out)
        except json.JSONDecodeError:result['output_is_not_one_json']=True
    with gzip.open(dest,'wt',encoding='utf8',compresslevel=6)as f:json.dump(result,f,ensure_ascii=False,allow_nan=False)
    print(json.dumps({k:result[k]for k in('case','elapsed_seconds','returncode','code_revision_sha256')},ensure_ascii=False));return code
if __name__=='__main__':raise SystemExit(main())
