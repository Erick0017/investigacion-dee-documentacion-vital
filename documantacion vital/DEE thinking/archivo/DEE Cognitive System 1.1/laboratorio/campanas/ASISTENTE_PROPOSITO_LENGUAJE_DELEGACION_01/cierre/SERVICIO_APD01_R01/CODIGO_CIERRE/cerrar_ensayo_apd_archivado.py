"""Archive closure sources, then run only read-only extraction/recalculation.

Never starts a Runtime or retries material work. All evidence is tied to the
reached stopped cut; files are created exclusively, preserving earlier failures.
"""
import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in('sistema','ensayo','configuracion','historia-inicial','piloto','presupuesto'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--revision',choices=('R03','R04'),required=True);a=p.parse_args();trial=a.ensayo.resolve();result=json.loads((trial/'RESULTADO.json').read_bytes())
    if not result.get('final')or not result.get('final_paired_export'):raise ValueError('A durable reached post-run cut and actual pre-STOP export are required; never fabricate a replacement')
    code=trial/'CODIGO_RECALCULO_FINAL';code.mkdir(exist_ok=False);here=Path(__file__).resolve().parent
    names=['auditar_apd_resultados_r04.py','recalcular_servicio_apd.py','resumir_funciones_apd.py','recalcular_tiempo_apd.py','recalcular_tiempo_apd_r04.py','recalcular_piloto_apd.py','exportar_ensayo_apd.py','documentar_corte_apd.py','redactar_resumen_servicio_apd_r03.py','redactar_resumen_servicio_apd_r04.py','cerrar_ensayo_apd_archivado.py']
    sources=[]
    for name in names:
        source=here/name;shutil.copyfile(source,code/name);sources.append({'file':name,'bytes':source.stat().st_size,'sha256':sha(source)})
    with(trial/'FUENTES_CIERRE_ANTES_DEL_RECALCULO.json').open('x',encoding='utf8')as f:json.dump({'sources':sources,'native_ticks':0,'scope':'Exact closure code bytes archived before executing calculations; native sources were separately archived before the reserve.'},f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    commands=[('exportar_ensayo_apd.py',['--sistema',a.sistema,'--ensayo',trial,'--configuracion',a.configuracion,'--historia-inicial',a.historia_inicial,'--piloto',a.piloto]),('recalcular_servicio_apd.py',['--evidencia',trial,'--salida',trial/'RECALCULO_SERVICIO_APD.json']),('recalcular_tiempo_apd.py'if a.revision=='R03'else'recalcular_tiempo_apd_r04.py',['--evidencia',trial,'--salida',trial/'RECALCULO_TIEMPO_APD.json']),('resumir_funciones_apd.py',['--evidencia',trial,'--salida',trial/'PANELES_Y_FUNCIONES.json'])]
    if a.revision=='R03':commands.append(('recalcular_piloto_apd.py',['--evidencia',trial,'--salida',trial/'RECALCULO_PILOTO_APD.json']))
    commands.append(('documentar_corte_apd.py',['--sistema',a.sistema,'--ensayo',trial,'--presupuesto',a.presupuesto]))
    outputs=[]
    for index,(script,args)in enumerate(commands):
        argv=[sys.executable,'-I','-B','-X','utf8',str(code/script),*map(str,args)];r=subprocess.run(argv,capture_output=True,text=True,encoding='utf8',timeout=600)
        item={'script':script,'argv':argv,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr};outputs.append(item)
        with(trial/('CIERRE_PASO_'+str(index).zfill(2)+'.json')).open('x',encoding='utf8')as f:json.dump(item,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
        print(json.dumps({'script':script,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}),flush=True)
        if r.returncode:break
    with(trial/'RECORRIDO_CIERRE_ARCHIVADO.json').open('x',encoding='utf8')as f:json.dump({'revision':a.revision,'native_ticks':0,'sources':sources,'steps':outputs,'all_completed':len(outputs)==len(commands)and all(x['returncode']==0 for x in outputs)},f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    return len(outputs)!=len(commands)or any(x['returncode']for x in outputs)
if __name__=='__main__':raise SystemExit(main())
