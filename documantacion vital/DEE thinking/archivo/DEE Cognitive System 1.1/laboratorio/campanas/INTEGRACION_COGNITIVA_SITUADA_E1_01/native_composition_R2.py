"""Route a real private B output into a current E1 operand, all under v27.

No response is read and copied. Geometry, zero-load opportunities and the
current public object are frozen before evaluation. Received payload adds
physically to a learned-reference or current-object carrier before the native
gradient acts. The prepared operation is not learned grammar.
"""
import ic_native_core as ic
from app.native_tools import physical

def execute(a,*,name,value=18,obj=73,mode='full',reader=True,escaped=True):
    if mode not in('full','no_partner','cut','sham'):raise ValueError('Composition mode')
    B=list(a.transferred_quantity.geometry['center']);Q=list(a.quantity.geometry['center'])
    if B!=[21,59,40]or Q!=[50,35,35]:raise ValueError('Frozen domain')
    T=147+67*max(0,(a.tick+10-142+66)//67);decision=T+57;rr=[];routes={};first_pulses=[]
    if mode!='no_partner':
        for port,payload,t in [('B.quantity.object.cue',5,T-5),('B.quantity.object.resource',value,T-5),('B.quantity.reader',7,T-1)]:
            r=(a.world.probe if port.endswith('reader')else a.world.submit)(port,payload,t);rr.append({'id':int(r.id),'port':port,'payload':payload,'tick':t,'private_to_B':True})
    k=(decision-70)//67;a.quantity.present_object(obj,round_index=k);rr.extend(dict(r)for r in a.quantity.state['requests'][-2:])
    if reader:rr.append(a.input('quantity.reader',7,decision-1,'probe','FIXED_GENERIC_COMPARATOR_RENEWAL_AFTER_GAP'))
    for sign in(-1,1):
        p=ic.move(B,(sign,0,0));when=T+1;incoming=[sign,0,0];turns=[];travel=[]
        segments=([([sign,0,1],4),([0,0,-1],14),([0,-1,0],7),([1,-1,0],17),([1,0,0],8),([0,0,1],5)]if sign==1 else[([sign,0,1],4),([0,0,-1],9),([1,0,-1],5),([0,-1,0],4),([1,-1,0],20),([1,0,0],8),([0,0,1],5)])if escaped else[([0,0,-1],10),([0,-1,0],11),([1,-1,0],13),([1,0,0],16),([0,0,1],5)]
        for j,(v,length)in enumerate(segments):
            pulses=ic._transport.turning_inputs(tuple(incoming),tuple(v));turn={'site':p[:],'tick':when,'incoming':incoming[:],'outgoing':v[:],'pulses':pulses};turns.append(turn)
            for z,pulse in enumerate(pulses):
                if j==0:first_pulses.append({'name':'IC01.composition.'+name+'.'+str(sign)+'.first.'+str(z),'site':ic.move(p,pulse['direction'],-1),'direction':pulse['direction'],'tick':when-1,'payload':pulse['payload']})
                else:rr.append(ic.arrive(a,'IC01.composition.'+name+'.'+str(sign)+'.'+str(j)+'.'+str(z),p,pulse['direction'],when,pulse['payload']))
            p=ic.move(p,v,length);when+=length;travel.append({'site_after':p[:],'tick_after':when,'direction':v[:],'steps':length});incoming=v
        expected=ic.move(Q,(sign,0,0))
        if p!=expected or when!=decision-1:raise AssertionError('Frozen native operand route')
        routes[str(sign)]={'turns':turns,'travel':travel,'destination':p,'arrival_tick':when,'role':'current_object_operand'if sign==1 else'acquired_reference_operand'}
    events={T:'B_SOURCE',T+1:'RECEIVED_AND_TRANSFORMED',decision-2:'PRE_OPERAND',decision-1:'OPERAND_COMBINATION',decision:'NATIVE_DECISION'}
    for key,r in routes.items():
        for j,t in enumerate(r['turns']):events.setdefault(t['tick'],'TURN')
    frames=[];cuts=[]
    for t,role in sorted(events.items()):
        a.run_until(t);row={'tick':t,'role':role,'B':ic.obs(a,B),'Q':ic.obs(a,Q),'reference_hub':ic.obs(a,a.quantity.geometry['reference_hub']),'reference_operand':ic.obs(a,ic.move(Q,(-1,0,0))),'object_operand':ic.obs(a,ic.move(Q,(1,0,0))),'turns':[{'branch':key,'turn':j,'expected':turn,'actual':ic.obs(a,turn['site'])}for key,r in routes.items()for j,turn in enumerate(r['turns'])if turn['tick']==t]}
        if role in('PRE_OPERAND','OPERAND_COMBINATION','NATIVE_DECISION'):row['Q_context']=[ic.obs(a,ic.move(Q,(x,y,z)))for x in(-2,-1,0,1,2)for y in(-2,-1,0,1,2)for z in(-2,-1,0,1,2)]
        frames.append(row)
        if role=='B_SOURCE':
            for pulse in first_pulses:rr.append(ic.submit(a,pulse['name'],pulse['site'],pulse['direction'],pulse['tick'],pulse['payload']))
            if mode in('cut','sham'):
                for sign in(-1,1):
                    site=ic.move(B,(sign,0,0))
                    if mode=='sham':site=ic.move(site,(0,0,1),9)
                    before=ic.obs(a,site);entry={'site':site,'pre':before,'source_already_formed':True}
                    if before['raw']=='0':r=ic.submit(a,'IC01.composition.'+name+'.interceptor.'+str(sign),site,(0,0,0),T,0,4);rr.append(r);entry['request']=r
                    else:entry['unsupported_occupied']=True
                    cuts.append(entry)
    return{'name':name,'mode':mode,'private_B_object':value,'public_current_object':obj,'source_tick':T,'decision_tick':decision,'routes':routes,'frames':frames,'cuts':cuts,'requests':ic.receipts(a,rr),'native_result':ic.obs(a,Q),'physical':physical(a.world,occupation=True),'scope':'Prepared native transport and gradient combine an acquired cost-dependent reference, a new actual object and material B output. No external arithmetic determines the DEE response; no general language or learned comparison rule claimed.'}
