"""Brief same-gestor CLI path; only evaluation copies consume queued first use."""
import gzip,hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];EV=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA_R02/mecanismo_repetible'
def main():
    out=EV/'MA02_P1_GESTOR_COMPLETO.json.gz'
    if out.exists():raise FileExistsError(out)
    paths=[ROOT/'sistema/gestionar.py',ROOT/'sistema/capacidades/selector_p1_ma02.py',*sorted((ROOT/'sistema/app').rglob('*.py'))]
    shas={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in paths};rev=hashlib.sha256(json.dumps(shas,sort_keys=True).encode()).hexdigest();archive=HERE/'codigo_cli'/rev
    if not archive.exists():
        for p in paths:
            dest=archive/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
    rows=[]
    for suffix in('H1','H0'):
        src='MA02_SELECTOR_P1_'+suffix;dest=src+'_CLI_01'
        commands=[['bifurcar',src,dest,'--modalidad','DIAGNOSTIC_COPY'],['mente2-p1-estado','--vida',dest],['mente2-p1-usar','--vida',dest,'--detalle'],['guardar','--vida',dest],['mente2-p1-estado','--vida',dest],['mente2-p1-usar','--vida',dest]]
        for index,command in enumerate(commands):
            argv=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'sistema/gestionar.py'),*command];p=subprocess.run(argv,capture_output=True,text=True,encoding='utf8',timeout=30)
            r={'source_life':src,'evaluation_life':dest,'index':index,'command':command,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'gestor_sha256':hashlib.sha256((ROOT/'sistema/gestionar.py').read_bytes()).hexdigest()}
            try:r['result']=json.loads(p.stdout)
            except json.JSONDecodeError:pass
            rows.append(r)
            with(EV/'MA02_P1_GESTOR_COMPLETO_INTENTOS.jsonl').open('a',encoding='utf8')as journal:journal.write(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n')
            if (index<5 and p.returncode)or(index==5 and not p.returncode):raise RuntimeError('Unexpected operation status, preserve existing copy: '+p.stderr)
    result={'schema':'MA02.P1.gestor_path.1','identifier':'MA02_P1_GESTOR_COMPLETO','code_revision_sha256':rev,'archived_sources':shas,'rows':rows,'scope':'Operational deterministic checks on evaluation forks, not independent learning samples; ready H1/H0 are not advanced. Repeat is explicitly rejected without silent recipe substitution.'}
    out.write_bytes(gzip.compress(json.dumps(result,ensure_ascii=False,sort_keys=True).encode(),mtime=0));print(json.dumps({'operations':len(rows),'statuses':[r['returncode']for r in rows]},ensure_ascii=False))
if __name__=='__main__':main()
