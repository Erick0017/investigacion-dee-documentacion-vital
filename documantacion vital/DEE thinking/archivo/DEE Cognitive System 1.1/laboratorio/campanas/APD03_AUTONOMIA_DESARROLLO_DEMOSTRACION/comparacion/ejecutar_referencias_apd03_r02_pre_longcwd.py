"""Run three separate conventional reference processes; never call Native."""
import argparse,datetime,hashlib,json,shutil,subprocess,sys,time
from pathlib import Path


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,value):
    with Path(path).open('x',encoding='utf8')as stream:
        json.dump(value,stream,sort_keys=True,ensure_ascii=False,indent=2);stream.write('\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--program',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path);args=parser.parse_args()
    program=args.program.resolve();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    here=Path(__file__).resolve().parent;source=out/'CODIGO_EJECUTADO';source.mkdir();(source/'vendor').mkdir()
    files=['comparadores_apd03_r02.py','comparadores_apd03.py','test_comparadores_r02_n0.py',
        'ejecutar_referencias_apd03_r02.py','vendor/evaluador_calidad_apd02.py',
        'vendor/proveedores_prueba_apd02.py','vendor/process_control.py']
    sources=[]
    for relative in files:
        original=here/relative;target=source/relative;shutil.copyfile(original,target)
        sources.append({'source':str(original),'file':target.relative_to(out).as_posix(),
            'bytes':target.stat().st_size,'sha256':sha(target)})
    frozen=out/'PROGRAMA_PROSPECTIVO.json';shutil.copyfile(program,frozen)
    if sha(program)!='96b6b1a82bd4a3f3bc0cb6f9650752ed8bf3506b9e0bf37de2ea6dc2c51ca599':
        raise ValueError('Not the agreed frozen MAIN-derived R02 program')
    write(out/'ANTES_PRIMERA_REFERENCIA.json',{'schema':'DEE.APD03.reference_prospective.R02',
        'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'program_source':str(program),
        'program_sha256':sha(program),'sources':sources,'policies':['fijo','tabla_contextual','wsls'],
        'max_process_memory_bytes':256*1024**2,'wall_timeout_per_trajectory_seconds':60,
        'policy_input':'literal old learned math cue, raw present/missing bit, fixed tool interfaces; context0 constant, no magnitudes',
        'policy_feedback':'only binary result after its own action; omitted exactly when program says omit',
        'arithmetic':'Classical callbacks on both nominal routes, not v27 cost or a controller of E1',
        'schedule':'same logical event order and opportunity budget, no 3600s sleep or DEE basal evolution equivalence',
        'scope':'8 mathematical shared goals +3 two-provider quality tasks, one trajectory per policy; lexical/MA/composition excluded',
        'native_ticks':0,'energy':'NO MEDIDA'})
    n0=subprocess.run([sys.executable,'-I','-B',str(source/'test_comparadores_r02_n0.py'),'-v'],
        cwd=out,capture_output=True,text=True,encoding='utf8',timeout=30)
    write(out/'COMPROBANTE_N0.json',{'exit_code':n0.returncode,'stdout':n0.stdout,'stderr':n0.stderr,
        'tests':4,'scope':'Contract fixtures, not MAIN outcomes or Native tests','new_native_ticks':0})
    if n0.returncode:raise ValueError('N0 fence tests failed before execution')
    runs=[]
    for name in('fijo','tabla_contextual','wsls'):
        for row in sources:
            if sha(out/row['file'])!=row['sha256']:raise ValueError('Code changed after freeze')
        began=time.perf_counter();command=[sys.executable,'-I','-B',str(source/'comparadores_apd03_r02.py'),
            '--program',str(frozen),'--out',str(out/name),'--policy',name]
        with(out/(name+'_stdout.json')).open('xb')as stdout,(out/(name+'_stderr.txt')).open('xb')as stderr:
            run=subprocess.run(command,cwd=out,stdout=stdout,stderr=stderr,timeout=60)
        receipt={'policy':name,'command':command,'exit_code':run.returncode,'launcher_wall_seconds':time.perf_counter()-began}
        runs.append(receipt);write(out/(name+'_PROCESO.json'),receipt)
        if run.returncode:raise ValueError('Conventional run failed; preserve partials, no silent retry')
        recalc=subprocess.run([sys.executable,'-I','-B',str(source/'comparadores_apd03_r02.py'),
            '--recalculate',str(out/name)],cwd=out,capture_output=True,text=True,encoding='utf8',timeout=30)
        write(out/(name+'_VERIFICACION.json'),{'exit_code':recalc.returncode,'stdout':recalc.stdout,'stderr':recalc.stderr})
        if recalc.returncode:raise ValueError('Archived recalculation failed')
        write(out/(name+'_RECALCULADO.json'),json.loads(recalc.stdout))
        print(json.dumps({'policy':name,'summary':json.loads((out/name/'resumen.json').read_bytes())}),flush=True)
    write(out/'PROCESOS_COMPLETADOS.json',{'runs':runs,'new_native_ticks':0,'policies_controlled_E1':False})


if __name__=='__main__':main()
