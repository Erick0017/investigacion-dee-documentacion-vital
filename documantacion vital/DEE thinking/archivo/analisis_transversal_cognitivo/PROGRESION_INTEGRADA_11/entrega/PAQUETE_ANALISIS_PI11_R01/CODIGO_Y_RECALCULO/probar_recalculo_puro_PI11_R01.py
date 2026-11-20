"""Synthetic documentary recalculation fixtures; no DEE/Native evidence."""
from pathlib import Path
import copy,importlib.util,json,tempfile,unittest

FILE=Path(__file__).with_name('recalcular_PI11_R01.py')
spec=importlib.util.spec_from_file_location('pi11_pure_recalc',FILE)
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

def write(p,v):p.write_text(json.dumps(v),encoding='utf8')
def witness(n,before=1000,q1=0,q2=-1,physical=True,attributed=True,refresh=False):
    return {'version':'DEE.PI11.synthetic_fixture.NOT_NATIVE','life_id':'DIAGNOSTIC_SYNTHETIC_NOT_A_REAL_LIFE',
        'ordinal':n,'before_tick':before,'after_tick':before+1500,'new_native_ticks':1500,
        'first_stage':{'reader':{'choice':q1},'register':{'released':False,'access':{'allowed':False,'native_gate':q1}}},
        'second_stage':{'reader':{'choice':q2},'refresh_FI':refresh,'FI':{'old_q6_choice':1}if refresh else None},
        'resource':{'physical_delivered':physical,'attributed_useful':attributed,'actual_failed':not attributed,'certificate_valid':True,'remaining_stock':24-n-int(physical)},
        'environment_after':{'start_tick':1000,'permissions':4},'offer':{'environment':{'mode':'need'}},
        'environment_spec_at_input':{'cue':'z'},'actual_failed':not attributed,'returned_failed':not attributed,
        'Q1_references_before':{'A_minus_B':0},'references_after':{'q1':{'A_minus_B':-1 if not attributed else 0}},
        'requests':[{'id':n+100,'receipt':{'id':n+100,'status':'applied'}}]}

class Recalculation(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='pure_recalc_PI11_',dir=FILE.parent.parent/'control')
        self.home=Path(self.temp.name);self.inputs=self.home/'primarios';self.inputs.mkdir()
        self.proof=self.home/'closure.json';write(self.proof,{'closed_for_documentary_read':True,'closure_evidence':'SYNTHETIC_TEST_ONLY_NOT_A_NATIVE_OWNER'})
        self.out=self.home/'out'
    def tearDown(self):self.temp.cleanup()
    def put(self,n,**kw):
        value=witness(n,**kw);path=self.inputs/('episodio_%04d.json'%n);write(path,value);return path,value
    def test_zero_and_NULL_are_distinct(self):
        self.put(0,q1=0);self.put(1,before=2500,q1=None,attributed=False)
        out=r.recalculate(self.inputs,self.out,self.proof);life=next(iter(out['by_life'].values()))
        self.assertEqual(life['q1_choices'],[0,None]);self.assertEqual(life['totals']['q1_NULL'],1)
        self.assertEqual(life['totals']['physical_delivered'],2);self.assertEqual(life['totals']['attributed_useful'],1)
        self.assertEqual(life['totals']['certificate_physical_reuse'],2);self.assertEqual(life['totals']['certificate_useful_reuse'],1)
    def test_crossing_boundary_does_not_reclassify(self):
        self.put(0,before=18000);self.put(1,before=19500)
        out=r.recalculate(self.inputs,self.out,self.proof);life=next(iter(out['by_life'].values()))
        self.assertEqual(life['reserved_opportunities'],1)
        self.assertEqual(life['Native_ticks_completed_witnesses'],3000)
    def test_duplicate_receipt_alias_not_new_event(self):
        path,value=self.put(0);value['requests'].append(copy.deepcopy(value['requests'][0]));write(path,value)
        out=r.recalculate(self.inputs,self.out,self.proof);life=next(iter(out['by_life'].values()))
        self.assertEqual(life['Native_inputs_unique']['unique_requested'],1)
        self.assertEqual(life['Native_inputs_unique']['receipt_aliases'],1)
    def test_contradictory_receipt_rejected_before_output(self):
        path,value=self.put(0);value['requests'].append({'id':100,'receipt':{'id':100,'status':'rejected_conflict'}});write(path,value)
        with self.assertRaises(ValueError):r.recalculate(self.inputs,self.out,self.proof)
        self.assertFalse(self.out.exists())
    def test_no_completed_file_is_not_zero_score(self):
        with self.assertRaises(ValueError):r.recalculate(self.inputs,self.out,self.proof)
        self.assertFalse(self.out.exists())
    def test_unclosed_declaration_rejected(self):
        self.put(0);write(self.proof,{'closed_for_documentary_read':False,'closure_evidence':'none'})
        with self.assertRaises(ValueError):r.recalculate(self.inputs,self.out,self.proof)
        self.assertFalse(self.out.exists())
    def test_distinct_same_ordinal_bytes_rejected(self):
        self.put(0);extra=self.inputs/'copy';extra.mkdir();value=witness(0,q1=1);write(extra/'episodio_0000.json',value)
        with self.assertRaises(ValueError):r.recalculate(self.inputs,self.out,self.proof)
        self.assertFalse(self.out.exists())
    def test_exact_duplicate_file_dealiased(self):
        _,value=self.put(0);extra=self.inputs/'copy';extra.mkdir();write(extra/'episodio_0000.json',value)
        out=r.recalculate(self.inputs,self.out,self.proof);self.assertEqual(len(out['witness_file_aliases_excluded']),1)
        self.assertEqual(next(iter(out['by_life'].values()))['completed_opportunities'],1)
    def test_csv_JSON_valid_and_existing_output_protected(self):
        self.put(0,refresh=True);r.recalculate(self.inputs,self.out,self.proof)
        self.assertTrue((self.out/'EPISODIOS_PI11.csv').read_text('utf8').startswith('life_id,ordinal,'))
        self.assertFalse(json.loads((self.out/'RESUMEN_PI11.json').read_text('utf8'))['Native_executed'])
        before=(self.out/'RESUMEN_PI11.json').read_bytes()
        with self.assertRaises(ValueError):r.recalculate(self.inputs,self.out,self.proof)
        self.assertEqual((self.out/'RESUMEN_PI11.json').read_bytes(),before)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Recalculation))
    print(json.dumps({'pure':True,'Native_imported':False,'Native_ticks':0,'tests':result.testsRun,'errors':len(result.errors),'failures':len(result.failures)},sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful()else 1)
