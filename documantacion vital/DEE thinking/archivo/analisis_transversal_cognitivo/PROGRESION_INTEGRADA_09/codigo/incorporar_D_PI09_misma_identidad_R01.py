"""Conditional Root-only D same-ID adoption using the reviewed move engine.

The original C1 adoption source remains literal. This private administrative
namespace changes only target/profile/evidence contracts; movement, all-three
trees/checkpoints/history verification, Store promotion and six-reference CAS
use the same implementation. Default does not read state or import Native.
"""
from pathlib import Path
import ast,datetime,hashlib,importlib.util,json,re,types
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';CS=P/'estados/DISCOVERY/sistema'
BASE=H/'incorporar_PI09_misma_identidad_R03.py';BASE_SHA='a4011725610dac74c2fe3322bc83ebdc3b55d2b08ca24a7e3092a4e1ea4b4ea3'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01';PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01';ANCESTOR='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01';_BASE=None;_DECISION=None
GATES=('functional_gain','conservation','causal_controls','source_reopening','new_function_at_final_cut','decisive_recipe_replay')
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def permission():
 spec=importlib.util.spec_from_file_location('PI09_D_exact_permission_adoption',H/'pi09_permiso_operativo_D_R01.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def parent(selected=True):
 need(_DECISION is not None,'Actual Root decision must bind the protected parent before any state phase');d=_DECISION;card=read(S/'estado/vidas'/PARENT/'VIDA.json')
 need(card['life_id']==PARENT and card['physical']['N']==67 and card['physical']['tick']==903603 and card['snapshot_sha256']==d['protected_parent_snapshot_sha256']and sha(S/card['snapshot'])==card['snapshot_sha256'],'Protected C1 Native903603 changed; never replace a later continuation')
 if selected:need(read(S/'estado/ACTIVO.json')['life_id']==PARENT,'Another current principal selected')
 old=read(S/'estado/vidas'/ANCESTOR/'VIDA.json');need(old['physical']['tick']==861426 and old['snapshot_sha256']=='2eeef08e3bebac4e218178ed379fd99aa5fdeb03650c0454ad55c6534824c133'and sha(S/old['snapshot'])==old['snapshot_sha256'],'Original A principal is protected literally')
 return card
def evidence(ref):
 b=base();file=b.bounded(ref['path'],P);need(sha(file)==ref['sha256'],'Actual D evidence hash differs');return read(file)
def closed_phase(ref,life):
 p=evidence(ref);need(p.get('closed')is True and p.get('error')is None and p.get('life_id')==life and p.get('protected_before')==p.get('protected_after'),'Actual closed protected D phase required')
 return p
def validate_D_evidence(d):
 b=base();seal=read(H/'SELLO_PI09_D_R02.json');p=permission();need(sha(H/'PROTOCOLO_PI09_D_R02.json')==p.PINS['PROTOCOLO_PI09_D_R02.json']and sha(H/'pi09_entorno_persistente_D_R02.py')==p.PINS['pi09_entorno_persistente_D_R02.py'],'Frozen D2 source changed')
 milestone=evidence(d['first_milestone_adoption']);need(milestone.get('schema')=='DEE.PI09.same_identity.adopted_product.R01'and milestone.get('phase')=='COMMITTED'and milestone.get('life_id')==PARENT and milestone.get('commit_witness')and milestone.get('source_history_not_rewritten')is True and d['first_milestone_adoption']['sha256']==seal['first_milestone_adoption_sha256'],'Actual C1 COMMITTED ancestry required')
 roles=d['D_actual_closed_arms'];need(set(roles)=={'real','none','yoked'},'All three D material controls required; optional WSLS is separate')
 for role,ref in roles.items():
  proof=closed_phase(ref,seal['arms'][role]);need(proof.get('schema')=='DEE.PI09.D.actual.finite_owner_phase.R03','Exact actual D supervisor schema required')
  ops=[r for r in proof.get('records',[])if r.get('literal',{}).get('modo')=='eci01-pi09-d-episodio'];need(len(ops)==6,'Each evaluation is exactly six actual D opportunities')
  for index,op in enumerate(ops):
   row=op['rows'][0];need(row.get('ordinal')==index and row.get('D_feedback_arm')==role and row.get('Native_inputs',{}).get('all_terminal')is True,'Actual D ordinal/role/receipts differ')
  if role=='real':need(proof.get('arm')=='real','Only acquired real source may be adopted')
 conservation=evidence(d['D_conservation_proof']);need(conservation.get('closed')is True and conservation.get('error')is None and conservation.get('life_id')==LIFE,'Actual same-Discovery conservation required')
 results=[r for r in conservation.get('records',[])if r.get('correct')is not None];need(len(results)>=12 and all(r.get('correct')is True for r in results[:12]),'All twelve declared legacy results required; do not weaken a failed numeric gate')
 reopened=closed_phase(d['D_source_reopening_function_proof'],LIFE);ops=[r for r in reopened.get('records',[])if r.get('literal',{}).get('modo')=='eci01-pi09-d-episodio'];need(ops and ops[-1]['rows'][0].get('actual_failed')is False and reopened.get('final_tick')==d['source_tick'],'Actual last useful D function after reopening at the final source cut required')
 labels={r.get('label')for r in reopened.get('records',[])};need({'STATE_BEFORE','STATE_AFTER'}<=labels,'Actual reopened owner STATE/use/STATE evidence required')
 last=ops[-1]['rows'][0];need(last.get('ordinal')==d['source_D_ordinal']-1 and 6<=d['source_D_ordinal']<12,'Actual unexhausted D stock at the source cut required')
 rp=evidence(d['D_reproduction_result']);comparison=evidence(d['D_reproduction_comparison'])
 if rp.get('schema')=='DEE.PI09.D.actual.finite_owner_phase.R03':
  replayops=[r for r in rp.get('records',[])if r.get('literal',{}).get('modo')=='eci01-pi09-d-episodio'];need(rp.get('closed')is True and rp.get('error')is None and rp.get('life_id')in seal['native_reproduction_ids']and len(replayops)==6 and all(r['rows'][0].get('ordinal')==i and r['rows'][0].get('D_feedback_arm')=='real'and r['rows'][0].get('Native_inputs',{}).get('all_terminal')is True for i,r in enumerate(replayops))and d.get('D_new_frontdoor_CLI_replay_verified')is False,'Actual DREPRO6 sealed procedure and honest separate CLI scope required')
 else:
  family=isinstance(rp.get('life'),str)and re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DRF_[A-Z0-9]{1,10}',rp['life'])is not None
  need(rp.get('status')=='COMPLETED'and rp.get('owner_closed_coherently')is True and rp.get('criteria_met')is True and(rp.get('life')in seal['native_reproduction_ids']or family)and d.get('D_new_frontdoor_CLI_replay_verified')is True,'Actual completed D frontdoor reproduction required for a CLI claim')
  if family:need(rp.get('recipe')=='pi09_d6_familia_desde_DISCOVERY_T907543_R01'and comparison.get('family_binding',{}).get('three_administrative_bindings_verified')is True,'Actual generic D family binding/comparison proof required')
 need(comparison.get('physical_equal')is True and comparison.get('causal_prefix_equal')is True and comparison.get('unexpected_metadata_changes')==[],'Actual narrow full D replay equality required')
 need(d['new_contract']['public_arithmetic_policy']=='legacy_partial','P0 arithmetic gain was zero; no guard promotion')
 return True
def decision(file):
 global _DECISION
 d=read(file);need(d.get('approved_for_adoption')is True and d.get('life_id')==LIFE and d.get('profile')=='fisica_directa'and type(d.get('source_tick'))is int and d['source_tick']>907543,'Only explicit Root-approved actual acquired Discovery may move')
 need(isinstance(d.get('protected_parent_snapshot_sha256'),str)and len(d['protected_parent_snapshot_sha256'])==64,'Current quiet Native parent snapshot must be bound after its selected zero reopening')
 need(set(d.get('gates',{}))==set(GATES),'All six explicit D gates required')
 for key,gate in d['gates'].items():need(gate.get('satisfied')is True and gate.get('criterion')and gate.get('result')and gate.get('evidence'),'Missing actual D gate '+key)
 for ref in d.get('evidence',[])+[ref for gate in d['gates'].values()for ref in gate['evidence']]:evidence(ref)
 for key in('decision_id','scope','gains','losses','uncertainties','assistance','regression_coverage','catalog_entry','approved_code_files','selectors_cas','new_contract','source_snapshot_sha256','process_proof','source_D_ordinal'):need(key in d,'Missing explicit reasoned D decision field '+key)
 need(set(d['selectors_cas'])==set(base().SELECTORS),'All six current product references require CAS')
 p=permission();contract=d['new_contract'];need(contract.get('schema')=='DEE.PI09.D.exact_operational_permission.v2'and contract.get('status')=='PREPARED_DIAGNOSTIC'and contract.get('life_id')==LIFE and contract.get('profile')=='fisica_directa'and contract.get('protocol_sha256')==p.PINS['PROTOCOLO_PI09_D_R02.json']and contract.get('allowed_modes')==[p.D_EP,p.D_STATE]and contract.get('frozen_files_sha256')==p.PINS and contract.get('all_adoption_gates_met')is True and contract.get('adoption_decision_sha256')is None,'Exact separately PREPARED D profile required before movement')
 need(contract.get('all_outer_FI_requests')is True and contract.get('public_FI_domain')==[0,20]and contract.get('public_FI_backend')=='explicit_FI8_same_frozen_body'and contract.get('internal_C2C_FI_redirected')is False and contract.get('historical_R02_material_disabled')is True and contract.get('historical_PI07_material_disabled')is True and contract.get('C2C_protocol_sha256')==p.C2C_PROTOCOL,'Fixed D public/ancestral/C2C routes required')
 _DECISION=d;validate_D_evidence(d);return d
def native_equal(a,b):
 need(a['physical']==b['physical']and a['causal_prefix_sha256']==b['causal_prefix_sha256'],'Whole physical/interface/agenda/receipt Native prefix changed')
 changes=[]
 for key in set(a['metadata'])|set(b['metadata']):
  if a['metadata'].get(key)==b['metadata'].get(key):continue
  changes.append(key)
  if key=='DEE.Cognitive.System.1.1.life.v1'or key=='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'or key.startswith('DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1.queue.'):continue
  if key=='DEE.Cognitive.PI04.C2C.coordination.R01':
   old=json.loads(a['metadata'][key]);new=json.loads(b['metadata'][key])
   if old.get('life_id')in(ANCESTOR,PARENT,LIFE)and new.get('life_id')==LIFE and {k:v for k,v in old.items()if k!='life_id'}=={k:v for k,v in new.items()if k!='life_id'}:continue
  raise ValueError('Nonadministrative D metadata changed '+key)
 return {'complete_Native_prefix_equal':True,'physical_equal':True,'changed_metadata_keys_all_listed':sorted(changes),'only_C2C_current_identity_leaf_allowed':True,'new_ticks':0}
def code(d):
 b=base();rows=[];seen=set()
 for name,digest in d['new_contract']['frozen_files_sha256'].items():need(sha(CS/'capacidades'/name)==digest,'Frozen D scientific source changed '+name)
 for row in d['approved_code_files']:
  rel=b.relative(row['file']);name=rel.as_posix();source=Path(row['source']).resolve(strict=True);target=b.bounded(S/rel,S,False);b.regular(source)
  need(name not in seen and(source.is_relative_to(CS.resolve())or source.is_relative_to(H.resolve()))and source.suffix in('.py','.json')and(rel.parts[0]in('app','capacidades','contratos')or name=='gestionar.py'),'Only explicit code/config delta; no engine/state/snapshot')
  if rel.parts[0]=='contratos':need(name=='contratos/PI09_D_USO_OPERATIVO_R02.json'and read(source)==d['new_contract'],'Only exact prepared D contract')
  need(sha(source)==row['sha256']and(sha(target)if target.exists()else None)==row['before_sha256'],'D code CAS differs '+name);ast.parse(source.read_bytes())if source.suffix=='.py'else read(source)
  rows.append({**row,'source':str(source),'target':str(target),'bytes':source.stat().st_size});seen.add(name)
 source_manifest=read(CS.parent/'SISTEMA_CODIGO_PI09.json');available=seen|{r['file']for r in source_manifest['files']if(S/r['file']).is_file()and sha(S/r['file'])==r['sha256']}
 required={'app/mundo_genesis_apd05.py','app/cola_local.py','app/pi09_identidad_c2c_D_R01.py','app/usar_dee.py','capacidades/pi04_dispatcher.py','capacidades/pi09_permiso_operativo_D_R01.py','capacidades/pi09_transporte_D_R02.py','capacidades/PI09_TRANSPORTE_D_R02.json','capacidades/PI09_TRANSPORTE_D_ANCESTRO_R02.json','capacidades/pi09_dispatcher_D_R02.py','capacidades/PI09_PLUGINS_D_R02.json','capacidades/pi09_entorno_persistente_D_R02.py','capacidades/pi09_antecedente_R02_readonly_D_R01.py','capacidades/pi09_FI8_D_alias_R01.py','capacidades/pi09_literal_producto_D_R01.py','contratos/PI09_D_USO_OPERATIVO_R02.json'}
 need(required<=available,'Complete D selected/public/ancestor code closure required')
 for row in source_manifest['files']:
  if row['file']not in seen:need((S/row['file']).is_file()and sha(S/row['file'])==row['sha256'],'Uncovered complete source dependency '+row['file'])
 return rows
def base():
 global _BASE
 if _BASE is not None:return _BASE
 need(sha(BASE)==BASE_SHA,'Literal reviewed C1 move engine changed');text=BASE.read_text('utf-8-sig')
 replacements={'PI09_CONSULTA_OPERATIVA_R01.json':'PI09_D_USO_OPERATIVO_R02.json','app.pi09_identidad_c2c_R01':'app.pi09_identidad_c2c_D_R01','MAPA_TRASLADO_PRODUCTO_PI09.json':'MAPA_TRASLADO_D_PRODUCTO_PI09.json','DECISION_PROMOCION_PRODUCTO_PI09.json':'DECISION_PROMOCION_D_PRODUCTO_PI09.json','PERFIL_PREPARADO_ANTES_COMMITTED_PI09.json':'PERFIL_D_PREPARADO_ANTES_COMMITTED_PI09.json','DEE.PI09.same_identity.prepared_product.R01':'DEE.PI09.D.same_identity.prepared_product.R01','DEE.PI09.same_identity.adopted_product.R01':'DEE.PI09.D.same_identity.adopted_product.R01','PI08_A_':'PI09_C1_','prior_selection_PI09':'prior_selection_PI09_D','prior_cut_PI09':'prior_cut_PI09_D','PI09_prior_selected_seed':'PI09_D_prior_selected_seed','PI09_prior_current_principal':'PI09_D_prior_current_principal'}
 replacements["d['PI09_actual_closed_arms']['native_real']"]="d['D_source_reopening_function_proof']"
 replacements['source_PI09_NATIVE_closed12']='source_PI09_D_last_actual_function'
 replacements['Actual Native12 source before same-ID relocation. Selected public use remains a separate operational test.']='Actual useful reopened D source before same-ID relocation. Selected material use remains a separate operational test.'
 for old,new in replacements.items():text=text.replace(old,new)
 namespace=types.ModuleType('PI09_D_private_reviewed_move_engine');namespace.__file__=str(BASE);exec(compile(text,str(BASE)+':D_admin_identity_and_paths_only','exec'),namespace.__dict__)
 namespace.CS=CS;namespace.LIFE=LIFE;namespace.PARENT=PARENT;namespace.PARENT_T=903603;namespace.PARENT_SHA=None
 namespace.PREPARED=P/'control/PREPARACION_TRASLADO_D_PRODUCTO_PI09.json';namespace.ADOPTED=P/'control/ADOPCION_D_PRODUCTO_PI09.json';namespace.INTENT=P/'control/TRASLADO_D_PRODUCTO_PI09_EN_CURSO.json';namespace.BACKUP=P/'control/RESPALDO_INCORPORACION_D_PI09'
 original_inventory=namespace.inventory
 def inventory(d):
  card,roots,snapshots,items=original_inventory(d);imported=read(CS/'estado/servicios_persistentes'/LIFE/'IMPORTACION.json');pair=P/'pares/NATIVE_POST12_T903603';mf=read(pair/'EXPORTACION_SERVICIO.json')
  need(sha(pair/'EXPORTACION_SERVICIO.json')=='0cce6bcfe366551b52b0ca25c5959bd6e07ed4493221ec26b76af962c13b6553'and card.get('parent',{}).get('source_tick')==903603 and card['parent'].get('encoded_sha256')==mf['snapshot_sha256']and imported.get('source_life_id')==PARENT and imported.get('new_life_id')==LIFE,'Discovery must remain the literal imported descendant of quiet Native903603; no genealogy rewriting')
  return card,roots,snapshots,items
 namespace.parent=parent;namespace.decision=decision;namespace.validate_PI09_evidence=validate_D_evidence;namespace.code=code;namespace.native_equal=native_equal;namespace.inventory=inventory;_BASE=namespace;return namespace
if __name__=='__main__':base().main()
