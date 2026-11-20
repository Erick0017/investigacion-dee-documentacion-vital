"""Read-only PI10 ledger; an exact same-ID product move never refunds a world."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';MAIN='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01';OLD_D='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def moved_main():
 cardfile=S/'estado/vidas'/MAIN/'VIDA.json'
 if not cardfile.exists():return None
 need(not(P/'estados/REAL2/sistema/estado/vidas'/MAIN/'VIDA.json').exists(),'Do not count duplicate same-ID worlds; exact whole move required');preparedfile=P/'control/PREPARACION_TRASLADO_PRODUCTO_PI10_R02.json';prepared=read(preparedfile);mappingfile=P/'control/MAPA_TRASLADO_PRODUCTO_PI10_R02.json';mapping=read(mappingfile);need(prepared.get('phase')=='PREPARED_MOVED_NOT_PROMOTED'and prepared.get('life_id')==MAIN and prepared['map']['sha256']==sha(mappingfile),'Actual prepared whole-move receipt/map required')
 need(mapping.get('same_life_id')==mapping.get('same_world_id')==MAIN and Path(mapping['source_system']).resolve()==(P/'estados/REAL2/sistema').resolve()and Path(mapping['target_system']).resolve()==S.resolve()and mapping.get('not_a_new_life_or_import')is True,'Exact three-tree same-ID map only');card=read(cardfile);need(card['life_id']==card['world_id']==MAIN and card['parent']==mapping['historical_parent_literal_preserved']and sha(S/card['snapshot'])==card['snapshot_sha256'],'Current moved identity/genealogy/snapshot must remain coherent')
 active=read(S/'estado/ACTIVO.json');profile=read(S/'contratos/PI10_USO_OPERATIVO_R01.json');committedfile=P/'control/ADOPCION_PRODUCTO_PI10_R02.json'
 if active['life_id']==MAIN:
  committed=read(committedfile);need(committed.get('phase')=='COMMITTED'and committed.get('life_id')==MAIN and profile.get('status')=='COMMITTED'and profile.get('life_id')==MAIN and profile.get('all_adoption_gates_met')is True,'Actual committed product permission/receipt required')
 else:need(active['life_id']==OLD_D and profile.get('status')=='PREPARED_DIAGNOSTIC'and profile.get('life_id')==MAIN,'Only actual not-yet-selected prepared movement is allowed before COMMITTED')
 original=P/'estados/REAL2/IMPORTACION_DIAGNOSTICA.json';imp=read(original);need(imp['life']==MAIN and imp['new_native_ticks']==0 and imp['comparison']['physical_equal']and imp['comparison']['causal_prefix_equal'],'Original full neutral import proof must survive movement');need(card['physical']['tick']>=imp['result']['physical']['tick'],'No main clock rewind')
 return cardfile,original,{'same_life_not_second_world':True,'movement_proof':str(preparedfile),'movement_proof_sha256':sha(preparedfile),'movement_map_sha256':sha(mappingfile),'current_selection':active['life_id'],'original_import_proof':str(original),'original_import_proof_sha256':sha(original)}
def ledger():
 worlds={};charges={};unresolved=[];cards=[(f,f.parents[4]/'IMPORTACION_DIAGNOSTICA.json',None)for f in sorted((P/'estados').glob('*/sistema/estado/vidas/*/VIDA.json'))];moved=moved_main()
 if moved:cards.append(moved)
 for cardfile,initial,movement in cards:
  card=read(cardfile);life=card['life_id'];need(initial.exists(),'Partial/unproven world import: '+str(cardfile));imported=read(initial);need(imported['life']==life,'Original import identity mismatch');start=imported['result']['physical']['tick'];now=card['physical']['tick'];need(life not in worlds and now>=start,'Duplicate same-ID identity or reversed Native tick');worlds[life]={'system':str(cardfile.parents[3]),'import_tick':start,'current_tick':now,'observed_native_ticks':now-start,'same_identity_product_movement':movement};charges[life]=now-start
 for proof in sorted((P/'control').glob('PI10_*_OWNER*.json')):
  v=read(proof)
  if v.get('schema')!='DEE.PI10.actual.finite_owner_plan.R01':continue
  life=v['life_id'];need(life in worlds,'Owner proof refers to missing world; no refund after move')
  if not(v.get('closed')and v.get('error')is None):charges[life]=max(charges[life],v['initial_tick']-worlds[life]['import_tick']+v['finite_bound']);unresolved.append({'proof':str(proof),'conservatively_charged_bound':v['finite_bound']})
 for intent in sorted((P/'control').glob('PI10_*_OWNER*.INTENT.json')):
  v=read(intent)
  if Path(v['proof']).exists():continue
  life=v['life_id'];need(life in worlds,'Owner intent refers to missing world');charges[life]=max(charges[life],v['initial_tick']-worlds[life]['import_tick']+v['finite_bound']);unresolved.append({'intent':str(intent),'conservatively_charged_bound':v['finite_bound']})
 rpf=P/'estados/RPF2';rpfcontext=rpf/'CONTEXTO_EJECUCION.json'
 if rpfcontext.exists():
  context=read(rpfcontext);life=context['life'];result=rpf/'RESULTADO_REPRODUCCION.json';complete=result.exists()and read(result).get('status')=='COMPLETED'and read(result).get('owner_closed_coherently')is True
  if life in worlds and not complete:
   reserve=read(P/'control/RESERVA_ROOT_RPF12_PI10_R02.json');need(reserve['life_id']==life and reserve['maximum_new_Native_ticks']==24192,'Exact cold-replay incomplete phase reservation');charges[life]=max(charges[life],24192);unresolved.append({'RP_replay':str(rpf),'conservatively_charged_bound':24192})
 return {'schema':'DEE.PI10.readonly.aggregate_native_ledger.R02','observed_saved_ticks':sum(v['observed_native_ticks']for v in worlds.values()),'charged_ticks':sum(charges.values()),'world_count':len(worlds),'worlds':worlds,'unresolved_reserved_phases':unresolved,'Native_executed':False,'same_ID_move_counts_once_without_refund':True,'includes_product_current_main_native_ticks':bool(moved)}
if __name__=='__main__':print(json.dumps(ledger(),ensure_ascii=False,indent=2))
