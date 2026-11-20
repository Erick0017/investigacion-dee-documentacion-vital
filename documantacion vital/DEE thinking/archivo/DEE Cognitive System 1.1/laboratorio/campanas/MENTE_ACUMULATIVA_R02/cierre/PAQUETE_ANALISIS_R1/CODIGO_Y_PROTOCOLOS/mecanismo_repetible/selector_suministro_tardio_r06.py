"""R06, one fixed late-supply contrast from COMPLETE existing R04 T129 states.
No T0 reconstruction, no old T138 queued feedback, no edits, no target routing.
Four scalar0 SEM4 supports arrive by legal interfaces140, after first use138;
actual rejected service gives fixed diagonal touch0 at+4 (or controlled delay).
Every arm retains the same inherited future requests, reader and horizon354.
"""
import hashlib,json,time,subprocess,sys,importlib.util
from array import array
from pathlib import Path
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import save_world_snapshot,load_world_snapshot,encode_metadata,decode_metadata
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('r05_helpers',HERE/'selector_consecuencia_ciclo_r05.py');h=importlib.util.module_from_spec(sp);sp.loader.exec_module(h)
OUT=h.OUT;N=h.N;E=h.E;D=h.D;V=h.V;add=h.add;WORKER=h.WORKER;TOUCH=(1,1,0)
SITES=[(35,31,34),(35,31,33),(34,31,33),(33,31,33)]
def fingerprint(w):return{'N':int(w.runtime.dimension),'tick':int(w.runtime.current_tick),'RAW_sha256':hashlib.sha256(array('Q',w.runtime.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',w.runtime.clock_copy()).tobytes()).hexdigest()}
def run(label,*,opposite=False,feedback='real',actuator=True):
    parent=OUT/('MA02_P1_R04_'+('OPPOSITE'if opposite else'GUARDED')+'.T129.before_activation.deetsnap.gz');w,_=load_world_snapshot(parent)
    if int(w.runtime.current_tick)!=129:raise ValueError('Exact parent boundary required')
    inherited=decode_metadata(dict(w.runtime.snapshot_metadata_entries)['MA02.P1.CYCLE.v1']);requests=json.loads(json.dumps(inherited['requests']))
    if any(q['channel']=='generic.rejection.touch'for q in requests):raise ValueError('Wrong parent, old return already queued')
    before=fingerprint(w);rows=[];jobs=[];pending=inherited['external_pending'];snaps=[];work=OUT/(label+'.worker');work.mkdir(exist_ok=False)
    def obs(p):return exact_observation(w.runtime.observe(d.Coordinate(*p)))
    pre_support=[obs(p)for p in SITES]
    if any(x['raw']!='0'for x in pre_support):raise ValueError('No overwrite of any raw, even inactive material')
    def send(name,p,v,t,val,*,state=1,semantic=1):
        if name not in set(w.runtime.channel_names):
            c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*p);c.direction=d.Direction(*v);c.state=state;c.semantic=semantic;c.allow_experience=True;c.allow_probe=True
            it=d.InterfaceSpec();it.name=name;it.channel=c;w.declare_interface(it)
        q=w.submit(name,val,t);requests.append({'id':int(q.id),'channel':name,'site':p,'direction':v,'tick':t,'value':val,'state':state,'semantic':semantic})
    for i,p in enumerate(SITES):send('environment.fixed_late_support.'+str(i),p,(0,0,0),140,0,semantic=4)
    def snapshot(name):
        m=json.loads(json.dumps({'identifier':label,'parent':{'name':parent.name,'sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),'tick':129},'tick':int(w.runtime.current_tick),'requests':requests,'external_pending':pending,'jobs_completed':len(jobs),'E':E,'D':D,'V':V,'protocol':'fixed4support140; actual generic rejection touch0; unchanged queued requests/reader; no target or correct route in return'}));w.runtime.set_snapshot_metadata('MA02.P1.R06.v1',encode_metadata(m));p=OUT/(label+'.'+name+'.deetsnap.gz');proof=save_world_snapshot(w,p,compress=True);x={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'proof':proof};snaps.append(x)
    snapshot('T129.queued_supply')
    read_ticks={138+67*j:j for j in range(4)};watch={129,139,140,141,145,146,147,354}
    for t in read_ticks:watch.update(range(max(129,t-8),t+18))
    support139=None;support141=None
    for t in range(129,355):
        w.run_until(t)
        if t==139:support139=[obs(p)for p in SITES]
        if t==141:support141=[obs(p)for p in SITES]
        if t in watch:
            dc=h.neighborhood(w,D);rows.append({'tick':t,'history_latch':obs(D),'selector':obs(E),'gates':[obs(add(add(E,v,4),(0,0,s)))for v in V for s in(-1,1)],'context':h.neighborhood(w,E),'history_context':dc,'symmetry':h.symmetry(dc),'late_supports':[obs(p)for p in SITES]})
        if t in(139,141,145,147):snapshot('T'+str(t))
        if t in read_ticks:
            panel=rows[-1]['gates'];cs=[{'site':p['site'],'sign':p['direction'][2]}for p in panel if p['state']>0 and p['semantic']==1 and p['direction']in([0,0,-1],[0,0,1])];command=cs[0]['sign']if len(cs)==1 else None;executed=command if actuator else None;receipt=None;ret=None
            if executed is not None:
                q={'domain':'transaccion','executed_worker':executed,'raw_observations':[17,17],'capacity_credit':0,'pending_transaction':pending,'attempt':len(jobs)+1,'native_tick':t,'output_directory':str(work.resolve())};p=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(WORKER)],input=json.dumps(q),text=True,encoding='utf8',capture_output=True,timeout=15)
                if p.returncode:raise RuntimeError('External process failure: '+p.stderr)
                receipt=json.loads(p.stdout);pending=receipt['pending_transaction']
                if not receipt['accepted']and feedback!='omit':
                    lag=67 if feedback=='desync'else 0
                    send('generic.actual_rejection.diagonal',add(add(D,(0,0,1)),TOUCH,-3),TOUCH,t+4+lag,0);ret=requests[-1]
            jobs.append({'window':read_ticks[t],'tick':t,'fixed_all_gate_panel':panel,'candidates':cs,'native_command':command,'executed_command':executed,'worker_receipt':receipt,'feedback_touch_request':ret});snapshot('T'+str(t)+'.after_job')
    snapshot('T354.final')
    result={'schema':'MA02.P1.actual_consequence_cycle.2','identifier':label,'revision':'R06 late supply','new_T0':False,'parent':{'path':str(parent),'sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),'tick':129},'inherited_native_fingerprint':before,'inherited_requests_before_late_supply':inherited['requests'],'pre_support_raw129':pre_support,'pre_support139':support139,'post_support141':support141,'feedback_mode':feedback,'actuator_enabled':actuator,'opposite_history_for_evaluator_only':opposite,'rows':rows,'jobs':jobs,'receipts':[{**q,'receipt':exact_receipt(w.runtime.receipt(q['id']))}for q in requests],'snapshots':snaps,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Four generic fixed-calendar prepared supports, same in all arms, not acquired growth. Restored exact learned parent history and future queues. Contact strategy contains no bank/content answer. A changed field alone is not useful policy or R2.'}
    h.b.b.put(OUT/(label+'.json.gz'),result);print(json.dumps({'identifier':label,'jobs':[{'tick':j['tick'],'command':j['native_command'],'accepted':j['worker_receipt']['accepted']if j['worker_receipt']else None}for j in jobs],'D147':next(r['history_latch']for r in rows if r['tick']==147),'E147':next(r['selector']['direction']for r in rows if r['tick']==147),'support_statuses':[x['receipt']['status']for x in result['receipts']if x['channel'].startswith('environment.fixed_late_support')]},ensure_ascii=False),flush=True)
if __name__=='__main__':
    source=OUT/'PROTOCOLO_SELECTOR_CONSECUENCIA_R05.json';old=json.loads(source.read_text(encoding='utf8'));s=old['existing_D_symmetry'];virtual=[]
    for phase,sites in[('actual',set()),('four_supports',set(SITES)),('four_supports_and_P',set(SITES)|{add(D,(0,0,1))})]:
        virtual.append({'phase':phase,'matches':sum((r['positive_active']or tuple(r['positive']['site'])in sites)==(r['negative_active']or tuple(r['negative']['site'])in sites)for r in s['pairs']),'scope':'Frozen-neighborhood algebra only, no predicted evolution treated as observation'})
    h.b.b.put(OUT/'PROTOCOLO_SELECTOR_SUMINISTRO_TARDIO_R06.json',{'frozen_before_new_ticks_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'bounded_family':'One R06, no parameter search; horizon354 fixed','question':'Does fixed late material supply avoid the acquisition interference of T0 supply and permit actual generic consequence to alter native access?','parents':'Exact R04 guarded/opposite complete T129, original queued query130 and all marker windows retained. Not T138 which already has old queued feedback.','preidentified_missing_pairs':SITES,'source_control_neighborhood':old['existing_D_symmetry'],'algebraic_necessary_check':virtual,'late_interface':{'tick':140,'state':1,'semantic':4,'direction':[0,0,0],'payload':0,'same_every_arm':True,'reject_instead_of_overwrite':True},'return':{'condition':'actual external worker rejection only','source':add(add(D,(0,0,1)),TOUCH,-3),'direction':TOUCH,'payload':0,'lag':4,'desync_control_additional_lag':67,'never_transmits_correct_route_or_content':True},'evaluation':'Fixed inherited four all-gate windows138,205,272,339; fieldD/E measured147 is a mechanism witness, not a substituted success metric. Architecture externally fixed after141.','arms':['guarded actual','guarded omit','opposite actual','opposite omit','opposite null actuator','opposite desynchronized return'],'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'dependency_R05_sha256':hashlib.sha256((HERE/'selector_consecuencia_ciclo_r05.py').read_bytes()).hexdigest()})
    run('MA02_P1_R06_GUARDED');run('MA02_P1_R06_GUARDED_OMIT',feedback='omit');run('MA02_P1_R06_OPPOSITE',opposite=True);run('MA02_P1_R06_OPPOSITE_OMIT',opposite=True,feedback='omit');run('MA02_P1_R06_OPPOSITE_NULLED',opposite=True,actuator=False);run('MA02_P1_R06_OPPOSITE_DESYNC',opposite=True,feedback='desync')
