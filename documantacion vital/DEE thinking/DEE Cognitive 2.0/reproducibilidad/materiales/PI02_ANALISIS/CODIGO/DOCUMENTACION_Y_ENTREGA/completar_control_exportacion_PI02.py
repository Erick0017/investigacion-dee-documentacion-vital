"""Compact documentary controls and explicit local omissions for the final ZIP."""
from pathlib import Path
import datetime,hashlib,json,shutil
P=Path(__file__).resolve().parent.parent;R=P.parent.parent.parent;C=R/'DEE Cognitive 2.0';S=C/'sistema';E=P/'entrega/EXPEDIENTE'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def desc(p):p=Path(p);return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def write(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=['documentos/DOCUMENTOS_PUBLICADOS_PI02_FINAL.json','documentos/ACTUALIZACION_DOCUMENTAL_PI02_FINAL_1_29.json','documentos/RENDER_WORD_PI02_FINAL_1_29_R01.json','documentos/QA_VISUAL_MANUAL_PI02_FINAL.json','documentos/QA_VISUAL_COMPENDIO_PI02_FINAL.json','control/DESPLIEGUE_OPERACION_R04_OP1.json','control/PROCESOS_PRE_INCORPORACION_PI02.json','control/DECISION_FINAL_PI02.json','control/TICKS_NATIVE_PI02_CIERRE_FINAL.json','control/RECURSOS_DISCO_R04.json']
for rel in files:
    src=P/rel
    if not src.is_file():
        if rel.endswith('TICKS_NATIVE_PI02_CIERRE_FINAL.json'):
            src=E/'EVIDENCIA/D_R04/PROTOCOLO/TICKS_NATIVE_PI02_CIERRE_FINAL.json'
        else:raise FileNotFoundError(str(src))
    dst=E/'CONTROL'/src.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
for name in('generar_informe_y_mapas_PI02.py','sellar_y_verificar_PI02.py','completar_control_exportacion_PI02.py','cerrar_texto_final_PI02.py','actualizacion_manual_PI02_final.py','publicar_documentos_PI02_FINAL.py','SELECCIONAR_EXPORTACION_CANONICA.py'):
    src=P/'codigo'/name;dst=E/'CODIGO/DOCUMENTACION_Y_ENTREGA'/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
thinking=[]
for name in('DEE_thinking_4_5_0_Maestro_Arquitectura_Reconstruccion.docx','DEE_thinking_4_5_0_Libro_Blanco_y_Manual_Tecnico.docx'):
    item=desc(R/'4.5'/name);item.update(reason='Official large complete manual stays local; PI01 full technical reading reused, directed PI02 notes exported. No replacement by a summary pretending to be this original.');thinking.append(item)
source=read(P/'control/PAR_FINAL_PI02.json');card=read(S/'estado/vidas/ECI02_PI02_MAIN/VIDA.json')
omissions={'schema':'DEE.PI02.explicit_local_omissions.v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'Thinking_complete_manuals':thinking,
 'engine':[dict(desc(S/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'),reason='Frozen official engine dependency, not duplicated in an analysis ZIP'),dict(desc(C/'motor/python313/site-packages/dee_thinking/_native.cp313-win_amd64.pyd'),reason='Frozen official Native binary, not copied')],
 'current_complete_operational_state':{'snapshot':desc(S/card['snapshot']),'identity_card':desc(S/'estado/vidas/ECI02_PI02_MAIN/VIDA.json'),'SQLite':desc(S/'estado/servicios_persistentes/ECI02_PI02_MAIN/cola.sqlite3'),'worker':str(S/'estado/servicios_locales/ECI02_PI02_MAIN'),'outbox':str(S/'estado/servicios_persistentes/ECI02_PI02_MAIN/resultados'),'paired_transport_seed':str(S/'estado/pares_iniciales/ECI02_PI02_MAIN'),'pair_manifest':desc(S/'estado/pares_iniciales/ECI02_PI02_MAIN/EXPORTACION_SERVICIO.json'),'members_in_seed':3365,'bytes_in_seed':158174090,'why':'Complete executable continuity retained locally. The imported seed precedes the final technical0tick transport operations, whose witness is exported; current product directories are authoritative.','minimum_for_new_Native_reproduction':'Bring the exact complete pair/closed current state plus Cognitive sources and frozen official engine, not just RAW/clocks or this ZIP.'},
 'experimental_full_states_and_deep_telemetry':{'root':str(P/'estados/candidato/sistema/estado'),'source_final_pair':source['pair'],'prefix_for_reproduction':desc(P/'control/PAR_POST_B_MAIN.json'),'primaries':str(P/'ensayos'),'transport_resource_ledger':desc(P/'ENSAYOS.jsonl'),'reason':'All lives, snapshots and deep records remain local. Exported compact primaries contain all positive/negative reserved opportunities and decisive controls, but not every full checkpoint or collision.','directory_wide_hash':'NOT_COMPUTED; explicit member/Native snapshot hashes apply only to their stated scope'},
 'historical_sources_not_repacked':{'PI01':str(P.parent/'PROGRESION_INTEGRADA_01'),'prior_audit_ZIP':str(R/'archivo/DEE_ESTADO_ACTUAL_Y_CONTINUIDAD_2026_11_07.zip'),'full_transversal_register':desc(R/'archivo/analisis_transversal_cognitivo/REVISION_TRANSVERSAL.json'),'reason':'Relevant source/reading notes and localizers reused; no mass inventory or historical ZIP nesting.'},
 'duplicate_staging_exports':{'selection':desc(P/'control/SELECCION_ABC_EXPORTACION_R02.json'),'omitted_only_from_ZIP':41,'reason':'Verified exact alternative exports of the sameABC evidence. Canonical gzip copies retain every original byte. None deleted locally.'},
 'document_QA':{'root':str(R.parents[1]/'PI02_WORD_QA_20261108'),'pdfs':[desc(P/'documentos/manual_1_29_PI02_32e5c92f.pdf'),desc(P/'documentos/compendio_PI02_FINAL_422d63cf.pdf')],'why':'Full source DOCX and publication/render/QA witnesses travel; bulk page PNGs/PDF copies remain local.','coverage':'120page Master overview plus affected fullsize pages;55page Compendium overview and affected pages; original protected body verified structurally. Not a new total historical scientific reading.'},
 'excluded_domains':['Business/commercialization','Email/accounts/credentials','Videos','Mac portability','Unrelated personal data'],'ZIP_scope':'Compact scientific analysis and documentary recalculation, not an executable/full-life backup.'}
write(E/'CONTROL/OMISIONES_LOCALIZADAS.json',omissions)
reg=read(R/'archivo/analisis_transversal_cognitivo/REVISION_TRANSVERSAL.json')
write(E/'CONTROL/EXTRACTO_REGISTRO_TRANSVERSAL_PI02.json',{'source':desc(R/'archivo/analisis_transversal_cognitivo/REVISION_TRANSVERSAL.json'),'scope':'Exported excerpt of the existing register, not another governing register','keys':{k:reg[k]for k in('resume','current_operation','current_operation_details','manual_update','manual_update_PI02_stage_A','progression_integrated_PI02')if k in reg}})
coverage='''# Cobertura y verificación

El Manual completo de Cognitive 1.29 y el Compendio se copiaron literalmente después de su publicación. El render Word16 usó copias de sólo lectura con macros/enlaces externos deshabilitados. Se revisaron vistas de120/55páginas y a tamaño completo las páginas afectadas declaradas en los dos testimonios QA. El cuerpo histórico protegido conserva sus bytes XML; no se afirma una nueva lectura científica completa de cada página histórica.

Fuentes: se reutiliza la lectura técnica completa de PI01;17fuentes dirigidas y13afirmaciones PI02 tienen localizadores y alcances. Metadatos, lecturas, cálculo documental y ejecución Native se distinguen. No se volvió a inventariar el corpus completo ni se repitieron las34familias.

Hubo93340ticks Native entre ramas; no son la edad del principal ni muestras independientes. El panel material12/12 y929/929cierraT751546. Después se comprobó la nueva función2/2hastaT753346; no se atribuye otro panel completo al último corte. La migración, reapertura técnica y promoción añadieron0ticks. Los originales de motor y estados protegidos se cotejan selectivamente en el testimonio final externo, sin prometer inmutabilidad de todo el proyecto autorizado a cambiar.

El recálculo portable tiene14verificaciones desde evidencia exportada ystdlib, sin Native: A,B,C,siete brazosD,OH,dos comparaciones de aviso,E_FINAL. F corresponde a incorporación estática y está cubierto por el manifiesto, no es una nueva reproducción. El sellado final verificará CRC de todos los miembros, hashes, textos/JSON/CSV/DOCX y Manual exacto desde extracción limpia, y ejecutará ese mismo recálculo. Su resultado, tamaño y SHA del contenedor se registran FUERA del ZIP en control/VERIFICACION_FINAL_EXTERNA_PI02.json para evitar autorreferencia. No se inventa aquí un hash futuro del contenedor.

No se borró ni limpió nada en PI02. La limpieza de la auditoría anterior pertenece a PI01 y no se repitió. Sólo la extracción de verificación y las imágenes QA derivadas son temporales regenerables después de revisar la entrega. P2/estados, ensayos, código ejecutado, pares completos y documentos con sus pruebas NO se consideran temporales prescindibles.

No hay subida a servicios externos. Datos históricos, estados grandes, motor, manuales Thinking y telemetría profunda permanecen en los localizadores de OMISIONES_LOCALIZADAS.json. Los41miembros excluidos únicamente del ZIP son duplicados comprobados; no se omitieron fracasos para mejorar la conclusión.
'''
(E/'CONTROL/COBERTURA_OMISIONES_Y_VERIFICACION.md').write_text(coverage,encoding='utf-8')
print(json.dumps({'control':str(E/'CONTROL'),'complete_Master':'1.29','new_Native_ticks':0,'originals_deleted':0},ensure_ascii=False))
