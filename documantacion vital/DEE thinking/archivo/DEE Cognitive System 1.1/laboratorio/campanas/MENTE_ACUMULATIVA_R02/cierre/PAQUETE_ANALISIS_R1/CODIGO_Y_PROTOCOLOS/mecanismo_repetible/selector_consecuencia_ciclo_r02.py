"""New P1 architecture revision: actual prepare/verify loop, native access.

The actor is NOT restarted between windows. A single initial generic probe
activates its native material selector. Both memory/sign resources recur with
fixed cadence. The external worker sees only the emitted direction; its fixed
rejection signal returns a generic zero touch, never the correct access/content.
Prepared inactive SEM4 terminators test the unused-resource interference found
in the earlier first-use pilot. The earlier adverse futures remain untouched.
"""
import gzip,hashlib,json,time,subprocess,sys,importlib.util
from pathlib import Path
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import save_world_snapshot,encode_metadata
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('p1_base',HERE/'selector_huella_p1_piloto.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
OUT=b.OUT;N=b.N;E=b.E;D=b.D;V=b.V;add=b.add
ROOT=HERE.parents[3];WORKER=ROOT/'sistema/capacidades/eo02_trabajador_local.py'
def run(label,guard=True,feedback=True,actuator=True,contents=(1,-1),rounds=4):
    original,frame=b.design();placements=list(original.placements)if hasattr(original,'placements')else None
    # Rebuild exactly the known prepared frame, adding zero-state SEM4 only at
    # RAW-empty new positions. Existing SEM4 state1 placements keep their bytes.
    raws={p:int(d.pack_record(1,val,0,0,0,4))for p,val in frame.items()}
    guards=[]
    if guard:
        for v in V:
            for sign in(-1,1):
                p=add(add(E,v,2),(0,0,sign))
                if p not in raws:raws[p]=int(d.pack_record(0,0,0,0,0,4));guards.append(p)
    ps=[]
    for p,raw in sorted(raws.items()):
        x=d.InitialPlacement();x.site=d.Coordinate(*p);x.raw=raw;x.clock=0;x.role='P0 prepared geometry, not acquired selector or content';ps.append(x)
    recipe=d.OrganizationRecipe.research(N,ps,0);recipe.execution=d.TickOptions(d.Backend.LAZY,1);w=d.OrganizationalWorld.create(recipe)
    requests=[];rows=[];jobs=[];pending=None;snapshots=[];work=OUT/(label+'.worker');work.mkdir(parents=True,exist_ok=False)
    def obs(p):return exact_observation(w.runtime.observe(d.Coordinate(*p)))
    def send(name,site,v,t,value):
        if name not in set(w.runtime.channel_names):
            c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(*v);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True
            it=d.InterfaceSpec();it.name=name;it.channel=c;w.declare_interface(it)
        r=w.submit(name,value,t);requests.append({'id':int(r.id),'channel':name,'site':site,'direction':v,'tick':t,'value':value})
    def snapshot(name):
        m=json.loads(json.dumps({'label':label,'revision':'P1 actual consequence cycle R02','N':N,'E':E,'D':D,'V':V,'tick':int(w.runtime.current_tick),'requests':requests,'external_pending':pending,'jobs_completed':len(jobs),'protocol':'one initial probe130; resources both routes/signs every67; rejected actual service gives same touch0 +4 ticks later; no correct route/content in feedback','guard_sites':guards}))
        w.runtime.set_snapshot_metadata('MA02.P1.CYCLE.v1',encode_metadata(m));p=OUT/(label+'.'+name+'.deetsnap.gz');proof=save_world_snapshot(w,p,compress=True)
        x={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'proof':proof};snapshots.append(x);return x
    snapshot('T0')
    for i,(v,sign,t)in enumerate(zip(V,contents,(0,67))):
        h=add(E,v,3);cue=(0,1,0)if i==0 else(1,0,0);teacher=(-cue[0],-cue[1],sign)
        send('experience.cue.'+str(i),add(h,cue,-3),cue,t,5);send('experience.event.'+str(i)+'.'+str(sign),add(h,teacher,-3),teacher,t,11)
    send('generic.activation',add(E,(0,0,1),-3),(0,0,1),130,0)
    for j in range(rounds):
        for i,v in enumerate(V):
            for sign in(-1,1):
                gate=add(add(E,v,4),(0,0,sign));mv=(-v[0],-v[1],0)
                send('generic.gate.'+str(i)+'.'+str(sign),add(gate,mv,-2),mv,136+67*j,7)
    read_ticks={138+67*j:j for j in range(rounds)};end=138+67*(rounds-1)+15
    watch=set(range(129,146))|{0,3,67,70}
    for r in read_ticks:watch.update(range(r-8,r+16))
    for t in range(end+1):
        w.run_until(t)
        if t in watch:
            rows.append({'tick':t,'history_latch':obs(D),'selector':obs(E),'gates':[obs(add(add(E,v,4),(0,0,s)))for v in V for s in(-1,1)],'context':[obs(add(E,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)],'guard_sites':[obs(p)for p in guards]})
        if t==129:snapshot('T129.before_activation')
        if t in read_ticks:
            panel=rows[-1]['gates'];cs=[{'site':o['site'],'sign':o['direction'][2]}for o in panel if o['state']>0 and o['semantic']==1 and o['direction']in([0,0,-1],[0,0,1])]
            command=cs[0]['sign']if len(cs)==1 else None;executed=command if actuator else None;receipt=None;feedback_request=None
            if executed is not None:
                q={'domain':'transaccion','executed_worker':executed,'raw_observations':[17,17],'capacity_credit':0,'pending_transaction':pending,'attempt':len(jobs)+1,'native_tick':t,'output_directory':str(work.resolve())}
                proc=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(WORKER)],input=json.dumps(q),text=True,encoding='utf-8',capture_output=True,timeout=15)
                if proc.returncode:raise RuntimeError('External process failure, not native cognitive failure: '+proc.stderr)
                receipt=json.loads(proc.stdout);pending=receipt['pending_transaction']
                if not receipt['accepted'] and feedback:
                    p=add(D,(0,0,1));direction=(0,1,0);before=len(requests)
                    send('generic.rejection.touch',add(p,direction,-3),direction,t+4,0)
                    feedback_request=requests[before]
            jobs.append({'window':read_ticks[t],'tick':t,'fixed_all_gate_panel':panel,'candidates':cs,'native_command':command,'executed_command':executed,'worker_receipt':receipt,'feedback_touch_request':feedback_request,'scope':'Same fixed four-gate observer; operator starts cadence but does not choose memory, response, worker or feedback strategy. Rejection maps only to generic material contact0.'})
            snapshot('T'+str(t)+'.after_job')
    snapshot('T'+str(end)+'.final')
    result={'schema':'MA02.P1.actual_consequence_cycle.2','identifier':label,'new_T0':True,'parent_biography':'New preparation, no inherited memories or EO02/MA_MAIN transplant','guard':guard,'feedback_enabled':feedback,'actuator_enabled':actuator,'contents_for_evaluator_only':contents,'E':E,'D':D,'V':V,'preparation':[{'site':p,'raw':str(raw)}for p,raw in sorted(raws.items())],'rows':rows,'jobs':jobs,'receipts':[{**x,'receipt':exact_receipt(w.runtime.receipt(x['id']))}for x in requests],'snapshots':snapshots,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'base_sha256':hashlib.sha256((HERE/'selector_huella_p1_piloto.py').read_bytes()).hexdigest(),'worker_sha256':hashlib.sha256(WORKER.read_bytes()).hexdigest(),'scope':'P0 anatomy + acquired two scalar directions + local history-dependent access. Persistent native activation and fixed cadence explicitly prepared. Rejection touch is an actual external consequence transduction, never a host-computed correct route; no general R2 claim.'}
    b.put(OUT/(label+'.json.gz'),result);print(json.dumps({'identifier':label,'jobs':[{'t':j['tick'],'command':j['native_command'],'accepted':j['worker_receipt']['accepted']if j['worker_receipt']else None,'operation':j['worker_receipt']['operation']if j['worker_receipt']else None,'completed':j['worker_receipt']['transaction_completed']if j['worker_receipt']else None}for j in jobs],'final':end},ensure_ascii=False),flush=True)
if __name__=='__main__':
    b.put(OUT/'PROTOCOLO_SELECTOR_CONSECUENCIA_R02.json',{'frozen_before_first_tick_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'question':'Can an actual rejected repeated prepare produce generic touch, alter native selection X→Y and permit learned opposite content to perform later verify, in one continuous life?','architecture_revision':'Only SEM4 state0 resource terminators at E+2v±Z added to prior P1 anatomy; original exact active preparation unchanged; new T0 identity.','frozen_decode':'All four gates, unique pureZ SEM1,138+67j; no token/history/expected target in observer. Four windows include post-success failure, no opportunistic early stop.','environment':'Existing isolated EO02 actual local worker, fixed transaction law, raw observations17,17; native+=prepare opportunity; pending transaction changes service demand without changing native cue. Rejected actual service maps to touch0 at+4, no route or scalar answer transmitted.','controls':['guarded intact','same without new terminators','return omitted','actuator nulled','opposite taught contents under same environmental law'],'criteria':'Report every requested/admitted/answered/correct/incorrect separately. Local consequence-conditioned selection requires common later situation, physical D/context contrast, and actual action consequence contrast. General policy, voluntary initiation and broad transfer not inferred.','horizon':354})
    run('MA02_P1_CYCLE_GUARDED');run('MA02_P1_CYCLE_UNGUARDED',guard=False);run('MA02_P1_CYCLE_RETURN_OMIT',feedback=False);run('MA02_P1_CYCLE_ACTUATOR_NULLED',actuator=False);run('MA02_P1_CYCLE_OPPOSITE',contents=(-1,1))
