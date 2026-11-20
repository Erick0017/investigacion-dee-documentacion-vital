"""Selective intervention on an already formed native question at T20.
External diagnostic copies, not autonomous repair or new learned MAIN content.
"""
import gzip,hashlib,json,time
from copy import deepcopy
from pathlib import Path
import dee_thinking as d
from dee_thinking import _native as n
from dee_thinking.consolidated import exact_observation
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA/mecanismo'
def put(p,x):
    if p.exists():raise FileExistsError(p)
    b=json.dumps(x,ensure_ascii=False,sort_keys=True).encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def run(mode):
    source=OUT/'MA_U0_SEL_BA_PLUS.T20.deetsnap.gz';parent=d.IntegratedSession.load_snapshot(source)
    at=(18,10,46);before=exact_observation(parent.world.runtime.observe(d.Coordinate(*at)))
    edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*at);edit.raw=0 if mode=='cut'else int(before['raw']);edit.label='Already formed question '+mode+' at T20, clocks preserved'
    world=parent.world.diagnostic_fork([edit],True)
    s=d.IntegratedSession(world,n.preparation_for_world(world),identifier='MA_U0_QUESTION_'+mode.upper(),state=deepcopy(parent._state))
    after=exact_observation(world.runtime.observe(d.Coordinate(*at)));parent_after=exact_observation(parent.world.runtime.observe(d.Coordinate(*at)))
    rows=[]
    for tick in(21,69,70,71,72,75):s.run_until(tick);rows.append({'tick':tick,'physical':s.observe(),'receipts':s.receipts()})
    p=OUT/(s.identifier+'.T75.deetsnap.gz');s.save_snapshot(p,compress=True)
    result={'schema':'MA.U0.formed_question.causal.v1','mode':mode,'identifier':s.identifier,'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_tick':20,'intervention':{'coordinate':at,'before':before,'after':after,'clock_not_edited':before['clock']==after['clock'],'parent_unchanged_selected_site':parent_after==before,'modality':'EXTERNAL_DIAGNOSTIC_COPY'},'rows':rows,'snapshot':{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size},'source_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Cut vs exact-sham already formed request, same future queues including all action/name resources; not an intervention selected by participant.'}
    put(OUT/(s.identifier+'.json.gz'),result)
    acts=next(r for r in rows if r['tick']==72)['physical']['sites']
    print(json.dumps({'mode':mode,'before':before,'after':after,'actions72':{k:v for k,v in acts.items()if k.startswith('action.')}},ensure_ascii=False),flush=True)
if __name__=='__main__':
    put(OUT/'PROTOCOLO_CORTE_PETICION_U0.json',{'before_run_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'parent':'MA_U0_SEL_BA_PLUS.T20.deetsnap.gz','coordinate':[18,10,46],'modes':'cutRAW0clockunchanged vs exactshamRAWsame','futures':'same complete parent agendas, no new sensory/teacher actionselection','criterion':'T72 learned-content transformed plus action should disappear after admitted cut, while generic7 supplies atbothaction sites still arrive. Sham should preserve plus transformed action. No whole-body paralysis inferred from this alone.','scope':'External diagnostic fork, not autonomous access regulation or learning.'})
    run('cut');run('sham')
