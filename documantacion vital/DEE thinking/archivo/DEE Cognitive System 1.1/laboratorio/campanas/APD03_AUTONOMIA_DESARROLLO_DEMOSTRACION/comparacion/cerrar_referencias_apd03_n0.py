"""Seal complete compact conventional references and check recalculation elsewhere."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8')as stream:
        json.dump(value,stream,sort_keys=True,ensure_ascii=False,indent=2);stream.write('\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--evidence',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path);args=parser.parse_args()
    evidence=args.evidence.resolve();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    here=Path(__file__).resolve().parent;shutil.copytree(evidence,out/'EVIDENCIA')
    shutil.copyfile(here/'INFORME_REFERENCIAS_CONVENCIONALES_R02.md',out/'INFORME_REFERENCIAS.md')
    code=out/'RECALCULO';code.mkdir();shutil.copyfile(here/'recalcular_referencias_apd03_r02.py',code/'recalcular_referencias_apd03_r02.py')
    jobs=[];proof=[]
    for name in('fijo','tabla_contextual','wsls'):
        reference=out/'REFERENCIAS'/(name+'.json');reference.parent.mkdir(exist_ok=True)
        command=[sys.executable,'-I','-B',str(code/'recalcular_referencias_apd03_r02.py'),
            '--evidence',str(out/'EVIDENCIA'),'--policy',name,'--out',str(reference)]
        result=subprocess.run(command,cwd=tempfile.gettempdir(),capture_output=True,text=True,encoding='utf8',timeout=30)
        if result.returncode:raise ValueError(result.stderr)
        result=json.loads(reference.read_bytes())
        jobs.append({'name':'REFERENCIA_'+name,'base':'.','script':'RECALCULO/recalcular_referencias_apd03_r02.py',
            'args':['--evidence','EVIDENCIA','--policy',name,'--out','{output}'],'reference':'REFERENCIAS/'+name+'.json'})
        proof.append({'policy':name,'checks':result['checks'],'issues':result['issues'],'artifacts':result['actual_artifacts_rechecked']})
    write(out/'PLAN_RECALCULO.json',{'jobs':jobs})
    temp=Path(tempfile.mkdtemp(prefix='dee_apd03_reference_'));portable=temp/'p';shutil.copytree(out,portable)
    for job,row in zip(jobs,proof):
        output=temp/(row['policy']+'.json')
        command=[sys.executable,'-I','-B',str(portable/job['script']),'--evidence',str(portable/'EVIDENCIA'),
            '--policy',row['policy'],'--out',str(output)]
        result=subprocess.run(command,cwd=temp,capture_output=True,text=True,encoding='utf8',timeout=30)
        same=result.returncode==0 and output.is_file()and output.read_bytes()==(portable/job['reference']).read_bytes()
        row.update(byte_identical=same,command=command,exit_code=result.returncode,stderr=result.stderr,
            expected_sha256=sha(portable/job['reference']),actual_sha256=sha(output)if output.is_file()else None)
        if not same:raise ValueError('Portable archived recalculation differed')
    write(out/'PRUEBA_PORTABLE.json',{'jobs':proof,'all_byte_identical':True,'new_provider_calls':0,
        'new_native_ticks':0,'scope':'Archived policy replay/artifact verification, not a new scientific trajectory'})
    members=[{'file':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(out.rglob('*'))if p.is_file()]
    write(out/'MANIFIESTO.json',{'schema':'DEE.APD03.reference_closed.R01','status':'CLOSED_RECALCULATED_PORTABLY_N0',
        'files':members,'files_count':len(members),'files_bytes':sum(r['bytes']for r in members),'self_reference_excluded':'MANIFIESTO.json'})
    print(json.dumps({'stage':str(out),'files':len(members)+1,'bytes_without_manifest':sum(r['bytes']for r in members),
        'manifest_sha256':sha(out/'MANIFIESTO.json'),'plan_sha256':sha(out/'PLAN_RECALCULO.json'),'jobs':proof}))


if __name__=='__main__':main()
