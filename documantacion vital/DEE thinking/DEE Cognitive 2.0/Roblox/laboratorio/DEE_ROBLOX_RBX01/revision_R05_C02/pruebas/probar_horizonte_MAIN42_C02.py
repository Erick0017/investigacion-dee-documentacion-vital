"""Actual production preflight AST target block, no run/Native/MCP execution."""
from pathlib import Path
import ast,datetime,hashlib,json,types
ROOT=Path(__file__).resolve().parents[1];path=ROOT/'control/orquestar_C02.py';tree=ast.parse(path.read_text('utf8'))
run=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='run')
def assigns(node,name):return isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in node.targets)
start=next(i for i,n in enumerate(run.body)if assigns(n,'scope_maximum'))
end=next(i for i,n in enumerate(run.body[start:],start)if assigns(n,'config'))
block=compile(ast.fix_missing_locations(ast.Module(body=run.body[start:end],type_ignores=[])),str(path)+':actual_target_guard','exec')
def need(ok,message):
    if not ok:raise ValueError(message)
def evaluate(maximum,target,suspend,world):
    scope={'max_cycles':maximum};before=dict(scope)
    env={'scope':scope,'args':types.SimpleNamespace(target_cycles=target,suspend_after=suspend,world_id=world),'need':need,'WORLD_ID':'RBX01_R05_C02_V1'}
    exec(block,env);assert scope==before;return env['maximum'],env['scope_maximum']
checks=[]
assert evaluate(48,42,14,'RBX01_R05_C02_V1')==(42,48);checks.append('Actual MAIN guard targets42 with Native supply48 unchanged')
assert evaluate(4,None,2,'RBX01_R05_C02_DEV4')==(4,4);checks.append('Existing DEV4/2 stays identical without target override')
for args in((48,49,14,'RBX01_R05_C02_V1'),(4,4,2,'RBX01_R05_C02_DEV4'),(48,42,16,'RBX01_R05_C02_V1')):
    try:evaluate(*args)
    except ValueError:pass
    else:raise AssertionError('Illegal target override accepted')
checks.append('Target above scope, DEV override and unapproved42/16 pair refused')
assert evaluate(48,48,16,'RBX01_R05_C02_V1')==(48,48);checks.append('Historical48/16 remains explicitly reproducible')
cmp_path=ROOT/'control/orquestar_comparador_C02.py';cmp_tree=ast.parse(cmp_path.read_text('utf8'))
guard=next(n for n in ast.walk(cmp_tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='need'and
           any(isinstance(a,ast.Constant)and isinstance(a.value,str)and 'Same prospective42/14'in a.value for a in n.args))
expression=compile(ast.Expression(guard.args[0]),str(cmp_path)+':actual_comparator_target_guard','eval')
assert eval(expression,{'args':types.SimpleNamespace(world_id='RBX01_R05_C02_V1',max_cycles=42,suspend_after=14),'WORLD_ID':'RBX01_R05_C02_V1'})
assert not eval(expression,{'args':types.SimpleNamespace(world_id='RBX01_R05_C02_V1',max_cycles=42,suspend_after=16),'WORLD_ID':'RBX01_R05_C02_V1'})
checks.append('Actual comparator preflight uses same prospective42/14 horizon')
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
report={'scope':'PRODUCTION_AST_PREFLIGHT_ONLY','tests':len(checks),'checks':checks,'Native_imports':0,'Native_ticks':0,'MCP_calls':0,
        'sources_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(path,cmp_path)}}
out=ROOT/'pruebas'/('HORIZONTE_MAIN42_'+stamp+'.json');out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps({'report':str(out),**report}))
