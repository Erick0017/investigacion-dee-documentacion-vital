"""Preserve the closed44 mock fixtures and verify their portable repeatability."""
import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    with p.open('x',encoding='utf8')as f:json.dump(x,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--referencia',type=Path,required=True);p.add_argument('--validador',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);p.add_argument('--portable',type=Path,required=True);a=p.parse_args();stage=a.stage.resolve();portable=a.portable.resolve()
    if stage.exists()or portable.exists():raise FileExistsError('Never replace an earlier stage/proof')
    stage.mkdir(parents=True);(stage/'FUENTES').mkdir();(stage/'RECALCULO').mkdir()
    for name in('arrancar.py','configurar_apd02.py','PLAN_DISTRIBUCION_APD02.md'):shutil.copy2(Path(__file__).with_name(name),stage/'FUENTES'/name)
    for name in('probar_lanzador_apd02_n0.py','recalcular_lanzador_n0.py'):shutil.copy2(Path(__file__).with_name(name),stage/'RECALCULO'/name)
    shutil.copy2(a.validador,stage/'FUENTES/protocolo_apd02.py');shutil.copy2(a.referencia,stage/'REFERENCIA_LANZADOR_N0.json')
    script='RECALCULO/recalcular_lanzador_n0.py';args=['--lanzador','FUENTES/arrancar.py','--validador','FUENTES/protocolo_apd02.py','--salida','{output}'];write(stage/'PLAN_RECALCULO.json',{'jobs':[{'name':'LAUNCHER44_TYPED_TRANSPORT_MOCK_FIXTURES','base':'.','script':script,'args':args,'reference':'REFERENCIA_LANZADOR_N0.json'}],'scope':'Reexecute mocks only, no manager/engine/Runtime/native calls. This is not an exact-FullZIP operational proof.'})
    shutil.copytree(stage,portable);out=portable/'RECALCULADO.json';r=subprocess.run([sys.executable,'-I','-B','-X','utf8',script,*[str(out)if x=='{output}'else x for x in args]],cwd=portable,capture_output=True,text=True,encoding='utf8',timeout=60);proof={'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'byte_identical':out.exists()and sha(out)==sha(stage/'REFERENCIA_LANZADOR_N0.json'),'new_native_ticks':0,'actual_manager_calls':0};write(stage/'PRUEBA_PORTABLE.json',proof)
    write(stage/'MANIFIESTO.json',{'files':[{'file':f.relative_to(stage).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(stage.rglob('*'))if f.is_file()],'scope':'Exact candidate launcher/configuration, frozen actual typed validator, mock code and original fixture output. No collaboration or system mutation. Manifest excludes itself.'});print(json.dumps(proof));return r.returncode or not proof['byte_identical']
if __name__=='__main__':raise SystemExit(main())
