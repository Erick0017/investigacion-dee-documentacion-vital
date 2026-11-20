"""Compact R04 after execution; no Native, complete checkpoints remain local."""
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
    out.mkdir(parents=True,exist_ok=False);included=[];omitted=[]
    for path in sorted(source.rglob('*')):
        if not path.is_file():continue
        relative=path.relative_to(source)
        row={'source':str(path),'relative_path':relative.as_posix(),'bytes':path.stat().st_size,'sha256':sha(path)}
        if path.name.endswith('.deetsnap.gz'):
            omitted.append({**row,'reason':'Complete physical/operational state remains local. Compact ROI/primary export is not a life continuation backup.'});continue
        if path.suffix=='.pyc'or'__pycache__'in path.parts:continue
        target=out/'EVIDENCIA'/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
        included.append({**row,'file':target.relative_to(out).as_posix()})
    (out/'RECALCULO').mkdir()
    shutil.copyfile(here/'recalcular_historia_acceso_lexico_apd03_r04.py',out/'RECALCULO/recalcular_historia_acceso_lexico_apd03_r04.py')
    shutil.copyfile(here/'diagnosticar_encuentros_historia_r04_n0.py',out/'RECALCULO/diagnosticar_encuentros_historia_r04_n0.py')
    shutil.copyfile(here/'INFORME_HISTORIA_ACCESO_R04.md',out/'INFORME_HISTORIA_ACCESO.md')
    reference=out/'REFERENCIAS/RECALCULO.json';reference.parent.mkdir()
    command=[sys.executable,'-I','-B',str(out/'RECALCULO/recalcular_historia_acceso_lexico_apd03_r04.py'),
        '--evidence',str(out/'EVIDENCIA'),'--out',str(reference)]
    run=subprocess.run(command,cwd=tempfile.gettempdir(),capture_output=True,text=True,encoding='utf8',timeout=90)
    if run.returncode:raise ValueError(run.stderr)
    result=json.loads(reference.read_bytes())
    if result['issues']:raise ValueError('Primary recalc discrepancies: '+repr(result['issues'][:3]))
    job={'name':'HISTORIA_ACCESO_R04','base':'.','script':'RECALCULO/recalcular_historia_acceso_lexico_apd03_r04.py',
        'args':['--evidence','EVIDENCIA','--out','{output}'],'reference':'REFERENCIAS/RECALCULO.json'}
    diagnostic=out/'REFERENCIAS/DIAGNOSTICO_ENCUENTROS.json'
    command=[sys.executable,'-I','-B',str(out/'RECALCULO/diagnosticar_encuentros_historia_r04_n0.py'),
        '--evidence',str(out/'EVIDENCIA'),'--out',str(diagnostic)]
    run=subprocess.run(command,cwd=tempfile.gettempdir(),capture_output=True,text=True,encoding='utf8',timeout=90)
    if run.returncode or diagnostic.read_bytes()!=(source/'DIAGNOSTICO_ENCUENTROS_N0.json').read_bytes():
        raise ValueError('Exact fixed-window diagnostic could not be regenerated')
    jobs=[job,{'name':'ENCUENTROS_HISTORIA_R04','base':'.','script':'RECALCULO/diagnosticar_encuentros_historia_r04_n0.py',
        'args':['--evidence','EVIDENCIA','--out','{output}'],'reference':'REFERENCIAS/DIAGNOSTICO_ENCUENTROS.json'}]
    emit(out/'PLAN_RECALCULO.json',{'jobs':jobs})
    emit(out/'INDICE_FUENTES_Y_OMISIONES.json',{'included':included,'omitted':omitted,
        'included_original_bytes':sum(r['bytes']for r in included),'omitted_bytes':sum(r['bytes']for r in omitted),
        'scope':'All completed/partial experiment events and recorded ROI retained. Whole-state equality receipts are source proofs, not exported snapshots.'})
    portable_root=Path(tempfile.mkdtemp(prefix='dee_apd03_history_'));portable=portable_root/'p';shutil.copytree(out,portable)
    proofs=[]
    for index,job in enumerate(jobs):
        actual=portable_root/('RECALCULADO_'+str(index)+'.json')
        command=[sys.executable,'-I','-B',str(portable/job['script']),
            '--evidence',str(portable/'EVIDENCIA'),'--out',str(actual)]
        run=subprocess.run(command,cwd=portable_root,capture_output=True,text=True,encoding='utf8',timeout=90)
        reference=out/job['reference']
        same=run.returncode==0 and actual.is_file()and actual.read_bytes()==reference.read_bytes()
        proofs.append({'name':job['name'],'command':command,'exit_code':run.returncode,'stderr':run.stderr,
            'byte_identical':same,'expected_sha256':sha(reference),'actual_sha256':sha(actual)if actual.is_file()else None})
        if not same:raise ValueError('Portable archived recalc differs')
    emit(out/'PRUEBA_PORTABLE.json',{'jobs':proofs,'all_byte_identical':True,
        'checks':result['checks'],'issues':len(result['issues']),'new_native_ticks':0})
    for row in included+omitted:
        if sha(row['source'])!=row['sha256']:raise ValueError('An original changed during N0 closure')
    members=[{'file':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(out.rglob('*'))if p.is_file()]
    emit(out/'MANIFIESTO.json',{'schema':'DEE.APD03.history_access_closed.R04','status':'CLOSED_RECALCULATED_PORTABLY_N0',
        'files':members,'files_count':len(members),'files_bytes':sum(r['bytes']for r in members),'self_reference_excluded':'MANIFIESTO.json'})
    print(json.dumps({'stage':str(out),'files':len(members)+1,'bytes_without_self':sum(r['bytes']for r in members),
        'checks':result['checks'],'issues':0,'manifest_sha256':sha(out/'MANIFIESTO.json'),'plan_sha256':sha(out/'PLAN_RECALCULO.json'),
        'reference_sha256':sha(out/'REFERENCIAS/RECALCULO.json'),'diagnostic_sha256':sha(diagnostic),
        'portable_jobs':len(jobs),'byte_identical':True}))


if __name__=='__main__':main()
