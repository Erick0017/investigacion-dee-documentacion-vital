"""MA02: one prepared common codec, selective circulating content and native use.

No stored answer table is read. The fixed ten-site decoder has no token argument.
Four contexts are initially admitted; a fifth requires declared preparation.
All execution state remains in the official whole-world snapshot metadata.
Routing is prepared P0; content and its later physical use depend on history P1.
"""
from pathlib import Path
import hashlib,json,subprocess,sys,time
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from dee_thinking.consolidated import exact_observation,exact_receipt
from app.native_tools import physical

KEY='DEE.Cognitive.System.1.1.MENTE_ACUMULATIVA_R02.v1'
OLD_KEY='MA.COMMON.ROUTER.R02.v1'
REVISION='MA02.restorative_common_access.R1.2'
N=67;I=(33,33,33)
TOKENS={'alfa':(1,0,0),'beta':(0,1,0),'gamma':(1,1,0),'delta':(-1,1,0)}
BASE_TOKENS=dict(TOKENS)
TOKENS['epsilon']=(1,-1,0)
TOKENS['zeta']=(-1,-1,0)
def codec(a):
    """Old lives retain their fixed ten gates. Zeta needs explicit anatomy.
    Enabling a public context is P0, not content/strategy selection by outcome.
    """
    return {k:v for k,v in TOKENS.items() if k!='zeta' or 'zeta' in get(a).get('enabled_contexts',[])}
def add(a,v,k=1):return tuple((a[j]+k*v[j])%N for j in range(3))
def pos(v,k,z=0):
    a=add(I,v,k);return(a[0],a[1],(a[2]+z)%N)
def view(a,p):return exact_observation(a.world.runtime.observe(d.Coordinate(*p)))
def get(a):
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:raise ValueError('This life has no admitted MA02 contract; do not substitute a new or different individual')
    if int(a.world.runtime.dimension)!=N:raise ValueError('MA02 only N67')
    return decode_metadata(entries[KEY])
def save(a,m):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))
def admit(a):
    if KEY in dict(a.world.runtime.snapshot_metadata_entries):return state(a)
    e=dict(a.world.runtime.snapshot_metadata_entries)
    if OLD_KEY not in e or int(a.world.runtime.dimension)!=N:raise ValueError('Requires complete validated MA02 restorative candidate state')
    old=decode_metadata(e[OLD_KEY])
    if old.get('recipe')!='MA02 restorative excursion R03B':raise ValueError('Wrong preparation; no compatibility inferred from N alone')
    for v in BASE_TOKENS.values():
        for sg in(-1,1):
            for k,z in[(2,1),(2,2),(5,3)]:
                o=view(a,pos(v,k,z*sg))
                if o['semantic']!=4 or o['direction']!=[0,0,0]:raise ValueError('Prepared resource terminator absent or transformed')
    m={'revision':REVISION,'origin_label':old['label'],'admitted_tick':a.tick,'enabled_contexts':list(BASE_TOKENS),'episodes':0,'requests':0,'jobs':0,'external_pending':None,'assistance':'Fixed typed context codec and six generic resource routes; operator initiates requests. No learned routing-policy assertion.','decoder':'Unique state>0 SEM1 pureZ at fixed gate sites, no token or expected answer in decoder'}
    save(a,m);return state(a)
def state(a):
    m=get(a)
    return {'revision':REVISION,'INSTRUMENTO':{'tick':a.tick,'physical':physical(a.world,occupation=True),'codec':{k:list(v)for k,v in codec(a).items()},'fixed_decoder_gate_sites':2*len(codec(a)),'admitted_contexts':m.get('enabled_contexts',list(BASE_TOKENS)),'request_counter_scope':'Operational primary-query/teaching counters only; actual outcome-return requests are separate in each job receipt. Not a complete admission denominator.','next_admissible_phase_tick':phase(a.tick),'endogenous_N67_period_not_universal_kernel_period':True},'ENTE':{'type':'New T0 N67 composed single-world circulating supports; four initial contexts, optional fifth/sixth externally prepared and separately taught. Generic readers and terminators are prepared; not historical E1 continuation','learned_content_not_decoded_from_metadata':True,'operational':m},'INTERPRETACION':{'P0':'Prepared context addressing, phase alignment and resource timing','P1':'Physical signed contents and selective revision acquired by encounters','P2_R2':'Not established by this contract'}}
def phase(t):return ((int(t)//N)+1)*N
def extend(a,context='epsilon'):
    """Declared anatomical preparation through legal state0 SEM4 inputs.
    No learned content is transferred or written; epsilon is taught later.
    """
    m=get(a);enabled=m.get('enabled_contexts',list(BASE_TOKENS))
    if context not in('epsilon','zeta'):raise ValueError('Only declared epsilon/zeta anatomical extensions')
    if context in enabled:raise ValueError('Context preparation already admitted; no silent reinstallation')
    v=TOKENS[context];at=a.tick+2;rs=[];rows=[]
    for sg in(-1,1):
        for k,z in[(2,1),(2,2),(5,3)]:
            site=pos(v,k,z*sg);pre=view(a,site)
            if int(pre['raw'])!=0:raise ValueError('Preparation will not overwrite nonzero RAW, including inactive fields: '+str(site))
            name='MA02.geometry.'+context+'.'+str(k)+'.'+str(z*sg)
            c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(0,0,0);c.state=0;c.semantic=4;c.allow_experience=True;c.allow_probe=False
            it=d.InterfaceSpec();it.name=name;it.channel=c;a.world.declare_interface(it)
            rid=a.world.submit(name,0,at);rs.append({'id':int(rid.id),'channel':name,'site':list(site),'direction':[0,0,0],'value':0,'state':0,'semantic':4,'tick':at});rows.append({'site':list(site),'pre':pre})
    a.run_until(at+1)
    for x in rows:x['post']=view(a,x['site'])
    if any(x['receipt']['status']!='applied'for x in receipts(a,rs)):raise ValueError('Preparation rejected; keep reached state and do not claim extension complete')
    m['enabled_contexts']=[*enabled,context];m['revision']=REVISION;m[context+'_external_preparation_tick']=at;save(a,m)
    return {'classification':'External anatomical extension P0 of same full life, not self-growth or learned content','context':context,'rows':rows,'requests':receipts(a,rs),'state':state(a)}
def submit(a,name,p,v,value,t,requests):
    if type(value)is not int or not 0<=value<=512:raise ValueError('Bounded exact native resource')
    names=set(a.world.runtime.channel_names)
    if name not in names:
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*p);c.direction=d.Direction(*v);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True
        it=d.InterfaceSpec();it.name=name;it.channel=c;a.world.declare_interface(it)
    rid=a.world.submit(name,value,t)
    requests.append({'id':int(rid.id),'channel':name,'site':list(p),'direction':list(v),'value':value,'tick':t})
def receipts(a,rs):return[{**x,'receipt':exact_receipt(a.world.runtime.receipt(x['id']))}for x in rs]
def fixed_read(a):
    panel=[];cs=[]
    for v in codec(a).values():
        for sg in(-1,1):
            o=view(a,pos(v,4,sg));panel.append(o)
            if o['state']>0 and o['semantic']==1 and o['direction']==[0,0,sg]:cs.append({'site':o['site'],'sign':sg,'s_reg':o['s_reg']})
    return {'panel':panel,'candidates':cs,'formed_native_command':cs[0]['sign']if len(cs)==1 else None,'ambiguous':len(cs)>1,'reader_uses_target_or_token':False}
def query(a,token,*,detail=False):
    get(a)
    if token not in get(a).get('enabled_contexts',list(BASE_TOKENS)):raise ValueError('Context not physically admitted for this life; no lexical inference or automatic extension')
    v=TOKENS[token];t=phase(a.tick);rs=[];pre=physical(a.world);frames=[]
    submit(a,'common.token.'+str(list(TOKENS).index(token)),I,v,5,t,rs)
    for sg in(-1,1):
        for stage,k,z,di,arrival in [('select',4,1,-1,4),('back',4,2,-1,5),('restore',3,3,1,6)]:
            dv=(di*v[0],di*v[1],0);dest=pos(v,k,z*sg)
            submit(a,'generic.'+stage+'.'+str(list(TOKENS).index(token))+'.'+str(sg),add(dest,dv,-2),dv,7,t+arrival-2,rs)
    for q in range(t,t+8):
        a.run_until(q)
        if detail:
            pts={pos(vv,k,z)for vv in codec(a).values()for k in(2,3,4,5)for z in range(-4,5)}
            frames.append({'tick':q,'sites':[view(a,p)for p in sorted(pts)]})
        if q==t+4:answer=fixed_read(a)
    return {'kind':'query','context_signal':token,'input_tick':t,'read_tick':t+4,'end_tick':a.tick,'before':pre,'after':physical(a.world),'reader':answer,'requests':receipts(a,rs),'frames':frames,'selection_scope':'Prepared typed context→native route, not acquired access policy; observer never selects bank using this signal'}
def teach(a,token,sign,*,revision=False):
    get(a)
    if token not in get(a).get('enabled_contexts',list(BASE_TOKENS)) or type(sign)is not int or sign not in(-1,1):raise ValueError('Explicit teaching uses admitted context and signed physical event, no other token or target')
    v=TOKENS[token];t=phase(a.tick);rs=[];h=pos(v,3);dv=(-v[0],-v[1],sign);pre=physical(a.world)
    submit(a,'common.token.'+str(list(TOKENS).index(token)),I,v,5,t,rs)
    submit(a,'experience.'+str(list(TOKENS).index(token))+'.'+str(sign),add(h,dv,-3),dv,11,t,rs)
    if revision:
        zz=(0,0,sign);submit(a,'contrast.second.'+str(list(TOKENS).index(token))+'.'+str(sign),add(h,zz,-3),zz,11,t,rs)
    a.run_until(t+3)
    return {'kind':'explicit_revision'if revision else'explicit_teaching','context_signal':token,'teaching_signal':sign,'input_tick':t,'end_tick':a.tick,'before':pre,'after':physical(a.world),'hub':view(a,h),'requests':receipts(a,rs),'scope':'Declared external teaching encounters, not spontaneous consolidation or task reward'}
def joint(a,*,detailed=False):
    """Prepared two-stage sequential concordance of alpha and beta contents.

    First already-acquired contribution returns after67 steps. The second
    contribution and common diagonal resource can form PUREZ only together.
    This consumes/sequesters the two individual routes; never a free copy.
    """
    get(a);t=phase(a.tick);st=t+67;rs=[];before=physical(a.world);frames=[]
    for i,token,at in[(0,'alfa',t),(1,'beta',st)]:
        v=TOKENS[token];submit(a,'common.token.'+str(i),I,v,5,at,rs)
        for sg in(-1,1):
            for stage,z,arrival in [('select',1,4),('back',2,5)]:
                dv=(-v[0],-v[1],0);dest=pos(v,4,z*sg)
                submit(a,'joint.r06.'+stage+'.'+str(i)+'.'+str(sg),add(dest,dv,-2),dv,7,at+arrival-2,rs)
    for sg in(-1,1):
        dv=(1,1,0);dest=(I[0],I[1],(I[2]+6*sg)%N)
        submit(a,'joint.r06.resource.'+str(sg),add(dest,dv,-2),dv,7,st+7,rs)
    for q in range(t,st+12):
        a.run_until(q)
        if detailed:
            pts={(I[0],I[1],(I[2]+z)%N)for z in range(-9,10)}
            pts.update(pos(v,k,z)for v in list(TOKENS.values())[:2]for k in(0,1,2,3,4)for z in range(-7,8))
            frames.append({'tick':q,'sites':[view(a,p)for p in sorted(pts)]})
        if q==st+9:panel=[view(a,(I[0],I[1],(I[2]+6*sg)%N))for sg in(-1,1)]
    cs=[{'site':o['site'],'sign':o['direction'][2],'s_reg':o['s_reg']}for o in panel if o['state']>0 and o['semantic']==1 and o['direction']in([0,0,-1],[0,0,1])]
    answer={'panel':panel,'candidates':cs,'formed_native_command':cs[0]['sign']if len(cs)==1 else None,'ambiguous':len(cs)>1,'reader_uses_target_or_token':False}
    return {'kind':'joint','context_signal':'alfa_beta','input_tick':t,'second_tick':st,'read_tick':st+9,'end_tick':a.tick,'before':before,'after':physical(a.world),'reader':answer,'requests':receipts(a,rs),'frames':frames,'scope':'Prepared sequential signed concordance; first acquired stream is reused through one67-step toroidal return. Individual alpha/beta access is consumed; mixed contents do not mean NO, they have no valid output here.'}
def job(a,row,work,folder,m,*,actuator='closed',feedback='real'):
    public=work.get('valores',[12,12])
    if not isinstance(public,list)or len(public)!=2 or any(type(x)is not int or not 0<=x<=64 for x in public):raise ValueError('Two raw bounded work values')
    domain=work.get('dominio','trabajadores')
    if domain not in('trabajadores','transaccion'):raise ValueError('Existing bounded local worker only')
    formed=row['reader']['formed_native_command'];executed=formed if actuator=='closed'else None
    m['jobs']+=1;folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    worker=None
    if executed is not None:
        command=[sys.executable,'-I','-B','-X','utf8',str(Path(__file__).with_name('eo02_trabajador_local.py'))]
        request={'domain':domain,'executed_worker':executed,'raw_observations':public,'capacity_credit':0,'pending_transaction':m['external_pending']if domain=='transaccion'else None,'attempt':m['jobs'],'native_tick':a.tick,'output_directory':str(folder.resolve())}
        start=time.monotonic();proc=subprocess.run(command,input=json.dumps(request),text=True,encoding='utf-8',capture_output=True,timeout=15)
        if proc.returncode:raise RuntimeError('External worker process error, not a native cognitive negative: '+proc.stderr)
        worker=json.loads(proc.stdout);worker['argv']=command;worker['host_elapsed_seconds']=time.monotonic()-start
        if domain=='transaccion':m['external_pending']=worker['pending_transaction']
    # Fixed outcome transduction: read-back byte count, not eligibility/correct
    # action. Two symmetric radial pulses add load without steering the Z sign.
    rs=[];returned=None
    if worker is not None and feedback=='real':
        value=min(64,int(worker['output_bytes']));sg=formed
        if row['kind']=='joint':
            inject_at=a.tick;dest=(I[0],I[1],(I[2]+9*sg)%N);post=(I[0],I[1],(I[2]+10*sg)%N)
        else:
            inject_at=row['input_tick']+7;v=TOKENS[row['context_signal']];dest=pos(v,3,5*sg);post=pos(v,3,6*sg)
        for dx in(-1,1):
            dv=(dx,0,sg)
            submit(a,'MA02.actual_result.'+row['context_signal']+'.'+str(sg)+'.'+str(dx),add(dest,dv,-1),dv,value,inject_at,rs)
        a.run_until(inject_at+2);returned={'fixed_source':'actual output bytes after worker read-back','quantized_value':value,'output_count_not_correct_target':True,'at_tick':inject_at+1,'post_content':view(a,post)}
    return {'formed_native_action':formed,'executed_action':executed,'actuator_mode':actuator,'worker_receipt':worker,'outcome_return':returned,'return_requests':receipts(a,rs),'feedback_mode':feedback,'scope':'Real bounded file service, selected by native sign. Byte-count return changes physical load; learned action utility or policy adaptation not inferred.'}
def session(a,*,situations,directory,actuator='closed',feedback='real',detailed=False):
    m=get(a)
    if not isinstance(situations,list)or not 1<=len(situations)<=64:raise ValueError('1..64 bounded episodes')
    if actuator not in('closed','nulled')or feedback not in('real','omit'):raise ValueError('Explicit actuator/feedback mode')
    rows=[]
    for q in situations:
        token=q.get('contexto');mode=q.get('modo','usar')
        if mode in('ensenar','revisar'):row=teach(a,token,q.get('senal'),revision=mode=='revisar')
        elif mode in('usar','trabajo'):
            row=query(a,token,detail=detailed)
            if mode=='trabajo':row['external']=job(a,row,q,directory,m,actuator=actuator,feedback=feedback)
        elif mode=='componer':
            if q.get('aceptar_consumo')is not True:raise ValueError('This material composition consumes individual alpha/beta access; explicit aceptar_consumo required')
            row=joint(a,detailed=detailed)
            if q.get('dominio')is not None:row['external']=job(a,row,q,directory,m,actuator=actuator,feedback=feedback)
        else:raise ValueError('Only explicit teaching/revision/common use/local job; no silent alternate expert')
        m['episodes']+=1;m['requests']+=len(row['requests']);rows.append(row);save(a,m)
    return {'revision':REVISION,'rows':rows,'final':state(a),'no_response_table_or_audit_reads':True,'no_NSM65_or_P2_R2_claim':True}
