"""A native received carrier, fixed ballistic delay and content-free reader.

Both physical branches receive identical Z0 resources. The host never copies
B's output or chooses a reader from the expected content. Observations belong
to the auditor and do not enter any participant input.
"""
import ic_native_core as ic
from app.native_tools import physical

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
