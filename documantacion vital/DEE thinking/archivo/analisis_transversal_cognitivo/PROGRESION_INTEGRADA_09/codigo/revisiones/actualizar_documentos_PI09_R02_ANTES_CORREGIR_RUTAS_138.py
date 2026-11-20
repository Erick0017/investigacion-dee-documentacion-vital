"""Surgical complete DOCX staging/publication. No DEE/Word import.

Root's already executed documents edit/2DOCX marker covers the same two outputs.
--marker-confirmed acknowledges it; this helper never repeats the marker. Default
is read-only. Old chapters1..53 and appendices are kept byte-for-byte in XML.
"""
from pathlib import Path
from datetime import datetime,timezone
from xml.sax.saxutils import escape
import argparse,copy,hashlib,importlib.util,json,os,re,shutil,zipfile
import xml.etree.ElementTree as ET
P=Path(__file__).resolve().parents[1];R=P.parents[2];C=R/'DEE Cognitive 2.0';D=P/'documentos'
MAN=C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx';COMP=R/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'
PINS={MAN.name:'0865b4e5e05ec6575d55c5a6581541ca55efe71dcc194c282c1aa1645a0d8a31',COMP.name:'928cd1181b6e50827a6f0cd18b091875f1b732ca6f756f5c8fb49594ba8933e0'}
BASE=P/'codigo/OOXML_HELPERS_PI08_B_LITERAL.py'
PUBLICATION_137=D/'PUBLICACION_EDICION_1_37_PI09.json'
HELPERS_SHA='ef5a23de5875c8ccd352f961417adfe068a190bdf46c131aeaf2d183f2790358'
PUBLICATION_137_SHA='67ebccbaa2c871cd41a706e77a3a2725b0b500c89ff191a18c6a551a789b1661'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main';TITLE='54 PI09 Regulación integrada, reproducción y límites';ANCHOR='DEE_PI09_CAP54'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def put(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def helpers():
 require(sha(BASE)==HELPERS_SHA,'Literal OOXML helper changed')
 sp=importlib.util.spec_from_file_location('PI09_preserved_OOXML_helpers',BASE);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);m.ANCHOR=ANCHOR;return m
def require(ok,msg):
 if not ok:raise ValueError(msg)
def validate_facts(f):
 require(f.get('schema') in ('DEE.PI09.final_document_facts.R02','DEE.PI09.final_document_facts.R01') and f.get('internal_edition')=='1.38' and f.get('closed_for_authoring') is True,'Closed actual final facts with explicit edition1.38 required')
 require(sha(PUBLICATION_137)==PUBLICATION_137_SHA and read(PUBLICATION_137).get('internal_edition')=='1.37','Literal actual publication1.37 changed')
 require(isinstance(f.get('manual_sections'),list) and f['manual_sections'] and isinstance(f.get('compendium_sections'),list) and f['compendium_sections'],'Actual final chapter/compendium sections required')
 require(datetime.fromisoformat(f['cut_utc'].replace('Z','+00:00')).tzinfo is not None,'Timezone-aware actual cut required')
 require(f['selected_life']['N']==67 and type(f['selected_life']['T'])is int and f['selected_life']['life_id'],'Actual selected cut required')
 for e in f['evidence']:
  path=Path(e['path']).resolve(strict=True);require(path.is_relative_to(P.resolve())and sha(path)==e['sha256'],'Actual local evidence hash differs')
 for source in(MAN,COMP):require(sha(source)==PINS[source.name],'Source document changed; preserve and inspect')
def edit_body(raw,f,manual):
 h=helpers();pre,parts,post,_=h.body_parts(raw);infos=[h.info(x,pre)for x in parts]
 if manual:
  first=next(i for i,(_,t,s)in enumerate(infos)if s=='Ttulo1'and re.match(r'^1(?:\.\s|\s)',t));append=next(i for i,(_,t,s)in enumerate(infos)if s=='Ttulo1'and t.startswith('Apéndice A'))
  require(not any(s=='Ttulo1'and t.startswith('54 ')for _,t,s in infos),'PI09 chapter already present')
  old_history=b''.join(parts[first:]);front=f['front']
  mapping={8:'DEE thinking 4.5.0 | DEE Cognitive 2.0 | Edición documental 1.38 | DCS11-MM-001',9:front['edition_summary'],13:front['principal_summary'],14:front['functional_summary'],15:front['conservation_summary'],16:front['resume_summary'],18:'Funciones heredadas: evidencia histórica por vida y corte; continuidad actual en el capítulo 54',26:front['coverage_summary']}
  for i,text in mapping.items():require(i<first,'Front edit escaped into history');parts[i]=h.whole_paragraph(parts[i],pre,text)
  # Rewrite only the values in the existing documentary-control table.
  node=infos[23][0];replacements={}
  for row in node.findall('.//{'+W+'}tr'):
   cells=row.findall('{'+W+'}tc')
   if len(cells)!=2:continue
   texts=[''.join(x.text or ''for x in cell.iter('{'+W+'}t'))for cell in cells]
   if texts[0]in front['control_table']:
    # Existing relevant cells each have one text node, verified below.
    ts=list(cells[1].iter('{'+W+'}t'));require(len(ts)==1,'Control-cell text was split; inspect before editing')
    replacements[ts[0].text or '']=front['control_table'][texts[0]]
  require(len(replacements)==len(front['control_table']),'Missing exact control-table labels')
  parts[23],count=h.replace_texts(parts[23],replacements);require(count==len(replacements),'Control-table exact anchor count mismatch')
  toc=next(i for i,(_,t,s)in enumerate(infos[:first])if t=='53 PI09 Consulta selectiva acceso y continuidad')
  ids=[int(x)for x in re.findall(rb'<w:bookmarkStart\b[^>]*w:id="(\d+)"',raw)]
  chapter=h.render_sections(f['manual_sections'],'54',TITLE,max(ids,default=0)+1)
  additions={toc+1:h.paragraph(TITLE,'TOCline',link=ANCHOR),append:chapter}
  out=pre+b''.join(additions.get(i,b'')+x for i,x in enumerate(parts))+post
  require(b''.join(parts[first:])==old_history,'Historical chapter/appendix XML changed')
  proof={'old_history_XML_sha256':hashlib.sha256(old_history).hexdigest(),'old_chapters1_to53_and_appendices_literal':True,'front_modified_children':list(mapping)+[23],'new_bookmark':ANCHOR}
 else:
  index=next((i for i,x in enumerate(infos)if x[0].tag=='{'+W+'}sectPr'),len(parts));old=b''.join(parts)
  out=pre+b''.join(parts[:index])+h.render_sections(f['compendium_sections'],'PI09','PI09 Regulación integrada, reproducción y límites')+b''.join(parts[index:])+post
  proof={'old_body_XML_sha256':hashlib.sha256(old).hexdigest(),'old_body_literal':True}
 ET.fromstring(out);return out,proof
def build(source,dest,f,manual):
 with zipfile.ZipFile(source)as zin:
  require(zin.testzip()is None,'Source DOCX CRC failure');old={i.filename:zin.read(i)for i in zin.infolist()}
  new,bodyproof=edit_body(old['word/document.xml'],f,manual);changes={'word/document.xml':new}
  core=old['docProps/core.xml'].decode()
  values={'cp:version':'1.38','cp:revision':'38','dcterms:modified':f['cut_utc'],'dc:description':f['description']}
  if manual:values['dc:title']='DEE Cognitive 2.0 Manual Maestro Edición 1.38 PI09'
  for tag,value in values.items():
   core,n=re.subn(r'(<'+re.escape(tag)+r'(?:\s[^>]*)?>).*?(</'+re.escape(tag)+r'>)',lambda m:m[1]+escape(value)+m[2],core,flags=re.S);require(n==1,'Missing/duplicate core property '+tag)
  changes['docProps/core.xml']=core.encode()
  if 'word/settings.xml'in old:changes['word/settings.xml']=helpers().settings_edit(old['word/settings.xml'])
  if manual:
   for name,data in old.items():
    if re.fullmatch(r'word/(?:header|footer)\d+\.xml',name):
     value=data.replace(b'1.37',b'1.38')
     if value!=data:changes[name]=value
  for name,data in changes.items():ET.fromstring(data)
  with zipfile.ZipFile(dest,'x')as zout:
   for member in zin.infolist():zout.writestr(copy.copy(member),changes.get(member.filename,old[member.filename]))
 with zipfile.ZipFile(dest)as z:
  require(z.testzip()is None,'Output DOCX CRC failed');unchanged=[]
  for name,data in old.items():
   if name.endswith('.xml'):ET.fromstring(z.read(name))
   if name not in changes:require(z.read(name)==data,'Unexpected package member edit');unchanged.append(name)
 return {'source':str(source),'source_sha256':sha(source),'output':str(dest),'output_sha256':sha(dest),'bytes':dest.stat().st_size,'modified_members':list(changes),'unchanged_members':unchanged,'structure_valid':True,'visual_QA_not_implied':True,**bodyproof}
def main(a):
 if a.check_facts:
  require(a.facts is not None,'Actual facts JSON required');validate_facts(read(a.facts));print(json.dumps({'facts_valid':True,'edition':'1.38','read_only':True,'Native_executed':False}));return
 if not a.author and not a.publish:
  print(json.dumps({'mode':'READ_ONLY','sources':[str(MAN),str(COMP)],'new_edition':'1.38','whole_previous_history_preserved':True,'Native_executed':False}));return
 require(a.facts is not None,'Actual final facts JSON required');f=read(a.facts)
 if a.author:
  require(a.marker_confirmed,'Root must acknowledge the already executed marker for these same two outputs; do not repeat it');validate_facts(f)
  stage=D/'edicion_1_37';backup=D/'respaldo_1_37';require(not stage.exists()and not backup.exists(),'Existing authoring outputs protected');stage.mkdir(parents=True);backup.mkdir()
  rows=[]
  for source,manual in((MAN,True),(COMP,False)):
   shutil.copyfile(source,backup/source.name);require(sha(backup/source.name)==PINS[source.name],'Backup bytes changed');rows.append(build(source,stage/source.name,f,manual))
  put(D/'ESTRUCTURA_EDICION_1_37_PI09.json',{'schema':'DEE.PI09.complete_DOCX_structural_staging.R02','facts_sha256':sha(a.facts),'rows':rows,'Native_executed':False,'published':False,'render_required_or_explicit_limitation':True});print(json.dumps({'staged':str(stage),'documents':2,'history_preserved':True}));return
 validate_facts(f);proof=read(D/'ESTRUCTURA_EDICION_1_37_PI09.json');require(proof['facts_sha256']==sha(a.facts),'Facts changed after authoring')
 for row in proof['rows']:
  source=Path(row['source']);out=Path(row['output']);require(sha(source)==row['source_sha256']and sha(out)==row['output_sha256'],'Source/stage changed before publication')
 for row in proof['rows']:
  source=Path(row['source']);temporary=source.with_name(source.name+'.PI09.pending');shutil.copyfile(row['output'],temporary);require(sha(temporary)==row['output_sha256'],'Copy failed');os.replace(temporary,source)
 put(D/'PUBLICACION_EDICION_1_37_PI09.json',{'schema':'DEE.PI09.actual_complete_DOCX_publication.R02','at':datetime.now(timezone.utc).isoformat(),'rows':[{**r,'published_sha256':sha(Path(r['source']))}for r in proof['rows']],'internal_edition':'1.38','facts_sha256':sha(a.facts),'visual_status':'See separate actual renderer log; structure is not visual approval','Native_executed':False});print(json.dumps({'published':True,'documents':2,'internal_edition':'1.38'}))
if __name__=='__main__':
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group();g.add_argument('--author',action='store_true');g.add_argument('--publish',action='store_true');p.add_argument('--facts',type=Path);p.add_argument('--marker-confirmed',action='store_true');p.add_argument('--check-facts',action='store_true');main(p.parse_args())
