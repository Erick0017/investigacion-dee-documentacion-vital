"""Edición documental R02. Sólo python-docx y biblioteca estándar; no importa DEE."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, shutil
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_BREAK
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

W=Path(__file__).resolve().parent
ROOT=W.parent.parent
PRODUCT=ROOT/'DEE Cognitive 2.0'
NAME='DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
REG=W/'REVISION_TRANSVERSAL.json'
R=json.loads(REG.read_text(encoding='utf8'))
BACKUP=W/'edicion_anterior'/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_22.docx'
SOURCE=PRODUCT/NAME
if not BACKUP.exists(): shutil.copyfile(SOURCE,BACKUP)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==hashlib.sha256(BACKUP.read_bytes()).hexdigest()
D=Document(BACKUP)

def para(text,heading=None):
    p=D.add_paragraph(text,style='Heading '+str(heading) if heading else None)
    for r in p.runs:
        r.font.name='Calibri'; r.font.color.rgb=RGBColor(0,0,0)
        if not heading:r.font.size=Pt(11)
    p.paragraph_format.space_after=Pt(7)
    if heading:p.paragraph_format.keep_with_next=True
    return p._p
def page():
    p=D.add_paragraph();p.add_run().add_break(WD_BREAK.PAGE);return p._p
def bookmark(e,name,idx):
    a=OxmlElement('w:bookmarkStart');a.set(qn('w:id'),str(idx));a.set(qn('w:name'),name)
    b=OxmlElement('w:bookmarkEnd');b.set(qn('w:id'),str(idx));e.insert(0,a);e.append(b)
def link(text,anchor):
    p=D.add_paragraph();a=OxmlElement('w:hyperlink');a.set(qn('w:anchor'),anchor)
    r=OxmlElement('w:r');t=OxmlElement('w:t');t.text=text;r.append(t);a.append(r);p._p.append(a);return p._p
def table(headers,rows,widths):
    t=D.add_table(rows=1,cols=len(headers));t.style='Table Grid';t.autofit=False
    for i,x in enumerate(headers):t.rows[0].cells[i].text=x
    rep=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(rep)
    for row in rows:
        for c,x in zip(t.add_row().cells,row):c.text=str(x)
    for ix,row in enumerate(t.rows):
        ns=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(ns)
        for i,c in enumerate(row.cells):
            c.width=Inches(widths[i]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            pr=c._tc.get_or_add_tcPr();sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'173B4F' if ix==0 else ('EFF3F6' if ix%2 else 'FFFFFF'));pr.append(sh)
            margins=OxmlElement('w:tcMar')
            for side in ['top','left','bottom','right']:
                el=OxmlElement('w:'+side);el.set(qn('w:w'),'85');el.set(qn('w:type'),'dxa');margins.append(el)
            pr.append(margins)
            for p in c.paragraphs:
                p.paragraph_format.space_after=Pt(3)
                if ix==0:p.paragraph_format.keep_with_next=True
                for r in p.runs:
                    r.font.name='Calibri';r.font.size=Pt(9.5);r.bold=ix==0
                    r.font.color.rgb=RGBColor(255,255,255) if ix==0 else RGBColor(0,0,0)
    borders=OxmlElement('w:tblBorders')
    for edge in ['top','left','bottom','right','insideH','insideV']:
        x=OxmlElement('w:'+edge);x.set(qn('w:val'),'single');x.set(qn('w:sz'),'4');x.set(qn('w:color'),'D9D9D9');borders.append(x)
    t._tbl.tblPr.append(borders)
    return t._tbl
def replace_range(start,end,new):
    body=D.element.body
    children=list(body);a=children.index(start);b=children.index(end) if end is not None else len(children)-1
    for e in children[a:b]:body.remove(e)
    for e in new:end.addprevious(e) if end is not None else body.insert(len(body)-1,e)
def find(text):return next(p._p for p in D.paragraphs if p.text==text and p.style.name.startswith('Heading'))

# Punto de reanudación breve, en el mismo lugar lógico.
start=find('Punto de reanudación')
end=next(p._p for p in D.paragraphs if p.text=='Control documental')
front=[para('Punto de reanudación',1)];bookmark(front[0],'AT_REANUDACION',9001)
front += [para('Corte documental R02 del 30 de octubre de 2026. La organización seleccionada sigue siendo DEE20_DEMO_01, N67, guardada en T697764, descendiente de APD05_MAIN mediante importación completa emparejada. El snapshot y los otros nueve archivos operativos protegidos coinciden con R01. La caché del propietario describe su corte guardado; la consulta de procesos del 30 de octubre es una observación fechada, no una garantía permanente de inactividad.'),
para('Los registros muestran asociaciones adquiridas que seleccionan operaciones nativas y una composición efectiva: el 9 producido por 4+5 alimenta 9−2 y resulta 7. El orden lo ofrece el operador; los algoritmos aritméticos están preparados. La revisión propia de clasifica a signo negativo y la asociación luma positiva se utilizaron después de reabrir. No se hicieron consultas nuevas para ampliar ese panel.'),
para('La continuación aclara dos fallos. En a29 se admitió el indicador de información ausente y retornaron las dos consecuencias de fallo, pero el selector volvió a actuar sin obtener el dato. En a32 la asociación revisada siguió seleccionando equilibra; apareció una emisión intermedia y faltó la lectura final. Ese protocolo omitía expresamente el retorno R04: no ensayó aprender de esas dos consecuencias.'),
para('Las fuentes antiguas añaden controles de memoria distribuida, acceso dependiente del tiempo, transporte de funciones y selección modificada por consecuencias. Sus sujetos y versiones permanecen separados. H1 y H2 siguen siendo compatibles: mecanismos especializados sostienen integración funcional acotada. H3 se concreta como búsqueda de funciones omitidas por observadores y horizontes, sin postular grados físicos adicionales ni una mente general oculta.'),
para('Siguiente prioridad: delimitar el dominio de discriminación del selector compartido y la frontera neutra del lector. Primero se usan los primarios ya localizados. Una comprobación causal nueva, si se autoriza en otro encargo, deberá fijar interfaz, horizonte y lector antes de evaluar, con controles emparejados. En esta revisión hubo cero ticks, enseñanza, reproducciones o cambios operativos.'),
para('La edición interna es 1.23 y conserva el nombre físico Edicion_1_21.docx para mantener las referencias del lanzador. El capítulo 39 contiene las cadenas y capacidades; el apéndice F precisa lectura y pendientes. El único registro vigente sigue en ../archivo/analisis_transversal_cognitivo/REVISION_TRANSVERSAL.json, sección continuation_R02. La edición 1.22 y el registro R01 quedan respaldados en esa área.'),
link('Ir al análisis causal y las tres hipótesis','AT_ANALISIS'),link('Ir al inventario y la cobertura de lectura','AT_INVENTARIO'),page()]
replace_range(start,end,front)

# Actualización íntegra del capítulo39; los capítulos históricos1–38 se preservan.
start=find('39 Análisis transversal y cartografía cognitiva')
end=find('Apéndice A. Inventario histórico de las 73 entradas')
c=[para('39 Análisis transversal y cartografía cognitiva',1)];bookmark(c[0],'AT_ANALISIS',9002)
c += [para('R02 conserva los positivos de R01 y precisa sus enlaces. La evidencia reúne aprendizaje físico de contenidos, uso de relaciones y composición en trayectorias identificadas. También muestra que compartir una referencia puede facilitar una función y sesgar otra. El repertorio de la plataforma, los experimentos históricos y los conocimientos de una vida se describen por separado.'),
para('39 1 Organización y genealogía',2),
para('DEE20_DEMO_01 es una organización compuesta en un mundo N67. Su línea pertinente es MA02_MAIN_5 → MU_MAIN y MU_MAIN_FASE_R3 → ASISTENTE_MAIN → APD02_MAIN → APD03_MAIN → APD04_MAIN y su semilla → APD05_MAIN → DEE20_DEMO_01. MA02 nació desde T0; esta línea no es la biografía física de E1_SOCIAL_11, MA_R9, U0, G07/G08, AA_READY o Ciclo02. Una importación completa conserva su padre declarado; una receta compartida no fusiona historias.'),
para('La anatomía incorpora soportes léxicos, comparación, rutas de selección, agregación numérica, interfaces y recursos. El anfitrión ofrece oportunidades, transporta resultados y ejecuta actuadores/evaluadores declarados. El contenido de una asociación y varias salidas se obtienen de la evolución DEE. Ni el diario de auditoría ni el catálogo se utilizan como memoria del participante. [AT-ESTADO; R02-TRAJECTORIES; R02-APD02-COMPOSE]'),
para('39 2 Capacidades y contenidos documentados',2),
para('La matriz conserva dimensiones distintas. Código y preparación indican disponibilidad de mecanismo; adquisición identifica la historia del contenido; último uso y conservación se apoyan en testigos fechados. El snapshot final T697764 no es una consulta de todo su repertorio. La matriz detallada de once filas queda en continuation_R02.blocks.trajectories.capability_content_matrix.'),
table(['Contenido y preparación','Adquisición y último uso','Uso conjunto y conservación','Asistencia y disponibilidad en el corte'],[
('clasifica; lector común36 incorporado','Revisión propia a − en T688964; último lector − T697742, tras reapertura.','El mismo signo selecciona equilibra en a32. Retención de la asociación acreditada; balance sin salida útil.','Consulta, recursos, fase y traducción signo→herramienta preparados. Uso cercano al corte; no panel nuevo en T697764.'),
('luma y nara; léxico incorporado','Adquiridas en APD03. luma+ T697675; nara− T689970.','Consultas intercaladas con revisión y operaciones de esta misma vida. luma se conserva tras reapertura.','Asociaciones funcionales en su protocolo. Función completa de luma y retención posterior de nara sin testigo final equivalente.'),
('suma, diferencia y secuencia numérica','Asociaciones heredadas; aritmética preparada. Lecturas 9 T690332 y 7 T691896; secuencia termina T693258.','Palabra→operación y ruta→proveedor; el 9 real pasa al segundo cálculo. Cuatro llamadas Native y ninguna externa.','Operador fija orden y datos; codec, escritor y evaluación preparados. Uso propio comprobado, no algoritmo ni plan aprendidos.'),
('compara, recuerda y contexto alfa','Relaciones heredadas; lectores T688630/T688697, cierres T688649/T688767.','Se usaron en esta trayectoria junto a aritmética y antes de revisar clasifica.','Contexto alfa, valor27 e iniciativa del operador. Disponibilidad final de todos los contextos no determinada.'),
('acumulador y mantenimiento','Referencia heredada; incremento3, salida50; petición termina T688906.','Uso intercalado con memoria y revisión. No hay otra prueba final del acumulador.','Recirculación, renovación y calendario P0. Su uso anterior no demuestra mantenimiento iniciado por E1.'),
('selector R04 y ACT/QUERY','Historia previa de referencias; a29 modifica diferencia4→3→2. ACT vuelve a T694967.','Comparte selector con elección de proveedor aritmético. El retorno llega, pero no obtiene el dato ausente en dos oportunidades.','Oportunidad y codec fijos. Actuación nativa y cambio de estado, sin mejora útil demostrada en ese tramo.'),
('vigencia, USE y balance','Referencia comparativa20 heredada y clasifica revisada. USE formado; balance sin candidato a T697204.','Sensor→consulta léxica→herramienta en el mismo mundo. Hay transformación intermedia y contenido conservado.','Sensor de versiones, caché y herramientas preparados. El modo vigencia no entrega retorno R04; cadena útil incompleta.'),
], [1.35,1.65,1.75,1.75]),
para('Los paneles de APD03/APD05 son antecedentes de esta genealogía, con sus últimos ticks y pérdidas propios. La comunicación, la recuperación alternativa y otras funciones de AA, CORE o Ciclo02 se mantienen como resultados de sus sujetos, o como componentes candidatos cuando no hay un uso acreditado en DEE20. La ausencia de un testigo actual deja una celda indeterminada, sin convertirla en pérdida ni en capacidad poseída. [Matriz detallada R02; apéndices históricos A–C]'),
para('39 3 a29 y la selección compartida',2),
para('La petición dee20_demo_paso_01 contiene dos oportunidades. La forma suma emite + en T693387 y T694861. El indicador público de ausencia tiene valor1 y sus entradas se aplican; el selector emite ACT− en T693403 y T694967. El entorno exige el segundo operando, que sigue sin observarse, y registra ACT_FAILED_MISSING_OBSERVATION. No se llama al proveedor numérico. El primer fallo funcional localizado está en actuar antes de obtener el dato, con sensor admitido y selección formada.'),
table(['Oportunidad','Referencias y retorno registrado','Resultado posterior'],[
('1','Referencias antes735/739. Tres pulsos FAILURE aplicados en T694805. Primer frame de retorno738/742; en T694808 izquierda739.','Diferencia B−A pasa4→3; la siguiente oportunidad vuelve ACT.'),
('2','Referencias antes739/742. Tres pulsos FAILURE aplicados en T696369. Primer frame742/745; en T696372 izquierda743.','Diferencia3→2 al cierre. No hubo una tercera oportunidad evaluada.'),
], [0.65,3.15,2.7]),
para('Se aplicaron48/48 entradas contabilizadas del episodio, incluidos6 pulsos de consecuencia. Ambas referencias ya habían aumentado3 antes del primer frame de cada ventana de retorno. No se atribuye toda esa deriva al feedback: falta observación local continua entre la lectura y boundary−3. El registro sí acredita recepción del retorno y transformación posterior, sin cambio útil dentro de las dos oportunidades.'),
para('El diferencial4 ya aparecía en operaciones útiles de la misma vida, donde la ruta negativa elegía el proveedor nativo. En auxiliares históricos APD03, diferencias0/1 y observaciones raw0/raw1 sí separaban QUERY/ACT bajo el mismo esquema de sensor. Es compatible con un sesgo adquirido que deja al indicador actual fuera del intervalo de discriminación. Esos auxiliares cambian historia y edad; no son controles emparejados de a29. Falta el contraste causal del mismo prefijo con intervención selectiva y sham, además del contexto del encuentro. [R02-A29; APD03_historical_comparison; fuentes y recibos exactos en el registro]'),
para('39 4 a32 y la frontera neutra de lectura',2),
para('En dee20_demo_vigencia_vivir_01 se forman dos USE. La consulta de clasifica conserva −, y TOOL_CODEC[-1] selecciona fijamente equilibra. Los balances reciben cargas[7,7], codificadas como[7,13] y126 ceros, con agregado20. Se admiten los176 aportes de cada frame. Contando sensores, balances y consultas léxicas, se aplicaron718/718 entradas: admitirlas no garantiza un resultado útil.'),
para('La diferencia entre referencias permanece20. En q+4 aparece en E una contribución de carga5, dirección[0,1,−1], y el agregado20 se observa en S. En q+6 no hay candidato en los seis sitios del lector final. Se localiza transformación física antes de una lectura vacía; no una respuesta funcional0. Falta q+5 y la vecindad de esa ruta para identificar el encuentro que elimina, desvía o transforma la contribución. La referencia y el signo léxico conservados no equivalen a acceso operativo completo.'),
para('El negativo tiene antecedentes concretos: APD04 REF_OMIT con agregado20 y referencias1487/1507 ya produjo esa firma intermedia y lector vacío; REF_A con diferencia21 produjo − y REF_B con diferencia19 produjo +. Los datos y las historias no son idénticos a a32, pero el antecedente restringe una explicación basada sólo en deterioro reciente. Un panel APD05 anterior también registró lectura vacía en el punto20 y signos válidos a ambos lados.'),
para('El enlace de aprendizaje por consecuencia estaba ausente por protocolo. El primario declara native_consequence_delivered=false; percepcion_vigencia_apd05.py omite R04 aunque la petición exterior indique retorno=real. ecosistema_apd04.live sí utiliza sensor.finish en otro dominio. Por ello a32 no demuestra un intento fallido de adaptación mediante ese retorno. Conservó una asociación y ejecutó parte de la cadena; no obtuvo efecto útil ni recibió esa consecuencia material. [R02-A32; R02_A32_NO_RETURN; APD04_neutral_boundary_comparison]'),
para('39 5 Aportes de las fuentes pendientes',2),
para('El Corpus Integral aporta pruebas de soporte distribuido con versiones propias. MEMORYEPISTASIS231X, v25-LAZY N64, compara83 intervenciones archivadas: el conjunto de32 sitios state reproduce el fenotipo de supresión y revertirlo elimina esa diferencia. Sólo2/32 escrituras individuales bastan;32/32 trasplantes de subconjuntos de31/32 sitios reproducen la supresión en controles envejecidos. Es degeneración del soporte en esa preparación, no32 bits independientes. Los trasplantes eran diagnósticos externos. El volumen4 documenta migración temporal del soporte y reversión global controlada. No son recuerdos atribuidos al descendiente v27. [R02-FOUNDATIONS, Corpus y primarios]'),
para('Ingeniería02 separa contenido y acceso: historias AB/BA con clocks iniciales iguales en los dos soportes y eventos de carga cero escriben diferencias relativas opuestas; cortar la ruta puede conservar la memoria y eliminar la respuesta. Ingeniería03 conserva22 diferencias RAW distribuidas: igualar una región local o remota por separado mantiene la respuesta; igualarlas todas elimina la distinción en el contraste. La recuperación de nuevos ciclos requirió vacancias diagnósticas, sin renovación autónoma demostrada. Ingeniería04.5 aclara que RAW+clock sigue siendo estado Markoviano suficiente de su mundo; descripciones relacionales o fingerprints no añaden grados ontológicos. Sus comparaciones compartido/separado muestran ganancias y pérdidas diferentes, sin arquitectura ganadora universal. [R02-MECHANISMS, I02–I04.5]'),
para('CORE07 conserva transporte de función adquirida y un bucle de un uso. CORE09 ofrece selección binaria modificada por consecuencias: 144/168 decisiones correctas y 24 daños, frente a84 daños en cada control de exposición sin consecuencia, reinicio y ablación. El anfitrión define entorno, daño y señal de consecuencia; DEE transforma la dirección de selección, con reparación y recursos preparados. CORE10 conserva transferencia controlada a receptor compatible con 12/12 éxitos, cortes y controles negativos, consumiendo el emisor. La revalidación maestra posterior deja promociones particulares parciales o fallidas; no invalida automáticamente los mecanismos originales de otro dominio. [R02-MECHANISMS, CORE y MASTER]'),
para('La lectura del código corrige una atribución de CORE14: los clocks distintivos de esa preparación incluían sellos y reinicios introducidos por el anfitrión. Su persistencia no demuestra una escritura autónoma de historia en clocks. Sí demuestra que mirar sólo RAW puede omitir una diferencia preparada. Esta restricción se limita al binario y al protocolo cotejados, sin trasladarla automáticamente a OBP o Ingeniería06.'),
para('Pensamiento01 muestra diferencias RAW que una misma sonda no distingue en T35, pero sí en T70/T94. Omitir la segunda experiencia conserva esas respuestas tardías; basta la continuación nativa de aquel estado. Esto añade disponibilidad dependiente del tiempo bajo lectura preparada, sin demostrar que un aprendizaje posterior desocultó la información. Los cierres de las demás colecciones y sus negativos se conservan con los localizadores precisos del registro. [R02-MECHANISMS, Pensamiento01 y cobertura]'),
para('Procesos01 distingue la expansión de un mundo y la diferencia entre futuros: una gran máscara FULL/OMIT no es materia oculta dentro de FULL; otras condiciones alcanzan densidades similares más tarde. Procesos02 conserva ocupación mientras cambia su función restauradora. Procesos03 no obtiene celdas elegibles en su fase discovery, posterior a la calibración, y conserva el resultado no informativo; no valida temperatura efectiva ni energía cognitiva. [R02-MECHANISMS, Procesos01–03]'),
para('39 6 Principios compartidos y subobservación',2),
para('Historia y soporte distribuido. El Corpus, Ingeniería02/03, OBP y AA muestran que una función puede depender de relaciones entre soportes y de su contexto, con redundancia o degeneración. Coinciden en exigir historias contrastadas y uso posterior; cambian kernel, geometría, lector e intervención. La predicción discriminante es conservar la función al retirar una parte y perderla al cortar el conjunto causal necesario. Los primarios de epistasis e igualaciones permiten examinarla; una diferencia de campos aislada no basta.'),
para('Acceso y tiempo. Ingeniería02 y Pensamiento01 separan relación conservada y ventana de lectura. AA46/47 añaden uso de un soporte inicialmente enseñado mediante acceso posterior aprendido; a32 añade una transformación temprana fuera del resultado final. La predicción útil exige contenido opuesto, lector fijado antes y primera consulta reservada. a32 carece del tramo intermedio necesario para atribuir su NULL a una causa única; no se construyó un lector favorable después de ver la respuesta.'),
para('Composición y consecuencias. CORE09, Ciclo02 y APD aportan cambios de estado y decisiones con retornos materiales, pero preparación y dominios difieren. a29 recibió retorno sin cambiar aún su acción; a32 ni siquiera cerró ese enlace. Compartir selector explica una posibilidad de integración y de interferencia: una referencia útil para escoger proveedor puede sesgar la consulta de un dato. La discriminación requiere comparar contenido actual, historia y retorno en el mismo prefijo, no sumar aciertos de ramas.'),
para('Frontera causal y observación. El Atlas propone medir distinciones efectivas para un observador, tolerancia y horizonte; no aporta esa medida ya estimada para DEE20. Una región leída puede ser insuficiente aunque el estado completo sea suficiente. AA13 demuestra convergencia causal delimitada, no identidad de todos los archivos. CORE16 revela diferencias omitidas por una interacción diagnóstica preparada; su contraste llamado topología también cambia direcciones. Estos casos delimitan el observador y la frontera, sin postular información recuperable después de una convergencia exacta.'),
para('Las correcciones R01 siguen vigentes. El cierre de OBP retira la necesidad de un retorno remoto concreto y conserva plasticidad local. CPC9 TAIL_NO_NEW conservaba consultas y omitía cuatro intentos docentes. CORE17 sí cierra un cociente causal en su dominio y reparación mediante otro respaldo entrenado; no autorregeneración general. Una recurrencia no acredita por sí sola memoria; una huella distinguible no acredita uso por el ente. [Fuentes AT y bloques R01/R02]'),
para('39 7 Tres hipótesis y correspondencias',2),
table(['Hipótesis','Aporte nuevo R02','Conclusión'],[
('H1 Mecanismos especializados','Dominios del sensor, frontera neutra y preparación de CORE separan mecanismo eficaz y alcance.','Sigue explicando muchas funciones, incluido contenido adquirido. No excluye integración finita.'),
('H2 Organización integrada','Se verifica palabra→operación nativa→resultado usado después; un selector compartido conecta tareas y también sesga otra.','Integración funcional respaldada en esta historia. Coordinación del currículo y orden no aprendidos.'),
('H3 Organización más amplia','Soporte distribuido, disponibilidad tardía y observadores parciales amplían lo que conviene examinar.','Subobservación concreta reforzada; alcance funcional mayor todavía por distinguir. No requiere materia o variables físicas no registradas.'),
], [1.25,2.65,2.6]),
para('Medio, memoria y transformación compartiendo grados físicos son principios funcionales que permiten investigar correspondencias con cerebro o naturaleza. Las33 ecuaciones de Fundamentos ahora inspeccionadas explicitan condiciones de cierre, medida, representación unitaria y mapa cuántico; no suministran una prueba biológica ni entrelazamiento cognitivo. Los20Hz examinados siguen siendo una calibración con entradas externas; las aproximaciones a constantes comparten anclas. Analogía funcional, correspondencia de mecanismos y equivalencia del sustrato son afirmaciones de alcance diferente. Una validación independiente exigiría predicción y calibración fijadas antes del dato, ausentes en los contrastes examinados. [R02-FOUNDATIONS; AT-V05 y correspondencias R01]'),
para('39 8 Prioridades y continuidad',2),
para('Prioridad1. Mantener la investigación de acceso, selección y utilidad, corrigiendo su punto de partida: antes de atribuir adaptación adicional, delimitar el rango donde el sensor puede cambiar la elección y el dominio donde el lector reconoce la salida. Los registros actuales permiten comparar referencias, entradas y frames de a29/a32 con los antecedentes APD03/APD04 ya localizados; no permiten inventar q+5 ni el contrafactual causal ausente.'),
para('Prueba futura delimitada, no ejecutada: desde un prefijo completo aislado, congelar codec, lector, recursos y horizonte; cruzar observación presente bit0/bit1 con la historia del selector; contrastar retorno real/omitido y una intervención selectiva con sham. Para el neutro, registrar E y su vecindad en q+4…q+6 antes de definir otro acceso. Cambiar selección con contenido igual distinguiría sensibilidad; conservar el signo sin efecto útil separaría memoria y actuación. Ningún resultado de esa copia deberá importarse como experiencia de la vida actual.'),
para('Prioridad2. Mantener un panel documental por contenido y último uso, aprovechando la matriz detallada. Una función demostrada en un antecesor no es garantía ni refutación de conservación presente. Una comprobación futura de primera lectura y retención deberá hacerse sólo con autorización experimental específica.'),
para('Prioridad3. Formular una predicción concreta de soporte distribuido o ventana temporal en preparaciones distintas, con un observador prospectivo y un control que pueda refutarla. Las capacidades subobservadas se reconocen por información y uso, sin rellenar cada fallo con H3. Las correspondencias externas conservan su pregunta independiente.'),
para('El estado se conserva en T697764 y su selección no cambió. No se añadieron capacidades, mecanismos, perfiles ni aprendizajes. El registro único contiene fuentes, rangos, primarios, recálculos y los puntos pendientes; el compendio sigue siendo mapa experimental, no inventario de recuerdos del activo.'),link('Volver al punto de reanudación','AT_REANUDACION')]
replace_range(start,end,c)

# El apéndiceF se completa después de integrar los tres fragmentos R02.
start=find('Apéndice F Inventario documental y cobertura transversal')
f=[para('Apéndice F Inventario documental y cobertura transversal',1)];bookmark(f[0],'AT_INVENTARIO',9003)
f += [para('Las lecturas se acumulan por fuente lógica y versión. Un índice, búsqueda o extracción no se contabiliza como lectura. El registro conserva R01 y una continuación R02 con los rangos efectivamente examinados, hashes, miembros y exclusiones concretas. Los identificadores AT remiten al inventario original; R02-FOUNDATIONS, R02-MECHANISMS y R02-TRAJECTORIES remiten a continuation_R02.blocks.'),
para('Cobertura de los documentos rectores',2)]
rows=R['continuation_R02'].get('manual_inventory_rows')
assert rows,'Integrar cobertura antes de generar Word'
f += [table(['ID y documento','Lectura acumulada y cambio R02','Pendiente o exclusión'],rows,[1.7,2.9,1.9])]
f += [para('Colecciones experimentales',2)]
rows=R['continuation_R02'].get('manual_collection_rows')
assert rows,'Integrar colecciones antes de generar Word'
f += [table(['Colección','Lectura y contraste realizados','Límites'],rows,[1.35,3.1,2.05]),
para('Los apéndices A–E conservan las clasificaciones históricas de su corte, incluidos DP y PE. La lectura documental R02 no cambia esas filas a reproducción Native ni atribuye sus aprendizajes a DEE20. El compendio Word se leyó completo por acumulación R01/R02; los campos técnicos de variantes del JSON no se declaran íntegramente leídos. El catálogo reproducible conserva 101 IDs y remite a sus condiciones originales. El índice técnico añade referencias hacia mecanismos históricos examinados; no registra capacidades nuevas del producto.'),
para('Las fuentes actuales se resuelven en PROYECTO.json, CONTINUIDAD_DEE_COGNITIVE_2_0.json y los primarios gzip estables de archivo/DEE_Cognitive_2_0_historial_presentacion_R01/videos/datos. a29 es a29_goal_opportunities.json.gz; a32 es a32_version_opportunities.json.gz. En cada cadena, el registro identifica el JSON Pointer, los ticks, recibos y código leído como texto. No se abrió SQLite para R02 ni se utilizó un journal como respuesta del participante.'),
para('Los localizadores de la edición1.21 se resuelven en su respaldo previo; los de la edición1.22 leída para R02 se resuelven en edicion_anterior/DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_22.docx. U cuenta párrafos del cuerpo y párrafos de tablas en orden; las convenciones P/L de cada bloque se documentan allí. No son números de página supuestos.'),
para('La revisión no es exhaustiva de todo el archivo. Los tramos no leídos del Corpus y de fuentes parciales permanecen pendientes, con razones concretas. Las copias byte-idénticas contrastadas se reutilizan sin contar dos lecturas. El detalle de compilación ajeno a la pregunta se distingue de lo pendiente; ningún material extenso se declara irrelevante por su tamaño. Las33 imágenes de ecuaciones inspeccionadas no significan que se vieran todas las figuras del corpus.'),
para('Para retomar, lea el punto inicial, las prioridades del capítulo39 y continuation_R02.resume. La entrega cambia el conocimiento documentado del sistema; no cambia su estado físico ni instala una corrección.'),link('Volver al punto de reanudación','AT_REANUDACION')]
replace_range(start,None,f)

# Identidad editorial y campos; no se renombra la ruta del lanzador.
for p in D.paragraphs:
    if p.text.startswith('DEE thinking 4.5.0 |'):
        for r in p.runs:r.text=''
        p.runs[0].text='DEE thinking 4.5.0 | DEE Cognitive 2.0 | Edición documental 1.23 | DCS11-MM-001'
    elif p.text.startswith('Edición documental 1.22. Análisis transversal'):
        for r in p.runs:r.text=''
        p.runs[0].text='Edición documental 1.23. Continuación R02 del análisis transversal, 30 de octubre de 2026. El punto de reanudación, el capítulo39 y el apéndiceF distinguen la organización actual, sus antecedentes y la cobertura real. La vida permanece en T697764; esta edición no añade experiencias.'
    elif 'Su edición vigente 1.22' in p.text:
        for r in p.runs:r.text=r.text.replace('Su edición vigente 1.22','Su edición vigente 1.23')
for row in D.tables[0].rows:
    if len(row.cells)<2:continue
    key=row.cells[0].text
    if key=='Documento':row.cells[1].text='DCS11-MM-001 / Edición documental 1.23 / Continuación R02 del 30 de octubre de 2026'
    elif key=='Base principal':row.cells[1].text='Mismo manual lógico y misma ruta de apertura. Ediciones 1.21 y 1.22 preservadas en archivo/analisis_transversal_cognitivo/edicion_anterior. El nombre se conserva para no modificar PROYECTO.json ni el lanzador.'
    elif key=='Estado de esta edición':row.cells[1].text='Revisión documental acumulativa por bloques. Código leído como texto y recálculos pasivos; cero simulaciones o consultas materiales. No instala capacidades ni promueve otra vida.'
for section in D.sections:
    for part in [section.header,section.footer,section.first_page_header,section.first_page_footer]:
        for p in part.paragraphs:
            for r in p.runs:
                if '1.22' in r.text:r.text=r.text.replace('1.22','1.23')
                if '29 OCT 2026' in r.text:r.text=r.text.replace('29 OCT 2026','30 OCT 2026')
# Correcciones tipográficas acotadas a los elementos nuevos, sin tocar identificadores.
replacements={'Las33':'Las 33','las33':'las 33','Los20Hz':'Los 20 Hz','20Hz':'20 Hz','seis sitios':'seis sitios','718/718':'718/718','los48':'los 48','las48':'las 48','incluidos6':'incluidos 6','Ambas referencias ya habían aumentado3':'Ambas referencias ya habían aumentado 3','los176':'los 176','y126 ceros':'y 126 ceros','referencias1487/1507':'referencias 1487/1507','diferencia21':'diferencia 21','diferencia19':'diferencia 19','sitios state':'sitios state','R02:3300':'R02: 3300','textoV4':'texto V4','completoP':'completo P','enT':'en T','con101':'con 101','lector común36':'lector común 36','comparativa20':'comparativa 20','valor27':'valor 27','incremento3':'incremento 3','salida50':'salida 50','diferencia4':'diferencia 4','consecuencias:144':'consecuencias: 144','por32':'por 32','de32':'de 32','Las33':'Las 33','capítulo39':'capítulo 39','apéndiceF':'apéndice F','edición1.21':'edición 1.21','edición1.22':'edición 1.22','edición1.23':'edición 1.23','33/33 ecuaciones':'33/33 ecuaciones','texto completo R01;33':'texto completo R01; 33','versiones:':'versiones:'}
replacements.update({'aplicaron48':'aplicaron 48','compara83':'compara 83','sólo2/32':'sólo 2/32',';32/32':'; 32/32','de31/32':'de 31/32','no32':'no 32','volumen4':'volumen 4','conserva22':'conserva 22','a84 daños':'a 84 daños','completoP':'completo P','Texto del Atlas':'Texto del Atlas','capítulos1':'capítulos 1','capítulos3':'capítulos 3','también9':'también 9','deCORE':'de CORE','MASTER:3':'MASTER: 3','continuaciónP01':'continuación P01','contraste:':'contraste:'})
for element in front+c+f:
    for text in element.iter(qn('w:t')):
        if text.text:
            for old,new in replacements.items():text.text=text.text.replace(old,new)
D.core_properties.revision=23
D.core_properties.modified=datetime.now(timezone.utc)
target=W/'manual_r02_en_revision.docx'
D.save(target)
R['continuation_R02']['manual_update']={'edition':'1.23','source':str(BACKUP),'source_sha256':hashlib.sha256(BACKUP.read_bytes()).hexdigest(),'candidate':str(target),'candidate_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'target':str(SOURCE),'original_operational_manual_unchanged_until_validation':True,'marker_successful_once':True,'render_status':'pending'}
REG.write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('CANDIDATE',target,'bytes',target.stat().st_size)
