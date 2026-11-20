"""CPC8 technical reproduction of the sealed product tests, not new samples."""
import argparse,hashlib,json,os,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=ROOT/'resultados/regresion_producto45')
OUT=parser.parse_args().out
OUT.mkdir(parents=True,exist_ok=False)
import dee_thinking as dee
from dee_thinking import _native
identity={'version':dee.__version__,'import':dee.__file__,'native':_native.__file__,
          'native_sha256':hashlib.sha256(Path(_native.__file__).read_bytes()).hexdigest()}
assert identity['version']=='4.5.0'
assert identity['native_sha256']=='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
class Recorded(unittest.TextTestResult):
    def startTest(self,test):
        self.began=time.monotonic();super().startTest(test)
    def record(self,test,status,detail=None):
        with (OUT/'TESTS.jsonl').open('a',encoding='utf-8') as f:
            f.write(json.dumps({'test':test.id(),'status':status,'elapsed_seconds':time.monotonic()-self.began,'detail':detail})+'\n')
    def addSuccess(self,test):super().addSuccess(test);self.record(test,'SUCCESS')
    def addFailure(self,test,err):super().addFailure(test,err);self.record(test,'FAILURE',self._exc_info_to_string(err,test))
    def addError(self,test,err):super().addError(test,err);self.record(test,'ERROR',self._exc_info_to_string(err,test))
    def addSkip(self,test,reason):super().addSkip(test,reason);self.record(test,'SKIP',reason)
start=time.monotonic()
suite=unittest.defaultTestLoader.discover(str(ROOT/'base_validada/product45/tests/python'))
result=unittest.TextTestRunner(verbosity=2,resultclass=Recorded).run(suite)
report={'kind':'Technical reproduction; deterministic runs are not independent scientific replicas',
        'instrument':identity,'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
        'skipped':len(result.skipped),'elapsed_seconds':time.monotonic()-start,'successful':result.wasSuccessful()}
(OUT/'RESULT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report));sys.exit(0 if result.wasSuccessful() else 1)
