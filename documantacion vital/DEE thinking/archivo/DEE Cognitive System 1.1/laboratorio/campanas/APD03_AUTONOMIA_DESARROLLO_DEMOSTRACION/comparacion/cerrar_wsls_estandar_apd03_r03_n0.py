"""Seal fourth actual conventional trajectory, preserving previous three."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8')as stream:
        json.dump(value,stream,sort_keys=True,ensure_ascii=False,indent=2);stream.write('\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--evidence',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path);args=parser.parse_args()
    source=args.evidence.resolve();out=args.out.resolve();here=Path(__file__).resolve().parent
    out.mkdir(parents=True,exist_ok=False);shutil.copytree(source,out/'EVIDENCIA')
    shutil.copyfile(here/'INFORME_WSLS_ESTANDAR_R03.md',out/'INFORME_WSLS_ESTANDAR.md')
    (out/'RECALCULO').mkdir();shutil.copyfile(here/'recalcular_wsls_estandar_apd03_r03.py',out/'RECALCULO/recalcular_wsls_estandar_apd03_r03.py')
    reference=out/'REFERENCIAS/RECALCULO.json';reference.parent.mkdir()
    command=[sys.executable,'-I','-B',str(out/'RECALCULO/recalcular_wsls_estandar_apd03_r03.py'),
        '--evidence',str(out/'EVIDENCIA'),'--out',str(reference)]
    run=subprocess.run(command,cwd=tempfile.gettempdir(),capture_output=True,text=True,encoding='utf8',timeout=30)
    if run.returncode:raise ValueError(run.stderr)
    result=json.loads(reference.read_bytes())
    if result['issues']:raise ValueError('Fourth reference recalc discrepancy')
    job={'name':'WSLS_ESTANDAR_R03','base':'.','script':'RECALCULO/recalcular_wsls_estandar_apd03_r03.py',
        'args':['--evidence','EVIDENCIA','--out','{output}'],'reference':'REFERENCIAS/RECALCULO.json'}
    emit(out/'PLAN_RECALCULO.json',{'jobs':[job]})
    temp=Path(tempfile.mkdtemp(prefix='dee_apd03_stdwsls_'));portable=temp/'p';shutil.copytree(out,portable)
    actual=temp/'RECALCULADO.json';command=[sys.executable,'-I','-B',str(portable/job['script']),
        '--evidence',str(portable/'EVIDENCIA'),'--out',str(actual)]
    run=subprocess.run(command,cwd=temp,capture_output=True,text=True,encoding='utf8',timeout=30)
    same=run.returncode==0 and actual.is_file()and actual.read_bytes()==reference.read_bytes()
    emit(out/'PRUEBA_PORTABLE.json',{'command':command,'exit_code':run.returncode,'stderr':run.stderr,
        'byte_identical':same,'expected_sha256':sha(reference),'actual_sha256':sha(actual)if actual.is_file()else None,
        'checks':result['checks'],'issues':result['issues'],'new_native_ticks':0,'new_provider_calls':0})
    if not same:raise ValueError('Portable fourth reference recalc differed')
    members=[{'file':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(out.rglob('*'))if p.is_file()]
    emit(out/'MANIFIESTO.json',{'schema':'DEE.APD03.standard_wsls_closed.R03','status':'CLOSED_RECALCULATED_PORTABLY_N0',
        'files':members,'files_count':len(members),'files_bytes':sum(r['bytes']for r in members),'self_reference_excluded':'MANIFIESTO.json'})
    print(json.dumps({'stage':str(out),'files':len(members)+1,'bytes_without_self':sum(r['bytes']for r in members),
        'checks':result['checks'],'issues':0,'manifest_sha256':sha(out/'MANIFIESTO.json'),
        'plan_sha256':sha(out/'PLAN_RECALCULO.json'),'reference_sha256':sha(reference),'byte_identical':True}))


if __name__=='__main__':main()
