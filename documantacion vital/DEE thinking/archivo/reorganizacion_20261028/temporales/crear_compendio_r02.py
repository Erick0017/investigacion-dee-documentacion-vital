"""Autoría editorial del compendio; no importa DEE ni ejecuta experimentos.

Uso por el responsable del documento, después de marcar su operación de autoría:
    python crear_compendio.py
Sólo lee las tres extracciones editoriales, metadatos vigentes y el registro único.
El único producto que escribe es archivo/_edicion/compendio.docx.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ARCHIVO_11 = ROOT / 'archivo' / 'DEE Cognitive System 1.1'
OUT = ROOT / 'archivo' / '_edicion' / 'compendio.docx'
AUTHOR = 'Ivan Erick Tlaltecatl Morales'
TITLE = 'Compendio científico acumulativo de DEE'
SUBTITLE = 'Mecanismos, capacidades, límites y continuidad hasta DEE Cognitive 2.0'


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def resolve_source(source, group):
    if group == 'recientes':
        return 'archivo/DEE Cognitive System 1.1/' + source['ruta']
    raw = source.get('ruta_original', source.get('ruta', ''))
    raw = raw.replace('\\', '/')
    if raw.startswith('DEE Cognitive System 1.1/'):
        return 'archivo/' + raw
    return raw


def source_set(modules, app):
    result = []
    for group, module in modules.items():
        for original in module.FUENTES:
            item = dict(original)
            item['ruta_actual'] = resolve_source(original, group)
            item['grupo'] = group
            if item['id'] == 'R08' and item.get('recalculo_leido'):
                item['recalculo_leido'] = dict(item['recalculo_leido'])
                item['recalculo_leido']['sha256'] = '0a6c4749582edda4fd1321defd2b87c4b066ca602d59c5e7adc2673bdc1f19b4'
            result.append(item)
    vital = ROOT.parent
    result += [
        dict(id='F-LB45', ruta_actual='4.5/DEE_thinking_4_5_0_Libro_Blanco_y_Manual_Tecnico.docx',
             sha256='02f7de4cdbc5dd1a4763e0ff2dc9c59e02d1988a507a091e6335d7eafaec33e4',
             localizador='Capítulos 3, 8, 31, 35–38 y 44. Lectura dirigida e identidad comprobadas por el responsable del compendio.',
             alcance='Instrumentación, consultas y observación; lectores y recibos no equivalen a significado, y journal no accesible como respuestas. Contrato FUNCTIONAL_CANDIDATE_VALIDATED limitado, no certificación universal.'),
        dict(id='F-MA45', ruta_actual='4.5/DEE_thinking_4_5_0_Maestro_Arquitectura_Reconstruccion.docx',
             sha256='8092eedf55c495a9729c4e9ce795fc7bb9135bcbfe60941ab050634b135194ec',
             localizador='Capítulos 41 y 48–51. Lectura dirigida e identidad comprobadas por el responsable del compendio.',
             alcance='Persistencia RAW/clocks, interfaces, colas, recibos, metadatos, tick y cursor; perfiles experimentales remote/absence/regulation separados de U0. Reutilizar una aplicación no equivale a reconstruir su vida desde T0.'),
        dict(id='F-PN', ruta_actual=str(vital / 'FISICA DEE Y PROCESAMIENTO NATIVO' / 'Procesamiento_Nativo_DEE_Libro_Manual_v1.docx'),
             sha256='d619b530658d2d352a24051508f3d49df555846afc475e3532e47a368a458ddb',
             localizador='Capítulos 16 y 18–21; Ingeniería 05, Ingeniería 06 y realizaciones de propagación. Lectura dirigida comunicada por el responsable del compendio.',
             alcance='Historia factorial, reutilización y acceso; antecedentes físicos, no recuerdos de DEE20_DEMO_01.'),
        dict(id='F-FIS', ruta_actual=str(vital / 'FISICA DEE Y PROCESAMIENTO NATIVO' / 'DEE_V4_0_1.docx'),
             sha256='d7033962e95e300abf3e583bac37319df1141aae4dc309ca3eac629dab5213a8',
             localizador='Sección 4.3 y sección 6; determinismo, no inyectividad y condiciones locales. Lectura dirigida comunicada por el responsable.',
             alcance='Distinguir trayectoria determinista de reversibilidad y confluencia local de una ley general de composición.'),
        dict(id='F-OBP', ruta_actual=str(vital / 'mente basal' / 'ORGANIZACION_BASAL_PERSISTENTE_DOCUMENTO_MAESTRO_V2_1.docx'),
             sha256='c9cd0f515e35982ea9fb726ccddfd0a61464a04fa6c2a630a0039c170f1f978f',
             localizador='Cierre, capítulos 27–36. Lectura dirigida comunicada por el responsable del compendio.',
             alcance='Memoria relacional, plasticidad condicionada y corrección de la necesidad atribuida al producto remoto; dominio histórico 2.2/v27.'),
    ]
    for identifier, filename, scope in [
        ('ACT-PROYECTO', 'PROYECTO.json', 'Identidad del producto, vida seleccionada, motor, lanzador y manual vigente.'),
        ('ACT-CONT', 'CONTINUIDAD_DEE_COGNITIVE_2_0.json', 'Corte físico, importación emparejada, testigos positivos y negativos, estado operativo y localizadores de primarios.'),
    ]:
        path = app / filename
        result.append(dict(id=identifier, ruta_actual='DEE Cognitive 2.0/' + filename,
                           sha256=digest(path), localizador='Documento completo; campos citados en la apertura y familia 12.', alcance=scope))
    return result


# Las familias reúnen mecanismos relacionados: no son un recuento de filas,
# nombres de comandos, señales o individuos distintos como capacidades nuevas.
FAMILIAS = [
    dict(id='familia_01', title='1. Procesamiento dependiente de historia y paisaje físico',
         opening='Una experiencia puede cambiar físicamente cómo una organización procesa una entrada posterior. Éste es el resultado acumulativo más básico: con un protocolo posterior común, historias distintas pueden producir respuestas distintas. Los expedientes documentan tanto soportes relativamente persistentes como contribuciones móviles y relaciones distribuidas. La forma dibujada de un cuerpo y sus puertos nominales no delimitan por sí solos toda la materia que interviene.',
         mechanism='El diseño factorial de Ingeniería 05 separa cuatro condiciones: sin historia ni entrada nueva, con historia sola, con entrada sola y con ambas. Antes de la nueva entrada, los pares correspondientes deben coincidir. Después se contrasta el efecto de esa entrada con y sin historia. Esto evita llamar aprendizaje a cualquier diferencia inicial. En la dinámica v27, los encuentros transforman campos y direcciones; clocks, vecindarios y actividad previa pueden cambiar qué transformación sucede. La inspección externa describe estas condiciones, pero no proporciona al participante un mapa que resuelva su tarea.',
         rows=[
             ['CP01 / CP02', 'Ocho contratos CP01 y seis trayectorias reservadas CP02 recuperados.', 'CP02 paired emite en T37 antes del objetivo T70: horizonte de 33 ticks. El control sin experiencia queda no resuelto.'],
             ['PC01, consulta material', 'Referencia 91 y contribución 7 se encuentran en T9986 y forman 98 con otra dirección.', 'Cuatro magnitudes: acceso original 0/4; omitir, desviar o retrasar la sonda un tick, 4/4 en cada contraste.'],
             ['PC01, contexto transformado', '+XYZ11 y −XYZ120 forman +YZ131.', 'El lector preparado aporta X y permite un uso nuevo; retirar 120 protege el acceso viejo, pero elimina ese uso del lector nuevo.'],
             ['OBP, cierre', 'Relación A−B: +1 / −1 / H0; actualización 131→132 condicionada por contexto y clock.', 'Los cortes no sostienen la necesidad del producto remoto 18 / descarga 65. Se conserva la plasticidad positiva en su dominio.'],
         ],
         controls='Los controles de omisión, historia opuesta, desacoplamiento, desplazamiento, fase, cortes y sham distinguen contexto causal de mera correlación. La observación pasiva se separa de una consulta: una entrada de carga cero sigue siendo material y puede cambiar vecinos o encuentros. El seguimiento toroidal acreditado por la retrospectiva cubre el sufijo T10928–T22318: 11390 pasos y 170 cruces por eje. No cubre toda la proyección inicial ni autoriza asignar linaje único por igual carga.',
         current='La conclusión vigente es que la historia modifica procesamiento en realizaciones concretas. No implica que toda recurrencia sea memoria, que todo residuo sea interferencia ni que cada estructura persistente sea accesible a E1. En thinking 4.5, la consulta predeterminada usa una espera ceil(N): ese calendario es del anfitrión, no una decisión aprendida. Un recibo y un lector direccional acreditan entrada y salida dentro de su contrato, sin definir significado por sí solos. El journal de instrumentación no es una tabla de respuestas accesible al ente. CP01, CP02, OBP y PC01 pertenecen a preparaciones, vidas y versiones de instrumento distintas; no transfieren conocimientos a DEE20_DEMO_01.',
         applications='Aplicación demostrada: comparar historias y localizar entradas o encuentros que cambian una función. Aplicación propuesta: diseñar entornos y accesos que aprovechen contexto útil sin destruir otras funciones. No se deduce de ello una arquitectura cerebral, reversibilidad global o memoria ilimitada.',
         refs=['F-LB45','F-MA45','F-PN','F-FIS','F-OBP','CPC_CORE_RECUPERACION','CPC_CORE_MATRIZ','PC-REPORT','PC-CALC','PC-OMIT','PC-TRANS','RET-CALC']),

    dict(id='familia_02', title='2. Asociaciones, revisión y retención acumulativa',
         opening='Las realizaciones positivas permiten adquirir correspondencias físicas, volver a utilizarlas y revisar alguna mediante nuevas experiencias. La revisión de una asociación no exige declarar que el sistema domina un lenguaje: una señal arbitraria puede tener una función adquirida limitada. El progreso acumulativo debe medirse en la misma vida, junto a las asociaciones anteriores que siguen accesibles.',
         mechanism='En SEM01 una señal inicialmente opaca se empareja con una consecuencia actual accesible. Los encuentros modifican un soporte móvil y la señal sola participa después en una actuación. En repertorios posteriores, varias asociaciones comparten un mundo con accesos preparados. MA02 convierte la consulta en una interacción que desvía una contribución y restaura una columna mediante recursos genéricos. El contenido depende de la experiencia; la geometría y el lector común son preparación. Nuevas experiencias pueden revisar una respuesta sin escribir directamente el target en un registro.',
         rows=[
             ['CPC5, K65', 'Paired y reserva: 65/65 en cada una de tres rondas.', 'Unpaired: 32/65 y después 65/65, 65/65. La evaluación enseñó: las rondas no son réplicas independientes.'],
             ['Revisión L01 / CPC7', 'L01 revisada; otras 64/64 conservadas en ese repertorio. U0: 14/14 consultas tras revisar L03.', 'U0 conserva las otras 13/13 del panel probado; no se sustituye ese panel por el máximo anterior de 16.'],
             ['MA02_MAIN5', 'Cinco asociaciones; panel final 5/5 y 64/64 usos tras demoras declaradas.', '154 consultas: 152 respuestas y dos ausencias después de composición; 1133 IDs nativos, 1131 aplicados y dos rechazos.'],
             ['APD03–APD05 / 2.0', 'Nuevas señales adquiridas y revisiones explícitas de clasifica.', 'En la vida 2.0, luma +1 y clasifica −1 reaparecen después de reabrir, sin reenseñanza en esos dos testigos.'],
         ],
         controls='Asignaciones opuestas, omisión de señal o consecuencia, desacoplamiento y cortes del soporte comprueban dependencia de enseñanza. CORE06 conserva 134 realizaciones —25 transferencias entrenadas, 100 controles, cuatro extinciones y cinco inversiones/reaprendizajes—; CORE07, 144 —48 positivas y 96 negativas—. Su recuperación con transición oficial registra 2208 y 4896 transiciones. Los protocolos históricos de arrays y escrituras instrumentales se declaran; no se inventan colas Runtime retrospectivas.',
         current='La retención no es uniforme. MA01 perdió el acceso a tres contextos antiguos después del cuarto. En MA02, una composición podía conservar gamma/delta y perder alfa/beta; reenseñar devolvió un panel, pero esa parte es readquisición. En APD05 una pausa de 8192 ticks conservó accesos en una rama, mientras tareas posteriores produjeron ausencias. La conservación se atribuye a cada corte y protocolo, no al nombre del repertorio.',
         applications='Aplicación demostrada: bancos finitos de asociaciones revisables, consulta y continuación con dominios de fase y recursos explícitos. Desarrollo propuesto: enseñar repertorios de mayor diversidad con menos daño de consulta. Los algoritmos de suma o diferencia preparados no se cuentan aquí como asociaciones que aprendieron dichos algoritmos.',
         refs=['CPC_CORE_RECUPERACION','CPC_CORE_MATRIZ','R06','R07','R11','R12','R13','ACT-CONT']),

    dict(id='familia_03', title='3. Memoria, acceso alternativo y pérdida causal',
         opening='La evidencia distingue tres resultados positivos diferentes: una diferencia histórica detectable, un contenido utilizable por otro acceso y una recuperación de uso sin volver a enseñar ese contenido. También contiene pérdidas causales legítimas. Un lector silencioso no permite elegir entre esas posibilidades por sí solo.',
         mechanism='AA01 preparó dos soportes que adquirieron contenido mediante experiencia. Tras fallar una ruta, una enseñanza de acceso —sin nuevas entradas .NEW del contenido— modificó un selector y permitió que una consulta común alcanzara el otro soporte. IC01 utilizó productos sociales transformados mediante recursos genéricos paralelos de carga cero para ambos signos, con decodificador fijado antes de las reservas. El signo recuperado procedía de la historia física; la iniciativa, la anatomía y el calendario eran del operador.',
         rows=[
             ['AA46, plus / minus', 'READY T45857, nueve entradas pendientes comunes.', 'Recuperación Z±, recepción y uso nativo en T45928 / T45929 / T45930. Cortar el segundo soporte o su enseñanza de acceso elimina la función.'],
             ['IC01, recuperación 167', '4/4 usos de cada signo; reserva tardía 4/4.', 'Sham, ausencia de intervención y control sin contenido antiguo: 0/4 en los contrastes declarados. Recuperación asistida P0/R0.'],
             ['AA13, auxiliar N17', 'Historias 11 y 17 convergen en T6: cero diferencias RAW y clock, mismos canales, recibos, pendientes y futuro nativo.', 'Los archivos documentales conservan IDs/diario distintos. No son memoria nativa accesible ni contradicen la convergencia del sistema causal delimitado.'],
             ['AA42 / AA46', 'AA42: retirar Z−192 entrante deja cero diferencias RAW/clock posteriores; vaciar destino deja dos diferencias RAW.', 'AA46: nueve diferencias RAW antes del acceso; tras cortar soporte quedan cinco, pero desaparece uso. Diferencia externa no basta.'],
         ],
         controls='Los cortes tardíos del producto, sham, contenidos opuestos, lector sin contenido y omisión de la enseñanza del nuevo acceso descartan una polaridad fija como única explicación. En AA13, retirar el muro o sham conserva la distinción; una experiencia nueva permite aprender otra vez, no recuperar aquel pasado convergente. El principio matemático pertinente es determinismo sin inyectividad: dos estados causales iguales sometidos al mismo futuro no pueden responder de modo distinto por historias que ya no están representadas.',
         current='Se conserva como capacidad limitada la recuperación asistida y el acceso alternativo adquirido en vidas específicas. MAIN AA01 termina en T47146 con bloqueo; las READY no reparan retroactivamente ese futuro. El bloqueo X+5 se sigue sólo en ventanas disponibles: no hay linaje único sin huecos hasta T45028. En MI02, una fase genérica recuperó 5/6 frente a 0/6 sin ella o con sham, manteniendo referencias RAW 174/162; esa iniciación seguía siendo P0 del anfitrión.',
         applications='Aplicación demostrada: diagnosticar pérdida de ruta o soporte, recuperar contenidos contrastados sin dar la respuesta y preservar estados adversos. Se mantiene abierta la recuperación iniciada por el propio ente con alcance general. Un lector externo nuevo se incorpora como instrumento, salvo que una interacción DEE demuestre su uso por la organización.',
         refs=['F-FIS','CPC9_MEMORIAS_PRIMARIO','CPC9_MAPA_AFIRMACIONES','AA-REPORT','AA-CALC','AA-PLUS46','AA-MINUS46','AA-OMIT','RET-REPORT','RET-CALC','IC-REPORT','IC-RECP','IC-RECM','IC-SHAM','R02']),

    dict(id='familia_04', title='4. Referencias cuantitativas y utilización de magnitudes',
         opening='El mecanismo positivo reiterado es adquirir o revisar una referencia material y utilizarla después frente a otra magnitud. Esto es más específico que memorizar una etiqueta y más limitado que aprender la ley general de comparación o cardinalidad. El comparador puede estar preparado mientras sus operandos y sus efectos posteriores dependen de la experiencia.',
         mechanism='Una contribución material modifica una referencia por encuentros v27. Una presentación posterior interactúa con la referencia realmente disponible en ese momento; no con la cifra que el evaluador esperaba que ya hubiera llegado. IC01 extendió el mecanismo: la consecuencia ambiental de acciones afectó una referencia y cambió la respuesta ante un objeto común. Ciclo02 definió además una utilidad ambiental antes de probarla. Las cadenas recientes añaden un acceso escalar transitorio que puede volver a recibir experiencias.',
         rows=[
             ['CPC9', '54→67 por aporte 13; reservas 57, 57, 70, 11.', 'Respuestas −X, +X, −X, +X; igual material fuera de ruta: −X, −X, −X, +X. T941 aún usa 54: 67 no había llegado.'],
             ['IC01', 'Tres pasos: referencia 81 frente a 78 sin retorno.', 'Objeto común 230: intacto +X, anulada/omitida −X en T5765; contraste conservado con demoras 67 y 134.'],
             ['Ciclo02', 'Nueve decisiones: referencia 5,11,11,11,17,17,28,28,39.', 'Retorno: 9/9 útiles, utilidad 4; sin retorno y sham: 2/9, utilidad −5. MAIN: 21/21 útiles, utilidad 10.'],
             ['MU/FI01 y APD02', 'Acceso escalar transitorio y renovación preparada de acumulador.', 'APD02: desde 24 se obtienen 25,29,29,36,38,41,42,42; después 43,45,46,46, sin reiniciar el cursor 5→19.'],
         ],
         controls='Omitir o desviar el aporte, anular la acción antes de su efecto y modificar operandos en copias distingue uso de historia de lectura preparada. En T2283 de CPC9, sustituir referencia 36 por 5 invierte el signo; por 16 deja portador activo de carga 7 sin dirección, y sham mantiene +X. El cero, una dirección ausente, un rechazo y un número obtenido no son sinónimos. La actualización post-tick del hub no identifica por sí sola cada comparando durante todas las decisiones internas del tick.',
         current='Los resultados de cantidad conservan su dominio: dosis, carga, magnitud, dos contactos y cardinalidad abstracta son cuestiones distintas. El acumulador reciente tiene renovación de recursos diseñada P0, experiencias y un horizonte concreto; no suma binaria arbitraria aprendida ni autocuración. En APD04 referencias 21 o 19 originadas desde 20 cambiaron la respuesta al mismo 20; la igualdad 6/6 produjo signos, sin universalizarla como HOLD.',
         applications='Aplicaciones ejecutadas: revisión contextual de una referencia, selección útil en una puerta ambiental y uso de números producidos por artefactos reales como experiencia de una decisión posterior. Desarrollo propuesto: referencias plurales, nuevos objetos y unidades con conservación de accesos anteriores. El ejemplo actual 4+5=9 y 9−2=7 utiliza aritmética nativa preparada; no prueba adquisición del algoritmo aritmético.',
         refs=['CPC9_REFERENCIA_PRIMARIO','CPC9_MEMORIAS_PRIMARIO','IC-REPORT','IC-ACTION','IC-NULL','IC-OMIT','C2-GATE','C2-GATE-OMIT','C2-GATE-SHAM','C2-HIST6','C2-HIST13','R08','R09','R10','R12','ACT-CONT']),

    dict(id='familia_05', title='5. Composición, reutilización y costes sobre otras funciones',
         opening='Hay composición física cuando contribuciones diferenciadas se encuentran y producen un uso dependiente de ambas. La evidencia incluye productos nuevos, reutilización de soportes y cadenas de tareas. El coste también importa: una composición exitosa puede consumir un acceso o cambiar el soporte que permitía responder por separado.',
         mechanism='CPC5 combina etapas adquiridas y respaldos en un producto común. CPC9 conserva una conjunción finita de orden y contacto con consecuencia física. En MA02 se reconstruyeron recorridos periódicos de productos concretos: no se asumió que todo movimiento tuviera periodo N. En MU/FI01 se reutilizó una salida para elegir una herramienta que generó un artefacto; su medida volvió como experiencia de otra decisión. En 2.0, el operador solicita dos operaciones encadenadas y transmite el resultado de una a la siguiente.',
         rows=[
             ['CPC9, T206→T210', '26(1,0,1) y 30(0,1,0) forman 56(1,1,1); uso 63(1,0,1).', 'Cortar llegada 0, llegada 1 o X deja 7(0,−1,0). Retirar Z deja 68(1,0,0), no 7. Sham conserva 63.'],
             ['MA02, retornos de composición', '66 pasos predecesores únicos. 270+461+7→738; con ambos signos 308+461+7→776.', '++ emite +, −− emite −; mixtos no emiten. Corte del producto elimina función; sham la conserva.'],
             ['Reutilización de residuo', 'Contribución 5 y nuevo docente 11 forman Z−16.', 'Cortar el residuo elimina nueva alfa, sham la conserva; gamma/delta permanecen. Es nuevo aprendizaje con docente, no recuerdo antiguo sin enseñanza.'],
             ['MU/FI01 y 2.0', 'Tres cadenas reales gamma/epsilon/zeta→artefactos 13/32/13→segunda decisión; tres commits.', 'En 2.0: 4+5→9 y 9−2→7. Encadenamiento solicitado por operador, no plan aprendido.'],
         ],
         controls='Los cortes de contribuciones y de productos ya formados, sham y variación de orden separan encuentro causal de una lectura correlacionada. La dirección se interviene a igual carga cuando el caso lo permite. La composición MA02 conservó gamma/delta pero eliminó alfa/beta en las seis ramas observadas; una reenseñanza posterior mejoró el panel, sin convertir el periodo perdido en retención intacta. El corte Z de CPC9 conserva un residuo distinto a los otros cortes y corrige la simplificación documental previa.',
         current='La composición demostrada tiene profundidad y recursos explícitos. Dos tramas seriales de ocho componentes no son una decisión simultánea de dieciséis. Una secuencia de consultas de Python que pide cada etapa no acredita iniciativa de planificarla. Los contratos de acceso individual y del compuesto deben convivir o declarar sus incompatibilidades; no basta conservar sólo el resultado compuesto.',
         applications='Uso demostrado: combinar relaciones y utilizar el producto en una consecuencia o segunda operación; reutilizar material transformado para otra adquisición. Desarrollo propuesto: composiciones reservadas más variadas, preservando consultas individuales y nuevas adquisiciones. No se infiere asociatividad general del kernel, gramática abierta ni productividad semántica ilimitada.',
         refs=['F-FIS','CPC9_COMPOSICION_PRIMARIO','CPC_CORE_RECUPERACION','R01','R05','R07','R08','ACT-CONT']),

    dict(id='familia_06', title='6. Comunicación, información privada y protección social',
         opening='La comunicación positiva está sustentada cuando una información adquirida por otro participante llega mediante portadores, cambia materialmente al receptor y afecta un uso posterior. Hay casos de actualización y recuperación social. Eso no convierte a cada región receptora en otra mente completa ni acredita negociación o lenguaje general.',
         mechanism='CPC4–CPC9 usan canales y encuentros del mismo mundo para transmitir contribuciones. IC01 conserva signos procedentes de información privada de B y actuaciones posteriores de E1; nuevos mensajes revisan el estado. Ciclo02 protege rutas vulnerables mediante contraflujos transitorios preparados. MI02 y CF01 utilizan consultas y contexto social en una organización compacta, con beneficios y conflictos medidos. El contenido privado se distingue de los recursos genéricos y del calendario que el anfitrión instala.',
         rows=[
             ['CPC9, retorno E1→B→E1', 'Tres condiciones restore / cut / sham.', 'Cortar mensaje positivo deja signo negativo residual; cortar negativo conserva dirección y cambia carga 44→32. La necesidad no es simétrica.'],
             ['IC01', 'Recuperación social: 4/4 por signo; sin contenido y sham, 0/4.', 'La vida continuable combina usos sociales y referencia adquirida; al final pierde los cuatro lectores sociales antiguos.'],
             ['Ciclo02, protección', 'Ramas 340/343: 9/9 muestras en fase correcta con signos privados opuestos; ocupación final 341/340 en T4435.', 'Sham: 297664 sitios ocupados en T3899; 5/7 muestras válidas previas. 11 solicitudes locales: 10 aplicadas y una rechazada por rama.'],
             ['MI02 / ENTE01', 'R9: nueve de doce oportunidades útiles con consulta social reactivada.', 'En ENTE01 llegaron mensajes, pero contextos 7/5 no se actualizaron de forma persistente; la válvula ambiental alternativa no repara por sí sola el canal nativo.'],
         ],
         controls='Los controles sin B, mensajes desacoplados y cortes posteriores a formar el mensaje excluyen una causa ambiental común como única explicación cuando el dominio permite realizarlos. Una ablación rechazada por ocupación no cuenta como corte efectuado. En la protección Ciclo02, igual RAW/clock sin agenda no era un estado emparejado con 191 eventos pendientes: el contraste válido preservó esa agenda. Guardas que suprimían entrada y función social no se aceptaron como reparación comunicativa.',
         current='La protección P0 conserva comunicación en una ruta y reduce una expansión específica, pero el selector corporal también se agotó bajo protección y sin record. La separación triple conserva contribuciones previas y una nueva en una vida seleccionable, con pérdidas laterales documentadas al cambiar contenido. CF01 mantiene servicios con contexto privado; cortar un mensaje dejó 16/18, porque existía adaptación por otra vía: no es una dependencia social absoluta.',
         applications='Aplicación demostrada: transmisión, actualización y uso finitos de información privada; protección de canal y recuperación asistida. Desarrollo propuesto: coordinación con roles intercambiables y nuevos interlocutores. No se acredita elección autónoma de interlocutor, comprensión de YO/TÚ o negociación por dos trayectos compatibles.',
         refs=['CPC9_RETORNO_PRIMARIO','CPC9_MAPA_AFIRMACIONES','IC-REPORT','IC-CALC','IC-RECP','IC-RECM','IC-SHAM','C2-REPORT','C2-PROTECT','C2-PROTECT-SHAM','C2-PROTECT-OPPOSITE','C2-TRIPLE','C2-TRIPLE-SHAM','C2-ONEPULSE','R02','R03','R04']),

    dict(id='familia_07', title='7. Selección por consecuencias, consulta e iniciativa',
         opening='Existen cambios locales de selección que dependen de consecuencias anteriores. Son resultados positivos aun cuando la organización no posea regulación general. Debe distinguirse una ruta preparada que usa un valor aprendido, un selector cuyo estado se revisa por consecuencias y la iniciativa de decidir cuándo consultar o recuperarse.',
         mechanism='Las oportunidades de ruta o estrategia son anatomía preparada. Una consecuencia material modifica un soporte o selector; la próxima entrada común encuentra otro estado y puede producir otra dirección. AA33 demuestra revisión local Y−→Y+. Ciclo02 demuestra cambio útil ante desgaste. APD02 compara calidad a precios iguales y muestra una selección posterior distinta después de una experiencia de fallo. La ley del entorno, los turnos y los recursos genéricos siguen siendo instrumentación.',
         rows=[
             ['CPC3 / CPC9', 'Core: ocho realizaciones policy, siete need y seis missing.', 'CPC9 conserva consulta condicionada por retorno y pregunta activa de carga cero; no acredita R2 general.'],
             ['AA33', 'Y−, s_reg70, T44718 → Y+, s_reg140, T44785.', 'Sin segunda consecuencia conserva Y−70. Selección modificada por experiencia en ese aparato, no diagnóstico general de fallo.'],
             ['Ciclo02', 'MAIN: 21/21 actuaciones útiles en trayectoria, utilidad 10.', 'Historiales de desgaste 6/13 dan referencias 11/18; objeto común 9 produce actuaciones opuestas pertinentes.'],
             ['APD02, calidad', 'MAIN 4/7 útiles frente a 3/7 OMIT; después de fallo 3/3 frente a 0/2.', 'Una política externa fija siempre-external también obtiene 4/7: P2 local compatible, sin superioridad ni R2 general.'],
         ],
         controls='Historia intacta frente a retorno omitido, desacoplado, acción anulada y sham distingue selección adquirida de edad o mayor suministro. MA02 conserva un selector auxiliar P1: la misma consulta va por X sin historia de contacto y por Y con ella; invertir contenido cambia el resultado, no el banco. Su segunda consulta se rechazó. Los ciclos R05 fallaron en los cinco brazos y la alternativa R06 sólo recuperó una primera función: se conservan esos negativos.',
         current='APD03 completa ocho metas de archivo con catorce oportunidades: ocho ACT y seis QUERY, cuatro hechos nuevos; dos consultas redundantes. La presencia de un sensor preparado que marca ausencia no demuestra que E1 deduzca toda necesidad de información. APD04 muestra WAIT frente a INSPECT por una diferencia histórica local, pero no una política general; APD05 cambia sensor y obtiene conformidad de selección sin convertirla en atención aprendida. Una consulta programada por el anfitrión no es iniciativa nativa.',
         applications='Aplicaciones demostradas: políticas locales, preguntas y elecciones condicionadas que utilizan estados adquiridos; aprendizaje por consecuencias en tareas acotadas. La recuperación asistida continúa siendo útil aunque no surja iniciativa propia. Desarrollo propuesto: selección de acceso ante contenidos y contextos nuevos con consecuencias omitidas, rutas intercambiadas y reservas suficientes.',
         refs=['CPC9_CONSULTA_PRIMARIO','CPC_CORE_RECUPERACION','AA-POLICY','AA-OMIT','AA-CALC','C2-GATE','C2-GATE-OMIT','R01','R07','R09','R10','R11','R12','R13']),

    dict(id='familia_08', title='8. Acción, entorno y puente externo',
         opening='DEE produjo salidas que modificaron entornos externos reales dentro de simuladores o trabajadores locales, y sus consecuencias pudieron volver como experiencia. La conexión es un instrumento utilizable, no una política de control aprendida por el mero hecho de emitir torque. Los registros separan salida válida, acción ejecutada y utilidad.',
         mechanism='Hábitat01 enlazó una bifurcación E1 con Pendulum-v1 mediante una transducción fija: redondeo y acotación de 73+40·sin(theta) a 1…145; ±X a ±2 Nm; 67 ticks DEE por 0,05 segundos externos. Coseno y velocidad se descartaban. Silencio o conflicto producía cero neutral desde el puente. CF01 aplicó comandos a servicios, pero su retorno nativo estaba preparado antes de comprobar el efecto externo. ENTE01 corrigió ese enlace: sólo el contacto externo real generó el retorno pertinente.',
         rows=[
             ['Hábitat01', '73 pasos; 57 torques no nulos; 16 salidas anuladas por control.', '219 solicitudes: 146 aplicadas y 73 rechazadas. Dos semillas, control de acción anulada y retardo de un paso.'],
             ['MI01, reserva integrada', '47 pasos Pendulum: una salida no neutral +2 y 46 neutrales obligatorias.', 'Nueve oportunidades nativas sin contacto útil; recompensa −271,31210209120714. 804 solicitudes: 173 aplicadas, 613 ocupadas y 18 conflictos.'],
             ['CF01 → ENTE01', 'CF01 completa 24/24 trabajos en 33 intentos; ENTE01, seis trabajos en ocho intentos.', 'CF01 no cierra aún acción→retorno. ENTE01 sin retorno: 0/12 intentos del primer trabajo; MAIN: 69 actuaciones válidas, 47 útiles y 22 erróneas.'],
             ['APD03 / 2.0', 'APD03: ocho archivos reales correctos; 12/14 oportunidades útiles.', '2.0 conserva dos ACT fallidos ante dato oculto y dos USE formados sin efecto útil. Un comando formado no basta.'],
         ],
         controls='La acción anulada después de producirse, retorno omitido/desacoplado y referencias fijas o aleatorias externas separan influencia causal de desempeño accidental. Ninguna referencia controla al E1 evaluado. En ENTE01, una oportunidad común tras experiencia intacta o sham cambia delta 4→5 y mejora 7/16 en su contexto; anulada, omitida, desacoplada y corte no producen ese mismo cambio. Las reservas A/B/C alcanzan 16/24 primeras actuaciones útiles frente a 15/24 de una referencia fija, sin superioridad general.',
         current='El puente y la continuidad entre procesos se conservan como instrumentación. En IC01 la recompensa externa −1232,1764 queda por debajo de neutral, fijo +2 y aleatorio del auditor en los registros comparados. El mecanismo positivo de historia no queda invalidado, pero tampoco se rebautiza como control competente del péndulo. La cola de servicios, caché, plan de exposición y manejo neutral pertenecen a la asistencia declarada, no a memoria o decisión inteligente del ente.',
         applications='Aplicación demostrada: ejecutar actuaciones, producir artefactos verificables y devolver consecuencias mediante una regla fija. Uso propuesto: control situado con mejores interfaces y aprendizaje útil, conservando controles sobre el retorno. Gravedad e inercia del entorno elegido no certifican robótica industrial, metabolismo o autonomía general.',
         refs=['HAB-REPORT','HAB-CALC','IC-REPORT','IC-CALC','R01','R03','R04','R05','R11','ACT-CONT']),

    dict(id='familia_09', title='9. Agregación física, escala y cadencia',
         opening='Los ensayos de agregación muestran que múltiples entradas separadas pueden contribuir a una transformación conjunta dentro de DEE. Ese hecho debe distinguirse de admitir muchos bytes, tomar muchas decisiones o poseer muchas palabras. Aumentar espacio o suministro no ha resultado una garantía de mayor capacidad útil.',
         mechanism='Las entradas se entregan como componentes crudos independientes y se encuentran en estructuras nativas preparadas. ENTE02 distingue la extensión compatible R9 de una arquitectura nueva R10, con su propia vida desde T0. FI01 extiende árboles de encuentros a 128 componentes y prueba la relevancia individual. El anfitrión cuantiza y entrega valores; no calcula la suma correcta para inyectarla. Una cadencia diferente cambia qué encuentros y retornos coinciden.',
         rows=[
             ['ENTE02, R9/R10', 'R9: cuatro componentes, 3/3 agregados exactos pero 1/3 actuaciones útiles. R10: 46/46 exactos.', 'Ocho variables con relevancia individual. R10 final: 52 actuaciones, 45 útiles y siete erróneas; nueva vida, no memoria trasladada.'],
             ['MU/FI01, 128', 'Cambiar un componente 0→2 afecta salida en los 128 lugares: 126 reservas nuevas y dos repeticiones técnicas.', 'Tres tramas de MAIN: 528 entradas y 18 consultas anteriores. La reserva R17 conserva 12/12 tramas conjuntas y 120/120 accesos.'],
             ['Cadencia FI01', 'Δ2: 352/352 entradas admitidas en dos tramas, pero primera NULL, segunda + y memoria previa 0/6.', 'Δ16/67/200 mantienen 6/6 en sus ventanas. N101 no mejora universalmente y también cambia una referencia tardía.'],
             ['PC01, N67/N83', 'Fallo en la tercera ronda de ambos dominios: T204 frente a T252.', 'El tamaño mayor retrasa el fenómeno; no demuestra eliminación ni capacidad funcional proporcional al volumen libre.'],
         ],
         controls='La omisión de componente, modificación individual y comparación de salida cualificada verifican que el árbol hace algo más que transportar el último dato. Los ensayos seriales de dieciséis en R10 son dos tramas de ocho, no dieciséis simultáneos; serial32 no se ejecutó en R10. Un auxiliar R9 serial32 falló. Una ráfaga de dieciséis con 52/52 admisiones tampoco son dieciséis decisiones separadas; concurrencia dieciséis rechazó 24 y admitió 28.',
         current='La comparación adecuada incluye diversidad de funciones, retención y consecuencias, además de recursos. FI01 conserva un futuro adverso y un perfil con protección preparada y reenseñanza explícita: no hace desaparecer la pérdida anterior. La ocupación 89/300763 del corte actual 2.0 describe ese estado, no demuestra memoria disponible para cualquier tarea. Una celda state=0 puede conservar otros campos pertinentes; no se trata como espacio libre sin examinar su contrato.',
         applications='Aplicación demostrada: integración sensorial finita mediante encuentros con verificación de cada componente y uso de paneles previos. Desarrollo propuesto: cambiar organización, separación y fases cuando una tarea lo requiera. No se infiere escalabilidad a 10000 significados, límite universal de v27 ni superioridad de una arquitectura sólo por número de componentes.',
         refs=['PC-REPORT','PC-CALC','R05','R08','ACT-CONT']),

    dict(id='familia_10', title='10. Transferencia, representación y alcance práctico',
         opening='Hay transferencia funcional limitada cuando una referencia o selección adquirida cambia una actuación en otro contexto antes de recibir allí la nueva solución. Los ensayos también muestran transferencia perjudicial: una regularidad anterior puede dejar de ser útil al invertir la ley ambiental. La representación es material y dependiente del soporte, no un contenido que se clone libremente mediante etiquetas de software.',
         mechanism='El contenido adquirido altera una referencia o un selector que se reutiliza en otro servicio o interfaz. ENTE02 compara historias entrenada, omisión y desacoplada en destinos que no entregan todavía feedback. FI01 aplica selecciones adquiridas a tareas de archivo y contrapone una ley contradictoria. APD01 asocia señales a funciones existentes y compone su uso con un retorno escalar. El operador prepara oportunidades, servicios y reglas de transducción; los productos físicos eligen dentro de ese marco.',
         rows=[
             ['ENTE02, servicios', 'T: 6/6; U: 4/6; H: 3/6; acción anulada: 0/3.', 'En composición C2: T 4/4, U 2/4 y H 0/4. Ley contradictoria: T 1/3 frente a U 3/3.'],
             ['R10, cambio de interfaz', 'Experiencia de dos entradas→trabajos nuevos de ocho: T 4/4 frente a U 3/4.', 'La primera actuación difiere antes de retorno del destino; dominio y tamaño de muestra limitados.'],
             ['FI01, contraste', 'Transferencia T 4/4 frente a U/H 2/4; ley opuesta T 0/4.', 'B14: T 8/8 commits y U/H 0/8 pese a 148/148 entradas. Coste de aprendizaje censurado >8, no exactamente ocho.'],
             ['APD01–APD03', 'Señales adquiridas seleccionan SUM/DIFF preparados; nuevos operandos positivos y negativos probados.', 'APD03: Native 23 y archivo perturbado 24; siguiente ruta externa 18 correcta, después nativa 16 correcta con externa ausente.'],
         ],
         controls='El control de historia opuesta, ausencia de experiencia, desacoplamiento y acción anulada permite distinguir transferencia de un servicio que siempre funciona igual. Cuando un servicio valida un archivo real, ese hecho se conserva separado de una simulación de copia. La fase pública P0 puede ser indispensable: su control desacoplado da 2/6 frente a 6/6 real en ENTE02. Eso no implica que el ente haya aprendido a planificar o corregir la fase.',
         current='La transferencia no es uniformemente útil: MAIN ENTE02 conserva una secuencia A→B→C→A con paneles 12/12, 8/12 y 11/15, pero el último incluye cuatro experiencias explícitas de alineación. El criterio antiguo se readquiere: no se mantienen intactas dos políticas incompatibles. Las lecciones de una copia Full, GUIWALK o rama diagnóstica no se atribuyen a MAIN. Una importación completa compatible conserva pasado hasta su bifurcación; una receta nueva sólo prepara posibilidades.',
         applications='Aplicaciones demostradas: reutilizar una relación en otro contexto finito, elegir una función preparada mediante señal adquirida y verificar artefactos reales. Desarrollo propuesto: repertorios derivados y transferencia más general con reservas de leyes, interlocutores y tiempo. No se establece representación abstracta independiente del soporte ni clonación semántica.',
         refs=['R04','R05','R08','R09','R10','R11','R12','R13']),

    dict(id='familia_11', title='11. Español funcional, señales y cobertura NSM65',
         opening='Los resultados positivos sostienen asociaciones y usos funcionales finitos, algunos comunicables. El español facilita pedir y leer esos usos mediante codificación fija. La historia de una señal, su función actual y la interpretación humana deben conservarse separadas. Un parser de formas finitas no demuestra conversación libre ni comprensión de cada palabra que reconoce.',
         mechanism='Una señal se empareja mediante experiencia con una transformación y después participa en un uso sin que el codificador entregue la solución. Las fases de asociación, uso, retención, generalización, composición y comunicación se evalúan por separado. GENESIS es una interfaz local de gramática finita, sin LLM decisor. Las funciones aritméticas y las reglas de actuación preparadas están explícitas; aprender a seleccionar una de ellas no equivale a haber aprendido su algoritmo.',
         rows=[
             ['NSM65, CPC9', '65 filas: 60 E0, cuatro E2 y un E3.', 'DOS, ANTES, TOCAR, COMO: E2; MÁS: E3. Cinco positivos limitados, nueve prerrequisitos, 51 sin adquisición semántica ejecutada.'],
             ['K65', '65 formas repartidas sobre dos clases direccionales.', '65/65 respuestas no son 65 relaciones semánticas distintas. Máximos episódicos no equivalen a disponibilidad final en T2493.'],
             ['MI02, señal léxica', '16/16 tras enseñanza, pero también 16/16 en control de consecuencias desacopladas.', 'No acredita la semántica pretendida; una adquisición de acción posterior deja 4/8 accesos léxicos.'],
             ['APD04/APD05', 'APD04: 18 formas finitas más seis MA. APD05: 44/44 selecciones conformes, 18/44 útiles.', 'No son 24 conceptos, 65 significados o atención aprendida. Prefix 4/4 con dos efectos útiles; reserva 40/40 con 16.'],
         ],
         controls='Los controles sin enseñanza, señales intercambiadas, historias opuestas y reservas verifican qué aporta el emparejamiento. En APD03, el contraste emparejado 95/95 frente a desacoplado 89/95 incluye seis rechazos de la señal B: el resultado no se traduce en metaaprendizaje. El sensor APD05 representa versiones actual y anterior con una regla diseñada; no selecciona la respuesta óptima, pero tampoco es una habilidad sensorial aprendida.',
         current='El dominio positivo actual contiene señales como luma y clasifica con testigos después de reapertura en la vida seleccionada. La elección USE en versiones iguales puede formarse y no conseguir efecto útil; una lectura NULL posterior no es el número cero. NO no se acredita por silencio, rechazo o inversión; YO/TÚ requieren papeles intercambiables y siguen sin demostración funcional general. El campo semantic del kernel no representa una escala de significado lingüístico.',
         applications='Aplicación demostrada: utilizar expresiones finitas para acceder a relaciones adquiridas y operaciones preparadas, y revisar asociaciones explícitamente. Desarrollo propuesto: comunicación funcional con combinaciones y referentes no enseñados completos. NSM65 sigue siendo un programa de cobertura: las palabras españolas adicionales y las relaciones nativas sin traducción clara se mantienen en inventarios distintos.',
         refs=['CPC9_NSM_CSV','CPC9_CATALOGO_NSM','CPC9_MAPA_AFIRMACIONES','R02','R07','R09','R10','R11','R12','R13','ACT-CONT']),

    dict(id='familia_12', title='12. Continuidad, recuperación operativa y estado vigente',
         opening='La aportación operativa acumulada es conservar mecanismos ejecutables y vidas con historia identificada, sin atribuir al individuo seleccionado todo lo que existe en la biblioteca. Un snapshot físico aislado puede ser insuficiente para continuar una sesión: también pueden ser indispensables colas, interfaces, recibos, progreso de protocolos y estado del entorno o de trabajadores externos.',
         mechanism='El Core reconstruye familias históricas desde fuentes y configuraciones conservadas. Cognitive administra perfiles y vidas; cada continuidad exacta preserva el estado compatible y cada bifurcación identifica un nuevo futuro. La persistencia thinking 4.5 requiere RAW/clocks, interfaces, colas, recibos, metadatos y progreso tick/cursor completos. Sus perfiles experimentales remote/absence/regulation son dominios separados: no se fusionan en U0 por compartir biblioteca. DEE Cognitive 2.0 reutiliza esa aplicación sobre thinking 4.5.0 y Universe v27 congelados; su vida procede de una importación completa emparejada de APD05_MAIN, no de reconstruir desde T0 ni de fusionar recuerdos. El contrato FUNCTIONAL_CANDIDATE_VALIDATED mantiene su alcance; el nombre 4.5 no acredita una liberación universal.',
         rows=[
             ['Core CPC1–CPC8', '34 familias reconstruidas en 2504,199 s desde un ZIP de 73601685 bytes, sin abrir ZIP históricos.', 'Matriz de 56 filas: 39 C, una B y 16 D. Matriz CPC1–CPC9: 68 filas, 39 C,16 D,8 A,3 B,2 E. Las filas no son capacidades independientes.'],
             ['CPC9, vida histórica', 'T0–T2493, siete fases; seis fronteras concordantes, 352 frames y 1573 recibos únicos.', 'Una preparación N67 de 107 sitios; interfaces vacías añadidas en T1220/T1907 son ampliación instrumental.'],
             ['DEE20_DEMO_01', 'N67, T697764; padre APD05_MAIN T684418; perfil fisica_directa.', 'Snapshot completo y directorios emparejados. Selección personal no sustituye automáticamente ACTIVO.'],
             ['Testigos de la vida 2.0', 'luma +1 en T697678; clasifica −1 en T697745.', 'Cada uno registra siete peticiones aplicadas después de reabrir, sin nueva enseñanza en esos usos. Fallos a29/a32 permanecen.'],
         ],
         controls='Las reproducciones técnicas no son nuevas adquisiciones ni réplicas independientes. La prueba de recuperación del Core verifica sus contratos y declara Windows x64, CPython 3.13 x64 y dependencia opcional NumPy 2.2.6 para CORE06/07. No se repitieron aquí las 34 familias. El corte 2.0 declara cero pendientes de cola en su ficha, propietario pausado y conservación del transporte; esos diarios no se convierten por ello en memoria usada para contestar.',
         current='La fuente operativa vigente es DEE Cognitive 2.0, con Manual Maestro edición 1.21. Los expedientes 1.1 permanecen en archivo/DEE Cognitive System 1.1. Las producciones audiovisuales están en archivo/produccion_audiovisual_DEE_Cognitive_2_0_20261028/videos. casos practicos permanece en la raíz por un permiso de movimiento denegado: el compendio no afirma un archivado que no sucedió. La comprobación de traslado sobre copia aislada es operativa, no una nueva certificación de todas las capacidades científicas.',
         applications='Uso demostrado: cargar, bifurcar, guardar y continuar historias completas dentro de sus contratos; recuperar mecanismos separados y conservar futuros adversos. Uso propuesto: ampliaciones compatibles o perfiles alternativos con comparación proporcional. La selección de una vida especializada no la convierte en memoria colectiva de mundos desconectados, mente general, conciencia ni regulación ilimitada.',
         refs=['F-LB45','F-MA45','CPC_CORE_RECUPERACION','CPC_CORE_MATRIZ','CPC9_VIDA_INTEGRAL','CPC9_FINAL_PRIMARIO','CPC9_MAPA_AFIRMACIONES','ACT-PROYECTO','ACT-CONT','R10','R11','R12','R13']),
]


def set_cell_width(cell, width_cm):
    cell.width = Cm(width_cm)
    pr = cell._tc.get_or_add_tcPr()
    width = pr.find(qn('w:tcW'))
    if width is None:
        width = OxmlElement('w:tcW'); pr.append(width)
    width.set(qn('w:type'), 'dxa')
    width.set(qn('w:w'), str(round(width_cm * 567)))


def configure_styles(doc):
    sec = doc.sections[0]
    sec.page_width = Cm(21); sec.page_height = Cm(29.7)
    sec.top_margin = sec.bottom_margin = sec.left_margin = sec.right_margin = Cm(2)
    sec.header_distance = sec.footer_distance = Cm(0.8)
    for style in doc.styles:
        if style.type == 1 or style.type == 2:
            style.font.name = 'Calibri'; style.font.color.rgb = RGBColor(0,0,0)
    normal = doc.styles['Normal']
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.08
    normal.paragraph_format.widow_control = True
    for name, size in [('Title',27),('Subtitle',15),('Heading 1',17),('Heading 2',13),('Heading 3',11)]:
        st = doc.styles[name]
        st.font.name = 'Calibri'; st.font.size = Pt(size); st.font.color.rgb = RGBColor(0,0,0)
        st.paragraph_format.keep_with_next = True
        st.paragraph_format.space_before = Pt(12 if name != 'Title' else 0)
        st.paragraph_format.space_after = Pt(8)
    doc.styles['Title'].base_style = None
    doc.styles['Subtitle'].base_style = None
    # Clear template paragraph borders, including those inherited by Title.
    for style in doc.styles:
        for border in list(style.element.iter(qn('w:pBdr'))):
            border.getparent().remove(border)
    doc.styles['Heading 1'].paragraph_format.page_break_before = True
    # Keep titles plain, without theme accent colors or decorative geometry.
    header = sec.header.paragraphs[0]
    header.text = 'DEE · Compendio científico acumulativo'
    header.runs[0].font.size = Pt(8)
    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = footer.add_run('Investigación privada · ')
    run.font.size = Pt(8)
    field = OxmlElement('w:fldSimple'); field.set(qn('w:instr'), 'PAGE')
    footer._p.append(field)
    props = doc.core_properties
    props.title = TITLE; props.subject = SUBTITLE; props.author = AUTHOR
    props.keywords = 'DEE; mecanismos; historia; memoria; acceso; evidencia; compendio'
    props.comments = 'Síntesis editorial de registros existentes. No ejecuta simulaciones ni certifica capacidades generales.'


def bookmark(paragraph, name, value):
    start = OxmlElement('w:bookmarkStart')
    start.set(qn('w:id'), str(value)); start.set(qn('w:name'), name)
    end = OxmlElement('w:bookmarkEnd'); end.set(qn('w:id'), str(value))
    paragraph._p.insert(0, start); paragraph._p.append(end)


def internal_link(paragraph, label, anchor, size=10):
    link = OxmlElement('w:hyperlink'); link.set(qn('w:anchor'), anchor)
    link.set(qn('w:history'), '1')
    run = OxmlElement('w:r'); props = OxmlElement('w:rPr')
    color = OxmlElement('w:color'); color.set(qn('w:val'), '000000'); props.append(color)
    underline = OxmlElement('w:u'); underline.set(qn('w:val'), 'single'); props.append(underline)
    font_size = OxmlElement('w:sz'); font_size.set(qn('w:val'), str(round(size*2))); props.append(font_size)
    run.append(props); text = OxmlElement('w:t'); text.text = label; run.append(text)
    link.append(run); paragraph._p.append(link)


def anchor_name(identifier):
    return 'src_' + re.sub(r'[^A-Za-z0-9_]', '_', identifier)


def refs(doc, identifiers):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(8)
    p.add_run('Fuentes: ').font.size = Pt(9)
    for index, identifier in enumerate(dict.fromkeys(identifiers)):
        if index:
            p.add_run(' · ').font.size = Pt(9)
        internal_link(p, identifier, anchor_name(identifier), 9)


def para(doc, text, bold_prefix=None, size=None):
    p = doc.add_paragraph()
    if bold_prefix:
        p.add_run(bold_prefix + ' ').bold = True
    run = p.add_run(text)
    if size: run.font.size = Pt(size)
    return p


def table(doc, headers, rows, widths=(3.0,6.0,8.0), size=9):
    assert len(headers) == len(widths) and abs(sum(widths)-17) < 0.01
    tb = doc.add_table(rows=1, cols=len(headers))
    tb.alignment = WD_TABLE_ALIGNMENT.CENTER; tb.autofit = False
    for col, width in zip(tb.columns, widths): col.width = Cm(width)
    properties = tb._tbl.tblPr
    overall = properties.find(qn('w:tblW'))
    overall.set(qn('w:type'),'dxa'); overall.set(qn('w:w'),'9638')
    borders = OxmlElement('w:tblBorders')
    for side in ('top','left','bottom','right','insideH','insideV'):
        el = OxmlElement('w:'+side); el.set(qn('w:val'),'single')
        el.set(qn('w:sz'),'4'); el.set(qn('w:color'),'D9D9D9'); borders.append(el)
    properties.append(borders)
    repeat = OxmlElement('w:tblHeader'); repeat.set(qn('w:val'),'true')
    tb.rows[0]._tr.get_or_add_trPr().append(repeat)
    for cells, content, heading in [(tb.rows[0].cells, headers, True)]:
        for c, text, width in zip(cells, content, widths):
            set_cell_width(c, width); c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
            p=c.paragraphs[0]; p.paragraph_format.space_after=Pt(3); p.paragraph_format.space_before=Pt(3)
            r=p.add_run(str(text)); r.bold=heading; r.font.size=Pt(size)
    for row in rows:
        new = tb.add_row()
        cant = OxmlElement('w:cantSplit'); new._tr.get_or_add_trPr().append(cant)
        for c, value, width in zip(new.cells, row, widths):
            set_cell_width(c,width); c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.TOP
            p=c.paragraphs[0]; p.paragraph_format.space_after=Pt(3); p.paragraph_format.space_before=Pt(3)
            p.paragraph_format.line_spacing=1.0
            p.add_run(str(value)).font.size=Pt(size)
    doc.add_paragraph().paragraph_format.space_after=Pt(1)
    return tb


def heading(doc, title, anchor=None, level=1, number=1):
    p=doc.add_heading(title,level)
    if anchor: bookmark(p,anchor,number)
    return p


def breakable(value):
    # U+200B changes only displayed line-break opportunities, not source paths.
    return re.sub(r'([/\\_.-])', lambda m: m.group(1)+'\u200b', str(value))


def strip_decorative_lines(doc):
    # This compendium has no figures. Remove template rules/shapes from every
    # document story and style so a theme cannot render a decorative title bar.
    containers=[doc.element, doc.styles.element]
    for section in doc.sections:
        containers.extend([section.header._element, section.footer._element])
    for container in containers:
        for tag in ('w:pBdr','w:drawing','w:pict'):
            for node in list(container.iter(qn(tag))):
                parent=node.getparent()
                if parent is not None: parent.remove(node)


def small(doc, label, text, size=8.5):
    p=doc.add_paragraph()
    p.paragraph_format.line_spacing=1.0; p.paragraph_format.space_after=Pt(3)
    p.add_run(label+' ').bold=True
    p.add_run(breakable(text))
    for run in p.runs: run.font.size=Pt(size)
    return p


def add_opening(doc, project, continuity, source_ids):
    doc.add_paragraph(TITLE,'Title')
    doc.add_paragraph(SUBTITLE,'Subtitle')
    para(doc, AUTHOR)
    para(doc, 'Proyecto INVESTIGACION DEE · Corte editorial: 28 de octubre de 2026')
    para(doc, 'Universe v27 y DEE thinking 4.5.0 congelados. Documento privado de investigación.')
    para(doc, 'La evidencia acumulada demuestra mecanismos físicos que adquieren asociaciones, revisan referencias, conservan y utilizan información, combinan contribuciones y transmiten efectos entre participantes. Parte de esas funciones está disponible en vidas operativas con genealogía propia. También demuestra interferencias, pérdida de acceso y pérdidas causales en dominios concretos. Este compendio explica ambos resultados a partir de registros existentes.')
    para(doc, 'No se ejecutaron nuevos experimentos para redactarlo. Los resultados de campañas distintas se reúnen por mecanismo para comprender su evolución; no se suman como capacidades simultáneas de un individuo. La reorganización de carpetas y su comprobación operativa sobre copia son trabajos distintos de la investigación histórica resumida aquí.')
    table(doc, ['Capa','Qué es','Alcance actual'], [
        ['Universe v27','Dinámica fundamental congelada.','No se modifica ni se infiere reversibilidad global.'],
        ['DEE thinking 4.5.0','Instrumento oficial: ejecución, mundos, experiencias, observación y persistencia.','Una receta o API no contiene por sí sola aprendizajes de otra vida.'],
        ['Cognitive 1.1 / presentación 2.0','Capa de gestión y capacidades; vidas, protocolos, interfaces y aplicación local.','La presentación 2.0 no es una versión nueva del kernel ni certifica una mente general.'],
    ], size=9.5)
    refs(doc,['ACT-PROYECTO','ACT-CONT'])

    heading(doc,'Cómo leer la evidencia','lectura',number=2)
    para(doc,'Cada familia empieza por el resultado positivo, explica la cadena experiencia→transformación física→uso posterior y después indica controles, asistencia, pérdidas y alcance. Los identificadores de fuentes son enlaces internos al índice final; allí figuran el archivo, hash y localizador pertinente. Un archivo ZIP y un miembro extraído tienen identidades distintas: cuando la extracción dispone de ambos hashes, se conservan ambos.')
    table(doc,['Distinción','Qué permite afirmar','Qué debe acompañarla'],[
        ['Hecho computacional','Un recuento, un campo, una diferencia o un artefacto comprobados.','Fuente primaria, denominador, condición y localizador.'],
        ['Mecanismo físico','Una intervención cambia la transformación o consecuencia pertinente.','Corte u omisión, control sham cuando corresponde y efectos sobre funciones testigo.'],
        ['Capacidad funcional','La organización utiliza una relación para producir una consecuencia definida.','Vida, historia, acceso, preparación y reservas dentro de su dominio.'],
        ['Interpretación o hipótesis','Una lectura científica o posibilidad de desarrollo.','Separarla de lo ejecutado y especificar qué evidencia falta.'],
    ],size=9.5)
    para(doc,'P0/R0 designa preparación eficaz; P1/R1, respuesta condicionada por estado adquirido; P2/R2 local, selección modificada por experiencias y consecuencias dentro de un contrato. Ninguna etiqueta local acredita regulación general. El origen de una petición también importa: calendario externo, recurrencia preparada y consulta producida por un estado adquirido son modalidades distintas.')
    para(doc,'Los numeradores conservan sus denominadores. Entradas solicitadas, admitidas, rechazadas, respuestas formadas y acciones útiles no se sustituyen entre sí. Consultas sucesivas de una vida y bifurcaciones con prefijo común no son muestras biográficas independientes. Reproducción técnica y adquisición nueva son hechos diferentes.')
    para(doc,'El cierre de OBP corrige interpretaciones históricas: un producto remoto observado no resultó necesario bajo sus cortes, aunque permanece evidencia positiva de plasticidad relacional en su dominio. La no inyectividad explicada en Física DEE impide exigir reconstruir un pasado diferente cuando el sistema causal completo ya convergió y recibe idéntico futuro. Estas precisiones limitan atribuciones sin borrar funciones demostradas.')
    refs(doc,['F-PN','F-FIS','F-OBP','RET-CALC'])

    heading(doc,'Índice navegable','indice',number=3)
    for family in FAMILIAS:
        p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(6)
        internal_link(p,family['title'],family['id'],11)
    for text,anchor in [('Síntesis de integración y estado presente','integracion'),('Cronología científica acumulativa','cronologia'),('Índice de fuentes, primarios y localizadores','fuentes')]:
        p=doc.add_paragraph(); internal_link(p,text,anchor,11)
    para(doc,'El índice interno enlaza las familias y las fuentes. Los números de página se muestran en el pie; cada fuente conserva su archivo, hash y localizador.')


def add_family(doc, family, ordinal):
    heading(doc,family['title'],family['id'],number=10+ordinal)
    para(doc,family['opening'])
    heading(doc,'Cómo sucede',level=2)
    para(doc,family['mechanism'])
    heading(doc,'Resultados y contrastes decisivos',level=2)
    table(doc,['Caso / organización','Resultado registrado','Contraste y alcance'],family['rows'])
    para(doc,family['controls'],bold_prefix='Causalidad y controles.')
    para(doc,family['current'],bold_prefix='Interpretación y disponibilidad actuales.')
    para(doc,family['applications'],bold_prefix='Uso y desarrollo.')
    refs(doc,family['refs'])
    p=doc.add_paragraph(); internal_link(p,'Volver al índice','indice',9)


def add_current(doc,project,continuity,register):
    heading(doc,'Síntesis de integración y estado presente','integracion',number=40)
    para(doc,'La conservación operativa tiene tres niveles que no deben confundirse: mecanismos ejecutables del sistema, conocimiento físico de una vida y herramientas externas. El catálogo permite encontrar realizaciones y contratos; no es una lista de todo lo que sabe la vida seleccionada. Las incorporaciones históricas 1.1 no se certifican otra vez por esta síntesis editorial.')
    table(doc,['Mecanismo o uso','Dónde está demostrado','Estado de atribución'],[
        ['Asociaciones y revisión','SEM01, repertorios, U0, MA02 y descendientes APD; cada uno en sus propios cortes.','Adquisición y retención finitas; no se trasladan sus máximos a otro individuo.'],
        ['Acceso alternativo','AA READY, IC01 recuperación y separación triple de Ciclo02.','Capacidad asistida y/o condicionada; no recuperación general iniciada autónomamente.'],
        ['Consecuencias y acción útil','Puerta Ciclo02, R8/R9, ENTE y selección APD02 dentro de reservas específicas.','Positivos locales con negativos de inversión, calidad e interferencia.'],
        ['Herramientas y actuación externa','Puente Pendulum, trabajadores de archivo, codec, colas y observadores.','Instrumentación externa explícita; el efecto de la salida requiere control causal.'],
        ['Aritmética y encadenamiento 2.0','DEE20_DEMO_01, trayecto registrado 4+5→9; después 9−2→7.','Operación nativa preparada y secuencia pedida por operador; no algoritmo o plan aprendidos.'],
    ],size=9)
    physical=continuity.get('physical_cut',{})
    parent=continuity.get('parent',{})
    life=continuity.get('life_id',project.get('selected_life','no indicado'))
    para(doc,f"La vida seleccionada es {life}, perfil {continuity.get('profile','no indicado')}, N={physical.get('N')}, T{physical.get('tick')}. Su padre es {parent.get('life_id')} en T{parent.get('source_tick')}. La importación fue completa y emparejada una vez, con identificación nueva de la continuidad seleccionada, sin T0 ni fusión de memorias. El producto mantiene aparte sus originales y futuros adversos.")
    para(doc,'El corte declara 300763 sitios, 89 con state>0 y máximo s_reg 4530. Son observables de ese estado; no son energía, capacidad cognitiva total ni número de recuerdos. Los hashes RAW y clocks y el snapshot completo figuran en la ficha vigente. Los archivos históricos de evidencia son localizadores de procedencia opcionales; no respuestas que el actor consulte durante el funcionamiento normal.')
    for w in continuity.get('latest_functional_witnesses_in_this_life',[]):
        para(doc,f"Testigo {w.get('step')}: {w.get('form')} produce signo {w.get('native_sign'):+d} después de T{w.get('after_tick')}; {w.get('native_requests')} peticiones nativas, estados {w.get('native_receipt_states')}. La ficha lo identifica como uso después de reapertura sin reenseñanza. Este testigo acredita ese uso, no la disponibilidad de todo el vocabulario.")
    para(doc,'Los contraejemplos vigentes se preservan: a29 elige ACT dos veces y falla en ambos intentos de una meta con dato privado no obtenido; a32 forma dos USE con versiones iguales, pero no obtiene efecto útil, y la lectura posterior numérica/balance es NULL. El controlador anterior también registró una pausa por espejo pendiente obsoleto; el mismo ID se conservó sin repetición silenciosa. No se retocan esos resultados para la presentación.')
    heading(doc,'Continuar sin recrear ni mezclar',level=2)
    para(doc,'La entrada operativa es DEE Cognitive 2.0/ABRIR_DEE_COGNITIVE.bat. La ficha permite indicar --sistema --vida DEE20_DEMO_01, abrir/continuar y reanudar con Vivir. Se conserva el snapshot completo y los directorios íntegros de identidad, servicio persistente, servicio local y progreso de entrada sencilla. La cola SQLite y sus sidecars se tratan coherentemente; una copia de RAW/clocks o este compendio no sustituyen el conjunto operativo.')
    para(doc,'La reorganización conserva 4.5 y archiva DCS1.1 como antecedente. casos practicos permanece en raíz porque el movimiento fue denegado con WinError5: no se fuerza el permiso ni se presenta una copia parcial como archivado completo. El registro único conserva la excepción y la comprobación de traslado. La versión de software y edición del manual no cambian por generar este compendio.')
    # Summarize only completed relocation events, never claim a still-running check passed.
    check=register.get('prueba_operativa_aislada',{})
    events=check.get('eventos',[]) if isinstance(check,dict) else []
    stages=[e.get('etapa','') for e in events if isinstance(e,dict)]
    if stages:
        para(doc,'El registro de reorganización leído durante la autoría contiene estas etapas operativas, sin reinterpretarlas como pruebas científicas: '+', '.join(dict.fromkeys(stages))+'. La inspección y las consultas materiales de esa comprobación pertenecen a la copia aislada, no a nuevas experiencias del original protegido.')
    refs(doc,['ACT-PROYECTO','ACT-CONT','R07','R08','R10','R13'])


CRONOLOGIA = [
    ('CORE / Ingenierías / OBP','Plasticidad, historia y accesos como mecanismos físicos.','La reutilización y memoria relacional se conservan en dominios propios; el cierre OBP retira la necesidad del producto remoto.','F-PN, F-FIS, F-OBP'),
    ('CPC1–CPC3','Orden, anticipación y asociación adquirida.','Contratos separados recuperados; sensores y oportunidades preparados, sin conocimiento del futuro entregado.','CPC_CORE_RECUPERACION'),
    ('CPC4–CPC6','Transmisión, composición y conservación/acceso.','Comunicación finita, lectores no inocuos y recuperaciones asistidas; auxiliares no se suman a E1.','CPC_CORE_MATRIZ'),
    ('CPC7 / dos CPC8','Repertorios, revisión y continuidad finita.','U0, MCTS y K65 tienen historias diferentes. 65 formas direccionales no son NSM65.','CPC_CORE_MATRIZ, CPC9_NSM_CSV'),
    ('CPC9','Vida N67 T0–2493; integración y deterioro.','K65 57/65→53/65→4/65; finales 177/178 rechazadas por diferencia de IDs, no por últimas posiciones.','CPC9_K65_PRIMARIO, CPC9_FINAL_PRIMARIO'),
    ('EF01 / PC01','Enseñanza espacial y acceso bajo encuentros.','Lectores, protección y contexto tienen efectos mixtos; N83 retrasa el fallo de N67, sin resolverlo.','PC-REPORT, PC-CALC'),
    ('AA01 / Retrospectiva','Acceso alternativo, selector local y pérdida causal.','READY conserva otro futuro; AA13 demuestra convergencia causal delimitada, no igualdad de todo archivo documental.','AA-CALC, RET-CALC'),
    ('Hábitat / IC01','Puente externo, información privada y referencia por retorno.','Actuación causal no es control competente. Recuperación social de ambos signos asistida 4/4 por dirección.','HAB-CALC, IC-CALC'),
    ('Ciclo02','Acción útil y protección social limitada.','21/21 útiles en MAIN; separación triple operativa T21711 con pérdidas posteriores y P0 explícito.','C2-CALC'),
    ('MI01 / MI02','Interferencia integrada y alternativas distribuidas.','MAIN MI01 adversa; nuevas vidas N26 con selección útil, recuperación P0 y límites léxicos.','R01, R02'),
    ('CF01 / ENTE01','Servicio compuesto y corrección del retorno.','CF01 tenía retorno preparado antes de acción externa; ENTE01 hace depender el retorno del contacto real.','R03, R04'),
    ('ENTE02 / MA01','Agregación, transferencia y límites acumulativos.','R10 nuevo desde T0; transferencia puede ser negativa. MA01 no retiene cuatro políticas a la vez.','R05, R06'),
    ('MA02','Cinco asociaciones y acceso repetible preparado.','Composición con pérdidas; residuos reutilizados para enseñanza nueva y selector P1 complementario.','R07'),
    ('Mente unificada / FI01','Seis asociaciones, 128 componentes y aplicación real.','Deterioro localizado; protección P0 y reenseñanza declaradas en nuevo futuro, sin borrar adverso.','R08'),
    ('APD01 / APD02','Señales, servicios, acumulador y calidad local.','Renovación P0, P2 local limitado; 4/7 frente 3/7 no supera siempre-external 4/7.','R09, R10'),
    ('APD03 / APD04','Metas, señales nuevas y ecosistema de información.','Ocho archivos correctos en APD03; APD04 expone sensor insuficiente, información obsoleta y deterioro.','R11, R12'),
    ('APD05','GENESIS local y versión sensorial diseñada.','44/44 selecciones conformes, 18/44 útiles; T684418 con negativos, nuevas enseñanzas y pausa exacta conservados.','R13'),
    ('DEE Cognitive 2.0','Presentación y continuidad seleccionable.','DEE20_DEMO_01 T697764, padre APD05 T684418; testigos de reapertura y fallos reales. Manual 1.21.','ACT-PROYECTO, ACT-CONT'),
]


def add_chronology(doc):
    heading(doc,'Cronología científica acumulativa','cronologia',number=41)
    para(doc,'La secuencia ordena campañas y correcciones, no una escala única de inteligencia. Las filas no son capacidades independientes ni una biografía sin bifurcaciones. Cada leyenda identifica qué avance se conserva y qué interpretación posterior limita o corrige la lectura anterior.')
    # Split the chronology into moderate tables with their own repeated headers.
    for offset in range(0,len(CRONOLOGIA),6):
        rows=[list(x) for x in CRONOLOGIA[offset:offset+6]]
        table(doc,['Etapa','Contribución','Corrección o límite','Fuentes'],rows,(2.3,4.2,7.0,3.5),8.8)
    para(doc,'Las fuentes incluyen resultados positivos, contraejemplos y recálculos ya archivados. Los prompts históricos orientan el objetivo de una campaña, pero no se tratan como evidencia de que una función se ejecutó. Una ausencia de artefacto o reproducción se conserva como pendiente, sin completar huecos por analogía.')
    refs(doc,['CPC_CORE_MATRIZ','RET-CALC','R13','ACT-CONT'])


def add_sources(doc, sources):
    heading(doc,'Índice de fuentes, primarios y localizadores','fuentes',number=42)
    para(doc,'Este índice forma parte del mismo documento. SHA-256 identifica los bytes de la fuente leída, no valida por sí solo su interpretación. Los hashes de campañas son los de las extracciones dirigidas existentes; no se rehizo una auditoría integral del corpus. Las fuentes fundacionales fueron consultadas de forma dirigida por el responsable editorial. Los metadatos actuales se leyeron para resolver identidad y continuidad, sin avanzar el ente.')
    para(doc,f'El índice reúne {len(sources)} fuentes. Una comprobación dirigida de las 68 fuentes anteriores confirmó sus rutas y SHA-256, junto con 13 miembros ZIP y siete primarios adicionales; los dos manuales oficiales 4.5 añadidos fueron abiertos de forma dirigida y comprobados por el responsable. También se obtuvo el hash del recálculo R08 antes no registrado. Esta cobertura identifica los archivos citados; no declara íntegro ni revalidado todo el corpus histórico.')
    para(doc,'Las rutas de CPC conservan casos practicos en raíz. Las rutas antes relativas a DEE Cognitive System 1.1 se resuelven ahora en archivo/DEE Cognitive System 1.1. Un localizador dentro de JSON o un miembro ZIP permite llegar al dato pertinente. Los identificadores se conservan aunque varias familias utilicen el mismo mecanismo o documento.')
    for index,source in enumerate(sources):
        identifier=source['id']
        title=identifier
        if source.get('campana'): title+=' · '+source['campana']
        p=doc.add_paragraph()
        p.paragraph_format.keep_with_next=True; p.paragraph_format.space_before=Pt(7); p.paragraph_format.space_after=Pt(3)
        r=p.add_run(title); r.bold=True; r.font.size=Pt(10)
        bookmark(p,anchor_name(identifier),100+index)
        small(doc,'Archivo:',source['ruta_actual'])
        if source.get('sha256'): small(doc,'SHA-256:',source['sha256'])
        if source.get('miembro'):
            small(doc,'Miembro ZIP:',source['miembro'])
            if source.get('sha256_miembro'): small(doc,'SHA-256 miembro:',source['sha256_miembro'])
        locator=source.get('localizador') or '; '.join(source.get('localizadores',[]))
        if locator: small(doc,'Localizador:',locator)
        scope=source.get('alcance') or source.get('alcance_lectura')
        if scope: small(doc,'Alcance:',scope)
        for primary in source.get('primarios',[]):
            small(doc,'Primario leído:', 'archivo/DEE Cognitive System 1.1/'+primary['ruta'])
            if primary.get('sha256'): small(doc,'SHA-256 primario:',primary['sha256'])
            if primary.get('localizador'): small(doc,'Localizador primario:',primary['localizador'])
            if primary.get('observado'): small(doc,'Comprobación registrada:',primary['observado'])
        recalc=source.get('recalculo_leido')
        if recalc:
            small(doc,'Recálculo archivado consultado:','archivo/DEE Cognitive System 1.1/'+recalc['ruta'])
            if recalc.get('sha256'):small(doc,'SHA-256 recálculo:',recalc['sha256'])
            else:small(doc,'Identidad del recálculo:','La extracción dirigida no registra un hash independiente de ese archivo; no se inventa uno.')
            small(doc,'Localizador:',recalc.get('localizador',''))
            small(doc,'Alcance:',recalc.get('observado',''))
    heading(doc,'Cobertura y límite documental',level=2)
    para(doc,'El compendio sintetiza las fuentes primarias y resultados identificados en este índice. No es copia íntegra de la telemetría, respaldo operativo, reproducción nativa nueva ni certificación de todas las familias. Las 16 filas históricas D del Core mantienen su pendiente de recuperación amplia aunque haya mecanismos parciales reproducidos después. No se niegan resultados originales por esa clasificación. Los estados completos, variantes, negativas y código histórico permanecen en sus expedientes.')
    para(doc,'En particular, ningún éxito auxiliar se suma a E1 por compartir motor o gestor; ningún máximo histórico sustituye el panel final de una vida; ninguna respuesta de un diario externo se atribuye al participante. Las aplicaciones futuras descritas son preguntas de desarrollo, separadas de usos ejecutados. La evidencia positiva acumulada sigue siendo utilizable dentro de esos límites.')
    p=doc.add_paragraph(); internal_link(p,'Volver al índice','indice',10)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=OUT)
    parser.add_argument('--app',type=Path,default=ROOT/'DEE Cognitive 2.0')
    args=parser.parse_args()
    modules={n:load_module('fuentes_'+n) for n in ['cpc','intermedias','recientes']}
    # Read only the current authority; never create a replacement if it is absent.
    project=read_json(args.app/'PROYECTO.json')
    continuity=read_json(args.app/'CONTINUIDAD_DEE_COGNITIVE_2_0.json')
    register=read_json(ROOT/'archivo/reorganizacion_20261028/REGISTRO_REORGANIZACION.json')
    sources=source_set(modules,args.app)
    ids={s['id'] for s in sources}
    assert len(ids)==len(sources),'Identificadores de fuente duplicados'
    assert all(set(f['refs'])<=ids for f in FAMILIAS),'Referencia editorial sin fuente'
    # The modules are the cited, curated input. Assert their expected coverage,
    # while leaving their detailed texts out of any capability-count arithmetic.
    assert len(modules['cpc'].FICHAS)==13
    assert len(modules['intermedias'].FICHAS)==9
    assert len(modules['recientes'].FICHAS)==10
    doc=Document(); configure_styles(doc)
    add_opening(doc,project,continuity,ids)
    for number,family in enumerate(FAMILIAS,1):add_family(doc,family,number)
    add_current(doc,project,continuity,register)
    add_chronology(doc)
    add_sources(doc,sources)
    strip_decorative_lines(doc)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    doc.save(args.output)
    print(json.dumps({'docx':str(args.output),'bytes':args.output.stat().st_size,
                      'familias':len(FAMILIAS),'fuentes':len(sources),
                      'native_imports':0,'new_experimental_ticks':0,
                      'visual_qa':'Pendiente de renderizar e inspeccionar por el responsable del documento.'},ensure_ascii=False))


if __name__=='__main__':
    main()
