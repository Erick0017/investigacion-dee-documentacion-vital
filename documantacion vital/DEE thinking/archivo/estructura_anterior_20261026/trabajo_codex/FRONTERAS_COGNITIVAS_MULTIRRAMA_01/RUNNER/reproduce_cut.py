"""Fresh isolated reproduction of the frozen measured cut, never production resume."""
import datetime as D
import json,shutil,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import dee_thinking as dt
from observations import *
from run_multibranch import run,summarize,technical,utc

def reproduce(source,target,config):
    source=Path(source).resolve();target=Path(target).resolve()
    if target.exists():raise ValueError('Replica output already exists; use resume for an unfinished replica, not rebuild.')
    target.mkdir(parents=True);shutil.copytree(source/'RUNNER',target/'RUNNER',ignore=shutil.ignore_patterns('__pycache__'))
    cfg=dict(config);cfg['sealed']=False;cfg.pop('seal_utc',None)
    cfg['reproduction_parent_config_sha256']=sha(source/'CAMPAIGN_CONFIG.json')
    cfg['reproduction_parent_root']=str(source);cfg['start_utc']=utc()
    cfg['deadline_utc']=(D.datetime.now(D.timezone.utc)+D.timedelta(minutes=90)).isoformat()
    dump(target/'CAMPAIGN_CONFIG.json',cfg)
    run(target,cfg)
    for helper in ('run_contingency_replay.py','run_combination.py'):
        subprocess.run([sys.executable,'-I','-B',str(target/'RUNNER'/helper),str(target)],check=True)
    technical(target);summarize(target,cfg)
    comparisons=[]
    for base in ('BRANCHES','COMBINATIONS'):
        pattern='*/*/MEASUREMENTS.json' if base=='BRANCHES' else '*/MEASUREMENTS.json'
        for original in sorted((source/base).glob(pattern)):
            relative=original.relative_to(source);copy=target/relative
            if not copy.exists():raise AssertionError(f'missing reproduced case {relative}')
            a=json.loads(original.read_text(encoding='utf-8'));b=json.loads(copy.read_text(encoding='utf-8'))
            assert a['phi']==b['phi'],str(relative)
            ap=a['checkpoints'][-1];bp=b['checkpoints'][-1]
            ra=dt.Runtime.load_snapshot(str(source/ap['path']));rb=dt.Runtime.load_snapshot(str(target/bp['path']))
            exact=state_equal(ra,rb);assert exact,str(relative)
            comparisons.append({'case':str(relative),'phi_exact':True,'final_tick_raw_clock_exact':exact,
                                'reference_checkpoint_sha256':ap['sha256'],'reproduced_checkpoint_sha256':bp['sha256']})
    dump(target/'REPRODUCTION_COMPARISON.json',{'source_config_sha256':sha(source/'CAMPAIGN_CONFIG.json'),
          'cases_compared':len(comparisons),'comparisons':comparisons,'verified_utc':utc(),
          'scope':'Finite measured panel and full final RAW/uint64 clock equality, not a scientific verdict.'})
    print('REPRODUCED_MEASURED_CASES_EXACT',len(comparisons),flush=True)

if __name__=='__main__':
    source=Path(sys.argv[1]);target=Path(sys.argv[2])
    reproduce(source,target,json.loads((source/'CAMPAIGN_CONFIG.json').read_text(encoding='utf-8')))
