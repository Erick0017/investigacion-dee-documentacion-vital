"""Final12h prospective deadline/import-only versions; never starts a runtime."""
from pathlib import Path
import ast,hashlib,json
ROOT=Path(__file__).resolve().parent.parent;C=ROOT/'comparadores';P=ROOT/'prototipo/NATIVE_LIMPIO_R07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def emit(p,s):
    if p.exists():raise ValueError('Preserve existing version:'+str(p))
    compile(s,str(p),'exec');p.write_text(s,encoding='utf-8',newline='\n')
    return{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def named(s,t):return{n.name:ast.dump(n,include_attributes=False)for n in ast.parse(s).body if isinstance(n,t)}
def public_rules(s):
    for n in ast.parse(s).body:
        if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PUBLIC_RULES'for t in n.targets):return ast.literal_eval(n.value)
def main():
    files=[C/'cliente_modelo_v3_R04.py',C/'servidor_modelo_v3_R04.py',C/'backends_v3_R04.py',ROOT/'control/runner_comparador_v3_R04.py',P/'ejecutar_piloto_R07_preparado_R03.py']
    before={str(p):sha(p)for p in files};outputs=[]
    old=files[0].read_text('utf-8');new=old.replace('STOP_NEW_CALLS=1794870000','STOP_NEW_CALLS=1794880800').replace('2026-11-16 23:00 UTC','2026-11-17 02:00 UTC')
    if named(old,ast.FunctionDef)!=named(new,ast.FunctionDef)or named(old,ast.ClassDef)!=named(new,ast.ClassDef):raise ValueError('Client policy changed')
    outputs.append(emit(C/'cliente_modelo_v3_R05.py',new))
    old=files[1].read_text('utf-8');new=old.replace('1794874020','1794884820').replace('1794870000','1794880800')
    new=new.replace('2026-11-17 00:07 UTC','2026-11-17 03:07 UTC').replace('2026-11-16 23:00 UTC','2026-11-17 02:00 UTC')
    new=new.replace('V3_R04','V3_R05').replace('MODEL.V3.R04','MODEL.V3.R05')
    outputs.append(emit(C/'servidor_modelo_v3_R05.py',new))
    old=files[2].read_text('utf-8');new=old.replace('cliente_modelo_v3_R04','cliente_modelo_v3_R05')
    if public_rules(old)!=public_rules(new):raise ValueError('Public prompt changed')
    a=named(old,ast.ClassDef);b=named(new,ast.ClassDef)
    for n in('ProgrammedBackend','ConventionalAIBackend','PersistedLocalPolicy'):
        if a[n]!=b[n]:raise ValueError('Reference decision policy changed')
    outputs.append(emit(C/'backends_v3_R05.py',new))
    old=files[3].read_text('utf-8');new=old.replace('world_comprimido_v3_R04','world_comprimido_v3_R05').replace('backends_v3_R04','backends_v3_R05')
    new=new.replace('1794870000','1794880800').replace('1794874020','1794884820').replace('2026-11-16 23:00 UTC','2026-11-17 02:00 UTC')
    outputs.append(emit(ROOT/'control/runner_comparador_v3_R05.py',new))
    old=files[4].read_text('utf-8');new=old.replace('1794874020','1794884820').replace('1794870000','1794880800').replace('owner_support_v3_R04.py','owner_support_v3_R05.py').replace('after23:00UTC','after02:00UTCNov17')
    outputs.append(emit(P/'ejecutar_piloto_R07_preparado_R05.py',new))
    for p,h in before.items():
        if sha(p)!=h:raise ValueError('R04 source altered')
    record={'schema':'DEE.R07.final_prospective_deadline_sources.R05','originals_preserved':before,'outputs':outputs,
      'start_unchanged_utc':'2026-11-16T15:07:00Z','last_new_utc':'2026-11-17T02:00:00Z','hard_close_utc':'2026-11-17T03:07:00Z',
      'maximum_campaign_hours':12,'no_further_extension_implicit':True,
      'model_policy_prompt_grammar_weights_and_options_unchanged':True,
      'global_quota_unchanged_reused':'comparadores/CUOTA_LLM_V3.json,160calls',
      'reference_horizon_unchanged':'29..46,18new','pilot_scope_unchanged':'fresh1/cap3,Source991187/seq56',
      'Native_calls':0,'model_calls':0,'MCP_calls':0,'active_Main_not_touched':True,
      'activation':'Only after Root/P closed-boundary lease migration R05; prior files and receipts remain historical.'}
    p=ROOT/'control/REFERENCIAS_PILOTO_LEASE_R05.json'
    if p.exists():raise ValueError('Preserve prior witness')
    p.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(record,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
