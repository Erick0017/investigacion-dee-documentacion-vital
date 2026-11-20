"""Technical preflight only; --help never starts a native trajectory."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from common import put,sha

old_path=ROOT/'resultados/clean_preliminary/attempt_02/life.py'
old=old_path.read_text(encoding='utf-8')
new=(ROOT/'src/life.py').read_text(encoding='utf-8')
def functions(source):
    return {node.name:node for node in ast.parse(source).body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))}
of,nf=functions(old),functions(new)
checks={name:{'AST_equal':ast.dump(node,include_attributes=False)==ast.dump(nf[name],include_attributes=False),
              'function_source_exact':ast.get_source_segment(old,node)==ast.get_source_segment(new,nf[name])}
        for name,node in of.items() if name!='main'}
assert checks and all(all(row.values()) for row in checks.values())
plan=json.loads((ROOT/'configuraciones/clean_reproduction_plan.json').read_text(encoding='utf-8'))
env=dict(os.environ,PYTHONUTF8='1',PYTHONNOUSERSITE='1',PYTHONDONTWRITEBYTECODE='1')
env.pop('PYTHONPATH',None);env.pop('PYTHONHOME',None)
rows=[]
for test in plan['commands']:
    script=next(value.replace('{root}',str(ROOT)) for value in test['argv'] if value.endswith('.py'))
    argv=[sys.executable,'-I','-B','-X','utf8',script,'--help']
    completed=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8',env=env,timeout=30)
    rows.append({'id':test['id'],'argv':argv,'exit_code':completed.returncode,
                 'stdout':completed.stdout,'stderr':completed.stderr})
result={'schema':'CPC6.clean-cli-preflight.v1','native_trajectories_started':0,
        'life_scientific_function_comparisons':checks,'commands':rows,
        'old_life_sha256':sha(old_path),'current_life_sha256':sha(ROOT/'src/life.py'),
        'reference_replay_sha256':sha(ROOT/'src/reference_replay.py'),
        'plan_sha256':sha(ROOT/'configuraciones/clean_reproduction_plan.json'),
        'scope':'Only CLI bootstrap and external evidence-index base changed. Frozen run/summarize function source is byte-exact.',
        'status':'VERIFIED' if all(row['exit_code']==0 for row in rows) else 'ERROR'}
put(Path(__file__).with_name('PREFLIGHT_REPORT.json'),result)
print(json.dumps(result,ensure_ascii=False,indent=2))
assert result['status']=='VERIFIED'
