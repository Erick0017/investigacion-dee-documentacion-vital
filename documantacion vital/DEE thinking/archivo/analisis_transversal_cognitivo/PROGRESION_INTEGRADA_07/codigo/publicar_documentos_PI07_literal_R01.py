"""Root-only literal publication of already authored complete PI07 documents.



Default is a read-only preflight. --apply copies the exact staged DOCX bytes

and updates only root document descriptors in the three existing JSON files.

No DEE imports, authoring, rendering, Native calls, contracts or selections.

The exact prior publisher is preserved under codigo/FUENTES_EDITORIAL_PI06_EXACTO/publicar_documentos_PI06_literal_R02.py.

"""

from pathlib import Path

import argparse,copy,datetime,hashlib,io,json,os,uuid,zipfile

from lxml import etree as E

from docx import Document



P=Path(__file__).resolve().parents[1];R=P.parents[2];C=R/'DEE Cognitive 2.0';S=C/'sistema';D=P/'documentos'

EDITION='1.34'

NAME='DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'

OLD={'Manual':'55f77c470b2b442e8fce341dd0eb9d669a6e8e565d35b9ca9f3236f34459922d',

     'Compendium':'34ae6c7eddb0a72afa846c720eaa0b1b30d990a354350d67d5402d00978aa559'}

W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}';NS={'w':W[1:-1]}



def sha(b):return hashlib.sha256(b).hexdigest()

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def info(p):

 p=Path(p);b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':sha(b)}

def encoded(v):return(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')

def require(ok,message):

 if not ok:raise ValueError(message)

def regular(path):

 for p in(path,*path.parents):

  if p.exists():require(not p.is_symlink()and not(getattr(p.lstat(),'st_file_attributes',0)&1024),'Linked path refused: '+str(p))

def atomic(p,b,expected=None):

 regular(p)

 if expected is not None:require(sha(p.read_bytes())==expected,'Concurrent target change: '+str(p))

 tmp=p.with_name(p.name+'.PI07_LITERAL_'+uuid.uuid4().hex+'.tmp')

 with tmp.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())

 if expected is not None:require(sha(p.read_bytes())==expected,'Concurrent change before replacement: '+str(p))

 os.replace(tmp,p);require(p.read_bytes()==b,'Literal publication mismatch: '+str(p))

def dump(p,v,expected=None):atomic(p,encoded(v),expected)

def strings(v):

 if isinstance(v,str):yield v

 elif isinstance(v,dict):

  for x in v.values():yield from strings(x)

 elif isinstance(v,list):

  for x in v:yield from strings(x)



def validate_docx(path,expected):

 b=path.read_bytes();require(sha(b)==expected,'Staged hash mismatch: '+str(path))

 with zipfile.ZipFile(io.BytesIO(b))as z:

  require(z.testzip()is None,'DOCX CRC failure')

  xmls={n:E.fromstring(z.read(n))for n in z.namelist()if n.endswith(('.xml','.rels'))}

 root=xmls['word/document.xml'];core=xmls['docProps/core.xml']

 version=core.find('{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}version')

 require(version is not None and version.text==EDITION,'Staged core edition is not1.34')

 texts=[''.join(t.text or''for t in p.iter(W+'t'))for p in root.iter(W+'p')]

 require(not any('[[CIERRE'in t or'[[PENDIENTE'in t for t in texts),'Unresolved authored prose')

 document=Document(io.BytesIO(b));count=0

 for name,part in xmls.items():

  if name=='word/document.xml'or name.startswith(('word/header','word/footer')):

   for par in part.iter(W+'p'):''.join(par.itertext());count+=1

 return {'file':info(path),'CRC_all_members':True,'XML_relationship_parts':len(xmls),

  'paragraphs_XML':len(texts),'tables_XML':len(list(root.iter(W+'tbl'))),

  'body_header_footer_paragraphs_traversed':count,'python_docx_paragraphs':len(document.paragraphs),

  'python_docx_tables':len(document.tables),'python_docx_table_cells':sum(len(r.cells)for t in document.tables for r in t.rows),

  'core_version':version.text,'readable_structure':True,'visual_QA_performed_by_publisher':False}



def history1_49(path):

 with zipfile.ZipFile(path)as z:body=E.fromstring(z.read('word/document.xml')).find(W+'body')

 items=list(body)

 def text(e):return''.join(t.text or''for t in e.iter(W+'t'))

 def h1(e):

  n=e.find('w:pPr/w:pStyle',NS)

  return n is not None and n.get(W+'val','').lower()in('heading1','ttulo1','titulo1','title1')

 start=next(i for i,e in enumerate(items)if e.tag==W+'p'and h1(e)and text(e).startswith('1. Qué es'))

 end=next(i for i,e in enumerate(items[start+1:],start+1)if e.tag==W+'p'and h1(e)and(text(e).startswith('50 PI07')or text(e)=='Apéndice A. Inventario histórico de las 73 entradas'))

 return[E.tostring(e)for e in items[start:end]]



def appendix_history(path):
 with zipfile.ZipFile(path)as z:body=E.fromstring(z.read('word/document.xml')).find(W+'body')
 items=list(body);starts=[]
 for i,e in enumerate(items):
  if e.tag!=W+'p':continue
  text=''.join(t.text or''for t in e.iter(W+'t'))
  style=e.find('w:pPr/w:pStyle',NS)
  is_h1=style is not None and style.get(W+'val','').lower()in('heading1','ttulo1','titulo1','title1')
  if is_h1 and text=='Apéndice A. Inventario histórico de las 73 entradas':starts.append(i)
 require(len(starts)==1,'Expected exactly one real Heading1 Appendix A; no index entry or ambiguous heading')
 return[E.tostring(e)for e in items[starts[0]:]]

def visual_evidence(file,manual_sha):

 result={'status':'NOT_VALIDATED','validation_visual':'NOT_VALIDATED','witness':None,'rendered_pdf':None,'reviewed_images':[],

  'limitations':'No rendering or visual approval is inferred by this publisher.'}

 if file is None:return result

 file=file.resolve(strict=True);regular(file);require(file.is_relative_to(P),'Visual proof must be an existing PI07 artifact')

 v=read(file);status=v.get('status','NOT_VALIDATED')

 require(status in('PASSED','PARTIAL','NOT_VALIDATED','BLOCKED','FAILED'),'Explicit real visual status required')

 require(v.get('manual_sha256')==manual_sha,'Visual proof is not bound to current staged Manual')

 if status=='PASSED':

  require(v.get('rendered_pdf')and Path(v['rendered_pdf']).is_file(),'PASSED requires actual rendered PDF')

  require(v.get('reviewed_images')and all(Path(x).is_file()for x in v['reviewed_images']),'PASSED requires actual reviewed image files')

 result.update(status=status,validation_visual=status,witness=info(file),rendered_pdf=v.get('rendered_pdf'),

  reviewed_images=v.get('reviewed_images',[]),limitations=v.get('limitations',result['limitations']))

 return result



def metadata_updates(metadata,paths,manual,visual,publication,struct,now):

 """Pure, narrowly allowlisted document-descriptor changes; no life changes."""

 result=copy.deepcopy(metadata);key='manual_before_PI07_publication_historical'

 project=result[str(paths[0])];continuity=result[str(paths[1])];catalog=result[str(paths[2])]

 require(all(key not in x for x in(project,continuity,catalog)),'PI07 document history already recorded')

 project[key]={k:copy.deepcopy(project.get(k))for k in('manual_current','manual_internal_edition','manual_current_sha256','manual_current_bytes','manual_publication_witness')}

 continuity[key]={k:copy.deepcopy(continuity.get(k))for k in('manual','manual_current')};catalog[key]=copy.deepcopy(catalog.get('manual_current'))

 mi=manual['published'];relative=Path(mi['path']).name

 require(project.get('manual_current')==relative,'Compatible Manual name must remain unchanged')

 project.update(manual_internal_edition=EDITION,manual_current_sha256=mi['sha256'],manual_current_bytes=mi['bytes'],manual_publication_witness=str(publication))

 continuity.setdefault('manual',{}).update(edition=EDITION,path_relative_to_product=relative,sha256=mi['sha256'],bytes=mi['bytes'],

  document_publication=str(publication),validation_visual=visual['validation_visual'])

 continuity['manual_current']={**mi,'internal_edition':EDITION,'same_logical_manual_and_filename':True,

  'prior_complete_document':manual['literal_backup'],'visual_qa':visual['status'],'validation_visual':visual['validation_visual'],

  'visual_witness':visual['witness'],'rendered_pdf':visual['rendered_pdf'],'reviewed_images':visual['reviewed_images'],

  'structural_validation':str(struct),'publication_witness':str(publication),'historical_chapters_1_49_preserved_literal':True}

 continuity['last_documentary_update_PI07']=now

 catalog['manual_current']={'path_relative_to_product':relative,'internal_edition':EDITION,'bytes':mi['bytes'],

  'sha256':mi['sha256'],'publication_witness':str(publication),'validation_visual':visual['validation_visual']}

 allowed=[{key,'manual_internal_edition','manual_current_sha256','manual_current_bytes','manual_publication_witness'},

          {key,'manual','manual_current','last_documentary_update_PI07'},{key,'manual_current'}]

 for path,keys in zip(paths,allowed):

  old=metadata[str(path)];new=result[str(path)]

  require({k:v for k,v in old.items()if k not in keys}=={k:v for k,v in new.items()if k not in keys},'Unexpected non-document metadata change')

 return result



def prepare(args):

 facts_path=P/'control/CIERRE_CIENTIFICO_PI07.json';facts_bytes=facts_path.read_bytes();facts=json.loads(facts_bytes)

 require(facts.get('closed_for_authoring')is True,'Only actual closed final facts may be published')

 LIFE=facts['principal']['life_id']

 require(isinstance(LIFE,str)and LIFE.startswith('ECI02_'),'Explicit actual principal required')

 require(not any('[[CIERRE'in x or'[[PENDIENTE'in x for x in strings(facts)),'Closed facts contain placeholders')

 stage_path=D/'ACTUALIZACION_DOCUMENTAL_PI07_1_34.json';stage=read(stage_path)

 require(stage['source_facts_sha256']==sha(facts_bytes),'Staged documents do not match exact closed facts')

 require(stage.get('body_history_preserved_exact_except_current_front')is True and stage.get('historical_current_pointers_kept_as_historical')is True,'Historical-preservation authoring proof required')

 active_path=S/'estado/ACTIVO.json';active=read(active_path);card_path=S/'estado/vidas'/LIFE/'VIDA.json';card=read(card_path)

 require(active['life_id']==facts['principal']['life_id']==card['life_id']==LIFE,'Actual selected principal differs from final facts')

 require(card['physical']['N']==facts['principal']['N']==67 and card['physical']['tick']==facts['principal']['tick'],'Actual current cut differs from final facts')

 principal=facts['principal'];current_sha=principal.get('current_snapshot_sha256',principal.get('snapshot_sha256'))

 require(not('current_snapshot_sha256'in principal and'snapshot_sha256'in principal)or principal['current_snapshot_sha256']==principal['snapshot_sha256'],'Conflicting current snapshot fields in final facts')

 require(card['physical']['tick']>=active['tick']and current_sha==card['snapshot_sha256'],'Current saved snapshot differs from final facts; no documentary promotion')

 require(sha((S/card['snapshot']).read_bytes())==card['snapshot_sha256'],'Current snapshot bytes differ from VIDA')

 protected=[active_path,card_path,S/active['snapshot'],S/card['snapshot'],

  S/'estado/genesis/SELECCION_PERSONAL.json',S/'capacidades/ENTRADA_SIMPLE_SELECCION.json',

  S/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl',C/'motor/python313/site-packages/dee_thinking/_native.cp313-win_amd64.pyd']

 # The selected entry may live in genesis rather than capacidades; only actual files are included.

 protected=list(dict.fromkeys(p for p in protected if p.is_file()))

 for p in protected:regular(p)

 protected_before={str(p):info(p)for p in protected}

 pub=D/'DOCUMENTOS_PUBLICADOS_PI07_1_34.json';struct=D/'VALIDACION_ESTRUCTURAL_PI07_1_34.json';intent=D/'PUBLICACION_EN_CURSO_PI07_1_34.json'

 require(not any(p.exists()for p in(pub,struct,intent)),'Publication output already exists; inspect/reconcile, never blindly retry')

 targets={'Manual':C/NAME,'Compendium':R/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'};entries={}

 for label in('Manual','Compendium'):

  item=stage[label];target=Path(item['source']).resolve(strict=True);staged=Path(item['output']).resolve(strict=True)

  backup=Path(stage['prior_literal_backups'][label]['path']).resolve(strict=True)

  for path in(target,staged,backup):regular(path)

  require(target==targets[label].resolve(strict=True),'Unexpected publication target '+label)

  require(staged.parent==(D/'staging_1_34_R01').resolve()and backup.is_relative_to(D),'Only exact PI07 staging/backups permitted')

  require(item['source_sha256']==OLD[label]and sha(target.read_bytes())==sha(backup.read_bytes())==OLD[label],'Prior original/backup CAS mismatch '+label)

  entries[label]={'target':target,'staged':staged,'backup':backup,'before':info(target),'literal_backup':info(backup),

   'published':{**info(staged),'path':str(target)},'validation':validate_docx(staged,item['sha256'])}

 require(facts['compendium_before_sha256']==OLD['Compendium'],'Final facts refer to another prior Compendium')

 require(history1_49(entries['Manual']['backup'])==history1_49(entries['Manual']['staged']),'Historical chapters1–49 changed')

 require(appendix_history(entries['Manual']['backup'])==appendix_history(entries['Manual']['staged']),'Historical appendices changed')

 visual=visual_evidence(args.visual_proof,entries['Manual']['published']['sha256'])

 meta_paths=[C/'PROYECTO.json',C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json',S/'capacidades/CATALOGO_CAPACIDADES.json']

 raw_meta={str(p):p.read_bytes()for p in meta_paths};metadata={k:json.loads(v.decode('utf-8-sig'))for k,v in raw_meta.items()}

 project=metadata[str(meta_paths[0])];continuity=metadata[str(meta_paths[1])];catalog=metadata[str(meta_paths[2])]

 require(project.get('selected_life')==LIFE and project.get('latest_saved_tick')==card['physical']['tick'],'Project current selection/cut must be reconciled before documentary publication')

 require(continuity.get('life_id')==LIFE and continuity.get('physical_cut',{}).get('tick')==card['physical']['tick'],'Continuity must already describe current saved life')

 require(continuity.get('latest_snapshot',{}).get('sha256')==card['snapshot_sha256'],'Continuity snapshot must already be synchronized by the operational closer')

 require(catalog.get('current_principal',{}).get('life_id')==LIFE,'Catalog principal must already be synchronized; publisher cannot select')

 now=datetime.datetime.now(datetime.timezone.utc).isoformat()

 future=metadata_updates(metadata,meta_paths,entries['Manual'],visual,pub,struct,now)

 return locals()



def main(args):

 q=prepare(args);entries=q['entries'];plan={'mode':'DRY_RUN_NO_WRITES'if not args.apply else'EXPLICIT_LITERAL_PUBLICATION',

  'Manual':entries['Manual']['published'],'Compendium':entries['Compendium']['published'],

  'metadata_paths':[str(p)for p in q['meta_paths']],'principal_not_changed':q['LIFE'],'visual_QA':q['visual']['status'],

  'Native_ticks':0,'contracts_modified':False,'REVISION_TRANSVERSAL_modified':False}

 if not args.apply:print(json.dumps(plan,ensure_ascii=False,indent=2));return

 backup_dir=D/'respaldo_metadata_pre_publicacion_1_34';backup_dir.mkdir(exist_ok=False)

 original_bytes={str(e['target']):e['target'].read_bytes()for e in entries.values()};original_bytes.update(q['raw_meta'])

 for i,p in enumerate(q['meta_paths']):(backup_dir/(str(i)+'_'+p.name)).write_bytes(original_bytes[str(p)])

 writes=[];intent={'schema':'PI07.literal_document_publication.intent.v1','status':'COMMITTING','Native_ticks':0,

  'created_utc':q['now'],'planned_targets':[str(e['target'])for e in entries.values()]+[str(p)for p in q['meta_paths']],'completed':[]}

 dump(q['intent'],intent)

 try:

  require(sha(q['facts_path'].read_bytes())==sha(q['facts_bytes']),'Closed facts changed after preflight')

  require({str(p):info(p)for p in q['protected']}==q['protected_before'],'Protected operational input changed before publication')

  for label,e in entries.items():

   payload=e['staged'].read_bytes();atomic(e['target'],payload,e['before']['sha256']);writes.append((e['target'],sha(payload)))

   intent['completed'].append(str(e['target']));dump(q['intent'],intent,sha(q['intent'].read_bytes()))

  for p in q['meta_paths']:

   payload=encoded(q['future'][str(p)]);atomic(p,payload,sha(q['raw_meta'][str(p)]));writes.append((p,sha(payload)))

   intent['completed'].append(str(p));dump(q['intent'],intent,sha(q['intent'].read_bytes()))

  after={str(p):info(p)for p in q['protected']};require(after==q['protected_before'],'Protected operational files changed during publication')

  require(sha(q['facts_path'].read_bytes())==sha(q['facts_bytes']),'Closed facts changed during publication')

  structural={'schema':'PI07.document_structure.v1','at':q['now'],'documents':{k:v['validation']for k,v in entries.items()},

   'historical_chapters1_49_literal_equal':True,'historical_appendices_literal_equal':True,'authoring_historical_body_check':True,

   'scope':'CRC/all XML/relationships and structure; no visual inference','visual_evidence':q['visual'],'new_DOCX_authored':False,'Native_ticks':0}

  dump(q['struct'],structural)

  proof={'schema':'PI07.literal_documents_published.v1','at':q['now'],'status':'PUBLISHED_LITERAL_STRUCTURALLY_VERIFIED',

   'documents':{k:{'before':e['before'],'literal_backup':e['literal_backup'],'published':info(e['target']),

    'literal_staging_equal':e['target'].read_bytes()==e['staged'].read_bytes()}for k,e in entries.items()},

   'metadata_updated':[{'before_sha256':sha(q['raw_meta'][str(p)]),'after':info(p)}for p in q['meta_paths']],

   'metadata_originals_preserved_in':str(backup_dir),'structural_validation':info(q['struct']),

   'visual_evidence':q['visual'],'visual_QA_inferred_from_XML':False,'protected_before':q['protected_before'],'protected_after':after,

   'protected_operational_equal':True,'actual_selected_principal':q['LIFE'],'documentary_publication_does_not_adopt_or_reopen':True,

   'principal_selectors_modified_by_publisher':False,'contracts_modified':False,'REVISION_TRANSVERSAL_modified':False,

   'new_DOCX_authored':False,'Native_ticks':0,'DEE_imports':0,'GUI_opened':False}

  dump(q['pub'],proof);intent.update(status='COMPLETE',publication=info(q['pub']),completed=[str(p)for p,_ in writes]);dump(q['intent'],intent,sha(q['intent'].read_bytes()))

  print(json.dumps({'publication':info(q['pub']),'structure':info(q['struct']),'Manual':info(entries['Manual']['target']),

   'Compendium':info(entries['Compendium']['target']),'visual_QA':q['visual']['status'],'Native_ticks':0},ensure_ascii=False,indent=2))

 except Exception as exc:

  rollback=[]

  for path,written_sha in reversed(writes):

   try:atomic(path,original_bytes[str(path)],written_sha);rollback.append({'path':str(path),'restored':True})

   except Exception as error:rollback.append({'path':str(path),'restored':False,'error':repr(error)})

  intent.update(status='FAILED_PRESERVED_INSPECT_BEFORE_RETRY',error=repr(exc),rollback=rollback)

  dump(q['intent'],intent,sha(q['intent'].read_bytes()));raise



if __name__=='__main__':

 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--apply',action='store_true');ap.add_argument('--visual-proof',type=Path);main(ap.parse_args())

