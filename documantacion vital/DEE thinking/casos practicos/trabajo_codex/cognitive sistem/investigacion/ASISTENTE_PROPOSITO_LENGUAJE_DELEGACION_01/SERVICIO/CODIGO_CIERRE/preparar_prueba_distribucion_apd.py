"""Compact exact-FullZIP proof with actual artifacts and portable recalculation."""
import argparse,hashlib,importlib.util,json,shutil,subprocess,sys
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def write(p,x):
    with p.open('x',encoding='utf8')as f:json.dump(x,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in('prueba','extraccion','protocolo','sello','salida','prueba-corta'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();root=a.extraccion.resolve();out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False);proof=read(a.prueba);service=proof.get('service_sequence',{})
    if proof.get('status')!='COMPLETED_WITH_RECORDED_SCOPE':raise ValueError('Preserve failed operational proof separately; do not silently reseal it as success')
    life=service['exact_import']['life_id'];actualroot=(root/'trabajo_personal/estado/servicios_locales'/life).resolve(strict=True)
    def cp(src,relative):
        target=out/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
        if sha(target)!=sha(src):raise ValueError('Moving exported source: '+str(src))
    cp(a.prueba,'EVIDENCIA/PRUEBA_FULL.json');cp(a.protocolo,'EVIDENCIA/PROTOCOLO_FULL_FIJO.json');cp(a.sello,'SELLO_DISTRIBUCION.json');cp(Path(__file__).parent/'distribucion/PROTOCOLO_FULL_APD_R01_MATERIAL_FIJO.json','EVIDENCIA/PROTOCOLO_MATERIAL_PROSPECTIVO_ORIGINAL.json')
    for name in('arrancar.py','probar_servicio_distribuido.py','verificar_entrega_independiente.py','auditar_apd_archivado.py','actualizar.py'):cp(root/'actualizaciones'/name,'EVIDENCIA/CODIGO/'+name)
    here=Path(__file__).resolve().parent;script=here/'recalcular_entrega_apd.py';cp(script,'RECALCULO/recalcular_entrega_apd.py');cp(root/'actualizaciones/auditar_apd_archivado.py','RECALCULO/auditar_apd_resultados_r04.py');cp(Path(__file__),'CODIGO_CIERRE/preparar_prueba_distribucion_apd.py')
    spec=importlib.util.spec_from_file_location('closed_proof_iterator_only',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);files={}
    def include(name,size,digest):
        if Path(name).name!=name:raise ValueError('Declared artifact name must be a bounded basename')
        key=(name,digest)
        if key in files:return
        matches=[f for f in actualroot.rglob(name)if f.is_file()and f.stat().st_size==size and sha(f)==digest]
        if not matches:raise ValueError('Actual artifact missing within THIS extracted life: '+name)
        relative='ARTEFACTOS/'+digest+'/'+name;cp(matches[0],'EVIDENCIA/'+relative);files[key]={'name':name,'file':relative,'bytes':size,'sha256':digest,'source_matches_in_this_life':[str(f)for f in matches]}
    for node in m.objects(proof):
        if node.get('schema')=='EO02.local_worker.receipt.v2':include(node['output_name'],node['output_bytes'],node['output_sha256'])
        if node.get('kind')in('APD01_integrated_request','APD01_assisted_composition')and node.get('artifact'):
            x=node['artifact'];include(x['name'],x['bytes'],x['sha256'])
    write(out/'EVIDENCIA/ARCHIVOS_REALES.json',{'files':list(files.values()),'scope':'Exact actual artifacts from this one newly evaluated extracted life only. No reconstruction from target, other life or worker replay.'})
    reference=out/'REFERENCIAS/ENTREGA_APD.json';reference.parent.mkdir();r=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(out/'RECALCULO/recalcular_entrega_apd.py'),'--evidencia',str(out/'EVIDENCIA'),'--salida',str(reference)],capture_output=True,text=True,encoding='utf8',timeout=180)
    write(out/'RECALCULO_LOCAL.json',{'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'native_ticks':0})
    if r.returncode:raise ValueError('Keep this failed stage; exported evidence disagrees with independent recalculation')
    job={'name':'EXACT_FULLZIP_APD','id':'EXACT_FULLZIP_APD','base':'.','script':'RECALCULO/recalcular_entrega_apd.py','args':['--evidencia','EVIDENCIA','--salida','{output}'],'reference':'REFERENCIAS/ENTREGA_APD.json','scope':'Archived RAW/readers/actual bytes only, not another execution of the full ZIP.'};write(out/'PLAN_RECALCULO.json',{'schema':'DEE.portable_recalculation.plan.v1','jobs':[job]})
    short=a.prueba_corta.resolve();short.mkdir(exist_ok=False);shutil.copytree(out,short/'PRUEBA');portable=short/'RESULTADO.json';run=subprocess.run([sys.executable,'-I','-B','-X','utf8',job['script'],*['../RESULTADO.json'if x=='{output}'else x for x in job['args']]],cwd=short/'PRUEBA',capture_output=True,text=True,encoding='utf8',timeout=180);same=run.returncode==0 and portable.is_file()and portable.read_bytes()==reference.read_bytes()
    write(out/'PRUEBA_PORTABLE.json',{'native_ticks':0,'returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'reference_sha256':sha(reference),'actual_sha256':sha(portable)if portable.is_file()else None,'byte_identical':same})
    write(out/'INDICE_OMISIONES.json',{'omitted':['Full collaboration ZIP, engine, WHL, complete native snapshots and SQLite journals'],'local_proof_file':str(a.prueba),'local_extraction':str(root),'scope':'Hashes/protection of omitted operational resources are archived receipts, not freshly re-opened by the compact standard-library recalculation.'})
    members=[{'file':f.relative_to(out).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(out.rglob('*'))if f.is_file()];write(out/'MANIFIESTO.json',{'members':members,'self_exclusion':'MANIFIESTO.json only','scope':'Exact archived portable proof, with functional negatives distinct from integrity discrepancies.'});print(json.dumps({'stage':str(out),'files':len(members)+1,'manifest_sha256':sha(out/'MANIFIESTO.json'),'all_byte_identical':same}));return not same
if __name__=='__main__':raise SystemExit(main())
