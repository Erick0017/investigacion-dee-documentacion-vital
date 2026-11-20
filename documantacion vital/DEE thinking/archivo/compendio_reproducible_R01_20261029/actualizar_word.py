"""Actualización local del compendio existente; conserva su explicación científica."""
from pathlib import Path
import argparse,datetime,hashlib,json,re,shutil
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
B=Path(__file__).resolve().parent
P=argparse.ArgumentParser();P.add_argument('--catalogo',type=Path,required=True);P.add_argument('--zip',type=Path,required=True);P.add_argument('--verificacion',type=Path,required=True);P.add_argument('--output',type=Path,required=True);a=P.parse_args()
root=B.parents[1];original=root/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
cat=load(a.catalogo);verification=load(a.verificacion);d=Document(original)
def para(text='',style=None,before=None):
 if 'reproducir.py'not in text and not re.fullmatch(r'[0-9a-f]{64}',text):
  text=re.sub(r'(?<=[,;])(?=\S)',' ',text)
  text=re.sub(r'(?<=[.!?])(?=[A-ZÁÉÍÓÚÑ])',' ',text)
  text=re.sub(r'\b(de|del|por|en|un|una|con|sin|los|las|el|al|otro|esta|sus|para|la|este|mismo|cada)(?=(?:Native|ZIP|DEE|Cognitive|CPython|NumPy|Python|R01|CATALOGO|ID|E1))',r'\1 ',text)
  text=re.sub(r'(?<=[A-Za-zÁÉÍÓÚÑáéíóúñ0-9])(?=\()',' ',text)
  text=text.replace('x 64','x64').replace('NativeM','Native M').replace('Native32','Native 32')
 p=d.add_paragraph(text,style)
 if before is not None:before._p.addprevious(p._p)
 return p
BOOKMARK_COUNTER=5000
def bookmark(p,name):
 global BOOKMARK_COUNTER
 BOOKMARK_COUNTER+=1
 start=OxmlElement('w:bookmarkStart');start.set(qn('w:id'),str(BOOKMARK_COUNTER));start.set(qn('w:name'),name)
 end=OxmlElement('w:bookmarkEnd');end.set(qn('w:id'),start.get(qn('w:id')));p._p.insert(0,start);p._p.append(end)
def link(p,text,anchor):
 h=OxmlElement('w:hyperlink');h.set(qn('w:anchor'),anchor);r=OxmlElement('w:r');pr=OxmlElement('w:rPr');u=OxmlElement('w:u');u.set(qn('w:val'),'single');pr.append(u);r.append(pr);t=OxmlElement('w:t');t.text=text;r.append(t);h.append(r);p._p.append(h)
def format_table(table,widths):
 table.autofit=False
 for col,w in zip(table.columns,widths):col.width=Inches(w)
 for i,row in enumerate(table.rows):
  for cell,w in zip(row.cells,widths):
   cell.width=Inches(w);pr=cell._tc.get_or_add_tcPr();borders=OxmlElement('w:tcBorders')
   for name in('top','left','bottom','right','insideH','insideV'):
    edge=OxmlElement('w:'+name);edge.set(qn('w:val'),'single');edge.set(qn('w:sz'),'4');edge.set(qn('w:color'),'D9D9D9');borders.append(edge)
   pr.append(borders);margins=OxmlElement('w:tcMar')
   for edge in('top','bottom','left','right'):
    x=OxmlElement('w:'+edge);x.set(qn('w:w'),'90');x.set(qn('w:type'),'dxa');margins.append(x)
   pr.append(margins)
   if i==0:
    fill=OxmlElement('w:shd');fill.set(qn('w:fill'),'E6E6E6');pr.append(fill)
   for p in cell.paragraphs:
    p.paragraph_format.space_after=Pt(3)
    for r in p.runs:r.font.size=Pt(9.5);r.font.bold=i==0
  if i==0:
   header=OxmlElement('w:tblHeader');row._tr.get_or_add_trPr().append(header)
  # Las filas pueden continuar en otra página cuando sea necesario.
  for x in list(row._tr.get_or_add_trPr()):
   if x.tag==qn('w:cantSplit'):row._tr.get_or_add_trPr().remove(x)
def status(id):return verification.get('mechanisms',{}).get(id,{})
def label(id):
 r=status(id)
 return r.get('summary','Material recuperado; ejecución no comprobada en este corte')
def compact(s,n=280):
 if not isinstance(s,str):s=json.dumps(s,ensure_ascii=False)
 return s if len(s)<=n else s[:n-1].rsplit(' ',1)[0]+'…'
# Las setenta fichas completas se conservan dentro del registro único delZIP.
# El Word mantiene sus identificadores enlazados y su alcance científico.
source_mode=False;source_id=None;source_ids={r['id']for r in load(B/'FUENTES_DOCUMENTALES.json')}
for p in list(d.paragraphs):
 t=p.text.replace('\u200b','').strip()
 if t=='Índice de fuentes, primarios y localizadores':source_mode=True;continue
 if source_mode and t=='Cobertura y límite documental':source_mode=False
 if not source_mode:continue
 if t in source_ids:source_id=p;continue
 if t.startswith(('Archivo:','SHA-256:','Localizador:')):
  p._p.getparent().remove(p._p)
 elif t.startswith('Alcance:')and source_id is not None:
  run=source_id.add_run(' — '+t[8:]);run.bold=False;p._p.getparent().remove(p._p)
 elif t.startswith('Las rutas de CPC conservan'):
  p.text='Las rutas históricas, hashes y localizadores de estas setenta fuentes se conservan completos en CATALOGO.json → documentary_sources. La lista siguiente mantiene los identificadores citados y su alcance. Es procedencia histórica, no una lista de archivos externos que deban importarse para ejecutar los mecanismos verificados delZIP.'
# Edición localizada de los datos que cambiaron desde la edición documental.
for p in d.paragraphs:
 if p.text.startswith('No se ejecutaron nuevos experimentos para redactarlo.'):
  p.text='La primera edición se redactó a partir de resultados existentes. Esta edición R01 añade la recuperación de materiales, recálculos y reproducciones técnicas sobre copias aisladas. No inicia una investigación nueva, no fusiona biografías y no modifica la vida vigente de Cognitive 2.0. El alcance efectivamente comprobado se identifica por mecanismo y modalidad.'
 if 'Corte editorial: 28 de octubre de 2026'in p.text:p.text=p.text.replace('Corte editorial: 28 de octubre de 2026','Edición reproducible R01 · 29 de octubre de 2026')
intro=next(p for p in d.paragraphs if p.text=='Cómo leer la evidencia')
intro.paragraph_format.page_break_before=False
title=para('Biblioteca reproducible R01',style='Heading 1',before=intro);bookmark(title,'r01_inicio')
para('Esta edición acompaña el ZIP consolidado que permite recuperar protocolos históricos sin abrir sus distribuciones originales. Las doce familias científicas de la edición anterior se conservan; los materiales ejecutables y su cobertura se localizan en el catálogo incorporado al final de este documento.',before=intro)
para('Archivo: DEE_COMPENDIO_MECANISMOS_REPRODUCIBLES_R01.zip',before=intro)
para('Tamaño: '+format(a.zip.stat().st_size,',').replace(',',' ')+' bytes. SHA256 calculado después de cerrar el ZIP:',before=intro)
p=para(hashlib.sha256(a.zip.read_bytes()).hexdigest(),before=intro)
for r in p.runs:r.font.name='Consolas';r.font.size=Pt(9)
para(verification.get('coverage_text','La cobertura se detalla por ID en el catálogo de esta edición.'),before=intro)
para('Requisitos: Windows x64, CPython 3.13 x64 para el motor oficial y su ABI histórico. Los protocolos de Pendulum necesitan además CPython 3.12 x64. Los intérpretes no se distribuyen. Los wheels nativos, las versiones de NumPy de cada ABI y las dependencias del puente están dentro del paquete; no se requiere instalar Cognitive ni acceder a sus carpetas privadas.',before=intro)
para('La colección conserva mecanismos preparados, contenidos adquiridos, instrumentos y negativos causales. No declara 101 capacidades cognitivas independientes ni un ente que las reúna todas. Variantes, consultas, bifurcaciones y repeticiones técnicas mantienen sus denominadores y su dependencia histórica.',before=intro)
para('Inicio y reproducción independiente',style='Heading 2',before=intro)
para('Extraiga el ZIP en una ruta corta y escribible. Abra INICIAR_REPRODUCCION.bat para consultar el catálogo sin ejecutar física. Para preparar un entorno local use la ruta de su CPython 3.13; el lanzador instala únicamente el wheel incluido y verifica sus bytes. No modifica la instalación global.',before=intro)
commands=[
'python reproducir.py integridad',
'python reproducir.py preparar --python "C:\\Python313\\python.exe"',
'.entorno\\Scripts\\python.exe -I -B reproducir.py ejecutar M001 --out resultados\\M001',
'.entorno\\Scripts\\python.exe -I -B reproducir.py recalcular M038 --out resultados\\CPC9',
'.entorno\\Scripts\\python.exe -I -B reproducir.py todos --sector paisaje --out resultados\\paisaje --reanudar']
for text in commands:
 p=para(text,before=intro);p.paragraph_format.space_after=Pt(5)
 for r in p.runs:r.font.name='Consolas';r.font.size=Pt(9)
para('C:\\Python313\\python.exe es un ejemplo: sustitúyalo por el intérprete instalado. Use --external-python con la rutaCPython 3.12 en los protocolos que el catálogo marca como externos. Las consultas del menú no eligen un lector según la respuesta esperada.',before=intro)
para('El primer uso materializa los objetos verificados en resultados\\_materializado. Allí aparecen codigo_comun y sectores con sus nombres legibles. CATALOGO.json registra rutas, procedencia, hashes, variantes, comandos, estados iniciales, resultados esperados y límites. Los objetos iguales comparten almacenamiento, pero cada copia experimental recibe su propia historia. No edite las referencias; use otra carpeta de resultados para un intento nuevo.',before=intro)
para('La opción todos ejecuta sólo protocolos que tienen rutaNative o instrumental anunciada; no convierte los pendientes en ejecutables. La opción recalcular todos recorre los recálculos disponibles. Reanudar conserva las ejecuciones ya terminadas; no devuelve una vida a un pasado favorable. Para inspección sin ticks utilice materializar --out resultados\\inspeccion.',before=intro)
para('Validación y límites de independencia',style='Heading 2',before=intro)
para(verification.get('validation_text','La verificación se realizó desde una extracción limpia y se detalla en el catálogo de cobertura.'),before=intro)
para('El auditor recursivo controla accesos y subprocesosPython, y restringe las escrituras al árbol nuevo de resultados y su temporal exclusivo. No es una máquina virtual: el cargador DLL y fopen directo desdeC++ no son interceptados por CPython. La independencia comprobada corresponde a los protocolos incluidos, sus bytes congelados y las rutas efectivamente utilizadas, no a una certificación general de aislamiento del sistema operativo.',before=intro)
for text in verification.get('important_pending',[]):para(text,before=intro)
# Referencia cruzada por familia dentro de la explicación científica conservada.
for family in range(1,13):
 anchor=next((p for p in d.paragraphs if p.style.name=='Heading 1'and p.text.startswith(str(family)+'. ')),None)
 if anchor:
  ids=[m['id']for m in cat['mechanisms']if str(family)in list(map(str,m.get('word_families',[])))]
  p=para('Materiales R01 de esta familia: '+', '.join(ids)+'. La ubicación y modalidad de comprobación de cadaID se detallan en el catálogo reproducible.');anchor._p.addnext(p._p)
# Índice interno adicional, sin sustituir los enlaces históricos existentes.
index=next(p for p in d.paragraphs if p.text=='Índice navegable')
p=para('');index._p.addnext(p._p);link(p,'Biblioteca R01 requisitos y ejecución','r01_inicio')
p=para('');index._p.addnext(p._p);link(p,'Catálogo de mecanismos y cobertura comprobada','r01_catalogo')
# Catálogo funcional, no otro índice de rutas históricas obligatorias.
h=para('Catálogo reproducible y cobertura comprobada',style='Heading 1');h.paragraph_format.page_break_before=True;bookmark(h,'r01_catalogo')
para('Cada entrada remite a su directorio lógico después de materializar. El bloque correspondiente de CATALOGO.json conserva la relación completa con variantes, código, configuración, estado, evidencia y controles. Los documentos históricos citados antes son procedencia; no se necesitan para ejecutar un mecanismo que aquí haya quedado verificado.')
t=d.add_table(rows=1,cols=4)
for c,text in zip(t.rows[0].cells,('Sector','Entradas','Variantes','Materiales internos')):c.text=text
for sector in('core','paisaje','mente','apd','apd_extra'):
 ms=[m for m in cat['mechanisms']if m['sector']==sector];r=t.add_row().cells
 for c,text in zip(r,(sector,str(len(ms)),str(sum(len(m.get('variants',[]))for m in ms)),'sectores/'+sector)):c.text=text
format_table(t,[1.0,.65,.7,4.1])
para('Una entrada es una realización o un contrato reproducible con su dominio. El catálogo reúne preparaciones relacionadas cuando comparten mecanismo; tampoco suma controles como habilidades distintas. El recuento de doce familias sirve para navegar la evidencia y no estima una capacidad general.')
para('Los contratos finitos mantienen sus soportes, suministros, calendario y lector declarados. Su reproducción técnica no integra automáticamente esas funciones en una vida ni repite necesariamente toda su ontogenia. Los límites técnicos completos y los controles disponibles permanecen en la ficha del mismoID enCATALOGO.json. Para una selección nueva utilice otro directorio de resultados y conserve sus estados adversos.')
for m in cat['mechanisms']:
 p=para(m['id']+' '+m['name'],style='Heading 2');bookmark(p,'r01_'+m['id'])
 para(compact(m.get('function','Realización histórica con materiales y controles conservados.'),520))
 para('Cobertura comprobada: '+label(m['id'])+'. Campañas: '+', '.join(m.get('campaigns',[]))+'. Variantes o condiciones incluidas: '+str(len(m.get('variants',[])))+'.')
 block=m.get('native')or m.get('recalc');command='ejecutar'if m.get('native')else'recalcular'
 para('Uso: reproducir.py '+command+' '+m['id']+' --out resultados\\'+m['id']+'. Materiales: sectores/'+m['sector']+'; localizador exacto: CATALOGO.json → mechanisms → '+m['id']+'.')
 limits=m.get('limitations',[])
 if isinstance(limits,str):limits=[limits]
 if m['sector']=='core':
  limits=[]
  if m['id']=='M034':limits=['El puerto4.5 se contrasta con los observables históricos locales y con estados completos de referencia del puerto. El expediente histórico no conserva hashes finales completos: no se afirma identidad de ese microestado histórico.']
  elif m['id']=='M038':limits=['K65 es un repertorio de formas físicas. Sus barridos no prueban65 significadosNSM; los registros tardíos son observaciones parciales y no snapshots continuables.']
  elif m['id']=='M046':limits=['Se conserva como resultado negativo de un método de descubrimiento. No es una capacidad cognitiva positiva.']
 if limits:para('Dominio y asistencia: '+compact(' '.join(map(str,limits)),420))
 row=status(m['id'])
 if row.get('pending'):para('Pendiente concreto: '+compact(row['pending'],500))
para('Conservar y ampliar la biblioteca',style='Heading 1')
para('La vida vigente de Cognitive 2.0 permanece fuera de los replays y no se modifica. Los protocolos reconstruyen posibilidades o continúan estados históricos identificados; no transfieren esos conocimientos al activo. Para ampliar esta biblioteca conserve nuevos protocolos, estados completos, lectores y controles bajo otroID o una revisión declarada. Recalcule el catálogo y repita las comprobaciones afectadas antes de sellar otra edición.')
for style in d.styles:
 if style.type==1 and(style.name.startswith('Heading')or style.name in('Title','Subtitle')):
  style.font.color.rgb=RGBColor(0,0,0)
for p in d.paragraphs:
 for r in p.runs:
  if 'No se ejecutó de nuevo para el compendio.'in r.text:r.text=r.text.replace('No se ejecutó de nuevo para el compendio.','La edición documental inicial no lo repitió; las reproducciones deR01 se identifican porID en el catálogo.')
for p in d.paragraphs:
 if p.style.name.startswith('Heading')or p.style.name=='Title':
  for r in p.runs:r.font.color.rgb=RGBColor(0,0,0)
for table in d.tables:
 if table.rows:
  for cell in table.rows[0].cells:
   for paragraph in cell.paragraphs:paragraph.paragraph_format.keep_with_next=True
for sec in d.sections:
 p=sec.footer.paragraphs[0];p.text='Compendio DEE · Biblioteca reproducible R01 · Página '
 field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');p._p.append(field)
 for r in p.runs:r.font.size=Pt(8.5);r.font.color.rgb=RGBColor(0,0,0)
settings=d.settings.element;upd=settings.find(qn('w:updateFields'))
if upd is None:upd=OxmlElement('w:updateFields');settings.append(upd)
upd.set(qn('w:val'),'true')

# Clarificación editorial de las comprobaciones posteriores.
for p in d.paragraphs:
 if p.text.startswith('El compendio sintetiza las fuentes primarias y resultados identificados en este índice.'):
  p.text='La síntesis documental inicial reunió las fuentes de este índice sin repetir física. La edición R01 añade las reproducciones y recálculos identificados por mecanismo en el catálogo siguiente. El ZIP no es una copia íntegra de toda la telemetría ni un respaldo de la vida actual; tampoco certifica todas las familias. Las dieciséis filas históricas D del Core conservan su pendiente de recuperación amplia donde no existe una prueba posterior suficiente. Los materiales recuperados y las exclusiones concretas se declaran en CATALOGO.json.'
 for run in p.runs:
  text=run.text
  text=text.replace('Lectura dirigida; no se ejecutó el motor ni se avanzaron ticks','Lectura documental inicial sin ticks; véase la comprobación R01 del mecanismo correspondiente')
  text=re.sub(r'(?<=[a-záéíóúñ])(?=(?:Native|CPython|NumPy|Python|C\\+\\+|CATALOGO|NSM|R01|ZIP|ID|P0|P1|P2|R0|R1|R2))',' ',text)
  text=text.replace('deE1','de E1').replace('delZIP','del ZIP').replace('enCATALOGO','en CATALOGO').replace('deR01','de R01')
  text=re.sub(r'(?<![0-9])1 comprobaciones del informe coinciden','1 comprobación del informe coincide',text)
  text=re.sub(r'(?<=[a-záéíóúñ])(?=(?:[A-Z]{2,}|T[0-9]{3}|M[0-9]{3}|[CD]:|Runtime))',' ',text)
  text=re.sub(r'(?<=[a-záéíóúñ])\.(?=[0-9])','. ',text)
  text=re.sub(r'(?<=R2)(?=[a-z])',' ',text)
  text=re.sub(r'(?<=[0-9])(?=significados)',' ',text)
  text=text.replace('wall 11','wall11').replace('wall 17','wall17').replace('puerto4.5','puerto 4.5').replace('prueban65','prueban 65')
  text=text.replace('; 0 comprobaciones del informe coinciden','; verificación contractual según el informe de ejecución incluido')
  run.text=text
 visible=''.join(p._p.itertext())
 if 'Volver al índice' in visible:
  previous=p._p.getprevious()
  if previous is not None and previous.tag==qn('w:p'):
   from docx.text.paragraph import Paragraph
   Paragraph(previous,p._parent).paragraph_format.keep_with_next=True

a.output.parent.mkdir(parents=True,exist_ok=True);d.save(a.output)
print(json.dumps(dict(path=str(a.output),bytes=a.output.stat().st_size,paragraphs=len(d.paragraphs),tables=len(d.tables)),ensure_ascii=False))
