"""Preserve the bounded comparator fixture receipt (no Native imports)."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    here=Path(__file__).resolve().parent
    sources=[]
    for name in ('comparadores_apd03.py','test_comparadores_apd03.py',
                 'vendor/evaluador_calidad_apd02.py','vendor/proveedores_prueba_apd02.py',
                 'CONTRATO_COMPARACION_R01.md'):
        data=(here/name).read_bytes()
        sources.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    started=time.perf_counter()
    result=subprocess.run([sys.executable,'-B',str(here/'test_comparadores_apd03.py'),'-v'],
        capture_output=True,text=True,encoding='utf8',timeout=30)
    record={'schema':'DEE.APD03.comparator_N0_fixture_receipt.R01',
        'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'sources':sources,'exit_code':result.returncode,
        'stdout':result.stdout,'stderr':result.stderr,
        'wall_seconds':time.perf_counter()-started,
        'scope':'5 N0 fixtures including3 classical rollouts, actual artifact bytes and portable metrics recalculation. Temporary fixture outputs are not science trajectories.',
        'new_native_ticks':0,'energy':'NO MEDIDA',
        'is_comparison_with_E1':False,'fixture_processes':1,
        'not_a_declaration_of_general_capability':True}
    data=(json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    with Path(args.output).open('xb') as stream:stream.write(data)
    print(json.dumps({'output':args.output,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
        'exit_code':result.returncode},ensure_ascii=False))
    raise SystemExit(result.returncode)


if __name__=='__main__':main()
