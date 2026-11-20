"""Prepare the reviewed update of DCS11-MM-001. N0; never imports DEE.

Only a closed, root-approved result record supplies the final life/cut and
observed counts. This file does not run the authoring operation by itself.
"""
from pathlib import Path
from zipfile import ZipFile
import argparse,hashlib,json
from lxml import etree as E

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).parent
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
BASE=ROOT/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_16_APD02_CONTINUIDAD_CALIDAD_SIN_VALIDACION_VISUAL.docx'
BASE_SHA='8ef2f084621693b4a0d3d97fa6b7586ce402b7f0b6b7823680732945be39b855'
def text(p):return ''.join(t.text or ''for t in p.iter(W+'t'))
def p(value,style='Normal'):return {'style':style,'text':value}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--closed',type=Path,required=True);args=ap.parse_args()
    final=json.loads(args.closed.read_bytes())
    assert final['status']=='ROOT_APPROVED_CLOSED_APD03'
    assert final['life']=='APD03_MAIN' and final['parent_tick']==548407
    assert final['evolving_seconds']>=3600 and final['pending_same_id_resumed_once'] is True
    assert final['catalog_is_not_faculty_count'] is True
    tick=int(final['tick']);elapsed=final['evolving_seconds']
    assert len(final['snapshot_sha256'])==64 and len(final['paired_manifest_sha256'])==64
    assert hashlib.sha256(BASE.read_bytes()).hexdigest()==BASE_SHA
    with ZipFile(BASE)as z:body=E.fromstring(z.read('word/document.xml')).find(W+'body')
    ps=body.findall(W+'p');assert len(ps)==813
    new={
      8:'DEE thinking 4.5.0  |  DEE Cognitive System 1.1.0\nEdición documental 1.17  |  DCS11-MM-001',
      9:f'Edición documental 1.17\nCorte APD03: 26/10/2026 UTC\nOpción operativa APD03_MAIN T{tick}\nPadre protegido APD02_MAIN T548407\nActivo protegido MA_MAIN_R9 T230379\nReferencia histórica E1_SOCIAL_11 T3154',
      15:'Este mismo Manual Maestro conserva sus capítulos científicos 20 a 33 sin reescribir el pasado. La edición 1.17 actualiza el uso operativo y añade el capítulo 34 sobre entrada única, selección condicionada por consecuencias, información incompleta, señales nuevas y límites del desarrollo. Los estados completos y sus contratos prevalecen. Incorporar código no transmite aprendizajes entre individuos.',
      70:f'APD03_MAIN continúa el par completo de APD02_MAIN T548407, sin preparación T0 ni fusión de auxiliares. Su corte real es T{tick}. La entrada única puede crear una copia emparejada, recibir objetivos y docencia explícita, guardar y reabrir la misma vida. MA_MAIN_R9 sigue protegido. El operador ofrece oportunidades; la selección nativa en ellas no acredita iniciativa general ni un planificador libre.',
      117:'La opción APD03 conserva una sola genealogía durante el bloque integrado. Las bifurcaciones de sensor, retorno omitido y curvas léxicas son otros individuos experimentales y no aportan sus recuerdos a MAIN. Catorce formas anteriores, dos señales nuevas y seis consultas contextuales usan mecanismos y soportes compartidos; no representan veintidós facultades ni nuevos significados NSM65. El panel y el momento realmente comprobados figuran en el capítulo 34.',
      122:'El activo real MA_MAIN_R9 T230379 no se reemplazó. APD03_MAIN es una continuación seleccionable de APD02_MAIN, ASISTENTE_MAIN y la genealogía MA02/MU. Sus estados se eligen por procedencia y alcance comprobado, no por mayor tick. Los futuros adversos, controles y ramas históricas permanecen identificados y no se fusionan.',
      145:'El inicio ordinario del sistema conserva el activo protegido. La operación usar de cognitive sistem abre una copia personal del par APD03 seleccionado mediante --nueva y continúa esa identidad mediante --vida. No crea otro universo si falla la restauración. Una pausa no equivale a evolución entre peticiones; reanudar y detener son operaciones explícitas.',
      259:'El software sigue siendo Cognitive 1.1.0 sobre thinking 4.5.0 y Universe v27 congelados. La edición documental 1.17 incorpora APD03 y corrige el control documental desfasado de la edición recibida. La capa de sistema añade entrada única y adaptadores de percepción y acceso; no cambia el kernel ni convierte esos aparatos preparados en contenido aprendido.',
      264:'Las ediciones 1.5 a 1.15 conservan sus campañas históricas. La edición 1.16 incorporó APD02; la 1.17 incorpora APD03 en este mismo Manual Maestro y conserva íntegros los capítulos 20 a 33. La historia del producto no equivale al repertorio actual de cada individuo.',
      269:'DCS11-MM-001 mantiene una sola autoridad documental vigente y conserva la edición 1.16 en el archivo histórico. El catálogo registra mecanismos, vidas y asistencia; no mide inteligencia por número de entradas. Los hashes de los ZIP exactos y sus pruebas se guardan fuera de esos contenedores. El Word actualizado y su comprobación estructural se distinguen de su validación visual.'
    }
    replacements={text(ps[i]):value for i,value in new.items()}
    control=body.findall(W+'tbl')[0]
    cells={text(row.findall(W+'tc')[0]):row.findall(W+'tc')[1] for row in control.findall(W+'tr')[1:]}
    control_values={
      'Documento':'DCS11-MM-001 / Edición documental 1.17',
      'Corte de liberación registrado':f'26/10/2026 UTC; APD03_MAIN T{tick} continúa el par APD02_MAIN T548407. El capítulo 34 distingue selección física, contenido adquirido, preparación y asistencia. ACTIVO.json conserva MA_MAIN_R9 T230379 sin promoción global. La continuidad requiere snapshot y protocolo emparejado, no sólo arrays físicos.',
      'Base principal':'Edición 1.16 conservada por hash en documentos/historico_manuales. Se modifica este mismo Manual Maestro lógico y se preservan los capítulos científicos 20 a 33.',
      'Estado de esta edición':'Word 1.17 actualizado en el mismo documento lógico. El comprobante editorial registra preservación de estructura, campos y geometría y el intento real de render. XML válido no acredita páginas revisadas; si el render no genera imágenes, la validación visual queda expresamente pendiente.'
    }
    for key,value in control_values.items():
        paras=cells[key].findall(W+'p');assert len(paras)==1
        replacements[text(paras[0])]=value
    additions={
      '4. Configuración efectiva de carpetas y dependencias':[p('APD03 utiliza el entorno instalado y el motor oficial sin recompilarlo. El punto de entrada único es sistema/app/usar_dee.py; en la distribución se alcanza con INICIAR.bat usar. Los registros científicos no participan en las respuestas. El paquete completo incluye el par aprendido seleccionado y sus dependencias declaradas.')],
      '9. Operaciones del gestor y efectos sobre la vida':[p('La entrada APD03 conserva IDs materiales, resultados inciertos y el entorno pendiente. No se repite una solicitud incierta con un ID nuevo. estado es una observación externa cacheada; panel, lenguaje y paso son interacciones materiales que pueden modificar el paisaje. Véase el capítulo 34 y la guía de uso vigente.')],
      '13. Lo heredado, lo mejorado y lo todavía separado':[p('APD03 añade un enlace perceptivo reutilizable y prueba selección ACT/QUERY con información completa e incompleta. La anatomía sensorial es preparada; el estado relativo que influye en la selección cambia por experiencias. Las curvas auxiliares no demuestran por sí solas aprender a aprender: se distingue historia útil de dosis admitida y accesibilidad temporal.')],
      '14. Qué muestran las verificaciones y qué no':[p('Los recálculos APD03 reconstruyen señales y archivos desde primarios sin ejecutar el motor. Las pruebas nativas y del ZIP exacto son comprobaciones diferentes. CPU, RAM e I/O se informan con su cobertura; energía NO MEDIDA. La prueba en otra carpeta no representa una segunda computadora ni a una persona externa.')],
      '16. Pendientes reales y mecanismos de deterioro':[p('APD03 conserva los intentos de sensor no reutilizable, la ocupación de una ruta propuesta y las consultas rechazadas en controles de enseñanza. No se transforma ese fallo local en límite universal. Un código no leído puede depender de admisión, fase, trayectoria o contenido; su simple ausencia en el lector no demuestra borrado global.')],
      '17. Lenguaje español: objetivo y estado del programa':[p('Las seis formas numéricas españolas de APD02 nombran dos operaciones preparadas; compara y recuerda asocian señales a dos funciones preparadas. luma y nara son señales arbitrarias adicionales, no palabras españolas nuevas ni primitivas NSM. Sus correspondencias y retención se atribuyen a la vida que las experimentó. El contexto consultado todavía lo declara el operador.')],
      '18. Memoria de proyecto y relevo entre conversaciones':[p(f'La opción seleccionada APD03_MAIN queda en T{tick}, con snapshot SHA256 {final["snapshot_sha256"]}. Su manifiesto emparejado tiene SHA256 {final["paired_manifest_sha256"]}. La ficha de continuidad y el contrato de entrada señalan archivos completos y operaciones pendientes. El ZIP pequeño de análisis no sustituye ese estado operativo.')]
    }
    chapter=[
      p('34 1 Organización y atribución','Heading2'),
      p(f'APD03_MAIN parte de APD02_MAIN N67 T548407 mediante importación de mundo, SQLite, interfaces, colas, recibos, outbox y artefactos del mismo corte. La ventana congelada evolucionó {elapsed:.3f} segundos reales y continuó en otro proceso; el corte actual es T{tick}. El activo global no cambió.'),
      p('El sensor transmite un indicador actual de disponibilidad de datos, no el operando oculto ni la mejor acción. La emisión nativa selecciona ACT o QUERY; después, el ejecutor restringido consulta el dato o compromete una operación y un archivo. Sólo entonces el entorno devuelve la consecuencia permitida. El operador fija objetivos, presupuesto de oportunidades, suministros y docencia. No hubo un LLM decisor ni lectura de diarios para resolver.'),
      p('34 2 Percepción y selección con consecuencias','Heading2'),
      p('El sensor preparado reutilizó sus interfaces en las secuencias 0 1 0 y 1 0 1. El primer diseño dejó material y no fue reutilizable; se conserva como negativo. En el contraste auxiliar R03, después de una experiencia común, la historia con consecuencia real eligió ACT y produjo el archivo 13 ante la primera reserva común; la historia con retorno omitido eligió una consulta redundante. Las acciones no fueron seleccionadas por Python.'),
      p('En ese auxiliar, las cinco oportunidades posteriores de la historia real aportaron tres archivos correctos y dos hechos nuevos; el control omitido aportó dos hechos y ningún archivo. No son cinco tareas terminadas ni aprendices independientes. La disponibilidad sensorial y el código de acciones son preparación; el resultado respalda una selección local modificada por consecuencias, no curiosidad general ni regulación contextual abierta.'),
      p('34 3 Funciones que coexistieron en MAIN','Heading2'),
      p(final['main_functions_text']),
      p(final['retention_text']),
      p('El objetivo incompleto exige combinar la obtención de un hecho con el cálculo y el compromiso de un resultado. El presupuesto ofrecido no dicta la lista ACT/QUERY; la selección ocurre en DEE. La operación aritmética y su ejecución restringida sí están preparadas. La prueba componer con una lista escrita por el operador se conserva como composición asistida, no programa inventado por el ente.'),
      p('El número revelado por QUERY queda disponible en el entorno público del objetivo y vuelve a entrar como observación actual al cálculo. Su conservación por el wrapper no es memoria cognitiva nativa de ese número. Las asociaciones léxicas y memorias MA tienen soportes físicos y pruebas separados; no se suman a la memoria ambiental del protocolo.'),
      p('34 4 Desarrollo y límites','Heading2'),
      p(final['lexical_history_text']),
      p('Dos casillas genéricas disponibles antes de las reservas permiten nuevas asociaciones dentro de un repertorio finito; no acreditan crecimiento anatómico ilimitado. Los contextos de memoria siguen nombrados por el operador. No se probó producción lingüística libre, herramienta inventada, planificación general ni nuevos niveles de dominio NSM65.'),
      p('34 5 Calidad y referencias convencionales','Heading2'),
      p(final['quality_text']),
      p(final['comparators_text']),
      p(final['resource_text']),
      p('34 6 Entrada única y continuidad','Heading2'),
      p('En cognitive sistem, abra una copia nueva sólo una vez. Los comandos de esta interfaz son de Cognitive 1.1, no funciones públicas nuevas del motor congelado. La nueva copia conserva su propio pasado y no modifica el origen. Reabrir utiliza --vida y no vuelve a importar el padre.'),
      p('INICIAR.bat usar --nueva MI_APD03\nreanudar\nestado\nobjetivo suma 18 7 --oculto\npaso 4\nguardar\ndetener','Code'),
      p('INICIAR.bat usar --vida MI_APD03\nreanudar\npanel --nuevas --memorias\nensenar-nueva luma -1 --revision\nlenguaje-nuevo luma 23 gamma\nguardar\ndetener','Code'),
      p('La enseñanza opuesta es explícita y modifica esa copia; no es retención del signo anterior. Las consultas materiales pueden enseñar o consumir recursos. Un timeout exige consultar el mismo ID, no sustituir la vida, repetir trabajo ni escoger otro futuro. El corte emparejado conserva también un objetivo parcialmente consultado cuando exista.'),
      p('34 7 Demostrabilidad y pendientes','Heading2'),
      p('La evidencia permite mostrar de forma acotada una tarea con información incompleta, la emisión que decide consultar o actuar, el archivo real y la conservación de señales durante uso posterior. También deben mostrarse la consulta redundante, el error de calidad y la asistencia preparada. El guion propuesto dura entre tres y cinco minutos; no se produjo un video ni se publicó material privado.'),
      p('El comprobante de la distribución exacta especifica qué arranque, docencia opuesta, retención y continuación se probaron después del sellado. No se anticipan esos resultados en esta edición. Los límites de render del Word se registran por separado; no se afirma revisión visual cuando no hubo páginas.'),
      p('Fuentes operativas: sistema/contratos/APD03_AUTONOMIA_DESARROLLO.json; sistema/contratos/ENTRADA_SENCILLA_APD03.json; sistema/documentacion/GUIA_USO_APD03.md; CONTINUIDAD_APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION.json. Primarios y recálculos seleccionados: evidencia/campanas/APD03_AUTONOMIA_DESARROLLO_DEMOSTRACION y el paquete pequeño de análisis.','Source')
    ]
    result={'status':'FINAL_RESULTS_APPROVED_FOR_MANUAL','schema':'APD03.root_approved_same_manual.v1','inline_replacements':replacements,'method_additions':additions,'chapter':chapter,'closed_result':str(args.closed.resolve()),'closed_result_sha256':hashlib.sha256(args.closed.read_bytes()).hexdigest(),'native_ticks':0}
    target=HERE/'CONTENIDO_APROBADO_MANUAL_APD03.json'
    with target.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'content':str(target),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'new_native_ticks':0}))

if __name__=='__main__':main()
