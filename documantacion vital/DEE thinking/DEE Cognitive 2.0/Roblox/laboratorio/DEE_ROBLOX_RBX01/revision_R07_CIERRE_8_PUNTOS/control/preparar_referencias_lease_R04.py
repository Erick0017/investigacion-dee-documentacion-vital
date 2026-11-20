"""Prospective lease-only source versions. No service, model, SDK or Native calls."""
from pathlib import Path
import ast
import hashlib
import json

ROOT=Path(__file__).resolve().parent.parent
C=ROOT/'comparadores';P=ROOT/'prototipo/NATIVE_LIMPIO_R07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def create(path,s):
 if path.exists():raise ValueError('NO_OVERWRITE:'+str(path))
 compile(s,str(path),'exec');path.write_text(s,encoding='utf-8',newline='\n')
 return{'path':str(path),'sha256':sha(path),'bytes':path.stat().st_size}
def assignment(s,name):
 for item in ast.parse(s).body:
  if isinstance(item,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in item.targets):return ast.literal_eval(item.value)
 raise ValueError('Required assignment:'+name)
def functions(s):
 return{n.name:ast.dump(n,include_attributes=False)for n in ast.parse(s).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
def main():
 originals=[C/'cliente_modelo_v3.py',C/'servidor_modelo_v3.py',C/'backends_v3.py',ROOT/'control/runner_comparador_v3_R03.py',P/'ejecutar_piloto_R07_preparado_R02.py']
 before={str(p):sha(p)for p in originals};outputs=[]
 old=originals[0].read_text('utf-8');client=old.replace('STOP_NEW_CALLS=1794859200  #2026-11-16 20:00 UTC','STOP_NEW_CALLS=1794870000  #2026-11-16 23:00 UTC; prospective renewal before old cutoff')
 if assignment(client,'STOP_NEW_CALLS')!=1794870000:raise ValueError('Exact new client cutoff')
 if functions(client)!=functions(old):raise ValueError('Model grammar/request/validation changed beyond lease')
 outputs.append(create(C/'cliente_modelo_v3_R04.py',client))
 old=originals[1].read_text('utf-8')
 server=old.replace('HARD_FINISH=1794863220','HARD_FINISH=1794874020').replace('STOP_NEW_CALLS=1794859200','STOP_NEW_CALLS=1794870000')
 server=server.replace('2026-11-16 21:07 UTC, prospective R07 finish.','2026-11-17 00:07 UTC, prospectively renewed R07 finish.')
 server=server.replace('2026-11-16 20:00 UTC; enforced by R07 client.','2026-11-16 23:00 UTC; enforced by R07 R04 client.')
 server=server.replace('tmp_ollama_V3','tmp_ollama_V3_R04').replace('SERVIDOR_MODELO_V3.jsonl','SERVIDOR_MODELO_V3_R04.jsonl')
 server=server.replace('ollama_V3.stop','ollama_V3_R04.stop').replace('ollama_isolated_V3_','ollama_isolated_V3_R04_')
 server=server.replace('R07.CIERRE8.MODEL.V3','R07.CIERRE8.MODEL.V3.R04')
 outputs.append(create(C/'servidor_modelo_v3_R04.py',server))
 old=originals[2].read_text('utf-8');backend=old.replace('from cliente_modelo_v3 import','from cliente_modelo_v3_R04 import').replace("with_name('cliente_modelo_v3.py')","with_name('cliente_modelo_v3_R04.py')")
 if assignment(backend,'PUBLIC_RULES')!=assignment(old,'PUBLIC_RULES'):raise ValueError('Public prompt changed')
 for oldnode,newnode in zip(ast.parse(old).body,ast.parse(backend).body):
  if isinstance(oldnode,ast.ClassDef)and oldnode.name in('ProgrammedBackend','ConventionalAIBackend'):
   if ast.dump(oldnode,include_attributes=False)!=ast.dump(newnode,include_attributes=False):raise ValueError('Reference policy changed')
 outputs.append(create(C/'backends_v3_R04.py',backend))
 old=originals[3].read_text('utf-8');runner=old.replace('from world_comprimido_v3_R03 import CompressedWorld','from world_comprimido_v3_R04 import CompressedWorld').replace('from backends_v3 import create_backend','from backends_v3_R04 import create_backend')
 runner=runner.replace('CUTOFF=1794859200','CUTOFF=1794870000').replace('HARD_CLOSE=1794863220','HARD_CLOSE=1794874020')
 runner=runner.replace('2026-11-16 20:00 UTC','2026-11-16 23:00 UTC')
 outputs.append(create(ROOT/'control/runner_comparador_v3_R04.py',runner))
 old=originals[4].read_text('utf-8');pilot=old.replace('CUTOFF=1794863220;LAST_NEW=1794859200','CUTOFF=1794874020;LAST_NEW=1794870000')
 pilot=pilot.replace("ROOT/'native/owner_support_v3.py'","ROOT/'native/owner_support_v3_R04.py'")
 pilot=pilot.replace("default='DEEConnector_PILOTO_OTRO_MAPA_R07.rbxlx'","default='PILOTO_R07.rbxlx'")
 pilot=pilot.replace('after20:00UTC','after23:00UTC')
 outputs.append(create(P/'ejecutar_piloto_R07_preparado_R03.py',pilot))
 for p,h in before.items():
  if sha(p)!=h:raise ValueError('Preserved source changed:'+p)
 record={'schema':'DEE.R07.prospective_lease_only_versions.R04','originals':before,'outputs':outputs,
  'start_unchanged_utc':'2026-11-16T15:07:00Z','new_last_start_utc':'2026-11-16T23:00:00Z',
  'new_hard_close_utc':'2026-11-17T00:07:00Z','prior_main_live_lease_untouched':True,
  'model_policy_and_phase_grammar_unchanged':True,'model_weights_unchanged':True,
  'quota_file_reused_without_reset':'comparadores/CUOTA_LLM_V3.json','global_model_limit_unchanged':160,
  'new_server_lifecycle':'comparadores/SERVIDOR_MODELO_V3_R04.jsonl','server_stop':'comparadores/ollama_V3_R04.stop',
  'reference_horizon_unchanged':'global29..46,18new','pilot_horizon_unchanged':'fresh1episode; ScopeMax3',
  'pilot_expected_place':'PILOTO_R07.rbxlx','pilot_scene_content_sha256':'ef39c6bf193c2f26386384e564ffcb16ab2e93c29f7b8a9e071431781dbcfd92',
  'Native_calls':0,'model_calls':0,'MCP_calls':0,
  'activation_requires':'Root closes old service if active, and P validates/migrates the role0/closed boundary lease before opening an owner. No runtime activation by this source preparation.'}
 create_record=ROOT/'control/REFERENCIAS_PILOTO_LEASE_R04.json'
 if create_record.exists():raise ValueError('Preserve lease preparation witness')
 create_record.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(record,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
