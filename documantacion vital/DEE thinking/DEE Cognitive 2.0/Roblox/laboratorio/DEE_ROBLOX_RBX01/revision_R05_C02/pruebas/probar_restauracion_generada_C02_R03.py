"""Read actual closed DEV checkpoint + actual production code generators.

Evaluates only the Python string-construction AST expression, not its containing
run function and never Lua/Native/MCP. Verifies real ABI names across persisted
checkpoint, Estado.apply and Bridge.resumeCheckpoint. Lua parse remains Root's
separate Studio verification, explicitly not claimed by these lexical fixtures.
"""
from pathlib import Path
import ast,datetime,hashlib,importlib.util,json,re,sys,types
ROOT=Path(__file__).resolve().parents[1]
checkpoint=ROOT/'evidencia/DEV_SELLADO_R02/PAREJA_C02/WORLD_CHECKPOINT.json'
closed=ROOT/'evidencia/DEV_SELLADO_R02/SELLADO_VINCULO_C02.json'
world=json.loads(checkpoint.read_text('utf8'));seal=json.loads(closed.read_text('utf8'))
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');folder=ROOT/'pruebas'/('RESTORE_GENERATOR_R03_FIXTURE_'+stamp);folder.mkdir()
spec=importlib.util.spec_from_file_location('_restore_strings_R03',ROOT/'control/transporte_checkpoint_C02_R02.py')
t=importlib.util.module_from_spec(spec);sys.modules[spec.name]=t;spec.loader.exec_module(t)
expected={k:world[k]for k in('world_id','scenario_sha256','native_life_id','native_tick','checkpoint_id')}
expected.update(checkpoint_sha256=seal['bound_checkpoint_sha256'],owner_closed=True,bridge_quiescent=True)
raw=json.dumps(world,ensure_ascii=False,separators=(',',':'),allow_nan=False);count=(len(raw)+23999)//24000
checks=[];sources={}
for name in('orquestar_C02.py','orquestar_comparador_C02.py'):
    path=ROOT/'control'/name;text=path.read_text('utf8');tree=ast.parse(text)
    candidates=[n.value for n in ast.walk(tree)if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='code'for x in n.targets)
                and any(isinstance(v,ast.Constant)and isinstance(v.value,str)and 'RBX01Restore_C02:Invoke'in v.value for v in ast.walk(n.value))]
    assert len(candidates)==1
    expression=compile(ast.Expression(candidates[0]),str(path)+':actual_restore_string_expression','eval')
    generated=eval(expression,{'json':json,'count':count,'expected':expected,'long_string':t.long_string,'u':types.SimpleNamespace(long_string=t.long_string)})
    assert 'for i=0,'+str(count-1)+' do 'in generated
    assert not re.search(r'\d(?:do|then|end)\b',generated)
    assert 'RBX01Restore_C02:Invoke'in generated and str(world['native_tick'])in generated
    target=folder/(name.replace('.py','')+'_RESTORE_GENERADO.luau');target.write_text(generated+'\n',encoding='utf8')
    checks.append(name+': actual AST-generated full restore expression separates numeric loop limit from do')
    sources[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
state=(ROOT/'mundo/EstadoPareja_C02.luau').read_text('utf8');bridge=(ROOT/'mundo/Bridge_mailbox_C02.luau').read_text('utf8')
resume=bridge[bridge.index('function Bridge:resumeCheckpoint'):]
assert set(('session_id','server_id'))<=world['bridge'].keys()
assert 'self.sessionId=context.session_id' in resume and 'self.serverInstanceId=context.server_id'in resume
assert 'context.server_instance_id'not in resume
assert 'serverInstanceId=state.bridge.server_id'in state and 'sessionId=state.bridge.session_id'in state
checks.append('Actual DEV bridge session_id/server_id cross Estado.apply and Bridge.resumeCheckpoint without alias')
assert 'checkpointId=context.resumeTransport.checkpointId'in resume and 'checkpointSha256=context.resumeTransport.checkpointSha256'in resume
checks.append('Actual resume checkpoint ID/hash body uses only explicit persisted transport context')
report={'scope':'ACTUAL_FROZEN_DEV_FILES_AND_PRODUCTION_PYTHON_STRING_AST_ONLY','tests':len(checks),'checks':checks,
        'checkpoint':str(checkpoint),'checkpoint_sha256':hashlib.sha256(checkpoint.read_bytes()).hexdigest(),'Native_tick_in_existing_checkpoint':world['native_tick'],
        'restore_chunks':count,'source_files_sha256':sources,'fixture':str(folder),'Native_imports':0,'Native_ticks_executed':0,'MCP_calls':0,
        'Lua_parse_or_execution':False,'limitation':'Static ABI and real generated-source checks. Root separately compiles/applies this in fresh Studio before owner starts.'}
out=ROOT/'pruebas'/('RESTORE_GENERATOR_R03_'+stamp+'.json');out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'report':str(out),**report},ensure_ascii=False))
