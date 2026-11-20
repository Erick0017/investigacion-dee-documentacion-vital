"""STAGED R03 Root-only whole-REAL2 adoption, no execution on import.

Uses the exact reviewed PI09 movement engine under a PI10 administrative
namespace. Scientific gates, source/current identities and permission schema
are bound before any Store call. Default is read-only. No fixed final tick,
successful learning, code deployment or promotion is inferred by this file.
R02 stays preserved. This revision implements the PRE-replay R03 comparator
criterion: exact physical state and full structured Native correspondence,
with only explicitly listed current transport labels normalized. It never
calls two differing raw causal hashes binary equality.
"""
from pathlib import Path
import ast,hashlib,json,re,types
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';CS=P/'estados/REAL2/sistema'
BASE=H/'MOTOR_TRASLADO_PI09_R03_LITERAL.py';BASE_SHA='a4011725610dac74c2fe3322bc83ebdc3b55d2b08ca24a7e3092a4e1ea4b4ea3'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01';PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01';PARENT_T=922371;PARENT_SHA='72743ad2fc708e41c2529af8f7192fe1087184562e4cd094f469384faedcd331'
SCHEMA='DEE.PI10.exact_operational_permission.v2';CONTRACT='PI10_USO_OPERATIVO_R01.json'
KEY='DEE.Cognitive.PI10.adaptive_query.two_native_traces.R02';OLD_KEY='DEE.Cognitive.PI10.adaptive_query.two_native_traces.R01';C2C='DEE.Cognitive.PI04.C2C.coordination.R01'
GATES=('functional_gain','conservation','causal_controls','source_reopening','new_function_at_final_cut','decisive_recipe_replay')
CORE_PINS={'pi09_entorno_persistente_D_R02.py':'c9938b50fbdf68d94954eaf341abae025faa307e4c8d24d23862c7b78bf085f8','pi09_consulta_selectiva_R02.py':'3b81573f4dc0d9401db2210f3b23694e1f1f4a4d820d7654bcbd1e1b42b2dfbf'}
_BASE=None
COMPARATOR=H/'comparar_reproduccion_PI10_R03.py'
COMPARATOR_SHA='0a46aac30d8ff8088887450133dc5894447ee5c4292b585e0195dd466210dd1e'
BINDING_FILES={'capacidades/PI10_TRANSPORTE_ANCESTRAL_R01.json','capacidades/PI10_EXPERIMENTO_R02.json','capacidades/PI10_PLUGINS_R01.json'}
def need(ok,why):
 if not ok:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def evidence(ref):
 p=base().bounded(ref['path'],P);need(sha(p)==ref['sha256'],'Actual evidence hash differs: '+str(p));v=read(p)
 for pointer,expected in ref.get('checks',{}).items():
  x=v
  for part in pointer.strip('/').split('/')if pointer else []:x=x[int(part)]if isinstance(x,list)else x[part.replace('~1','/').replace('~0','~')]
  need(x==expected,'Actual evidence check differs: '+pointer)
 return v
def parent(selected=True):
 card=read(S/'estado/vidas'/PARENT/'VIDA.json')
 need(card['life_id']==PARENT and card['physical']['N']==67 and card['physical']['tick']==PARENT_T and card['snapshot_sha256']==PARENT_SHA and sha(S/card['snapshot'])==PARENT_SHA,'Protected D parent advanced or changed; never replace a newer continuation')
 if selected:need(read(S/'estado/ACTIVO.json')['life_id']==PARENT,'Another principal is selected')
 return card
def closed(ref,life=LIFE):
 v=evidence(ref);need(v.get('closed')is True and v.get('error')is None and v.get('life_id')==life,'Actual closed exact-life phase required');return v
def native_equal(a,b):
 need(a['physical']==b['physical']and a['causal_prefix_sha256']==b['causal_prefix_sha256'],'Complete physical/interface/agenda/receipt Native prefix changed')
 changed=[]
 for key in set(a['metadata'])|set(b['metadata']):
  if a['metadata'].get(key)==b['metadata'].get(key):continue
  changed.append(key)
  if key=='DEE.Cognitive.System.1.1.life.v1'or key=='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'or key.startswith('DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1.queue.'):continue
  if key==C2C:
   old=read_metadata(a['metadata'][key]);new=read_metadata(b['metadata'][key])
   if old.get('life_id')in(PARENT,LIFE)and new.get('life_id')==LIFE and {k:v for k,v in old.items()if k!='life_id'}=={k:v for k,v in new.items()if k!='life_id'}:continue
  raise ValueError('Nonadministrative moved metadata changed: '+key)
 return {'complete_Native_prefix_equal':True,'physical_equal':True,'changed_metadata_keys_all_listed':sorted(changed),'only_C2C_current_identity_leaf_allowed':True,'new_ticks':0}
def read_metadata(value):return json.loads(value)

def replay_comparison_admissible(c):
 need(sha(COMPARATOR)==COMPARATOR_SHA,'Prospectively fixed complete R03 comparator changed')
 need(c.get('schema')=='DEE.PI10.actual_real12_RPF12.full_passive_comparison.R03'and c.get('physical_equal')is True and c.get('overall')is True and c.get('unexpected_metadata_changes')==[],'Actual exact-physical, strict-metadata closed R03 replay comparison required')
 s=c.get('Native_structured_correspondence',{})
 need(s.get('normalized_equal')is True and s.get('unexplained_different_paths')==[] and s.get('all_other_fields_and_fixed_bytes_preserved')is True and s.get('entire_original_prefix_hashes_preserved')is True,'Complete structured Native correspondence without unexplained differences required')
 need(s.get('components_source')==s.get('components_replay')and isinstance(s.get('components_source'),dict),'Interface/agenda/receipt counts and phase must also match exactly')
 source=c.get('source_causal_prefix_sha256');target=c.get('replay_causal_prefix_sha256')
 need(all(isinstance(x,str)and re.fullmatch('[0-9a-f]{64}',x)for x in(source,target)),'Both original exact binary causal hashes required')
 binary=source==target
 need(c.get('binary_causal_prefix_equal')is binary and c.get('causal_prefix_equal')is binary,'Never relabel normalized correspondence as binary causal equality')
 if not binary:
  a=s.get('exact_current_ID_label_paths_source');b=s.get('exact_current_ID_label_paths_replay')
  need(isinstance(a,list)and bool(a)and a==b and len(a)==len(set(a)),'Only identical nonempty lists of exact current-ID transport-label paths may explain differing raw hashes')
  allowed=re.compile(r'^/(?:interfaces/\d+/name|pending/\d+/tags/\d+|receipts/\d+/(?:tags/\d+|detail))$')
  need(all(isinstance(p,str)and allowed.fullmatch(p)for p in a),'No normalization of phase, payload, clock, RAW, signature or arbitrary scientific field')
 r=c.get('closed_replay_verified',{})
 need(r.get('status')=='COMPLETED'and r.get('owner_closed_coherently')is True and r.get('SQLite_integrity')=='ok'and r.get('unresolved_requests')==0 and r.get('no_nonempty_WAL_or_journal')is True and r.get('result_criteria_met')is True,'Actual coherent closed replay and original operational/witness criteria required')
 b=c.get('three_administrative_bindings_verified',{})
 need(b.get('all_other_capsule_files_literal')is True and b.get('Native_or_learned_state_files_changed')is False and isinstance(b.get('files'),list)and len(b['files'])==3 and set(b['files'])==BINDING_FILES and re.fullmatch('[0-9a-f]{64}',b.get('proof_sha256',''))is not None,'Exact pre-import three-file administrative binding proof required')
 return {'binary_causal_prefix_equal':binary,'full_structured_Native_correspondence':True,'only_listed_exact_current_transport_labels_normalized':not binary,'all_other_bytes_preserved':True}
def validate_science(d):
 evaluation=closed(d['PI10_actual_real12_proof']);ops=[r for r in evaluation.get('records',[])if r.get('literal',{}).get('modo')=='eci01-pi10-episodio']
 need(len(ops)==12,'Actual complete Real12 owner proof required, not a simulation or a prospective plan')
 for ordinal,op in enumerate(ops):
  rows=op.get('rows',[]);need(len(rows)==1,'One actual result per opportunity');r=rows[0]
  need(r.get('version')=='DEE.PI10.adaptive_query.two_native_traces.R02'and r['ordinal']==ordinal and r['life_id']==LIFE and r.get('feedback_arm')=='real'and r.get('trace_control')=='none'and r.get('operator_calibration')is False and r.get('Native_inputs',{}).get('all_terminal')is True,'Only unforced REAL2 exact history is eligible')
 closed(d['PI10_conservation_proof'])
 used=closed(d['PI10_source_reopening_function_proof']);last=[r for r in used.get('records',[])if r.get('literal',{}).get('modo')=='eci01-pi10-episodio']
 need(last and last[-1]['rows'][0].get('actual_failed')is False and last[-1]['rows'][0]['ordinal']>=12 and used['final_tick']==d['source_tick'],'Actual useful new function after reopening at exact final source cut required')
 zero=closed(d['PI10_source_zero_reopening_proof']);before=zero['initial_saved_Native'];after=zero['final_saved_Native']
 need(zero.get('new_Native_ticks')==0 and before['physical']==after['physical']and before['causal_prefix_sha256']==after['causal_prefix_sha256']and after['encoded_sha256']==d['source_snapshot_sha256'],'Actual source0 must preserve full Native prefix and bind exact final checkpoint')
 replay=evidence(d['PI10_reproduction_result']);comparison=evidence(d['PI10_reproduction_comparison'])
 need(replay.get('status')=='COMPLETED'and replay.get('owner_closed_coherently')is True and replay.get('criteria_met')is True and replay.get('life')!=LIFE and replay.get('recipe')==d['PI10_reproduction_recipe_id'],'Actual fresh diagnostic cold-acquisition replay required')
 replay_comparison_admissible(comparison)
 return True
def decision(file):
 d=read(file)
 need(d.get('schema')=='DEE.PI10.reasoned_adoption_decision.R02'and d.get('approved_for_adoption')is True and d.get('life_id')==LIFE and d.get('profile')=='fisica_directa','Actual explicit Root R02 decision required; no automatic promotion')
 required={'source_tick','source_snapshot_sha256','source_PI10_ordinal','source_code_manifest','neutral_P02_manifest','measured_adoption_metrics','adoption_metrics_proof','gates','approved_code_files','selectors_cas','catalog_entry','new_contract','scope','gains','losses','uncertainties','assistance','evidence','regression_coverage','process_proof','decision_id','PI10_actual_real12_proof','PI10_conservation_proof','PI10_source_reopening_function_proof','PI10_source_zero_reopening_proof','PI10_reproduction_result','PI10_reproduction_comparison','PI10_reproduction_recipe_id'}
 need(required<=set(d)and type(d['source_tick'])is int and isinstance(d['source_snapshot_sha256'],str)and len(d['source_snapshot_sha256'])==64,'Actual reached source fields required; no fixed future tick')
 need(set(d['gates'])==set(GATES)and set(d['selectors_cas'])==set(base().SELECTORS),'All actual gates and six selector CAS references required')
 for name,gate in d['gates'].items():
  need(gate.get('satisfied')is True and gate.get('criterion')and gate.get('result')and gate.get('evidence'),'Missing real empirical gate '+name)
  for ref in gate['evidence']:evidence(ref)
 for ref in d['evidence']:evidence(ref)
 c=d['new_contract'];need(c.get('schema')==SCHEMA and c.get('status')=='PREPARED_DIAGNOSTIC'and c.get('life_id')==LIFE and c.get('N')==67 and c.get('profile')=='fisica_directa'and c.get('all_adoption_gates_met')is True and c.get('adoption_decision_sha256')is None,'Exact PI10 separately PREPARED contract before movement/Store')
 neutral=evidence(d['neutral_P02_manifest']);need(neutral['physical']['N']==67 and d['source_tick']>neutral['physical']['tick'],'Actual neutral P02 before acquired future required')
 need(c.get('source_P02_manifest_sha256')==d['neutral_P02_manifest']['sha256']and c.get('protocol_sha256')==sha(CS/'capacidades/PROTOCOLO_PI10_R02.json'),'Exact neutral P02 and evaluated R02 protocol bindings required')
 need(c.get('allowed_modes')==['eci01-pi10-episodio','eci01-pi10-estado']and c.get('public_FI_backend')=='inherited_FI8_same_frozen_body'and c.get('public_FI_domain')==[0,20]and c.get('internal_FI_redirected')is False and c.get('historical_material_disabled')is True and c.get('public_arithmetic_policy')=='legacy_partial','Only fixed PI10/current FI8 public routes; no changed arithmetic or stock reset')
 need(c.get('C2C_protocol_sha256')=='0cf6bf8508e071a1c8cf1448023a096bc43336d66b8a1deb98f488b29b4205fd','Literal C2C32 only')
 metrics=evidence(d['adoption_metrics_proof']).get('measured_adoption_metrics');need(metrics==d['measured_adoption_metrics'],'Actual summary metrics must bind the reasoned decision exactly')
 ints=('reserved_attributed_gain','total_physical_gain','core_requested','core_responded','core_correct','numerical_requested','numerical_formed','numerical_correct','numerical_incorrect')
 need(all(type(metrics.get(k))is int for k in ints),'Exact observed integer denominators required')
 need(metrics['reserved_attributed_gain']>=2 and metrics['total_physical_gain']>=1 and metrics.get('useful_revision_bypass')is True and metrics.get('useful_return_to_query')is True,'Frozen bounded useful gain and both contextual revisions required')
 need(metrics['core_requested']==metrics['core_responded']==metrics['core_correct']==10 and metrics['numerical_requested']==metrics['numerical_formed']==2 and metrics['numerical_correct']+metrics['numerical_incorrect']==2 and metrics.get('operational_uncertainty')is False,'Ten critical functions, both actual formed numerical responses and no operational uncertainty required')
 need(metrics['numerical_correct']==2 or(metrics['reserved_attributed_gain']>=3 and metrics['numerical_correct']==1 and metrics['numerical_incorrect']==1 and metrics.get('additional_actual_arithmetic_correct')is True),'One formed numerical loss only under prospectively frozen stronger gain and actual additional arithmetic success')
 parent();validate_science(d);return d
def inventory(d):
 b=base();card,roots,snapshots,items=b.PI10_original_inventory(d);view=b.parser().snapshot_view(CS/card['snapshot']);entries=view['metadata'];m=json.loads(entries[KEY])
 need(m.get('ready')and m.get('admitted')and not m.get('pending')and not m.get('uncertain')and m.get('ordinal')==d['source_PI10_ordinal']and 12<=m['ordinal']<18 and len(m['rows'])==m['ordinal'],'Actual closed unexhausted acquired REAL2 PI10 history, no reset')
 need(m.get('admission_control')=={'role':'evaluation','arm':'real','trace_control':'none','force_query':None},'No calibration/reference/cut/sham candidate may be adopted')
 source=evidence(d['neutral_P02_manifest']);pair=Path(d['neutral_P02_manifest']['path']).parent;snap=pair/source['native_snapshot'];need(sha(snap)==source['snapshot_sha256'],'Actual neutral P02 snapshot bytes required')
 neutral=b.parser().snapshot_view(snap);old=json.loads(neutral['metadata'][OLD_KEY]);prepared=json.loads(neutral['metadata'][KEY])
 need(old.get('ready')and old.get('admitted')is False and old.get('ordinal')==0 and old.get('rows')==[]and not old.get('pending')and not old.get('uncertain'),'The frozen R01 parent must remain neutral, never its failed/acquired future')
 need(prepared.get('ready')and prepared.get('admitted')is False and prepared.get('ordinal')==0 and prepared.get('rows')==[]and not prepared.get('pending')and not prepared.get('uncertain'),'Actual reached R02 neutral prefix before any forced calibration/admission required')
 need(entries[OLD_KEY]==neutral['metadata'][OLD_KEY]and m.get('source_R01_P0_metadata_sha256')==hashlib.sha256(entries[OLD_KEY].encode('utf8')).hexdigest(),'Parent R01 preparation metadata must remain literal; no rewriting progress')
 need(card.get('parent',{}).get('source_tick')==source['physical']['tick']and card['parent'].get('encoded_sha256')==source['snapshot_sha256'],'Actual full P02 import genealogy must remain literal')
 return card,roots,snapshots,items
def code(d):
 b=base();rows=[];seen=set();contract=d['new_contract']
 for name,digest in CORE_PINS.items():need(sha(CS/'capacidades'/name)==digest and sha(S/'capacidades'/name)==digest,'Frozen ancestral scientific actor changed '+name)
 for name,digest in contract['frozen_files_sha256'].items():need(Path(name).name==name and sha(CS/'capacidades'/name)==digest,'Frozen PI10 source changed '+name)
 for item in d['approved_code_files']:
  rel=b.relative(item['file']);name=rel.as_posix();source=Path(item['source']).resolve(strict=True);target=b.bounded(S/rel,S,False);b.regular(source)
  need(name not in seen and(source.is_relative_to(CS.resolve())or source.is_relative_to(H.resolve()))and source.suffix in('.py','.json')and(rel.parts[0]in('app','capacidades','contratos')or name=='gestionar.py'),'Only explicit reviewed Cognitive code/config delta, no motor/state/manual')
  if rel.parts[0]=='contratos':need(name=='contratos/'+CONTRACT and read(source)==contract,'Only the exact PI10 PREPARED permission may deploy')
  need(sha(source)==item['sha256']and(sha(target)if target.exists()else None)==item.get('before_sha256'),'Source/target code CAS differs '+name)
  ast.parse(source.read_bytes())if source.suffix=='.py'else read(source);seen.add(name);rows.append({**item,'source':str(source),'target':str(target),'bytes':source.stat().st_size})
 manifest=evidence(d['source_code_manifest']);available=set(seen)
 for item in manifest['files']:
  name=item['file']
  if name in seen:continue
  target=S/b.relative(name);need(target.is_file()and sha(target)==item['sha256'],'Uncovered complete source dependency '+name);available.add(name)
 required={'app/mundo_genesis_apd05.py','app/cola_local.py','app/pi10_identidad_c2c_R02.py','capacidades/pi04_dispatcher.py','capacidades/pi10_consulta_adaptativa_R02.py','capacidades/pi10_dos_trazas_legales_R01.py','capacidades/pi10_entorno_dos_puertas_R01.py','capacidades/pi10_transporte_ancestral_R01.py','capacidades/pi10_dispatcher_R01.py','capacidades/pi10_permiso_operativo_R02.py','capacidades/PI10_PLUGINS_R01.json','capacidades/PI10_TRANSPORTE_ANCESTRAL_R01.json','capacidades/PI10_EXPERIMENTO_R02.json','capacidades/PROTOCOLO_PI10_R02.json','contratos/'+CONTRACT}
 need(required<=available,'Complete public PI10/ancestral/permission code closure required');return rows
def base():
 global _BASE
 if _BASE is not None:return _BASE
 need(sha(BASE)==BASE_SHA,'Reviewed literal movement engine changed');text=BASE.read_text('utf8')
 replacements={'PI09_CONSULTA_OPERATIVA_R01.json':CONTRACT,'app.pi09_identidad_c2c_R01':'app.pi10_identidad_c2c_R02','MAPA_TRASLADO_PRODUCTO_PI09.json':'MAPA_TRASLADO_PRODUCTO_PI10_R02.json','DECISION_PROMOCION_PRODUCTO_PI09.json':'DECISION_PROMOCION_PRODUCTO_PI10_R02.json','PERFIL_PREPARADO_ANTES_COMMITTED_PI09.json':'PERFIL_PREPARADO_ANTES_COMMITTED_PI10_R02.json','DEE.PI09.same_identity.prepared_product.R01':'DEE.PI10.same_identity.prepared_product.R02','DEE.PI09.same_identity.adopted_product.R01':'DEE.PI10.same_identity.adopted_product.R02','DEE.PI09.exact_native_consultation_permission.v1':SCHEMA,'PI08_A_':'PI09_D_','prior_selection_PI09':'prior_selection_PI10_R02','prior_cut_PI09':'prior_cut_PI10_R02','PI09_prior_selected_seed':'PI10_R02_prior_selected_seed','PI09_prior_current_principal':'PI10_R02_prior_current_principal'}
 for old,new in replacements.items():text=text.replace(old,new)
 text=text.replace("'source_PI09_NATIVE_closed12':d['PI09_actual_closed_arms']['native_real']","'source_PI10_actual_new_use':d['PI10_source_reopening_function_proof']")
 text=text.replace('Actual Native12 source before same-ID relocation. Selected public use remains a separate operational test.','Actual useful reopened REAL PI10 source before same-ID relocation. Selected public use remains a separate operational test.')
 namespace=types.ModuleType('PI10_private_reviewed_whole_REAL_movement');namespace.__file__=str(BASE);exec(compile(text,str(BASE)+':PI10_administrative_namespace_only','exec'),namespace.__dict__)
 namespace.P=P;namespace.C=C;namespace.S=S;namespace.CS=CS;namespace.H=H;namespace.CONTROL=P/'control';namespace.LIFE=LIFE;namespace.PARENT=PARENT;namespace.PARENT_T=PARENT_T;namespace.PARENT_SHA=PARENT_SHA
 namespace.PREPARED=P/'control/PREPARACION_TRASLADO_PRODUCTO_PI10_R02.json';namespace.ADOPTED=P/'control/ADOPCION_PRODUCTO_PI10_R02.json';namespace.INTENT=P/'control/TRASLADO_PRODUCTO_PI10_R02_EN_CURSO.json';namespace.BACKUP=P/'control/RESPALDO_INCORPORACION_PI10_R02'
 namespace.PI10_original_inventory=namespace.inventory;namespace.inventory=inventory;namespace.parent=parent;namespace.decision=decision;namespace.code=code;namespace.native_equal=native_equal;namespace.GATES=GATES
 original_adopt=namespace.adopt
 def guarded_adopt(d,file,reopening,process):
  profile=read(S/'contratos'/CONTRACT);need(profile==d['new_contract']and profile.get('schema')==SCHEMA and profile.get('status')=='PREPARED_DIAGNOSTIC','Exact PI10 schema/status before entering Store.promote')
  return original_adopt(d,file,reopening,process)
 namespace.adopt=guarded_adopt;_BASE=namespace;return namespace
if __name__=='__main__':base().main()
