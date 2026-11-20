"""R02 semantic delta tests; technical doubles only, no Native or World."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m);return m

class A:
    tick=108
class Timer:
    def __init__(self,a):self.a=a;self.samples=[]
    def run_until(self,t):self.a.tick=t;self.samples.append(t)
class Tools:
    def __init__(self):self.serial=0
    @staticmethod
    def next_lexical_tick(t):return(t//67+1)*67
    def req(self,t,p):
        self.serial+=1;return{'id':self.serial,'port':'TEST.'+str(self.serial),'tick':t,'payload':p}
    def lesson(self,a,form,sign,**kw):
        t=self.next_lexical_tick(a.tick);a.run_until(t+3)
        return{'form':form,'observed_sign':sign,'requests':[self.req(t,5),self.req(t,11),self.req(t,11)]}
    def solve(self,a,form,left,right,**kw):
        a.run_until(a.tick+20)
        return{'recall':{'native_sign':1},'operation':'suma','numeric_result':123,
               'status':'FORMED','requests':[self.req(a.tick-1,4)]}
class Apparatus:
    def __init__(self,rejected):self.rejected=set(rejected)
    def receipts(self,a,rows):
        return[{**r,'receipt':{'id':r['id'],'status':'rejected_occupied'if r['id']in self.rejected else'applied'}}for r in rows]
    @staticmethod
    def summary(rows):
        n=sum(r['receipt']['status']=='applied'for r in rows)
        return{'unique_requested':len(rows),'applied':n,'rejected':len(rows)-n}

class R02Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'pruebas');self.directory=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def exercise(self,version='R02',rejected=(3,6),kind='LESSON'):
        file=ROOT/('native/r02_bundle/rbx02_native_C02.py'if version=='R02'else'native/rbx02_native_C02.py')
        actor=load('C02_'+version+'_DOUBLE',file);actor.identity=lambda a:{'life_id':'TECHNICAL_C02_R02'}
        actor.scope=lambda:{'teacher_mode':'paired'};actor.home=lambda directory,a:Path(directory)
        package=types.ModuleType('capacidades');package.c02_funciones_native=Tools()
        a=A();timer=Timer(a);m={'pending':{'calendar':{'second':{'query_tick':100,'outcome_injection_tick':500}}}}
        tool={'kind':'LESSON','items':[{'form':'luma','observedSign':1},{'form':'nara','observedSign':-1}]}
        if kind=='CALCULATE':tool={'kind':kind,'slot':'A','form':'luma','left':6,'right':2}
        row={'payload':{'tool':tool},'context':{'operation_id':'OP_R02_TEST'}}
        with patch.dict(sys.modules,{'capacidades':package}):
            result=actor.function(a,row,self.directory,m,timer,Apparatus(rejected))
        return actor,a,m,result
    def test_known_partial_lesson_completes_with_explicit_no_result(self):
        actor,a,m,result=self.exercise()
        self.assertTrue(result['accepted']);self.assertTrue(result['null'])
        self.assertEqual(result['toolResult']['reason'],'NATIVE_PARTIAL_ADMISSION')
        self.assertFalse(result['toolResult']['formed']);self.assertIsNone(result['toolResult']['numeric_result'])
        self.assertTrue(m['pending']['function_used'])
        primary=json.loads((self.directory/'functions/OP_R02_TEST.json').read_text('utf8'))
        self.assertEqual(len(primary['requests_normalized']),6)
        self.assertEqual(primary['Native_inputs'],{'unique_requested':6,'applied':4,'rejected':2})
        self.assertEqual(primary['public_tool_result'],result['toolResult'])
        self.assertFalse(primary['input_admission_complete'])
    def test_old_R01_behavior_is_preserved(self):
        with self.assertRaises(ValueError):self.exercise('R01')
        self.assertTrue((self.directory/'functions/OP_R02_TEST.json').is_file())
    def test_all_admitted_numeric_result_is_not_recomputed(self):
        actor,a,m,result=self.exercise(rejected=(),kind='CALCULATE')
        self.assertEqual(result['toolResult']['numeric_result'],123)
        self.assertTrue(result['toolResult']['formed'])
    def test_partial_numeric_keeps_raw_observation_but_world_gets_no_result(self):
        actor,a,m,result=self.exercise(rejected=(1,),kind='CALCULATE')
        self.assertIsNone(result['toolResult']['numeric_result'])
        primary=json.loads((self.directory/'functions/OP_R02_TEST.json').read_text('utf8'))
        self.assertEqual(primary['native_function']['numeric_result'],123)
        self.assertIsNone(primary['public_tool_result']['numeric_result'])
    def test_helper_byte_identity_and_no_native_import(self):
        old=(ROOT/'capacidades/c02_funciones_native.py').read_bytes()
        new=(ROOT/'native/r02_bundle/c02_funciones_native.py').read_bytes()
        self.assertEqual(hashlib.sha256(old).hexdigest(),hashlib.sha256(new).hexdigest())
        self.assertNotIn('dee_thinking',sys.modules)
        actor=load('C02_R02_PURE',ROOT/'native/r02_bundle/rbx02_native_C02.py')
        self.assertEqual(actor.KEY,'DEE.Cognitive.RBX01.async_native.C02.R02')
        self.assertEqual(actor.FOLDER,'RBX02_NATIVE_C02_R02')

if __name__=='__main__':unittest.main(verbosity=2)
