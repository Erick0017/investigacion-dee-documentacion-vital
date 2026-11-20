"""Actual proposed dispatcher AST with fake plugin, never app/DEE/Native."""
from pathlib import Path
import ast,hashlib,json,sys,types
P=Path(__file__).resolve().parents[1];H=P/'codigo/FUENTES_HOOKS_PI06_R01';checks=[];calls=[]
def test(name,condition):
 if not condition:raise AssertionError(name)
 checks.append({'name':name,'passed':True})
plugin=types.ModuleType('capacidades.pi06_organizacion_R01');plugin.VERSION='FAKE_ONLY'
def literal(row):
 if row!={'modo':'eci01-pi06-fiplus','izquierda':14,'derecha':3,'captura':'normal'}:raise ValueError('Fake exact contract rejects unknown fields/modes')
 calls.append(('literal',row.copy()))
def validate(a,row):literal(row);calls.append(('validate',a))
def dispatch(a,row,*,actuator='closed',directory=None):
 literal(row);calls.append(('dispatch',actuator,str(directory)));return {'fake_result':True}
plugin.validate_literal=literal;plugin.validate=validate;plugin.dispatch=dispatch;plugin.uncertain=lambda a:True
package=types.ModuleType('capacidades');package.pi06_organizacion_R01=plugin
sys.modules['capacidades']=package;sys.modules[plugin.__name__]=plugin
class OldBase:
 def validate(self,payload):return 'OLD_VALIDATE_UNCHANGED'
 def execute(self,payload):return 'OLD_EXECUTE_UNCHANGED'
owner_ast=ast.parse((H/'app/mundo_genesis_apd05.py').read_bytes())
cls=next(n for n in owner_ast.body if isinstance(n,ast.ClassDef))
ns={'NativeWorld':OldBase,'Path':Path,'hashlib':hashlib}
exec(compile(ast.Module(body=[cls],type_ignores=[]),'ACTUAL_PROPOSED_OWNER_AST','exec'),ns)
world=ns['GenesisNativeWorld']();world.a=object();world.work_directory=Path('FAKE_ONLY');world.backend='mente_unificada';mutations=[];world.before_mutation=mutations.append
row={'modo':'eci01-pi06-fiplus','izquierda':14,'derecha':3,'captura':'normal'};payload={'operacion':'sesion','situaciones':[row],'actuador':'closed','retorno':'omit'}
world.validate(payload);result=world.execute(payload)
test('new_prefix_validate_and_dispatch_signature',any(x[0]=='validate'for x in calls)and('dispatch','closed','FAKE_ONLY')in calls)
test('result_not_replaced_by_owner',result=={'version':'FAKE_ONLY','rows':[{'fake_result':True}]})
test('explicit_mutation_instrument_marker_only',mutations==['PI06_DECLARED_FINITE_ORGANIZATION_PROTOCOL'])
test('old_non_session_fallback_preserved',world.validate({'operacion':'guardar'})=='OLD_VALIDATE_UNCHANGED'and world.execute({'operacion':'guardar'})=='OLD_EXECUTE_UNCHANGED')
try:world.validate({'operacion':'sesion','situaciones':[row,row]})
except ValueError:test('reject_mixed_or_two_ECI01_rows',True)
else:raise AssertionError('Mixed protocol allowed')
test('uncertainty_is_propagated',world.external_uncertainty()is True)
queue_ast=ast.parse((H/'app/cola_local.py').read_bytes());fn=next(n for n in queue_ast.body if isinstance(n,ast.FunctionDef)and n.name=='validate_request')
qns={'CONTROL':{'pausar','reanudar','guardar','detener','exportar'},'MATERIAL':{'sesion','avanzar'},
 'canonical':lambda value:json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)}
exec(compile(ast.Module(body=[fn],type_ignores=[]),'ACTUAL_PROPOSED_QUEUE_AST','exec'),qns)
qns['validate_request'](payload);test('queue_reaches_fixed_new_plugin',calls[-1][0]=='literal')
for bad in({'modo':'eci01-pi06-unknown'},dict(row,target='expected_answer')):
 try:qns['validate_request']({'operacion':'sesion','situaciones':[bad]})
 except ValueError:test('reject_unsupported_literal_'+str(len(checks)),True)
 else:raise AssertionError('Unknown protocol field accepted')
qns['validate_request']({'operacion':'avanzar','ticks':4096});test('old_bounded_advance_validation_remains',True)
test('no_dee_or_app_modules_imported',not any(name=='app'or name.startswith(('app.','dee_thinking'))for name in sys.modules))
proof={'schema':'DEE.PI06.dispatcher_fake_tests.R01','checks':checks,'passed':len(checks),'Native_executed':False,
 'scope':'Exact proposed owner class and queue validator AST, fake plugin/data only. Does not validate physical passivity or the real PI06 plugin.',
 'files':{name:hashlib.sha256((H/name).read_bytes()).hexdigest()for name in('app/mundo_genesis_apd05.py','app/cola_local.py')}}
out=P/'control/HOOKS_PI06_PRUEBAS_PURAS_R01.json'
with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'proof':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'passed':len(checks),'Native_executed':False}))
