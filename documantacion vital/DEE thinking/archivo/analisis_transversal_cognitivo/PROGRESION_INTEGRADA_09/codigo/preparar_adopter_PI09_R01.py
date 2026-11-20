"""Derive the bounded PI08 whole-move workflow; no product/state mutation."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;P=H.parent;BASE=P.parent/'PROGRESION_INTEGRADA_08/codigo/incorporar_B_PI08_misma_identidad_R01.py';OUT=H/'incorporar_PI09_misma_identidad_R01.py'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 if OUT.exists():raise FileExistsError('Adopter preparado anterior preservado')
 text=BASE.read_text('utf-8-sig').replace("CS=P/'estados/B_REAL_R01/sistema'","CS=P/'estados/NATIVE/sistema'")
 text=text.replace('ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_REAL_01','ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01')
 text=text.replace('PI08_B_USO_OPERATIVO_R01','PI09_CONSULTA_OPERATIVA_R01').replace('pi08_identidad_c2c_B_R01','pi09_identidad_c2c_R01')
 text=text.replace('PI08_B','PI09').replace('DEE.PI08.B','DEE.PI09').replace("d['B_actual_closed_arms']['real']","d['PI09_actual_closed_arms']['native_real']")
 text=text.replace('source_B_REAL_closed18','source_PI09_NATIVE_closed12').replace('Actual learned source work before same-ID relocation; selected public/B use remains an explicit next operational gate.','Actual Native12 source before same-ID relocation. Selected public use remains a separate operational test.')
 tree=ast.parse(text);lines=text.splitlines(keepends=True)
 remove={'decision','validate_B_evidence','code'}
 for node in sorted([n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in remove],key=lambda n:n.lineno,reverse=True):lines[node.lineno-1:node.end_lineno]=[]
 text=''.join(lines);anchor="if __name__=='__main__':main()";assert text.count(anchor)==1
 functions=r'''
def decision(file):
 d=read(file);required={'approved_for_adoption','life_id','source_snapshot_sha256','source_tick','gates','approved_code_files','selectors_cas','catalog_entry','new_contract','scope','gains','losses','uncertainties','assistance','evidence','regression_coverage','process_proof','PI09_actual_closed_arms','PI09_source_full_pair','PI09_reproduction_result','PI09_reproduction_comparison','PI09_conservation_proof'}
 if not required<=set(d)or d['approved_for_adoption']is not True or d['life_id']!=LIFE:raise ValueError('Actual reasoned Root approval required; no prospective promotion')
 for name in GATES:
  gate=d['gates'].get(name,{})
  if gate.get('satisfied')is not True or not gate.get('criterion')or not gate.get('result')or not gate.get('evidence'):raise ValueError('Missing actual empirical gate: '+name)
 for item in d['evidence']+[e for gate in d['gates'].values()for e in gate.get('evidence',[])]:
  if sha(bounded(item['path'],P))!=item['sha256']:raise ValueError('Actual evidence hash differs')
 if set(d['selectors_cas'])!=set(SELECTORS):raise ValueError('All six existing product references require CAS')
 c=d['new_contract'];template=read(H/'PERMISO_OPERATIVO_PI09_R01_PROPUESTO/contratos/PI09_CONSULTA_OPERATIVA_R01.json')
 immutable=('schema','life_id','profile','protocol_sha256','allowed_modes','all_outer_FI_requests','public_FI_domain','internal_C2C_FI_redirected','FI_protocol_sha256','C2C_protocol_sha256','C2C_allowed_modes','frozen_files_sha256','finite_resources_preserved_without_reset','historical_PI07_environment_material_disabled')
 if any(c.get(k)!=template.get(k)for k in immutable)or c.get('status')!='PREPARED_DIAGNOSTIC'or c.get('adoption_decision_sha256')is not None or c.get('all_adoption_gates_met')is not True:raise ValueError('Exact separately prepared PI09 public/Native/C2C profile required')
 if c.get('public_arithmetic_policy')not in('legacy_partial','P0_phase19_fixed'):raise ValueError('Explicit public arithmetic scope required')
 if c['public_arithmetic_policy']=='P0_phase19_fixed':
  refs=c.get('arithmetic_guard_actual_evidence',[])
  if c.get('arithmetic_guard_actual_gate_met')is not True or len(refs)<2:raise ValueError('Actual paired/reserved P0 evidence required before public guard')
  for ref in refs:
   if sha(bounded(ref['path'],P))!=ref['sha256']:raise ValueError('P0 evidence changed')
 validate_PI09_evidence(d)
 return d

def evidence(ref):
 file=bounded(ref['path'],P)
 if sha(file)!=ref['sha256']:raise ValueError('Actual proof bytes changed')
 return read(file)

def validate_PI09_evidence(d):
 seal=read(H/'SELLO_PI09_CONSULTA_R02.json')
 if sha(H/'SELLO_PI09_CONSULTA_R02.json')!='30e0160fa4bdb05dd258295611a68416ddab7858fc06d1f9cea7e9b67df931d8':raise ValueError('Frozen normalized PI09 seal changed')
 arms=d['PI09_actual_closed_arms']
 if set(arms)!={'native_real','always_real','never','always_desacoplado'}:raise ValueError('All four actual prospectively declared PI09 arms required')
 for role,ref in arms.items():
  proof=evidence(ref);ops=[r for r in proof.get('records',[])if r.get('literal',{}).get('modo')=='eci01-pi09-episodio']
  if proof.get('life_id')!=seal['arms'][role]or proof.get('initial_tick')!=884835 or proof.get('closed')is not True or proof.get('error')is not None or len(ops)!=12:raise ValueError('Missing closed actual twelve-opportunity arm: '+role)
  for index,op in enumerate(ops):
   row=op['rows'][0]
   if row.get('ordinal')!=index or row.get('query_control')!=('native'if role=='native_real'else'never'if role=='never'else'always')or row.get('Native_inputs',{}).get('all_terminal')is not True:raise ValueError('Incomplete/misbound material PI09 arm')
  if role=='native_real'and proof['final_tick']!=d['source_tick']:raise ValueError('Approved source cut differs from canonical Native12')
 pair_ref=d['PI09_source_full_pair'];pair=bounded(pair_ref['path'],P);m=read(pair/'EXPORTACION_SERVICIO.json')
 if sha(pair/'EXPORTACION_SERVICIO.json')!=pair_ref['manifest_sha256']or m['life_id']!=LIFE or m['physical']['tick']!=d['source_tick']or m['snapshot_sha256']!=d['source_snapshot_sha256']or sha(pair/m['native_snapshot'])!=m['snapshot_sha256']:raise ValueError('Actual complete canonical source pair required')
 result=evidence(d['PI09_reproduction_result'])
 if result.get('status')!='COMPLETED'or result.get('owner_closed_coherently')is not True or result.get('criteria_met')is not True or result.get('life')not in seal['native_reproduction_ids']:raise ValueError('Actual full RP frontdoor cold12 result required')
 comparison=evidence(d['PI09_reproduction_comparison'])
 if comparison.get('physical_equal')is not True or comparison.get('causal_prefix_equal')is not True or comparison.get('unexpected_metadata_changes')!=[]:raise ValueError('Full actual Native replay comparison with narrow explained identity differences required')
 conservation=evidence(d['PI09_conservation_proof'])
 if conservation.get('closed')is not True or conservation.get('error')is not None:raise ValueError('Actual closed prospective conservation/challenge evidence required')
 if d['new_contract']['public_arithmetic_policy']=='P0_phase19_fixed'and not d['gates']['conservation']['satisfied']:raise ValueError('No untested public arithmetic repair')
 return True

def code(d):
 rows=[];seen=set();c=d['new_contract']
 for name,digest in c['frozen_files_sha256'].items():
  if Path(name).name!=name or sha(CS/'capacidades'/name)!=digest:raise ValueError('Scientific source changed: '+name)
 for item in d['approved_code_files']:
  rel=relative(item['file']);name=rel.as_posix();source=Path(item['source']).resolve(strict=True);target=bounded(S/rel,S,False);regular(source)
  if name in seen:raise ValueError('Repeated source delta target')
  seen.add(name)
  if not(source.is_relative_to(CS.resolve())or source.is_relative_to(H.resolve()))or source.suffix not in('.py','.json')or rel.parts[0]not in('app','capacidades','contratos')and name!='gestionar.py':raise ValueError('Only explicit reviewed current source/protocol/permission bytes; no engine/state')
  if rel.parts[0]=='contratos':
   if name!='contratos/PI09_CONSULTA_OPERATIVA_R01.json'or read(source)!=c:raise ValueError('Only the exact approved PREPARED contract may deploy before selection')
  if sha(source)!=item['sha256']or(target.exists()and sha(target)!=item.get('before_sha256'))or(not target.exists()and item.get('before_sha256')is not None):raise ValueError('Code CAS differs: '+name)
  ast.parse(source.read_bytes())if source.suffix=='.py'else read(source)
  rows.append({**item,'source':str(source),'target':str(target),'bytes':source.stat().st_size})
 required={'app/mundo_genesis_apd05.py','app/cola_local.py','app/pi09_identidad_c2c_R01.py','app/usar_dee.py','capacidades/pi04_dispatcher.py','capacidades/pi09_permiso_operativo_R01.py','capacidades/pi09_transporte_heredado_R02.py','capacidades/PI09_TRANSPORTE_HEREDADO_R02.json','capacidades/pi09_dispatcher_R02.py','capacidades/PI09_PLUGINS_R02.json','capacidades/pi09_consulta_selectiva_R02.py','capacidades/PROTOCOLO_PI09_CONSULTA_R01.json','capacidades/SELLO_PI09_CONSULTA_R02.json','contratos/PI09_CONSULTA_OPERATIVA_R01.json'}
 if not required<=seen:raise ValueError('Missing exact public/identity/dispatcher/whole-source required delta')
 if c['public_arithmetic_policy']=='P0_phase19_fixed'and 'capacidades/pi09_aritmetica_temporal_P0_R01.py'not in seen:raise ValueError('Approved P0 public helper missing')
 # Entire current dependency closure must remain available after the delta.
 source_manifest=read(P/'estados/NATIVE/SISTEMA_CODIGO_PI09.json')
 for original in source_manifest['files']:
  name=original['file']
  if name in seen:continue
  target=S/name
  if not target.is_file()or sha(target)!=original['sha256']:raise ValueError('Uncovered current dependency closure: '+name)
 return rows
'''
 text=text.replace(anchor,functions+'\n'+anchor);ast.parse(text);OUT.write_text(text,'utf8')
 proof={'schema':'DEE.PI09.same_identity_adopter.prepared_derivation.R01','base':str(BASE),'base_sha256':sha(BASE),'prepared':str(OUT),'sha256':sha(OUT),'Native_executed':False,'product_modified':False,'default_no_source_state_read':True,'gates_actual_and_Root_approval_required':True,'reused':['whole three-directory and all checkpoint same-volume move','six selector CAS','Store.promote COMMITTED witness','prepared profile then committed publication','actual0tick unselected reopening','narrow C2C identity leaf only'],'new_guards':['four closed PI09 arms','actual RPcold12 and full Native comparison','actual prospective conservation','no public P0 unless actual pair/reserve evidence','complete current code closure']}
 (H/'ADOPTER_PI09_R01_PREPARADO.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(proof))
if __name__=='__main__':main()
