"""Preserve operational N0 fixture results; never instantiate Native."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    args=parser.parse_args();here=Path(__file__).resolve().parent
    files=[here/'asistente_apd03.py',here/'entorno_compartido_apd03.py',
        here/'protocolo_apd03.py',here/'test_operativo_apd03_n0.py',
        here/'PROPUESTA_INTEGRACION_MINIMA.md',here.parent/'entorno_compartido_apd03_r01.py',
        here.parent/'vendor/entorno_objetivo_apd02.py']
    sources=[]
    for path in files:
        data=path.read_bytes();sources.append({'path':path.relative_to(here.parent).as_posix(),
            'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
        if path.suffix=='.py':compile(data,str(path),'exec')
    started=time.perf_counter()
    result=subprocess.run([sys.executable,'-I','-B',str(here/'test_operativo_apd03_n0.py'),'-v'],
        capture_output=True,text=True,encoding='utf8',timeout=30)
    record={'schema':'APD03.operational_N0_fixtures.R01',
        'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'sources':sources,'test_exit_code':result.returncode,
        'stdout':result.stdout,'stderr':result.stderr,'wall_seconds':time.perf_counter()-started,
        'new_native_ticks':0,'scope':'Five conventional fake-actor/sensor/learner fixtures, real synthetic files and complete environment serialization; not native learning or cross-process physical continuation.',
        'original_LAB_environment_unchanged_sha256':hashlib.sha256((here.parent/'entorno_compartido_apd03_r01.py').read_bytes()).hexdigest(),
        'energy':'NO MEDIDA'}
    data=(json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    with Path(args.output).open('xb')as stream:stream.write(data)
    print(json.dumps({'output':args.output,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
        'test_exit_code':result.returncode},ensure_ascii=False))
    raise SystemExit(result.returncode)


if __name__=='__main__':main()
