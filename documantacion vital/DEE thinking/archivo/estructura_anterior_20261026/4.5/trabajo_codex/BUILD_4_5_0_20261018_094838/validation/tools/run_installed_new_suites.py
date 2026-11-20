"""Run the published new tests against an immutable installed final wheel."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import unittest


EXPECTED_WHEEL='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
EXPECTED_PYD='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


class Result(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.records=[]
    def startTest(self,test):self.started=time.monotonic();super().startTest(test)
    def record(self,test,status,detail=None):
        self.records.append({'test_id':test.id(),'status':status,'wall_seconds':time.monotonic()-self.started,'detail':detail})
    def addSuccess(self,test):self.record(test,'PASS');super().addSuccess(test)
    def addFailure(self,test,err):self.record(test,'FAIL',self._exc_info_to_string(err,test));super().addFailure(test,err)
    def addError(self,test,err):self.record(test,'ERROR',self._exc_info_to_string(err,test));super().addError(test,err)
    def addSkip(self,test,reason):self.record(test,'SKIPPED',reason);super().addSkip(test,reason)
    def addExpectedFailure(self,test,err):self.record(test,'EXPECTED_FAILURE',self._exc_info_to_string(err,test));super().addExpectedFailure(test,err)
    def addUnexpectedSuccess(self,test):self.record(test,'UNEXPECTED_SUCCESS');super().addUnexpectedSuccess(test)


def main():
    p=argparse.ArgumentParser();p.add_argument('--tests',type=Path,required=True);p.add_argument('--wheel',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    import dee_thinking as d
    assert d.__version__=='4.5.0'
    assert Path(d.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    assert sha(a.wheel)==EXPECTED_WHEEL and sha(d._native.__file__)==EXPECTED_PYD
    names=['test_consolidated_api.py','test_remote_reader_api.py','test_experimental_absence.py','test_experimental_regulation.py']
    suite=unittest.TestSuite();sources=[]
    for i,name in enumerate(names):
        path=a.tests/name;spec=importlib.util.spec_from_file_location('published_suite_'+str(i),path)
        module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
        subsuite=unittest.defaultTestLoader.loadTestsFromModule(module)
        sources.append({'path':str(path),'sha256':sha(path),'tests':subsuite.countTestCases()});suite.addTests(subsuite)
    start=time.monotonic();cpu=time.process_time();r=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
    result={'schema':'DEE4.5.installed-final-new-suites.v1','version':d.__version__,'module':d.__file__,'python':sys.executable,
            'wheel_sha256':sha(a.wheel),'native_sha256':sha(d._native.__file__),'instrument_sha256':sha(__file__),
            'sources':sources,'tests_run':r.testsRun,'passed':sum(x['status']=='PASS' for x in r.records),
            'failures':len(r.failures),'errors':len(r.errors),'skipped':len(r.skipped),
            'expected_failures':len(r.expectedFailures),'unexpected_successes':len(r.unexpectedSuccesses),
            'wall_seconds':time.monotonic()-start,'cpu_seconds':time.process_time()-cpu,'results':r.records,
            'sources_unchanged':all(sha(x['path'])==x['sha256'] for x in sources),
            'historical_runner_imports':[x for x in sys.modules if x in('common','life','integrated','curriculum','word_bus','selective_native')],
            'status':'PASS' if r.wasSuccessful() and not r.skipped and not r.expectedFailures else'FAIL'}
    (a.out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    if result['status']!='PASS':raise SystemExit(1)


if __name__=='__main__':main()
