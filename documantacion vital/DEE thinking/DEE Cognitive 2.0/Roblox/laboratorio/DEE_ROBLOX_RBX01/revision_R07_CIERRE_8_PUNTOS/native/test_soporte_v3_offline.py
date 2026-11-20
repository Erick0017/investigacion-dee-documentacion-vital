"""Synthetic ledger/codec/contract tests. No Native, queues, Studio or model."""
from pathlib import Path
import ast,concurrent.futures,hashlib,importlib.util,json,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
def module(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
L=module(ROOT/'native/ledger_v3.py','_ledger_fixture_v3')
class Technical(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='rbx07_fixture_');self.base=Path(self.temp.name).resolve();self.old=L.ROOT;L.ROOT=self.base
    def tearDown(self):
        L.ROOT=self.old;self.assertTrue(self.base.name.startswith('rbx07_fixture_'));self.assertEqual(self.base.parent,Path(tempfile.gettempdir()).resolve());self.temp.cleanup()
    def test_three_isolated_ledgers_share_one_budget_without_lost_updates(self):
        path=self.base/'budget.json'
        ledgers=[L.TickLedger(path,L.PREFIX+'LOAD'+str(i),3,role='load')for i in(1,2,3)]
        def run(ledger):
            ledger.begin(ledger.life,'q1_'+ledger.life,'eci01-rbx01-decision');ledger.finish(ledger.life,'q1_'+ledger.life,991187,991217,'eci01-rbx01-decision')
            ledger.begin(ledger.life,'fb_'+ledger.life,'eci01-rbx01-feedback');ledger.finish(ledger.life,'fb_'+ledger.life,991217,991227,'eci01-rbx01-feedback')
        with concurrent.futures.ThreadPoolExecutor(max_workers=3)as e:list(e.map(run,ledgers))
        value=ledgers[0].read();self.assertEqual(value['consumed'],120);self.assertEqual(value['intents'],{})
        self.assertEqual(L.protected_load_slots(value),6);self.assertEqual({w['cycles']for w in value['worlds'].values()},{1})
    def test_ambiguous_intent_not_replayed_or_deleted(self):
        ledger=L.TickLedger(self.base/'budget.json',L.PREFIX+'MAIN',24)
        ledger.begin(ledger.life,'same','eci01-rbx01-decision')
        with self.assertRaises(RuntimeError):ledger.begin(ledger.life,'different','eci01-rbx01-decision')
        self.assertEqual(ledger.read()['intents'][ledger.life]['id'],'same')
    def test_load_tick_reservation_and_world_slots_protected(self):
        path=self.base/'budget.json';main=L.TickLedger(path,L.PREFIX+'MAIN',24)
        v=main.read();v['worlds']={L.PREFIX+'MAIN':{'consumed':98304,'reserved':0,'cycles':24,'max_cycles':24,'role':'main'},
            L.PREFIX+'CTRL1':{'consumed':24576,'reserved':0,'cycles':6,'max_cycles':6,'role':'control'}};v['consumed']=122880;L.write(path,v)
        pilot=L.TickLedger(path,L.PREFIX+'PILOT',3)
        with self.assertRaisesRegex(RuntimeError,'PROTECTED_LOAD'):pilot.begin(pilot.life,'not_steal','eci01-rbx01-decision')
        self.assertEqual(main.read()['consumed'],122880);self.assertEqual(main.read()['intents'],{})
    def test_q2_fixed_cue_only_and_omission_not_zero(self):
        tree=ast.parse((ROOT/'native/bundle/rbx07_native_v3.py').read_text('utf-8'))
        node=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='station_datum')
        def need(ok,msg):
            if not ok:raise ValueError(msg)
        c={'q2_sensor_codec':'price_tag_v1','q2_sensor_arm':'local_tag'};ns={'need':need,'scope':lambda:c}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'pure_codec_fixture','exec'),ns)
        f=ns['station_datum'];self.assertEqual(f(1,True,3),10);c['q2_sensor_arm']='constant_tag2';self.assertEqual(f(1,True,3),7)
        self.assertIsNone(f(-1,False,3))
        with self.assertRaises(ValueError):f(1,True,6)
    def test_inherited_R06_counter_is_not_reset_in_source(self):
        text=(ROOT/'native/bundle/rbx07_native_v3.py').read_text('utf-8');ast.parse(text)
        self.assertIn("prior.get('cycles') == 24",text);self.assertIn("prior.get('last_sequence') == 56",text)
        self.assertIn("'last_sequence': 56",text);self.assertIn("'parent_completed_opportunities': 28",text)
        self.assertIn('DEE.Cognitive.RBX01.async_native.INTEGRAL.V2.R01',text)
        self.assertIn('1794859200',text);self.assertIn('1794863220',text)
    def test_all_explicit_technical_sources_parse_without_importing(self):
        for name in('owner_support_v3.py','adapter_v3.py','servicio_eventos_v3.py','preparar_par28_v3.py','import0_v3.py','importar_par_v3.py'):
            ast.parse((ROOT/'native'/name).read_text('utf-8-sig'),filename=name)
if __name__=='__main__':unittest.main()
