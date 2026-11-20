"""Bounded R05: repair the identified return-to-trace physical link.
Two explicit P0 factors: three missing active counterparts outside E Moore;
generic zero-contact re-routed around a measured SEM4 interception. No target,
correct bank or answer enters this fixed return codec. R1 finite lives untouched.
"""
import hashlib,json,time,subprocess,sys,importlib.util
from pathlib import Path
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import save_world_snapshot,load_world_snapshot,encode_metadata
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('r04_for_r05',HERE/'selector_consecuencia_ciclo_r04.py');r4=importlib.util.module_from_spec(sp);sp.loader.exec_module(r4)
b=r4.r.c;OUT=b.OUT;N=b.N;E=b.E;D=b.D;V=b.V;add=b.add;WORKER=b.WORKER
CLOSURES=[(2,-2,1),(2,-2,0),(1,-2,0)];TOUCH=(1,1,0)
def neighborhood(w,p):return[exact_observation(w.runtime.observe(d.Coordinate(*add(p,(x,y,z)))))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]
def symmetry(points):
    by={tuple(p['site']):p for p in points};pairs=[];active=0
    for v in[(x,y,z)for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)if(x,y,z)>(0,0,0)]:
        p=by[add(D,v)];n=by[add(D,v,-1)];pa=p['state']>0 and p['semantic']!=5;na=n['state']>0 and n['semantic']!=5;active+=pa+na
        pairs.append({'offset':v,'positive':p,'negative':n,'positive_active':pa,'negative_active':na,'matched':pa==na})
    return{'active_neighbors':active,'pairs_matched':sum(p['matched']for p in pairs),'pairs_total':13,'pairs':pairs}
def prepared():
    _,frame=b.b.design()
    for offset in CLOSURES:
        p=add(E,offset)
        if p in frame:raise ValueError('Preserve previous prepared material, do not overwrite')
        if max(abs(x)for x in offset)<=1:raise ValueError('Counterpart must not directly modify E gradient')
        frame[p]=0
    ps=[]
    for p,val in sorted(frame.items()):
        x=d.InitialPlacement();x.site=d.Coordinate(*p);x.raw=d.pack_record(1,val,0,0,0,4);x.clock=0;x.role='P0 declared R05 anatomy, not acquired content';ps.append(x)
    # Same resource terminators as the preceding guarded revisions.
    for v in V:
        for sign in(-1,1):
            p=add(add(E,v,2),(0,0,sign))
            if p not in frame:
                x=d.InitialPlacement();x.site=d.Coordinate(*p);x.raw=d.pack_record(0,0,0,0,0,4);x.clock=0;x.role='Prepared inactive resource terminator';ps.append(x)
    recipe=d.OrganizationRecipe.research(N,ps,0);recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    return recipe,ps
def run(label,*,feedback=True,actuator=True,contents=(1,-1)):
    recipe,ps=prepared();w=d.OrganizationalWorld.create(recipe);requests=[];rows=[];jobs=[];pending=None;snapshots=[];work=OUT/(label+'.worker');work.mkdir(exist_ok=False)
    def obs(p):return exact_observation(w.runtime.observe(d.Coordinate(*p)))
    def send(name,p,v,t,val):
        if name not in set(w.runtime.channel_names):
            c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*p);c.direction=d.Direction(*v);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True
            it=d.InterfaceSpec();it.name=name;it.channel=c;w.declare_interface(it)
        q=w.submit(name,val,t);requests.append({'id':int(q.id),'channel':name,'site':p,'direction':v,'tick':t,'value':val})
    def snap(name):
        m=json.loads(json.dumps({'identifier':label,'tick':int(w.runtime.current_tick),'revision':'R05 three opposite activity closures and re-routed generic contact','requests':requests,'external_pending':pending,'jobs':len(jobs),'E':E,'D':D,'V':V,'codec':'rejected actual service -> zero material diagonal touch at+4; no bank/content code'}));w.runtime.set_snapshot_metadata('MA02.P1.R05.v1',encode_metadata(m));p=OUT/(label+'.'+name+'.deetsnap.gz');proof=save_world_snapshot(w,p,compress=True);x={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'proof':proof};snapshots.append(x)
    snap('T0')
    for i,(v,sign,t)in enumerate(zip(V,contents,(0,67))):
        h=add(E,v,3);cue=(0,1,0)if i==0 else(1,0,0);teacher=(-cue[0],-cue[1],sign)
        send('experience.cue.'+str(i),add(h,cue,-3),cue,t,5);send('experience.event.'+str(i)+'.'+str(sign),add(h,teacher,-3),teacher,t,11)
    send('generic.activation',add(E,(0,0,1),-3),(0,0,1),130,0)
    for j in range(4):
        for i,v in enumerate(V):
            for sign in(-1,1):
                gate=add(add(E,v,4),(0,0,sign));mv=(-v[0],-v[1],0);send('generic.gate.'+str(i)+'.'+str(sign),add(gate,mv,-2),mv,136+67*j,7)
    read_ticks={138+67*j:j for j in range(4)};watch={0,3,67,70,129}
    for t in read_ticks:watch.update(range(t-8,t+17))
    for t in range(355):
        w.run_until(t)
        if t in watch:
            dcontext=neighborhood(w,D);rows.append({'tick':t,'history_latch':obs(D),'selector':obs(E),'gates':[obs(add(add(E,v,4),(0,0,s)))for v in V for s in(-1,1)],'context':neighborhood(w,E),'history_context':dcontext,'symmetry':symmetry(dcontext)})
        if t==129:snap('T129')
        if t in read_ticks:
            panel=rows[-1]['gates'];cs=[{'site':o['site'],'sign':o['direction'][2]}for o in panel if o['state']>0 and o['semantic']==1 and o['direction']in([0,0,-1],[0,0,1])];command=cs[0]['sign']if len(cs)==1 else None;executed=command if actuator else None;receipt=None;returned=None
            if executed is not None:
                q={'domain':'transaccion','executed_worker':executed,'raw_observations':[17,17],'capacity_credit':0,'pending_transaction':pending,'attempt':len(jobs)+1,'native_tick':t,'output_directory':str(work.resolve())};p=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(WORKER)],input=json.dumps(q),capture_output=True,text=True,encoding='utf8',timeout=15)
                if p.returncode:raise RuntimeError(p.stderr)
                receipt=json.loads(p.stdout);pending=receipt['pending_transaction']
                if not receipt['accepted']and feedback:
                    send('generic.rejection.touch',add(add(D,(0,0,1)),TOUCH,-3),TOUCH,t+4,0);returned=requests[-1]
            jobs.append({'window':read_ticks[t],'tick':t,'fixed_all_gate_panel':panel,'candidates':cs,'native_command':command,'executed_command':executed,'worker_receipt':receipt,'feedback_touch_request':returned});snap('T'+str(t)+'.after_job')
    snap('T354.final')
    x={'schema':'MA02.P1.actual_consequence_cycle.2','identifier':label,'new_T0':True,'revision':'R05','feedback_enabled':feedback,'actuator_enabled':actuator,'contents_for_evaluator_only':contents,'rows':rows,'jobs':jobs,'receipts':[{**q,'receipt':exact_receipt(w.runtime.receipt(q['id']))}for q in requests],'snapshots':snapshots,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Two P0 engineering factors tested jointly; same resources and anatomy in return/omit/nulled, no separate attribution of each factor. Contact contains no correct strategy. Only subsequent native useful action would establish the missing functional consequence loop.'}
    b.b.put(OUT/(label+'.json.gz'),x);print(json.dumps({'identifier':label,'jobs':[{'tick':j['tick'],'command':j['native_command'],'accepted':j['worker_receipt']['accepted']if j['worker_receipt']else None}for j in jobs],'trace_births':[r['tick']for r in rows if r['history_latch']['semantic']==7]},ensure_ascii=False),flush=True)
if __name__=='__main__':
    parent=OUT/'MA02_P1_R04_OPPOSITE.T138.after_job.deetsnap.gz';w,_=load_world_snapshot(parent);control=symmetry(neighborhood(w,D));route=[exact_observation(w.runtime.observe(d.Coordinate(*add(add(D,(0,0,1)),(0,1,0),k))))for k in(-3,-2,-1,0)]
    b.b.put(OUT/'PROTOCOLO_SELECTOR_CONSECUENCIA_R05.json',{'frozen_before_first_new_tick_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'existing_control_snapshot':{'name':parent.name,'sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),'tick':int(w.runtime.current_tick)},'existing_D_symmetry':control,'old_contact_route_with_SEM4_interceptor':route,'two_prepared_factors':{'closures_about_E':CLOSURES,'closure_scalar':0,'closure_semantic':4,'closure_state':1,'new_contact_direction':TOUCH,'new_contact_payload':0,'new_contact_source':add(add(D,(0,0,1)),TOUCH,-3)},'predictions':'Opposite actual rejected action may now form D after contact, changing native selection; omission/nulled should distinguish consequence effect from spontaneous XNOR. No useful decision or P2 claim unless subsequent output is valid and useful.','arms':['guarded intact','return omitted same actual service','actuator nulled','opposite acquired contents same actual law','opposite contents return omitted'],'fixed_read_windows':[138,205,272,339],'horizon':354,'revision_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'dependent_sources':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in[HERE/'selector_consecuencia_ciclo_r02.py',HERE/'selector_consecuencia_ciclo_r03.py',HERE/'selector_consecuencia_ciclo_r04.py',HERE/'selector_huella_p1_piloto.py']},'scope':'One bounded R05; protected R1 finite lives and MA02_MAIN not touched. No posthoc reader or answer route changes.'})
    run('MA02_P1_R05_GUARDED');run('MA02_P1_R05_RETURN_OMIT',feedback=False);run('MA02_P1_R05_ACTUATOR_NULLED',actuator=False);run('MA02_P1_R05_OPPOSITE',contents=(-1,1));run('MA02_P1_R05_OPPOSITE_OMIT',feedback=False,contents=(-1,1))
