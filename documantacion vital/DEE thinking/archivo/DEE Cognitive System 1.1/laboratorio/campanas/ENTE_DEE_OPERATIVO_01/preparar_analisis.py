"""Exporta evidencia cerrada y delta; no restaura el motor ni ejecuta ticks."""
from pathlib import Path
import hashlib,json,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];SYSTEM=ROOT/'sistema';E=ROOT/'evidencia/campanas/ENTE_DEE_OPERATIVO_01';C=HERE/'cierre';OUT=C/'PAQUETE_ANALISIS'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def main():
    if OUT.exists():raise FileExistsError('Prior staged package protected: '+str(OUT))
    OUT.mkdir(parents=True);sources=[]
    def cp(src,name):
        src=Path(src);dest=OUT/name
        if dest.exists():raise FileExistsError('Duplicate output member '+name)
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
        expected=sha(src);assert sha(dest)==expected
        sources.append({'member':name,'source':str(src),'bytes':src.stat().st_size,'sha256':expected,'extraction':'Byte-identical complete file, no lossy editing'})
    for name in ['INFORME_CIENTIFICO.md','CAPACIDADES_POR_VIDA_Y_MOMENTO.json','INCORPORACIONES.md']:
        cp(C/name,name)
    cp(ROOT/'CONTINUIDAD_ENTE_DEE_OPERATIVO_01.json','CONTINUIDAD_ENTE_DEE_OPERATIVO_01.json')
    recalc=json.loads((C/'recalculo/resultados/RECALCULO_RESULTADOS.json').read_bytes())
    # Preserve exactly the closed recalculation input set. Later state-summary
    # checks are exported separately, not smuggled into its input denominator.
    for item in recalc['primaries']:
        src=E/item['path'];assert sha(src)==item['sha256']and src.stat().st_size==item['bytes']
        cp(src,'EVIDENCIA_CAUSAL/'+item['path'])
    for base in [E/'codigo_ejecutado',E/'social/codigo_ejecutado']:
        for p in sorted(base.rglob('*')):
            if p.is_file():cp(p,'EVIDENCIA_CAUSAL/'+p.relative_to(E).as_posix())
    for p in sorted((C/'recalculo').glob('*')):
        if p.is_file():cp(p,'RECALCULO/'+p.name)
    cp(C/'recalculo/resultados/RECALCULO_RESULTADOS.json','RECALCULO/REFERENCIA_RESULTADOS.json')
    for folder in ['mecanismo','social']:
        for p in sorted((HERE/folder).rglob('*')):
            if p.is_file()and '__pycache__'not in p.parts:cp(p,'CODIGO_EXPERIMENTAL/'+folder+'/'+p.relative_to(HERE/folder).as_posix())
    for name in ['PRESUPUESTO.json','RECURSOS_INICIALES.json','PROTOCOLO_Y_RESERVAS.json','SELLO_RESERVAS.json','PROTOCOLO_COOPERACION_AMBIENTAL.json','SELLO_RESERVAS_SOCIALES.json','PROTOCOLO_COLA_OPERATIVA.json','ejecutar_operacion.py','ejecutar_secuencia.py','comparar_observacion.py','cerrar_corte.py']:
        cp(HERE/name,'CODIGO_EXPERIMENTAL/'+name)
    for name in ['SNAPSHOT_FINAL_COMPLETO_VERIFICADO.json','INDICE_ESTADOS_COMPLETOS.json']:
        cp(E/name,'ESTADOS_Y_CONTINUIDAD/'+name)
    for name in ['gestionar.py','capacidades/ente_operativo_01.py','capacidades/ente_operativo_01_core.py','capacidades/CATALOGO_CAPACIDADES.json','contratos/EO01_ENTE_OPERATIVO.json','documentacion/GUIA_ENTE_OPERATIVO_01.md']:
        cp(SYSTEM/name,'DELTA_SISTEMA/sistema/'+name)
    cp(ROOT/'LEER_PRIMERO.md','DELTA_SISTEMA/LEER_PRIMERO.md')
    word=ROOT/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_10_ENTE01_SIN_VALIDACION_VISUAL.docx'
    cp(word,'MANUAL/'+word.name)
    for name in ['CAMBIOS_MANUAL.md','actualizar_manual_ente01.py','verificar_manual_ente01.py','RESULTADOS_MANUAL_ENTE01_FINAL.json','EDICION_MANUAL_1_10_ENTE01.json','qa_final_1_10/VERIFICACION_MANUAL_ENTE01.json']:
        cp(HERE/'documentos'/name,'MANUAL/'+name)
    cf=ROOT/'laboratorio/campanas/CF01_CIERRE_FUNCIONAL/cierre/PAQUETE_ANALISIS'
    for name in ['INFORME_CIENTIFICO.md','ANEXO_MECANISMO.md','AUDITORIA_ALCANCE_CF01.md']:
        cp(cf/name,'ANTECEDENTE_CF01/'+name)
    for name in ['SERVICIO_CF01_MAIN_V3.json.gz','SERVICIO_CF01_SERVICIO_ANULADO_V3.json.gz']:
        cp(ROOT/'evidencia/campanas/CF01_CIERRE_FUNCIONAL'/name,'ANTECEDENTE_CF01/'+name)
    cp(SYSTEM/'contratos/CF01_SERVICIO_CONTEXTUAL.json','ANTECEDENTE_CF01/CF01_SERVICIO_CONTEXTUAL.json')
    snapshots=[]
    for p in sorted((SYSTEM/'estado/checkpoints').glob('EO01*.deetsnap.gz')):
        snapshots.append({'source':str(p),'relative_to_system':p.relative_to(SYSTEM).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),'omitted_from_analysis':True,'reason':'Complete native/operational world remains local; selected MAIN/R02 states travel in the separate full collaborator package.'})
    index={'scope':'Essential analysis export, not an integral historical archive or operational backup','native_ticks_executed_by_export':0,'sources':sources,'complete_snapshots_omitted':snapshots,'selected_complete_states_for_full_package':['EO01_MAIN T121681','EO01_CORTE_R02 T95093','Previous admitted lives retained by updater'],'other_omissions':[{'item':'Official WHL, native engine and Python runtimes','location':'Original sistema/runtime and separate full collaboration package','identity_primary':'EVIDENCIA_CAUSAL/00_IDENTIDAD.json.gz','reason':'Not required for archived metric recalculation; this analysis is not a self-contained native installation.'},{'item':'All original life histories and earlier CPC/MI/CF corpora beyond the directed CF01 contrast','location':str(ROOT),'reason':'Previous results are not rerun; local genealogy and existing contracts retain their domains.'},{'item':'Deep complete snapshots prior to each operation','location':str(SYSTEM/'estado/checkpoints'),'locator':'See complete_snapshots_omitted and per-life HISTORIA.jsonl in sistema/estado/vidas','reason':'Analysis includes decisive microscopic traces, exact input/receipt records and full-state endpoint identities; does not claim all sites at every tick.'}],'recalculation_input_manifest_sha256':recalc['input_manifest_sha256'],'no_container_self_hash':True}
    (OUT/'INDICE_FUENTES_Y_OMISIONES.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    readme="""# Análisis EO01
Leer INFORME_CIENTIFICO.md y CAPACIDADES_POR_VIDA_Y_MOMENTO.json.
Con Python3.10+ estándar, sin motor:
    python RECALCULO/recalcular.py --primarios EVIDENCIA_CAUSAL --codigos EVIDENCIA_CAUSAL/codigo_ejecutado --salida RECALCULADO
RECALCULADO/RECALCULO_RESULTADOS.json debe ser byteidéntico a RECALCULO/REFERENCIA_RESULTADOS.json.
El delta contiene bytes operativos para revisión; no es un instalador autónomo. Use el paquete completo para ejecutar/continuar vidas.
No sobrescriba una instalación distinta ni trabajo_personal sin comprobar compatibilidad y guardar sus estados.
No incluye motor ni todos los snapshots. INDICE_FUENTES_Y_OMISIONES identifica originales completos.
La verificación del ZIP completo se conserva fuera de ese contenedor para evitar autorreferencias; puede viajar como miembro adicional de este análisis final.
"""
    (OUT/'LEER_PRIMERO.md').write_text(readme,encoding='utf8')
    release={'schema':'EO01.closed_scientific_export.v1','campaign':'ENTE_DEE_OPERATIVO_01','status':'CLOSED_SCIENTIFIC_CUT','life':'EO01_MAIN','tick':121681,'snapshot_sha256':'2ecbc6dee1c5b2ec41d18b28037c5022b18d45aa2137ba8d4f8ceaf35626aa52','analysis_stage':str(OUT),'manual_sha256':sha(word),'no_active_main_writer':not any((SYSTEM/'estado/locks').glob('EO01_MAIN.lock')),'source_files':len(sources),'input_manifest_sha256':recalc['input_manifest_sha256'],'private_no_remote_publication':True}
    (C/'CORTE_CERRADO.json').write_text(json.dumps(release,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'stage':str(OUT),'files':len([p for p in OUT.rglob('*')if p.is_file()]),'bytes':sum(p.stat().st_size for p in OUT.rglob('*')if p.is_file()),'complete_local_snapshots_indexed':len(snapshots),'release':str(C/'CORTE_CERRADO.json')},ensure_ascii=False))
if __name__=='__main__':main()
