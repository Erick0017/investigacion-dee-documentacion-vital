"""Offline pilot source/XML/ABI fixtures; no Native, SDK, Studio or model."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,unittest,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent
P=ROOT/'prototipo/NATIVE_LIMPIO_R07'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class PilotChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=json.loads((P/'MANIFIESTO_PILOTO_R07.json').read_text('utf-8'))
  cls.d=(P/'ejecutar_piloto_R07_preparado_R02.py').read_text('utf-8')
  cls.a=(P/'LiveAdapters_R07.luau').read_text('utf-8')
  cls.i=(P/'INSTALAR_PILOTO_R07.luau').read_text('utf-8')
 def test_01_original_sources_preserved(self):
  for path,h in self.m['preserved_sources'].items():self.assertEqual(sha(path),h)
 def test_02_another_map_and_inherited_facts(self):
  d=self.m['definition'];self.assertEqual(d['positions']['start'],[20,3,20])
  self.assertEqual(d['source_sequence_offset'],56)
  self.assertEqual(d['inherited_public_state']['permissionStock'],164)
  self.assertEqual(d['inherited_public_state']['numberAVersion'],5)
  self.assertFalse(d['inherited_public_state']['codeBPresent'])
 def test_03_scene_module_sources_and_no_autorun(self):
  root=ET.parse(P/'DEEConnector_PILOTO_OTRO_MAPA_R07.rbxlx')
  for e in root.iter('Item'):
   if e.get('class')=='ModuleScript':
    n=e.find("Properties/string[@name='Name']").text
    s=e.find("Properties/ProtectedString[@name='Source']").text
    self.assertEqual(hashlib.sha256(s.encode()).hexdigest(),self.m['modules_sha256'][n])
   elif e.get('class')=='Script':self.assertEqual(e.find("Properties/bool[@name='Disabled']").text,'true')
 def test_04_raw_json_string_deliver_action(self):
  self.assertIn("a:deliverAction('+literal(wire)+')",self.d)
  self.assertNotIn("a:deliverAction(H:JSONDecode",self.d)
 def test_05_all_actual_sources_are_pinned(self):
  self.assertIn('"Main","BackendBinding","LiveAdapters_R07","MotorPathfinding_R07"',self.d)
  self.assertIn("scope['parent_native_cycles']==24",self.d)
  self.assertIn("scope['parent_last_sequence']==56",self.d)
 def test_06_fresh_and_budget_guards(self):
  self.assertIn("card['physical']['tick']==991187",self.d)
  self.assertIn("not journal.exists()or journal.stat().st_size==0",self.d)
  self.assertIn("ledger['limit']==160000",self.d)
  self.assertIn('LAST_NEW=1794859200',self.d)
  self.assertIn('CUTOFF=1794863220',self.d)
 def test_07_no_waypoint_teleport_or_semantic_strategy(self):
  self.assertIn('motor:moveTo(points[port+1]',self.a)
  self.assertNotIn('target_answer',self.a);self.assertNotIn('expected_answer',self.a)
  self.assertNotIn('Native',self.a.replace('-- No target selection, anti-loop, arithmetic, teacher or Native memory edit.',''))
  self.assertNotIn('ASSISTED_ORDER',self.a)
 def test_08_pilot_horizon_and_prepared_actuator(self):
  self.assertIn('MaxOpportunities=3,MaxActions=6',self.i)
  self.assertIn('AllowTechnicalTest=false',self.i)
  self.assertIn('device:SetAttribute("ActuatorValue",port)',self.a)
  self.assertIn('resourceCollected=false',self.a)
  self.assertNotIn('r.resourceCollected=true',self.a)
 def test_09_driver_import_is_inert(self):
  spec=importlib.util.spec_from_file_location('pilot_fixture_pure',P/'ejecutar_piloto_R07_preparado_R02.py')
  m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
  self.assertEqual(m.LIFE,'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_PILOT')
  self.assertEqual(m.LAST_NEW,1794859200)
  obs={'protocol':'DEE.RBX.Connector.R01','namespace':'R07_NATIVE_PILOT/map_b/PILOT',
   'observationId':'fixture','seq':1,'phase':'QUERY_CHOICE','worldTimeMs':0,'sampleTimeMs':0,'sensors':{}}
  self.assertEqual(m.native_observation(obs)['seq'],57)
 def test_10_json_typed_array_envelope_and_only_one_new_episode(self):
  self.assertIn('JSONEncode(r06TypedValue())',self.d)
  tree=ast.parse(self.d)
  native_calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='native']
  self.assertEqual(len(native_calls),3) # one Q1, optional Q2, feedback; no loop/replay.
if __name__=='__main__':unittest.main(verbosity=2)
