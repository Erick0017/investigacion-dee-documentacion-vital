"""Compile only pure validation functions from actor TEXT; no Native import."""
from pathlib import Path
import ast,importlib.util,json,re,sys,unittest
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('_clean_live_contract',HERE/'ejecutar_native_limpio.py');driver=importlib.util.module_from_spec(spec);sys.modules[spec.name]=driver;spec.loader.exec_module(driver)
tree=ast.parse((ROOT/'native/bundle/rbx06_native_integral.py').read_text(encoding='utf8'))
constants={'Q1','Q2','FEEDBACK','STATE','FUNCTION','MODES'};functions={'need','canonical','validate_literal','validate_tool'}
nodes=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id in constants for x in n.targets)or isinstance(n,ast.FunctionDef)and n.name in functions]
namespace={'json':json,'re':re};exec(compile(ast.Module(body=nodes,type_ignores=[]),'actor_pure_validation_TEXT','exec'),namespace)
def sensors(signal=-1,stock=200):
    return dict(station=0,stage=0,contact=0,inventoryKey=False,inventoryResource=False,queryAvailable=True,
        stationSignal=signal,permissionStock=stock,publicContactCode=0,lastFailure=False,numberAPresent=False,
        codeBPresent=False,numberAVersion=0,codeBCurrent=False,goalDelivery=True)
def obs(seq=1,phase='QUERY_CHOICE',signal=-1,stock=200):
    return dict(protocol='DEE.RBX.Connector.R01',namespace='R06_NATIVE_CLEAN/scene_01/CTRL1',sessionId='S',seq=seq,
        observationId='OBS'+str(seq),phase=phase,worldTimeMs=0,sampleTimeMs=0,previousActionId=None if seq==1 else'Q1_REAL_ID',sensors=sensors(signal,stock))
class Tests(unittest.TestCase):
    def test_q1_exact_actual_actor_abi(self):
        converted=driver.native_observation(obs());self.assertEqual(converted['seq'],9)
        context=dict(session_id='S',sequence=9,observation_id='OBS1',operation_id='OP1',mode='LIVE_NATIVE')
        namespace['validate_literal'](dict(modo=namespace['Q1'],payload={'observation':converted},context=context))
    def test_q2_preserves_real_previous_id_paid_panel(self):
        converted=driver.native_observation(obs(2,'ROUTE_CHOICE',1,199));self.assertEqual(converted['seq'],10)
        self.assertEqual(converted['previousActionId'],'Q1_REAL_ID')
        context=dict(session_id='S',sequence=10,observation_id='OBS2',operation_id='OP2',mode='LIVE_NATIVE')
        namespace['validate_literal'](dict(modo=namespace['Q2'],payload={'observation':converted},context=context))
    def test_no_extra_or_missing_native_sensor_keys(self):
        converted=driver.native_observation(obs());converted['sensors']['expected_route']=0
        context=dict(session_id='S',sequence=9,observation_id='OBS1',operation_id='OP1',mode='LIVE_NATIVE')
        with self.assertRaises(Exception):namespace['validate_literal'](dict(modo=namespace['Q1'],payload={'observation':converted},context=context))
    def test_no_native_runtime_imported(self):
        self.assertFalse(any(x=='dee_thinking'or x.startswith('dee_thinking.')for x in sys.modules))
    def test_sdk_preserves_lua_array_types_via_full_json(self):
        code=driver.typed_result_code('return {pose={1,2,3},zero=0,absent=false}')
        self.assertIn('JSONEncode(r06TypedValue())',code)
        self.assertEqual(code.count('return {pose={1,2,3},zero=0,absent=false}'),1)
        self.assertNotIn('table.sort',code)
if __name__=='__main__':unittest.main()
