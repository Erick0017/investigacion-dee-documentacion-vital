"""Actual RP evaluator helpers over already frozen originals, never a replay."""
from pathlib import Path
import hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
spec=importlib.util.spec_from_file_location('PI06_existing_RP_evaluator',RP/'ejecutar_diagnostico.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rf=P/'codigo/RP_PI06_R01_PREPARADA/recetas/pi06_transitorio_izq0_y_continuacion_R01.json';r=read(rf);v=r['variants']['izq0_sin_captura'];proof=read(P/'control/PI06_DISC_IZQ0_R01.json');results={};all_receipts={};tests=[]
def test(name,yes):
 if not yes:raise AssertionError(name)
 tests.append({'name':name,'passed':True})
for step,source in zip(v['batches'][0],proof['outcomes'],strict=True):
 p=Path(source['primary']);test('primary_identity_'+step['label'],sha(p)==source['primary_sha256']);record=read(p);packet=record['result'];packet=json.loads(packet)if isinstance(packet,str)else packet;results[step['label']]=packet
 value=m.path_value(packet,step['read_path']);test('actual_fixed_read_path_'+step['label'],value==step['expected']and type(value)is type(step['expected']))
 collected=m.receipts(packet,step['receipt_paths'])
 for rid,receipt in collected.items():
  if rid in all_receipts and all_receipts[rid]!=receipt:raise ValueError('Contradictory original alias')
  all_receipts[rid]=receipt
 test('actor_literal_has_no_expected_answer_'+step['label'],not any(x in step['literal']for x in('expected','target','read_path','response','answer')))
 test('no_replay_global_capture_'+step['label'],step['literal'].get('captura')=='normal')
for check in v['final_checks']:
 values=[m.path_value(results[x['step']],x['path'])for x in check['values']]
 actual=values[0]-values[1]if check['operation']=='difference'else values[0]
 test('fixed_final_check_'+check['label'],actual==check['expected']and type(actual)is type(check['expected']))
test('all529_actual_receipts_applied',len(all_receipts)==529 and all(x['status']=='applied'for x in all_receipts.values()))
test('actual_negative_positive_negative_preserved',[s['expected']for s in v['batches'][0]if s['literal']['modo']=='eci01-pi06-fiplus']==[-1,1,-1])
test('Native_replay_not_claimed',r['verification']['state']=='PREPARADA_REPLAY_NATIVE_PENDIENTE'and r['verification']['Native_replay_verified']is False)
test('no_DEE_or_app_import',not any(x=='app'or x.startswith(('app.','dee_thinking'))for x in sys.modules))
out=P/'control/RECETA_PI06_R01_VERIFICACION_DOCUMENTAL.json'
with out.open('x',encoding='utf8')as f:json.dump({'schema':'DEE.PI06.recipe_documentary_check.R01','checks':tests,'passed':len(tests),'recipe_sha256':sha(rf),'Native_executed':False,
 'scope':'Existing RP evaluator paths/criteria against original frozen primaries only. The proposed replay removes global capture prospectively; no new material reproduction/passivity verified here.'},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'proof':str(out),'sha256':sha(out),'passed':len(tests),'Native_executed':False}))
