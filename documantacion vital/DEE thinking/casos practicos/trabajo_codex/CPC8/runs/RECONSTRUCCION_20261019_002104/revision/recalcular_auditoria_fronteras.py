"""Static informational-boundary audit, not a simulator or security proof.

Only this report is written. Explicitly reviewed source closure is hashed;
operating sessions, historical evidence and primary results are not modified.
"""
import ast
from datetime import datetime,timezone
import hashlib,json,os,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILES=['ejecutar.py','app/experimento.py',
 'src/transferencia_magnitud/cts_integrado.py','src/transferencia_magnitud/transferencia.py',
 'src/comunicacion/contact_social_regulated.py','src/comunicacion/contact_social_e1.py',
 'src/integracion/initiative_use_e1.py','src/integracion/initiative_e1.py','src/integracion/contact_renewal_e1.py',
 'src/integracion/longitudinal_e1.py','src/integracion/complete_e1.py','src/integracion/quantity_core.py',
 'src/integracion/relational_guarded_v2.py','src/integracion/relational_social.py','src/integracion/relational_ensemble.py',
 'src/integracion/relational_pair_v2.py','src/integracion/relational_pair.py',
 'src/comunicacion/mode_communication.py','src/relaciones/mode_reference.py',
 'src/iniciativa_accion/solicitud.py','src/iniciativa_accion/return_use.py']
PACKAGE_INITS=['app/__init__.py','src/transferencia_magnitud/__init__.py','src/comunicacion/__init__.py',
 'src/integracion/__init__.py','src/relaciones/__init__.py','src/iniciativa_accion/__init__.py']
EVENTS=['configuraciones/demo_magnitud_social.jsonl','configuraciones/demo_magnitud_social_historia11.jsonl',
 'configuraciones/demo_magnitud_social_reserva17.jsonl','configuraciones/demo_magnitud_social_control.jsonl']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def text(p):return Path(p).read_text(encoding='utf-8-sig')

class Definitions(ast.NodeVisitor):
 def __init__(self):self.stack=[];self.symbols={};self.file_io=[];self.imports=[];self.calls_at_module=[]
 def visit_ClassDef(self,n):
  self.stack.append(n.name);self.symbols['.'.join(self.stack)]={'line':n.lineno,'end_line':n.end_lineno}
  self.generic_visit(n);self.stack.pop()
 def visit_FunctionDef(self,n):
  self.stack.append(n.name);self.symbols['.'.join(self.stack)]={'line':n.lineno,'end_line':n.end_lineno}
  self.generic_visit(n);self.stack.pop()
 visit_AsyncFunctionDef=visit_FunctionDef
 def visit_ImportFrom(self,n):self.imports.append({'line':n.lineno,'scope':'.'.join(self.stack)or'MODULE','module':'.'*n.level+(n.module or''),'names':[x.name for x in n.names]})
 def visit_Import(self,n):self.imports.append({'line':n.lineno,'scope':'.'.join(self.stack)or'MODULE','module':','.join(x.name for x in n.names),'names':[]})
 def visit_Call(self,n):
  name=ast.unparse(n.func)
  if any(name.endswith('.'+x)for x in('read_text','read_bytes','open','load_snapshot','load_world_snapshot','save_world_snapshot'))or name in('open','load_world_snapshot','save_world_snapshot'):
   self.file_io.append({'line':n.lineno,'scope':'.'.join(self.stack)or'MODULE','call':name})
  if not self.stack:self.calls_at_module.append({'line':n.lineno,'call':name})
  self.generic_visit(n)

def record(rel):
 p=ROOT/rel;tree=ast.parse(text(p),filename=rel);v=Definitions();v.visit(tree)
 return{'path':rel,'sha256':sha(p),'bytes':p.stat().st_size,'symbols':v.symbols,'imports':v.imports,'file_io_calls_including_unreachable_harness':v.file_io,'module_level_calls':v.calls_at_module}

def main():
 sources=[record(p)for p in FILES]+[record(p)for p in PACKAGE_INITS if(ROOT/p).is_file()];lookup={x['path']:x for x in sources}
 def ref(path,symbol):
  obj=lookup[path];return{'path':path,'sha256':obj['sha256'],'symbol':symbol,**obj['symbols'][symbol]}
 installed=Path(sys.prefix)/'Lib/site-packages/dee_thinking'
 native=installed/'_native.cp313-win_amd64.pyd';wheel=ROOT/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
 instrument={'python':sys.executable,'native':{'path':str(native),'sha256':sha(native),'expected_sha256':'17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'},
  'wheel':{'path':str(wheel.relative_to(ROOT)),'sha256':sha(wheel),'expected_sha256':'09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'},
  'kernel_reference_sha256':'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31',
  'kernel_scope':'Frozen instrument identity from the campaign contract; this static audit does not re-prove C++ internals.'}
 installed_sources=[]
 for name in('__init__.py','persistence.py','consolidated.py','cognition.py','dialogue.py','remote_reader.py','_remote_preparation.py'):
  p=installed/name;v=Definitions();v.visit(ast.parse(text(p),filename=str(p)))
  installed_sources.append({'path':str(p),'sha256':sha(p),'scope':'Import side-effect review; only exact_observation/exact_receipt and persistence helpers are operationally invoked by this app. Other session factories are imported definitions, not called.','module_level_calls':v.calls_at_module})
 ledger=[
 {'boundary':'ENTRY_AND_EVENT_GENERATOR','owner':'HUMAN/EXTERNAL_EXPERIMENT','reads':['Explicit JSONL or interactive event and scenario parameters; installed version/PYD identity'],'writes':['A sequence of requested actual events, neutral opportunities and human-requested probes'],'decision':'Select profile and operations from user commands. The event file contains actual order, quantities, routes and source experiences, not expected comparison outputs.','refs':[ref('ejecutar.py','identity'),ref('app/experimento.py','read_events'),ref('app/experimento.py','Experiment.execute')]},
 {'boundary':'FRESH_PREPARATION','owner':'DESIGNER','reads':['Declared preparation options and fixed recipe constants'],'writes':['Initial untrained body/supports, clocks, geometry, all candidate interfaces beforeT0'],'decision':'Reject overlap; no source snapshot is loaded or merged during create. Initial nonzero body state and guide phases are prepared resources, not absent knowledge or autonomous design.','refs':[ref('src/transferencia_magnitud/cts_integrado.py','prepare_magnitude_cts'),ref('src/integracion/complete_e1.py','prepare_complete'),ref('src/integracion/relational_pair.py','prepare')]},
 {'boundary':'MAGNITUDE_SOURCE_EXPERIENCE','owner':'ENVIRONMENT/SOURCE_A','reads':['Explicit current magnitude value and experimental paired/unpaired/omitted switch'],'writes':['Source cue5 and actual-value material at0; two formatter payloads0 at67/77'],'decision':'Neither formatter choice nor schedule depends on observed A/B output. This is a separate real source exposure, not an automatic read/copy of the main E1 quantity reference.','refs':[ref('src/transferencia_magnitud/transferencia.py','schedule_source'),ref('src/transferencia_magnitud/cts_integrado.py','MagnitudeCTSSession.curriculum')]},
 {'boundary':'NATIVE_MAGNITUDE_TRANSPORT','owner':'RUNTIME_V27','reads':['Current physical source carrier and fixed formatting opportunities'],'writes':['Carrier reaches recipient reference physically'],'decision':'No Python callback reads A and emits its value into B. Python routes only constant prepared ports; no world output is an input to schedule_source.','refs':[ref('src/transferencia_magnitud/transferencia.py','prepare_component'),ref('src/transferencia_magnitud/transferencia.py','RecipientQuantitySession.input')]},
 {'boundary':'RECIPIENT_OBJECTS_AND_COMPARISON','owner':'ENVIRONMENT plus PREPARED_NATIVE_INSTRUMENT','reads':['Three actual object magnitudes and acquired native recipient reference'],'writes':['Object cue/material and fixed reader requests; native comparator fields'],'decision':'Objects are not precompared labels. Gradient comparison, reader support, seven recipient supports/interceptors and alias prefix are prepared. General MORE rule/routing is not learned by this code. Published curriculum does not stimulate B.quantity.reference ports directly.','refs':[ref('src/integracion/quantity_core.py','QuantitySession.present_object'),ref('src/integracion/quantity_core.py','QuantitySession.reader_opportunity'),ref('src/integracion/quantity_core.py','prepare'),ref('src/transferencia_magnitud/transferencia.py','attach_recipient')]},
 {'boundary':'ORDER_CONTACT_TEACHING_AND_FORM_BANKS','owner':'ENVIRONMENT plus PREPARED_FORMAT','reads':['Actual A/B event order; actual actor route/medium; explicit teaching condition'],'writes':['Real events; same cue/probe/use opportunities to ALL fixed candidate banks'],'decision':'No target-selected bank is stimulated after reading a state. Dictionary keys name prepared candidate geometries; the native history determines which record meets a cue. This is not learned general grammar or free naming.','refs':[ref('src/integracion/relational_pair_v2.py','PairV2.curriculum'),ref('src/integracion/contact_renewal_e1.py','ContactRenewalE1Session.curriculum'),ref('src/comunicacion/contact_social_e1.py','ContactSocialE1Session.curriculum')]},
 {'boundary':'MODE_REFERENCE_CONTEXT','owner':'ENVIRONMENT plus PREPARED_COMPARATOR','reads':['Actual reference direction a, new carrier b, current context c'],'writes':['Sensor channels encode a/b/c; fixed normalizers to every candidate route'],'decision':'No input bit already says LIKE or DIFFERENT. Code chooses ports from the current physical property provided by the environment, not from a future correctness label. Similarity of a declared component is a prepared operation with an acquired reference.','refs':[ref('src/relaciones/mode_reference.py','ModeReferenceSession.acquire_reference'),ref('src/relaciones/mode_reference.py','ModeReferenceSession.query_object'),ref('src/relaciones/mode_reference.py','ModeReferenceSession.prepare_normalizers'),ref('src/comunicacion/mode_communication.py','ModeCommunicationSession.present_context')]},
 {'boundary':'CONDITIONAL_QUESTION_RETURN_USE','owner':'NATIVE_GEOMETRIC_TAP plus DECLARED_SOURCE_EXPERIENCE','reads':['Native upstream comparator product, separately acquired source, symmetric opportunities'],'writes':['Native request, source interaction, return and use'],'decision':'All opportunities are enqueued in curriculum. No observed comparison selects whether Python should ask or which result should be returned. Source p is an explicit current experience, not a target computed from another rollout. Prepared finite question/use policy is not a learned utility policy.','refs':[ref('src/iniciativa_accion/solicitud.py','prepare_gradient_tap'),ref('src/iniciativa_accion/solicitud.py','InitiativeSession.acquire_source'),ref('src/iniciativa_accion/solicitud.py','InitiativeSession.opportunities'),ref('src/iniciativa_accion/return_use.py','prepare_return_use'),ref('src/integracion/initiative_use_e1.py','InitiativeUseE1Session.curriculum')]},
 {'boundary':'FIXED_REGULATION','owner':'DESIGNER_FIXED_PHYSICAL_OPPORTUNITIES','reads':['Frozen geometry and explicit control mode'],'writes':['Counterflow payload0 on both contact candidate routes at497'],'decision':'No query to RAW, no cleanup edit, no learned attention claimed. On/offpath/omitted are overt experimental manipulations.','refs':[ref('src/comunicacion/contact_social_regulated.py','prepare_regulated_contact_social'),ref('src/comunicacion/contact_social_regulated.py','RegulatedContactSocialE1Session.curriculum')]},
 {'boundary':'PASSIVE_CAPTURE_SORTED_BOUNDARIES','owner':'AUDITOR','reads':['Current RAW-derived exact observations and receipt status; fixed critical ticks'],'writes':['Observation lists and textual decoded labels only'],'decision':'sorted run_until boundaries are instrumentation/scheduling. They add no response-specific submit; no capture result is consulted by curriculum. Receipt journals are used for provenance/coverage, not a learned answer table.','refs':[ref('src/transferencia_magnitud/cts_integrado.py','MagnitudeCTSSession.run_until'),ref('src/comunicacion/contact_social_e1.py','ContactSocialE1Session.capture_contact_social'),ref('src/relaciones/mode_reference.py','ModeReferenceSession.capture'),ref('src/comunicacion/mode_communication.py','ModeCommunicationSession.capture')]},
 {'boundary':'RENDERER_AND_LOGS','owner':'INTERFACE/AUDITOR','reads':['Live view plus stored passive captures restricted to current tick'],'writes':['Console and output/OBSERVACIONES.jsonl, append only'],'decision':'No method reads the output log back. Fixed CONTACT/FREE and LIKE/DIFFERENT texts decode current direction predicates; they are not free sentences produced by the entity. Captures restored at their same tick are recorded measurements, not new emissions or a policy memory.','refs':[ref('app/experimento.py','Experiment.emit'),ref('app/experimento.py','Experiment.observe')]},
 {'boundary':'SNAPSHOT_CONTINUITY','owner':'EXPLICIT_HUMAN_STORAGE_OPERATION','reads':['Explicit user-selected native snapshot plus bounded internal metadata'],'writes':['The native loaded world and inert Python wrappers; no curriculum replay'],'decision':'Snapshot contains legitimate RAW/clocks/queue/receipts and operational geometry/journals. Metadata chooses wrapper profile, never supplies a learned answer. Old Python capture journals are restored for audit, not used as decision tables. Loader CRC/size/integer checks are storage integrity, not authentication of an adversarial author.','refs':[ref('app/experimento.py','Experiment.execute'),ref('src/integracion/relational_pair.py','PairSession.load'),ref('src/transferencia_magnitud/cts_integrado.py','MagnitudeCTSSession.__init__'),ref('src/transferencia_magnitud/cts_integrado.py','MagnitudeCTSSession.save')]}
 ]
 events=[]
 for name in EVENTS:
  p=ROOT/name;items=[json.loads(line)for line in text(p).splitlines()if line.strip()and not line.lstrip().startswith('#')]
  events.append({'path':name,'sha256':sha(p),'operations':len(items),'fields_by_operation':{op:sorted({key for item in items if item['op']==op for key in item})for op in sorted({x['op']for x in items})},'contains_expected_target_seed_fields':any(k in('expected','target','seed','correct_answer','resultado_esperado')for item in items for k in item),'note':'Current scenario parameters inside parametros are real experience magnitudes/directions/routes; not hidden expected comparisons.'})
 exclusions=[{'path':'src/iniciativa_accion/return_use.py','scope':'main()/sha()/put() standalone research harness, imported definitions but not called by app. It reads config and writes research outputs. Its import-level ROOT/sys.path setup is a local source-path operation, not a result reader.','refs':[ref('src/iniciativa_accion/return_use.py','main')]},
  {'paths':['src/transferencia_magnitud/run_cts.py','src/transferencia_magnitud/cts_causal_restore.py','src/transferencia_magnitud/confirmar_cts.py','src/integracion/index_integracion.py'],'scope':'Not imported by app operational closure. These laboratory runners/auditors may read configurations, primaries, expected references and forks. No claim is made that all files in src lack evaluator access.'},
  {'paths':['revision/NSM65_EVIDENCIAS.json','resultados/**','referencias/**'],'scope':'Not imported/read by the reviewed operating functions as policy, associative memory, target or routing source.'}]
 report={'schema':'CPC8R.information_boundaries.static_audit.v1','created_utc':datetime.now(timezone.utc).isoformat(),
  'author':'Codex reviewer; human provisional interpretation, not generated certification','scope':'Static read-only review of the published magnitud_social app/profile and explicit imported operational closure. No new physical experiment was executed for this audit.',
  'auditor_source':{'path':str(Path(__file__).relative_to(ROOT)),'sha256':sha(__file__)},'instrument':instrument,
  'reviewed_local_sources':sources,'installed_import_review':installed_sources,'published_event_files':events,'decision_and_data_ledger':ledger,'excluded_laboratory_branches':exclusions,
  'namespace_packages_without_init_file':[p for p in PACKAGE_INITS if not(ROOT/p).is_file()],
  'findings':{'operational_target_or_result_lookup':'No path found in reviewed reachable functions that reads evaluator targets, scientific result logs, NSM catalog, seeds or prior answer files to decide a new entity response. This is a bounded static finding, not proof of absence in arbitrary code or binary internals.',
   'host_read_to_solution_write_callback':'No such path found. Observations feed capture/render/storage, whereas inputs are explicit scenario properties, user requests or schedules frozen in geometry/curriculum.',
   'physical_preparation_and_sensors':'Prepared native comparator rules, directions, guide clocks, guard geometry, phase windows and normalized format signals materially contribute. Experience supplies references/associations; those are not equivalent to acquiring the general comparator or schedule.',
   'manual_override':'entrada deliberately exposes a named physical intervention. A user can inject arbitrary allowed payloads or choose an informative scenario; this interface is not a security sandbox or proof that every possible interactive session respects a blinded scientific protocol.',
   'dynamic_dispatch':'Profile dispatch uses explicit profile/protocol strings; input dispatch uses getattr(world, kind) from an explicit user operation or the fixed submit/probe protocol. This is not output-conditioned routing. The static audit does not certify every arbitrary method-name input as a secure grammar; published event files use the declared methods.',
   'no_hidden_secondary_runtime':'Factories prepare recipe components before creating one OrganizationalWorld; wrappers attach the same world. Static review does not claim all higher-level organizations are one fused individual merely because they share Runtime.',
   'scientific_scope':'Information-boundary review supports provenance separation only. It does not establish semantic mastery, causal efficacy of every output, advantage, general intelligence, or all microscopic correctness.'},
  'source_stability_at_report':all(sha(ROOT/x['path'])==x['sha256']for x in sources)}
 path=ROOT/'revision/AUDITORIA_FRONTERAS_INFORMACION.json';temp=path.with_name(path.name+'.pending');temp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,path)
 print(json.dumps({'local_sources':len(sources),'installed_sources':len(installed_sources),'event_files':len(events),'boundaries':len(ledger),'stable':report['source_stability_at_report'],'native_matches':instrument['native']['sha256']==instrument['native']['expected_sha256'],'wheel_matches':instrument['wheel']['sha256']==instrument['wheel']['expected_sha256']}))

if __name__=='__main__':main()
