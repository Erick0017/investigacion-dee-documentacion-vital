"""Critical-time diagnostics from the existing complete queued T129 parent.
No reconstructed biography and no advancement of a protected operational life.
The earlier T129 cut regenerated at T130: retained as an informative negative.
"""
import gzip,hashlib,json,time,importlib.util
from pathlib import Path
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import load_world_snapshot,save_world_snapshot,encode_metadata
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('base_p1',HERE/'selector_huella_p1_piloto.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
OUT=b.OUT;E=b.E;D=b.D;V=b.V;add=b.add
PARENT=OUT/'MA02_P1_CAUSAL_HISTORY_CUT.T129.queued_parent.deetsnap.gz'
def run(label,kind):
    w,_=load_world_snapshot(PARENT);rows=[]
    def obs(p):return exact_observation(w.runtime.observe(d.Coordinate(*p)))
    w.run_until(133);pre=obs(D)
    ed=d.ResearchStateEdit();ed.coordinate=d.Coordinate(*D);ed.clock=int(pre['clock']);ed.label='MA02 P1 critical-time diagnostic '+kind
    ed.raw=int(pre['raw'])if kind=='sham'else(0 if kind=='cut'else int(d.pack_record(0,0,0,0,0,4)))
    w=w.diagnostic_fork([ed],True);post=obs(D)
    for t in range(133,146):
        w.run_until(t);rows.append({'tick':t,'history_latch':obs(D),'selector':obs(E),'gates':[obs(add(add(E,v,4),(0,0,s)))for v in V for s in(-1,1)],'local_context':[obs(add(E,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
    gate=next(r['gates']for r in rows if r['tick']==138);cs=[{'site':p['site'],'sign':p['direction'][2]}for p in gate if p['state']>0 and p['semantic']==1 and p['direction']in([0,0,-1],[0,0,1])]
    path=OUT/(label+'.T145.deetsnap.gz');w.runtime.set_snapshot_metadata('MA02.P1.CRITICAL.v1',encode_metadata({'label':label,'parent_sha256':hashlib.sha256(PARENT.read_bytes()).hexdigest(),'tick':145,'diagnostic_kind':kind}));proof=save_world_snapshot(w,path,compress=True)
    r={'schema':'MA02.native_history_selector.critical.1','identifier':label,'parent':{'path':str(PARENT),'sha256':hashlib.sha256(PARENT.read_bytes()).hexdigest(),'tick':129},'intervention':{'tick':133,'site':D,'kind':kind,'pre':pre,'post':post,'scope':'External diagnostic copy only. cut clears one formed D for the critical pre134 step; state0SEM4 additionally prevents reconstitution as a separate diagnostic, not native forgetting.'},'read_tick':138,'rows':rows,'candidates':cs,'decoded_sign':cs[0]['sign']if len(cs)==1 else None,'final_snapshot':{'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'proof':proof},'receipts':[exact_receipt(w.runtime.receipt(i))for i in range(1,11)],'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'First-use causal role of formed D in the directional gradient; broader trace may regenerate it, so D is not asserted to be sole historical support.'}
    b.put(OUT/(label+'.json.gz'),r);print(json.dumps({'identifier':label,'selector134':next(r['selector']['direction']for r in rows if r['tick']==134),'candidates':cs,'D134':next(r['history_latch']['semantic']for r in rows if r['tick']==134)},ensure_ascii=False),flush=True)
if __name__=='__main__':
    b.put(OUT/'PROTOCOLO_SELECTOR_P1_CRITICAL.json',{'frozen_before_ticks_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'parent':str(PARENT),'observation_motivating_revision':'T129 D cut regrew immediately at130; negative remains in original archive.','critical_intervention':'Fork exact queued parent129; advance133 identical; cut D or exact sham before134 direction update, fixed gate138. Additional diagnostic state0SEM4 tests preventing regrowth, never an action of the participant.','reader':'unchanged fixed all-four pureZ gate138','scope':'Critical causal gradient component, not sole history store or general recovery policy.'})
    run('MA02_P1_CRITICAL_CUT','cut');run('MA02_P1_CRITICAL_SHAM','sham');run('MA02_P1_CRITICAL_BLOCK_REBIRTH','block_rebirth')
