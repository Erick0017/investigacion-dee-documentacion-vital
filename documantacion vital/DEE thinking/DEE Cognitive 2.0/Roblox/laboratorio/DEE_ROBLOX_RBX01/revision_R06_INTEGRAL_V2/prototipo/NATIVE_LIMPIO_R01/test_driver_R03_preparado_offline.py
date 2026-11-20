"""Pure AST/string/XML contract fixtures; NEVER preflight a real Native root."""
from pathlib import Path
import ast, hashlib, importlib.util, json, sys, unittest
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
SOURCE=HERE/'ejecutar_native_limpio_R03_preparado.py'
SPEC=importlib.util.spec_from_file_location('_r03_driver_prepared_contract',SOURCE)
driver=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(driver)
tree=ast.parse(SOURCE.read_text('utf8'))

def modules():
    root=ET.fromstring((HERE/'DEEConnector_NATIVE_LIMPIO_R01.rbxlx').read_bytes());result={}
    for item in root.iter('Item'):
        if item.get('class')!='ModuleScript':continue
        name=item.find("Properties/string[@name='Name']");source=item.find("Properties/ProtectedString[@name='Source']")
        if name is not None and source is not None:result[name.text]=source.text or''
    return result

def extracted_deliver():
    # Compile only the pure wire-building nested function. Its MCP is an inert
    # test double, not the SDK/client/owner, and never controls a real body.
    fn=next(n for n in ast.walk(tree)if isinstance(n,ast.FunctionDef)and n.name=='deliver')
    calls=[];acks=[]
    def mcp(code,label):
        calls.append((code,label))
        if label.startswith('deliver_'):
            argument=code.split('return a:deliverAction(',1)[1][:-1]
            raw=json.loads(argument)
            if not isinstance(raw,str):raise AssertionError('API must receive raw JSON string')
            wire=json.loads(raw)
            return {'actionId':wire['actionId'],'operationId':wire['operationId'],'executionStatus':'EXECUTED'}
        return {}
    namespace={'need':driver.need,'literal':driver.literal,'HEADER':driver.HEADER,'json':json,
               'mcp':mcp,'acks':acks,'session_id':'FIXTURE_SESSION'}
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'isolated_wire_builder_AST_only','exec'),namespace)
    return namespace['deliver'],calls,acks

class Contract(unittest.TestCase):
    def test_actual_exported_API_requires_string(self):
        source=modules()['Main']
        self.assertIn('function Agent:deliverAction(raw)',source)
        self.assertIn('type(raw)=="string"and #raw<=65536',source)

    def test_actual_wire_argument_is_string_not_H_JSONDecode(self):
        deliver,calls,acks=extracted_deliver()
        deliver({'action':'EXIT_0','nativeTick':955215,'null':False},'FIXTURE_REAL_RESULT_ID',
                {'namespace':'R06_NATIVE_CLEAN/scene_01/CTRL1','seq':2,'observationId':'FIXTURE_OBS'})
        code,label=calls[0]
        self.assertIn('a:deliverAction(',code);self.assertNotIn('H:JSONDecode(',code)
        raw=json.loads(code.split('return a:deliverAction(',1)[1][:-1]);self.assertIsInstance(raw,str)
        wire=json.loads(raw);self.assertEqual(wire['action']['name'],'EXIT_0')
        self.assertEqual(wire['actionId'],wire['operationId']);self.assertEqual(len(acks),1)
        self.assertEqual([x[1]for x in calls],['deliver_0_once','confirm_0_once'])

    def test_null_and_zero_are_not_replaced(self):
        deliver,calls,_=extracted_deliver()
        deliver({'action':'SAFE_WAIT','nativeTick':0,'null':True},'FIXTURE_NULL',
                {'namespace':'R06_NATIVE_CLEAN/scene_01/CTRL1','seq':1,'observationId':'FIXTURE_ZERO'})
        raw=json.loads(calls[0][0].split('return a:deliverAction(',1)[1][:-1]);wire=json.loads(raw)
        self.assertEqual(wire['action']['nativeTick'],0);self.assertIs(wire['action']['null'],True)
        self.assertEqual(wire['action']['name'],'SAFE_WAIT')

    def test_unknown_action_has_no_MCP_attempt(self):
        deliver,calls,_=extracted_deliver()
        with self.assertRaises(ValueError):
            deliver({'action':'CHOOSE_EXPECTED_ROUTE','nativeTick':1,'null':False},'X',
                    {'namespace':'N','seq':1,'observationId':'O'})
        self.assertEqual(calls,[])

    def test_LF_normalized_sources_match_unchanged_manifest(self):
        expected=json.loads((HERE/'MANIFIESTO_LIVE_ESCENA_R01.json').read_text('utf8'))['modules_sha256']
        for name in('Main','BackendBinding','LiveAdapters_R01'):
            text=modules()[name]
            self.assertEqual(hashlib.sha256(text.replace('\r\n','\n').encode()).hexdigest(),expected[name])
            crlf=text.replace('\r\n','\n').replace('\n','\r\n')
            self.assertEqual(hashlib.sha256(crlf.replace('\r\n','\n').encode()).hexdigest(),expected[name])
        self.assertIn('Source:gsub(string.char(13)..string.char(10),string.char(10))',SOURCE.read_text('utf8'))

    def test_fresh_guard_rejects_current_tick_without_opening_files(self):
        preflight=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='preflight')
        call=next(n for n in ast.walk(preflight)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='need'and len(n.args)>1 and isinstance(n.args[1],ast.Constant)and str(n.args[1].value).startswith('At most one fresh episode'))
        expression=compile(ast.Expression(body=call.args[0]),'pure_tick_guard_AST','eval')
        self.assertTrue(eval(expression,{'card':{'physical':{'tick':953651}}}))
        self.assertFalse(eval(expression,{'card':{'physical':{'tick':955215}}}))
        self.assertEqual(driver.LAST_NEW,1794798600);self.assertEqual(driver.CUTOFF,1794802380)

    def test_default_has_no_material_permission_and_typing_preserves_arrays(self):
        source=SOURCE.read_text('utf8')
        self.assertIn("if not a.execute_root_only:return dict(status='PREFLIGHT_ONLY_NO_NATIVE_OR_SDK'",source)
        self.assertIn('JSONEncode(r06TypedValue())',driver.typed_result_code('return {pose={0,3,0}}'))
        self.assertFalse(any(k=='dee_thinking'or k.startswith('dee_thinking.')for k in sys.modules))

if __name__=='__main__':unittest.main(verbosity=2)
