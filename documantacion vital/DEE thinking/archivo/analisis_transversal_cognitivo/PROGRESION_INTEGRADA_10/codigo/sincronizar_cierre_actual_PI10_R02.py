"""Root-only final current-cut/document metadata synchronization; no Native.
Default prints requirements. With actual Manual/publication arguments, PLAN
checks all inputs and reports changes without writing. --aplicar preserves
six original descriptors, performs exact CAS and changes only current aliases.
Adoption COMMITTED at T945831 remains historical and untouched.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,importlib.util,json,os,re,zipfile
H=Path(__file__).resolve().parent;P=H.parent;C=H.parents[3]/'DEE Cognitive 2.0';S=C/'sistema'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01';OLD='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'
FILES=('PROYECTO.json','CONTINUIDAD_DEE_COGNITIVE_2_0.json','sistema/estado/ACTIVO.json','sistema/estado/genesis/SELECCION_PERSONAL.json','aplicacion/GENESIS/SELECCION_CANDIDATA.json','sistema/capacidades/CATALOGO_CAPACIDADES.json')
MANUAL='DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
CLIENT_SHA='8bf36a67a2683393a81b2c3120dcd588ea73484739ff59eac0e87398e3ca6d96'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def encoded(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def capture(v,keys):return {k:copy.deepcopy(v.get(k))for k in keys}
def setkeys(v,d):v.update(copy.deepcopy(d))
def historical(v,keys):v.setdefault('PI10_pre_final_sync_aliases_historical',capture(v,keys))
def witness(p):return {'path':str(p),'sha256':sha(p)}
def changed(a,b,path=''):
 if type(a)!=type(b):return[path or'/']
 if isinstance(a,dict):
  out=[]
  for k in sorted(set(a)|set(b)):
   q=path+'/'+k.replace('~','~0').replace('/','~1')
   out.extend([q]if k not in a or k not in b else changed(a[k],b[k],q))
  return out
 if isinstance(a,list):return []if a==b else[path]
 return []if a==b else[path]
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manual-sha256');ap.add_argument('--manual-bytes',type=int);ap.add_argument('--manual-edition',default='1.39');ap.add_argument('--compendium-sha256');ap.add_argument('--compendium-bytes',type=int);ap.add_argument('--publication-proof',type=Path);ap.add_argument('--aplicar',action='store_true');a=ap.parse_args()
 if not a.manual_sha256 or a.manual_bytes is None or a.publication_proof is None:
  need(not a.aplicar,'Manual current SHA/bytes/publication proof required')
  print(json.dumps({'mode':'REQUIREMENTS_ONLY_NO_NATIVE','required':['--manual-sha256 ACTUAL','--manual-bytes ACTUAL','--publication-proof ACTUAL_JSON'],'edition':a.manual_edition,'default':'PLAN no writes; --aplicar Root only','six_selectors':FILES,'preserved':'COMMITTED adoption record/contract at945831, existing history and Native worlds'}));return 0
 now=datetime.now(timezone.utc).isoformat();manual=C/MANUAL;a.publication_proof=a.publication_proof.resolve()
 need(re.fullmatch('[0-9a-f]{64}',a.manual_sha256)is not None and manual.is_file()and sha(manual)==a.manual_sha256 and manual.stat().st_size==a.manual_bytes,'Actual complete Manual hash/bytes must match arguments')
 need(a.publication_proof.is_file()and a.publication_proof.resolve().is_relative_to(P.resolve()),'Publication proof must exist inside PI10 campaign')
 with zipfile.ZipFile(manual)as z:
  need(z.testzip()is None,'Manual ZIP integrity')
  xml=z.read('word/document.xml').decode('utf-8');need('DCS11-MM-001'in xml and a.manual_edition in xml,'Manual ID/internal edition must be represented; no renaming')
 proofpath=P/'control/PI10_PRODUCTO_EP13_OWNER_R02.json';proof=read(proofpath)
 need(proof.get('closed')is True and proof.get('error')is None and proof.get('status')=='CLOSED_FINITE_PHASE'and proof.get('life_id')==LIFE and proof.get('original_ordinal_before')==13 and proof.get('original_ordinal_after')==14 and proof.get('functional_success')is True,'Actual completed useful post-COMMITTED R05 opportunity13/reopen proof required')
 need(proof['new_Native_ticks']==1564 and proof['final_tick']==947395 and proof['reopen0']['new_ticks']==0 and all(proof['reopen0']['Native_field_equalities'].values()),'Exact completed proof scope required')
 need(sha(S/'app/cliente_mente_unificada.py')==CLIENT_SHA,'Reviewed one-line public client hash changed')
 adoption=P/'control/ADOPCION_PRODUCTO_PI10_R02.json';adopt=read(adoption);contractpath=S/'contratos/PI10_USO_OPERATIVO_R01.json';contract=read(contractpath)
 need(adopt.get('phase')=='COMMITTED'and adopt['life_id']==LIFE and adopt['record']['physical']['tick']==945831,'Historical same-ID adoption must remain945831')
 need(contract.get('status')=='COMMITTED'and contract.get('life_id')==LIFE,'Current exact contract must remain COMMITTED')
 cardpath=S/'estado/vidas'/LIFE/'VIDA.json';card=read(cardpath);snap=S/card['snapshot'];active=read(C/FILES[2])
 need(card['life_id']==card['world_id']==active['life_id']==LIFE and card['physical']['N']==67 and card['physical']['tick']==active['tick']==proof['final_tick'] and card['snapshot_sha256']==active['snapshot_sha256']==proof['snapshot_sha256']==sha(snap),'Current final saved card/ACTIVO/full Native identity mismatch')
 guardfile=H/'comprobar_proceso_PI10_R02.py';need(sha(guardfile)=='21d41a1e429f135d100f17826258561dc9f98ca52a465cc2015f30efb5966adb','Process guard changed')
 spec=importlib.util.spec_from_file_location('PI10_final_sync_read_only_guard',guardfile);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);process=g.inspect('PI10_final_documentary_sync',S,LIFE);need(process['no_live_affected_writer'],'Actual final world must be closed and reconciled')
 need(not(P/'PI10_ROOT_NATIVE_WRITER.lock').exists()and not(C/'reproducibilidad/EJECUCION_MATERIAL.lock').exists(),'Root/RP material writer lock remains; do not synchronize a live future')
 before_protected={str(p):sha(p)for p in(cardpath,snap,adoption,contractpath,S/'estado/vidas'/OLD/'VIDA.json',S/'app/cliente_mente_unificada.py')}
 before={name:read(C/name)for name in FILES};cas={name:sha(C/name)for name in FILES};after=copy.deepcopy(before)
 current_snapshot={'path_relative_to_product':'sistema/'+card['snapshot'],'sha256':card['snapshot_sha256']}
 current_card={'path_relative_to_product':cardpath.relative_to(C).as_posix(),'sha256':sha(cardpath)}
 manual_descriptor={'path':str(manual),'path_relative_to_product':MANUAL,'bytes':a.manual_bytes,'sha256':a.manual_sha256,'internal_edition':a.manual_edition,'edition':a.manual_edition,'document_publication':str(a.publication_proof),'publication_witness':witness(a.publication_proof),'visual_validation':'See actual publication/render proof; this synchronization performs no rendering'}
 use={'proof':witness(proofpath),'life_id':LIFE,'request_id':proof['actual_row'].get('request_id',proof['records'][0]['id']),'before_tick':proof['initial_tick'],'after_tick':proof['final_tick'],'new_Native_ticks':proof['new_Native_ticks'],'functional_success':True,'physical_resource':proof['physical_resource'],'attributed_useful':proof['attributed_useful'],'original_ordinal_before':13,'original_ordinal_after':14,'remaining_original_offers':4,'reopened_without_new_ticks':True,'scope':'One real selected public opportunity after COMMITTED, followed by STATE/save/close/reopen0; not another full inherited panel at947395.'}
 closed={'schema':'DEE.PI10.actual_final_closed_current.R01','life_id':LIFE,'world_id':LIFE,'profile':card['profile'],'physical':card['physical'],'snapshot':current_snapshot,'identity_card':current_card,'recorded_utc':now,'post_committed_public_use':use,'adoption_point_historical':{'tick':945831,'witness':witness(adoption)},'finite_PI10_supply':{'used':14,'total':18,'remaining':4,'no_reset_or_resupply':True},'Native_queries_in_this_sync':0}
 # Personal pointer and simple existing-continuation entry: current references only.
 personal=after[FILES[3]];historical(personal,('current_saved_tick','current_saved_snapshot_sha256','current_identity_card_sha256','current_cut_updated_utc'))
 setkeys(personal,{'current_saved_tick':947395,'current_saved_snapshot_sha256':card['snapshot_sha256'],'current_identity_card_sha256':sha(cardpath),'current_cut_updated_utc':now,'PI10_post_committed_use':use})
 seed=after[FILES[4]];historical(seed,('source_tick','source_snapshot_sha256','current_operational_snapshot_sha256','current_operational_tick','latest_actual_use'))
 need(seed.get('existing_continuation_only')is True and seed.get('source_life')==LIFE,'Do not rewrite a separate historical seed')
 setkeys(seed,{'source_tick':947395,'source_snapshot_sha256':card['snapshot_sha256'],'current_operational_tick':947395,'current_operational_snapshot_sha256':card['snapshot_sha256'],'latest_actual_use':witness(proofpath),'PI10_post_committed_use':use})
 # Product project aliases; adoption object is explicitly left unchanged.
 project=after[FILES[0]];keys=('latest_saved_tick','current_operational_snapshot','current_operational_identity_card_sha256','operational_current_cut','operational_current_snapshot','latest_selected_use','manual_internal_edition','manual_current_sha256','manual_current_bytes','manual_publication_witness','selected_operational_use_pending','selected_material_function_test_pending','selected_material_function_test_executed')
 historical(project,keys)
 setkeys(project,{'latest_saved_tick':947395,'current_operational_snapshot':current_snapshot,'current_operational_identity_card_sha256':sha(cardpath),'operational_current_cut':card['physical'],'operational_current_snapshot':current_snapshot,'latest_selected_use':use,'manual_internal_edition':a.manual_edition,'manual_current_sha256':a.manual_sha256,'manual_current_bytes':a.manual_bytes,'manual_publication_witness':str(a.publication_proof),'selected_operational_use_pending':False,'selected_material_function_test_pending':False,'selected_material_function_test_executed':True,'selected_material_function_success':True,'PI10_final_closed_current':closed})
 # Continuity aliases, including embedded copies actually used by the application.
 con=after[FILES[1]];historical(con,('physical_cut','latest_snapshot','identity_card','manual','manual_current','latest_operational_use','personal_selection','selected_seed','selected_material_function_test_pending','selected_material_function_test_executed'))
 available=con.get('current_available_lives',[]);available=[LIFE]+[v for v in available if v!=LIFE]
 setkeys(con,{'updated_utc':now,'physical_cut':card['physical'],'latest_snapshot':current_snapshot,'identity_card':current_card,'personal_selection':personal,'selected_seed':seed,'manual':manual_descriptor,'manual_current':manual_descriptor,'latest_operational_use':use,'selected_material_function_test_pending':False,'selected_material_function_test_executed':True,'selected_material_function_success':True,'current_available_lives':available,'PI10_final_closed_current':closed})
 # Catalog retains earlier validated_lives coverage and adds a narrow public-use record.
 cat=after[FILES[5]];historical(cat,('current_principal','manual_current'))
 cp=cat['current_principal'];need(cp['life_id']==LIFE,'Catalog principal mismatch');cp.setdefault('PI10_adopted_cut_historical',capture(cp,('tick','snapshot_sha256','updated_utc')));setkeys(cp,{'tick':947395,'snapshot_sha256':card['snapshot_sha256'],'updated_utc':now,'latest_closed_current':closed})
 cat['manual_current']=manual_descriptor;cat['PI10_final_closed_current']=closed
 entries=[e for e in cat['entries']if e.get('id')=='PI10_R02_CONSULTA_CONTEXTO_DOS_TRAZAS'];need(len(entries)==1,'Exact one PI10 catalog entry required')
 e=entries[0];e['post_committed_public_use']=use;e['current_executable_life']=closed;e['implementation']=list(dict.fromkeys([*e['implementation'],'app/cliente_mente_unificada.py']));e['public_client_repair']={'implementation':'app/cliente_mente_unificada.py','sha256':CLIENT_SHA,'proof':witness(P/'control/REPARACION_CLIENTE_PUBLICO_PI10_R05/APLICACION.json'),'scope':'Technical import path only; no Native policy/physics/learned-state edit'}
 if a.compendium_sha256 is not None or a.compendium_bytes is not None:
  need(a.compendium_sha256 is not None and a.compendium_bytes is not None,'Both actual Compendium SHA/bytes required')
  oldcomp=before[FILES[0]]['compendium_current'];compath=Path(oldcomp['path']).resolve()
  need(compath.is_relative_to(C.parent.resolve())and compath.is_file()and sha(compath)==a.compendium_sha256 and compath.stat().st_size==a.compendium_bytes,'Actual current Compendium identity mismatch')
  with zipfile.ZipFile(compath)as z:
   need(z.testzip()is None and a.manual_edition in z.read('word/document.xml').decode('utf-8'),'Compendium ZIP/internal current edition mismatch')
  compdesc=copy.deepcopy(oldcomp);compdesc.update({'sha256':a.compendium_sha256,'bytes':a.compendium_bytes,'internal_edition':a.manual_edition,'publication_witness':witness(a.publication_proof)})
  for name in(FILES[0],FILES[1],FILES[5]):
   after[name].setdefault('PI10_pre_final_compendium_historical',copy.deepcopy(before[name].get('compendium_current')))
   after[name]['compendium_current']=copy.deepcopy(compdesc)
 need(after[FILES[2]]==before[FILES[2]],'ACTIVO was already correct: verify it, do not edit')
 need(project['operational_adoption']==before[FILES[0]]['operational_adoption'],'Never rewrite the945831 adoption cut')
 deltas={name:changed(before[name],after[name])for name in FILES};mutated=[name for name in FILES if deltas[name]]
 result={'schema':'DEE.PI10.final_current_metadata_sync.R02','mode':'APPLY'if a.aplicar else'PLAN','at':now,'life_id':LIFE,'actual_final_tick':947395,'actual_final_snapshot_sha256':card['snapshot_sha256'],'Manual':manual_descriptor,'post_use':use,'cas_before':cas,'changed_paths':deltas,'modified_files':mutated,'already_correct_verified':['sistema/estado/ACTIVO.json'],'protected_hashes_before':before_protected,'Native_calls':0,'adoption945831_untouched':True,'historical_fields_retained':True}
 if not a.aplicar:print(json.dumps(result,ensure_ascii=False,indent=2));return 0
 out=P/'control/SINCRONIZACION_CIERRE_ACTUAL_PI10_R02';need(not out.exists(),'No overwrite sync transaction')
 need(all(sha(C/name)==cas[name]for name in FILES),'All six selector CAS must hold before first write')
 out.mkdir();backup=out/'originales';backup.mkdir()
 for name in FILES:
  b=backup/name;b.parent.mkdir(parents=True,exist_ok=True);b.write_bytes((C/name).read_bytes());need(sha(b)==cas[name],'Original descriptor backup mismatch')
 (out/'INTENCION.json').write_bytes(encoded(result))
 for name in mutated:
  target=C/name;need(sha(target)==cas[name],'Final per-file CAS mismatch')
  temp=target.with_name(target.name+'.PI10_FINAL_WRITING');need(not temp.exists(),'Do not overwrite another writer temp')
  with temp.open('xb')as f:f.write(encoded(after[name]));f.flush();os.fsync(f.fileno())
  os.replace(temp,target);need(read(target)==after[name],'Written descriptor mismatch')
 result['cas_after']={name:sha(C/name)for name in FILES};result['protected_hashes_after']={p:sha(p)for p in before_protected};need(result['protected_hashes_after']==before_protected,'Native/card/adoption/contract/oldD/client changed')
 result['all_six_json_readable']=all(read(C/name)==after[name]for name in FILES);result['completed']=True
 f=out/'SINCRONIZACION.json';f.write_bytes(encoded(result));print(json.dumps({'proof':str(f),'sha256':sha(f),'modified':mutated,'ACTIVO_verified_not_modified':True,'Native_calls':0},ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())

