"""Publish only the frozen/visually reviewed1.29documents and continuity metadata.

Run only after Root's explicit approval of the actual render (flag below).
No Native import, owner, physical state write, selector change or promotion.
The already committed actual principal is checked, never selected by this code.
"""
from pathlib import Path
from copy import deepcopy
import argparse,collections,datetime,hashlib,json,os
P=Path(__file__).resolve().parent.parent;D=P/'documentos';R=P.parents[2];C=R/'DEE Cognitive 2.0'
EXPECTED={'Manual':'d6f3b8d8cbf12353573f062bd7730b679aef2768f8487de79c9348c734c11f01','Compendium':'26b58062eac0a804bd73f27139dc5b9d7a9bafa1579d67babedc420105baf9c7'}
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def desc(path):return {'path':str(path.resolve()),'bytes':path.stat().st_size,'sha256':sha(path)}
def encoded(value):return(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def replace(path,data,expected):
    if sha(path)!=expected:raise ValueError('Concurrent publication target change:'+str(path))
    temp=path.with_name(path.name+'.PI02_FINAL_PUBLICACION.tmp')
    if temp.exists():raise ValueError('Prior interrupted publication temporary protected')
    temp.write_bytes(data)
    if temp.read_bytes()!=data or sha(path)!=expected:raise ValueError('Concurrent source/temp write inconsistency')
    os.replace(temp,path)
    if path.read_bytes()!=data:raise ValueError('Published bytes differ')
def historical_field(data,key,backup_name):
    value=deepcopy(data.get(key))
    if backup_name in data and data[backup_name]!=value:raise ValueError('Historical field already has a different preserved value:'+backup_name)
    data[backup_name]=value
def journal_count():
    path=P/'ENSAYOS.jsonl';all_bytes=path.read_bytes();last=all_bytes.rfind(b'\n')+1;prefix=all_bytes[:last]
    records=[json.loads(line)for line in prefix.splitlines()];unique={}
    for row in records:
        if row.get('kind')!='MATERIAL_REQUEST':continue
        key=(row['life'],row['id'])
        if key in unique:raise ValueError('Duplicate material operation ID in campaign journal')
        unique[key]=row
    completed=[r for r in unique.values()if r['status']=='completed']
    if any(type(r.get('before_tick'))is not int or type(r.get('after_tick'))is not int or r['after_tick']<r['before_tick']for r in completed):raise ValueError('Invalid completed tick interval')
    count=sum(r['after_tick']-r['before_tick']for r in completed)
    return {'journal':str(path),'prefix_bytes':len(prefix),'prefix_sha256':hashlib.sha256(prefix).hexdigest(),'last_material_id':next(reversed(unique.values()))['id'],'unique_material_operations':len(unique),'statuses':dict(collections.Counter(r['status']for r in unique.values())),'completed_material_native_tick_sum_across_related_branches':count,'unscored_failed_ids':[r['id']for r in unique.values()if r['status']!='completed'],'scope':'Completed unique queue-operation deltas across branches, not MAINage/independent learning counts/live uncheckpointed progress. Failed futures remain separate. New Native ticks by this publication0.'}
def main(args):
    if not args.root_approved:raise ValueError('Actual final document render must be approved by Root before publication')
    witness=D/'DOCUMENTOS_PUBLICADOS_PI02_FINAL.json'
    if witness.exists():raise ValueError('Final publication already witnessed; inspect and reuse')
    stage_path=D/'ACTUALIZACION_DOCUMENTAL_PI02_FINAL_1_29.json';stage=read(stage_path);render_path=D/'RENDER_WORD_PI02_FINAL_1_29_R01.json';render=read(render_path)
    qm_path=D/'QA_VISUAL_MANUAL_PI02_FINAL.json';qc_path=D/'QA_VISUAL_COMPENDIO_PI02_FINAL.json';qm=read(qm_path);qc=read(qc_path)
    if qm.get('blocking_findings')or qc.get('blocking_findings')or qc.get('blocking_issues_within_reviewed_scope'):raise ValueError('Final visual blocker unresolved')
    if not any(key in qc for key in('blocking_findings','blocking_issues_within_reviewed_scope')):raise ValueError('Compendium QA has no explicit blocker scope')
    for kind in('Manual','Compendium'):
        item=stage[kind];row=next(x for x in render if x['Kind']==kind)
        if item['source_sha256']!=EXPECTED[kind]or sha(item['source'])!=EXPECTED[kind]or sha(item['output'])!=item['sha256']or row['InputSha256']!=item['sha256']or sha(row['Output'])!=row['OutputSha256']:raise ValueError('Source/staged/render bytes changed')
        if sha(D/'respaldo_1_28'/Path(item['source']).name)!=EXPECTED[kind]:raise ValueError('Complete literal1.28backup missing/different')
    if stage['Manual']['sha256']!='32e5c92f5e912d293474b80d757373f0a14882c4fbcbba65e0f9189ea557178c':raise ValueError('This approval is for actual frozen R01Master only')
    closed_path=P/'control/CIERRE_CIENTIFICO_PI02.json';closed=read(closed_path)
    if not closed['closed_for_authoring']or sha(closed_path)!=stage['closed_scientific_input']['sha256']:raise ValueError('Closed scientific input differs from actual rendered document')
    m=closed['manual_1_29'];active_path=C/'sistema/estado/ACTIVO.json';active_before=desc(active_path);active=read(active_path)
    if(active['life_id'],active['tick'])!=('ECI02_PI02_MAIN',753346)or m['principal']['life_id']!=active['life_id']or m['principal']['tick']!=active['tick']:raise ValueError('Actual committed principal differs; do not choose or overwrite it')
    continuity_PI02=P/'CONTINUIDAD_PI02.json'
    if not continuity_PI02.is_file():raise ValueError('Root must first write the adopted PI02continuity locator; publication remains pending')
    read(continuity_PI02)
    project_path=C/'PROYECTO.json';continuity_path=C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json';registry_path=R/'archivo/analisis_transversal_cognitivo/REVISION_TRANSVERSAL.json';campaign_path=P/'REGISTRO_CAMPANA.json'
    metadata_paths=[project_path,continuity_path,registry_path,campaign_path];before_bytes={str(p):p.read_bytes()for p in metadata_paths};before={str(p):desc(p)for p in metadata_paths}
    project=read(project_path);continuity=read(continuity_path);registry=read(registry_path);campaign=read(campaign_path)
    if project['manual_internal_edition']!='1.28'or continuity['manual']['edition']!='1.28':raise ValueError('Current editorial source must still be1.28')
    for path in metadata_paths:
        name=path.name if path!=registry_path else'REVISION_TRANSVERSAL.json';backup=D/'respaldo_1_28'/name
        if backup.exists():
            if backup.read_bytes()!=before_bytes[str(path)]:raise ValueError('Different prior final-editorial backup protected')
        else:backup.write_bytes(before_bytes[str(path)])
    now=datetime.datetime.now(datetime.timezone.utc).isoformat();manual=stage['Manual'];man_render=next(x for x in render if x['Kind']=='Manual')
    manual_description={'path':manual['source'],'bytes':manual['bytes'],'sha256':manual['sha256'],'internal_edition':'1.29','same_logical_manual_and_filename':True,
        'prior_complete_document':desc(D/'respaldo_1_28'/Path(manual['source']).name),'rendered_pdf':desc(Path(man_render['Output'])),'rendered_pages':120,
        'visual_qa':{'manual':desc(qm_path),'compendium':desc(qc_path),'scope':'All-page contact overviews plus affected pages; no claim of a new full historical scientific rereading.'},
        'publication_witness':str(witness),'historical_stage_A':'Edition1.28/PI01principal/cutA740343 retained literally in chapter44; chapter45 is the actual later closure.'}
    project['manual_before_PI02_FINAL_historical']={key:deepcopy(value)for key,value in project.items()if key.startswith('manual')}
    project['manual_internal_edition']='1.29';project['manual_current_sha256']=manual['sha256']
    continuity['manual_before_PI02_FINAL_historical']={key:deepcopy(continuity[key])for key in('manual','manual_current')}
    continuity['manual']={**continuity['manual'],'edition':'1.29','sha256':manual['sha256'],'document_publication':str(witness)};continuity['manual_current']=manual_description
    for key,backup in(('resume','resume_before_PI02_COMMITTED'),('current_operation','current_operation_before_PI02_COMMITTED'),('current_operation_details','current_operation_details_before_PI02_COMMITTED'),('manual_update','manual_update_before_PI02_FINAL')):historical_field(registry,key,backup)
    registry['manual_update']=deepcopy(manual_description)
    registry['resume']={'status':'PI02_SCIENTIFIC_AND_OPERATIONAL_CLOSED_FINAL_ZIP_PENDING','principal':active['life_id'],'N':67,'tick':active['tick'],'manual_internal_edition':'1.29','continuity':str(continuity_PI02),'continuity_at_document_publication':desc(continuity_PI02),'next':m['continuation_paragraph'],'final_analysis_zip':'Pending final packaging/manifest verification; do not infer delivery from document publication.'}
    registry['current_operation']='PI02 COMMITTED: ECI02_PI02_MAIN, N67, T753346. The actual adopted complete state is selected; Manual1.29 published and Word-rendered. PI01T735843 and divergent controls remain preserved. This editorial operation ran no Native ticks.'
    registry['current_operation_details']={'life_id':active['life_id'],'N':67,'tick':active['tick'],'profile':active['profile'],'selection':'COMMITTED','ACTIVO':deepcopy(active),'manual':deepcopy(manual_description),'continuity':str(continuity_PI02),'document_publication':str(witness),'parent_physical':{'life_id':'ECI02_PI01_MAIN','tick':735843},'source_scientific_closure':desc(closed_path),'native_execution_by_editor':False}
    previous=deepcopy(registry.get('progression_integrated_PI02',{}))
    registry['progression_integrated_PI02']={'status':'COMMITTED','updated_utc':now,'campaign':str(P),'current_principal':{'life_id':active['life_id'],'N':67,'tick':active['tick'],'profile':active['profile']},'continuity':str(continuity_PI02),'manual':deepcopy(manual_description),'stageA_documented_historical':previous,'scientific_closure':desc(closed_path),'scope':'Actual progression and adoption are corroborated by their own records; this publication changes only documents/continuity metadata, not physics or selection.'}
    registry['manual_update_PI02_FINAL']={'edition':'1.29','updated_utc':now,'publication':str(witness),'same_DCS11_MM_001':True,'source_before_edition':'1.28','retained_stageA_chapter44':True};registry['updated_utc']=now
    counts=journal_count();campaign.setdefault('phase_history',[]).append({'prior_phase':campaign['phase'],'prior_tick_counter':campaign['new_native_ticks_so_far'],'updated_utc':now,'scope':'Final documentary synchronization after actual Nativeadoption, not a new physical experience'})
    campaign['phase']='CLOSED_SCIENCE_AND_COMMITTED_OPERATION_DOCUMENTS_1_29_FINAL_ZIP_PENDING';campaign['new_native_ticks_so_far']=counts['completed_material_native_tick_sum_across_related_branches'];campaign['final_recorded_journal_scope']=counts
    campaign['principal_final']={'life_id':active['life_id'],'N':67,'tick':active['tick'],'profile':active['profile'],'selection':'COMMITTED','physical_parent':{'life_id':'ECI02_PI01_MAIN','tick':735843},'continuity':str(continuity_PI02)}
    campaign['manual_final']={'edition':'1.29','path':manual['source'],'sha256':manual['sha256'],'publication':str(witness)};campaign['closed_documentary_utc']=now;campaign['final_zip_verification']='PENDING_ROOT_SEAL_NO_NATIVE'
    # Permit only manual-related product metadata; operational fields are literal.
    for path,value,allowed in((project_path,project,{'manual_before_PI02_FINAL_historical','manual_internal_edition','manual_current_sha256'}),(continuity_path,continuity,{'manual_before_PI02_FINAL_historical','manual','manual_current'})):
        old=json.loads(before_bytes[str(path)].decode('utf-8-sig'));changed={k for k in set(old)|set(value)if old.get(k)!=value.get(k)}
        if not changed<=allowed:raise ValueError('Unexpected nonmanual product metadata edit:'+str(changed))
    done=[]
    try:
        for kind in('Manual','Compendium'):
            item=stage[kind];replace(Path(item['source']),Path(item['output']).read_bytes(),EXPECTED[kind]);done.append(desc(Path(item['source'])))
        for path,value in((project_path,project),(continuity_path,continuity),(registry_path,registry),(campaign_path,campaign)):
            replace(path,encoded(value),before[str(path)]['sha256']);done.append(desc(path))
        if desc(active_path)!=active_before:raise ValueError('ACTIVO changed concurrently; do not claim stable selection')
    except BaseException as exc:
        (D/'DOCUMENTOS_PUBLICADOS_PI02_FINAL_ERROR.json').write_bytes(encoded({'error':repr(exc),'completed_files':done,'metadata_before':before,'scope':'Partial editorial operation preserved, no Native rollback or state repair'}));raise
    result={'schema':'PI02.final.document_publication.v1','created_utc':now,'status':'PUBLISHED_SAME_MASTER_1_29','published_files':done,'metadata_before':before,'complete_prior_documents':stage['literal_prior_documents'],
        'render_proof':desc(render_path),'visual_QA':[desc(qm_path),desc(qc_path)],'closed_scientific_input':desc(closed_path),'continuity_at_publication':desc(continuity_PI02),'ACTIVO_before':active_before,'ACTIVO_after':desc(active_path),'principal_final':active,
        'new_native_ticks':0,'DEE_imports':0,'operational_state_code_or_selection_modified_by_publication':False,'publication_does_not_execute_adoption':True,'source_manual_filename_preserved':True,'final_ZIP':'Root must seal/verify after this publication and refresh Fmetadata copies.'}
    witness.write_bytes(encoded(result));print(json.dumps({'witness':str(witness),'published':done,'principal':active['life_id'],'tick':active['tick'],'journal_completed_ticks_multibranch':counts['completed_material_native_tick_sum_across_related_branches']},ensure_ascii=False,indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root-approved',action='store_true');main(parser.parse_args())
