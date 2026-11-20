"""Prepare exact 600-tick adverse/positive-history replay from closed primaries.

Writes only proposed recipe/requirements/registrar source under PI06/codigo.
No Native execution, Cognitive write, capability promotion or hidden answer.
"""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';STAGE=H/'RP_PI06_R01_PREPARADA';NAME='pi06_transitorio_izq0_y_continuacion_R01'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
proofpath=P/'control/PI06_DISC_IZQ0_R01.json';proof=read(proofpath);planpath=Path(proof['plan']);plan=read(planpath)
if proof.get('status')!='CLOSED'or proof.get('closed')is not True or proof.get('error')is not None or proof['initial_tick']!=825849 or proof['final_tick']!=826449 or proof['new_ticks']!=600:raise ValueError('Only the actual closed600-tick R01, not an imagined successful capacity')
if sha(planpath)!=proof['plan_sha256']:raise ValueError('Executed plan identity changed')
batch=[];checks=[];receipts={};answers=[];lastphysical=None
for source,planned in zip(proof['outcomes'],plan['steps'],strict=True):
 path=Path(source['primary'])
 if sha(path)!=source['primary_sha256']:raise ValueError('Closed primary bytes changed')
 primary=read(path);packet=primary['result'];packet=json.loads(packet)if isinstance(packet,str)else packet;row=packet['result']['rows'][0]
 step={'label':source['label'],'literal':copy.deepcopy(planned['literal']),'feedback':planned.get('feedback','omit'),'actuator':planned.get('actuator','closed'),
  'receipt_paths':[['result','rows',0,'requests']],'stop_on_unapplied_receipt':True}
 if step['literal']['modo']=='eci01-pi06-fiplus':
  answer=row['early_physical_choice'];answers.append(answer)
  if type(answer)is not int:raise ValueError('Do not convert a NULL into a replay answer')
  step['literal']['captura']='normal'
  step.update(read_path=['result','rows',0,'early_physical_choice'],expected=answer,stop_on_NULL=True)
  checks.append({'label':source['label']+'_fixed_q6','operation':'value','values':[{'step':source['label'],'path':['result','rows',0,'old_q6_choice']}],'expected':row['old_q6_choice']})
 else:step.update(read_path=['after_tick'],expected=source['after_tick'])
 for req in row.get('requests',[]):
  rid=req['id'];r=req['receipt']
  if rid!=r['id']or not source['before_tick']<=r['requested_tick']<=source['after_tick']or(rid in receipts and receipts[rid]!=r):raise ValueError('Current-step receipt identity/window differs')
  receipts[rid]=r
 batch.append(step);lastphysical=packet['committed_snapshot']['physical']
if answers!=[-1,1,-1]or len(receipts)!=529 or any(r['status']!='applied'for r in receipts.values()):raise ValueError('Actual R01 negative/positive/negative chronology or529-input dose changed')
checks+=[{'label':'complete600ticks','operation':'difference','values':[{'step':batch[-1]['label'],'path':['after_tick']},{'step':batch[0]['label'],'path':['before_tick']}],'expected':600},
 {'label':'actualfinaltick','operation':'value','values':[{'step':batch[-1]['label'],'path':['after_tick']}],'expected':826449}]
recipe={'schema':'DEE.reproduction.recipe.v1','id':NAME,'title':'PI06: reproducción de interferencia transitoria y uso posterior -1,+1,-1',
 'revision':'R01_PREPARADA_REPLAY_NATIVE_PENDIENTE','prefix':'PI06_POST_BASE_T825849','code_capsule_key':'PI06_ORGANIZACION_DIAGNOSTICO_R01',
 'required_life_prefix':'ECI02_PI03_REPRO_PI04_PI05_PI06_','reproduction_enabled':True,'requires_explicit_material':True,
 'variants':{'izq0_sin_captura':{'batches':[batch],'final_checks':checks,'native_receipt_expectations':{'unique_requested':529,'applied':529,'rejected':0,'pending_or_other':0}}},
 'assistance':['Operator supplies the complete frozen prefix, opportunity schedule, fixed FI128 queries/readers and one legal SEM1 zero packet.','The environment and host advance the official world; no correction, new SEM4 guard, clearing, target-aware action or response substitution.'],
 'limitations':['Technical replay of the observed local transient vulnerability: only1/3 FI14>3 comparisons was useful (-1,+1,-1). Reproduction coincidence is not3/3 cognitive success.','The replay fixes captura=normal for all three FI calls, while the original discovery captured globally. This is a preregistered material passivity contrast plus replay, not a byte-identical repetition of instrumentation. Inputs/readers/calendars/perturbation remain fixed.','The variants share history; not independent organisms or a new acquisition. Expected values are evaluator-only after each original fixed Native output.','No spontaneous repair, regulation, autonomy or promotion is certified. Inspect complete final Native fields/prefix and every metadata difference after replay; no universal observer claim.'],
 'verification':{'state':'PREPARADA_REPLAY_NATIVE_PENDIENTE','original_execution':{'path':str(proofpath),'sha256':sha(proofpath),'life_id':proof['life_id'],'initial_tick':825849,'final_tick':826449,'Native_ticks':600,'inputs_unique_applied':529},'Native_replay_verified':False},
 'expected_final_physical':{k:lastphysical[k]for k in('N','tick','RAW_sha256','clocks_sha256')},
 'fixed_reader':'Original FI128 q+4 early and q+6 original; material zero remains0, NULL remainsNone. No retrospective reader selection.'}
snapshots=list((P/'estados/candidato/sistema/estado/checkpoints').glob(proof['life_id']+'.T826449.*.deetsnap.gz'))
frozen=[p for p in snapshots if sha(p)==proof['final_snapshot_sha256']]
if len(frozen)!=1:raise ValueError('One exact frozen closed original snapshot is required; never use a current live card')
C=P.parents[2]/'DEE Cognitive 2.0';spec=importlib.util.spec_from_file_location('PI06_recipe_frozen_parser',C/'reproducibilidad/observador_pasivo.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
view=parser.snapshot_view(frozen[0]);recipe['expected_final_Native']={'source_frozen_snapshot':str(frozen[0]),'source_snapshot_sha256':proof['final_snapshot_sha256'],
 'physical':view['physical'],'causal_prefix_sha256':view['causal_prefix_sha256'],'interfaces':view['interfaces'],'pending_native':view['pending_native'],'native_receipts':view['native_receipts'],
 'scope':'Predetermined before cold replay. Compare actual complete Native fields/prefix; list every metadata change separately, not blanket acceptance.'}
req={'complete_pair':{'alias':'PI06_POST_BASE_T825849','manifest_sha256':'1dc5636081eb828ffe5219dbab3a08ec2c163f62708935b293c0eeb281cf5cd2'},
 'frozen_pi06_module':{'sha256':'c2cec3a42ea9c033869a2c689564ea51faac079f929b51cc271463b396477285'},
 'frozen_pi06_protocol':{'sha256':'2a1743f16c9969c770f1fbc8bdad26ee411ac1b395664eb6a2c679a46e7c2570'},
 'scope':'Full capsule and prefix must be stably preserved before registration. The recipe remains Native-replay-pending until a real closed test is registered.'}
(STAGE/'recetas').mkdir(parents=True,exist_ok=False)
for file,data in((STAGE/'recetas'/(NAME+'.json'),recipe),(STAGE/'SOLICITUD_MATERIALES.json',req)):
 with file.open('x',encoding='utf8')as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
old=P.with_name('PROGRESION_INTEGRADA_05')/'codigo/registrar_receta_guardia_RP_PI05_R02.py';text=old.read_text('utf-8-sig')
changes=[('RP_GUARDIA_PI05_R01_PREPARADA','RP_PI06_R01_PREPARADA'),('pi05_guardia_y_sham_transito_R01',NAME),('PI03_PI05_REAL_PREFI_T817876','PI06_POST_BASE_T825849'),
 ('frozen_guard_module','frozen_pi06_module'),('frozen_guard_protocol','frozen_pi06_protocol'),('pi05_guardia_transito_R01.py','pi06_organizacion_R01.py'),
 ('PROTOCOLO_PI05_GUARDIA_R01.json','PROTOCOLO_PI06_ORGANIZACION_R01.json'),('PI05_TRANSITO_GUARDIA_R01','PI06_ORGANIZACION_DIAGNOSTICO_R01'),
 ('817876','825849'),('pares/REAL_PREFI_T825849','pares/POST_BASE_T825849'),('RP_GUARDIA_PI05_R01_','RP_PI06_TRANSITORIO_R01_'),
 ('DEE.PI05.RP.additive_registration.R01','DEE.PI06.RP.additive_registration.R01'),('ECI02_PI03_MAIN/VIDA.json','ECI02_PI03_REPRO_PI04_PI05_MAIN_01/VIDA.json')]
for before,after in changes:
 if before not in text:raise ValueError('Registrar source contract changed: '+before)
 text=text.replace(before,after)
ast.parse(text);registrar=H/'registrar_receta_RP_PI06_R01.py'
with registrar.open('x',encoding='utf8')as f:f.write(text)
print(json.dumps({'recipe':str(STAGE/'recetas'/(NAME+'.json')),'recipe_sha256':sha(STAGE/'recetas'/(NAME+'.json')),
 'registrar':str(registrar),'registrar_sha256':sha(registrar),'answers_preserved':answers,'Native_inputs':len(receipts),'Native_executed':False},ensure_ascii=False))
