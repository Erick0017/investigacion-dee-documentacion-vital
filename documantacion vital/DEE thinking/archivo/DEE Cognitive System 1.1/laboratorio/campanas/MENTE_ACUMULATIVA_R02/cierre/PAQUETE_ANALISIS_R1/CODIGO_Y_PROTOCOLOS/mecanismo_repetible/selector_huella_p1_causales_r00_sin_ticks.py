"""Prospective selective controls for the previously frozen P1 first-use pilot.
No edits to the executed pilot. All diagnostic cuts occur on identified copies
of full queued states at T129; the protected worlds and parent stay unchanged.
"""
import gzip,hashlib,json,time,importlib.util
from pathlib import Path
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import encode_metadata,save_world_snapshot
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('ma02_p1_original',HERE/'selector_huella_p1_piloto.py');base=importlib.util.module_from_spec(sp);sp.loader.exec_module(base)
OUT=base.OUT;N=base.N;E=base.E;D=base.D;V=base.V;add=base.add;put=base.put
def run(label,touch=True,contents=(1,-1),query_tick=130,edit_kind=None):
    recipe,frame=base.design();w=d.OrganizationalWorld.create(recipe);requests=[];rows=[];intervention=None
    def obs(p):return exact_observation(w.runtime.observe(d.Coordinate(*p)))
    def send(name,site,v,t,value):
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(*v);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True
        it=d.InterfaceSpec();it.name=name;it.channel=c;w.declare_interface(it)
        r=w.submit(name,value,t);requests.append({'id':int(r.id),'port':name,'site':site,'direction':v,'tick':t,'payload':value})
    def snap(name):
        w.runtime.set_snapshot_metadata('MA02.P1.SELECTOR.CAUSAL.v1',encode_metadata({'label':label,'N':N,'E':E,'D':D,'V':V,'tick':int(w.runtime.current_tick),'requests':requests,'scope':'External diagnostic cut identified separately. Operational pending interfaces retained in Runtime.'}))
        p=OUT/(label+'.'+name+'.deetsnap.gz');proof=save_world_snapshot(w,p,compress=True)
        return{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'proof':proof}
    initial=snap('T0')
    for i,(v,sign,t)in enumerate(zip(V,contents,(0,67))):
        h=add(E,v,3);cue=(0,1,0)if i==0 else(1,0,0);teacher=(-cue[0],-cue[1],sign)
        send('experience.cue.'+str(i),add(h,cue,-3),cue,t,5);send('experience.event.'+str(i),add(h,teacher,-3),teacher,t,11)
    if touch:
        p=add(D,(0,0,1));v=(0,1,0);send('generic.touch',add(p,v,-3),v,10,0)
    send('generic.current.query',add(E,(0,0,1),-3),(0,0,1),query_tick,0)
    for i,v in enumerate(V):
        for sign in(-1,1):
            gate=add(add(E,v,4),(0,0,sign));mv=(-v[0],-v[1],0)
            send('generic.gate.'+str(i)+'.'+str(sign),add(gate,mv,-2),mv,query_tick+6,7)
    parent=None
    for t in sorted({0,3,14,70,128,129,query_tick-1,*range(query_tick,query_tick+16)}):
        w.run_until(t)
        if t==129:
            parent=snap('T129.queued_parent')
            if edit_kind:
                if edit_kind.startswith('history'):site=D
                elif edit_kind.startswith('content'):
                    # M1 formed at T70. Follow its declared vertical support,
                    # then require the expected physical carrier before editing.
                    site=add(add(E,V[1],3),(0,0,contents[1]),129-70)
                else:raise ValueError(edit_kind)
                before=obs(site)
                if edit_kind.startswith('history') and before['semantic']!=7:raise RuntimeError('Missing formed history latch')
                if edit_kind.startswith('content') and not(before['semantic']==1 and before['direction']==[0,0,contents[1]] and before['s_reg']==16):raise RuntimeError('Expected selected content not found')
                sham=edit_kind.endswith('sham');edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site);edit.raw=int(before['raw'])if sham else 0;edit.clock=int(before['clock']);edit.label='MA02 P1 exact sham'if sham else'MA02 P1 selective '+edit_kind+' diagnostic cut'
                w=w.diagnostic_fork([edit],True)
                intervention={'kind':edit_kind,'site':site,'tick':t,'pre':before,'post':obs(site),'parent_snapshot':parent,'scope':'External diagnostic copy, not learned repair.'}
        rows.append({'tick':t,'history_latch':obs(D),'selector':obs(E),'gates':[obs(add(add(E,v,4),(0,0,s)))for v in V for s in(-1,1)],'local_context':[obs(add(E,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
    read_tick=query_tick+8;read=next(r for r in rows if r['tick']==read_tick);cs=[{'site':p['site'],'sign':p['direction'][2]}for p in read['gates']if p['state']>0 and p['semantic']==1 and p['direction']in([0,0,-1],[0,0,1])]
    result={'schema':'MA02.native_history_selector.causal.1','identifier':label,'new_T0':True,'history_touch':touch,'contents_for_evaluator_only':contents,'query_tick':query_tick,'read_tick':read_tick,'intervention':intervention,'initial_snapshot':initial,'queued_parent_snapshot':parent,'final_snapshot':snap('T'+str(query_tick+15)),'rows':rows,'candidates':cs,'decoded_sign':cs[0]['sign']if len(cs)==1 else None,'receipts':[{**r,'receipt':exact_receipt(w.runtime.receipt(r['id']))}for r in requests],'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'base_source_sha256':hashlib.sha256((HERE/'selector_huella_p1_piloto.py').read_bytes()).hexdigest(),'scope':'First native access only. P0 gradient anatomy, P1 past-touch-dependent selection; not consequence utility or repeated access.'}
    put(OUT/(label+'.json.gz'),result);print(json.dumps({'identifier':label,'candidates':cs,'selector':next(r['selector']['direction']for r in rows if r['tick']==query_tick+4),'intervention':edit_kind},ensure_ascii=False),flush=True)
if __name__=='__main__':
    put(OUT/'PROTOCOLO_SELECTOR_HUELLA_P1_CAUSALES.json',{'frozen_before_ticks_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'hypotheses':'Cut formed D removes historical selection but not acquired content; exact sham retains. Cut selected content removes signed answer but selector Y remains; sham retains. Reserve +67 query phase tests fixed new timing with same reader and anatomy.','controls':['history_cut','history_sham','content_cut','content_sham','touch_reserve197','omit_touch_reserve197'],'reader':'all four pureZ SEM1 gates at query+8; unique or abstention, never infer output from expected history/content','scope':'Diagnostic interventions external; reserved timing within previously declared N67 memory phase, not arbitrary-interval temporal generality.'})
    for k in('history_cut','history_sham','content_cut','content_sham'):run('MA02_P1_CAUSAL_'+k.upper(),edit_kind=k)
    run('MA02_P1_RESERVE_TOUCH_197',query_tick=197);run('MA02_P1_RESERVE_NO_TOUCH_197',touch=False,query_tick=197)
