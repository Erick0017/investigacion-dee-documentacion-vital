"""Prepare table values from primary recalculation and preserved scope records.

The four requested CSVs are authored/round-trip checked by tablas.mjs. This
preparation never imports a participant and never assigns a new NSM level.
"""
from pathlib import Path
import argparse,json,csv,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from codec import Reader,canonical
sys.stdout.reconfigure(encoding='utf8')
def read(p):return json.loads(p.read_text(encoding='utf8'))
def text(v):return ''if v is None else json.dumps(v,ensure_ascii=False,separators=(',',':'))if isinstance(v,(dict,list))else str(v)
def matrix(rows,headers=None):
    headers=headers or list(rows[0]);return{'headers':headers,'rows':[[text(r.get(k))for k in headers]for r in rows]}
def main():
    p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--recalculation',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();reader=Reader(a.package/'EVIDENCIA_PRIMARIA_ESENCIAL');lookup={}
    for r in reader.index['documents']:
        for o in r['origins']:lookup[(o.get('archive'),o.get('logical_path',o.get('member')))]=r['id']
    def d(rel):return reader.get(lookup[('CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip','CPC9/'+rel)])
    calc=read(a.recalculation/'CALCULOS_RECALCULADOS.json');trajectory=read(a.recalculation/'TRAYECTORIA_DATOS.json')
    original=a.package/'EVIDENCIA_PRIMARIA_ESENCIAL/MATRIZ_ORIGINAL_CPC01_A_CPC09.csv'
    with original.open(encoding='utf-8-sig',newline='')as f:rows=list(csv.DictReader(f));headers=list(rows[0])
    for r in rows:
        r.update(auditoria_esencial='Sin nueva ejecución nativa; evidencia histórica y de E1 separadas',fuente_matriz_original='EVIDENCIA_PRIMARIA_ESENCIAL/MATRIZ_ORIGINAL_CPC01_A_CPC09.csv',nueva_integracion_por_compartir_paquete='NO')
    tables={'MATRIZ_CAPACIDADES_CPC01_CPC09.csv':matrix(rows,headers+['auditoria_esencial','fuente_matriz_original','nueva_integracion_por_compartir_paquete'])}
    ns=d('revision/NSM65_EVIDENCIAS.json');nrows=[]
    # Authored critical readings, distinct from the original level labels.
    special={
      'NSM65.TWO':'Firma funcional de dos contactos/contribuciones calibradas; no cardinalidad abstracta ni aprendizaje del significado lingüístico completo.',
      'NSM65.BEFORE':'Historia de dos eventos y orden físico con uso posterior; transferencia semántica amplia y ligamiento general de referentes no demostrados.',
      'NSM65.TOUCH':'Contacto y conservación/asociación funcional finitos; lector renovado tardío falla; no concepto humano completo.',
      'NSM65.MORE':'La experiencia adquiere y revisa la referencia54→67. La ley comparativa estaba preparada; E3 original corresponde al uso reservado acotado, no al aprendizaje del operador MÁS.',
      'NSM65.LIKE_AS':'Componente direccional adquirido utilizado por normalizadores/comparadores preparados; no similitud general aprendida.'}
    for e in ns['entries']:
        dim=e['dimensions_A_J'];witness=[]
        for w in e.get('primary_witnesses',[]):
            path=w['member'].replace('\\','/');witness.append({'member':path,'sha256':w['sha256'],'audit_document':lookup.get(('CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip','CPC9/'+path)),'scope':w.get('coverage')})
        nrows.append({'id':e['id'],'forma_es':e['forma_es'],'grupo':e['grupo'],'glosa_fuente':e['glosa_fuente'],'pregunta_operacional':e['funcion_a_investigar'],
          'nivel_original_E1_maximo_episodico':e['E1_level'],'estado_experimental_original':e['experimental_status'],
          'evaluacion_critica_de_auditoria':special.get(e['id'],'No hay adquisición semántica atribuible a E1 en estos registros; los prerrequisitos o resultados auxiliares/históricos no la sustituyen.'),
          'significado_linguistico_completo_demostrado':'NO','disponible_al_final_2493':'NO_ESTABLECIDO; rechazo no equivale a borrado',
          **{'dimension_original_'+k:dim.get(k)for k in'ABCDEFGHIJ'},'aporte_externo':dim.get('J'),
          'prerrequisito_auxiliar':e.get('prerequisite_experiment'),'evidencia_historica':e.get('historical_positive'),'interpretacion_original_acotada':e.get('manual_assessment_scope'),
          'evidencias':witness,'faltante_especifico':e.get('remaining_specific_blocker',e.get('limitacion_y_evidencia_faltante'))})
    tables['ESTADO_REAL_NSM65.csv']=matrix(nrows)
    tables['TRAYECTORIA_CAUSAL_E1.csv']=matrix(trajectory)
    ixrows=[];seen=set()
    for r in reader.index['documents']:
        for o in r['origins']:
            key=(o.get('kind'),o.get('archive'),o.get('member'),o.get('logical_path'),o.get('path'))
            if key in seen:continue
            seen.add(key);origin=o.get('origin',{})
            ixrows.append({'evidence_id':r['id'],'tipo':o.get('kind'),'rol':r['role'],'archivo_origen':o.get('archive',o.get('path')),'sha256_contenedor':o.get('archive_sha256'),
              'miembro_origen':o.get('member'),'ruta_logica_Core':o.get('logical_path'),'SHA256_bytes_originales':o['sha256'],'bytes_originales':o['bytes'],
              'SHA256_valores_JSON_canonicos':r['canonical_sha256'],'archivo_extraido_codificado':'EVIDENCIA_PRIMARIA_ESENCIAL/'+r['data_file'],'byte_offset':r.get('byte_offset'),'bytes_registro':r.get('record_bytes',r['encoded_bytes']),'SHA256_registro_codificado':r['data_sha256'],
              'modo_sin_perdida_de_valores':r['mode'],'documento_base':r.get('base'),'archivo_historico_anterior':origin.get('archive',origin.get('archive_sha256')),
              'miembro_historico_anterior':origin.get('member',origin.get('relative')),'nota_identidad':'El SHA original verifica bytes de origen; el SHA canónico verifica todos los valores JSON. No se promete recuperar el espacio en blanco original.'})
    for f in sorted((a.package/'EVIDENCIA_PRIMARIA_ESENCIAL/CAMPOS_COMPACTOS').glob('S*.json')):
        data=read(f);o=data['source_snapshot'];ixrows.append({'evidence_id':f.stem,'tipo':'EXACT_UINT64_ARRAY_EXTRACTION','rol':'Campos físicos completos; no snapshot operativo','archivo_origen':o['archive'],'sha256_contenedor':o['archive_sha256'],
          'miembro_origen':o['member'],'SHA256_bytes_originales':o['sha256'],'archivo_extraido_codificado':f.relative_to(a.package).as_posix(),'nota_identidad':'RAW/clocks uint64le reconstruibles exactamente; metadata operativa del snapshot original excluida.'})
    index_headers=list(ixrows[0]);tables['INDICE_EVIDENCIA_ORIGINAL.csv']=matrix(ixrows,index_headers)
    if len(rows)!=68 or len(nrows)!=65 or len(trajectory)!=352:raise ValueError('Requested table coverage mismatch')
    with a.out.open('x',encoding='utf8')as f:json.dump({'tables':tables,'row_counts':{n:len(t['rows'])for n,t in tables.items()}},f,ensure_ascii=False,separators=(',',':'));f.write('\n')
    print(json.dumps({'status':'PASS','tables':{n:len(t['rows'])for n,t in tables.items()},'semantic_levels_not_awarded_by_script':True}))
if __name__=='__main__':main()
