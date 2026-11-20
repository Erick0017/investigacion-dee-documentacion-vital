"""Final selected MA02 genealogy: archived admissions and offline memory references."""
import argparse
import importlib.util
import json
from pathlib import Path
spec=importlib.util.spec_from_file_location('references_archived',Path(__file__).with_name('recalcular_referencias_memoria.py'))
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args();x=r.calculate(a.evidencia,include_final05=True);a.salida.parent.mkdir(parents=True,exist_ok=True)
    a.salida.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'issues':len(x['issues']),'summary':x['summary'],'workers':x['selected_main_worker_summary'],
        'admissions':{k:v for k,v in x['selected_genealogy_native_admissions'].items()if k!='records'}},ensure_ascii=False))
    return 1 if x['issues']else 0
if __name__=='__main__':raise SystemExit(main())
