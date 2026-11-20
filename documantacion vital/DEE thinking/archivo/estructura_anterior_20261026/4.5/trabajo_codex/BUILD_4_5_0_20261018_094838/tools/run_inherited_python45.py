"""Run unchanged inherited tests against site-packages, recording every result."""
import argparse, hashlib, importlib.util, json, sys, time, traceback, unittest
from pathlib import Path

class Result(unittest.TextTestResult):
    def startTest(self,test):
        super().startTest(test);self.started=time.monotonic()
    def record(self,test,status,detail=None):
        self.rows.append({'test':test.id(),'status':status,'seconds':time.monotonic()-self.started,'detail':detail})
    def addSuccess(self,test):super().addSuccess(test);self.record(test,'PASS')
    def addFailure(self,test,err):super().addFailure(test,err);self.record(test,'FAIL',''.join(traceback.format_exception(*err)))
    def addError(self,test,err):super().addError(test,err);self.record(test,'ERROR',''.join(traceback.format_exception(*err)))
    def addSkip(self,test,reason):super().addSkip(test,reason);self.record(test,'SKIP',reason)

def main():
    p=argparse.ArgumentParser();p.add_argument('--tests',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();import dee_thinking as d
    assert d.__version__=='4.5.0' and 'site-packages' in d.__file__.lower(),d.__file__
    import dee_thinking._native as n
    suite=unittest.TestSuite();files=[]
    root=Path(__file__).resolve().parents[1]
    original=json.loads((root/'evidence/SOURCE40_MANIFEST.json').read_text(encoding='utf-8'))
    inherited_names={Path(row['path']).name for row in original
                     if row['path'].startswith('tests/python/test_') and row['path'].endswith('.py')}
    for file in sorted(a.tests.glob('test_*.py')):
        if file.name not in inherited_names:continue
        spec=importlib.util.spec_from_file_location(file.stem,file);module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module);suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
        files.append({'path':file.name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
    Result.rows=[];started=time.monotonic()
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
    report={'schema':'DEE45.inherited-python-tests.v1','version':d.__version__,'import_path':d.__file__,
      'python':sys.executable,'native_sha256':hashlib.sha256(Path(n.__file__).read_bytes()).hexdigest(),
      'files':files,'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
      'skipped':len(result.skipped),'elapsed_seconds':time.monotonic()-started,'cases':result.rows,
      'scope':'Technical tests, not independent scientific replicas; version assertions only updated4.0→4.5.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return 0 if result.wasSuccessful() else 1
if __name__=='__main__':raise SystemExit(main())
