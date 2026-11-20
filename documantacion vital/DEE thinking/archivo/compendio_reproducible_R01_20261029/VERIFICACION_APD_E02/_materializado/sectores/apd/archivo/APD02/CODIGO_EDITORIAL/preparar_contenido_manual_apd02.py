"""Root-approved content for the same manual, from closed APD02 evidence."""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json
from lxml import etree as E
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).parent
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
BASE=ROOT/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_15_ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_SIN_VALIDACION_VISUAL.docx'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()=='2cc8c39640a5926963459ec648f6c3bc446be9b10e5edb6402fd2d74bf429a70'
with ZipFile(BASE)as z:body=E.fromstring(z.read('word/document.xml')).find(W+'body')
paras=body.findall(W+'p')
assert len(paras)==738
def text(p):return ''.join(t.text or ''for t in p.iter(W+'t'))
new={
8:'DEE thinking 4.5.0  |  DEE Cognitive System 1.1.0\nEdición documental 1.16  |  DCS11-MM-001',
9:'Edición documental 1.16\nCorte APD02: 26/10/2026 UTC\nOpción de investigación APD02_MAIN T548407\nPadre protegido ASISTENTE_MAIN T361114\nActivo protegido MA_MAIN_R9 T230379\nReferencia histórica E1_SOCIAL_11 T3154',
15:'Este Manual Maestro conserva la genealogía de CPC y campañas posteriores. Los capítulos20–32 mantienen sus resultados y cortes históricos sin reescribirlos. La edición1.16 actualiza los apartados operativos afectados y añade el capítulo33: continuidad, calidad real, asociaciones funcionales, renovación de acumulación, selección por consecuencias y objetivos consultables. Estados completos, contratos y primarios prevalecen; incorporar código no transfiere conocimientos entre vidas.',
69:'La opción de investigación APD02_MAIN continúa el corte completo emparejado ASISTENTE_MAIN T361114, sin T0 ni fusión de auxiliares. Alcanzó T548407 después de una hora propia de uso y de contrastes de calidad a precios iguales. Conserva sus negativos y sus últimos accesos comprobados; consulte el capítulo33 y la continuidad vigente. MA_MAIN_R9 T230379 sigue protegido. No se elige otra vida por la respuesta esperada.',
116:'APD02_MAIN mantiene una identidad durante sus experiencias, herramientas y servicio. Las bifurcaciones de lenguaje, historia, selector y control OMIT son otras trayectorias: no aportan sus aprendizajes a MAIN. Las seis memorias contextuales MA se distinguen de las catorce formas del lector común; formas y sinónimos no son facultades independientes. El panel final conserva cinco memorias anteriores y una beta revisada explícitamente a+.',
121:'En la entrega original ACTIVO.json identificaba E1_SOCIAL_11 T3154. El activo real MA_MAIN_R9 T230379 permanece protegido y no se reemplazó globalmente. APD02_MAIN es una opción operativa de investigación descendiente de ASISTENTE_MAIN, MU_MAIN_FASE_R3 y la genealogía MA02/MU. Sus cortes se identifican por procedencia y función comprobadas, no por mayor tick ni por reunir recuerdos de auxiliares.',
144:'El inicio normal del sistema conserva el activo real MA_MAIN_R9, perfil fisica_directa. La entrada de investigación de cognitive sistem ofrece una copia personal identificada y emparejada del resultado APD02 seleccionado, sin dueño automático ni sustitución de una vida personal. Un corte nuevo requiere otra identidad explícita. La continuación de una vida avanzada usa su estado actual, no el tick impreso en un capítulo histórico.',
254:'El software permanece en Cognitive1.1.0 sobre thinking4.5.0 y Universev27 congelados. La edición documental es1.16. APD02 añade renovación de acceso, asociaciones funcionales, verificación externa posterior, selección local modificada por consecuencias y objetivos consultables reanudables, con la preparación y límites del capítulo33. Esta edición no cambia la física ni crea o fusiona conocimientos.',
259:'Las ediciones1.5–1.9 incorporaron Integración Situada, Ciclo02, MI01, MI02 y CF01;1.10 conservó ENTE01 y1.11 ENTE02.1.12 integró desarrollo acumulativo;1.13 concretó contexto, consulta actual y composición con coste.1.14 añadió Mente Unificada/FI01, y1.15 conservó APD01 en el mismo Manual.1.16 incorpora APD02 y mantiene intactos los capítulos científicos20–32. La memoria de versiones no equivale al repertorio actual de una vida.',
264:'La edición1.16 mantiene DCS11-MM-001 y modifica el mismo Manual Maestro. Los capítulos20–32 y las entregas anteriores conservan valor histórico. El inventario original de73entradas no es el catálogo total actual ni una cuenta de capacidades de MAIN. Los hashes de los paquetes exactos y sus verificaciones van en el comprobante externo; no se incorpora el hash del propio contenedor dentro del Word.'
}
draft_path=HERE/'BORRADOR_CAPITULO33_APD02.json'
draft=json.loads(draft_path.read_bytes());chapter=draft['chapter']['paragraphs']
assert not any(any(marker in x.get('text','')for marker in('PENDIENTE_RESULTADOS','PENDIENTE_INCORPORAR','{{'))for x in chapter)
assert 'T548407'in chapter[1]['text']
rows=[['Vida y momento','Función comprobada','Asistencia y límite']]
for life,function,assistance,limit in draft['chapter']['table']['rows']:
    rows.append([life,function,assistance+'. '+limit])
chapter=chapter+[{'type':'table','rows':rows},
 {'style':'Heading2','text':'33 14 Uso personal y continuidad'},
 {'style':'Normal','text':'En cognitive sistem, investigacion importa explícitamente el alias ASISTENTE_CALIDAD completo. La nueva copia no modifica APD02_MAIN ni el activo global. Inicie un solo propietario en una terminal y envíe solicitudes con IDs nuevos desde otra. Para continuar, vuelva a iniciar esa misma identidad, no importe de nuevo el padre.'},
 {'style':'Code','text':'INICIAR.bat investigacion COLAB_APD02_01\nINICIAR.bat asistente2 COLAB_APD02_01 iniciar --pausado\nINICIAR.bat asistente2 COLAB_APD02_01 reanudar --id MI_RESUME_01\nINICIAR.bat asistente2 COLAB_APD02_01 usar --texto suma --operandos 18 7 --id MI_TAREA_01'},
 {'style':'Normal','text':'La docencia de una forma es explícita: ensenar --texto compara --senal -1 --revision. lenguaje direcciona un contexto declarado; acumular usa recursos genéricos preparados; componer recibe el orden del operador. meta-iniciar guarda hechos del objetivo, y meta-paso ofrece oportunidades genéricas: la emisión nativa decide ACT o QUERY, sin un planificador externo que elija la siguiente acción.'},
 {'style':'Code','text':'INICIAR.bat asistente2 COLAB_APD02_01 guardar --id MI_SAVE_01\nINICIAR.bat asistente2 COLAB_APD02_01 exportar --id MI_EXPORT_01 --esperar 180\nINICIAR.bat asistente2 COLAB_APD02_01 detener --id MI_STOP_01'},
 {'style':'Normal','text':'Un timeout o efecto incierto no autoriza repetir el trabajo. Consulte resultado con el ID original y preserve el par completo. La exportación necesita snapshot, diario, outbox, archivos y progreso; una receta o snapshot aislado no equivale a esta vida aprendida. El ZIP de análisis no sustituye ese respaldo. La extracción en otra carpeta prueba portabilidad local, no otra computadora ni certificación24/7.'},
 {'style':'Source','text':'Fuentes actuales: sistema/contratos/APD02_CONTINUIDAD_CALIDAD.json; sistema/documentacion/GUIA_ASISTENTE_APD02.md; CONTINUIDAD_APD02_CONTINUIDAD_CALIDAD_ADAPTACION.json; fichas y comprobantes externos de los paquetes exactos.'}]
additions={
'13. Lo heredado, lo mejorado y lo todavía separado':[{'style':'Normal','text':'APD02 conserva la misma continuación y añade usos que coexisten: formas numéricas heredadas, dos señales funcionales nuevas, acumulación renovada y selección nativa/externa por consecuencias. El panel final tiene cinco memorias antiguas y beta revisada+, no seis memorias antiguas intactas. El control OMIT es otra vida; no transmite su pasado a MAIN. Véase capítulo33.'}],
'14. Qué muestran las verificaciones y qué no':[{'style':'Normal','text':'APD02 distingue recálculo archivado, ejecución física nativa y prueba del ZIP exacto desde una extracción independiente. Ninguno implica por sí solo otro equipo, estabilidad ilimitada o eficiencia energética. La estructura Word y el intento de render se registran separadamente: un archivo actualizado no equivale a páginas visualmente validadas.'}],
'17. Lenguaje español: objetivo y estado del programa':[{'style':'Normal','text':'compara y recuerda se asociaron por enseñanza física a funciones preparadas y se utilizaron con datos nuevos; la correspondencia opuesta invirtió su uso. No se midió producción libre, sintaxis general ni nuevos niveles NSM65. El contexto de consulta y la iniciativa de solicitarlo siguen siendo asistencia explícita.'}],
'18. Memoria de proyecto y relevo entre conversaciones':[{'style':'Normal','text':'La continuidad APD02 actual parte de ASISTENTE_MAIN T361114 y llega aT548407 con su propio par postSTOP. Consulte su ficha y el contrato antes de continuar. La hora intermedia T524491 y el futuro adverso R03 son antecedentes conservados; no reemplazan silenciosamente al corte actual.'}]
}
result={'status':'FINAL_RESULTS_APPROVED_FOR_MANUAL','schema':'APD02.root_approved_same_manual.v1',
 'inline_replacements':{text(paras[i]):v for i,v in new.items()},'method_additions':additions,'chapter':chapter,
 'scientific_sources':{'draft_sha256':hashlib.sha256(draft_path.read_bytes()).hexdigest(),'final_snapshot_sha256':'64359d48edd49f8a1f5616ceacd04c4479a27383877c23381e217a39f0cc05a9','quality_stage_manifest':'253a2b05c423431e7bbf8985631066d86c80657f3cb6373c9dcd991990649da5'},
 'attribution':'Root approves only closed science; Word/render and exact Full evidence have separate reports, not anticipated as completed.'}
target=HERE/'CONTENIDO_APROBADO_MANUAL_APD02.json'
with target.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'content':str(target),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'new_native_ticks':0}))

