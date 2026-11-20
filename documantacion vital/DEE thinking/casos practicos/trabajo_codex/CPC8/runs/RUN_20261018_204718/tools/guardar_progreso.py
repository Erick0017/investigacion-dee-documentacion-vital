"""Finite campaign progress, with the original monotonic budget unchanged."""
import ctypes,hashlib,json,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];budget=json.loads((ROOT/'BUDGET.json').read_text(encoding='utf-8'))
counter=ctypes.c_longlong();ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(counter))
elapsed=(counter.value-budget['start_qpc'])/budget['qpc_frequency']
jobs=[]
for folder in sorted((ROOT/'jobs').iterdir()):
 if not folder.is_dir():continue
 completed=folder/'COMMAND.json';started=folder/'START.json'
 if completed.exists():r=json.loads(completed.read_text(encoding='utf-8'))
 elif started.exists():r=json.loads(started.read_text(encoding='utf-8'))
 else:continue
 jobs.append({'name':folder.name,'status':r['status'],'exit_code':r.get('exit_code'),'pid':r.get('pid'),'closed':r.get('owned_job_closed',False)})
checkpoints=[]
for p in sorted((ROOT/'resultados').rglob('*.deetsnap.gz')):
 checkpoints.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
state={'campaign':'CPC8','updated_utc':datetime.now(timezone.utc).isoformat(),'original_budget':budget,
 'elapsed_monotonic_seconds':elapsed,'remaining_seconds':max(0,budget['budget_seconds']-elapsed),
 'jobs':jobs,'checkpoints':checkpoints,'runtime_version':'4.5.0','kernel_version':27,
 'completed_fronts':['official identity and82product tests','CP01/CP02 short unchanged-source execution','SEM01 physical hash parity','CORE17 diagnostic replay and standard inputs','integrated E1/SocialI21 through690','selective M1 revision','comparison B1/B2/DEE with private model RNG','zero-load premature join reconstruction','isolated restored query without documentary history'],
 'in_progress':['publication and exact-ZIP independent validation'],
 'scientific_fronts_closed':['contact/consequence three families, finite reader repair and controls','chronological extension1051 and explicit newRIGHT1182','independent regulator and zero-load encounter reconstruction','semantic E1/E2 positive2, E3partial2, noNSM E4/E5 confirmed'],
 'next_task':'Seal final source/configuration and evidence, reproduce exact candidate, preserve external verification and publish. No more experiments and no silent budget restart. Exact post-seal job logs and final consumed time remain outside the immutable ZIP.',
 'future_resume':'Requires a new authorized execution; no indefinite background work promised.'}
(ROOT/'REANUDACION.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'elapsed_seconds':elapsed,'remaining_seconds':state['remaining_seconds'],'checkpoints':len(checkpoints),'unclosed_jobs':[r['name'] for r in jobs if not r['closed']]}))
