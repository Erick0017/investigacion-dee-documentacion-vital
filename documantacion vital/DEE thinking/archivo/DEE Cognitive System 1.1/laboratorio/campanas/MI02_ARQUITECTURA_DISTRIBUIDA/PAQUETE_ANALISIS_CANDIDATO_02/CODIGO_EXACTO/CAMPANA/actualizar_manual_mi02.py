"""Actual DOCX1.8 edit of retained1.7, no engine import or native ticks."""
import hashlib,json,re,sys,zipfile
from pathlib import Path
from datetime import datetime,timezone
from docx import Document
from docx.shared import RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree
sys.stdout.reconfigure(encoding='utf8')
L=Path(__file__).resolve().parent;R=L.parents[2];E=R/'evidencia/campanas/MI02_ARQUITECTURA_DISTRIBUIDA'
src=R/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_7_MI01_SIN_VALIDACION_VISUAL.docx'
dst=R/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_8_MI02_SIN_VALIDACION_VISUAL.docx'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
original=sha(src);assert original=='8a73d88bcdc3fbefb9537bc2026480c7d9762021e058d2a8d27954b6216984d9'
if dst.exists():
    preserved=L/'editorial_MI02/PRIMERA_EDICION_ESTRUCTURAL.docx'
    assert sha(dst)=='b5b8183f24d67c927e9a956cb50b70ac799e4f9dd7abf9625388fd2fa11fd92c'and sha(preserved)==sha(dst),'Only refine the identified preserved editorial draft; never replace another edition'
continuity=json.loads((R/'CONTINUIDAD_MI02_ARQUITECTURA_DISTRIBUIDA.json').read_bytes());assert continuity['main_final_tick']==81207
d=Document(src);anchor=next(p for p in d.paragraphs if p.style.name=='Heading 1'and p.text.startswith('Apéndice A'))
tocend=next(p for p in d.paragraphs if p.style.name=='TOCline'and p.text.startswith('Apéndice A'));tocend.insert_paragraph_before('25 Arquitectura distribuida MI02 y alcance operativo',style='TOCline')
for p in d.paragraphs:
    if'Edición documental 1.7  |'in p.text:p.text=p.text.replace('Edición documental 1.7','Edición documental 1.8')
    if p.text.startswith('Corte documental actualizado:'):
        p.text='Corte documental actualizado: 22 de octubre de 2026\nPredeterminado protegido: E1_SOCIAL_11 T3154\nMAIN MI02: D1_MI02_MAIN T81207\nAlternativa R9: MI02_SOCIAL_REUSABLE_240 T15329 y MI02_R9_OPERATIVA47 T20021'
    if p.text.startswith('La edición original se basó en el resumen funcional'):
        p.add_run(' El capítulo25 incorpora MI02 y distingue sus dos realizaciones, la evaluación fijada de MAIN y la alternativa reutilizable posterior. Las expresiones de estado actual en los capítulos anteriores pertenecen a sus cortes históricos; la continuidad vigente se consulta en25 y en CONTINUIDAD_MI02_ARQUITECTURA_DISTRIBUIDA.json.')
updates={'Documento':'DCS11-MM-001 / Edición documental 1.8','Corte de liberación registrado':'22/10/2026; MI02 MAIN T81207; alternativa operativa R9 T20021','Base principal':'Edición1.7 MI01 preservada; estados y resultados ejecutados de MI02','Estado de esta edición':'Word actualizado realmente y estructura comprobada. Validación visual no acreditada; consulte el registro de render MI02.'}
for row in d.tables[0].rows:
    if row.cells[0].text in updates:row.cells[1].text=updates[row.cells[0].text]
for section in d.sections:
    for area in(section.header,section.footer):
        for p in area.paragraphs:
            for run in p.runs:
                if'1.7'in run.text:run.text=run.text.replace('1.7','1.8')
content=[
('Heading 1','25 Arquitectura distribuida MI02 y alcance operativo'),
('Normal','Conclusión: existe integración útil, todavía dependiente de asistencia relevante y de condiciones físicas acotadas. MAIN conservó una historia común para aprendizaje local, solicitud material, comunicación y actuación externa, pero perdió usos durante la evaluación. La alternativa R9 añadió liberación y reutilización del lector social sin limpieza del anfitrión. No se declara integración sostenida general ni una mente completa.'),
('Heading 2','Identidad y cortes que pueden continuarse'),
('Normal','E1_SOCIAL_11 T3154 continúa como predeterminado protegido. E1_MI01_MAIN T28169 y su futuro adverso permanecen intactos. La realización A, E1_MI02_HEREDADA_R8, es una bifurcación exacta del snapshot MI01 T24752 y llegó a T36366. Su región añadida aprendió por consecuencias, pero no se acreditó que el conocimiento antiguo alimentara las nuevas decisiones. Compartir mundo y biblioteca no demuestra esa integración.'),
('Normal','La realización B empezó realmente desde T0, sin importar memorias entrenadas. D1_MI02_MAIN usa un mundo N26 con A, un participante privado B y canales nativos preparados. El programa fijado terminó en T64749. Una continuación posterior expresamente declarada llevó la misma vida hasta T81207, sin restauración ni cambio de arquitectura. D1_MI02_LEXICO_CONSERVADO T60839 y D1_MI02_POST_CAMBIO34 T81207 son bifurcaciones identificadas, no pasados favorables que puedan devolverse a MAIN.'),
('Normal','La alternativa MI02_SOCIAL_REUSABLE_240 nació desde T0 con otra preparación, R9. Alcanzó T15329; su copia operativa MI02_R9_OPERATIVA47 continuó hasta T20021 mediante oportunidades nativas y dieciséis pasos externos. No es la biografía de E1 ni una sustitución retrospectiva de MAIN. Cada checkpoint completo guarda el mundo compartido una sola vez, con sus interfaces, entradas pendientes y estado del puente cuando corresponde.'),
('Heading 2','Qué cambió mediante experiencias'),
('Normal','El retorno material de una actuación fallida modificó campos relativos que después cambiaron la elección. En el perfil local N17, dieciséis de las dieciocho oportunidades posteriores fueron útiles frente a siete en los controles de retorno omitido o cortado. En la rama heredada N67 hubo diez de quince frente a cinco de quince sin retorno. Son trayectorias finitas, no tantas réplicas independientes como consultas.'),
('Normal','En MAIN, una perturbación genérica recuperó un contacto que estaba desfasado sin volver a enseñar su referencia. Después, al cambiar la disponibilidad, las diez primeras actuaciones fueron incorrectas y las diez siguientes útiles. El control sin retorno siguió emitiendo la acción anterior: no era silencio. Este cambio acotado por consecuencias no acredita regulación flexible R2 ni aprendizaje competente de una política de control externo.'),
('Heading 2','Consulta privada composición y reutilización'),
('Normal','En la organización unificada, un estado producido por la historia local inició materialmente la solicitud a B. B disponía inicialmente de experiencias privadas; su respuesta llegó por canales del mismo mundo y cambió una actuación posterior de A. Cortar consulta o mensaje y contrastar la historia privada delimitó esa contribución. El signo recibido se combinó con campos propios adquiridos. La misma corriente equilibrada puede cumplir también un papel motor predeterminado: no se atribuye una elección exclusiva entre preguntar y actuar.'),
('Normal','R9 separó el contenido privado del recurso de lectura. B pudo volver a vacío sin perder sus referencias61/19 y reactivarse por solicitudes nativas posteriores. La continuación45 registró tres episodios activos separados por intervalos vacíos y nueve contactos útiles de doce. Un tren de solicitudes puede mantener activo al lector durante un intervalo; no se afirma que se vacíe tras cada paquete. El registro adicional produjo los mismos RAW, clocks, agenda y recibos que su control técnico.'),
('Normal','En reservas R9 con referencias propias13/13 y privadas91/29 o29/91, ambas terceras actuaciones de prueba fueron útiles. Cortar el mensaje o retirar la historia privada eliminó el uso que requería esa información; el sham lo conservó. Se transmite una distinción relativa, no los dos valores privados completos. La actualización arbitraria de nuevos mensajes no quedó demostrada: A conserva su primer contexto.'),
('Normal','Las revisiones previas que no liberaban el lector permanecen archivadas. El cambio de anatomía fue ingeniería del investigador, no reorganización aprendida del ente. Una observación localizó un soporte que aparecía en un hueco; la intervención estructural y su control delimitaron su papel en la persistencia. No se atribuye a esa observación una capacidad de inspección del propio participante.'),
('Heading 2','Lectura auxiliar y límites del lenguaje'),
('Normal','El perfil auxiliar MI02_EFIMERO_210 conserva referencias32/10 mediante usos repetidos y una demora pasiva de845ticks. Su lector vuelve a vacío por evolución nativa y admite otra sonda genérica sin limpieza. Los controles de historia opuesta, ausencia de adquisición, dato omitido y sonda omitida delimitan la función. Otra vida aprendió explícitamente la referencia después de consultas inicialmente infructuosas; eso es adquisición tardía, no recuperación de un recuerdo perdido. Este lector auxiliar no fue trasplantado a MAIN.'),
('Normal','Dos señales fijas, presentadas como izquierda y derecha, produjeron dieciséis respuestas previstas de dieciséis después de las lecciones. Sin embargo, consecuencias desacopladas también produjeron dieciséis de dieciséis. Por ello no se acredita asociación específica palabra-significado ni comprensión española. Después del aprendizaje del nuevo régimen de actuación, ambas señales provocaron derecha y sólo cuatro de ocho coincidieron con la etiqueta prevista. El resultado positivo de discriminación física y su contraejemplo se conservan juntos.'),
('Normal','No se elevó ninguna entrada NSM65. Las palabras adicionales no se convierten en primitivas nuevas; tampoco se atribuyen YO/TÚ, gramática, conversación libre o significado humano a un código direccional. El lector escalar tiene un marco preparado y un dominio limitado; no demuestra por sí solo igualdad o cantidad general.'),
('Heading 2','Actuación externa acceso y asistencia'),
('Normal','MAIN ejecutó112pasos reales de Pendulum en tres ventanas, conservando su estado DEE entre bloques y entre dos episodios externos. La interfaz corregida recibió datos y produjo torque de ambos signos, pero sus resultados no sostienen control competente aprendido. Los controles de actuador anulado, sensores omitidos y retardo cambiaron trayectorias o comandos con resultados mixtos. La velocidad angular no entró por el codec utilizado; no se promete un cuerpo robótico completo.'),
('Normal','Las consultas y estímulos pueden conservar los campos de referencia y, a la vez, desfasar el contacto útil. Una intervención genérica asistida recuperó acceso en el caso tardío; en una reserva después de ruido dio cinco contactos útiles de seis frente a cero de seis sin intervención y cero de seis con sham. El operador inició esa intervención. No fue recuperación autónoma, reenseñanza del valor, limpieza de mundo ni regulación R2.'),
('Normal','El estrés no tuvo efecto monotónico: perturbaciones espaciadas bloquearon contactos, mientras una ráfaga más densa no produjo ese bloqueo en el mismo prefijo. Referencia conservada, lectura disponible y actuación útil son dimensiones distintas. Ocupación y duración no se utilizan como sinónimos de energía, capacidad mental o supervivencia.'),
('Heading 2','Uso desde el gestor existente'),
('Normal','Los comandos mi02-estado, mi02-crear, mi02-adquirir, mi02-vivir y mi02-social-continuar utilizan el gestor habitual. mi02-vivir ofrece oportunidades ambientales declaradas; las actuaciones y las solicitudes condicionadas se producen físicamente, sin que Python elija la habilidad según la respuesta esperada. Crear es una preparación T0; bifurcar conserva exactamente el prefijo de una vida; continuar conserva su estado real. Son operaciones diferentes.'),
('Normal','Para proteger un estado, use bifurcar MI02_SOCIAL_REUSABLE_240 MI02_MI_CONTINUACION y después mi02-vivir --vida MI02_MI_CONTINUACION --condiciones=1,1,-1,-1. Un nombre que ya existe no se reemplaza silenciosamente. guardar y una llamada posterior cargan el checkpoint completo. mi02-externo continúa el puente persistido; un reinicio explícito del entorno no reinicia DEE. El episodio externo tiene horizonte declarado, no duración ilimitada.'),
('Normal','mi02-comparar-efimero presenta datos actuales a una copia del perfil auxiliar. mi02-recurso-fase es asistencia P0 exclusiva de su dominio R6, no una acción autónoma. mi02-orden transporta los dos códigos físicos y muestra una emisión nueva; su nombre no convierte la operación en comprensión de lenguaje. Las guías, contratos y fichas vigentes explican alcance y rechazos. La operación normal no lee laboratorio, evidencia o diarios para resolver respuestas.'),
('Heading 2','Evidencia alcance y preservación'),
('Normal','Consulte CONTINUIDAD_MI02_ARQUITECTURA_DISTRIBUIDA.json y sistema/documentacion/GUIA_MI02.md. Los primarios y estados profundos permanecen en evidencia/campanas/MI02_ARQUITECTURA_DISTRIBUIDA y en el estado operativo. El ZIP de análisis incluye proyecciones verificables, controles, fuentes exactas, recálculo y snapshots seleccionados; no sustituye la instalación completa ni todos los estados locales.'),
('Normal','No hubo promoción del predeterminado ni unión de memorias de ramas. Se conservaron capacidades históricas y futuros adversos. R9 se incorporó como alternativa ejecutable; el lector auxiliar y el recurso P0 conservan contratos separados. La presente edición1.8 actualiza realmente el Word desde1.7 sin alterar el motor ni divulgar sus reglas internas. La estructura está comprobada; la situación de la renderización se informa en el comprobante editorial y no se presenta como validación visual.')]
for style,text in content:
    text=re.sub(r'(?<=\d)(?=[A-Za-zÀ-ÿ])',' ',text)
    text=re.sub(r'(?<=[a-záéíóúñ])(?=(?:R\d|T\d|NSM\d|MI\d))',' ',text)
    text=re.sub(r'\b(referencias|referencia|semilla|revisión|edición|capítulo|pasos|Sistema|System)(?=\d)',r'\1 ',text)
    text=text.replace(' Bya ',' B ya ')
    p=anchor.insert_paragraph_before(text,style=style);p.paragraph_format.widow_control=True
    if style.startswith('Heading'):
        p.paragraph_format.keep_with_next=True
        for run in p.runs:run.font.color.rgb=RGBColor(0,0,0)
d.core_properties.title='DEE Cognitive System 1.1 Manual maestro de continuidad Edición 1.8'
d.core_properties.subject='Arquitectura distribuida MI02 y alcance operativo';d.core_properties.revision=18
setting=d.settings.element.find(qn('w:updateFields'))
if setting is None:setting=OxmlElement('w:updateFields');d.settings.element.append(setting)
setting.set(qn('w:val'),'true')
tmp=L/'editorial_MI02/EDITADO_INTERMEDIO.docx';tmp.parent.mkdir(parents=True,exist_ok=True);d.save(tmp)
changed={'word/document.xml','word/settings.xml','docProps/core.xml'}
with zipfile.ZipFile(src)as a,zipfile.ZipFile(tmp)as b,zipfile.ZipFile(dst,'w',compression=zipfile.ZIP_DEFLATED)as z:
    assert set(a.namelist())==set(b.namelist()),'No unreviewed added package members'
    for name in a.namelist():
        if name.startswith(('word/header','word/footer'))and name.endswith('.xml')and a.read(name)!=b.read(name):changed.add(name)
    for info in a.infolist():z.writestr(info,b.read(info.filename)if info.filename in changed else a.read(info.filename))
assert sha(src)==original
with zipfile.ZipFile(src)as a,zipfile.ZipFile(dst)as z:
    assert z.testzip()is None
    for name in z.namelist():
        if name.endswith('.xml'):etree.fromstring(z.read(name))
        if name not in changed:assert a.read(name)==z.read(name),'Unexpected unchanged-part modification'
dd=Document(dst);numbers=[int(re.match(r'^\d+',p.text).group())for p in dd.paragraphs if p.style.name=='Heading 1'and re.match(r'^\d+',p.text)]
assert numbers==list(range(1,26)),numbers
assert len([p for p in dd.paragraphs if p.style.name=='TOCline'and p.text.startswith('25 ')])==1
assert all('1.7'not in p.text for s in dd.sections for area in(s.header,s.footer)for p in area.paragraphs)
assert any('T81207'in p.text for p in dd.paragraphs[:20]);assert any('T20021'in p.text for p in dd.paragraphs[:20])
result={'source':str(src),'source_sha256':original,'original_unchanged':True,'output':str(dst),'output_sha256':sha(dst),'output_bytes':dst.stat().st_size,'changed_parts':sorted(changed),'unchanged_parts_byte_identical':True,'chapters':numbers,'TOC25_unique':True,'all_XML_parseable':True,'ZIP_CRC_valid':True,'edition':'1.8','visual_validation':False,'render_attempt_required':True,'native_ticks':0,'edited_utc':datetime.now(timezone.utc).isoformat()}
(E/'VERIFICACION_WORD_MI02_ESTRUCTURAL.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(result,ensure_ascii=False,indent=2))
