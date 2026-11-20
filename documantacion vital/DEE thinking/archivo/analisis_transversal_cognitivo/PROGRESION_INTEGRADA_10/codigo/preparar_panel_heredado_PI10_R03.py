"""Pure P9-exact inherited panel: actual numeric-result transport, no Native."""
from pathlib import Path
import copy,hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';SOURCE=P.with_name('PROGRESION_INTEGRADA_09')/'codigo/PLAN_PI09_PANEL_POST_D12_R03.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 data=json.dumps(v,ensure_ascii=False,indent=2)+'\n'
 if p.exists():assert p.read_text('utf8')==data
 else:
  with p.open('x',encoding='utf8')as f:f.write(data)
def main():
 original=json.loads(SOURCE.read_text('utf-8-sig'));wanted=['habitat_off','luma','nara','clasifica','suma','alfa','FIplus','FIminus','FIzero','number13','number8','alfa_after','luma_after'];assert [s['label']for s in original['steps']]==wanted
 allowed={'label','literal','max_ticks','feedback','actuator','expected','read_path','actual_integer_binding'};steps=[]
 for old in original['steps']:
  s={k:copy.deepcopy(v)for k,v in old.items()if k in allowed}
  if s['label'].startswith('FI'):s['literal']['modo']='eci01-balance'
  assert not any(k in s['literal']for k in('expected','respuesta','target','correcto','espera_previa'))
  steps.append(s)
 assert steps[9]['literal']=={'modo':'eci01-aritmetica-directa','operacion':'suma','izquierda':6,'derecha':7}
 assert steps[10]['literal']=={'modo':'eci01-aritmetica-directa','operacion':'diferencia','derecha':5}
 assert steps[10]['actual_integer_binding']=={'from_step':'number13','field':'izquierda'}
 value={'schema':'DEE.PI10.R02.inherited12.fixed_steps.v2','steps':steps,'source':{'path':str(SOURCE),'sha256':sha(SOURCE)},'coverage':{'total_scored':12,'critical_core10':['luma','nara','clasifica','suma','alfa','FIplus','FIminus','FIzero','alfa_after','luma_after'],'numeric2':['number13','number8'],'non_scored_zero_tick':['habitat_off']},'prepared_transduction':'Only outer balance mode is routed by the exact PI10 permission to inherited FI8, same frozen body/reader and actual remaining stock. No internal PI10/C2C FI reroute. The second arithmetic left operand is the first actual integer output, including a wrong integer, never expected13. NULL/noninteger means explicit zero-tick dependent abstention; no guessed integer, resend or numerical repair.','numeric_scope':'P9 exact:6+7, then actual_integer-5. Expected13/8 are auditor-only. No wait36, reteaching, moved geometry, extra reader or rescue.','Native_executed':False,'expected_values_are_auditor_only_not_literal':True,'supersedes_unexecuted_wrong_draft':'PANEL_HEREDADO_12_PI10_R02_PASOS.json (independent9-1 was a corrected instruction, never executed)'}
 out=H/'PANEL_HEREDADO_12_PI10_R03_PASOS.json';put(out,value);print(json.dumps({'file':str(out),'sha256':sha(out),'finite_bound':sum(s['max_ticks']for s in steps),'Native':0}))
if __name__=='__main__':main()
