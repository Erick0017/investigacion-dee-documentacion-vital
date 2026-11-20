"""R02 source/target coherence only: no Native imports, HTTP, owner or MCP."""
from pathlib import Path
import ast,datetime,hashlib,json,types
ROOT=Path(__file__).resolve().parents[1];checks=[]
sources={name:(ROOT/name).read_text('utf8')for name in('control/orquestar_C02_R02.py','control/orquestar_comparador_C02_R02.py',
         'puente/run_live_native_C02_R02.py','fuentes/rbx02_owner_support_C02_R02.py')}
for name,text in sources.items():ast.parse(text)
checks.append('All four new R02 orchestration/launcher/support modules parse')
launcher=sources['puente/run_live_native_C02_R02.py']
for value in('RBX02_NATIVE_SCOPE_C02_R02.json','CODE_SCOPE_C02_R02.json','fixed_native_scope.C02.R02',
              'rbx02_adapter_C02_R02.py','rbx02_import0_C02_R02.py','rbx02_owner_support_C02_R02.py',"life.endswith('_RBX01_C02_MAIN_R02')"):
    assert value in launcher,value
checks.append('Launcher pins unique R02 scope/code/importer/adapter/host/life')
native=sources['control/orquestar_C02_R02.py'];tree=ast.parse(native);run=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='run')
def assigns(node,name):return isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in node.targets)
start=next(i for i,n in enumerate(run.body)if assigns(n,'scope_maximum'));end=next(i for i,n in enumerate(run.body[start:],start)if assigns(n,'config'))
def need(ok,msg):
    if not ok:raise ValueError(msg)
env={'scope':{'max_cycles':48},'args':types.SimpleNamespace(target_cycles=36,suspend_after=12,world_id='RBX01_R05_C02_R02'),
     'need':need,'WORLD_ID':'RBX01_R05_C02_R02'}
exec(compile(ast.Module(body=run.body[start:end],type_ignores=[]),'<R02_actual_target_guard>','exec'),env)
assert env['maximum']==36 and env['scope_maximum']==48;checks.append('Actual R02 target guard selects36/12 without changing Native supply48')
assert 'control/studio_mailbox_relay_C02_R02.py'in native and 'puente/run_live_native_C02_R02.py'in native
assert 'DEE_RBX01_C02_R02_PROGRAMMED.rbxlx'in sources['control/orquestar_comparador_C02_R02.py']
checks.append('New R02 Studio/relay/launcher routing is separate from R01')
support=sources['fuentes/rbx02_owner_support_C02_R02.py']
assert 'cutoff_epoch - 1800'in support and 'cutoff_epoch - 3600'not in support
assert "system/'app/servicio_eventos_C02.py'"in support and 'app/HOST_C02.json'in support
assert 'AGGREGATE = 200000'in support and 'MAX_WORLDS = 6'in support;checks.append('R02 prospective lastQ110:00 reuses exact event host and shared200000/6 budget')
def ledger_ast(text):
    c=next(n for n in ast.parse(text).body if isinstance(n,ast.ClassDef)and n.name=='TickLedger')
    c.body=[n for n in c.body if not(isinstance(n,ast.Expr)and isinstance(n.value,ast.Constant)and isinstance(n.value.value,str))]
    return ast.dump(c,include_attributes=False)
assert ledger_ast(support)==ledger_ast((ROOT/'fuentes/rbx02_owner_support_C02.py').read_text('utf8'));checks.append('Shared ledger implementation AST unchanged acrossR01/R02')
scope=json.loads((ROOT/'protocolo/CODE_SCOPE_C02.json').read_text('utf8'))
for relative,expected in scope['source_files_sha256'].items():assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==expected,relative
checks.append('All five sealed original R01 Native sources still hash-identical')
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
report={'scope':'STATIC_PRODUCTION_SOURCES_AND_PREFLIGHT_AST_ONLY','tests':len(checks),'checks':checks,
        'Native_imports':0,'Native_ticks':0,'MCP_calls':0,'HTTP_requests':0,
        'sources_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()for name in sources}}
out=ROOT/'pruebas'/('INFRA_R02_'+stamp+'.json');out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps({'report':str(out),**report}))
