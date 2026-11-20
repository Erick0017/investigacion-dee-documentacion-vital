"""Private B output meets the native lived selector, not a host answer copy.

Two fixed channels carry either B directional output to S at the SAME time.
The encoded class is transported geometrically. Zero-load helper descendants
are retained and controlled, not silently cleared. The decoder is frozen.
"""
import ic_native_core as ic

def plan(a,*,name,value=45,mode='full'):
    if mode not in('full','no_partner','cut','sham','unpaired'):raise ValueError('Social mode')
    B=list(a.transferred_quantity.geometry['center']);S=ic.configuration(a)['center'];T=147+67*max(0,(a.tick+10-147+66)//67)
    # This frozen anatomical realization, no content transplant or repositioning.
    if B!=[21,59,40]or S!=[15,15,50]:raise ValueError('Fixed N67 physical domain')
    rr=[];routes={};a._ic_shared_opportunities={}
    if mode!='no_partner':
        for port,payload,t in [('B.quantity.object.cue',5,T-5),('B.quantity.object.resource',value,T-5),('B.quantity.reader',7,T-1)]:
            rec=(a.world.probe if port.endswith('reader')else a.world.submit)(port,payload,t);rr.append({'id':int(rec.id),'port':port,'payload':payload,'tick':t,'private_to_B':True})
    for r in(-1,1):
        p=ic.move(B,(r,0,0),4);when=T+4;vin=[r,0,0];turns=[];travel=[]
        segments=[([0,0,1],14),([0,1,0],28),([-1,1,0],3),([-1,0,0],7),([0,0,-1],4),([0,-1,0],8)]if r==1 else[([0,0,1],22),([-1,0,0],3),([-1,1,0],3),([0,1,0],12),([1,0,0],4),([0,0,-1],12),([0,1,0],8)]
        for j,(v,k)in enumerate(segments):
            pulses=ic._transport.turning_inputs(tuple(vin),tuple(v));turn={'site':p[:],'tick':when,'incoming':vin[:],'outgoing':v[:],'pulses':pulses};turns.append(turn)
            for z,pulse in enumerate(pulses):rr.append(ic.arrive(a,'IC01.social.'+name+'.'+str(r)+'.'+str(j)+'.'+str(z),p,pulse['direction'],when+int(mode=='unpaired'),pulse['payload']))
            p=ic.move(p,v,k);when+=k;travel.append({'site_after':p[:],'tick_after':when,'direction':v[:],'steps':k});vin=v
        if p!=S or when!=T+68:raise AssertionError('Social spatial/temporal mismatch')
        routes[str(r)]={'turns':turns,'travel':travel,'arrival':when,'final_direction':vin}
    del a._ic_shared_opportunities
    return{'name':name,'value_private_B':value,'mode':mode,'B':B,'S':S,'source_tick':T,'arrival_tick':T+68,'requests':rr,'routes':routes,'no_host_read_copy':True,'codec':'B+X transports as Y-; B-X as Y+. Prepared arbitrary channel correspondence, not learned common language.'}

def execute(a,p):
    frames=[];rr=p['requests'];events={p['source_tick']:'B_SOURCE',p['source_tick']+1:'AFTER_SOURCE',p['arrival_tick']-1:'PRE_COMPOSITION',p['arrival_tick']:'COMPOSITION'}
    for key,r in p['routes'].items():
        for j,t in enumerate(r['turns']):events.setdefault(t['tick'],'TURN')
    cuts=[]
    for t,role in sorted(events.items()):
        a.run_until(t)
        row={'tick':t,'role':role,'B':ic.obs(a,p['B']),'S':ic.obs(a,p['S']),'turns':[{'branch':key,'turn':j,'expected':turn,'actual':ic.obs(a,turn['site'])}for key,route in p['routes'].items()for j,turn in enumerate(route['turns'])if turn['tick']==t]}
        if role in('PRE_COMPOSITION','COMPOSITION'):row['S_context']=[ic.obs(a,ic.move(p['S'],(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]
        frames.append(row)
        if role=='B_SOURCE'and p['mode']in('cut','sham'):
            for r in(-1,1):
                site=ic.move(p['B'],(r,0,0),2)
                if p['mode']=='sham':site=ic.move(site,(0,0,1),9)
                before=ic.obs(a,site);c={'site':site,'pre':before,'after_source_already_formed':True}
                if before['raw']=='0':
                    req=ic.submit(a,'IC01.social.'+p['name']+'.intercept.'+str(r),site,(0,0,0),t+1,0,4);rr.append(req);c['request']=req
                else:c['unsupported_occupied_no_edit']=True
                cuts.append(c)
    return{'plan':p,'frames':frames,'cuts':cuts,'requests':ic.receipts(a,rr),'result':ic.obs(a,p['S']),'attribution':'Private B material, native comparator emission, fixed native transport, native coincidence with lived E1 state. Prepared mapping; no learned semantics, autonomous interlocutor choice, negotiation or universal social policy.'}
