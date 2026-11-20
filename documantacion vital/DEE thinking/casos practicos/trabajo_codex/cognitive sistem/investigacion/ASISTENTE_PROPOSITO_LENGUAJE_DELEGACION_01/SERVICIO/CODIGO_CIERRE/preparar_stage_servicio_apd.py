"""One closed portable APD service component, without operational backups.

Copies exact successful/adverse primaries, their executed sources and portable
reference outputs. Full local paired snapshots/journals remain outside analysis.
"""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def write(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--r01',type=Path,required=True);p.add_argument('--r02',type=Path,required=True);p.add_argument('--r03',type=Path,required=True);p.add_argument('--r04',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);p.add_argument('--prueba-corta',type=Path,required=True);a=p.parse_args();out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False);here=Path(__file__).resolve().parent;jobs=[];omissions=[]
    def copy(source,relative):
        target=out/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        if sha(source)!=sha(target):raise ValueError('Exact stage member differs: '+relative)
    common=('RESULTADO.json','PROTOCOLO.json','CONFIG_READY.json','REGISTROS_APD.json.gz','PROYECCION_TRANSPORTE.json','BASELINE_P26.json.gz','CAMPOS_Y_RECIBOS_COMPLETOS.json.gz','ARTEFACTOS_REALES.json','ADMISIONES_Y_EVENTOS.jsonl','FUENTES_Y_CORTE_ANTES_DEL_PRIMER_TICK.json','CODIGO_ENSAYO.py')
    for label,source in(('R01',a.r01),('R02',a.r02),('R03',a.r03),('R04',a.r04)):
        for name in common:copy(source/name,'EVIDENCIA/'+label+'/'+name)
        for name in('RESERVA_PARES_NUEVOS.json','CODIGO_HELPER_PASIVO_R02.py','NOVELTY_POST_PANEL.json','HISTORIA_PREVIA_DE_EJECUCION.json'):
            if(source/name).is_file():copy(source/name,'EVIDENCIA/'+label+'/'+name)
        for folder in('artefactos','codigo'):
            for f in sorted((source/folder).rglob('*')):
                if f.is_file():copy(f,'EVIDENCIA/'+label+'/'+f.relative_to(source).as_posix())
        copy(source/'RECALCULO_SERVICIO_APD.json','EVIDENCIA/'+label+'/RECALCULO_SERVICIO_APD.json')
        if label=='R01':
            for name in('CORTE_INTERRUMPIDO.json','RECALCULO_INTERRUPCION.json','PANELES_Y_FUNCIONES_R03_DENOMINADORES.json','RECALCULO_SERVICIO_APD_R01_ERROR_GEOMETRIA_TRES.json'):
                copy(source/name,'EVIDENCIA/R01/'+name)
            code=source/'CODIGO_RECALCULO_R02'
            for f in code.glob('*.py'):copy(f,'RECALCULO/R01/'+f.name)
            for f in(source/'CODIGO_RECALCULO_R01').glob('*.py'):copy(f,'INSTRUMENTO_HISTORICO/R01_ERROR_LECTOR_TRES/'+f.name)
            copy(source/'resumir_funciones_apd_R03.py','RECALCULO/R01/resumir_funciones_apd_R03.py')
            manifest=source/'CORTE_INTERRUMPIDO_POSTSTOP/EXPORTACION_SERVICIO.json';copy(manifest,'CONTINUIDAD/R01_EXPORTACION_SERVICIO.json')
            reference_pairs=[('recalcular_servicio_apd.py','RECALCULO_SERVICIO_APD.json'),('recalcular_interrupcion_apd.py','RECALCULO_INTERRUPCION.json'),('resumir_funciones_apd_R03.py','PANELES_Y_FUNCIONES_R03_DENOMINADORES.json')]
        elif label=='R02':
            for name in('CORTE_INTERRUMPIDO.json','RECALCULO_INTERRUPCION.json','PANELES_Y_FUNCIONES.json'):copy(source/name,'EVIDENCIA/R02/'+name)
            for f in(source/'CODIGO_RECALCULO_FINAL_R02').glob('*.py'):copy(f,'RECALCULO/R02/'+f.name)
            manifest=source/'CORTE_INTERRUMPIDO_POSTSTOP/EXPORTACION_SERVICIO.json';copy(manifest,'CONTINUIDAD/R02_EXPORTACION_SERVICIO.json')
            reference_pairs=[('recalcular_servicio_apd.py','RECALCULO_SERVICIO_APD.json'),('recalcular_interrupcion_apd_r02.py','RECALCULO_INTERRUPCION.json'),('resumir_funciones_apd.py','PANELES_Y_FUNCIONES.json')]
        elif label=='R03':
            code=source/'CODIGO_RECALCULO_FINAL'
            for f in code.glob('*.py'):copy(f,'RECALCULO/R03/'+f.name)
            for name in('RECALCULO_TIEMPO_APD.json','PANELES_Y_FUNCIONES.json','CORTE_PARA_MANUAL.json'):copy(source/name,'EVIDENCIA/R03/'+name)
            manifest=source/'PAQUETE_FINAL_POSTSTOP/EXPORTACION_SERVICIO.json';copy(manifest,'CONTINUIDAD/R03_EXPORTACION_SERVICIO.json')
            reference_pairs=[('recalcular_servicio_apd.py','RECALCULO_SERVICIO_APD.json'),('recalcular_tiempo_apd.py','RECALCULO_TIEMPO_APD.json'),('resumir_funciones_apd.py','PANELES_Y_FUNCIONES.json')]
            # Pilot bytes already verified from their actual files, once only.
            copy(source/'PILOTO_APD.json.gz','EVIDENCIA/R03/PILOTO_APD.json.gz');copy(source/'RECALCULO_PILOTO_APD.json','EVIDENCIA/R03/RECALCULO_PILOTO_APD.json')
            for f in(source/'PILOTO_CODIGO').rglob('*'):
                if f.is_file():copy(f,'EVIDENCIA/R03/PILOTO_CODIGO/'+f.relative_to(source/'PILOTO_CODIGO').as_posix())
            reference_pairs.append(('recalcular_piloto_apd.py','RECALCULO_PILOTO_APD.json'))
        else:
            for f in(source/'CODIGO_RECALCULO_FINAL').glob('*.py'):copy(f,'RECALCULO/R04/'+f.name)
            for name in('RECALCULO_TIEMPO_APD.json','PANELES_Y_FUNCIONES.json','CORTE_PARA_MANUAL.json'):copy(source/name,'EVIDENCIA/R04/'+name)
            manifest=source/'PAQUETE_FINAL_POSTSTOP/EXPORTACION_SERVICIO.json';copy(manifest,'CONTINUIDAD/R04_EXPORTACION_SERVICIO.json')
            reference_pairs=[('recalcular_servicio_apd.py','RECALCULO_SERVICIO_APD.json'),('recalcular_tiempo_apd_r04.py','RECALCULO_TIEMPO_APD.json'),('resumir_funciones_apd.py','PANELES_Y_FUNCIONES.json')]
        for script,reference in reference_pairs:jobs.append({'id':label+'_'+Path(script).stem,'name':label+'_'+Path(script).stem,'base':'.','script':'RECALCULO/'+label+'/'+script,'args':['--evidencia','EVIDENCIA/'+label,'--salida','{output}'],'reference':'EVIDENCIA/'+label+'/'+reference,'scope':'Archived data recalculation only, no DEE/worker/native ticks'})
        for name in('OWNER_1_STDOUT.txt','OWNER_1_STDERR.txt','OWNER_2_STDOUT.txt','OWNER_2_STDERR.txt'):
            if(source/name).exists():copy(source/name,'EVIDENCIA/'+label+'/'+name)
        for original in(source/'REGISTROS_TRANSPORTE.json.gz',source/'REGISTROS_TRANSPORTE_POSTSTOP.json.gz'):
            if original.exists():omissions.append({'file':str(original),'bytes':original.stat().st_size,'sha256':sha(original),'why':'Full inherited transport history remains local; every current-prefix row and frozen inherited pending row is exported in REGISTROS_APD with original hash and exact selection procedure.'})
        for row in read(manifest)['members']:
            if row['file']in('VIDA.deetsnap.gz','cola.sqlite3')or row['file'].startswith('resultados/'):
                omissions.append({'file':str(manifest.parent/row['file']),'bytes':row['bytes'],'sha256':row['sha256'],'why':'Complete operational snapshot/journal/outbox remains local and in full collaboration delivery, not the reduced scientific analysis.'})
    for source in here.glob('*.py'):
        # Exact closure/harness/instrument tools; operative S sources are the
        # archived copies under each trial, not mutable current originals.
        copy(source,'CODIGO_CIERRE/'+source.name)
    for source in here.glob('APLICAR_S_APD01_*.patch'):copy(source,'CODIGO_CIERRE/'+source.name)
    for source in(here/'distribucion').glob('*'):
        if source.is_file()and source.suffix in('.py','.json','.md'):copy(source,'CODIGO_CIERRE/distribucion/'+source.name)
    for label in('JOB_ACCOUNTING_N0_R01','JOB_ACCOUNTING_N0_R02'):
        folder=a.r03.parent/label
        if folder.is_dir():
            for source in folder.rglob('*'):
                if source.is_file():copy(source,'EVIDENCIA/INSTRUMENTACION/'+label+'/'+source.relative_to(folder).as_posix())
    copy(a.r03/'RESULTADOS_SERVICIO_APD.md','INFORME_R03_PROCESOS_SEPARADOS.md')
    copy(a.r04/'RESULTADOS_SERVICIO_APD.md','RESULTADOS_SERVICIO_APD.md')
    write(out/'PLAN_RECALCULO.json',{'schema':'DEE.portable_recalculation.plan.v1','jobs':jobs,'scope':'Thirteen standard-library jobs: pilot once; two technical negatives; R03continuous-world with process reload; R04one-owner interval including final fixed panels. Minutes from different windows are never added. R1postpanel candidate was superseded without execution. No native replay or operational world restoration.'})
    write(out/'INDICE_OMISIONES.json',{'files':omissions,'scope':'Local complete operational bytes are deliberately not claimed to be present in this reduced analysis. All results, controls, native uint64 projections and actual decisive artifact bytes are exported.'})
    portable=a.prueba_corta.resolve();portable.mkdir(parents=True,exist_ok=False);shutil.copytree(out,portable/'SERVICIO');base=portable/'SERVICIO';checks=[]
    for i,job in enumerate(jobs):
        output=portable/('RESULTADO_'+str(i)+'.json');argv=[sys.executable,'-I','-B',job['script'],*[str(output)if x=='{output}'else x for x in job['args']]];r=subprocess.run(argv,cwd=base,capture_output=True,text=True,encoding='utf8',timeout=180);expected=base/job['reference'];same=r.returncode==0 and output.exists()and output.read_bytes()==expected.read_bytes();checks.append({'id':job['id'],'argv':argv,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'reference_sha256':sha(expected),'actual_sha256':sha(output)if output.exists()else None,'byte_identical':same})
        if not same:break
    write(out/'PRUEBA_PORTABLE.json',{'schema':'DEE.APD01.service_portability.v1','native_ticks':0,'cases':checks,'all_byte_identical':len(checks)==len(jobs)and all(c['byte_identical']for c in checks),'scope':'Actual standard-library recomputation from a separately copied short location. No original path is resolved to calculate results; absolute strings in primaries are source locators only.'})
    members=[{'file':f.relative_to(out).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(out.rglob('*'))if f.is_file()and f.name!='MANIFIESTO.json'];write(out/'MANIFIESTO.json',{'schema':'DEE.closed_component.manifest.v1','members':members,'self_exclusion':'MANIFIESTO.json only; PRUEBA_PORTABLE is included','scope':'Exact exported bytes and declared local omissions, not an operational backup.'})
    print(json.dumps({'stage':str(out),'files':len(members)+1,'bytes':sum(r['bytes']for r in members),'all_byte_identical':len(checks)==len(jobs)and all(c['byte_identical']for c in checks),'manifest_sha256':sha(out/'MANIFIESTO.json')}));return not(len(checks)==len(jobs)and all(c['byte_identical']for c in checks))
if __name__=='__main__':raise SystemExit(main())
