"""Launch bounded conventional learners through the campaign supervisor."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from supervisor import run,put


def main():
    p=argparse.ArgumentParser();p.add_argument('--split',choices=['PILOT','RESERVED'],required=True)
    p.add_argument('--model',choices=['B1','B2'],required=True);p.add_argument('--profile',required=True);p.add_argument('--config',type=Path)
    p.add_argument('--all-modes',action='store_true');p.add_argument('--task',choices=['DIRECT','DIRECT_CONTEXT','ORDER']);a=p.parse_args()
    fixtures=ROOT/'configuraciones/comparadores/fixtures_v1';index=json.loads((fixtures/'INDEX.json').read_text(encoding='utf-8'));entries=[]
    destination=ROOT/'resultados/comparadores'/a.profile
    destination.mkdir(parents=True,exist_ok=False)
    for case in index['cases']:
        if case['split']!=a.split or (case['mode']!='paired' and not a.all_modes) or (a.task and case['task']!=a.task):continue
        out=destination/case['case_id'];argv=[sys.executable,'-I','-B',ROOT/'src/comparadores/run.py','--stream',fixtures/case['stream'],
            '--evaluator',fixtures/case['evaluator'],'--model',a.model,'--out',out]
        if a.config:argv.extend(['--config',a.config])
        job=run('comparadores_'+a.profile+'_'+case['case_id'],argv,timeout=120)
        entries.append({'case_id':case['case_id'],'fixture':case,'job_status':job['status'],'exit_code':job['exit_code'],
            'elapsed_seconds':job['elapsed_seconds'],'trajectory':str((out/'TRAJECTORY.json').relative_to(ROOT)),
            'evaluation':str((out/'EVALUATION.json').relative_to(ROOT))})
        put(destination/'INDEX.json',{'schema':'CPC7.comparator.batch.v1','model':a.model,'profile':a.profile,
            'split':a.split,'config':str(a.config.relative_to(ROOT)) if a.config else None,'cases':entries})
    print(json.dumps({'profile':a.profile,'completed':sum(x['exit_code']==0 for x in entries),'jobs':len(entries)}))
    if any(x['exit_code']!=0 for x in entries):raise SystemExit(1)


if __name__=='__main__':main()
