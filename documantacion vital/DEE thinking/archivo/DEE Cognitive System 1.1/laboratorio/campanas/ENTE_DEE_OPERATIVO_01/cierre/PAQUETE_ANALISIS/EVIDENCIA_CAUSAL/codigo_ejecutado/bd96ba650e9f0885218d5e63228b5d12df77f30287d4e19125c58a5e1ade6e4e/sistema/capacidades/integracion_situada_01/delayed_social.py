"""A native received carrier, fixed ballistic delay and content-free reader.

Both physical branches receive identical Z0 resources. The host never copies
B's output or chooses a reader from the expected content. Observations belong
to the auditor and do not enter any participant input.
"""
from . import ic_native_core as ic
from app.native_tools import physical
import json
from dee_thinking.persistence import encode_metadata,decode_metadata
KEY='DEE.Cognitive.System.1.1.IC01.delayed_social.v1'

def get(a):
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    return json.loads(decode_metadata(entries[KEY])['protocol_json'])if KEY in entries else None
def put(a,s):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'protocol_json':json.dumps(s,ensure_ascii=False,separators=(',',':'))}))

def prepare(a,*,name,value=18,mode='full',public_object=None):
    if mode not in('full','no_partner','cut','sham','unpaired'):raise ValueError('Declared social-memory mode')
    B=list(a.transferred_quantity.geometry['center']);T=147+67*max(0,(a.tick+10-142+66)//67);end=T+57;rr=[];banks=[]
    if mode!='no_partner':
        for port,payload,t in [('B.quantity.object.cue',5,T-5),('B.quantity.object.resource',value,T-5),('B.quantity.reader',7,T-1)]:
            r=(a.world.probe if port.endswith('reader')else a.world.submit)(port,payload,t);rr.append({'id':int(r.id),'port':port,'payload':payload,'tick':t,'private_to_B':True})
    for sign in(-1,1):
        R=ic.move(B,(sign,0,0));target=ic.move(R,(sign,0,1),56);rr.append(ic.arrive(a,'IC01.delay.'+name+'.reader.'+str(sign),target,(0,0,-1),end+int(mode=='unpaired'),0));banks.append({'sign':sign,'birth':R,'direction':[sign,0,1],'target':target,'read_tick':end,'retention_before_query_ticks':56})
    if public_object is not None:
        k=(end-70)//67;a.quantity.present_object(public_object,round_index=k);rr.extend(dict(r)for r in a.quantity.state['requests'][-2:]);rr.append(a.input('quantity.reader',7,end-1,'probe','GENERIC_COMMON_COMPARATOR_RESOURCE'))
    return{'name':name,'value_private_B':value,'mode':mode,'B':B,'source_tick':T,'birth_tick':T+1,'end_tick':end,'banks':banks,'requests':rr,'public_object':public_object,'prepared':'Both zero-load Z association opportunities and both zero-load opposite-Z retrieval probes. No answer, reference36 or selected branch supplied to E1.'}

def advance(a,plan,*,record=True):
    T=plan['source_tick'];end=plan['end_tick'];rr=plan['requests'];frames=[];cuts=[];start=physical(a.world,occupation=True)
    a.run_until(T);source=ic.obs(a,plan['B'])
    for b in plan['banks']:
        rr.append(ic.submit(a,'IC01.delay.'+plan['name']+'.generic_record.'+str(b['sign']),ic.move(b['birth'],(0,0,1),-1),(0,0,1),T,0))
    if plan['mode']in('cut','sham'):
        for b in plan['banks']:
            site=b['birth']if plan['mode']=='cut'else ic.move(b['birth'],(0,0,1),9);pre=ic.obs(a,site);item={'site':site,'pre':pre,'B_source_already_formed':source}
            if pre['raw']=='0':r=ic.submit(a,'IC01.delay.'+plan['name']+'.cut.'+str(b['sign']),site,(0,0,0),T,0,4);rr.append(r);item['request']=r
            else:item['unsupported_occupied']=True
            cuts.append(item)
    # Fixed monotone grid is identical with logging enabled or disabled.
    for t in range(T+1,end+1+int(plan['mode']=='unpaired')):
        a.run_until(t)
        if record:
            rows=[]
            for b in plan['banks']:
                k=min(t-(T+1),56);position=ic.move(b['birth'],b['direction'],k);rows.append({'bank':b['sign'],'unwrapped':[b['birth'][i]+b['direction'][i]*k for i in range(3)],'expected_ballistic_site':position,'read':ic.obs(a,position),'context125':[ic.obs(a,ic.move(position,(x,y,z)))for x in(-2,-1,0,1,2)for y in(-2,-1,0,1,2)for z in(-2,-1,0,1,2)]if t in(T+1,T+2,end-1,end)else[]})
            frames.append({'tick':t,'banks':rows})
    reads=[{'bank':b['sign'],'site':b['target'],'read':ic.obs(a,b['target'])}for b in plan['banks']]
    return{'plan':plan,'initial_after_source':start,'B_source':source,'frames':frames,'cuts':cuts,'requests':ic.receipts(a,rr),'received_outputs':reads,'native_quantity_result':ic.obs(a,a.quantity.geometry['center']),'final':physical(a.world,occupation=True),'scope':'Limited native retention and use of the received directional relation. Content-free prepared reader, not autonomous access choice or learned language. Ballistic continuity is only claimed where successive observed fields and local contexts support it.'}

def begin(a,**arguments):
    prior=get(a)
    if prior and a.tick<prior['plan']['end_tick']:raise ValueError('A social protocol is pending, not silently replaceable')
    p=prepare(a,**arguments);s={'schema':'IC01.delayed_social.operational.v1','plan':p,'source':None,'source_resources_submitted':False,'last_tick':a.tick,'cuts':[],'phase':'SCHEDULED'};put(a,s);return p

def advance_until(a,target,advance_fn,*,record=True):
    s=get(a)
    if s is None:raise ValueError('No social protocol')
    p=s['plan'];T=p['source_tick'];end=p['end_tick'];rows=[];rr=p['requests']
    trace_end=end+67;events=([T]if not s['source_resources_submitted']else[])+list(range(max(T+1,a.tick+1),min(target,trace_end)+1))
    for t in sorted(set(t for t in events if a.tick<=t<=target)):
        advance_fn(t)
        if t==T and not s['source_resources_submitted']:
            s['source']=ic.obs(a,p['B'])
            for b in p['banks']:rr.append(ic.submit(a,'IC01.delay.'+p['name']+'.generic_record.'+str(b['sign']),ic.move(b['birth'],(0,0,1),-1),(0,0,1),T,0))
            if p['mode']in('cut','sham'):
                for b in p['banks']:
                    site=b['birth']if p['mode']=='cut'else ic.move(b['birth'],(0,0,1),9);pre=ic.obs(a,site);cut={'site':site,'pre':pre,'source_already_formed':True}
                    if pre['raw']=='0':r=ic.submit(a,'IC01.delay.'+p['name']+'.cut.'+str(b['sign']),site,(0,0,0),T,0,4);rr.append(r);cut['request']=r
                    else:cut['unsupported_occupied']=True
                    s['cuts'].append(cut)
            s['source_resources_submitted']=True
        elif t>T and record:
            ports=[]
            for b in p['banks']:
                if t<=end:position=ic.move(b['birth'],b['direction'],t-(T+1));direction=b['direction']
                else:position=ic.move(b['target'],(b['sign'],0,0),t-end);direction=[b['sign'],0,0]
                read=ic.obs(a,position);unwrapped=[b['birth'][i]+b['direction'][i]*(min(t,end)-(T+1))+(b['sign']*(t-end)if i==0 and t>end else 0)for i in range(3)]
                special=t in(T+1,T+2,end-1,end,end+1,end+67)or any(u<0 or u>=67 for u in unwrapped)
                ports.append({'bank':b['sign'],'expected_site':position,'unwrapped':unwrapped,'read':read,'context125':[ic.obs(a,ic.move(position,(x,y,z)))for x in(-2,-1,0,1,2)for y in(-2,-1,0,1,2)for z in(-2,-1,0,1,2)]if special and read['s_reg']>0 else[]})
            rows.append({'tick':t,'ports':ports,'scope':'Passive expected-path samples. Any mismatch ends an unbranched lineage claim, not the physical life.'})
        s['last_tick']=t
    if a.tick<target:advance_fn(target)
    s['last_tick']=a.tick;s['phase']='RECEIVED_AND_ACCESSED'if a.tick>=end else'IN_PROGRESS';put(a,s)
    return rows
