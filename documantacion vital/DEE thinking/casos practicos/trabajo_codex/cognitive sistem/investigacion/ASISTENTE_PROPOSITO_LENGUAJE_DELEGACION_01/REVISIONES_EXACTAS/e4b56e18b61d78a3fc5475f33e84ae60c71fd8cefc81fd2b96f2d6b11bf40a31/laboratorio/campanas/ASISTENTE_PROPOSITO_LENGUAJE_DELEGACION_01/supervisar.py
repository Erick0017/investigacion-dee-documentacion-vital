"""One bounded command; preserve exact executed source and both outputs."""
from pathlib import Path
import argparse,datetime,gzip,hashlib,json,os,subprocess,sys,time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
EV=ROOT/'evidencia/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01'
def sha(b): return hashlib.sha256(b).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--caso',required=True);p.add_argument('--limite',type=int,default=300);p.add_argument('--script',type=Path);p.add_argument('args',nargs=argparse.REMAINDER);a=p.parse_args()
    if not a.caso.replace('_','').replace('-','').isalnum():raise ValueError('Safe case id required')
    budget=json.loads((HERE/'PRESUPUESTO.json').read_bytes())
    remaining=float(budget['monotonic_deadline'])-time.monotonic()
    if remaining<=0:raise TimeoutError('Original campaign deadline exhausted')
    dest=EV/(a.caso+'.json.gz');EV.mkdir(parents=True,exist_ok=True)
    if dest.exists():raise FileExistsError('Existing primary protected')
    files=[*sorted((ROOT/'sistema').rglob('*.py')),*sorted(HERE.rglob('*.py'))]
    signatures={str(f.relative_to(ROOT)).replace('\\','/'):sha(f.read_bytes()) for f in files}
    revision=sha(json.dumps(signatures,sort_keys=True).encode());archive=EV/'codigo_ejecutado'/revision
    if not archive.exists():
        for f in files:
            t=archive/f.relative_to(ROOT);t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes(f.read_bytes())
        (archive/'INDICE.json').write_text(json.dumps(signatures,indent=2)+'\n',encoding='utf8')
    arguments=a.args[1:] if a.args[:1]==['--'] else a.args
    argv=[sys.executable,'-I','-B','-X','utf8',str(a.script or ROOT/'sistema/gestionar.py'),*arguments]
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1');env.pop('PYTHONPATH',None)
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic()
    try:
        r=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf8',timeout=min(a.limite,max(1,int(remaining))));rc,out,err,timed=r.returncode,r.stdout,r.stderr,False
    except subprocess.TimeoutExpired as e:
        rc,out,err,timed=124,e.stdout or '',e.stderr or '',True
        if isinstance(out,bytes):out=out.decode('utf8','replace')
        if isinstance(err,bytes):err=err.decode('utf8','replace')
    result={'case':a.caso,'started_utc':started,'elapsed_seconds':time.monotonic()-t,'argv':argv,'code_revision_sha256':revision,'returncode':rc,'stdout':out,'stderr':err,'timed_out':timed,'supervisor_not_actor':True}
    try:result['result']=json.loads(out)
    except json.JSONDecodeError:result['output_is_not_one_JSON']=True
    dest.write_bytes(gzip.compress(json.dumps(result,ensure_ascii=False,allow_nan=False).encode(),mtime=0))
    print(json.dumps({k:result[k] for k in ('case','returncode','elapsed_seconds','code_revision_sha256')}));return rc
if __name__=='__main__':raise SystemExit(main())
