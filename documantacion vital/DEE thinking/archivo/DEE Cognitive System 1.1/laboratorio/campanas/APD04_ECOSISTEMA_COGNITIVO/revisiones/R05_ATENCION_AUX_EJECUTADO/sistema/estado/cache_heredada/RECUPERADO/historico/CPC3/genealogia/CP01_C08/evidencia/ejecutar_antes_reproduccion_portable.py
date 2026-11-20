"""Campaign driver: isolated bounded processes, incremental results, no historical reruns."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from supervision import Budget,atomic_json,run_child


def main(a):
    root=Path(a.root or Path(__file__).resolve().parent);fields=a.fields.split(',') if a.fields else ['C01','C02','C03','C04','C05','C08_INTERFACE_V2','C06','C07'];budget=Budget(root);results=[]
    for field in fields:
        existing=root/'casos'/field/'RESULTADOS.json'
        if existing.exists() and not a.retry:
            result=json.loads(existing.read_text());results.append({'field':field,'status':'SKIP_VERIFIED','result':result['status']});continue
        if budget.elapsed()>=budget.data['science_stop_after_seconds']:
            results.append({'field':field,'status':'NO_EJECUTADO_POR_PRESUPUESTO'});continue
        job=run_child(root,'case_'+field,[a.python,'-I','-B',str(root/'src/worker.py'),'--root',str(root),'--field',field],timeout=240,reserve=900)
        results.append({'field':field,'supervision':job});atomic_json(root/'resultados/EXECUTION_PROGRESS.json',{'elapsed_seconds':budget.elapsed(),'remaining_seconds':budget.remaining(),'results':results})
    print(json.dumps(results,indent=2));return int(any(r.get('supervision',{}).get('status') in ['TECHNICAL_ERROR','TIMEOUT'] for r in results))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root');p.add_argument('--python',default=sys.executable);p.add_argument('--fields');p.add_argument('--retry',action='store_true');raise SystemExit(main(p.parse_args()))
