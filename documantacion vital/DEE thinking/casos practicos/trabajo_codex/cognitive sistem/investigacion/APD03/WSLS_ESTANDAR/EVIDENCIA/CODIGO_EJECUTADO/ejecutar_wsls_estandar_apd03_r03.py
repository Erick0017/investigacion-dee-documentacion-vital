"""Fourth conventional reference only, exact common program, no Native."""
import argparse,datetime,hashlib,json,shutil,subprocess,sys,tempfile,time
from pathlib import Path


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(path,value):
    with Path(path).open('x',encoding='utf8')as stream:
        json.dump(value,stream,sort_keys=True,ensure_ascii=False,indent=2);stream.write('\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--program',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--root-go',required=True,choices=['APD03_STANDARD_WSLS_CONVENTIONAL_ONLY']);args=parser.parse_args()
    program=args.program.resolve();out=args.out.resolve();here=Path(__file__).resolve().parent
    if sha(program)!='96b6b1a82bd4a3f3bc0cb6f9650752ed8bf3506b9e0bf37de2ea6dc2c51ca599':raise ValueError('Frozen common R02 program required')
    out.mkdir(parents=True,exist_ok=False);code=out/'CODIGO_EJECUTADO';code.mkdir();(code/'vendor').mkdir()
    names=['comparadores_apd03_wsls_estandar_r03.py','comparadores_apd03_r02.py','comparadores_apd03.py',
        'test_wsls_estandar_apd03_n0.py','test_comparadores_r02_n0.py','PROTOCOLO_CUARTA_REFERENCIA_WSLS_ESTANDAR_R03.md',
        'ejecutar_wsls_estandar_apd03_r03.py','vendor/evaluador_calidad_apd02.py','vendor/proveedores_prueba_apd02.py','vendor/process_control.py']
    sources=[]
    for name in names:
        shutil.copyfile(here/name,code/name);sources.append({'file':(code/name).relative_to(out).as_posix(),
            'source':str(here/name),'bytes':(code/name).stat().st_size,'sha256':sha(code/name)})
    frozen=out/'PROGRAMA_PROSPECTIVO.json';shutil.copyfile(program,frozen)
    emit(out/'ANTES_PRIMERA_REFERENCIA.json',{'schema':'DEE.APD03.standard_WSLS.prospective.R03',
        'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':sources,'root_go':args.root_go,
        'program_sha256':sha(frozen),'scope':'Fourth conventional trajectory; three previous references preserved, no MAIN outcome read',
        'policy_change':'Stay/shift relative to the route effectively ACTed, including permitted-interface fallback',
        'information':'Same blinded R02 presence-only/context0 projection and binary post-commit feedback',
        'memory_limit_bytes':256*1024**2,'native_ticks':0,'energy':'NO MEDIDA'})
    test=subprocess.run([sys.executable,'-I','-B',str(code/'test_wsls_estandar_apd03_n0.py'),'-v'],
        cwd=tempfile.gettempdir(),capture_output=True,text=True,encoding='utf8',timeout=30)
    emit(out/'COMPROBANTE_N0.json',{'exit_code':test.returncode,'stdout':test.stdout,'stderr':test.stderr,'tests':4,'new_native_ticks':0})
    if test.returncode:raise ValueError('Standard policy fence fixture failed before trajectory')
    for row in sources:
        if sha(out/row['file'])!=row['sha256']:raise ValueError('Frozen source changed')
    began=time.monotonic();command=[sys.executable,'-I','-B',str(code/'comparadores_apd03_wsls_estandar_r03.py'),
        '--program',str(frozen),'--out',str(out/'wsls_estandar'),'--policy','wsls_estandar']
    with(out/'stdout.json').open('xb')as stdout,(out/'stderr.txt').open('xb')as stderr:
        run=subprocess.run(command,cwd=tempfile.gettempdir(),stdout=stdout,stderr=stderr,timeout=60)
    emit(out/'PROCESO.json',{'command':command,'exit_code':run.returncode,'launcher_wall_seconds':time.monotonic()-began})
    if run.returncode:raise ValueError('Fourth reference failed; preserve partials, no silent retry')
    recalculated=subprocess.run([sys.executable,'-I','-B',str(code/'comparadores_apd03_wsls_estandar_r03.py'),
        '--recalculate',str(out/'wsls_estandar')],cwd=tempfile.gettempdir(),capture_output=True,text=True,encoding='utf8',timeout=30)
    emit(out/'VERIFICACION.json',{'exit_code':recalculated.returncode,'stdout':recalculated.stdout,'stderr':recalculated.stderr})
    if recalculated.returncode:raise ValueError('Fourth archived reference cannot be recalculated')
    emit(out/'RECALCULADO.json',json.loads(recalculated.stdout))
    print((out/'wsls_estandar/resumen.json').read_text('utf8'))


if __name__=='__main__':main()
