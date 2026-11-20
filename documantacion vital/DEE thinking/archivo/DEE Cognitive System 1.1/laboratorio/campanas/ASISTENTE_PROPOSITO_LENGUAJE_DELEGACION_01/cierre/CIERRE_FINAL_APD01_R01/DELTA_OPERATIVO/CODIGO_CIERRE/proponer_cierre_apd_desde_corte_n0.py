"""Deterministic document proposals from one ACTUAL stopped cut. No Runtime or S/root writes."""
import argparse,copy,hashlib,json,shutil,sqlite3
from pathlib import Path,PurePosixPath

LIFE='ASISTENTE_MAIN'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def emit(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
def actual_file(root,value,*,system_relative=False):
 p=Path(value)
 if not p.is_absolute():p=(root/'sistema'if system_relative else root)/p
 p=p.resolve(strict=True)
 if not p.is_file()or not p.is_relative_to(root):raise ValueError('Required source is not a file inside the declared root')
 return p
def locator(root,p):return p.resolve().relative_to(root).as_posix()
def member(package,name):
 rel=PurePosixPath(name)
 if rel.is_absolute()or'..'in rel.parts or'\\'in name or':'in name:raise ValueError('Unsafe paired member')
 p=(package/Path(*rel.parts)).resolve(strict=True)
 if not p.is_relative_to(package)or p.is_symlink()or not p.is_file():raise ValueError('Paired member escapes or is not a file')
 return p
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for key in('root','cut','candidates','out'):ap.add_argument('--'+key,type=Path,required=True)
 ap.add_argument('--manual',type=Path);ap.add_argument('--manual-edition',default='1.15');a=ap.parse_args()
 root=a.root.resolve(strict=True);out=a.out.resolve();close=Path(__file__).resolve().parent
 if not out.is_relative_to(close)or out==close or out.exists():raise ValueError('Only a NEW child folder of this laboratory/cierre is allowed')
 cp=a.cut.resolve(strict=True)
 if not cp.is_relative_to(root):raise ValueError('The actual cut must belong to this research root')
 cut_digest=sha(cp);cut=load(cp);maincut=cut['main'];service=cut['persistent_service']
 if cut.get('issues')!=[]or maincut['life_id']!=LIFE:raise ValueError('Cut must have an explicit empty integrity-issues list and selected MAIN')
 if not service.get('owner_stopped')or service.get('pending_or_uncertain')or service.get('queue')or any(service.get('pending',{}).values())or service.get('native_pending')or service.get('native_pending_count')!=0:raise ValueError('A real stopped owner and empty transport/native/protocol pending state are required')
 if service.get('owner',{}).get('running')is not False:raise ValueError('Cut owner is not recorded stopped')
 card=actual_file(root,maincut['record'],system_relative=True);snapshot=actual_file(root,maincut['snapshot'],system_relative=True);record=load(card)
 if sha(card)!=maincut['record_sha256']or sha(snapshot)!=maincut['snapshot_sha256']:raise ValueError('Current saved bytes differ from the named cut')
 if record['life_id']!=LIFE or record['world_id']!=maincut['world_id']or record['physical']!=maincut['physical']or record['snapshot_sha256']!=maincut['snapshot_sha256']:raise ValueError('Current identity/physical state differs; no favorable selection or rewind')
 if(root/'sistema/estado/locks'/(record['world_id']+'.lock')).exists():raise ValueError('An owner lock still exists; do not inspect a live writer')
 journal=actual_file(root,service['journal'])
 if sha(journal)!=service['journal_sha256']:raise ValueError('Current paired queue differs')
 wal=journal.with_name(journal.name+'-wal')
 if wal.exists()and wal.stat().st_size:raise ValueError('Unsettled WAL must be preserved, never discarded')
 with sqlite3.connect(journal.as_uri()+'?mode=ro&immutable=1',uri=True)as db:
  outstanding=db.execute("SELECT id,status FROM requests WHERE status IN('queued','processing','uncertain')").fetchall()
  row=db.execute("SELECT value FROM meta WHERE key='owner'").fetchone();owner=json.loads(row[0])if row else None
 if outstanding or not owner or owner.get('running')is not False or owner.get('uncertain_external_result'):raise ValueError('Actual read-only journal disagrees with stopped empty cut')
 if owner.get('life_id')!=LIFE or owner.get('epoch')!=service.get('epoch')or any(owner.get('physical',{}).get(k)!=record['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')):raise ValueError('Actual stopped journal owner belongs to a different physical/protocol cut')
 manifest_path=actual_file(root,cut['paired_export']['manifest']);manifest=load(manifest_path)
 if sha(manifest_path)!=cut['paired_export']['manifest_sha256']or manifest['snapshot_sha256']!=maincut['snapshot_sha256']or manifest['physical']!=record['physical']or manifest['source_record']['life_id']!=LIFE:raise ValueError('Complete post-STOP paired export belongs to another cut')
 seen=set();verified_bytes=0;members={}
 for row in manifest['members']:
  name=row['file']
  if name in seen:raise ValueError('Duplicate paired member')
  seen.add(name);p=member(manifest_path.parent,name)
  if p.stat().st_size!=row['bytes']or sha(p)!=row['sha256']:raise ValueError('Paired operational member changed: '+name)
  members[name]=row;verified_bytes+=row['bytes']
 if members['VIDA.deetsnap.gz']['sha256']!=maincut['snapshot_sha256']or members['cola.sqlite3']['sha256']!=service['journal_sha256']:raise ValueError('Paired snapshot/journal do not match current saved cut')
 candidate_contract=a.candidates/'ASISTENTE_PROPOSITO_01.json';candidate_guide=a.candidates/'GUIA_ASISTENTE_APD01.md';contract_digest=sha(candidate_contract);guide_digest=sha(candidate_guide);contract=load(candidate_contract);guide=candidate_guide.read_text(encoding='utf8')
 if contract['id']!='ASISTENTE_PROPOSITO_01'or contract['selected_life']['life_id']!=LIFE:raise ValueError('Unexpected candidate identity')
 if contract['selected_life']['profile']!=record['profile']or contract['selected_life']['dimension']!=record['physical']['N']:raise ValueError('Candidate profile/dimension differs from the actual cut')
 observed={'old_memory':copy.deepcopy(cut.get('functional_results',{}).get('last_memory_observations',{})),'APD_forms':{},'scope':'Last actual recorded uses only, at their own ticks. Not a passive decoding of knowledge in the final snapshot and not a guarantee after later idle evolution.'}
 table=cp.parent/'PANELES_Y_FUNCIONES.json';table_sha=None
 if table.is_file():
  values=load(table)
  if values.get('underlying_recalculation_issues'):raise ValueError('Functional table integrity issues require review')
  table_sha=sha(table)
  primitive=values.get('APD_primitive_uses_including_composition_stages')
  if isinstance(primitive,list):
   for i,row in enumerate(primitive):
    form=row.get('form');tick=row.get('after_tick');command=row.get('word_command')
    if form in('suma','diferencia','agrega','resta','total','quita')and type(tick)is int:
     if form not in observed['APD_forms']or tick>=observed['APD_forms'][form]['reported_after_tick']:
      observed['APD_forms'][form]={'actual_word_command':command,'reported_after_tick':tick,'transport_id':row.get('id'),'JSON_locator':'/APD_primitive_uses_including_composition_stages/'+str(i),'table_relative_to_root':locator(root,table),'table_sha256':table_sha}
 if not observed['APD_forms']:observed['APD_forms_parse_status']='NOT_PARSED_OR_ABSENT_REFER_TO_EXACT_EVIDENCE_NO_SIGNS_INVENTED'
 epoch={'number':service.get('epoch'),'closed':service.get('epoch_closed'),'clean_closure_recorded':service.get('clean_closure'),'last_completed_transport_receipt':service.get('protocol',{}).get('last_completed_receipt')}
 state=contract['selected_life'];state.update(final_tick=maincut['tick'],final_snapshot=locator(root,snapshot),final_snapshot_sha256=maincut['snapshot_sha256'],paired_export_directory=locator(root,manifest_path.parent),paired_export_manifest_sha256=sha(manifest_path),persistent_epoch_status='EXPLICITLY_CLOSED'if epoch['closed']else'OPEN_REQUIRES_MATCHED_JOURNAL',fill_requirement='Filled from the exact verified stopped cut; Root reviews and installs this document proposal. No ACTIVO/promotion or native mutation performed.')
 contract['contract_revision']='APD01.R04.PROPOSED_FROM_ACTUAL_FINAL_CUT_N0';contract['publication_status']='DOCUMENT_PROPOSAL_FROM_VERIFIED_ACTUAL_CUT_AWAITING_ROOT_INSTALL';contract['actual_cut_evidence']={'root_relative_cut':locator(root,cp),'cut_sha256':sha(cp),'epoch':epoch,'integrity_issues':copy.deepcopy(cut['issues']),'operational_issues':copy.deepcopy(cut.get('operational_issues',[])),'recorded_clean_closure_is_not_overridden':service.get('clean_closure'),'observations':observed}
 for capability in contract['capability_attribution']:
  if capability['id']=='APD_LEXICAL_ASSOCIATIONS':capability['availability']=capability['availability'].replace('FINAL_PANEL_PENDING','LAST_RECORDED_USE_EVIDENCE_ATTACHED');capability['final_current_signs']=observed
  if capability['id']=='APD_ASSISTED_DSL_COMPOSITION':capability['availability']=capability['availability'].replace('FINAL_RESERVE_PENDING','FINAL_WINDOW_EVIDENCE_ATTACHED_NOT_UNLIMITED_ACCESS')
 manual={'edition_requested_by_root':a.manual_edition,'file':None,'sha256':None,'status':'ROOT_EDITORIAL_ARTIFACT_NOT_BOUND_BY_THIS_PROPOSAL'}
 if a.manual:
  mf=actual_file(root,str(a.manual));manual.update(file=locator(root,mf),sha256=sha(mf),status='EXACT_WORD_BYTES_BOUND_NO_RENDER_VALIDATION_BY_THIS_HELPER')
 continuity={'schema':'DEE.APD01.continuity.document_proposal.v1','life':copy.deepcopy(maincut),'root_relative_record':locator(root,card),'root_relative_snapshot':locator(root,snapshot),'paired_export':{'directory':locator(root,manifest_path.parent),'manifest':locator(root,manifest_path),'manifest_sha256':sha(manifest_path),'members_verified_read_only':len(members),'bytes_verified_read_only':verified_bytes},'epoch':epoch,'operational_issues':copy.deepcopy(cut.get('operational_issues',[])),'source_capture_scope':copy.deepcopy(cut.get('source_capture_scope')),'recorded_functional_results':copy.deepcopy(cut.get('functional_results',{})),'last_observed_uses':observed,'later_idle_ticks_do_not_guarantee_preserved_access':True,'manual':manual,'continuation':'Import this complete paired directory under a new identity, then use the existing mente-unificada owner. Never a bare snapshot/empty queue, never merge auxiliary memories. ASISTENTE_MAIN and ACTIVO were not changed by this generator.','separate_auxiliary_profiles_not_added_to_MAIN':True,'next_task':'Root reviews exact final evidence and installs only metadata/documents; experiment on an explicit complete personal copy.','new_native_ticks':0,'Runtime_imports':False}
 cutline=next((line for line in guide.splitlines()if line.startswith('Corte a completar:')),None)
 if not cutline:raise ValueError('Candidate guide marker changed; review explicitly rather than rewriting other content')
 replacement='Corte documentado: vida '+LIFE+'; tick '+str(maincut['tick'])+'; snapshot '+locator(root,snapshot)+'; SHA256 '+maincut['snapshot_sha256']+'; par completo '+locator(root,manifest_path.parent)+'; manifiesto SHA256 '+sha(manifest_path)+'; epoch '+str(epoch['number'])+' ('+('cerrado'if epoch['closed']else'abierto, diario obligatorio')+'); último recibo técnico '+str((epoch['last_completed_transport_receipt']or{}).get('id'))+'. Las últimas lecturas observadas preceden al ocio posterior; no garantizan acceso indefinido.'
 guide=guide.replace(cutline,replacement,1)
 old='**BORRADOR DE CIERRE.** Comandos cotejados con el gestor y esquemas actuales, sin ejecutar ticks. El corte final, snapshot, par de exportación y resultados de la reserva deben completarse por Root antes de publicar. No interpretar este archivo como confirmación de que terminó la reserva.'
 new='**PROPUESTA DOCUMENTAL DESDE EL CORTE REAL.** Identidades, bytes y par completo verificados en lectura, sin Runtime ni ticks. Root debe revisar e instalar. Esta generación no promociona la vida ni convierte una incidencia operacional o una abstención en éxito.'
 if old not in guide:raise ValueError('Guide header marker changed; no broad editorial rewrite')
 guide=guide.replace(old,new,1)
 guide=guide.replace('Las verificaciones de éxito del corte final, sus pérdidas, literalidades actualmente utilizables y snapshot exacto se completarán en la ficha de continuidad.','Las observaciones, pérdidas y snapshot exacto constan en la propuesta de continuidad y sus fuentes archivadas; son observaciones en sus propios ticks, no una garantía posterior.',1)
 entry={'id':'ASISTENTE_PROPOSITO_01','version':'APD01.R04.actual_cut_document_proposal','origin':'ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01; exact final stopped cut '+str(maincut['tick']),'implementation':'capacidades/asistente_proposito_01.py and its declared lexical/arithmetic/O2 modules; same gestor and paired service','contract':'contratos/ASISTENTE_PROPOSITO_01.json','availability':'BOUNDED_IMPLEMENTED_INTERFACES_WITH_ACTUAL_PER_LIFE_EVIDENCE_AND_RECORDED_LIMITS','integration':'One existing N67 ASISTENTE_MAIN physical world; original parent and ACTIVO preserved. No auxiliary-life knowledge merged.','knowledge':'Use recorded per-life observations in continuity; installed tokens and prepared numeric geometry are not automatically learned meanings.','limits':'Prepared SUM/affine DIFF/COUNT and assisted sequence; six admitted APD forms; local asymmetric consequence-conditioned route, not generalR2. Five accumulator opportunities observed; no sixth tested or physical erasure inferred.','execution_command':'estado --vida ASISTENTE_MAIN','life_id':LIFE,'tick':maincut['tick'],'snapshot_sha256':maincut['snapshot_sha256'],'paired_manifest_sha256':sha(manifest_path),'observed_clean_closure':service.get('clean_closure'),'operational_issues':copy.deepcopy(cut.get('operational_issues',[])),'publication_status':'PROPOSAL_AWAITING_ROOT_INSTALL_NO_GLOBAL_ACTIVO_CHANGE'}
 # Recheck mutable durable sources immediately before creating output proposals.
 if sha(card)!=maincut['record_sha256']or sha(snapshot)!=maincut['snapshot_sha256']or sha(journal)!=service['journal_sha256']or sha(cp)!=cut_digest:raise ValueError('Actual durable cut moved during read-only verification')
 if sha(candidate_contract)!=contract_digest or sha(candidate_guide)!=guide_digest or(table_sha is not None and sha(table)!=table_sha):raise ValueError('Input document/table bytes changed during proposal preparation')
 out.mkdir(parents=True);evidence=out/'EVIDENCIA';evidence.mkdir();copied=[]
 for p in[cp,*[cp.parent/n for n in('RESULTADO.json','RECALCULO_SERVICIO_APD.json','RECALCULO_TIEMPO_APD.json','PANELES_Y_FUNCIONES.json','RESULTADOS_SERVICIO_APD.md')if(cp.parent/n).is_file()]]:
  dest=evidence/p.name;shutil.copyfile(p,dest)
  if sha(dest)!=sha(p):raise ValueError('Evidence changed while copied')
  copied.append({'output':dest.relative_to(out).as_posix(),'source_root_relative':locator(root,p),'bytes':p.stat().st_size,'sha256':sha(p)})
 emit(out/'CONTINUIDAD_ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION.json',continuity);emit(out/'ASISTENTE_PROPOSITO_01.json',contract);emit(out/'ENTRADA_CATALOGO_APD01.json',entry);(out/'GUIA_ASISTENTE_APD01.md').write_text(guide,encoding='utf8')
 prefix='# APD01: corte operativo documentado\n\nASISTENTE_MAIN, N67, T'+str(maincut['tick'])+'. Continúe una copia del par completo indicado en CONTINUIDAD_ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION.json; no cambie ACTIVO ni use un snapshot sin diario.\n\nGuía: sistema/documentacion/GUIA_ASISTENTE_APD01.md. Manual Maestro edición '+a.manual_edition+': '+(manual['file']or'Root debe ligar los bytes editoriales exactos; esta propuesta no certifica renderizado')+'.\n\nCapacidades y límites se atribuyen por vida y momento. Consultar informe científico y tabla final existentes, sin sumar perfiles auxiliares. Cierre limpio registrado: '+str(service.get('clean_closure'))+'; incidencias operacionales conservadas en continuidad. Últimas lecturas antes de ocio no garantizan acceso posterior. No se certifican R2 general, español libre ni65 significados.\n'
 (out/'LEER_PRIMERO_APD01.md').write_text(prefix,encoding='utf8')
 generated=[{'file':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(out.rglob('*'))if p.is_file()]
 emit(out/'REGISTRO_PROPUESTA_N0.json',{'schema':'APD01.deterministic_actual_cut_document_proposal.v1','source_candidates':[{'file':str(p.resolve()),'sha256':sha(p)}for p in(candidate_contract,candidate_guide)],'source_cut_sha256':sha(cp),'generator_sha256':sha(Path(__file__)),'copied_exact_evidence':copied,'generated_members_before_this_log':generated,'approved_change_scope':'Fill pending cut/epoch/observed-use fields and guide markers; propose one catalog entry and root prefix. Preserve candidate mechanisms, inherited genealogy and negative/operational issues. No broad manual regeneration.','new_native_ticks':0,'Runtime_imported':False,'S_or_root_or_ACTIVO_written':False,'clean_false_never_promoted_to_PASS':True,'manual_rendering_verified_here':False})
 emit(out/'MANIFIESTO.json',{'members':[{'file':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(out.rglob('*'))if p.is_file()],'self_exclusion':'MANIFIESTO.json only'})
 print(json.dumps({'proposals':str(out),'life':LIFE,'tick':maincut['tick'],'snapshot_sha256':maincut['snapshot_sha256'],'recorded_clean_closure':service.get('clean_closure'),'new_ticks':0,'manual_or_system_installed':False,'manifest_sha256':sha(out/'MANIFIESTO.json')}))
if __name__=='__main__':main()

