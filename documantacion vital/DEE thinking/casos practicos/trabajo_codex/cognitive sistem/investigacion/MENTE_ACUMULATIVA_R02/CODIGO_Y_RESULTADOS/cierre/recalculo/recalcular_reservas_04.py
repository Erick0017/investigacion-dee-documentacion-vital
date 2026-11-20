"""MA02 fifth-content work, request-order/delay reserves and repeated use."""
import argparse
import importlib.util
import json
from pathlib import Path
spec=importlib.util.spec_from_file_location('service_archived',Path(__file__).with_name('recalcular_servicio_01.py'))
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args();x=r.calculate(a.evidencia,phase='04');a.salida.parent.mkdir(parents=True,exist_ok=True)
    a.salida.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'issues':len(x['issues']),'observations_checked':x['observations_checked'],'workers':len(x['workers']),
        'sessions':[{'case':q['case'],'correct':q['correct'],'requested':q['requested'],'receipts':q['receipts']}for q in x['sessions']]},ensure_ascii=False))
    return 1 if x['issues']else 0
if __name__=='__main__':raise SystemExit(main())
