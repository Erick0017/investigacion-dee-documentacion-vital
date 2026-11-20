"""Stage complete existing Manual and Compendium from closed PI04 facts.

No engine/life import, execution, publication or adoption. Historical body
elements are verified byte-exact except explicitly current front matter.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,re,zipfile
from lxml import etree as E
P=Path(__file__).resolve().parents[1];R=P.parents[2];C=R/'DEE Cognitive 2.0';D=P/'documentos'
NAME='DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
MAN=C/NAME;COMP=R/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'
EXPECTED_MAN='86e72b0d35e340effeb83c9fd018ad0ab3bf1fe2e4aa1d6fa12fea2926bd243f'
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
TITLE='47 PI04 Contingencia información histórica y coordinación funcional'
def sha(b):return hashlib.sha256(b).hexdigest()
def module(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def core(u,old,title,description):
 root=E.fromstring(old);CP='{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}';DC='{http://purl.org/dc/elements/1.1/}';DT='{http://purl.org/dc/terms/}'
 for tag,value in((DC+'title',title),(DC+'description',description),(CP+'version','1.31'),(CP+'revision','31'),(DT+'modified',datetime.datetime.now(datetime.timezone.utc).isoformat())):
  node=root.find(tag)
  if node is None:node=E.SubElement(root,tag)
  node.text=value
 return u.xml(root)
def main(a):
 if not a.artifact_marker_completed:raise ValueError('The skill authoring marker must have succeeded exactly once for this PI04 operation')
 facts=P/'control/CIERRE_CIENTIFICO_PI04.json';data=facts.read_bytes();m=json.loads(data)
 if m.get('closed_for_authoring')is not True:raise ValueError('Closed scientific facts required')
 if sha(MAN.read_bytes())!=EXPECTED_MAN or sha(COMP.read_bytes())!=m['compendium_before_sha256']:raise ValueError('Prior original changed; no silent overwrite')
 active_bytes=(C/'sistema/estado/ACTIVO.json').read_bytes();active=json.loads(active_bytes)
 current=json.loads((C/'sistema/estado/vidas'/active['life_id']/'VIDA.json').read_text(encoding='utf8'))
 if active['life_id']!=m['principal']['life_id']or current['physical']['tick']!=m['principal']['tick']or current['physical']['N']!=m['principal']['N']:raise ValueError('Current selected identity or actual saved cut differs; documentary promotion is forbidden')
 lib=P.parent/'PROGRESION_INTEGRADA_03/codigo/revisiones/EDITORIAL_PI02_EXACTO'
 u=module(lib/'actualizacion_manual_PI02.py','PI04_document_helpers');f=module(lib/'actualizacion_manual_PI02_final.py','PI04_document_final_helpers')
 D.mkdir(exist_ok=True);staged=D/'staging_1_31_R01';staged.mkdir(exist_ok=False)
 backups={'Manual':u.preserve(MAN,D/'respaldo_1_30'),'Compendium':u.preserve(COMP,D/'respaldo_1_30')}
 with zipfile.ZipFile(MAN)as z:
  root=E.fromstring(z.read('word/document.xml'));body=root.find(W+'body');old=list(body);before={id(e):E.tostring(e)for e in old};allowed=set();ps=list(body.iter(W+'p'))
  def exact_at(index,value):
   p=ps[index-1];top=p
   while top.getparent()is not body:top=top.getparent()
   allowed.add(id(top));u.settext(p,value,verbatim=True)
  exact_at(9,u.text(ps[8]).replace('1.30','1.31'))
  for index,key in((10,'cover_summary'),(14,'resume1'),(15,'resume2'),(16,'resume3'),(17,'resume4'),(74,'release_cut'),(82,'state_of_edition'),(85,'review_scope')):exact_at(index,m[key])
  exact_at(68,'DCS11-MM-001 / Edición documental 1.31 / Cierre PI04 / '+m['cut_date_local'])
  exact_at(76,'Mismo Manual rector y nombre operativo 1_21 por compatibilidad. La edición 1.30 y el Compendio anterior se preservan literalmente en documentos/respaldo_1_30 de PI04. Los capítulos 1–46 y los apéndices mantienen sus hechos; el capítulo 47 incorpora resultados, negativos, medios de uso y continuidad de PI04.')
  exact_at(683,u.text(ps[682]).replace('vigente 1.30','vigente 1.31'))
  heading=next(p for p in old if p.tag==W+'p'and u.h1(p)and u.text(p).startswith('46 PI03 '))
  h2=next(p for p in old if p.tag==W+'p'and u.text(p).startswith('46.1 '))
  appendix=next(p for p in old if p.tag==W+'p'and u.h1(p)and u.text(p)=='Apéndice A. Inventario histórico de las 73 entradas')
  ordinary=next(p for p in old[old.index(heading)+1:old.index(appendix)]if p.tag==W+'p'and len(u.text(p))>180 and not u.h1(p)and not re.match(r'^46\.',u.text(p)))
  title=f.paragraph(u,heading,TITLE);u.insert_bookmark(root,title,'PI04_CIERRE');appendix.addprevious(title)
  for section in m['sections']:
   if not section['title'].startswith('47.'):raise ValueError('Explicit47.x sections required')
   appendix.addprevious(f.paragraph(u,h2,section['title']))
   for paragraph in section['paragraphs']:
    if not paragraph.strip()or'[[PENDIENTE' in paragraph:raise ValueError('Unresolved prose')
    appendix.addprevious(f.paragraph(u,ordinary,paragraph))
   for block in section.get('commands',[]):appendix.addprevious(f.command_block(u,ordinary,block))
  appendix.addprevious(f.paragraph(u,ordinary,'Fuentes PI04: '+'; '.join(m['sources'])+'. Los diarios pertenecen al investigador y no alimentan las decisiones del ente.'))
  index=next(p for p in old if p.tag==W+'p'and not u.h1(p)and u.text(p)=='46 PI03 Reproducción de capacidades y crédito por consecuencias diferidas')
  index.addnext(u.index_entry(index,TITLE,'PI04_CIERRE'))
  for e in old:
   if id(e)not in allowed and(e.getparent()is not body or E.tostring(e)!=before[id(e)]):raise ValueError('Unapproved historical body change')
  edits={'word/document.xml':u.xml(root),'docProps/core.xml':core(u,z.read('docProps/core.xml'),'DEE Cognitive 2.0 Manual Maestro Edición 1.31 PI04',m['core_description'])}
  for name in z.namelist():
   if re.fullmatch(r'word/(header|footer)\d+\.xml',name):
    part=E.fromstring(z.read(name));changed=False
    for t in part.iter(W+'t'):
     if t.text:
      new=t.text.replace('ED. 1.30','ED. 1.31').replace('Ed. documental 1.30','Ed. documental 1.31').replace('PI03 cierre','PI04 cierre');changed|=new!=t.text;t.text=new
    if changed:
     out=u.xml(part)
     if u.fields(z.read(name))!=u.fields(out):raise ValueError('Field instructions changed')
     edits[name]=out
 manual=u.package(MAN,staged/NAME,edits)
 with zipfile.ZipFile(COMP)as z:
  root=E.fromstring(z.read('word/document.xml'));body=root.find(W+'body');old=list(body);before=[E.tostring(e)for e in old];ps=[p for p in old if p.tag==W+'p'];head=next(p for p in ps if u.h1(p));ordinary=next(p for p in ps if len(u.text(p))>180 and not u.h1(p));sec=body.find(W+'sectPr')
  title=f.paragraph(u,head,'PI04 Contingencia e información histórica y coordinación');u.insert_bookmark(root,title,'PI04_CIERRE_COMPENDIO')
  first_title=next(p for p in ps if u.h1(p))
  first_title.addnext(f.paragraph(u,ordinary,'Corte acumulativo PI04 '+m['cut_date_local']+'. Se conserva la base histórica y se añade su actualización al final, con enlace en el índice. El Manual rector Cognitive es la edición interna 1.31; el nombre compatible del archivo continúa terminado en 1_21. '+m['compendium_current_summary']))
  additions=[title]+[f.paragraph(u,ordinary,p)for p in m['compendium_paragraphs']]
  for item in additions:
   if sec is not None:sec.addprevious(item)
   else:body.append(item)
  idx=next(p for p in ps if not u.h1(p)and u.text(p)=='PI03 Reproducción y continuidad');idx.addnext(u.index_entry(idx,'PI04 Contingencia y coordinación','PI04_CIERRE_COMPENDIO'))
  if any(e.getparent()is not body or E.tostring(e)!=b for e,b in zip(old,before)):raise ValueError('Compendium historical elements changed')
  comp=u.package(COMP,staged/COMP.name,{'word/document.xml':u.xml(root),'docProps/core.xml':core(u,z.read('docProps/core.xml'),'Compendio Maestro de Mecanismos y Resultados DEE','Actualización PI04. '+m['core_description'])})
 if sha(MAN.read_bytes())!=EXPECTED_MAN or sha(COMP.read_bytes())!=m['compendium_before_sha256']or(C/'sistema/estado/ACTIVO.json').read_bytes()!=active_bytes or facts.read_bytes()!=data:raise ValueError('A protected input changed during staging')
 proof={'schema':'DEE.PI04.complete_document_staging.1.31','Manual':manual,'Compendium':comp,'prior_literal_backups':backups,'principal':m['principal'],'source_facts_sha256':sha(data),'body_history_preserved_exact_except_current_front':True,'new_Native_ticks':0,'publication_performed':False,'visual_QA':'PENDING_NOT_CLAIMED'}
 with(D/'ACTUALIZACION_DOCUMENTAL_PI04_1_31.json').open('x',encoding='utf8')as out:json.dump(proof,out,ensure_ascii=False,indent=2)
 print(json.dumps(proof,ensure_ascii=False))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--artifact-marker-completed',action='store_true');main(ap.parse_args())
