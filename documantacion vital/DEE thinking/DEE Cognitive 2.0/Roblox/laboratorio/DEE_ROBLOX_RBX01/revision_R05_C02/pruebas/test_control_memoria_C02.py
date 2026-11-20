"""Focal runner transport fixtures, no Native or Roblox; Fake is test-only."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('C02_focal_technical',ROOT/'control/control_memoria_reservado_C02.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class Fake:
    def __init__(self,first=12,null_first=False):
        self.calls=[];self.calc=0;self.first=first;self.null_first=null_first;self.tick=947395
    def execute(self,kind,payload,context):
        self.calls.append((kind,payload,context));self.tick+=1
        out={'nativeTick':self.tick,'nativeTicks':1}
        if kind=='decision':
            return dict(out,action='SAFE_WAIT'if self.null_first else'SKIP_STATION',null=self.null_first)
        if kind=='query_sensor':return dict(out,action='EXIT_0',null=False)
        if kind=='feedback':return dict(out,accepted=True)
        tool=payload['tool']
        if tool['kind']=='LESSON':return dict(out,accepted=True,toolResult={'kind':'LESSON','numeric_result':None})
        values=[self.first,11,4,5,4];actual=values[self.calc];self.calc+=1
        return dict(out,accepted=True,toolResult={'kind':'CALCULATE','slot':tool['slot'],
                    'form':tool['form'],'numeric_result':actual})


class FocalTests(unittest.TestCase):
    def test_import_and_default_protocol_are_non_material(self):
        self.assertNotIn('dee_thinking',sys.modules)
        protocol,sha=m.protocol()
        self.assertEqual(protocol['status'],'PREPARED_NOT_NATIVE_EXECUTED')
        self.assertEqual(protocol['opportunities'],6);self.assertEqual(len(sha),64)

    def test_actual_wrong_integer_is_next_input_not_expected_value(self):
        fake=Fake(first=12);records=[]
        out=m.run_sequence(fake,'FOCAL_TEST_01',lambda event,**data:records.append((event,data)))
        tools=[p['tool']for k,p,c in fake.calls if k=='function']
        self.assertEqual(tools[1]['left'],12)
        self.assertFalse(out['rows'][0]['correct_if_numeric_opportunity'])
        self.assertEqual(tools[4]['left'],4)
        self.assertEqual(out['opportunities_completed'],6)

    def test_zero_is_valid_intermediate(self):
        self.assertEqual(m.step_tool(2,0)['left'],0)
        self.assertIsNone(m.step_tool(2,None))
        self.assertIsNone(m.step_tool(2,700))

    def test_no_expected_value_or_sign_enters_calculation_request(self):
        fake=Fake();out=m.run_sequence(fake,'FOCAL_TEST_02',lambda *args,**kw:None)
        for kind,payload,context in fake.calls:
            if kind=='function' and payload['tool']['kind']=='CALCULATE':
                self.assertEqual(set(payload['tool']),{'kind','slot','form','left','right'})
            if kind=='query_sensor':
                self.assertEqual(payload['observation']['sensors']['stationSignal'],-1)
        self.assertFalse(out['Roblox_executed'])

    def test_generic_return_does_not_correct_a_formed_wrong_number(self):
        fake=Fake(first=12);m.run_sequence(fake,'FOCAL_TEST_03',lambda *args,**kw:None)
        feedback=[p for k,p,c in fake.calls if k=='feedback']
        self.assertFalse(feedback[0]['materialConsequence'])
        self.assertFalse(feedback[1]['materialConsequence'])

    def test_q1_null_completes_only_feedback_and_stops_without_repair(self):
        fake=Fake(null_first=True);out=m.run_sequence(fake,'FOCAL_TEST_04',lambda *args,**kw:None)
        self.assertEqual([k for k,p,c in fake.calls],['decision','feedback'])
        self.assertEqual(out['opportunities_completed'],1)
        self.assertTrue(fake.calls[-1][1]['materialConsequence'])


if __name__=='__main__':unittest.main(verbosity=2)
