"""Edición local de apartados afectados, originales conservados."""
from pathlib import Path
from datetime import datetime,timezone
from zipfile import ZipFile
import argparse,hashlib,json,xml.etree.ElementTree as ET
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2]
EV=ROOT/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
SOURCE=ROOT/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_5_INTEGRACION_SITUADA_SIN_VALIDACION_VISUAL.docx'
TARGET=ROOT/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_6_CICLO02_SIN_VALIDACION_VISUAL.docx'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def life(name):
    r=json.loads((ROOT/'sistema/estado/vidas'/name/'VIDA.json').read_text(encoding='utf8'))
    return {'vida':name,'tick':r['physical']['tick'],'snapshot':r['snapshot'],'sha256':r['snapshot_sha256'],'padre':r.get('parent')}

parser=argparse.ArgumentParser();parser.add_argument('--inspect',action='store_true');args=parser.parse_args()
if args.inspect:
    d=Document(SOURCE)
    print(json.dumps({'source':str(SOURCE),'sha256':sha(SOURCE),'intro':[p.text for p in d.paragraphs[:26]],
        'headings':[p.text for p in d.paragraphs if p.style.name.startswith('Heading')],
        'IC01':[p.text for p in d.paragraphs if p.text.startswith(('El predeterminado continúa','Una misma trayectoria complementaria','Las consecuencias reales','El circuito nativo','La dosis nominal','La comprobación material final','Esta edición modifica'))]},ensure_ascii=False,indent=2))
    raise SystemExit(0)

assert sha(SOURCE)=='b41e424beef3b9782750f7fe6008e9ea845e9f07532ea7c835371cc71c3c36bf'
source_hash=sha(SOURCE);d=Document(SOURCE)
# Sólo identificación editorial vigente; los capítulos históricos se preservan.
for p in d.paragraphs[:60]:
    if 'Edición documental 1.5'in p.text:p.text=p.text.replace('Edición documental 1.5','Edición documental 1.6')
    elif 'Este libro tiene edición documental 1.5.'in p.text:p.text=p.text.replace('Este libro tiene edición documental 1.5.','Este libro tiene edición documental 1.6.')
    elif p.text.startswith('La edición 1.5 conserva'):p.text='La edición 1.6 conserva los resultados anteriores e incorpora las funciones operativas de IC01 y los resultados alcanzados durante Consolidación y Evolución Real de E1 Ciclo 02. Distingue disponibilidad del sistema, conocimiento de cada vida y asistencia. El software continúa en 1.1.0 y el motor 4.5.0/v27 permanece congelado.'
for p in d.paragraphs:
    if 'Este libro tiene edición documental 1.5.'in p.text:p.text=p.text.replace('Este libro tiene edición documental 1.5.','Este libro tiene edición documental 1.6.')
    if p.text.startswith('La edición 1.5 conserva la integración documental anterior'):
        p.text='Como antecedente, la edición1.5 integró los cortes anteriores, corrigió Hábitat a ECO_EXT_01 T6167 y añadió IC01. La edición vigente1.6 incorpora Ciclo02, sus vidas y capacidades operativas acotadas en el capítulo23 y en la ficha CONTINUIDAD_CICLO02.json. Los capítulos anteriores conservan su genealogía; un máximo histórico no reemplaza un estado actual. El predeterminado sigue protegido y el motor no cambió.'

anchor=next(p for p in d.paragraphs if p.text.startswith('Apéndice A.'))
# Sustituir únicamente el apartado generado por esta campaña, no su genealogía.
old=next((p for p in d.paragraphs if p.text=='23 Consolidación y evolución de E1 Ciclo 02'),None)
if old is not None:
    node=old._p
    while node is not None and node is not anchor._p:
        nxt=node.getnext();node.getparent().remove(node);node=nxt
def para(text,style='Normal'):
    p=d.add_paragraph(text,style=style);anchor._p.addprevious(p._p);return p
h=para('23 Consolidación y evolución de E1 Ciclo 02','Heading 1')
b=OxmlElement('w:bookmarkStart');b.set(qn('w:id'),'2026002');b.set(qn('w:name'),'DCS11_CICLO02');h._p.insert(0,b)
b=OxmlElement('w:bookmarkEnd');b.set(qn('w:id'),'2026002');h._p.append(b)
para('Disponibilidad operativa y atribución','Heading 2')
para('Las cinco funciones de IC01 se admitieron como capacidades operativas oficiales dentro de sus dominios comprobados. Se reutilizan las implementaciones y los controles causales anteriores; no se repitió la campaña para cambiar su categoría. El mismo gestor permite seleccionar, cargar, utilizar, guardar y continuar vidas concretas. Esta admisión no constituye una promoción global ni atribuye a todos los entes el contenido de la biblioteca.')
para('La adquisición de una referencia a partir de consecuencias reales y su utilización posterior es una capacidad contextual. No se declara todavía política competente de control. La comunicación física y su actualización dependen de los contenidos adquiridos en las vidas documentadas. La recuperación social genérica es una función asistida P0/R0 cuyo contenido depende de la historia física. La continuidad y el puente son instrumentación. El selector por consecuencias conserva su dominio finito, sus errores y sus pérdidas posteriores; no se lo atribuye actualmente a toda continuación.')
para('Vida principal y continuidad','Heading 2')
current=life('E1_CICLO02_MAIN')
para('El predeterminado E1_SOCIAL_11 permanece protegido en T3154. Antes de evaluar se seleccionó como padre E1_INTEGRADO_RECUPERACION_01 T17155, por conservar comparación, acceso social alternativo y puente persistente. E1_CICLO02_MAIN es su bifurcación exacta; no mezcla memorias de otras ramas. Las primeras operaciones cargaron, utilizaron, guardaron, recargaron y continuaron ese estado en procesos ordinarios separados. El futuro adverso de E1_INTEGRADO_MAIN T3899 se conserva intacto.')
para('Corte actual de E1_CICLO02_MAIN: T'+str(current['tick'])+'. El localizador autorizado, hash completo, interfaces, colas y progreso están en CONTINUIDAD_CICLO02.json junto a este manual y en la ficha operativa de la vida. Una receta nueva o un archivo de análisis no sustituye este estado vivido.')
para('Uso de las funciones admitidas','Heading 2')
for line in ['python sistema/gestionar.py integrado-estado --vida E1_CICLO02_MAIN',
             'python sistema/gestionar.py integrado-externo --vida E1_CICLO02_MAIN --pasos 1',
             'python sistema/gestionar.py guardar --vida E1_CICLO02_MAIN',
             'python sistema/gestionar.py bifurcar E1_CICLO02_MAIN COPIA_DIAGNOSTICA --modalidad DIAGNOSTIC_COPY']:
    para(line)
para('integrado-experiencia programa experiencias declaradas o mecanismos finitos. integrado-continuar avanza el mundo nativo manteniendo explícitamente pausado el entorno externo. integrado-panel introduce materia: para diagnóstico utilice una copia. integrado-recuperar-social sólo se admite en la frontera concreta del protocolo de consulta genérica; no es una reparación universal ni una iniciativa aprendida. Consulte USO_CAPACIDADES_ADMITIDAS_CICLO02.md para los parámetros y limitaciones.')
facts=EV/'RESULTADOS_INCORPORADOS.json'
if facts.exists():
    for section in json.loads(facts.read_text(encoding='utf8'))['manual_sections']:
        para(section['title'],'Heading 2')
        for text in section['paragraphs']:para(text)
para('La incorporación cambia la disponibilidad ejecutable, no los hechos históricos. Los resultados negativos permanecen con sus mundos y controles. No se certifica una mente general, dominio de 65 significados ni regulación general por estas admisiones. Los datos y el código decisivo están indexados en la entrega de análisis de Ciclo 02; los estados completos permanecen localmente.')

# Añadir un enlace a la sección actual sin rehacer el índice histórico.
links=d._element.xpath('.//w:hyperlink[@w:anchor="DCS11_CICLO02"]')
if not links:
    toc=next(p for p in d.paragraphs if p.style.name=='TOCline'and ''.join(x.text or''for x in p._p.xpath('.//w:t')).startswith('22.'))
    p=d.add_paragraph(style='TOCline');link=OxmlElement('w:hyperlink');link.set(qn('w:anchor'),'DCS11_CICLO02')
    r=OxmlElement('w:r');t=OxmlElement('w:t');t.text='23 Consolidación y evolución de E1 Ciclo 02';r.append(t);link.append(r);p._p.append(link);toc._p.addnext(p._p)
for section in d.sections:
    for part in(section.header,section.footer):
        for p in part.paragraphs:
            for r in p.runs:
                # Do not assign text to PAGE/NUMPAGES field-only runs: doing
                # so removes their OOXML instructions even when text is empty.
                if '1.5'in r.text:r.text=r.text.replace('1.5','1.6')
settings=d.settings.element;u=settings.find(qn('w:updateFields'))
if u is None:u=OxmlElement('w:updateFields');settings.append(u)
u.set(qn('w:val'),'true')
d.core_properties.version='1.6 documental / software1.1.0';d.core_properties.modified=datetime.now(timezone.utc)
d.save(TARGET)
with ZipFile(TARGET)as z:
    assert z.testzip()is None
    for n in z.namelist():
        if n.endswith('.xml'):ET.fromstring(z.read(n))
    final_fields=sum(z.read(n).count(b'PAGE')for n in z.namelist()if n.startswith('word/footer')and n.endswith('.xml'))
with ZipFile(SOURCE)as z:
    source_fields=sum(z.read(n).count(b'PAGE')for n in z.namelist()if n.startswith('word/footer')and n.endswith('.xml'))
assert source_fields>0 and final_fields==source_fields
assert sha(SOURCE)==source_hash
out={'source':str(SOURCE),'source_sha256_unchanged':source_hash,'updated_word':str(TARGET),'sha256':sha(TARGET),'bytes':TARGET.stat().st_size,
     'edition':'1.6','software':'1.1.0','main':current,'zip_xml_verified':True,
     'footer_page_field_instructions_preserved':final_fields,
     'visual_validation':'NOT_YET_VALIDATED; a bounded renderer attempt must be recorded separately',
     'kernel_rules_or_code_added':False}
(EV/'CAMBIOS_MANUAL_ACTUAL.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False))
