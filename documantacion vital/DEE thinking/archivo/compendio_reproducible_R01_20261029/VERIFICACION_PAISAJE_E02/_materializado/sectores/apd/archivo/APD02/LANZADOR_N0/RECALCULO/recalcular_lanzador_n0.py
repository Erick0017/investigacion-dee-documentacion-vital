"""Repeat exact launcher mock fixtures; this never calls the actual manager."""
import argparse,hashlib,json,subprocess,sys,tempfile
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--lanzador',type=Path,required=True);p.add_argument('--validador',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    with tempfile.TemporaryDirectory(prefix='apd2_mock_')as tmp:
        out=Path(tmp)/'FIXTURES';run=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(Path(__file__).with_name('probar_lanzador_apd02_n0.py')),'--lanzador',str(a.lanzador.resolve()),'--validador',str(a.validador.resolve()),'--salida',str(out)],capture_output=True,text=True,encoding='utf8',timeout=45)
        if run.returncode:print(run.stdout);print(run.stderr);return run.returncode
        result=out/'RESULTADO_N0.json'
        with a.salida.open('xb')as f:f.write(result.read_bytes())
        print(json.dumps({'mock_cases':len(json.loads(result.read_bytes())['cases']),'native_ticks':0,'actual_manager_calls':0,'sha256':hashlib.sha256(result.read_bytes()).hexdigest()}))
    return 0
if __name__=='__main__':raise SystemExit(main())
