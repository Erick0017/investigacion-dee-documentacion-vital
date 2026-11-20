"""Exercise the exporter against synthetic closed evidence, not MAIN."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
    p=argparse.ArgumentParser();p.add_argument('--salida',required=True,type=Path);a=p.parse_args()
    fixtures=load('apd03_closure_fixtures',HERE/'probar_servicio_hora_apd03_n0.py');builder=load('apd03_closure_builder',HERE/'cerrar_servicio_hora_apd03_n0.py')
    case=fixtures.ServiceAuditFixtures();case.setUp()
    try:
        case.test_complete_synthetic_closure_checks_same_id_without_new_submission()
        result=builder.close_existing(case.root,case.root/'CIERRE_SINTETICO')
        if result['issues']or result['phase']!='closed':raise ValueError('Synthetic closure was not recomputed')
        manifest=fixtures.M.read(case.root/'CIERRE_SINTETICO/MANIFIESTO.json')
        for member in manifest['members']:
            path=case.root/'CIERRE_SINTETICO'/member['file']
            if path.stat().st_size!=member['bytes']or fixtures.M.sha(path)!=member['sha256']:raise ValueError('Manifest fixture mismatch')
        report={'schema':'APD03.service_hour.portable_export.N0_fixture.R01','synthetic_not_MAIN':True,'fixtures':1,'issues':[],'new_native_ticks':0,'spawned_child_processes':0,'recalculated_checks':result['recalculated_checks'],'member_hashes_verified':len(manifest['members']),'same_archived_result_in_three_directories':True,'sources':{n:{'bytes':(HERE/n).stat().st_size,'sha256':hashlib.sha256((HERE/n).read_bytes()).hexdigest()}for n in('cerrar_servicio_hora_apd03_n0.py','probar_cierre_portable_apd03_n0.py','recalcular_servicio_hora_apd03_n0.py')}}
    finally:case.tearDown()
    with a.salida.open('x',encoding='utf8',newline='\n')as s:json.dump(report,s,ensure_ascii=False,sort_keys=True,indent=2);s.write('\n')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
