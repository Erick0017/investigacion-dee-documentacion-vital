import importlib.util,json,tempfile,unittest
from pathlib import Path
P=Path(__file__).with_name('LATENCIAS_Q1_Q2_VIDEO_R06_R01.py')
s=importlib.util.spec_from_file_location('lat_fixture',P);M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
class TestLatency(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory(prefix='r06_latency_fixture_');self.root=Path(self.tmp.name).resolve()
    def tearDown(self):
        self.assertTrue(self.root.name.startswith('r06_latency_fixture_'));self.assertEqual(self.root.parent,Path(tempfile.gettempdir()).resolve());self.tmp.cleanup()
    def write(self,rows):
        p=self.root/'events.jsonl';p.write_text(''.join(json.dumps(x)+'\n'for x in rows),encoding='utf-8');return p
    def row(self,i,value,phase='decision',kind='NATIVE_COMPLETED'):
        return {'kind':kind,'operation_id':'R06_OP'+str(i),'phase':phase,'cycle':5+i//2,'wall_seconds':value}
    def test_even_median_aliases_and_nonphase_fields_excluded(self):
        r=self.row(0,4);p=self.write([r,r,self.row(1,2,'query_sensor'),{'kind':'OTHER','S':{'latency':999999}}])
        v=M.main(['LIVE_NATIVE='+str(p)],self.root/'out')
        self.assertEqual(v['summary']['LIVE_NATIVE']['Q1_Q2_combined']['p50_seconds'],3)
        self.assertEqual(v['summary']['LIVE_NATIVE']['Q1_Q2_combined']['n'],2)
        self.assertEqual(v['identical_aliases_deduplicated'],1)
    def test_missing_Q2_not_filled_and_conflicting_same_ID_rejected(self):
        p=self.write([self.row(0,4)]);v=M.main(['LIVE_NATIVE='+str(p)],self.root/'one')
        self.assertEqual(v['summary']['LIVE_NATIVE']['query_sensor']['n'],0)
        self.assertIsNone(v['summary']['LIVE_NATIVE']['query_sensor']['p50_seconds'])
        p=self.write([self.row(0,4),self.row(0,99)])
        with self.assertRaisesRegex(ValueError,'CONFLICTING'):M.main(['LIVE_NATIVE='+str(p)],self.root/'bad')
if __name__=='__main__':unittest.main()
