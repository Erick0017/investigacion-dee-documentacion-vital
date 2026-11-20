"""Seal the reached internal A cut; this is not final delivery or a PASS."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];S=ROOT/'sistema';EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    dest=HERE/'CIERRE_INTERNO_A.json'
    if dest.exists():raise FileExistsError('A close already sealed, do not reset its B budget')
    b=json.loads((HERE/'PRESUPUESTO.json').read_bytes());rec=json.loads((S/'estado/vidas/MU_MAIN/VIDA.json').read_bytes());snap=S/rec['snapshot']
    if rec['physical']['tick']!=16634 or sha(snap)!='b6c02df2e804b167b85f9e8fd849e091227b81ccfd7a49e442f67156944c71ad':raise ValueError('Expected reached coherent service cut not found; never substitute another future')
    if (S/'estado/locks/MU_MAIN.lock').exists():raise RuntimeError('A writer remains active')
    checks={}
    for name,r in b['protected'].items():checks[name]={'record_unchanged':sha(r['record'])==r['record_sha256'],'snapshot_unchanged':sha(r['snapshot'])==r['snapshot_sha256']}
    if not all(all(q.values())for q in checks.values()):raise ValueError('A protected original changed; diagnose before B')
    now=datetime.now(timezone.utc);limit=min(datetime.fromisoformat(b['total_limit_utc']),now+timedelta(hours=8))
    calc=EV/'RECALCULO_CORTE_A.json';d=json.loads(calc.read_bytes())
    if d['errors']:raise ValueError('A archived recalculation contains disagreements')
    data={'block_A_closed':True,'block':'A','status':'PARTIAL_INTEGRATION_REACHED_AND_PRESERVED_NOT_GLOBAL_PASS',
      'closed_utc':now.isoformat(),'closed_monotonic':time.monotonic(),'block_B_limit_utc':limit.isoformat(),
      'block_B_deadline_monotonic':time.monotonic()+(limit-now).total_seconds(),'original_budget_file_sha256':sha(HERE/'PRESUPUESTO.json'),
      'life':'MU_MAIN','parent':'MA02_MAIN_5 T11196 exact full fork','N':67,'tick':rec['physical']['tick'],'snapshot':rec['snapshot'],'snapshot_sha256':sha(snap),'physical':rec['physical'],
      'protected_identity_checks':checks,'active_pointer_unchanged':sha(S/'estado/ACTIVO.json')==b['active_record_sha256'],
      'demonstrated':['Same life acquired sixth relation and selectively revised beta; five others retained','All six read after actual prepare/commit and after own scalar-selector experience/action/consequence cycle','Native repeatable P1 selector, three useful reserved actual file workers versuszero/three omitted-return control','Persistent same-life service executed two new useful workers and three old-memory uses, idle evolution, explicit consistent technical close','Full snapshot and pending transport state preserved, no hidden rerun of an uncertain action'],
      'partial_or_negative':['Old memory context choice remains operator P0, not native learned bank routing','Supplying two banks without cue impaired all six responses; native gating not solved','Fission calibration preserved scalar but recurrent expression blocked; prior early reader kept as negative','Fixed failureA asymmetry and phase are P0; no general reversible policy/R2 or learned query initiative','No non-consuming composition of the old six sign associations demonstrated; B will investigate feasible joint use, not assume it'],
      'recalculation':{'path':str(calc),'sha256':sha(calc),'raw_observations_checked':d['raw_observations_checked'],'readers_reconstructed':d['readers_reconstructed'],'errors':d['errors']},
      'operating_state':'Service epoch explicitly closed, no pending/uncertain transport action. CLI may continue this exact world; next service must declare a new epoch rather than replay old calls.',
      'next':'Block B runs from exact diagnostic forks before introducing new native raw-tree interactions in MAIN. No missing prompt or further authorization required.'}
    dest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(data,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
