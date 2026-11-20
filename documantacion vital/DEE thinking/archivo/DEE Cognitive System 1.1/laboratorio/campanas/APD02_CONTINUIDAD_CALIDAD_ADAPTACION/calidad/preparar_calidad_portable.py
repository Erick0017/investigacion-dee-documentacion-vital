"""Close pure-quality evidence, then recalculate it from an independent copy."""
import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):
    with path.open('x',encoding='utf8')as f:json.dump(value,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);p.add_argument('--portable',type=Path,required=True);a=p.parse_args()
    original=a.evidencia.resolve();stage=a.stage.resolve();portable=a.portable.resolve()
    if stage.exists()or portable.exists():raise FileExistsError('New independent paths required; historical evidence is not overwritten')
    stage.mkdir(parents=True);(stage/'RECALCULO').mkdir();(stage/'EVIDENCIA').mkdir()
    for src in(original/'FUENTES').iterdir():
        if src.suffix=='.py':shutil.copy2(src,stage/'RECALCULO'/src.name)
        else:shutil.copy2(src,stage/src.name)
    shutil.copytree(original/'CASOS',stage/'EVIDENCIA'/'CASOS')
    shutil.copy2(original/'RESULTADOS_CALIDAD.json',stage/'EVIDENCIA'/'RESULTADOS_CALIDAD.json')
    shutil.copy2(original/'RECALCULO_CALIDAD.json',stage/'REFERENCIA_RECALCULO_CALIDAD.json')
    plan={'schema':'DEE.APD02.pure_quality_portable_plan.v1','jobs':[{'name':'CALIDAD_POST_ACCION_PURA','base':'.','script':'RECALCULO/recalcular_calidad_apd02.py','args':['--evidencia','EVIDENCIA','--salida','{output}'],'reference':'REFERENCIA_RECALCULO_CALIDAD.json'}],'scope':'Only archived post-commit real synthetic files; no provider call, DEE Runtime or native reproduction. Time/CPU fields of individual evaluations are excluded explicitly from equality; all deterministic semantic/FS/resource/category fields are compared.'}
    write(stage/'PLAN_RECALCULO.json',plan)
    shutil.copytree(stage,portable)
    output=portable/'RECALCULADO.json';cmd=[sys.executable,'-I','-B','-X','utf8','RECALCULO/recalcular_calidad_apd02.py','--evidencia','EVIDENCIA','--salida',str(output)]
    run=subprocess.run(cmd,cwd=portable,timeout=30,capture_output=True,text=True,encoding='utf8')
    proof={'schema':'DEE.APD02.pure_quality_portable_proof.v1','returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'byte_identical_reference':output.exists()and sha(output)==sha(stage/'REFERENCIA_RECALCULO_CALIDAD.json'),'reference_sha256':sha(stage/'REFERENCIA_RECALCULO_CALIDAD.json'),'new_DEE_ticks':0,'provider_callbacks':0,'scope':'Executed from a separately copied tree with isolated Python import flags; no source data paths are needed by the calculator. The outer preparation tool alone knows the original evidence path.'}
    write(stage/'PRUEBA_PORTABLE.json',proof)
    manifest={'schema':'DEE.APD02.quality_stage_manifest.v1','files':[{'file':f.relative_to(stage).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(stage.rglob('*'))if f.is_file()],'omissions':[{'scope':'Older pure-test R01/R02 synthetic fixtures are retained locally under evidencia/.../calidad; R03 includes every current positive/negative case. No historical primary is rewritten.'}]}
    write(stage/'MANIFIESTO.json',manifest)
    print(json.dumps({'stage':str(stage),'files':len(manifest['files'])+1,'returncode':run.returncode,'byte_identical':proof['byte_identical_reference'],'new_ticks':0}))
    return run.returncode or not proof['byte_identical_reference']
if __name__=='__main__':raise SystemExit(main())
