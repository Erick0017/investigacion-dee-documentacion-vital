"""Close N0 fixtures and pure geometry before Root authorizes any trajectory."""
import argparse
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    args=parser.parse_args();here=Path(__file__).resolve().parent
    names=('comparadores_apd03.py','test_comparadores_apd03.py',
        'entorno_compartido_apd03_r01.py','test_entorno_compartido_apd03.py',
        'lexico_generico_apd03_r01.py','protocolo_curvas_lexico_apd03_r01.py',
        'vendor/evaluador_calidad_apd02.py','vendor/proveedores_prueba_apd02.py',
        'vendor/entorno_objetivo_apd02.py','CONTRATO_COMPARACION_R01.md')
    sources=[]
    for name in names:
        data=(here/name).read_bytes()
        sources.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
        if name.endswith('.py'):compile(data,str(here/name),'exec')
    started=time.perf_counter();tests=[]
    for name in('test_comparadores_apd03.py','test_entorno_compartido_apd03.py'):
        result=subprocess.run([sys.executable,'-B',str(here/name),'-v'],
            capture_output=True,text=True,encoding='utf8',timeout=30)
        tests.append({'file':name,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    spec=importlib.util.spec_from_file_location('apd03_curve_design',here/'protocolo_curvas_lexico_apd03_r01.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    plan=module.plan()
    record={'schema':'DEE.APD03.interfaces_N0.R02','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'sources':sources,'tests':tests,'wall_seconds':time.perf_counter()-started,
        'new_native_ticks':0,'native_modules_imported_in_this_process':any('dee_thinking'in name for name in sys.modules),
        'geometry':{'preparation_sites':len(plan['geometry']['preparation_sites']),
            'ports':len(plan['geometry']['new_ports']),'reader_sites':len(plan['geometry']['common_reader']),
            'static_duplicate_preparation_count':plan['geometry']['new_preparation_duplicate_count'],
            'static_overlap_old_readers':plan['geometry']['new_preparation_overlap_legacy_readers'],
            'actual_RAW_not_observed':True},'prospective_curve_protocol':plan,
        'scope':'12 N0 fixtures, compile checks and pure integer geometry. No scientific comparison with E1, Native evolution, acquisition or physical vacancy claim.',
        'energy':'NO MEDIDA','all_tests_exit_zero':all(t['exit_code']==0 for t in tests)}
    data=(json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    with Path(args.output).open('xb')as stream:stream.write(data)
    print(json.dumps({'output':args.output,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
        'all_tests_exit_zero':record['all_tests_exit_zero'],'new_native_ticks':0},ensure_ascii=False))
    raise SystemExit(0 if record['all_tests_exit_zero'] else 1)


if __name__=='__main__':main()
