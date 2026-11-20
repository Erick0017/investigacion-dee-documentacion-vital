"""Export exact closed primary bytes, then run the read-only isolation worker."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys,tempfile
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--primarios',type=Path,required=True);p.add_argument('--codigos',type=Path,required=True);p.add_argument('--artefactos',type=Path,required=True);p.add_argument('--indice-artefactos',type=Path,required=True);p.add_argument('--referencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);p.add_argument('--prohibir-raiz',type=Path,action='append',required=True);a=p.parse_args()
    if a.salida.exists():raise FileExistsError('Previous proof protected')
    temp=Path(tempfile.mkdtemp(prefix='EO02-analisis-exportado-'));prim=temp/'primarios';prim.mkdir();code=temp/'codigo';art=temp/'artefactos'
    for source in a.primarios.iterdir():
        if source.is_file()and re.match(r'^\d+[A-Za-z]*_',source.name)and source.name!='00_ESTADO_PROTEGIDO_INICIAL.json'and(source.name.endswith('.json.gz')or source.suffix=='.json'):shutil.copyfile(source,prim/source.name)
    shutil.copytree(a.primarios/'codigo_experimento',prim/'codigo_experimento');shutil.copytree(a.codigos,code);shutil.copytree(a.artefactos,art)
    index=temp/'INDICE_ARTEFACTOS.json';shutil.copyfile(a.indice_artefactos,index);reference=temp/'REFERENCIA.json';shutil.copyfile(a.referencia,reference)
    for name in('verificar_recalculo_aislado.py','recalcular_eo02.py','referencias_eo02.py'):shutil.copyfile(Path(__file__).with_name(name),temp/name)
    argv=[sys.executable,'-I','-B','-X','utf8',str(temp/'verificar_recalculo_aislado.py'),'--primarios',str(prim),'--codigos',str(code),'--artefactos',str(art),'--indice-artefactos',str(index),'--referencia',str(reference),'--salida',str(temp/'recalculado')]
    for root in a.prohibir_raiz:argv+=['--prohibir-raiz',str(root)]
    r=subprocess.run(argv,capture_output=True,text=True,encoding='utf8',timeout=240)
    if r.returncode:raise RuntimeError(r.stdout+'\n'+r.stderr)
    proof=json.loads((temp/'recalculado/INDEPENDENCIA_RECALCULO.json').read_bytes());proof.update(retained_export=str(temp),command=argv,calculator_sha256=sha(temp/'recalcular_eo02.py'),frozen_reference_sha256=sha(temp/'referencias_eo02.py'),not_final_delivery_zip_test=True)
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(proof,ensure_ascii=False))
if __name__=='__main__':main()
