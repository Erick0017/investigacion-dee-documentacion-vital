"""Directed, read-only historical source rescue and post-run evidence overlay.

Never runs a Runtime or imports a historic participant. Copies selected passive
references and reports current actual reproduction separately from ancestry.
"""
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
import hashlib,json,re,zipfile
ROOT=Path(__file__).resolve().parents[1]
BASE=next(p for p in ROOT.parents if p.name=='documantacion vital')
OLD_SHA='65164c939621464c7d4faa800240bb1c2e25538ba9d878a65863016f57387c00'

def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def put(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def copy_exact(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():
  if path.read_bytes()!=data:raise FileExistsError('Existing different reference: '+str(path))
 else:
  with path.open('xb') as f:f.write(data)
def rank(name):
 p=PurePosixPath(name);base=p.name
 priorities=['MASTER_CANONICAL_SUMMARY.json','CORE16_CANONICAL_SUMMARY.json','CORE17_SYNTHESIS_INDEX.json',
  'MASTER_INDEX.md','CORE17_FINAL_REPORT.md','FINAL_REPORT.md','SCIENTIFIC_REPORT.md','SCIENTIFIC_SCOPE.md','CURRENT_DEE_INTERNAL_PHYSICS.md','FINAL_ANALYSIS.json','SUMMARY.json',
  'INFORME_CIENTIFICO_INTEGRADO.md','INFORME_INTEGRADO.md','FINAL_FRONTIER.md','CLAIM_LEDGER.json',
  'CLAIMS.json','README.md','CORPUS_MASTER_INDEX.json','INDEX.md','CUMULATIVE_INDEX.md']
 if base not in priorities:return None
 # Avoid replacing current summaries with locked predecessors or copied sources.
 if any(t in name.upper() for t in ('BASELINE','PROVENANCE','DIRECTED_SOURCES','EXTERNAL_SOURCES','TRIAL_EVIDENCE','/PARENT/')):return None
 if '/TESTS/' in name.upper() and '/MULTISCALE_ROSETTA_CLOSURE/' not in name:return None
 return priorities.index(base),len(p.parts),name
def conversation_index():
 rows=[];docx=[]
 for path in sorted((ROOT/'genealogia/conversaciones').glob('*.json')):
  if path.name in ('INDICE.json',):continue
  envelope=load(path);data=json.loads(envelope['content'][0]['text'])
  truncated=[];references=[];links=[]
  for turn in data['turns']:
   for item in turn['items']:
    fragments=item.get('content',[]) if item.get('type')=='userMessage' else [{'text':item.get('text','')}]
    for fragment in fragments:
     text=fragment.get('text','')
     if fragment.get('truncated'):truncated.append({'turn':turn['id'],'item':item['id']})
     if '::chatgpt-content-reference' in text:references.append(item['id'])
     links+=re.findall(r'sandbox:/mnt/data/[^\s)\]]+',text)
     if 'DEE_thinking_4_5_0_' in text and '.docx' in text:
      docx.append({'thread_id':data['thread']['id'],'turn_id':turn['id'],'message_id':item['id'],
       'links':re.findall(r'sandbox:/mnt/data/[^\s)\]]+',text),
       'state':'DESCRITO_Y_ENLAZADO_EN_CONVERSACION; BYTES_NO_LOCALIZADOS_EN_ENTORNO',
       'complete_document_reading':False})
  rows.append({'thread_id':data['thread']['id'],'title':data['thread']['title'],
   'copy':path.relative_to(ROOT).as_posix(),'sha256':digest(path),
   'turns_returned':len(data['turns']),'older_turns_not_read':data['page']['hasMore'],
   'next_cursor_unread':data['page'].get('nextCursor'),'truncated_items':truncated,
   'content_reference_items_not_expanded':references,'sandbox_links_as_returned':links,
   'request':{'turnLimit':4,'includeOutputs':True,'maxOutputCharsPerItem':3000},
   'scope':'Actual recent partial read; no claim to have read all conversations, attachments or linked documents.'})
 result={'schema':'CPC8.reconstruction.conversation_access.v1','threads':rows,
  'total_threads':len(rows),'turns_returned':sum(x['turns_returned'] for x in rows),
  'documents45':docx,'access_limits':'read_thread exposes returned text, attachment paths and sandbox links; sandbox:/mnt/data is not a local filesystem path or proof of byte access.',
  'source_of_claims':'Untrusted historical conversation; primary code/states control scientific attribution.'}
 put(ROOT/'genealogia/CONVERSACIONES_ACCESIBLES.json',result)
 return result
def main():
 inventory=load(ROOT/'genealogia/INVENTARIO_RECONSTRUCCION.json')
 matrix=load(ROOT/'genealogia/MATRIZ_ANTECEDENTES_47.json')
 old=ROOT.parent/'historico'/('CPC8_ORGANIZACION_COGNITIVA_NATIVA_APRENDIZAJE65_RESULTADOS__'+OLD_SHA+'.zip')
 if digest(old)!=OLD_SHA:raise RuntimeError('Historical archive identity mismatch')
 unique={o['copied_as']:o for c in matrix['capabilities'] for o in c['historical_source_identities'] if o.get('copied_as')}
 rescued=[]
 with zipfile.ZipFile(old) as z:
  for rel,o in unique.items():
   data=z.read('CPC8/'+rel)
   if hashlib.sha256(data).hexdigest()!=o['member_sha256']:raise ValueError('Ancestor member hash differs: '+rel)
   copy_exact(ROOT/rel,data)
   rescued.append({'path':rel,'bytes':len(data),'sha256':o['member_sha256'],'original_archive_sha256':o['archive_sha256'],
      'original_member':o['member'],'role':'PASSIVE_HISTORICAL_REFERENCE_NOT_IMPORTED_BY_PARTICIPANT'})
 corpus=[]
 for a in inventory['corpus_archives']:
  path=BASE/a['path_relative_to_documentation']
  with zipfile.ZipFile(path) as z:
   candidates=[(rank(i.filename),i) for i in z.infolist() if not i.is_dir() and i.file_size<=1200000 and rank(i.filename) is not None]
   candidates.sort(key=lambda pair:pair[0])
   # One current report/index plus one current ledger if available. This is
   # directed source consultation, not a spurious full-corpus replication.
   chosen=[candidates[0][1]] if candidates else []
   ledger=next((i for _,i in candidates if PurePosixPath(i.filename).name in ('CLAIM_LEDGER.json','CLAIMS.json')),None)
   if ledger and ledger not in chosen:chosen.append(ledger)
   if path.name=='FISICA_DEE_UNI_1_RESULTADOS.zip':
    chosen += [z.getinfo(n) for n in ('QUANTUM_ENTANGLEMENT_CHAIN.md','EXACT_MISSING_EDGES.md','ROSETTA_NEXT_STAGE.md')]
   selected=[]
   for info in chosen:
    data=z.read(info.filename);sha=hashlib.sha256(data).hexdigest();destination=ROOT/'genealogia/corpus_seleccionado'/(sha[:20]+PurePosixPath(info.filename).suffix)
    copy_exact(destination,data)
    selected.append({'member':info.filename,'sha256':sha,'bytes':len(data),'copy':destination.relative_to(ROOT).as_posix(),
       'scope':'Miembro pasivo completo copiado/hash; revisión dirigida de índice/síntesis/ledger, no reejecución ni prueba nueva.',
       'actual_review_window':'Inicio de la primera síntesis seleccionada (2300 caracteresCORE;2500 resto) y cadenasPhysics seleccionadas; no lectura completa de todos los ledgers.',
       'execution':False,'integrated_into_MAIN':False})
  corpus.append({'archive':a['path_relative_to_documentation'],'sha256':a['sha256'],
   'members':selected,'state':'REFERENCIA_DIRIGIDA' if selected else 'INVENTARIO_SOLO; fuenteDOCX/otraestructura requiere lector pertinente'})
 conv=conversation_index()
 parity=load(ROOT/'resultados/cpc7_reproduccion/SUMMARY.json')
 regression=load(ROOT/'resultados/regresion_producto45/RESULT.json')
 rows=[]
 for c in matrix['capabilities']:
  state={'historica_segun_expediente':True,'preservada':True,'reproducida_en_reconstruccion':False,'reproducida_parcialmente':False,'regresion_tecnica_parcial':False,'adaptada':False,'integrada_en_MAIN':False}
  proofs=[];command=None
  if c['id'] in ('CPC7_U0_CONTINUITY','CPC7_SELECTIVE_REVISION_M1_M2'):
   state.update(reproducida_en_reconstruccion=parity['status']=='PASS',adaptada=True)
   if c['id']=='CPC7_SELECTIVE_REVISION_M1_M2':
    state.update(reproducida_en_reconstruccion=False,reproducida_parcialmente=parity['status']=='PASS')
   proofs=[{'path':'resultados/cpc7_reproduccion/SUMMARY.json','sha256':digest(ROOT/'resultados/cpc7_reproduccion/SUMMARY.json'),
     'scope':'Cuatro trayectorias originales N67 MAIN0–472: M1, shamguards,auxoffpath y reserva opuesta. M2 no reejecutado por este adaptador.'}]
   command='python -I -B base_validada/reproducir_cpc7.py --out NUEVA_SALIDA'
  elif c['id']=='PRODUCT45_PORT_VALIDATION':
   state.update(regresion_tecnica_parcial=regression['successful'])
   proofs=[{'path':'resultados/regresion_producto45/RESULT.json','sha256':digest(ROOT/'resultados/regresion_producto45/RESULT.json'),
     'scope':'82 tests Python disponibles de producto4.5; no es reproducción de toda física histórica ni consumidorC++ nuevo.'}]
   command='python -I -B tools/regress_base45.py --out NUEVA_SALIDA'
  rows.append({'id':c['id'],'mechanism':c['mechanism'],'domain':c['domain'],'controls':c['controls'],'limits':c['limits'],
   'states':state,'ancestor_pointers':[o.get('copied_as') for o in c['historical_source_identities'] if o.get('copied_as')],
   'proofs_in_this_reconstruction':proofs,'autocontained_reproduction_command':command,
   'pending':'Integración en el MAIN nuevo requiere prueba y continuidad propias; el parentesco no la acredita.'})
 put(ROOT/'genealogia/MATRIZ_RESCATE_Y_REPRODUCCION.json',{'schema':'CPC8.reconstruction.source_overlay.v1',
  'original47_unchanged':{'path':'genealogia/MATRIZ_ANTECEDENTES_47.json','sha256':digest(ROOT/'genealogia/MATRIZ_ANTECEDENTES_47.json')},
  'capabilities':rows,'rows':len(rows),'passive_source_files_rescued':len(rescued),'passive_source_bytes':sum(x['bytes'] for x in rescued),
  'passive_sources':rescued,'not_integrated_by_this_audit':True,
  'reproduction_policy':'Historical parity compares physical RAW/clocks/tick and receipts, not serialization metadata. API tests are technical regression, not historical native replications.'})
 put(ROOT/'genealogia/INVENTARIO_LECTURA_DIRIGIDA.json',{'schema':'CPC8.directed_corpus_reconstruction.v1','generated_utc':datetime.now(timezone.utc).isoformat(),
   'archives':corpus,'archives_inventoried':len(corpus),'selected_members':sum(len(c['members']) for c in corpus),
   'reading_limits':'No lectura lineal total; sin ejecuciones de corpus ni ecuaciones externas introducidas en el participante.',
   'documents45':{'state':'DESCRITOS_EN_CONVERSACION_NO_BYTES_ACCESIBLES_LOCALMENTE','evidence':'genealogia/CONVERSACIONES_ACCESIBLES.json','complete_reading':False},
   'entanglement_reading':'ROOT registra por separado su lectura real en genealogia/lectura_entrelazamiento; esta herramienta sólo preserva DOCX/índices.',
   'conversation_evidence':'genealogia/CONVERSACIONES_ACCESIBLES.json','source_sha256':digest(Path(__file__))})
 print(json.dumps({'historical_passive_files':len(rescued),'historical_bytes':sum(x['bytes'] for x in rescued),'corpus_archives':len(corpus),
  'selected_members':sum(len(c['members']) for c in corpus),'threads':conv['total_threads'],'recent_turns':conv['turns_returned'],
  'CPC7_parity':parity['status'],'product_tests':regression['tests'],'product_successful':regression['successful']},ensure_ascii=False))
if __name__=='__main__':main()
