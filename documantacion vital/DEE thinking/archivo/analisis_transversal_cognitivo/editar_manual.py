"""Edición documental DCS11-MM-001. No importa ni ejecuta DEE."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_BREAK

W = Path(__file__).resolve().parent
ROOT = W.parent.parent
NAME = 'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
SOURCE = W / 'edicion_anterior' / NAME
TARGET = W / 'manual_en_revision.docx'
REG = W / 'REVISION_TRANSVERSAL.json'
R = json.loads(REG.read_text(encoding='utf8'))
D = Document(SOURCE)

def replace(p, text):
    for r in p.runs: r.text = ''
    (p.runs[0] if p.runs else p.add_run()).text = text

for p in D.paragraphs:
    if p.text.startswith('DEE thinking 4.5.0 |'):
        replace(p, 'DEE thinking 4.5.0 | DEE Cognitive 2.0 | Edición documental 1.22 | DCS11-MM-001')
    elif p.text.startswith('Edición documental 1.21, revisión de organización'):
        replace(p, 'Edición documental 1.22. Análisis transversal del 29 de octubre de 2026. Lea primero el punto de reanudación y el capítulo 39. La vida protegida continúa en T697764; esta revisión no ejecuta experiencias ni modifica su selección o estado.')
    elif p.text.startswith('Se conservan los capítulos 1 a 37, sus tablas'):
        replace(p, 'Los capítulos 1 a 38 y los apéndices originales conservan sus resultados e identidades históricas. El punto de reanudación, el capítulo 39 y el apéndice F incorporan el análisis transversal. Una afirmación antigua sobre ACTIVO o una edición se interpreta en su corte, no como sustitución del estado vigente.')
for row in D.tables[0].rows:
    if len(row.cells) < 2: continue
    key = row.cells[0].text
    if key == 'Documento': row.cells[1].text = 'DCS11-MM-001 / Edición documental 1.22 / Análisis transversal 29 de octubre de 2026'
    elif key == 'Base principal': row.cells[1].text = 'Mismo manual lógico y misma ruta de apertura. Edición 1.21 preservada en archivo/analisis_transversal_cognitivo/edicion_anterior. Se conserva el nombre del archivo para no cambiar PROYECTO.json ni el lanzador.'
    elif key == 'Estado de esta edición': row.cells[1].text = 'Revisión documental por bloques, sin simulaciones ni consultas materiales. Cobertura y comprobación visual en el registro único. No es una versión nueva del motor ni una promoción de vida.'
for section in D.sections:
    for obj in (section.header, section.footer, section.first_page_header, section.first_page_footer):
        for p in obj.paragraphs:
            for r in p.runs:
                if '1.21' in r.text: r.text = r.text.replace('1.21', '1.22')
                if '28 OCT 2026' in r.text: r.text = r.text.replace('28 OCT 2026', '29 OCT 2026')

def p(text):
    a = D.add_paragraph()
    r = a.add_run(text); r.font.name = 'Calibri'; r.font.size = Pt(11)
    a.paragraph_format.space_after = Pt(6)
    return a._p

def h(text, level=2):
    a = D.add_paragraph(text, style='Heading ' + str(level))
    for r in a.runs: r.font.color.rgb = RGBColor(0, 0, 0)
    a.paragraph_format.keep_with_next = True
    return a._p

def page():
    a = D.add_paragraph(); a.add_run().add_break(WD_BREAK.PAGE); return a._p

def bookmark(e, name, idx):
    a = OxmlElement('w:bookmarkStart'); a.set(qn('w:id'), str(idx)); a.set(qn('w:name'), name)
    b = OxmlElement('w:bookmarkEnd'); b.set(qn('w:id'), str(idx)); e.insert(0, a); e.append(b)

def link(text, anchor):
    a = D.add_paragraph(); e = OxmlElement('w:hyperlink'); e.set(qn('w:anchor'), anchor)
    r = OxmlElement('w:r'); t = OxmlElement('w:t'); t.text = text; r.append(t); e.append(r); a._p.append(e)
    return a._p

def table(headers, rows, widths):
    t = D.add_table(rows=1, cols=len(headers)); t.style = 'Table Grid'; t.autofit = False
    for i, v in enumerate(headers): t.rows[0].cells[i].text = v
    repeat = OxmlElement('w:tblHeader'); t.rows[0]._tr.get_or_add_trPr().append(repeat)
    for row in rows:
        for c, v in zip(t.add_row().cells, row): c.text = str(v)
    for row in t.rows:
        for i, c in enumerate(row.cells):
            c.width = Inches(widths[i])
            for a in c.paragraphs:
                a.paragraph_format.space_after = Pt(4)
                for r in a.runs: r.font.name = 'Calibri'; r.font.size = Pt(10)
    for c in t.rows[0].cells:
        for a in c.paragraphs:
            for r in a.runs: r.bold = True
    return t._tbl

def before(elements, anchor):
    for e in elements: anchor.addprevious(e)

def after(elements, anchor):
    for e in reversed(elements): anchor.addnext(e)

# Tres páginas iniciales de continuidad.
a = [h('Punto de reanudación', 1)]; bookmark(a[-1], 'AT_REANUDACION', 9001)
a += [h('Qué existe y desde qué estado se continúa'),
p('DEE dispone de una dinámica congelada, un instrumento de ejecución y persistencia, y una capa Cognitive que administra organizaciones con historia. Hay aprendizaje físico limitado, revisión de asociaciones, conservación, accesos alternativos, composición y actuaciones con consecuencias documentadas. Algunas funciones se utilizaron juntas en una misma trayectoria. La aplicación común no atribuye a un individuo todos los resultados de la biblioteca.'),
p('La selección personal actual es DEE20_DEMO_01, perfil fisica_directa, N67, guardada en T697764. Proviene de una importación completa y emparejada de APD05_MAIN T684418. La ficha, el snapshot y el diario coinciden: propietario detenido, paused=true y ninguna petición no terminal. No se abrió ni avanzó la vida en este análisis. El campo paused=0 del snapshot Runtime, aislado, no describe el estado del propietario externo.'),
table(['Nivel', 'Qué está acreditado'], [
('Vida actual', 'En su propia trayectoria utilizó asociaciones, comparación, memoria contextual, acumulación y operaciones sucesivas. Los últimos testigos tras reapertura son luma+ en T697678 y clasifica− en T697745. Guardar T697764 no añade otro panel.'),
('Otras trayectorias', 'APD02 y APD03 reúnen memoria, nuevas asociaciones, consultas y actuación en historias continuas. AA READY, U0, G07, OBP y Ciclo02 conservan sus sujetos y dominios; sus máximos no pasan automáticamente al actual.'),
('Plataforma', 'La biblioteca R01 contiene 101 fichas y 554 variantes o condiciones. Su verificación histórica es desigual y declarada. No son 101 facultades simultáneas ni 65 significados del ente.')], [1.15, 5.35]),
p('La edición 1.22 actualiza únicamente este documento. Se mantiene el nombre de archivo anterior para que PROYECTO.json y el lanzador sigan encontrándolo sin cambiar configuración. La copia exacta de 1.21 queda en el archivo histórico de esta revisión.'), page(), h('Qué concluye el análisis'),
p('H1 y H2 son compatibles en parte: una anatomía especializada y preparada puede sostener contenido adquirido y funciones integradas dependientes de historia. H1 explica cómo están construidos muchos aparatos; su versión extrema de etiquetas o respuestas siempre escogidas por el anfitrión no explica los controles físicos positivos. H2 está respaldada en sentido funcional acotado, en trayectorias históricas y en los usos consecutivos del descendiente actual.'),
p('H3 tiene una base concreta como problema de observación: existen variables y soportes que un lector parcial omitió y otro protocolo pudo utilizar. Justifica buscar funciones aún no medidas; no demuestra una mente general escondida. También existen convergencias físicas legítimas. Una diferencia residual sin uso no constituye memoria funcional.'),
p('El actual ofrece una distinción esclarecedora. Después de enseñar clasifica−, la señal sigue dando −; el mapa fijo interpreta ese signo como equilibra. En dos oportunidades de vigencia se eligió USE y se conservó ese signo, pero el lector de balance no produjo cifra. La asociación revisada y la utilidad de la tarea son eslabones distintos. Los registros no acreditan olvido global ni control competente.'),
p('El cierre posterior de OBP conserva plasticidad local, pero retira la necesidad de un retorno remoto concreto. AA13 iguala el sistema causal delimitado, no todos los diarios exportados. CPC9 TAIL_NO_NEW conserva consultas y omite intentos docentes. CORE16 necesita una interacción diagnóstica preparada para revelar el clock omitido. Estas correcciones conservan los positivos y cambian su explicación.'),
p('La relación con cerebro o naturaleza permanece como programa científico. Medio compartido, historia, plasticidad y acceso contextual son principios funcionales candidatos. Los 20 Hz examinados fueron calibrados con entradas externas. Las correspondencias físicas revisadas no proporcionan por sí solas validación biológica ni predicción independiente suficiente.'), page(), h('Dónde están los materiales y cómo retomar'),
p('Entrada vigente: DEE Cognitive 2.0/ABRIR_DEE_COGNITIVE.bat. Conserve el conjunto completo de sistema/estado: snapshot, identidad, interfaces, agenda, SQLite y sidecars, recibos, servicios locales y progreso de entrada. Una copia diagnóstica tiene identidad propia. T697812 pertenece a la prueba de reorganización, no al original T697764.'),
p('Snapshot actual: sistema/estado/checkpoints/DEE20_DEMO_01.T697764.c1d5bc53b25c.deetsnap.gz. SHA256: 3ad3e16b772e8ea44a7814c197651d4cb8d841c8739a1950ad2f0e6953884b8f. CONTINUIDAD_DEE_COGNITIVE_2_0.json y VIDA.json localizan el resto del par. Arrays, videos y manuales no sustituyen ese conjunto operativo.'),
p('El compendio y su ZIP siguen en la carpeta hermana CPC - Experimentos y mecanismos. Los fundamentos permanecen en las demás carpetas de documantacion vital. Los expedientes Cognitive1.1 y futuros adversos siguen en archivo. casos practicos conserva su ubicación real; no se intentó resolver su traslado bloqueado.'),
p('Registro recuperable único: ../archivo/analisis_transversal_cognitivo/REVISION_TRANSVERSAL.json, relativo a esta carpeta Cognitive. Contiene fuentes, localizadores, cobertura, recálculos, cambios de interpretación y punto exacto de reanudación. Al retomar, lea este apartado y el registro; revise de nuevo sólo las fuentes que hayan cambiado.'),
p('Siguiente paso: delimitar el enlace entre contenido conservado, observación actual, selección y efecto útil en el descendiente, contrastándolo con APD02/APD03. Primero se aprovechan las trazas existentes. Si falta una intervención discriminante, se propone una prueba futura emparejada en copias, con interfaz y criterio congelados, consecuencias omitidas y retención intercalada. No se ejecutó aquí.'),
p('Cobertura: 20 documentos Word lógicos inventariados; seis con lectura textual completa, doce parciales y dos sólo localizados. Además, 29 informes o suplementos científicos Markdown, código y primarios dirigidos. No se declara leído el corpus integral de casi seis millones de caracteres ni todas las figuras. El apéndice F y el registro precisan el alcance.'),
link('Ir al análisis causal y las tres hipótesis', 'AT_ANALISIS'), link('Ir al inventario y la cobertura de lectura', 'AT_INVENTARIO'), page()]
before(a, next(p._p for p in D.paragraphs if p.text == 'Control documental'))

b = [page(), h('39 Análisis transversal y cartografía cognitiva', 1)]; bookmark(b[-1], 'AT_ANALISIS', 9002)
b += [p('Dictamen documental del 29 de octubre de 2026. Se cruzaron fundamentos, protocolos, datos y cierres posteriores sin ejecutar el motor. La contribución positiva es una familia de mecanismos físicos que adquieren y utilizan diferencias de historia, y varias organizaciones donde esas funciones interactúan. Su alcance se determina por sujeto, interfaz, asistencia y uso observado.'), h('39 1 Tres activos y una genealogía comprobable'),
p('La plataforma ofrece mecanismos; el corpus demuestra realizaciones; la vida actual conserva su propio estado e historial de usos. La presencia de un módulo, una clave de metadata o un nombre de capacidad no acredita que su función siga accesible en cualquier fase. El kernel común permite estudiar principios compartidos, pero no fusiona recuerdos.'),
p('La línea pertinente es MA02_MAIN_5 → MU_MAIN y MU_MAIN_FASE_R3 → ASISTENTE_MAIN → APD02_MAIN → APD03_MAIN → APD04_MAIN y su semilla → APD05_MAIN → DEE20_DEMO_01. Sus continuidades identifican importaciones y bifurcaciones. MA02 nació desde T0 en N67: no es la continuación física ininterrumpida de E1_SOCIAL_11 o MA_MAIN_R9. Los futuros AUX, los controles AA y la copia de reorganización no pertenecen a la biografía actual. [AT-T, genealogía y continuidades]'),
h('39 2 Capacidades actuales y alcance temporal'),
table(['Capacidad y clase', 'Evidencia', 'Disponibilidad y asistencia'], [
('A Revisión y retención cercana al corte', 'clasifica+ → lección− → clasifica−; tras reapertura luma+ T697678 y clasifica− T697745; siete entradas aplicadas por consulta.', 'Mismo lector y forma; docencia explícita, recursos y fase preparados. No panel completo después de T697764.'),
('B Funciones ya utilizadas en esta vida', '4+5→9; 11−4→7; (4+5)−2→7; comparación, recuerda y acumulador50.', 'Código y estado incorporados; no revalidados todos al final. Árbol numérico preparado; orden y contexto del operador.'),
('B Selección sensorial y herramientas', 'a32 forma dosUSE; clasifica− selecciona equilibra; lectores numéricosNULL.', 'La selección ocurrió, pero hubo cero efectos útiles. NULL no es cero ni olvido de la señal.'),
('C Paneles antiguos de la genealogía', 'APD03 conserva14formas,6memorias y2asociaciones nuevas en su corte; APD05 aporta paneles posteriores.', 'No se comprobó aquí conservación completa después de todas las actividades DEE20. La metadata no sustituye el panel.'),
('D Otras organizaciones', 'G07/G08, U0, AA READY, recuperaciónIC01, Ciclo02, MBP/OBP yselectoresAUX.', 'Positivos de otros sujetos y dominios; no conocimientos automáticamente actuales.'),
('E Recetas y perfiles', 'Repertoire, regulación, ausencia, lector remoto y bibliotecaR01.', 'Disponibilidad de código o materiales, sin adquisición acreditada por la vida actual.'),
('F yG Acceso fallido o indeterminación', 'AA46 controla otro soporte utilizable. Otros futuros conservan huellas sin uso probado.', 'F requiere controles de contenido; G permanece cuando faltan datos. No cadaRAWdistinto es memoria.')], [1.45, 2.55, 2.5]),
p('A identifica uso documentado próximo al corte o en su ventana; B, componente incorporado sin verificación final completa; C, antecesor sin retención posterior comprobada; D, otra organización; E, código o receta; F, indicio controlado de conservación con acceso fallido; G, indeterminado. Las letras clasifican evidencia, no valor científico. [AT-ESTADO; AT-JOBS; AT-NEG]'),
h('39 3 Recorridos causales documentados'),
p('Asociación actual. Un codec fijo convierte clasifica en señal. La enseñanza admitida modifica el estado material; la misma consulta posterior, sin signo objetivo en su petición, produce el otro signo. El lector común examina36sitios prefijados y no recibe el token para escoger una respuesta favorable; la consulta aporta recursos genéricos a ambos brazos. Contenido aprendido, anatomía preparada y decodificación externa tienen papeles distintos. Después de guardar y reabrir se utiliza otra vez la asociación. [AT-JOBS; lexico_compartido_apd04.py, fixed_read/teach/query]'),
p('Consecuencia y decisión. En Ciclo02 una actuación modifica una consecuencia ambiental que retorna y cambia la referencia5→11. Ante la oportunidad común fuerza2, cambia la actuación. Los cuatro primarios dan9/9 decisiones útiles con retorno,2/9 sin retorno y2/9 sham; con acción anulada se forman salidas, pero no efectos útiles. Es función local de un comparador, actuador y ley de desgaste preparados. No se hereda por ello al actual. [AT-T, C02_GATE_050–053, data/result/rows]'),
p('Integración APD03. MAIN adquiere luma/nara, conserva usos anteriores y participa en14oportunidades de ocho objetivos: ochoACT y seisQUERY, doce útiles. En apd03_goal_4, QUERY revela13; ACT calcula28−13 yproduce15; un trabajador externo escribe el archivo de150bytes. El13 queda público en el entorno entre pasos: no es prueba de memoria numérica nativa de ese valor. Elección material, operación preparada, memoria ambiental y escritura externa participan en una misma historia. [AT-T, evento024_material, decoded_result/result/rows/0/opportunities]'),
p('Divergencia actual. a29 formaACT dos veces con dato no observado; no se ejecuta proveedor numérico yambas consecuencias sonFAILURE. a32 conserva clasifica− y selecciona equilibra mediante el mapa fijo; el balance quedaNULL yno es útil. El fallo está después o fuera del contenido léxico demostrado. No se identifica aquí una causa microscópica única delNULL ni se inventa una recuperación. [AT-NEG; percepcion_vigencia_apd05.py,L93–114; ecosistema_apd04.py,L26]'),
h('39 4 Principios comunes y dominios diferentes'),
p('Ingeniería05 separa historiaH yentradaI con cuatro condiciones ycomprueba igualdad de pares antes deI. La historia puede conservar un efecto inmediato y cambiar su propagación posterior. El recálculo de arrays archivados da131clases de respuesta para256preparacionesH1 y19para128H2. Son clases bajo ese observador y preparación, no conceptos ni puntuación de inteligencia. Ingeniería06 reutiliza entradas: FULL, omisiones yNO_NEW dan17firmasRAW+clock distintas; una omisión conservaRAW y cambiaunclock. Su soporte causal se extiende fuera de los sitios de entrada. [AT-Z Ingeniería05/06; ProcesamientoNativo caps16–21]'),
p('Las memorias móviles, relativas y distribuidas no se sustituyen por nombre. G07 utiliza dos relaciones adquiridas en encuentros sucesivos ante una nueva consulta; G08 cambia la ruta de una función mediante relay. OBP separa cambio absoluto del soporte, diferencia funcional y expresión. En MA02 una composición conservó algunas funciones y consumió accesos alfa/beta; su retorno tras docencia fue readquisición explícita. [AT-V ProcesamientoNativo yOBP; AT-T MA02]'),
p('La comunicación requiere controles de mensajes. IC01 yotros casos muestran información privada que modifica usos posteriores; sus cortes yshams conservan dominio. Emergencia conserva también un supuesto intercambioA→B→A′ que no resistió ablaciones. EnMA cierta novedad social no cambió el estado final. Un canal compatible o un intercambio aparente no bastan por sí solos. [AT-T IC01/MA; AT-V Emergencia,P60–61]'),
h('39 5 Información conservada accesible o perdida'),
p('AA46/47 es un positivo de acceso alternativo. Dos soportes adquirieron contenido inicialmente. Tras fallar la lectura habitual, una enseñanza del acceso permite utilizar el segundo sin nueva docencia del contenido. Cortar ese soporte o la enseñanza elimina la función; sham la conserva. Redundancia, iniciativa de consulta y recursos siguen preparados. Se utiliza información conservada, no se reconstruye un pasado destruido. [AT-T AA46/47]'),
p('AA13 ofrece el contrario: historias11y17 convergen conRAW/clocks, canales, pendientes, recibos y futuro común iguales. Los archivos conservan diarios distintos; no son byteidénticos ni se borró toda información del ordenador. Esos diarios no alimentan el protocolo futuro ensayado. No cabe exigir a ese sistema causal convergente respuestas distintas por el pasado. [AT-V Física§4.3; AT-T AA13]'),
p('CORE16 muestra por quéRAWpuede ser incompleto. Dos clocks distintos sobreviven conRAWigual durante11ticks; una interacción diagnóstica común instalada por el investigador revela11y10. El protocolo cambia semántica y añade soportes: no es recuperación espontánea deE1. El caso llamado topología cambió también las direcciones, por lo que no aísla sólo geometría. [AT-CORE16,cases3–6yrunnerL67–101]'),
p('Coincidir en una lectura o región no demuestra convergencia global. Diferir en algún campo tampoco demuestra significado retenido. Se distinguen conservación observable, conservación utilizable y pérdida causal. Colas y entorno pertenecen a la continuidad; un diario de auditoría no se convierte en memoria decisional sin prueba de uso.'),
h('39 6 Correcciones y autoridad temporal'),
p('OBP. Su cierre localiza la reescritura en condiciones locales y de clock. Retirar el producto remoto o su descendiente no impide el cambio; intervenciones locales sí lo alteran. Rescatar un incremento deB puede incrementar tambiénA y conservar la diferencia original. La plasticidad positiva permanece; se retira la necesidad del retorno exterior concreto. [AT-V OBP,caps27–36ytelemetría s24]'),
p('CPC9. TAIL_NO_NEW omite cuatro intentos docentes y conserva consultas;173/174frente177/178rechazos no contrasta consultar/no consultar. Los controles posteriores de protocolos intercalados y reposo tienen autoridad propia. K65 tampoco acredita65significados: el catálogo histórico registra60E0,cuatroE2yunE3 en su marco, no en la vida actual. [AT-T Retrospectiva; compendiofamilias11–12]'),
p('CORE17. Los cierres añadidos sustituyen un encabezado antiguo de noR*: sí hay cociente causalR0_FACTOR_52 en su dominio y reparación mediante otra copia previamente entrenada. Se conserva ese positivo sin convertirlo en autorregeneración o Rosetta externa. [AT-Z CORE17,EXTENSION_RESULTS yDEFINITIVE_CLOSURE]'),
p('Distribuciones. FullAPD05R01 registra error de apertura antes de evolución nativa. SuZIPno acredita que ese intento pasó. Las pruebas posteriores deDEE20 yde su copiaT697812 tienen autoridad propia. Las afirmaciones antiguas sobreACTIVO o versiones se leen en su corte; el punto inicial ylos archivos operativos fijan el uso vigente. [AT-T verificaciónFullAPD05; capítulo38]'),
h('39 7 Evaluación de H1 H2 yH3'),
table(['Hipótesis', 'Evidencia y alternativas', 'Dictamen'], [
('H1 Mecanismos especializados', 'Anatomías, lectores, calendarios y tareas finitas explican la realización. La versión fuerte de respuestas precargadas o decisiones siempre elegidas porPython contradice historias opuestas y controles físicos.', 'Explicación mecanística suficiente en muchos casos; compatible conH2. No niega contenido y usos adquiridos.'),
('H2 Organización integrada dependiente de historia', 'MA02/MU/APD yel uso actual conectan adquisición, revisión yvarias funciones. Preparación y herramientas delimitan iniciativa ygeneralización.', 'Respaldada funcionalmente por vida ydominio. No se deduce mente general o conservación de todo el corpus.'),
('H3 Organización mayor que la observada', 'Variables omitidas y acceso alternativo justifican búsqueda. La misma evidencia puede apoyarH2. Convergencias yrastros sin uso limitan atribuciones.', 'Subobservación comprobada en dominios concretos. Un alcance mental mucho mayor sigue abierto yrequiere predicciones reservadas.')], [1.4, 3.2, 1.9]),
p('Son discriminantes las historias contrastadas bajo el protocolo pertinente ylos cortes que separan soporte, ruta yuso. No discriminan por sí solosH1/H2 un resultado correcto, la preparación o compartirRuntime. Una recuperación reservada mediante acceso genérico puede apoyarH3acotada, pero no distingue automáticamente mente general de integración finita. No se asignan probabilidades inventadas.'),
h('39 8 Cerebro naturaleza ycorrespondencias'),
p('El corpus propone medio, memoria yoperador compartiendo grados físicos, con historia que altera transformaciones posteriores. Es un principio funcional investigable. Aprender, recordar, revisar otransferir son analogías útiles; obtener salidas semejantes no demuestra identidad anatómica oneurofisiológica. Una implementación diferente tampoco impide estudiar principios organizativos comunes. [AT-V Manifiesto§9 yModelo§4.10]'),
p('La unitariedad, geometría yel cierre por observadores tienen hipótesis ysectores propios. No convierten todo v27 en evolución reversible ocuántica. La afirmación de que estados distintos siempre producen futuros distintos entra en conflicto con ejemplos no inyectivos; deben prevalecer condiciones ycorrecciones posteriores. [AT-V Fundamentosoperacionales; EntrelazamientoP239–242y486–503; Física§4.3]'),
p('Los20Hz examinados utilizan velocidad ylongitud externas elegidas como entradas ylas fuentes los denominan calibración histórica, no validación biológica. Las aproximaciones aconstantes comparten anclas yajustes: en el ejemploαcitado, la diferencia relativa es de3.71ppb, pero supera24.23veces la incertidumbre citada. No es una estimación estadística global ni predicción independiente confirmada. Los teoremas de puentes asumenHDEE yla existencia de mapas compatibles; no prueban esas premisas. [AT-V FGIF,Fórmulas,Puentes yFísica; recálculoDecimal del registro]'),
p('Las correspondencias revisadas conservan valor teórico yorientan pruebas. No acreditan equivalenciaDEE–cerebro oDEE–naturaleza. Esta revisión no añadió datos externos nirellenó huecos con conocimientos generales.'),
h('39 9 Dirección de investigación'),
table(['Prioridad', 'Pregunta yantecedente', 'Resultado discriminante'], [
('1 Cerrar el enlace útil', 'Contrastar a29/a32 conAPD02/APD03: observación admitida, selección yefecto. Es el pendiente antes de ampliar vocabulario.', 'Primero trazas existentes. Prueba futura si hace falta: copias emparejadas, interfaz ycriterio fijos, retorno real/omitido, reversión de utilidad yretención. Separar ajuste monótono, bloqueo yselección contextual.'),
('2 Verificar acceso previo', 'AA46yMA02 permiten separar conservación, recuperación yreadquisición. La metadata heredada no demuestra disponibilidad actual.', 'Primera consulta reservada con contenido contrastado yacceso genérico fijado antes; cortes ysham. Si hay convergencia, estudiar conservación previa, no reconstrucción inventada.'),
('3 Formular correspondencia comprobable', 'Factoriales yobservadores sugieren principios organizativos.20Hz yotras relaciones examinadas no son validación externa.', 'Predicción ylector congelados, datos conprocedencia/calibración, controles yevaluación independiente. Un anclaje conocido no basta.')], [1.25, 2.6, 2.65]),
p('Conservar vidas, perfiles ejecutables, futuros adversos ygenealogías ha sido acertado: permite reconocer mejoras locales. Conviene corregir el crecimiento de interfaces sin contrastar acceso anterior yla mezcla de emisión válida conutilidad. Las prioridades son propuestas posteriores; ninguna se ejecutó en esta revisión.'),
h('39 10 Relevo documental'),
p('Bloques completados: identidad pasiva, fundamentos ycierres, mecanismos, trayectorias integradas, primarios actuales ycontraste de hipótesis. El registro único conserva coberturas yrecálculos. Al retomar no se repiten simulaciones niinventarios completos: se verifican sólo fuentes cambiadas yse sigue la prioridad autorizada. La lectura fue amplia ydirigida, no exhaustiva de cada copia histórica.'),
link('Volver al punto de reanudación', 'AT_REANUDACION')]
anchor = next(p._p for p in D.paragraphs if p.text.startswith('Apéndice A. Inventario histórico') and p.style.name.startswith('Heading'))
before(b, anchor)

f = [page(), h('Apéndice F Inventario documental y cobertura transversal', 1)]; bookmark(f[-1], 'AT_INVENTARIO', 9003)
f += [p('Los identificadoresAT separan esta revisión de las fuentesF/M/Rhistóricas. Rutas completas yrangos están en el registro único. Se cuentan documentos lógicos, no copias idénticas nicada archivo de telemetría. Completo significa lectura textual ytablas declaradas, sin reproducción nativa; no implica revisar visualmente todas las figuras.')]
aliases = ['Física DEE4.0.1','Manifiesto2.0','Justificación yestructura v27','Entrelazamiento detallado','Fundamentos operacionales','Fórmulas ycorrespondenciasHDEE17.1','Modelo de la realidad','PuentesHDEE','Emergencia del sistema','Física geométrica informacional2.0','Enciclopedia del investigador','Corpus integral1–7','Documento MaestroVolumen7','ComposiciónWHLv25','Procesamiento Nativo1.0','OBPv2.1','Manual Cognitive1.21 leído','Libro Blanco thinking4.5','Maestro de Arquitectura4.5','Compendio reproducibleR01']
# Etiquetas por archivo, nunca por posición de llegada del inventario.
labels = {'DEE_V4_0_1.docx':'Física DEE 4.0.1', 'DOCUMENTO MAESTRO.docx':'Documento Maestro Volumen 7', 'DEE_CORPUS_INTEGRAL_VOLUMENES_1_A_7_Y_ATLAS_COMPLETO.docx':'Corpus integral 1 a 7'}
briefs = ['Caps.1–24 y secciones dirigidas de observación y correspondencias.', 'Texto completo; marco y condiciones de investigación.', 'Texto completo; justificación y alcance v27.', 'Texto y OMML completos; salvedades sobre no inyectividad.', 'Texto completo; ecuaciones incrustadas como imágenes no revisadas.', 'Secciones de cierre, fórmulas y reinterpretación HDEE; rangos en registro.', 'Memoria, observación, correspondencia y cierre; lectura parcial.', 'Premisas y cierres de los teoremas; lectura parcial.', 'Secciones sustantivas y cierre; controles y límites.', 'Cierres V7 y correspondencias seleccionadas; parcial.', 'Aprendizaje, observación y fronteras; secciones seleccionadas.', '', '', 'Sólo censo; ABI anterior, sin lectura sustantiva.', 'Caps.1–24, apéndices y tablas completos.', 'Caps.1–36 y tablas completos, incluido cierre posterior.', 'Texto principal U0–1396 leído por equipo; apéndices históricos no releídos.', 'Caps.3,23,27–28,35–38 y60 completos; resto no revisado.', 'Arquitectura y contratos relevantes, secciones precisas en registro.', 'Frente, doce familias y síntesis U0–441; resto dirigido.']
rows=[]
for ix,x in enumerate(R['vital_document_inventory']):
    basename=Path(x['path']).name
    label=labels.get(basename,aliases[ix])
    status=x.get('status','').lower()
    state='Texto completo' if 'completo'in status or 'completamente'in status else 'Sólo localizado' if 'localiz'in status else 'Parcial'
    cov=briefs[ix]
    if basename=='DOCUMENTO MAESTRO.docx': cov='Lectura sustantiva parcial de 554 párrafos; pregunta, memoria, observación y cierres.'
    if basename=='DEE_CORPUS_INTEGRAL_VOLUMENES_1_A_7_Y_ATLAS_COMPLETO.docx': cov='Sólo censo; casi 5,9 millones de caracteres. Cuerpo no leído.'
    if cov.startswith('Texto completo; '): cov=cov[len('Texto completo; '):]
    if x['logical_id']=='V20':cov='Frente, doce familias y síntesis U0–441 completos. CatálogoJSON censado; resto delWord no leído completo.'
    rows.append(('AT-'+x['logical_id'], label, state+'; '+cov))
f += [table(['ID','Documento','Lectura real'], rows, [.75,2.2,3.55]),
p('Los textos de cada chat se consultaron en por separado. Física yProcesamientoNativo aportan causalidad, historia yaccesibilidad; OBPincluye su cierre correctivo. Las teorías distinguen resultados internos de hipótesis externas. Corpusintegral yWHLv25 permanecen sólo localizados: el primero contiene5.9millones de caracteres; el segundo pertenece aotro ABI yno decide esta pregunta cognitiva.'), h('Colecciones yexpedientes consultados'),
table(['Referencia','Lectura sustantiva','Límite'], [
('AT-Z Ingeniería05/06','Cuatro informesI05 yunoI06completos; factoriales, subconjuntos yreutilización contrastados conarrays yJSON.', 'No toda la telemetría ni Ingeniería01–04directas; éstas entran por libros yantecedentes.'),
('AT-Z Procesos01/02','Informes completos; continuidad, observadores ycontexto de interfaz.', 'Procesos03 sólo localizado. No termodinámica biológica inferida.'),
('AT-CORE16 yAT-Z CORE17','Información oculta, runner ycasos3–6; informes ycierres definitivos, cociente yrespaldo.', 'CORE01–15yrevalidaciónmaestra sólo colecciones; no todos sus primarios.'),
('AT-Z Pensamiento01/02','Tres informes completos, incluida continuación de preacondicionamiento.', 'No todos los arrays ycontinuaciones. No herencia automática aDEE20.'),
('AT-T Paisaje,Acceso,Retrospectiva','Tres informes completos; AA13/46/47, snapshots ycontroles seleccionados.', 'No cartografía total nilinajes completados por intuición.'),
('AT-T Integración yCiclo02','Dos informes ycuatro brazos primarios de consecuencias.', 'Contexto, ley yprotocolo finitos; no política general.'),
('AT-T MA,MA02,MU/FI01','Tres informes completos, retención, composición, servicios ynegativos.', 'No todas sus capacidades actualizadas automáticamente enel actual.'),
('AT-T APD01–05','Cinco informes ytres suplementosAPD04completos; dos continuidades yprimarios dirigidos.', 'Las pruebas de Full, archivos ycontenido adquirido se separan.'),
('AT-ESTADO yAT-JOBS','Ficha, snapshot ySQLite actual inmutable; once trabajos positivos ycuatro oportunidades negativas.', 'No consultas materiales nipanel completo enT697764.'),
('AT-R01','Catálogo101fichas/554condiciones ycomprobante externo delZIPexacto.', '52Native seleccionados,4parciales,4continuaciones,36recálculos,4sin nueva prueba y1instrumento; evidencia histórica no ejecutada aquí.')], [1.2,3.1,2.2]),
p('AT-T se resuelve en archivo/DEE Cognitive System 1.1. Sus fuentes individuales están en review_blocks.trajectories.sources del registro. AT-Z identifica miembrosZIPen ingenieria, procesos, cores ypensamiento; los localizadores completos están en review_blocks.mechanisms yfoundations. Las fuentes permanecen donde estaban.'), h('Fuentes actuales ylocalizadores'),
p('AT-ESTADO: PROYECTO.json; CONTINUIDAD_DEE_COGNITIVE_2_0.json; sistema/estado/vidas/DEE20_DEMO_01/VIDA.json; snapshotT697764 ymeta.owner decola.sqlite3. SQLite se leyó mode=ro&immutable=1 después de verificarWALvacío. No se abrieron servicios.'),
p('AT-JOBS: requests.id dee20_demo_clasifica_01, dee20_demo_revision_clasifica_01, dee20_demo_clasifica_post_01, dee20_demo_luma_reabierta_01 ydee20_demo_clasifica_reabierta_01; claves result/rows, reader, requests yrecibos. Losgziphistóricos permanecen en archivo/DEE_Cognitive_2_0_historial_presentacion_R01/videos/datos.'),
p('AT-NEG: requests.id dee20_demo_paso_01 → result/rows/0/opportunities; ydee20_demo_vigencia_vivir_01 → result/rows/0/rows. Se contrastaron observación pública, selección, palabra, herramienta emitida, lector yefecto. No se dedujo un pasado único desde un estado final.'),
p('AT-R01: CPC - Experimentos y mecanismos/DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip, miembroDEE_COMPENDIO_REPRODUCIBLE/CATALOGO.json. El comprobante archivo/compendio_reproducible_R01_20261029/VERIFICACION_FINAL_EXTERNA.json identifica susbytes ycobertura. Conserva intentos fallidos; el campo antiguo current_validation no prevalece sobre validation_this_release.'),
p('Los localizadores del manual1.21 se refieren ala copia exacta preservada en archivo/analisis_transversal_cognitivo/edicion_anterior. Los índicesUson párrafos del cuerpo ytablas; losPde cada revisor se definen en el registro. No se convirtieron en números de página supuestos.'), h('Cobertura ypendiente'),
p('Word:6lecturas textuales completas,12parciales y2sólo localizadas sobre20documentos lógicos. Markdowncientífico:29informes osuplementos completos. Código, continuidades yprimarios se contabilizan aparte. No se encontró una fuente inaccesible entre las intentadas; las colecciones localizadas no se presentan como leídas.'),
p('No se revisaron visualmente todas las figuras originales. Fundamentosoperacionales contiene ecuaciones enimagen no leídas. Tampoco se leyó completo elCorpusintegral, todaslas versiones2.2–4.0, compilaciones ocadamiembro delarchivo. El registro conserva los rangos reales ylo pendiente, sin sustituir una fuente necesaria por una conclusión inventada.'),
p('Al retomar, conserve este corte yresuelva la primera prioridad del capítulo39 según la autorización del siguiente trabajo. Esta edición no incorpora mecanismos al producto, no promueveotra vida yno modifica aprendizajes.'), link('Volver al punto de reanudación','AT_REANUDACION')]
index = next(p._p for p in D.paragraphs if p.text == 'Índice de consulta')
entries=[link('Punto de reanudación y estado vigente','AT_REANUDACION'),link('39 Análisis transversal y cartografía cognitiva','AT_ANALISIS'),link('Apéndice F Inventario y lectura','AT_INVENTARIO')]
after(entries, index)
# Revisión de prosa únicamente en los elementos nuevos.
def polish(text):
    repl={
      'H1 y H2 son compatibles en parte: una anatomía especializada y preparada puede sostener contenido adquirido y funciones integradas dependientes de historia. H1 explica cómo están construidos muchos aparatos; su versión extrema de etiquetas o respuestas siempre escogidas por el anfitrión no explica los controles físicos positivos. H2 está respaldada en sentido funcional acotado, en trayectorias históricas y en los usos consecutivos del descendiente actual.':
      'Las pruebas respaldan integración funcional acotada (H2), realizada mediante mecanismos especializados que H1 también puede explicar. Historias contrastadas e intervenciones identifican contenido adquirido dentro de esas preparaciones. No se ha demostrado que todos los resultados requieran un mecanismo integrador general, ni que la coordinación instrumental haya sido aprendida. La especialización no invalida el aprendizaje físico.',
      'Anatomías, lectores, calendarios y tareas finitas explican la realización. La versión fuerte de respuestas precargadas o decisiones siempre elegidas porPython contradice historias opuestas y controles físicos.':
      'Anatomías, lectores, calendarios y tareas finitas explican muchas realizaciones, incluido aprendizaje dentro de mecanismos especializados. Los controles delimitan el aporte de la experiencia y del anfitrión, sin refutar por sí solos H1.',
      'yestado':'y estado','ycartografía':'y cartografía','ylectura':'y lectura','ycorrespondencias':'y correspondencias','yestructura':'y estructura','ypendiente':'y pendiente','yproduce':'y produce','yproduce15':'y produce 15','yclock':'y clock','yrevalidación':'y revalidación','ytelemetría':'y telemetría','ytransformación':'y transformación','yresultado':'y resultado','ylector':'y lector','ycódigo':'y código','ycobertura':'y cobertura','yconservación':'y conservación','yselección':'y selección','yactual':'y actual','yoperador':'y operador','yobservadores':'y observadores','yobservación':'y observación','yprimarios':'y primarios','yfuentes':'y fuentes','yregistros':'y registros','yrangos':'y rangos','ycomparación':'y comparación','ycondiciones':'y condiciones','ycontrol':'y control','ysham':'y sham','yretención':'y retención','yrecursos':'y recursos','ysoporte':'y soporte','yfunción':'y función','yversiones':'y versiones','yclases':'y clases','ysemántica':'y semántica','yentorno':'y entorno','yefecto':'y efecto','yplataforma':'y plataforma','yoperaciones':'y operaciones','ysu ':'y su ','ysus ':'y sus ','yel ':'y el ','ylos ':'y los ','ylas ':'y las ','yla ':'y la ','yse ':'y se ','yno ':'y no ','yotras':'y otras','yotros':'y otros','yde ':'y de ','yuna ':'y una ','yun ':'y un ','yen ':'y en ','conarrays':'con arrays','conRAW':'con RAW','conJSON':'con JSON','coninterfaces':'con interfaces','coninterfaz':'con interfaz','conprocedencia':'con procedencia','completo':'completo','cadamiembro':'cada miembro','todaslas':'todas las','todoel':'todo el','delarchivo':'del archivo','delNULL':'del NULL','ala copia':'a la copia','aotro ':'a otro ','asu ':'a su ','enimagen':'en imagen','noes ':'no es ','nuevocómputo':'nuevo cómputo','niel ':'ni el ','niinventarios':'ni inventarios','nicada ':'ni cada ','nirellenó':'ni rellenó','nipanel ':'ni panel ','nilinajes':'ni linajes','neurofisiológica':'neurofisiológica','oneurofisiológica':'o neurofisiológica','ocuántica':'o cuántica','otransferir':'o transferir','osuplementos':'o suplementos','ocadamiembro':'o cada miembro','Física§':'Física §','Manifiesto§':'Manifiesto §','Modelo§':'Modelo §','CPC9TAIL':'CPC9 TAIL','FullAPD05R01':'Full APD05 R01','deDEE20':'de DEE20','aDEE20':'a DEE20','deE1':'de E1','conH2':'con H2','H3acotada':'H3 acotada','CORE01–15yrevalidaciónmaestra':'CORE01–15 y revalidación maestra','Ingeniería01–04directas':'Ingeniería01–04 directas','Procesos03 sólo':'Procesos03 sólo','Word:6':'Word: 6','Markdowncientífico':'Markdown científico','elCorpusintegral':'el Corpus integral','Corpusintegral':'Corpus integral','Fundamentosoperacionales':'Fundamentos operacionales','20Hz':'20 Hz','3.71ppb':'3,71 ppb','24.23veces':'24,23 veces','5.9millones':'5,9 millones','cambiaunclock':'cambia un clock','da131clases':'da 131 clases','para256preparaciones':'para 256 preparaciones','y19para128H2':'y 19 para 128 H2','examina36sitios':'examina 36 sitios','reader36':'reader 36','cuatroE2yunE3':'cuatro E2 y un E3','dosUSE':'dos USE','ochoACT':'ocho ACT','seisQUERY':'seis QUERY','ambas consecuencias sonFAILURE':'ambas consecuencias son FAILURE','formaACT':'forma ACT','balance quedaNULL':'balance queda NULL','RAWpuede':'RAW puede','RAWigual':'RAW igual','casos3–6':'casos 3–6','cases3–6yrunner':'cases 3–6 y runner','P239–242y486–503':'P239–242 y 486–503','antes deI':'antes de I','historiaH yentradaI':'historia H y entrada I','APD02/APD03:':'APD02/APD03:','AT-V ProcesamientoNativo yOBP':'AT-V15 y AT-V16','AT-V OBP':'AT-V16 OBP','AT-V Física':'AT-V01 Física','AT-V Emergencia':'AT-V09 Emergencia','AT-V Manifiesto':'AT-V02 Manifiesto','AT-V Fundamentosoperacionales':'AT-V05 Fundamentos operacionales'
    }
    for word in ['accesibilidad','ajustes','ambas','cierres','comprueba','contraste','correcciones','dirigida','expedientes','foundations','genealogías','localizadores','longitud','meta','orientan','pensamiento','recibos','recálculos','resuelva','sectores','tablas','antecedente','cobertura','protocolos','continuidad','rutas','resultados','progreso','campos','aprendizaje','datos','decisiones','capítulos']:
        repl['y'+word]='y '+word
    for word in ['DEE','DEFINITIVE_CLOSURE','Física','H3','Modelo','NO_NEW','ProcesamientoNativo','WHLv25','RAW','JSON','CORE17','CORE16','OBP','APD03']:
        repl['y'+word]='y '+word
    repl['oDEE']='o DEE'
    repl['Cognitive1.1']='Cognitive 1.1'
    for a,b in sorted(repl.items(),key=lambda x:-len(x[0])): text=text.replace(a,b)
    text=re.sub(r'(?<=\d)(?=(?:lecturas|parciales|sólo|documentos|informes|formas|memorias|asociaciones|sitios|clases|preparaciones|para|frente|bytes|decisiones|fichas|condiciones|protocolos|continuaciones|recálculos|sin|instrumento|oportunidades|textuales|con|Native)\b)',' ',text)
    for old, new in [
        ("acumulador50", "acumulador 50"),
        ("numéricosNULL", "numéricos NULL"),
        ("conserva14 formas,6 memorias y2 asociaciones", "conserva 14 formas, 6 memorias y 2 asociaciones"),
        ("recuperaciónIC01", "recuperación IC01"),
        ("yselectoresAUX", "y selectores AUX"),
        ("bibliotecaR01", "biblioteca R01"),
        ("F yG", "F y G"),
        ("cadaRAWdistinto", "cada RAW distinto"),
        ("referencia5→11", "referencia 5→11"),
        ("fuerza2", "fuerza 2"),
        ("dan9/9", "dan 9/9"),
        ("retorno,2/9", "retorno, 2/9"),
        ("y2/9 sham", "y 2/9 sham"),
        ("en14 oportunidades", "en 14 oportunidades"),
        ("revela13", "revela 13"),
        ("calcula28−13", "calcula 28−13"),
        ("de150 bytes", "de 150 bytes"),
        ("El13", "El 13"),
        ("preparacionesH1", "preparaciones H1"),
        ("dan17firmasRAW+clock", "dan 17 firmas RAW+clock"),
        ("conservaRAW", "conserva RAW"),
        ("ProcesamientoNativo caps16–21", "Procesamiento Nativo caps. 16–21"),
        ("intercambioA→B→A′", "intercambio A→B→A′"),
        ("EnMA", "En MA"),
        ("Emergencia,P60–61", "Emergencia, P60–61"),
        ("historias11y17", "historias 11 y 17"),
        ("quéRAW", "qué RAW"),
        ("durante11ticks", "durante 11 ticks"),
        ("revela11y10", "revela 11 y 10"),
        ("runnerL67–101", "runner L67–101"),
        ("deB", "de B"),
        ("tambiénA", "también A"),
        ("OBP,caps27–36y telemetría", "OBP, caps. 27–36 y telemetría"),
        (";173/174frente177/178rechazos", "; 173/174 frente a 177/178 rechazos"),
        ("acredita65significados", "acredita 65 significados"),
        ("registra60E0,cuatro", "registra 60 E0, cuatro"),
        ("compendiofamilias11–12", "compendio, familias 11–12"),
        ("noR*", "no R*"),
        ("causalR0_FACTOR_52", "causal R0_FACTOR_52"),
        ("CORE17,EXTENSION_RESULTS", "CORE17, EXTENSION_RESULTS"),
        ("SuZIPno", "Su ZIP no"),
        ("copiaT697812", "copia T697812"),
        ("sobreACTIVO", "sobre ACTIVO"),
        ("verificaciónFullAPD05", "verificación Full APD05"),
        ("capítulo38", "capítulo 38"),
        ("yvarias", "y varias"),
        ("ygeneralización", "y generalización"),
        ("ydominio", "y dominio"),
        ("apoyarH2", "apoyar H2"),
        ("yrastros", "y rastros"),
        ("yrequiere", "y requiere"),
        ("yuso", "y uso"),
        ("solosH1/H2", "solos H1/H2"),
        ("compartirRuntime", "compartir Runtime"),
        ("apoyarH3", "apoyar H3"),
        ("EntrelazamientoP239–242", "Entrelazamiento P239–242"),
        ("Los20 Hz", "Los 20 Hz"),
        ("aconstantes", "a constantes"),
        ("ejemploαcitado", "ejemplo α citado"),
        ("de3,71 ppb", "de 3,71 ppb"),
        ("supera24,23 veces", "supera 24,23 veces"),
        ("asumenHDEE", "asumen HDEE"),
        ("FGIF,Fórmulas,Puentes", "FGIF, Fórmulas, Puentes"),
        ("recálculoDecimal", "recálculo Decimal"),
        ("equivalenciaDEE", "equivalencia DEE"),
        ("conAPD02/APD03", "con APD02/APD03"),
        ("ycriterio", "y criterio"),
        ("AA46yMA02", "AA46 y MA02"),
        ("yreadquisición", "y readquisición"),
        ("yacceso", "y acceso"),
        ("organizativos.20 Hz", "organizativos. 20 Hz"),
        ("yevaluación", "y evaluación"),
        ("conutilidad", "con utilidad"),
        ("sustituy en", "sustituyen"),
        ("identificadoresAT", "identificadores AT"),
        ("fuentesF/M/Rhistóricas", "fuentes F/M/R históricas"),
        ("DEE4.0.1", "DEE 4.0.1"),
        ("Manifiesto2.0", "Manifiesto 2.0"),
        ("correspondenciasHDEE17.1", "correspondencias HDEE 17.1"),
        ("PuentesHDEE", "Puentes HDEE"),
        ("informacional2.0", "informacional 2.0"),
        ("integral1–7", "integral 1–7"),
        ("MaestroVolumen7", "Maestro Volumen 7"),
        ("ComposiciónWHLv25", "Composición WHL v25"),
        ("Nativo1.0", "Nativo 1.0"),
        ("OBPv2.1", "OBP v2.1"),
        ("Cognitive1.21", "Cognitive 1.21"),
        ("thinking4.5", "thinking 4.5"),
        ("Arquitectura4.5", "Arquitectura 4.5"),
        ("reproducibleR01", "reproducible R01"),
        ("Caps.1–24", "Caps. 1–24"),
        ("Caps.1–36", "Caps. 1–36"),
        ("Caps.3,23,27–28,35–38 y60", "Caps. 3, 23, 27–28, 35–38 y 60"),
        ("en por separado", "por separado"),
        ("yProcesamientoNativo", "y Procesamiento Nativo"),
        ("OBPincluye", "OBP incluye"),
        ("fuentesF/M/R", "fuentes F/M/R"),
        ("contiene5,9 millones", "contiene 5,9 millones"),
        ("informesI05 yunoI06completos", "informes I05 y uno I06 completos"),
        ("yJSON", "y JSON"),
        ("ycontexto", "y contexto"),
        ("yAT-Z", "y AT-Z"),
        ("yrespaldo", "y respaldo"),
        ("CORE01–15 y revalidaciónmaestra", "CORE01–15 y revalidación maestra"),
        ("ycontinuaciones", "y continuaciones"),
        ("yCiclo02", "y Ciclo02"),
        ("ycuatro", "y cuatro"),
        ("ynegativos", "y negativos"),
        ("enel actual", "en el actual"),
        ("ytres suplementosAPD04completos", "y tres suplementos APD04 completos"),
        ("ycontenido", "y contenido"),
        ("yAT-JOBS", "y AT-JOBS"),
        ("ySQLite", "y SQLite"),
        ("enT697764", "en T697764"),
        ("Catálogo101 fichas/554 condiciones", "Catálogo 101 fichas/554 condiciones"),
        ("delZIPexacto", "del ZIP exacto"),
        ("52Native", "52 Native"),
        (",4 parciales", ", 4 parciales"),
        (",4 continuaciones", ", 4 continuaciones"),
        (",36 recálculos", ", 36 recálculos"),
        (",4 sin", ", 4 sin"),
        ("y1 instrumento", "y 1 instrumento"),
        ("miembrosZIPen", "miembros ZIP en"),
        ("snapshotT697764", "snapshot T697764"),
        ("ymeta.owner", "y meta.owner"),
        ("decola.sqlite3", "de cola.sqlite3"),
        ("verificarWALvacío", "verificar WAL vacío"),
        ("ydee20", "y dee20"),
        ("Losgziphistóricos", "Los gzip históricos"),
        ("miembroDEE_COMPENDIO", "miembro DEE_COMPENDIO"),
        ("susbytes", "sus bytes"),
        ("manual1.21", "manual 1.21"),
        ("índicesUson", "índices U son"),
        ("losPde", "los P de"),
        (",12 parciales", ", 12 parciales"),
        ("y2 sólo", "y 2 sólo"),
        ("sobre20 documentos", "sobre 20 documentos"),
        ("científico:29 informes", "científico: 29 informes"),
        ("versiones2.2–4.0", "versiones 2.2–4.0"),
        ("capítulo39", "capítulo 39"),
        ("promueveotra", "promueve otra"),
        ("byteidénticos", "idénticos byte por byte"),
        ("dosUSE", "dos USE"),
        ("yentre", "y entre"),
        ("CatálogoJSON", "Catálogo JSON"),
        ("delWord", "del Word"),
        ("ProcesamientoNativo", "Procesamiento Nativo"),
        ("yreutilización", "y reutilización"),
        ("ycasos", "y casos"),
        ("Paisaje,Acceso,Retrospectiva", "Paisaje, Acceso, Retrospectiva"),
        ("yprotocolo", "y protocolo"),
        ("MA,MA02,MU/FI01", "MA, MA02, MU/FI01"),
        ("ycomprobante", "y comprobante"),
        ("ylo pendiente", "y lo pendiente"),
    ]:
        text = text.replace(old, new)
    text = text.replace('Los textos de cada chat se consultaron por separado.', 'Las fuentes documentales se consultaron por separado.')
    return text
for element in a+b+f:
    for t in element.iter(qn('w:t')):
        if t.text: t.text=polish(t.text)
# Recuperar el positivo de bucles nativos finitos, con su sujeto propio.
target=next(x for x in D.paragraphs if x.text.startswith('La comunicación requiere controles'))
extra=target.insert_paragraph_before('Pensamiento01 y Pensamiento02 documentan cadenas nativas finitas donde una respuesta participa en interacciones posteriores y dos usos ambientales consecutivos, sin escrituras del anfitrión después de T0. Los reactivos y las rutas estaban preinstalados. Es un logro de esas organizaciones, sin herencia automática hacia el actual ni provisión indefinida de recursos. Autoridad: tres informes completos leídos; sus arrays no se recalcularon aquí. [AT-Z Pensamiento01/02]')
for r in extra.runs:r.font.name='Calibri';r.font.size=Pt(11)
D.core_properties.revision = 22
for paragraph in D.paragraphs:
    if 'Su edición vigente 1.21' in paragraph.text:
        for run in paragraph.runs:
            run.text = run.text.replace('Su edición vigente 1.21', 'Su edición vigente 1.22')
D.core_properties.modified = datetime.now(timezone.utc)
D.save(TARGET)
R['manual_update']={'candidate':str(TARGET),'original':str(SOURCE),'original_sha256':hashlib.file_digest(SOURCE.open('rb'),'sha256').hexdigest(),'edition':'1.22','filename_kept_for_existing_launcher':True,'product_version_unchanged':True,'new_content':['Punto de reanudación','Capítulo39','ApéndiceF'],'render_status':'pendiente'}
R['resume'].update(current_block='CandidatoWord1.22creado; pendiente render yrevisión visual',next_block='Renderizar todaslaspáginas ypublicar enmismaruta alvalidar')
REG.write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('CANDIDATE',TARGET,'bytes',TARGET.stat().st_size,'paragraphs',len(D.paragraphs),'tables',len(D.tables))
