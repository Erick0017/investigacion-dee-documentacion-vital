"""Surgical real DOCX revision; no kernel implementation is disclosed."""
from pathlib import Path
from datetime import datetime,timezone
from zipfile import ZipFile
import json,hashlib,re,xml.etree.ElementTree as ET
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt,Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
SOURCE=ROOT/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_4_CANDIDATO_SIN_VALIDAR.docx'
TARGET=ROOT/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_5_INTEGRACION_SITUADA_SIN_VALIDACION_VISUAL.docx'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def life(name):
    r=read(ROOT/'sistema/estado/vidas'/name/'VIDA.json');return{'life':name,'tick':r['physical']['tick'],'snapshot':r['snapshot'],'sha256':r['snapshot_sha256'],'profile':r['profile'],'parent':r.get('parent')}
if TARGET.exists():raise FileExistsError('One closing edition; inspect an existing revision rather than overwrite it')
source_hash=sha(SOURCE);original=ROOT/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_0.docx';original_hash=sha(original)
d=Document(SOURCE);changes=[]
def settext(p,text):
    p.text=text;changes.append({'new_text':text[:180]})
for p in d.paragraphs:
    if 'Edición documental 1.4' in p.text:settext(p,p.text.replace('Edición documental 1.4','Edición documental 1.5'))
    elif 'Este libro tiene edición documental 1.4.'in p.text:settext(p,p.text.replace('Este libro tiene edición documental 1.4.','Este libro tiene edición documental 1.5.'))
    elif p.text.startswith('La edición 1.4 integra'):settext(p,'La edición 1.5 conserva la integración documental anterior, corrige el corte de Hábitat a ECO_EXT_01 T6167 y añade Integración Cognitiva Situada E1 01. Actualiza el índice enlazado, la identificación editorial y los estados realmente alcanzados. No promueve automáticamente ninguna rama ni cambia el motor.')
    elif p.text.startswith('La edición original se basó'):settext(p,p.text+' El nuevo capítulo 22 integra los resultados, pérdidas y comandos de INTEGRACION_COGNITIVA_SITUADA_E1_01. Los addenda anteriores siguen preservados como fuentes; no sustituyen silenciosamente a este Word.')
    elif p.text.startswith('Se ejecutó una conexión externa real con Gymnasium'):
        settext(p,'En Hábitat 01 se ejecutó una conexión externa real con Gymnasium 1.4.0 en el intérprete externo ya instalado. La vida ECO_EXT_01 alcanzó T6167: los 24 pasos iniciales y una continuación operativa adicional sumaron 25 pasos de Pendulum. Este corte corrige ECO_EXT01/T6100 del borrador anterior. Se utilizaron un codec sensorial fijo y salidas nativas transducidas a torque; no se demostró aprendizaje de una política de control competente. Los controles históricos de acción anulada, retardo y otra semilla conservan su propio alcance.')
    elif p.text.startswith('El puente y sus dependencias son instrumentación externa'):
        settext(p,'El puente y sus dependencias son instrumentación externa, no comunicación cerrada puramente v27. Hábitat incorporó habitat-externo y habitat-estado y dejó una continuación operativa comprobada en ECO_EXT_01 T6167. La campaña posterior situada utiliza sus propios metadatos de puente y los comandos integrado-externo/integrado-estado; no deben intercambiarse silenciosamente ambos protocolos. Los ZIP de análisis no contienen todos los estados completos necesarios para continuar.')

# Existing field-free TOC lines duplicated their labels. Replace them with a
# single explicit internal-link index; do not invent pagination without render.
for p in list(d.paragraphs):
    if p.style.name=='TOCline':p._element.getparent().remove(p._element)
anchor=next(p for p in d.paragraphs if p.text.startswith('Apéndice A.'))
def para(text,style='Normal'):
    p=d.add_paragraph(text,style=style);anchor._p.addprevious(p._p);return p
def head(text):return para(text,'Heading 2')
def table(headers,rows,widths):
    t=d.add_table(rows=1,cols=len(headers));t.style='Table Grid';t.autofit=False
    for c,h,w in zip(t.rows[0].cells,headers,widths):c.text=h;c.width=Inches(w)
    for row in rows:
        cells=t.add_row().cells
        for c,v,w in zip(cells,row,widths):
            c.text=str(v);c.width=Inches(w)
            for p in c.paragraphs:
                for r in p.runs:r.font.size=Pt(8.5)
    for c in t.rows[0].cells:
        for r in c.paragraphs[0].runs:r.bold=True;r.font.size=Pt(9)
    anchor._p.addprevious(t._tbl);return t

selected=life('E1_INTEGRADO_CONTINUABLE_01');recovered=life('E1_INTEGRADO_RECUPERACION_01');active=life('E1_SOCIAL_11');main=life('E1_INTEGRADO_MAIN');damaged=life('E1_INTEGRADO_COSTO_SOCIAL_01')
para('22. Integración cognitiva situada: experiencia, consecuencias y uso','Heading 1')
head('Corte real, tipo de organización y asistencia')
para('El predeterminado continúa siendo E1_SOCIAL_11 T3154, protegido. Se ensayaron bifurcaciones completas del mismo mundo N67, no reconstrucciones desde T0. La organización es compuesta: soportes heredados, comparación cuantitativa, rutas y oportunidades de retorno preparadas y un participante B con su propia referencia. Compartir Runtime no convierte cada región funcional en una mente autónoma ni atribuye a E1 todo lo disponible en la biblioteca.')
para('El investigador preparó sensores, puertos, encuentros posibles, cadencias, suministro y leyes ambientales. DEE produjo los campos físicos, la transformación de referencias y las salidas utilizadas. El puente externo sumó señales físicas mediante un cableado fijo y ejecutó Pendulum; esa suma no es composición aprendida dentro de DEE. Los diarios, semillas y resultados del auditor no son memoria accesible a los participantes.')
table(['Vida / rama','Tick actual','Estado y alcance'],[(active['life'],active['tick'],'Activo heredado sin modificación.'),(main['life'],main['tick'],'MAIN conservado con pérdida de acceso y expansión; no promovido.'),(damaged['life'],damaged['tick'],'Rama integrada con futuro adverso bajo ruido, sin restauración.'),(selected['life'],selected['tick'],'Complementaria continuable, sin el estrés nominal que dañó la otra rama; no sustituye al activo.'),(recovered['life'],recovered['tick'],'Recuperación genérica preparada y uso en nuevo episodio externo; pérdidas anteriores declaradas.')],[2.7,.7,2.9])
para('Los localizadores exactos, hashes y parentescos están en CONTINUIDAD_INTEGRACION_COGNITIVA_SITUADA_E1_01.json, junto a este manual. El tick de un campo aislado o un máximo histórico no acredita acceso funcional actual. Sólo los estados completos del sistema permiten continuar; el ZIP de análisis no los reemplaza.')
head('Qué cambió por experiencia y qué no se demostró')
para('Las consecuencias reales de acciones externas se devolvieron como cargas materiales mediante un codec fijo. Cambiaron una referencia nativa y una decisión posterior ante una entrada común. Con el objeto nativo nuevo 230, la historia de acción intacta produjo +X; las historias con acción anulada o retorno omitido produjeron −X. La diferencia persistió con demoras adicionales de 67 y 134 ticks. Estos contrastes usan bifurcaciones dependientes, no aprendices independientes. La prueba está fuera del rango 1–145 del sensor de Pendulum y no demuestra mejor control del péndulo.')
para('El circuito nativo de oportunidades y consecuencias mostró selección dependiente de historia bajo una ley de aprendizaje preparada. En el panel R6 se observaron seis acciones con contenido y cuatro útiles en el contexto actual; la protección transitoria produjo doce con contenido y siete útiles. En una reserva con calentamiento hubo 25/32 lecturas con contenido, pero sólo 14/32 útiles. No deben confundirse admisión, respuesta válida y decisión útil. La reserva fría falló y el selector perdió acceso más adelante.')
para('B produjo dos relaciones direccionales contrastadas mediante su comparación privada. Una transformación recibida conservó ese contenido 56 ticks y pudo consultarse con recursos genéricos de carga cero en ambas ramas. Sin B o con el mensaje cortado no hubo la respuesta pertinente; el sham la conservó. El contenido positivo se utilizó repetidamente después, sin reenseñanza privada. No se demostró elección autónoma de lector, negociación ni una palabra española nueva adquirida.')
para('Una nueva experiencia social tardía con contenido opuesto cambió las actuaciones posteriores; repetir el mismo contenido conservó su uso. Una consulta material sin mensaje nuevo transformó el soporte anterior y perdió el acceso histórico. El procedimiento integrado-recuperar-social, preparado antes de las reservas, utiliza los mismos recursos genéricos de carga cero en ambas posibilidades y un conjunto paralelo fijo de lecturas. Recuperó ambos contenidos en las copias emparejadas y el positivo en una reserva tardía; el sham y la historia sin contenido anterior no lo hicieron. Es un acceso diseñado P0 cuyo resultado depende del contenido adquirido, no selección autónoma aprendida P2/R2.')
head('Integración real, límites y pérdidas')
para('Una misma trayectoria complementaria utilizó consecutivamente referencia modificada por consecuencias, información social recibida, actuación externa, nuevas experiencias nativas y funciones anteriores. Guardó y restauró el mundo y el estado del entorno entre procesos. El circuito corto de selección no conservó acceso indefinido: en la intercalación tardía se perdieron sus últimas respuestas, aun cuando comparación y comunicación siguieron utilizándose. La integración es parcial, no una mente general ni un inventario de 65 significados.')
para('La comprobación material final obliga a limitar la herencia: las dos comparaciones siguieron produciendo sus consecuencias, pero no se conservaron las cuatro firmas sociales históricas bajo el mismo lector. Tres conservaron huellas direccionales transformadas después de sondas sucesivas y S04 perdió su lectura. Esas tres huellas no se presentan como tres funciones recuperadas. El predeterminado protegido preserva su dominio anterior; no se lo reemplazó por la rama nueva. La vida complementaria llegó a T16485 y la reserva de recuperación a T17155, tras un reinicio explícito sólo de Pendulum, nunca de DEE.')
para('La acumulación de costes terminó haciendo constante la salida dentro del rango del sensor externo. El control con observación sensorial fijada mostró ese límite; una referencia modificable no es una política de control aprendida ni mejorada por definición. Los intentos de transportar la información de B al operando de comparación fallaron; el cableado externo de dos salidas se conserva como aparato preparado, no se rebautiza como composición nativa.')
para('La dosis nominal de ruido produjo un fallo distinto del choque fuerte. El evento de lector de carga 1 en T6366 fue causalmente relevante en los contrastes emparejados: su omisión o traslado sham evitó la expansión hasta el horizonte estudiado, mientras retirar sólo la otra entrada no la evitó. La primera lectura fuera de dominio fue T6368 y el primer estado 2 nuevo se registró en T6384 en el centro cuantitativo. No se estableció que ese nacimiento local fuese causa única de toda propagación. La retirada del ruido no restauró las funciones durante la ventana medida.')
para('En MAIN, una contribución de carga cero encontró al portador de contenido 140. Un desvío genérico selectivo conservó el uso posterior sin reenseñar el contenido; el sham no lo hizo. Es protección P0 diseñada, no regulación aprendida. La expansión asociada a una nueva señal de registro social y la colisión local son mecanismos distintos; no se atribuyen todas las pérdidas a ocupación, ruido o una supuesta muerte del ente.')
head('Cómo continuar sin reconstruir el proyecto')
for line in['python sistema/gestionar.py integrado-estado --vida E1_INTEGRADO_RECUPERACION_01','python sistema/gestionar.py integrado-externo --vida E1_INTEGRADO_RECUPERACION_01 --pasos 1','python sistema/gestionar.py integrado-panel --vida NUEVA_COPIA_DIAGNOSTICA','python sistema/gestionar.py bifurcar E1_INTEGRADO_CONTINUABLE_01 NUEVA_RAMA --modalidad CANDIDATE']:
    para(line,'Normal')
para('integrado-panel introduce sondas materiales; para diagnóstico use una copia identificada. integrado-experiencia ofrece adquisición, programación finita y una nueva experiencia social declarada. integrado-continuar avanza sólo el mundo nativo y declara la pausa del entorno externo. integrado-externo continúa ambos estados; al llegar al límite de 200 pasos de Pendulum exige un reinicio ambiental explícito, que no reinicia DEE. No cambie a habitat-externo para continuar estos metadatos de puente.')
para('La barrera de instrumentación permite únicamente el proceso ambiental exacto declarado y conserva el bloqueo de archivos históricos, laboratorio y evidencia en el camino normal. Los fallos de integración iniciales en T7440 fueron del adaptador de permisos y no fallos cognitivos. No se promovió ninguna vida al predeterminado: la rama complementaria es útil en un dominio acotado, pero la tolerancia al ruido y la estabilidad del selector siguen limitadas.')
head('Evidencia, edición y estado de validación')
para('Fuentes nuevas: CALCULOS.json y primarios 37–59, 67–95, 125–164 de INTEGRACION_COGNITIVA_SITUADA_E1_01, con resultados positivos, negativos y controles. El informe de análisis y su índice distinguen recálculo archivado, reproducción nativa, interacción externa y pruebas nuevas. Los intentos de rutas fallidos y los futuros adversos siguen almacenados localmente. NSM65 no se eleva por estos resultados y no se afirma lenguaje libre, conciencia ni estabilidad ilimitada.')
para('Esta edición modifica realmente el Word, integra el corte posterior y conserva las ediciones 1.0 y 1.4. La verificación estructural se registra en CAMBIOS_MANUAL.md y en el comprobante externo. Su nombre indica SIN_VALIDACION_VISUAL hasta que un renderizador disponible permita comprobar páginas. Una inspección XML o un documento Markdown no equivalen a esa validación visual.')

# Link all current chapter and appendix headings, using stable internal
# bookmarks. No static cached page numbers or duplicated title strings.
headings=[p for p in d.paragraphs if p.style.name=='Heading 1'and(p.text[:1].isdigit()or p.text.startswith('Apéndice '))]
idx=next(p for p in d.paragraphs if p.text=='Índice de consulta');cursor=idx._p
for i,h in enumerate(headings,1000):
    name='DCS11_s'+str(i);start=OxmlElement('w:bookmarkStart');start.set(qn('w:id'),str(i));start.set(qn('w:name'),name);end=OxmlElement('w:bookmarkEnd');end.set(qn('w:id'),str(i));h._p.insert(0,start);h._p.append(end)
    p=d.add_paragraph(style='TOCline');link=OxmlElement('w:hyperlink');link.set(qn('w:anchor'),name);r=OxmlElement('w:r');rp=OxmlElement('w:rPr');rs=OxmlElement('w:rStyle');rs.set(qn('w:val'),'Hyperlink');rp.append(rs);r.append(rp);text=OxmlElement('w:t');text.text=h.text;r.append(text);link.append(r);p._p.append(link);cursor.addnext(p._p);cursor=p._p
for sec in d.sections:
    sec.header.paragraphs[0].text='DEE COGNITIVE SYSTEM 1.1  |  MANUAL MAESTRO  |  ED. DOCUMENTAL 1.5'
    p=sec.footer.paragraphs[0];p.text='DCS11-MM-001  |  Ed. documental 1.5\t';p.add_run('Página ')
    for instruction in('PAGE','NUMPAGES'):
        if instruction=='NUMPAGES':p.add_run(' / ')
        run=p.add_run();begin=OxmlElement('w:fldChar');begin.set(qn('w:fldCharType'),'begin');code=OxmlElement('w:instrText');code.text=instruction;finish=OxmlElement('w:fldChar');finish.set(qn('w:fldCharType'),'end');run._r.extend([begin,code,finish])
    for p in sec.header.paragraphs+sec.footer.paragraphs:
        for run in p.runs:run.font.size=Pt(8)
settings=d.settings.element;update=settings.find(qn('w:updateFields'))
if update is None:update=OxmlElement('w:updateFields');settings.append(update)
update.set(qn('w:val'),'true');d.core_properties.version='1.5 documental / software1.1.0';d.core_properties.modified=datetime.now(timezone.utc);d.core_properties.comments='Actualización estructural comprobada. Validación visual registrada separadamente; sin cambios en el kernel o producto oficial.'
d.save(TARGET)
with ZipFile(TARGET)as z:
    bad=z.testzip()
    if bad:raise ValueError('Corrupt DOCX member '+bad)
    for n in z.namelist():
        if n.endswith('.xml'):ET.fromstring(z.read(n))
check=Document(TARGET);joined='\n'.join(p.text for p in check.paragraphs)
assert '22. Integración cognitiva situada' in joined and'Edición documental 1.5'in joined
assert not any('ECO_EXT'in p.text and'T6100'in p.text for p in check.paragraphs)
assert sha(SOURCE)==source_hash and sha(original)==original_hash
audit={'source':str(SOURCE),'source_sha256':source_hash,'original_1_0_unchanged_sha256':original_hash,'updated_word':str(TARGET),'updated_sha256':sha(TARGET),'bytes':TARGET.stat().st_size,'real_docx_modified':True,'structural_zip_and_xml_valid':True,'toc_internal_links':len(headings),'headers_and_footers_updated':True,'current_lives':[active,main,damaged,selected,recovered],'visual_validation':'NOT_YET_RUN_OR_NOT_AVAILABLE; see bounded renderer attempt, never inferred from XML','kernel_code_added':False,'software_version_unchanged':'1.1.0','document_edition':'1.5'}
(EV/'CAMBIOS_MANUAL_ESTRUCTURA.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(audit,ensure_ascii=False))
