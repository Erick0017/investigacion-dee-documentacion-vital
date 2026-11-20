"""Record technical transport tests without importing DEE or loading a world."""
import argparse,hashlib,importlib.util,io,json,sys,time,unittest
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();here=Path(__file__).resolve().parent
    sys.path.insert(0,str(here));spec=importlib.util.spec_from_file_location('mu_transport_tests',here/'pruebas_servicio_stdlib.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);log=io.StringIO();start=time.monotonic()
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
    native_imports=sorted(n for n in sys.modules if n=='dee_thinking'or n.startswith('dee_thinking.'))
    value={'schema':'DEE.persistent_service.stdlib_transport_tests.v1','tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
        'native_modules_imported':native_imports,'native_ticks':0,'fake_world_is_not_a_DEE_experiment':True,'host_seconds':time.monotonic()-start,
        'source':[{'file':q.name,'bytes':q.stat().st_size,'sha256':hashlib.sha256(q.read_bytes()).hexdigest()}for q in sorted(here.glob('*.py'))],
        'log':log.getvalue(),'scope':'Queue capacity/schema/deduplication/controls/reconciliation and synthetic uncertainty only; not native worker-interruption validation or semantic learning.'}
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(value,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:value[k]for k in('tests_run','failures','errors','native_modules_imported','native_ticks')}));return not result.wasSuccessful()or bool(native_imports)


if __name__=='__main__':raise SystemExit(main())
