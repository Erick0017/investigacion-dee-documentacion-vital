"""Recalculation parser fixtures only; no Native, World or summaries as proof."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('C02_recalc_technical',ROOT/'analisis/RECALCULO_FUNCIONES_Y_MUNDO_C02.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def primary(number=0,memory=1,operation='suma'):
    return {'schema':'DEE.RBX01.C02.function_primary.R01','life_id':'ECI02_TECHNICAL_ONLY',
        'context':{'session_id':'SESSION_01','sequence':2,'observation_id':'OBS_02','operation_id':'OP_01'},
        'visible_tool':{'kind':'CALCULATE','slot':'A','form':'luma','left':0,'right':0},
        'teacher_mode':'paired','before_tick':1,'after_tick':10,'fixed_deadline_tick':20,
        'native_function':{'recall':{'native_sign':memory},'operation':operation,
                           'numeric_result':number,'status':'FORMED'if number is not None else'NULL'},
        'requests_normalized':[{'id':1,'channel':'TEST','payload':0,'requested_tick':2,
                               'receipt':{'id':1,'status':'applied'}}]}


def event(kind,data,seq=2):
    return {'kind':kind,'sessionId':'SESSION_01','seq':seq,'participant':'LIVE_NATIVE',
            'wallUnixMs':100+seq,'segment':1,'data':data}


class RecalculationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'pruebas');self.folder=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def write(self,name,value):
        path=self.folder/name;path.write_text(json.dumps(value),encoding='utf8');return path
    def test_zero_and_null_are_separate(self):
        zero=self.write('zero.json',primary())
        a=m.recalculate([zero],[],[],self.folder/'out0')
        self.assertEqual(a['descriptive_denominators']['numeric_formed'],1)
        self.assertEqual(a['Native_functions'][0]['numeric_result'],0)
        null=self.write('null.json',primary(None,None,None))
        b=m.recalculate([null],[],[],self.folder/'outN')
        self.assertEqual(b['descriptive_denominators']['numeric_NULL_or_missing'],1)
        self.assertIsNone(b['Native_functions'][0]['selected_opcode_matches_native_sign'])
    def test_copy_aliases_are_not_new_functions(self):
        one=self.write('one.json',primary());two=self.write('two.json',primary())
        out=m.recalculate([one,two],[],[],self.folder/'out')
        self.assertEqual(out['coverage']['function_primaries'],1)
        self.assertEqual(out['coverage']['function_file_aliases'],1)
        self.assertEqual(out['coverage']['unique_receipts_observed'],1)
    def test_cumulative_world_logs_deduplicate_and_link_actual_zero(self):
        source=self.write('p.json',primary())
        first=event('FUNCTION_APPLIED',{'request':primary()['visible_tool'],
            'output':{'memory_value':1,'operation':'suma','numeric_result':0}})
        second=event('FUNCTION_APPLIED',{'request':{'kind':'CALCULATE','slot':'B','form':'nara','left':0,'right':1},
            'output':{'memory_value':-1,'operation':'diferencia','numeric_result':-1}},4)
        world=self.write('world.json',[{'kind':'PUBLIC_OBSERVER_SAMPLE','event_log_raw':json.dumps([first])},
                                      {'kind':'PUBLIC_OBSERVER_SAMPLE','event_log_raw':json.dumps([first,second])}])
        out=m.recalculate([source],[],[world],self.folder/'out')
        self.assertEqual(out['coverage']['world_events'],2)
        self.assertEqual(out['coverage']['world_event_aliases'],1)
        self.assertTrue(out['World']['functions'][0]['native_output_same_in_world'])
        self.assertTrue(out['World']['chains'][0]['actual_intermediate_transport_verified'])
        self.assertFalse(out['World']['chains'][0]['native_B_primary_resolved'])
    def test_wrong_number_is_audited_not_replaced(self):
        source=self.write('wrong.json',primary(9))
        out=m.recalculate([source],[],[],self.folder/'out')
        self.assertEqual(out['Native_functions'][0]['numeric_result'],9)
        self.assertFalse(out['Native_functions'][0]['correct_selected_arithmetic'])
    def test_unresolved_native_identity_is_not_invented(self):
        source=self.write('events.json',[{'kind':'PHASE_COMPLETED','index':0,'mode':'eci01-rbx01-feedback',
            'tick':20,'result':{'evidence':{'requests':[]}}}])
        out=m.recalculate([],[],[],self.folder/'out0')
        manifest=[];issues=[];receipts={}
        result=m.parse_native([(None,source)],manifest,issues,receipts,{})
        self.assertTrue(any(i['issue'].startswith('NATIVE_LIFE_UNRESOLVED')for i in issues))
        self.assertTrue(result['feedback'][0]['life_id'].startswith('UNRESOLVED:'))
    def test_output_must_be_new(self):
        with self.assertRaises(FileExistsError):m.recalculate([],[],[],self.folder)
    def test_tail_projection_is_not_a_complete_function_event(self):
        world=self.write('tail.json',[{'kind':'PUBLIC_OBSERVER_SAMPLE',
            'event_log_view':{'representation':'CHUNKS_R02_TAIL','partial':True,'totalRows':100,'tailRows':1},
            'event_log_raw':json.dumps([{'kind':'FUNCTION_APPLIED','data':{},'seq':2,
                'sessionId':'SESSION_01','observerTailProjection':True,'fullLogRowIndex':100}])}])
        out=m.recalculate([],[],[world],self.folder/'out')
        self.assertEqual(out['coverage']['world_events'],0)
        self.assertFalse(out['coverage']['full_world_checkpoint_provided'])
        self.assertTrue(out['issues'])
    def test_R02_partial_raw_output_and_public_no_result_remain_distinct(self):
        p=primary(9);p['schema']='DEE.RBX01.C02.function_primary.R02'
        p['requests_normalized'][0]['receipt']['status']='rejected_occupied'
        p['public_tool_result']={'kind':'CALCULATE','slot':'A','form':'luma','memory_value':1,
            'operation':'suma','numeric_result':None,'formed':False,'reason':'NATIVE_PARTIAL_ADMISSION'}
        source=self.write('r02.json',p)
        world=self.write('world.json',[event('FUNCTION_APPLIED',{'request':p['visible_tool'],
                                                               'output':p['public_tool_result']})])
        out=m.recalculate([source],[],[world],self.folder/'out')
        self.assertEqual(out['Native_functions'][0]['numeric_result'],9)
        self.assertIsNone(out['Native_functions'][0]['public_numeric_result'])
        self.assertFalse(out['Native_functions'][0]['input_admission_complete'])
        self.assertEqual(out['descriptive_denominators']['validated_numeric_outputs_available'],0)
        self.assertTrue(out['World']['functions'][0]['native_output_same_in_world'])


if __name__=='__main__':unittest.main(verbosity=2)
