"""Pure exact inherited panel12 adaptation; never runs a material query."""
from pathlib import Path
import copy,hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';P9=P.with_name('PROGRESION_INTEGRADA_09');source=P9/'codigo/PLAN_PI09_PANEL_POST_D12_R03.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 data=json.dumps(v,ensure_ascii=False,indent=2)+'\n'
 if p.exists():assert p.read_text('utf8')==data
 else:
  with p.open('x',encoding='utf8')as f:f.write(data)
p=json.loads(source.read_text('utf8'));wanted=['habitat_off','luma','nara','clasifica','suma','alfa','FIplus','FIminus','FIzero','number13','number8','alfa_after','luma_after'];assert [s['label']for s in p['steps']]==wanted
allowed={'label','literal','max_ticks','feedback','actuator','expected','read_path'};steps=[]
for old in p['steps']:
 s={k:copy.deepcopy(v)for k,v in old.items()if k in allowed}
 if s['label'].startswith('FI'):s['literal']['modo']='eci01-balance'
 if s['label']=='number8':s['literal']={'modo':'eci01-aritmetica-directa','operacion':'diferencia','izquierda':9,'derecha':1}
 assert 'expected'not in s['literal']and not any(k in s['literal']for k in('espera_previa','respuesta','target','correcto'))
 steps.append(s)
core=['luma','nara','clasifica','suma','alfa','FIplus','FIminus','FIzero','alfa_after','luma_after'];panel={'schema':'DEE.PI10.R02.inherited12.fixed_steps.v1','steps':steps,'source':{'path':str(source),'sha256':sha(source)},'coverage':{'total_scored':12,'critical_core10':core,'numeric2':['number13','number8'],'non_scored_zero_tick':['habitat_off']},'prepared_transduction':'Outer eci01-balance is routed by PI10 R02 permission to actual inherited FI8, same frozen body/reader; consumes exactly3 existing offers, no reset or new supply. Internal PI10/C2C FI is not redirected.','numeric_scope':'6+7=13 and independently9-1=8, as Root requested. Historical P9 used actual13->13-5; that chain is not claimed here. No wait36, reread, reteaching, geometry move or numerical rescue.','Native_executed':False,'expected_values_are_auditor_only_not_literal':True}
out=H/'PANEL_HEREDADO_12_PI10_R02_PASOS.json';put(out,panel)
extra={'schema':'DEE.PI10.R02.predeclared_extra_numeric.fixed_steps.v1','activation':'Only if exactly one formed numeric failure, critical10/10, reserved attributed gain>=3 and physical gain>=1, per frozen protocol. Not a retry of either original numeric case. Keep the original12 results unchanged and report this separately.','steps':[{'label':'additional_number9_predeclared','literal':{'modo':'eci01-aritmetica-directa','operacion':'suma','izquierda':4,'derecha':5},'max_ticks':600,'feedback':'real','actuator':'closed','read_path':['result','rows',0,'numeric_result'],'expected':9}],'Native_executed':False,'not_part_of_original_panel12_denominator':True};ef=H/'NUMERICO_ADICIONAL_PI10_R02_PASOS.json';put(ef,extra)
print(json.dumps({'panel':str(out),'sha256':sha(out),'finite_bound':sum(s['max_ticks']for s in steps),'scored':12,'core':10,'extra':str(ef),'extra_sha256':sha(ef),'Native':0}))
