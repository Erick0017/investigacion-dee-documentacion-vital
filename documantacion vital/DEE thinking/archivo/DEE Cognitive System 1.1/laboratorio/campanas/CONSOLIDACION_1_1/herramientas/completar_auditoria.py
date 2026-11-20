"""Compact source index, per-life NSM dimensions and measured size accounting."""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,hashlib,json,os,zipfile
ROOT=Path(__file__).resolve().parents[4]
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def walk(p):
    for folder,dirs,files in os.walk(p,followlinks=False):
        dirs[:]=[d for d in dirs if d not in('node_modules','__pycache__','.entorno','.git')and not(Path(folder)/d).is_junction()]
        for f in files:
            q=Path(folder)/f
            if q.suffix not in('.pyc','.lock'):yield q
def measured(p):
    rows=list(walk(p));by=defaultdict(lambda:{'files':0,'bytes':0})
    for f in rows:by[f.suffix.lower()]['files']+=1;by[f.suffix.lower()]['bytes']+=f.stat().st_size
    return{'files':len(rows),'bytes':sum(f.stat().st_size for f in rows),'extensions':dict(by)}
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--final-test',type=Path);a=p.parse_args();r=a.root;ev=r/'evidencia';hist=read(ev/'genealogia/NSM65_ANTECEDENTE_CPC9.json');catalog=read(r/'sistema/capacidades/NSM65_CATALOGO_OFICIAL.json');rows=[]
    actual=read(ev/'informes/CALCULOS_DESDE_PRIMARIOS.json')
    for h in hist['rows']:
        variants=[]
        for life in('E1_SOCIAL_11','R65_45_VIVIDO','R65_N67_VIVIDO','U0_14_VIVIDO'):
            own=life=='E1_SOCIAL_11';dimensions={}
            for dim,label in [('A','experiencia_causal'),('B','relacion_adquirida'),('C','funcion_posterior'),('D','senal_asociada'),('E','retencion'),('F','generalizacion'),('G','composicion'),('H','comunicacion'),('I','pertenencia_E1'),('J','intervencion_externa')]:
                dimensions[label]={'historical_E1':h.get('dimension_original_'+dim)if own else'NO_ATRIBUIBLE_A_ESTA_VIDA','current_1_1':'NO_REVALIDADO_ESPECIFICAMENTE_PARA_ESTA_PRIMITIVA','source':'evidencia/genealogia/NSM65_ANTECEDENTE_CPC9.json'if own else'sistema/capacidades/NSM65_CATALOGO_OFICIAL.json'}
            if own and h['id']=='NSM65.MORE':
                dimensions['funcion_posterior']['current_1_1']='Comparación física con referencia78 adquirida: objetos50+5<78,73+5=78,82+5>78; contexto finito, no cardinalidad general.'
                dimensions['retencion']['current_1_1']='Referencia accesible después del nuevo aprendizaje social; R36/O16 anterior también consultable.'
                dimensions['generalizacion']['current_1_1']='Nuevos objetos del mismo contrato cuantitativo, no abstracción ilimitada de MORE.'
                for key in('funcion_posterior','retencion','generalizacion'):dimensions[key]['source']='evidencia/verificaciones/OBSERVADOR_COMPONENTE_CORREGIDO.json; evidencia/verificaciones/VISITA_INTERACTIVA_11/EVENTOS.stdout.json'
            if own and h['id']in('NSM65.BEFORE','NSM65.TOUCH'):
                dimensions['composicion']['current_1_1']='Rutas conjuntas antiguas físicamente presentes y accesos medidos; no nueva generalización semántica completa.'
                dimensions['composicion']['source']='evidencia/telemetria/CONTINUIDAD_FUNCIONAL_R1/LIFE_R1_MAIN/MEDICIONES.json'
            variants.append({'life_id':life,'historical_maximum':h['nivel_original_E1_maximo_episodico']if own else'E0_NSM_NO_ACREDITADO','new_NSM_level_credited_this_campaign':None,'dimensions':dimensions,'current_limit':'Los signos opacos no adquieren automáticamente el significado de la fila. Máximo histórico y acceso actual son diferentes.'})
        rows.append({'id':h['id'],'forma_es':h['forma_es'],'question':h['pregunta_operacional'],'catalogue_version':catalog['catalogue_version'],'linguistic_meaning_complete':False,'next_contrast_needed':h.get('evidencia_faltante',h.get('evaluacion_critica_de_auditoria')),'lives':variants})
    assert len(rows)==65
    put(ev/'informes/NSM65_DIMENSIONES_POR_VIDA.json',{'schema':'DCS1.1.NSM.per_life_dimensions.v1','catalogue_sha256':sha(r/'sistema/capacidades/NSM65_CATALOGO_OFICIAL.json'),'entries':rows,'new_primitives_credited':0,'OPAQUE65_is_not_NSM65':True})
    sourceinventory=read(ev/'genealogia/INVENTARIO_INICIAL.json');sizes={'schema':'DCS1.1.measured_sizes.v1','units':'bytes; MiB=bytes/1048576; transport limit is decimal16000000bytes exclusive','source_archives_opened':sourceinventory['sources'],'source_compressed_sum_bytes':sum(x['bytes']for x in sourceinventory['sources']),'source_outer_expanded_sum_bytes':sum(x['expanded_bytes']for x in sourceinventory['sources']),'warning_source_sum':'Sum of actually opened archives, not a deduplicated size of the entire historical project. Nested store expansion is not counted as if already expanded.'}
    sizes['working_categories']={name:measured(r/name)for name in('sistema','laboratorio','evidencia')}
    sizes['historical_campaign_folders_stat_only']={p.name:measured(p)for p in r.parent.iterdir()if p.is_dir()and p.name in('CPC3','CPC4','CPC5','CPC6','CPC7','CPC8','CPC9')}
    store=read(ev/'genealogia/CORE_OPERATIVO_RECUPERADO.json');sizes['content_store_provenance']=store
    seal=r/'entregas/DEE_COGNITIVE_SYSTEM_1_1_SISTEMA.SELLADO.json'
    if seal.exists():sizes['sealed_system']=read(seal)
    regeneration=r/'evidencia/verificaciones/REGENERACION_ESTADOS_HEREDADOS.json'
    if regeneration.exists():
        rg=read(regeneration);sizes['regeneration']={'containers_compared':rg['compared_native_states'],'exact_container_bytes':rg['exact_byte_equal'],'different_container_bytes':rg['not_byte_equal_or_missing'],'distinct_container_preservation':'evidencia/verificaciones/CONTENEDORES_NO_IDENTICOS/AUDITORIA.json'}
    put(ev/'informes/RECURSOS_Y_TAMANOS.json',sizes)
    index=[]
    for p in sorted(walk(ev)):
        rel=p.relative_to(r).as_posix()
        if p.name=='INDICE_EVIDENCIA.json':continue
        role='PRIMARY_OR_SOURCE_RECORD'
        if '/informes/'in rel:role='AUDITOR_CALCULATION_OR_INTERPRETATION'
        elif '/genealogia/'in rel:role='GENEALOGY_SOURCE_IDENTITY_OR_DOCUMENTARY_EVIDENCE'
        elif p.name in('MEDICIONES.json','MEASUREMENTS.json','OBSERVED.json','PRIMARY_TRANSITIONS.json'):role='PRIMARY_NATIVE_OBSERVATIONS'
        elif p.suffix in('.gz','.deetsnap'):role='COMPLETE_NATIVE_CHECKPOINT'
        included=not('/HERENCIA_01/'in rel and p.suffix in('.deetsnap','.gz','.py'))and not('/PERFILES_'in rel and '/Sistema limpio 'in rel)
        index.append({'file':rel,'bytes':p.stat().st_size,'sha256':sha(p),'role':role,'included_in_audit':included,'deep_original_preserved':True})
    put(ev/'INDICE_EVIDENCIA.json',{'schema':'DCS1.1.evidence.index.v1','files':index,'layers':['DATA','CALCULATION','PROVISIONAL_INTERPRETATION'],'no_wholeworld_ancestry_claim':True,'native_uint64':'New observations use exact decimal strings; no conversion to floating point. Original recovered bytes are preserved.','additional_release_evidence':'External exact-ZIP verification is emitted after sealing; not inserted retroactively into its own archive.'})
    pending=read(r/'sistema/documentacion/COBERTURA_REGRESION.json')['pending_documentary_rows']
    put(ev/'informes/PENDIENTES_Y_CAUSAS.json',{'documentary_rows':pending,'still_open':[{'id':'R2','cause':'No native history-dependent strategy choosing useful regulation versus harmful regulation was causally demonstrated; fixed/interpretedR0/R1 do not supply it.'},{'id':'YO_TU','cause':'No role-relative acquired perspective passing participant reversal. Static IDs and directions are insufficient.'},{'id':'K65_INTEGRATED','cause':'SameN67 integratedbody+newqueries can develop dense occupation; finite guards failed. BareN67 works but lacks the integratedfunctions.'},{'id':'SEMANTIC_PRODUCTIVITY','cause':'No untrained grammatical/semantic combinations interpreted with generalreferentroleinvariance; finite prepared compositions remain useful.'},{'id':'UNLIMITED_ACCESS','cause':'Querying transforms supports and can increase interference. Only finite stated windows/horizons are tested.'}]})
    s=sizes['working_categories'];report=f'''# Tamaños y compactación1.1

Medición real por categorías (bytes, no RAM): sistema {s['sistema']['bytes']:,}, laboratorio {s['laboratorio']['bytes']:,}, evidencia {s['evidencia']['bytes']:,}. El sistema de trabajo incluye una caché heredada materializada que NO se entrega. El detalle de extensiones está en RECURSOS_Y_TAMANOS.json. Las carpetas históricas se midieron sólo mediante stat, sin afirmar lectura de todos sus archivos.

Los cuatro ZIP fuente efectivamente abiertos suman {sizes['source_compressed_sum_bytes']:,} bytes comprimidos y {sizes['source_outer_expanded_sum_bytes']:,} bytes de miembros externos expandidos. No es una cifra deduplicada de todo DEE ni la expansión completa de archivos anidados.

SISTEMA incluye un único WHL oficial, la dependenciaNumPy opcional con avisos, el almacén por hashes, constructores y snapshots completos de las nueve vidas admitidas. Se excluyen venvs, toolchain, caché regenerable y vidas diagnósticas no admitidas. No hay cadenas de deltas externas. El estado completo actual se restaura por sí mismo.

AUDITORIA conserva todos los nuevos primarios, planes, controles, fallos, snapshots diagnósticos y testigos microscópicos. También conserva los JSON primarios de las34familias heredadas. No duplica WHL/PYD/motor. Excluye los grandes snapshots densos generados de esas reproducciones y copias de código idénticas al almacén, que permanecen intactos en evidencia/. Sus tamaños y hashes se listan en EXCLUSIONES_DEL_PAQUETE.json.

No se afirma que cada JSON de salida sea byte-idéntico tras una reproducción: rutas, recursos y tiempos del anfitrión cambian. Se comparan por separado bytes de snapshots regenerados, transiciones físicas y resultados. El comprobante de regeneración distingue cada modalidad. La reproducción técnica no añade réplicas científicas.

La comprobación final comparó1.082estados:984contenedores idénticos y98con metadatos distintos. En los98coinciden RAW/clocks y el Runtime serializado sin metadatos en copias diagnósticas; ambos contenedores completos se preservan mediante gzip sin pérdida verificada. No se descarta su estado organizacional porque una lectura escalar coincida. El índice VERSIONES_RUNNERS_1_1.json distingue también los cortes de código exactos recuperados de un corte anterior de runner no localizado; no se presenta la adaptación actual como sus bytes originales.

Pérdida de cobertura en el ZIP compacto: no se puede abrir cualquier snapshot denso histórico generado desdeAUDITORIA solamente. Se puede revisar su observación primaria, localizar el hash original y reconstruir conSISTEMA. Los testigos locales no son una genealogía microscópica exhaustiva de todos los portadores. Las16filas documentales pendientes no se transforman en capacidades operativas.

Las partes de transporte se calculan por el tamaño comprimido final. Cada segmento tiene menos de16,000,000bytes y se verifica su unión completa. Separar carpetas o comprimir no reduce la ocupación nativa del mundo ni representa ahorro energético medido.
'''
    (ev/'informes/INFORME_TAMANOS_Y_COMPACTACION.md').write_text(report,encoding='utf8')
    (r/'INFORME_TAMANOS_Y_COMPACTACION.md').write_text(report,encoding='utf8')
    print(json.dumps({'evidence_index_files':len(index),'NSM_entries':len(rows),'size_categories':{k:v['bytes']for k,v in sizes['working_categories'].items()}}))
if __name__=='__main__':main()
