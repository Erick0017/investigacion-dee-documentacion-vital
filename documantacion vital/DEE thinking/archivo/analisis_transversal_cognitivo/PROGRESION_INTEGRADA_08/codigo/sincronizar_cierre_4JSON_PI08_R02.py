"""Root-only CAS synchronization of four effective PI08 metadata JSON files.

No Native, ACTIVO/card/snapshot, code, RP registry or DOCX changes. Default is
a plan. --crear-plantilla writes P8 only, closed=false. Actual preparation and
--aplicar require separate FINAL scientific facts and REAL1.36 publication.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,json,os,shutil
P=Path(__file__).resolve().parents[1];H=P/'codigo';R=P.parents[2];C=R/'DEE Cognitive 2.0';S=C/'sistema';RP=C/'reproducibilidad'
A='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01';ASHA='2eeef08e3bebac4e218178ed379fd99aa5fdeb03650c0454ad55c6534824c133'
RID='pi08_a_panel12_regulado_T861426_R01';BRID='pi08_b_adquisicion18_desde_A_T861426_R01'
ARP='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_ARP_PANEL12_01'
FILES={'PROYECTO.json':C/'PROYECTO.json','CONTINUIDAD.json':C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json',
 'CATALOGO.json':S/'capacidades/CATALOGO_CAPACIDADES.json','REVISION_TRANSVERSAL.json':R/'archivo/analisis_transversal_cognitivo/REVISION_TRANSVERSAL.json'}
STAGE=H/'CIERRE_4JSON_PI08_1_36_R02_PROPUESTO';PLAN=P/'control/PLAN_CIERRE_4JSON_PI08_1_36_R02.json'
PROOF=P/'control/CIERRE_4JSON_PI08_1_36_APLICADO_R02.json';TEMPLATE=H/'CIERRE_CIENTIFICO_PI08_R01_PLANTILLA.json'
MANUAL=C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
COMP=R/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'
def require(ok,text):
 if not ok:raise ValueError(text)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return{'path':str(Path(p).resolve()),'sha256':sha(p)}
def regular(p):
 for q in(p,*p.parents):require(not q.exists()or not(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024),'No reparse/linked metadata path')
def put(p,v,replace=False):
 regular(p);p.parent.mkdir(parents=True,exist_ok=True);require(replace or not p.exists(),'Existing evidence/metadata stage protected')
 temp=p.with_name(p.name+'.PI08_WRITING')
 with temp.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(temp,p)
def checked(entry):
 path=Path(entry['path']).resolve(strict=True);regular(path)
 require(path.is_relative_to(P.resolve())or path.is_relative_to(RP.resolve()),'Only exact PI08 evidence or preserved RP references')
 require(sha(path)==entry['sha256'],'Actual source reference hash differs: '+str(path));return path
def main_guard():
 active=read(S/'estado/ACTIVO.json');card=read(S/'estado/vidas'/A/'VIDA.json')
 require(active.get('life_id')==A and active.get('tick')==861426 and card['physical']['N']==67 and card['physical']['tick']==861426 and card['snapshot_sha256']==ASHA and sha(S/card['snapshot'])==ASHA,'The protected actual principal A861426 must remain exact')
 require(not(S/'contratos/PI08_B_USO_OPERATIVO_R01.json').exists()and not(S/'capacidades/pi08_revision_flexible_B_R01.py').exists(),'No B deployment is permitted by this metadata operation')
 return card
def protected():
 card=main_guard();names=[S/'estado/ACTIVO.json',S/'estado/vidas'/A/'VIDA.json',S/card['snapshot'],S/'contratos/PI08_USO_OPERATIVO_R01.json',RP/'RECURSOS.json']
 adoption=read(P/'control/ADOPCION_PRODUCTO_PI08.json');preparation=read(P/'control/PREPARACION_TRASLADO_PRODUCTO_PI08.json')
 require(adoption['phase']=='COMMITTED'and preparation['phase']=='PREPARED_MOVED_NOT_PROMOTED'and adoption['life_id']==preparation['life_id']==A,'Actual same-identity A preparation/adoption witnesses required')
 require(isinstance(preparation.get('deployed_code'),list)and len(preparation['deployed_code'])==20,'The actual preparation holds the approved20-file deployment closure')
 for row in preparation['deployed_code']:
  file=S/row['file'];regular(file);require(file.resolve().is_relative_to(S.resolve()),'Bounded approved A code target')
  expected=(adoption['contract']['sha256']if row['file']=='contratos/PI08_USO_OPERATIVO_R01.json'else row['sha256'])
  require(sha(file)==expected,'Approved deployed A source or actual COMMITTED profile changed: '+row['file'])
  if file not in names:names.append(file)
 return{str(p):sha(p)for p in names}
def template():
 require(not TEMPLATE.exists(),'Previous template protected')
 card=main_guard();sources={}
 paths={'A_adoption':P/'control/ADOPCION_PRODUCTO_PI08.json','A_selected_public_use':P/'control/PI08_USO_PUBLICO_PRINCIPAL_R01.json',
  'A_complete_prefix':RP/'materiales/PI08_A_CONSOLIDADA_T861426/EXPORTACION_SERVICIO.json',
  'A_panel_result':P/'estados/RP_A_PANEL12_R01/RESULTADO_REPRODUCCION.json','A_panel_supervision':P/'control/SUPERVISION_RP_A_PANEL12_PI08_R01.json',
  'A_panel_passive':P/'control/VERIFICACION_RO_A_PANEL12_PI08_R01.json','A_panel_registration':RP/'verificaciones'/RID/(ARP+'.json'),
  'B_four_arms':P/'control/B_PORTABLE_CUATRO18_R01/RESULTADO_RECALCULO.json','B_conservation':P/'control/PI08_B_CONSERVACION_R02.json',
  'B_evaluation':P/'control/EVALUACION_B_ACTUAL_PI08_R01.json','B_RP_registration':P/'control/RP_B_ADQUISICION18_INCORPORADA_PI08_R01.json',
  'B_RP_requirements':P/'control/RP_B_REQUISITOS_CLI_PI08_R01.json','F1_failed_identity_primary':P/'ensayos/PI08_F1_CUT_R03_OP4.json',
  'world_reassignment':P/'control/REASIGNACION_MUNDO_F1_A_CONTROL_PI08_R01.json'}
 for key,path in paths.items():sources[key]=ref(path)if path.exists()else{'path':str(path),'sha256':None,'state':'PENDING_ACTUAL_ROOT_PROOF'}
 sources['C_final']={'path':None,'sha256':None,'state':'PENDING_FINAL_C_PROOF'}
 sources['NONE_final']={'path':str(P/'control/PI08_B_NONE_AUTOPSIA_PANEL_R02.json'),'sha256':None,'state':'PENDING_FINAL_NONE_PROOF'}
 value={'schema':'DEE.PI08.scientific_closure.effective_metadata_inputs.R01','closed':False,'all_scoped_Native_writers_closed':False,
  'main_actual':{'life_id':A,'status':'COMMITTED','N':67,'T':861426,'snapshot_sha256':ASHA,'physical':card['physical']},'sources':sources,
  'outcomes':{'A':{'adopted':True,'routes':['R03 acquired regulation','explicit retimed outer FI0..20','prepared C2C32 transaction/supply'],
    'RP_panel':{'closed':True,'correct':12,'witnesses':12,'Native_requested':947,'Native_applied':947,'final_tick':864977,'is_clone_not_Main_queries':True}},
   'B':{'adopted':False,'local_joint_useful_real_none_yoked_reference':[14,13,9,14],'conservation_correct':10,'conservation_witnesses':12,'new_B_CLI_replay_verified':False},
   'F1':{'identity_audit':'FAILED_PRESERVED','raw_cut_performed':False},
   'C':{'closed':False,'status':'PENDING_FINAL_NATIVE_RESULT','summary':None},
   'NONE':{'closed':False,'status':'PENDING_CONDITIONAL_ACTUAL_DIAGNOSTIC','summary':None}},
  'documentation_target':{'edition':'1.36','publication_confirmed':False,'actual_source_edition_at_template':'1.35','publication_proof':None},
  'instructions':'Root fills actual C/NONE terminal results and exact references, then sets closed/all_scoped_Native_writers_closed true. This scientific closure does not assert publication. Pass actual publication1.36 separately to the updater; no A/B native-code deployment.'}
 put(TEMPLATE,value);return TEMPLATE
def validate(factsfile,pubfile):
 factsfile=factsfile.resolve(strict=True);pubfile=pubfile.resolve(strict=True)
 require(factsfile.is_relative_to((P/'control').resolve())and pubfile.is_relative_to((P/'documentos').resolve()),'Explicit final facts/publication paths only')
 facts=read(factsfile);pub=read(pubfile)
 require(facts.get('schema')=='DEE.PI08.scientific_closure.effective_metadata_inputs.R01'and facts.get('closed')is True and facts.get('all_scoped_Native_writers_closed')is True,'Final factual closure required; no pending conclusions')
 require(not(P/'PI08_ROOT_NATIVE_WRITER.lock').exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'A scoped Native/RP writer remains')
 main=facts['main_actual'];require(main['life_id']==A and main['N']==67 and main['T']==861426 and main['snapshot_sha256']==ASHA and main['status']=='COMMITTED','Facts must preserve exact actual A')
 for entry in facts['sources'].values():checked(entry)
 outcomes=facts['outcomes'];require(outcomes['B']['adopted']is False and outcomes['B']['conservation_correct']==10 and outcomes['B']['conservation_witnesses']==12 and outcomes['B']['local_joint_useful_real_none_yoked_reference']==[14,13,9,14]and outcomes['B']['new_B_CLI_replay_verified']is False,'B adverse result/domain must remain exact')
 require(outcomes['F1']['raw_cut_performed']is False,'Do not invent a material F1 cut')
 for key in('C','NONE'):
  outcome=outcomes[key];require(outcome.get('closed')is True and isinstance(outcome.get('summary'),str)and outcome['summary']and 'PENDING'not in outcome.get('status','').upper(),'Actual terminal '+key+' facts required')
 require(pub.get('edition')=='1.36'and pub.get('Native_executed')is False,'Actual separate1.36 publication witness required')
 actual=pub['actual_main'];require(actual.get('life_id')==A and actual.get('tick',actual.get('T'))==861426 and actual.get('snapshot_sha256')==ASHA,'Publication must describe current A861426')
 docs={}
 for key,target in[('manual',MANUAL),('compendium',COMP)]:
  matches=[row for row in pub['files']if Path(row['target']).resolve()==target.resolve()];require(len(matches)==1,'Exact complete '+key+' publication target')
  row=matches[0];require(sha(target)==row['new_sha256']and target.stat().st_size==row['bytes'],'Actual published '+key+' bytes/SHA differ')
  docs[key]={'path':str(target),'bytes':row['bytes'],'sha256':row['new_sha256'],'internal_edition':'1.36','publication_witness':ref(pubfile),'visual_validation':pub.get('visual_validation')}
 registration=read(checked(facts['sources']['A_panel_registration']))
 require(registration['recipe']==RID and registration['actual_native_execution_completed']is True and registration['owner_closed_coherently']is True and registration['fixed_local_criteria_met']is True and registration['native_receipts']['unique_requested']==registration['native_receipts']['applied']==947,'Actual new A panel registration required')
 b=read(checked(facts['sources']['B_RP_registration']));require(b['applied']is True and b['B_new_CLI_replay_verified']is False,'Actual B prepared media, no false replay')
 requirements=read(checked(facts['sources']['B_RP_requirements']));require(isinstance(requirements,list)and any(row.get('recipe')==BRID and row.get('requirements_available')is True for row in requirements),'Actual B requirements-only CLI witness required')
 recipe=Path(b['recipe_path']);capsule=Path(b['capsule_manifest']);require(sha(recipe)==b['recipe_sha256']and sha(capsule)==b['capsule_manifest_sha256'],'Actual B stable recipe/capsule changed')
 require(read(recipe)['id']==BRID and len(read(capsule)['files'])==315,'Exact B315 prepared recipe/tool scope')
 current=main_guard();require(current['physical']==main['physical'],'Current SourceA physical descriptor changed')
 return facts,pub,docs,b
def transform(objects,closure,docs,b):
 result=copy.deepcopy(objects);project=result['PROYECTO.json'];cont=result['CONTINUIDAD.json'];cat=result['CATALOGO.json'];rev=result['REVISION_TRANSVERSAL.json']
 index=next(i for i,e in enumerate(cat['entries'])if e.get('id')=='PI08_REGULACION_ADQUIRIDA_CONSOLIDADA_A_01');oldA=copy.deepcopy(cat['entries'][index])
 history={'scope':'Literal descriptor observed at the A1.35 cut; pending B/C and future-use labels here are historical, not current closure.',
  'catalog_A_entry':oldA,'document_publication_A_1_35':ref(P/'documentos/PUBLICACION_A_1_35.json')}
 for obj in(project,cont,cat):
  require('PI08_history_at_edition_1_35'not in obj,'Existing historical closure protected');obj['PI08_history_at_edition_1_35']=copy.deepcopy(history)
  obj['PI08_scientific_closure_current']=copy.deepcopy(closure)
 historyrev={'scope':'Prior fields preserved literally before final PI08 closure. Their PI02 labels are historical; scientific pending labels originated atA1.35. Document references may already reflect the separate1.36 publication.',
  **{key:copy.deepcopy(rev.get(key))for key in('current_operation','current_operation_details','resume','current_primary_jobs','current_document_references')}}
 require('PI08_history_at_edition_1_35'not in rev,'Existing transverse closure protected');rev['PI08_history_at_edition_1_35']=historyrev
 rev['progression_integrated_PI08_closed_science']=copy.deepcopy(closure)
 rev['current_operation']='PI08 closed: A remains COMMITTED N67/T861426. RP A panel12 actual12/12 and947Applied in a diagnostic descendant. B14/13/9/14 remains unadopted after10/12 conservation. Manual1.36 published with its actual QA status; no Native state/code change in this synchronization.'
 rev['current_operation_details']={'main_actual':closure['main_actual'],'scientific_closure':closure['facts'],'publication':closure['publication'],'scope':'One protected selected A continuation; research/control futures remain separate.'}
 rev['resume']={'status':'PI08_SCIENCE_CLOSED_MAIN_A_PRESERVED','principal':A,'N':67,'tick':861426,'manual_internal_edition':'1.36','facts':closure['facts'],'publication':closure['publication'],
  'next':'Use the actual selected A continuation and its fixed finite contracts. B remains experimental; the new A RP panel and B prepared replay recipe are distinct. No merge of branch memories or silent retry.'}
 rev['current_primary_jobs']=[];rev['current_document_references']=copy.deepcopy(docs);rev['document_publication_PI08_1_36']=copy.deepcopy(docs)
 project.update(manual_internal_edition='1.36',manual_current_sha256=docs['manual']['sha256'],manual_current_bytes=docs['manual']['bytes'],manual_publication_witness=closure['publication']['path'],compendium_current=copy.deepcopy(docs['compendium']))
 for obj in(cont,cat):
  prior=copy.deepcopy(obj.get('manual_current',{}));prior.update(path=docs['manual']['path'],bytes=docs['manual']['bytes'],sha256=docs['manual']['sha256'],internal_edition='1.36',edition='1.36',publication_witness=closure['publication'],visual_validation=docs['manual']['visual_validation']);obj['manual_current']=prior
 cont['compendium_current']=copy.deepcopy(docs['compendium']);cont['last_documentary_update_PI08_final']=closure['publication']
 entry=cat['entries'][index]
 entry['limits']=[line for line in oldA['limits']if 'B/C siguen pendientes'not in line and 'El uso público posterior deberá'not in line]
 entry['limits']+=['The prior pending B/C descriptor and pre-public resource statement are preserved under PI08_history_at_edition_1_35. Current Main remains A861426; exact current resources belong to its unchanged complete state.',
  'The current-prefix A RP panel was actually executed in a clone:12/12,947Applied,13 then actual13−5=8. This is not twelve new material queries on Main.',
  'B local histories14/13/9/14 and correct C2C do not clear its10/12 inherited conservation failure; B is not selected/deployed. No universal advantage over the reference is claimed.']
 entry['PI08_final_scientific_closure']=closure['facts'];entry['PI08_actual_RP_panel12']={'recipe_id':RID,'kind':'material_reproduction_instrument_with_shared_complete_prefix','actual_registered_Native_execution':True,'source_Main_queried':False,'source_tick':861426,'diagnostic_final_tick':864977,'correct':12,'witnesses':12,'Native_requested':947,'Native_applied':947,'registration':closure['sources']['A_panel_registration'],'source_C2C_opportunity_consumed':False}
 bid='PI08_B_REVISION_LOCAL_REPRODUCCION_EXPERIMENTAL_01';require(not any(e.get('id')==bid for e in cat['entries']),'Existing experimental B entry protected')
 cat['entries'].append({'id':bid,'name':'PI08 B: preserved local histories and prepared acquisition recipe','kind':'instrumento_diagnostico_y_receta_material_preparada','status':'EXPERIMENTAL_NOT_ADOPTED_MATERIAL_REPLAY_PENDING',
  'mental_capacity_or_new_concept_count':0,'selected_principal':False,'deployed_to_Main':False,'local_joint_useful_real_none_yoked_reference':[14,13,9,14],'conservation':{'correct':10,'witnesses':12,'satisfied':False},
  'recipe_id':BRID,'recipe':{'path':b['recipe_path'],'sha256':b['recipe_sha256']},'code_capsule':{'path':b['code_capsule'],'manifest_sha256':b['capsule_manifest_sha256'],'files':315},
  'requirements':closure['sources']['B_RP_requirements'],'incorporation':closure['sources']['B_RP_registration'],'new_B_CLI_replay_verified':False,
  'scope':'Prepared diagnostic real18 from preserved A. Frozen Native actor remains in isolated histories/RP; not a B deployment, second principal or independent replay of18.'})
 require(cat['current_principal']==objects['CATALOGO.json']['current_principal'],'Current principal must be unchanged')
 require(project['selected_life']==objects['PROYECTO.json']['selected_life']and project['latest_saved_tick']==objects['PROYECTO.json']['latest_saved_tick'],'Main pointers must not change')
 require(cont['life_id']==objects['CONTINUIDAD.json']['life_id']and cont['physical_cut']==objects['CONTINUIDAD.json']['physical_cut'],'Continuity cut must not change')
 return result
def prepare(factsfile,pubfile):
 facts,pub,docs,b=validate(factsfile,pubfile)
 if PLAN.exists():
  plan=read(PLAN);require(plan['facts']==ref(factsfile)and plan['publication']==ref(pubfile),'Previous reviewed metadata stage protected');return plan
 require(not STAGE.exists(),'Partial previous stage protected; no implicit retry')
 objects={key:read(path)for key,path in FILES.items()}
 closure={'schema':'DEE.PI08.current_effective_scientific_closure.v1','main_actual':facts['main_actual'],'facts':ref(factsfile),'publication':ref(pubfile),
  'sources':facts['sources'],'outcomes':facts['outcomes'],'scientific_facts_do_not_assert_prior_publication':True,'documentation_published_now':True,
  'Native_ticks_for_this_metadata_sync':0,'Native_or_actor_deployment':False,'A_selected_unchanged':True,'B_adopted':False,'manual_edition':'1.36','visual_validation_actual':pub.get('visual_validation')}
 changed=transform(objects,closure,docs,b);rows=[]
 for key,path in FILES.items():
  regular(path);before=STAGE/'ANTES'/key;before.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,before)
  require(sha(before)==sha(path),'Concurrent metadata change during literal backup');after=STAGE/'PROPUESTOS'/key;put(after,changed[key])
  rows.append({'name':key,'target':str(path),'before_sha256':sha(path),'before_literal':str(before),'after':str(after),'after_sha256':sha(after)})
 plan={'schema':'DEE.PI08.four_JSON_closure.CAS_plan.R02','facts':ref(factsfile),'publication':ref(pubfile),'files':rows,'protected_unchanged':protected(),
  'Native_executed':False,'A_ACTIVO_card_snapshot_or_code_modified':False,'B_deployment':False,'catalog_instrument_entries_added':1,'mental_entries_added':0}
 put(PLAN,plan);return plan
def main(args):
 if args.crear_plantilla:
  require(not args.aplicar,'Template is never an apply operation');file=template();print(json.dumps({'template':str(file),'sha256':sha(file),'closed':False,'Native_executed':False}));return
 if args.facts is None or args.publication is None:
  require(not args.aplicar,'Explicit final facts and separate actual publication required')
  print(json.dumps({'mode':'PLAN_ONLY_NO_WRITES','targets':[str(p)for p in FILES.values()],'facts_argument':'P8/control/CIERRE_CIENTIFICO_PI08_R01.json','template':str(TEMPLATE),'requires_closed_science':True,'requires_actual_separate_publication':'1.36','current_Main':A,'current_tick':861426,'no_ACTIVO_card_snapshot_or_actor_changes':True,'Native_executed':False}));return
 plan=prepare(args.facts,args.publication)
 require(not PROOF.exists(),'Applied metadata proof already exists; do not repeat')
 require(protected()==plan['protected_unchanged'],'A/RP code/protected state changed after preparation')
 for row in plan['files']:require(sha(Path(row['target']))==row['before_sha256']and sha(Path(row['after']))==row['after_sha256'],'CAS metadata or reviewed stage changed')
 if args.aplicar:
  intent=P/'control/CIERRE_4JSON_PI08_1_36_INTENTO_R02.json';put(intent,{'plan':ref(PLAN),'Native_executed':False,'phase':'METADATA_ONLY_INTENT_NO_NATIVE_STATE_CHANGE'})
  for row in plan['files']:put(Path(row['target']),read(Path(row['after'])),replace=True)
  require(protected()==plan['protected_unchanged'],'Unexpected protected state/code change; preserve evidence')
  put(PROOF,{'schema':'DEE.PI08.four_JSON_closure.applied.R02','applied':True,'recorded_utc':datetime.now(timezone.utc).isoformat(),'facts':plan['facts'],'publication':plan['publication'],
   'files':[{'path':r['target'],'before_sha256':r['before_sha256'],'after_sha256':sha(Path(r['target'])),'literal_before':r['before_literal']}for r in plan['files']],
   'A_ACTIVO_card_snapshot_and_code_unchanged':True,'B_deployed':False,'Native_executed':False,'mental_entries_added':0,'historical_pending_descriptors_preserved_at_A_1_35':True})
 file=PROOF if args.aplicar else PLAN;print(json.dumps({'mode':'APPLIED_ROOT_ONLY'if args.aplicar else'P8_PLAN_READY_NO_PRODUCT_WRITES','proof':str(file),'sha256':sha(file),'Native_executed':False}))
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--crear-plantilla',action='store_true');parser.add_argument('--facts',type=Path);parser.add_argument('--publication',type=Path);parser.add_argument('--aplicar',action='store_true');main(parser.parse_args())
