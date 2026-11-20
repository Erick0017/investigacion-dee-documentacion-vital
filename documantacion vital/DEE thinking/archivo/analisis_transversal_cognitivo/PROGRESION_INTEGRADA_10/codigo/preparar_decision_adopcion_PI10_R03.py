"""Read-only science/code collection; writes NEW staged pending decision only.

Never imports DEE/Store, runs Native, edits product, or approves promotion.
Default prints the input contract. --entradas ROOT.json --salida NEW.json
requires actual closed proofs. Root subsequently reviews and, only if all
gates really hold, writes a separate approved decision. The generated file
always has approved_for_adoption:false and status PENDING_ROOT_APPROVAL.

Input schema DEE.PI10.adoption_builder_inputs.R03. Required references:
PI10_actual_real12_proof, PI10_conservation_proof,
PI10_source_reopening_function_proof, PI10_source_zero_reopening_proof,
PI10_reproduction_result, PI10_reproduction_comparison,
adoption_metrics_proof, neutral_P02_manifest. Each is {path,sha256}.
Also: source_code_manifest:{path,sha256}, process_proof:path,
PI10_reproduction_recipe_id, decision_id, gates (six explicitly reasoned
objects with satisfied,criterion,result,evidence), scope,gains,losses,
uncertainties,assistance,regression_coverage. Optional additional_code_files
is [{file:product-system-relative,source:existingH/CSfile,sha256}].
No results, tick, counter, success, approval or code change is invented.
"""
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
import argparse,ast,copy,hashlib,importlib.util,json,os,re
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';CS=P/'estados/REAL2/sistema'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01';PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'
KEY='DEE.Cognitive.PI10.adaptive_query.two_native_traces.R02'
SELECTORS=('PROYECTO.json','CONTINUIDAD_DEE_COGNITIVE_2_0.json','sistema/estado/ACTIVO.json','sistema/estado/genesis/SELECCION_PERSONAL.json','aplicacion/GENESIS/SELECCION_CANDIDATA.json','sistema/capacidades/CATALOGO_CAPACIDADES.json')
GATES=('functional_gain','conservation','causal_controls','source_reopening','new_function_at_final_cut','decisive_recipe_replay')
REFS=('PI10_actual_real12_proof','PI10_conservation_proof','PI10_source_reopening_function_proof','PI10_source_zero_reopening_proof','PI10_reproduction_result','PI10_reproduction_comparison','adoption_metrics_proof','neutral_P02_manifest','source_code_manifest')
FROZEN=('pi10_consulta_adaptativa_R02.py','pi10_dos_trazas_legales_R01.py','pi10_entorno_dos_puertas_R01.py','pi10_transporte_ancestral_R01.py','pi10_dispatcher_R01.py','pi10_permiso_operativo_R02.py','PI10_PLUGINS_R01.json','PI10_TRANSPORTE_ANCESTRAL_R01.json','PI10_EXPERIMENTO_R02.json','PROTOCOLO_PI10_R02.json')

def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):p=Path(p).resolve(strict=True);return {'path':str(p),'sha256':sha(p)}
def safe(p,root):
 p=Path(p)
 for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No linked/reparse paths')
 p=p.resolve(strict=True);need(p.is_relative_to(root.resolve())and p.is_file(),'Explicit existing file outside allowed root');return p
def ref(r):
 p=safe(r['path'],P);need(sha(p)==r['sha256'],'Actual proof hash differs: '+str(p));return info(p)
def load(name,p):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def write(p,v):
 p=Path(p);need(not p.exists(),'Existing pending output is preserved');p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def rel(name):
 p=PurePosixPath(name);need(isinstance(name,str)and not p.is_absolute()and ':'not in name and '\\'not in name and not any(x in('.','..')for x in p.parts),'Safe relative code target required');return p

def prepare(i,source_input,out):
 need(i.get('schema')=='DEE.PI10.adoption_builder_inputs.R03','Actual Root input schema required')
 need(set(i['gates'])==set(GATES),'All six actual gate judgments required')
 references={key:ref(i[key])for key in REFS};views={key:read(x['path'])for key,x in references.items()}
 for name in GATES:
  gate=i['gates'][name];need(type(gate.get('satisfied'))is bool and gate.get('criterion')and gate.get('result')and gate.get('evidence'),'Actual result, criterion and references required for '+name)
  for r in gate['evidence']:ref(r)
 for k in('scope','gains','losses','uncertainties','assistance','regression_coverage','decision_id','PI10_reproduction_recipe_id'):need(k in i and i[k]is not None,'Explicit Root judgment required: '+k)
 need(read(S/'estado/ACTIVO.json')['life_id']==PARENT,'Protected source selection advanced or changed')
 card=read(CS/'estado/vidas'/LIFE/'VIDA.json');snap=safe(CS/card['snapshot'],CS)
 need(card['life_id']==card['world_id']==LIFE and card['physical']['N']==67 and sha(snap)==card['snapshot_sha256'],'Actual current complete REAL2 card and Native snapshot required')
 need(not(CS/'estado/locks'/(LIFE+'.lock')).exists()and not(CS/'estado/vidas'/LIFE/'FUTURO_INTERRUMPIDO.json').exists()and not(P/'PI10_ROOT_NATIVE_WRITER.lock').exists(),'Closed unambiguous source only')
 parser=load('PI10_static_existing_snapshot_parser',C/'reproducibilidad/observador_pasivo.py');meta=parser.snapshot_view(snap)['metadata'];m=read_meta(meta[KEY])
 need(m['ordinal']==len(m['rows'])and 12<=m['ordinal']<18 and not m.get('pending')and not m.get('uncertain')and m.get('admission_control')=={'role':'evaluation','arm':'real','trace_control':'none','force_query':None},'Actual acquired, closed, unexhausted source; never controls/calibration')
 zero=views['PI10_source_zero_reopening_proof'];need(zero.get('closed')is True and zero.get('life_id')==LIFE and zero.get('new_Native_ticks')==0 and zero.get('final_tick')==card['physical']['tick']and zero['final_saved_Native']['encoded_sha256']==card['snapshot_sha256'],'Actual zero-reopened final source checkpoint binding required')
 metrics=views['adoption_metrics_proof'].get('measured_adoption_metrics');need(isinstance(metrics,dict),'Actual measured_adoption_metrics proof required')
 manifest=views['source_code_manifest'];need(isinstance(manifest.get('files'),list)and manifest['files'],'Actual complete current source code closure required')
 code={}
 def add(name,source,digest):
  p=rel(name);source=Path(source).resolve(strict=True);need(source.is_relative_to(CS.resolve())or source.is_relative_to(H.resolve()),'Source code must be current CS or reviewed H')
  safe(source,CS if source.is_relative_to(CS.resolve())else H);need(sha(source)==digest,'Actual source code hash differs '+name)
  need(source.suffix in('.py','.json')and(p.parts[0]in('app','capacidades','contratos')or name=='gestionar.py'),'Unreviewed non-code delta needs separate explicit resolution: '+name)
  ast.parse(source.read_bytes())if source.suffix=='.py'else read(source)
  target=S/p;before=sha(target)if target.is_file()else None
  item={'file':name,'source':str(source),'sha256':digest,'before_sha256':before}
  need(name not in code or code[name]==item,'Conflicting additional/current code source '+name);code[name]=item
 for row in manifest['files']:
  p=rel(row['file']);source=CS/p;need(source.is_file()and sha(source)==row['sha256'],'Current source closure drift: '+row['file'])
  target=S/p
  if not target.is_file()or sha(target)!=row['sha256']:add(row['file'],source,row['sha256'])
 for row in i.get('additional_code_files',[]):add(row['file'],row['source'],row['sha256'])
 helper=H/'pi10_identidad_c2c_R02.py';add('app/pi10_identidad_c2c_R02.py',helper,sha(helper))
 need(all((CS/'capacidades'/name).is_file()for name in FROZEN),'Reviewed public permission/source delta not yet installed on closed REAL2')
 contract={'schema':'DEE.PI10.exact_operational_permission.v2','life_id':LIFE,'profile':'fisica_directa','N':67,'status':'PREPARED_DIAGNOSTIC','all_adoption_gates_met':all(x['satisfied']is True for x in i['gates'].values()),'adoption_decision_sha256':None,'source_P02_manifest_sha256':references['neutral_P02_manifest']['sha256'],'protocol_sha256':sha(CS/'capacidades/PROTOCOLO_PI10_R02.json'),'allowed_modes':['eci01-pi10-episodio','eci01-pi10-estado'],'public_FI_backend':'inherited_FI8_same_frozen_body','public_FI_domain':[0,20],'internal_FI_redirected':False,'historical_material_disabled':True,'C2C_protocol_sha256':'0cf6bf8508e071a1c8cf1448023a096bc43336d66b8a1deb98f488b29b4205fd','public_arithmetic_policy':'legacy_partial','frozen_files_sha256':{name:sha(CS/'capacidades'/name)for name in FROZEN},'assistance':copy.deepcopy(i['assistance']),'finite_resources_preserved_without_reset':True}
 contractpath=H/'PERMISO_OPERATIVO_PI10_R02_PROPUESTO/contratos/PI10_USO_OPERATIVO_R01.json'
 if contractpath.exists():need(read(contractpath)==contract,'An earlier different prepared contract is preserved')
 else:write(contractpath,contract)
 add('contratos/PI10_USO_OPERATIVO_R01.json',contractpath,sha(contractpath))
 catalog=i.get('catalog_entry',{'id':'PI10_R02_CONSULTA_CONTEXTO_DOS_TRAZAS','type':'seleccion_adquirida_acotada','status':'PENDING_ROOT_APPROVAL','scope':'Consulta contextual por consecuencias en dos trazas físicas; no iniciativa general ni planning aprendido.','reproduction_recipe':i['PI10_reproduction_recipe_id'],'positive_evidence':references['PI10_actual_real12_proof'],'adverse_evidence':'R01 stopped on mixed preview; cold Q1 NULL retained; all controls preserved.'})
 d={'schema':'DEE.PI10.reasoned_adoption_decision.R02','status':'PENDING_ROOT_APPROVAL','approved_for_adoption':False,'life_id':LIFE,'profile':'fisica_directa','source_tick':card['physical']['tick'],'source_snapshot_sha256':card['snapshot_sha256'],'source_PI10_ordinal':m['ordinal'],'measured_adoption_metrics':metrics,'gates':copy.deepcopy(i['gates']),'approved_code_files':[code[k]for k in sorted(code)],'selectors_cas':{name:sha(C/name)for name in SELECTORS},'catalog_entry':catalog,'new_contract':contract,'scope':i['scope'],'gains':i['gains'],'losses':i['losses'],'uncertainties':i['uncertainties'],'assistance':i['assistance'],'evidence':list(references.values()),'regression_coverage':i['regression_coverage'],'process_proof':str(safe(i['process_proof'],P)),'decision_id':i['decision_id'],'PI10_reproduction_recipe_id':i['PI10_reproduction_recipe_id'],**references,'builder':{'schema':'DEE.PI10.pending_root_decision_builder.R03','at':datetime.now(timezone.utc).isoformat(),'source_input':info(source_input),'source_card':info(CS/'estado/vidas'/LIFE/'VIDA.json'),'Source_or_product_modified':False,'Native_executed':False,'automatic_approval':False,'new_staged_contract':info(contractpath),'actual_Root_review_and_explicit_separate_approval_required':True}}
 adopter=load('PI10_staged_R03_readonly_code_check',H/'incorporar_PI10_misma_identidad_R03.py');adopter.code(d)
 write(out,d);return d
def read_meta(v):return json.loads(v)
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--entradas',type=Path);ap.add_argument('--salida',type=Path);a=ap.parse_args()
 if a.entradas is None:print(json.dumps({'mode':'READ_ONLY_PLAN','input_schema':'DEE.PI10.adoption_builder_inputs.R03','required_references':REFS,'required_gates':GATES,'output_always_pending_approval':True,'Native':0}));raise SystemExit
 need(a.salida is not None and not a.salida.exists(),'Explicit NEW pending output required');d=prepare(read(a.entradas),a.entradas,a.salida);print(json.dumps({'decision':info(a.salida),'status':d['status'],'approved_for_adoption':False,'source_tick':d['source_tick'],'source_PI10_ordinal':d['source_PI10_ordinal'],'reviewed_code_delta':len(d['approved_code_files']),'Native':0},ensure_ascii=False))
