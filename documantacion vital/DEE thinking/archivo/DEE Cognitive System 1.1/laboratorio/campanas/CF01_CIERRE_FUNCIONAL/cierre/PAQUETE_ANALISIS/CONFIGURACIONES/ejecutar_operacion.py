"""Supervisor finito del gestor original. No calcula decisiones del participante."""
from pathlib import Path
import argparse,gzip,hashlib,json,os,subprocess,sys,time
from datetime import datetime,timezone

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
EVIDENCE=ROOT/'evidencia/campanas/CF01_CIERRE_FUNCIONAL'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--caso',required=True);p.add_argument('--limite',type=int,default=900);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    if not a.command:raise ValueError('Comando real del gestor requerido')
    if not a.caso.replace('_','').replace('-','').isalnum():raise ValueError('Identificador de evidencia simple requerido')
    budget=json.loads((HERE/'PRESUPUESTO.json').read_bytes());remaining=budget['monotonic_deadline']-time.monotonic()
    if remaining<=0:raise TimeoutError('Presupuesto CF01 agotado; no se reinicia')
    EVIDENCE.mkdir(parents=True,exist_ok=True);destination=EVIDENCE/(a.caso+'.json.gz')
    if destination.exists():raise FileExistsError('Primario previo protegido: '+str(destination))
    files=[ROOT/'sistema/gestionar.py',*sorted((ROOT/'sistema/app').glob('*.py')),*sorted((ROOT/'sistema/capacidades').glob('*.py'))]
    signatures={x.relative_to(ROOT).as_posix():sha(x)for x in files}
    version=hashlib.sha256(json.dumps(signatures,sort_keys=True).encode()).hexdigest()
    archive=EVIDENCE/'codigo_ejecutado'/version
    if not archive.exists():
        for path in files:
            target=archive/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
        (archive/'INDICE.json').write_text(json.dumps(signatures,sort_keys=True,indent=2)+'\n',encoding='utf8')
    command=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'sistema/gestionar.py'),*a.command]
    before=time.monotonic();wall=datetime.now(timezone.utc).isoformat()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1');env.pop('PYTHONPATH',None)
    result=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf8',timeout=min(a.limite,max(1,int(remaining))))
    primary={'case':a.caso,'started_utc':wall,'elapsed_seconds':time.monotonic()-before,'argv':command,'code_revision_sha256':version,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'supervisor_never_selects_a_response':True}
    if result.stdout.strip():
        try:primary['result']=json.loads(result.stdout)
        except json.JSONDecodeError:primary['output_is_not_one_json']=True
    with gzip.open(destination,'wt',encoding='utf8',compresslevel=6)as f:json.dump(primary,f,ensure_ascii=False,allow_nan=False)
    print(json.dumps({'case':a.caso,'returncode':result.returncode,'primary':str(destination),'code_revision_sha256':version,'elapsed_seconds':primary['elapsed_seconds'],'stderr':result.stderr[-1000:]},ensure_ascii=False))
    return result.returncode

if __name__=='__main__':raise SystemExit(main())
