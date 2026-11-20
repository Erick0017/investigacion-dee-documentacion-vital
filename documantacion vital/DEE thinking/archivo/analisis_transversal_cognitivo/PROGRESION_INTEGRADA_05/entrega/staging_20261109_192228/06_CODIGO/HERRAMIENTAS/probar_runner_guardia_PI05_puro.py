"""Synthetic documentary test for runner parser only, no owner/Native import."""
from pathlib import Path
import copy,hashlib,importlib.util,json,sys
H=Path(__file__).resolve().parent;P=H.parent
path=H/'ejecutar_FI_GUARDIA_PI05_R01.py';spec=importlib.util.spec_from_file_location('PI05_guard_runner_fake',path)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
source=json.loads((P/'control/PI05_REAL_FI_GLOBAL_R01.json').read_text('utf8'))['actual']
assert not any(n.startswith(('dee_thinking','app.'))for n in sys.modules)
cases=[]
for answer in(1,0,None,-1):
    a=copy.deepcopy(source);row=a['result']['rows'][0];rid=max(r['id']for r in row['requests'])+1
    row['requests'].append({'id':rid,'port':'FAKE.guard','tick':817878,'payload':0,
        'receipt':{'id':rid,'status':'applied','requested_tick':817878}})
    row['Native_inputs']={'unique_requested':177,'applied':177,'rejected_or_other':0}
    row['early_physical_choice']=answer;row['old_q6_choice']=answer
    result=m.summarize(a,14,3)
    assert result['Native_inputs']['unique_requested']==177 and result['new_Native_ticks']==198
    cases.append({'synthetic_answer':answer,'reported_outcome':result['outcome'],'early_is_NULL':result['early_is_NULL'],'early_is_material_zero':result['early_is_material_zero']})
assert cases[1]['early_is_material_zero']and not cases[1]['early_is_NULL']
assert cases[2]['early_is_NULL']and not cases[2]['early_is_material_zero']
assert m.literal(14,3,'global','guardia')['modo']=='eci01-pi05-fiplus-guardia'
assert m.literal(14,3,'global','sham')['modo']=='eci01-pi05-fiplus-sham'
proof={'schema':'DEE.PI05.guard_runner.synthetic_parser_test.R01','Native_executed':False,'new_ticks':0,
       'scope':'Mutated in-memory documentary fixture only; outcomes below are synthetic parser cases, not Native trials.',
       'runner_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'cases':cases,'DEE_or_app_imports':False}
out=P/'control/PRUEBAS_RUNNER_GUARDIA_PURO_R01.json';assert not out.exists();out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(proof))
