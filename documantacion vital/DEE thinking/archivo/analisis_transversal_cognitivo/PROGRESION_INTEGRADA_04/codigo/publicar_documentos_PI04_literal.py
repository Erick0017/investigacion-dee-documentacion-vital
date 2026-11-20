"""Publish only previously authored PI04 DOCX bytes; default is read-only dry run.

Derived from publicar_documentos_PI03_literal.py. No authoring/rendering, GUI,
DEE import, Native call, selection or process control. An explicit --apply is
required. Document descriptors are synchronized; the existing transversal JSON
is appended without replacing its historical operation/resume/coverage fields.
"""
from pathlib import Path
import argparse,copy,datetime,hashlib,io,json,os,uuid,zipfile
from lxml import etree as E
from docx import Document

P=Path(__file__).resolve().parents[1]
R=P.parents[2];C=R/'DEE Cognitive 2.0';S=C/'sistema';D=P/'documentos'
REV=P.parent/'REVISION_TRANSVERSAL.json'
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
NS={'w':W[1:-1]}
EDITION='1.31'
EXPECTED_OLD_MANUAL='86e72b0d35e340effeb83c9fd018ad0ab3bf1fe2e4aa1d6fa12fea2926bd243f'
MARKER='[[CIERRE_REAL_PENDIENTE]]'

def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def info(p):
 b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':sha(b)}
def encoded(v):return(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')
def require(ok,message):
 if not ok:raise ValueError(message)
def atomic(p,b,expected=None):
 if expected is not None:require(sha(p.read_bytes())==expected,'Concurrent target change: '+str(p))
 tmp=p.with_name(p.name+'.PI04_LITERAL_'+uuid.uuid4().hex+'.tmp')
 with tmp.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
 if expected is not None:require(sha(p.read_bytes())==expected,'Concurrent change before replacement: '+str(p))
 os.replace(tmp,p);require(p.read_bytes()==b,'Literal published bytes mismatch: '+str(p))
def dump(p,v,expected=None):atomic(p,encoded(v),expected)

def validate_docx(path,expected):
 b=path.read_bytes();require(sha(b)==expected,'Unexpected staged bytes: '+str(path))
 with zipfile.ZipFile(io.BytesIO(b))as z:
  require(z.testzip()is None,'DOCX CRC failure')
  xmls={n:E.fromstring(z.read(n))for n in z.namelist()if n.endswith(('.xml','.rels'))}
 root=xmls['word/document.xml'];core=xmls['docProps/core.xml']
 version=core.find('{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}version')
 require(version is not None and version.text==EDITION,'Core edition is not1.31')
 texts=[''.join(t.text or''for t in p.iter(W+'t'))for p in root.iter(W+'p')]
 require(not any(MARKER in t or'[[PENDIENTE'in t for t in texts),'Unresolved staged prose')
 doc=Document(io.BytesIO(b));extracted=0
 for part,element in xmls.items():
  if part=='word/document.xml'or part.startswith(('word/header','word/footer')):
   for par in element.iter(W+'p'):''.join(par.itertext());extracted+=1
 return {'file':info(path),'CRC_all_members':True,'XML_relationship_parts':len(xmls),
  'paragraphs_XML':len(texts),'tables_XML':len(list(root.iter(W+'tbl'))),
  'body_header_footer_paragraphs_traversed':extracted,'python_docx_paragraphs':len(doc.paragraphs),
  'python_docx_tables':len(doc.tables),'python_docx_table_cells':sum(len(r.cells)for t in doc.tables for r in t.rows),
  'core_version':version.text,'readable_structure':True,'visual_QA_performed_by_publisher':False}

def history43_46(path):
 with zipfile.ZipFile(path)as z:body=E.fromstring(z.read('word/document.xml')).find(W+'body')
 items=list(body)
 def text(e):return''.join(t.text or''for t in e.iter(W+'t'))
 def h1(e):
  n=e.find('w:pPr/w:pStyle',NS)
  return n is not None and n.get(W+'val','').lower()in('heading1','ttulo1','titulo1','title1')
 start=next(i for i,e in enumerate(items)if e.tag==W+'p'and h1(e)and text(e).startswith('43 Progresión integrada'))
 end=next(i for i,e in enumerate(items[start+1:],start+1)if e.tag==W+'p'and h1(e)and(text(e).startswith('47 PI04')or text(e)=='Apéndice A. Inventario histórico de las 73 entradas'))
 return[E.tostring(e)for e in items[start:end]]

def visual_evidence(file,manual_sha):
 result={'status':'NOT_VALIDATED','validation_visual':'NO_VISUAL_APPROVAL_INFERRED_FROM_STRUCTURE',
  'witness':None,'rendered_pdf':None,'reviewed_images':[]}
 if file is None:return result
 file=file.resolve(strict=True);require(file.is_relative_to(P),'Visual witness must be an existing PI04 artifact')
 v=read(file);status=v.get('status','NOT_VALIDATED')
 require(status in('PASSED','PARTIAL','NOT_VALIDATED','BLOCKED','FAILED'),'Explicit visual witness status required')
 require(v.get('manual_sha256')==manual_sha,'Visual witness is not bound to staged Manual bytes')
 if status=='PASSED':
  require(v.get('rendered_pdf')and Path(v['rendered_pdf']).is_file(),'PASSED requires actual rendered PDF')
  require(v.get('reviewed_images')and all(Path(x).is_file()for x in v['reviewed_images']),'PASSED requires actual reviewed image locators')
 result.update(status=status,validation_visual=status,witness=info(file),
               rendered_pdf=v.get('rendered_pdf'),reviewed_images=v.get('reviewed_images',[]),limitations=v.get('limitations'))
 return result

def metadata_updates(metadata,paths,manual,visual,publication,struct,facts,now):
 """Pure transformations. Do not change principal, life, snapshot or engines."""
 result=copy.deepcopy(metadata);project=result[str(paths[0])];continuity=result[str(paths[1])]
 old_project=copy.deepcopy(project);old_continuity=copy.deepcopy(continuity)
 key='manual_before_PI04_publication_historical'
 require(key not in project and key not in continuity,'PI04 manual history already exists; do not overwrite it')
 project[key]={k:copy.deepcopy(project.get(k))for k in('manual_current','manual_internal_edition','manual_current_sha256','manual_current_bytes','manual_publication_witness')}
 continuity[key]={k:copy.deepcopy(continuity.get(k))for k in('manual','manual_current')}
 relative=Path(manual['published']['path']).name;mi=manual['published']
 require(project.get('manual_current')==relative,'Compatible Manual filename changed unexpectedly')
 project.update(manual_internal_edition=EDITION,manual_current_sha256=mi['sha256'],
                manual_current_bytes=mi['bytes'],manual_publication_witness=str(publication))
 continuity.setdefault('manual',{}).update(edition=EDITION,path_relative_to_product=relative,
  sha256=mi['sha256'],bytes=mi['bytes'],document_publication=str(publication),validation_visual=visual['validation_visual'])
 continuity['manual_current']={**mi,'internal_edition':EDITION,'same_logical_manual_and_filename':True,
  'prior_complete_document':manual['literal_backup'],'visual_qa':visual['status'],
  'validation_visual':visual['validation_visual'],'visual_witness':visual['witness'],
  'rendered_pdf':visual['rendered_pdf'],'reviewed_images':visual['reviewed_images'],
  'structural_validation':str(struct),'publication_witness':str(publication),
  'historical_chapters_43_46_preserved_literal':True,
  'PI04_scope':facts['core_description']}
 continuity['last_documentary_update_PI04']=now
 if len(paths)==3:
  catalog=result[str(paths[2])];require(key not in catalog,'PI04 catalog Manual history already exists')
  catalog[key]=copy.deepcopy(catalog.get('manual_current'))
  catalog['manual_current']={'path_relative_to_product':relative,'internal_edition':EDITION,
   'bytes':mi['bytes'],'sha256':mi['sha256'],'publication_witness':str(publication),
   'validation_visual':visual['validation_visual']}
 # Everything outside these descriptor/history keys must remain identical.
 allowed_project={key,'manual_internal_edition','manual_current_sha256','manual_current_bytes','manual_publication_witness'}
 allowed_cont={key,'manual','manual_current','last_documentary_update_PI04'}
 require(all(project[k]==v for k,v in old_project.items()if k not in allowed_project),'Unrelated project metadata changed')
 require(all(continuity[k]==v for k,v in old_continuity.items()if k not in allowed_cont),'Unrelated continuity metadata changed')
 return result

def prepare(args):
 facts_path=P/'control/CIERRE_CIENTIFICO_PI04.json';facts_bytes=facts_path.read_bytes();facts=json.loads(facts_bytes)
 require(facts.get('closed_for_authoring')is True,'Only closed final facts, never BORRADOR')
 published_fields=[facts[k]for k in('cover_summary','resume1','resume2','resume3','resume4','release_cut','state_of_edition','review_scope','core_description','compendium_current_summary')]
 published_fields+=facts['compendium_paragraphs']
 for section in facts['sections']:published_fields+=section['paragraphs']+section.get('commands',[])
 require(all(MARKER not in x and'[[PENDIENTE'not in x for x in published_fields),'Final documentary fields still have placeholders')
 stage_path=D/'ACTUALIZACION_DOCUMENTAL_PI04_1_31.json';stage=read(stage_path)
 require(stage['source_facts_sha256']==sha(facts_bytes),'Staged documents are not bound to exact closed facts')
 require(stage.get('body_history_preserved_exact_except_current_front')is True,'Authoring historical-preservation proof missing')
 active_path=S/'estado/ACTIVO.json';active_bytes=active_path.read_bytes();active=json.loads(active_bytes)
 require(active['life_id']==facts['principal']['life_id'],'Documentary adoption forbidden: selected life differs from facts')
 card_path=S/'estado/vidas'/active['life_id']/'VIDA.json';card=read(card_path)
 require(type(facts['principal']['tick'])is int and card['physical']['N']==facts['principal']['N']==67 and card['physical']['tick']==facts['principal']['tick'],'Current VIDA physical cut differs from final facts')
 require(card['physical']['tick']>=active['tick'],'Current VIDA regressed behind its selection reference')
 require(facts['principal'].get('snapshot_sha256')==card['snapshot_sha256'],'Current snapshot differs from final facts')
 require(info(S/card['snapshot'])['sha256']==card['snapshot_sha256'],'Current snapshot bytes differ from VIDA')
 protected=[active_path,card_path,S/active['snapshot'],S/card['snapshot'],
  S/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl',C/'motor/python313/site-packages/dee_thinking/_native.cp313-win_amd64.pyd']
 protected=list(dict.fromkeys(protected))
 protected_before={str(p):info(p)for p in protected}
 pub=D/'DOCUMENTOS_PUBLICADOS_PI04_1_31.json';struct=D/'VALIDACION_ESTRUCTURAL_PI04_1_31.json';intent=D/'PUBLICACION_EN_CURSO_PI04_1_31.json'
 require(not any(p.exists()for p in(pub,struct,intent)),'Publication proof/intent exists; inspect and reconcile, never overwrite/retry blindly')
 entries={}
 targets={'Manual':C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx',
          'Compendium':R/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'}
 for label in('Manual','Compendium'):
  item=stage[label];target=Path(item['source']).resolve(strict=True);staged=Path(item['output']).resolve(strict=True)
  require(target==targets[label].resolve(strict=True),'Only the exact original Manual/Compendium targets may be published')
  backup=Path(stage['prior_literal_backups'][label]['path']).resolve(strict=True)
  expected=EXPECTED_OLD_MANUAL if label=='Manual'else facts['compendium_before_sha256']
  require(item['source_sha256']==expected and sha(target.read_bytes())==sha(backup.read_bytes())==expected,'Old document/backup CAS failed '+label)
  require(staged.is_relative_to(D)and backup.is_relative_to(D),'Only preserved PI04 staging/backups permitted')
  projected={**info(staged),'path':str(target)}
  entries[label]={'target':target,'staged':staged,'backup':backup,'before':info(target),
   'literal_backup':info(backup),'published':projected,'validation':validate_docx(staged,item['sha256'])}
 require(history43_46(entries['Manual']['backup'])==history43_46(entries['Manual']['staged']),'Historical chapters43–46 changed')
 visual=visual_evidence(args.visual_proof,entries['Manual']['published']['sha256'])
 meta_paths=[C/'PROYECTO.json',C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json']
 catalog=S/'capacidades/CATALOGO_CAPACIDADES.json'
 if catalog.exists():meta_paths.append(catalog)
 require(REV.is_file(),'Existing REVISION_TRANSVERSAL is missing; do not recreate history')
 raw_meta={str(p):p.read_bytes()for p in meta_paths};metadata={k:json.loads(v.decode('utf-8-sig'))for k,v in raw_meta.items()}
 require(metadata[str(meta_paths[0])].get('selected_life')==active['life_id'],'Project selection differs; operational reconciliation must precede documentary publication')
 require(metadata[str(meta_paths[0])].get('latest_saved_tick')==card['physical']['tick'],'Project current tick differs; post-use synchronization required')
 require(metadata[str(meta_paths[1])].get('life_id')==active['life_id'],'Continuity selection differs; publisher cannot promote it')
 require(metadata[str(meta_paths[1])].get('physical_cut',{}).get('tick')==card['physical']['tick'],'Continuity current tick differs; publisher cannot synchronize Native use')
 if catalog.exists()and metadata[str(catalog)].get('current_principal'):
  require(metadata[str(catalog)]['current_principal']['life_id']==active['life_id'],'Catalog principal differs; publisher cannot change it')
 rev_bytes=REV.read_bytes();revision=json.loads(rev_bytes.decode('utf-8-sig'))
 require('document_publication_PI04_1_31'not in revision,'Transversal PI04 publication already recorded')
 require(type(revision.get('manual_update_history',[]))is list,'Existing history is not appendable list')
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 future=metadata_updates(metadata,meta_paths,entries['Manual'],visual,pub,struct,facts,now)
 record={'at':now,'edition':EDITION,'same_logical_manual':'DCS11-MM-001','publication':str(pub),
  'manual':{**entries['Manual']['published'],'path':str(entries['Manual']['target'])},
  'compendium':{**entries['Compendium']['published'],'path':str(entries['Compendium']['target'])},
  'actual_selected_principal_at_publication':copy.deepcopy(facts['principal']),
  'ACTIVO_selection_reference_cut_preserved':copy.deepcopy(active),
  'scientific_sources':facts['sources'],'scope':facts['core_description'],'visual_QA':visual['status'],
  'new_Native_ticks_by_document_publication':0,'record_is_append_not_historical_rewrite':True}
 rev_after=copy.deepcopy(revision);rev_after.setdefault('manual_update_history',[]).append(copy.deepcopy(record));rev_after['document_publication_PI04_1_31']=record
 require(all(rev_after[k]==v for k,v in revision.items()if k!='manual_update_history'),'Historical transversal content changed')
 require(rev_after['manual_update_history'][:-1]==revision.get('manual_update_history',[]),'Historical manual list prefix changed')
 return locals()

def main(args):
 q=prepare(args);entries=q['entries'];plan={'mode':'DRY_RUN_NO_WRITES'if not args.apply else'EXPLICIT_LITERAL_PUBLICATION',
  'Manual':entries['Manual']['published'],'Compendium':entries['Compendium']['published'],
  'metadata_paths':[str(p)for p in q['meta_paths']],'transversal_append':str(REV),
  'principal_not_changed':q['active']['life_id'],'visual_QA':q['visual']['status'],'Native_ticks':0}
 if not args.apply:print(json.dumps(plan,ensure_ascii=False,indent=2));return
 backup_dir=D/'respaldo_metadata_pre_publicacion_1_31';backup_dir.mkdir(exist_ok=False)
 original_bytes={str(e['target']):e['target'].read_bytes()for e in entries.values()}
 original_bytes.update(q['raw_meta']);original_bytes[str(REV)]=q['rev_bytes']
 for i,p in enumerate(q['meta_paths']+[REV]):(backup_dir/(str(i)+'_'+p.name)).write_bytes(original_bytes[str(p)])
 writes=[];intent={'schema':'PI04.literal_document_publication.intent.v1','status':'COMMITTING','Native_ticks':0,
  'created_utc':q['now'],'planned_targets':[str(e['target'])for e in entries.values()]+[str(p)for p in q['meta_paths']]+[str(REV)],'completed':[]}
 dump(q['intent'],intent)
 try:
  require(sha(q['facts_path'].read_bytes())==sha(q['facts_bytes']),'Closed facts changed after preflight')
  require({str(p):info(p)for p in q['protected']}==q['protected_before'],'Operational input changed before publication')
  for label,e in entries.items():
   payload=e['staged'].read_bytes();atomic(e['target'],payload,e['before']['sha256']);writes.append((e['target'],sha(payload)))
   intent['completed'].append(str(e['target']));dump(q['intent'],intent,sha(q['intent'].read_bytes()))
  for p in q['meta_paths']:
   payload=encoded(q['future'][str(p)]);atomic(p,payload,sha(q['raw_meta'][str(p)]));writes.append((p,sha(payload)))
   intent['completed'].append(str(p));dump(q['intent'],intent,sha(q['intent'].read_bytes()))
  payload=encoded(q['rev_after']);atomic(REV,payload,sha(q['rev_bytes']));writes.append((REV,sha(payload)))
  after={str(p):info(p)for p in q['protected']};require(after==q['protected_before'],'Protected operational files changed during publication')
  require(sha(q['facts_path'].read_bytes())==sha(q['facts_bytes']),'Closed facts changed during publication')
  structural={'schema':'PI04.document_structure.v1','at':q['now'],'documents':{k:v['validation']for k,v in entries.items()},
   'historical_chapters43_46_literal_equal':True,'authoring_historical_body_check':True,
   'scope':'CRC/all XML/relationships and document structure; no visual inference','visual_evidence':q['visual'],'new_DOCX_authored':False,'Native_ticks':0}
  dump(q['struct'],structural)
  proof={'schema':'PI04.literal_documents_published.v1','at':q['now'],'status':'PUBLISHED_LITERAL_STRUCTURALLY_VERIFIED',
   'documents':{k:{'before':e['before'],'literal_backup':e['literal_backup'],'published':info(e['target']),'literal_staging_equal':e['target'].read_bytes()==e['staged'].read_bytes()}for k,e in entries.items()},
   'metadata_updated':[{'before_sha256':sha(q['raw_meta'][str(p)]),'after':info(p)}for p in q['meta_paths']],
   'transversal_append':{'path':str(REV),'before_sha256':sha(q['rev_bytes']),'after':info(REV),'all_historical_keys_preserved':True,'manual_history_prefix_preserved':True},
   'metadata_originals_preserved_in':str(backup_dir),'structural_validation':info(q['struct']),
   'visual_evidence':q['visual'],'visual_QA_inferred_from_XML':False,'protected_before':q['protected_before'],'protected_after':after,
   'protected_operational_equal':True,'principal_selectors_modified_by_publisher':False,
   'new_DOCX_authored':False,'Native_ticks':0,'DEE_imports':0,'GUI_opened':False}
  dump(q['pub'],proof);intent.update(status='COMPLETE',publication=info(q['pub']),completed=[str(p)for p,_ in writes]);dump(q['intent'],intent,sha(q['intent'].read_bytes()))
  print(json.dumps({'publication':info(q['pub']),'structure':info(q['struct']),'Manual':info(entries['Manual']['target']),'Compendium':info(entries['Compendium']['target']),'visual_QA':q['visual']['status'],'Native_ticks':0},ensure_ascii=False,indent=2))
 except Exception as exc:
  # Restore only targets still equal to bytes written by THIS transaction.
  rollback=[]
  for path,written_sha in reversed(writes):
   try:atomic(path,original_bytes[str(path)],written_sha);rollback.append({'path':str(path),'restored':True})
   except Exception as error:rollback.append({'path':str(path),'restored':False,'error':repr(error)})
  intent.update(status='FAILED_PRESERVED_INSPECT_BEFORE_RETRY',error=repr(exc),rollback=rollback)
  dump(q['intent'],intent,sha(q['intent'].read_bytes()));raise

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--apply',action='store_true');ap.add_argument('--visual-proof',type=Path);main(ap.parse_args())
