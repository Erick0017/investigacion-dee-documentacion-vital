"""Acquired 'igual' signal from a declared material equality-route probe.

Revision3 preserves the two failed methods in the laboratory evidence.
This is equality of magnitudes in the inherited finite apparatus, not
general identity, logical negation or an external comparison of values.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from capacidades import espanol_funcional_01 as e

def prepare(a):
    g=e.prepare(a)
    if 'equality_word_v3'in g:return g['equality_word_v3']
    c=g['center'];slot=e.move(c,(0,0,1));hub=e.move(slot,(0,-1,1),3);ports={}
    for role,target,v,lead in(('material_probe1',c,(0,1,0),1),('material_probe3',c,(0,1,0),3),('word_cue',hub,(1,0,0),3),('word_query',hub,(1,0,0),3)):
        name='EF01.EQUALITY3.'+role
        if name in a.world.runtime.channel_names:raise ValueError('Equality interface collision')
        ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*e.move(target,v,-lead));ch.direction=d.Direction(*v);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True
        p=d.InterfaceSpec();p.name=name;p.channel=ch;a.world.declare_interface(p);ports[role]=name
    entry={'schema':'DCS1.1.EF01.equality_word.r3','center':c,'route_slot':slot,'hub':hub,'ports':ports,'phase':7,'signature':[1,-1,1],'teaching_events':[],
        'prepared':'Comparator, physical frame, material probe, cue and reader. Probe is active material, not passive observation.',
        'learned':'Native comparison/route consequence plus later opaque cue; without either the qualified signal is absent in the validated controls.',
        'scope':'Equality of actual magnitude+format5 to the acquired reference of this apparatus. Does not assert general identity or teach diferente/NO.'}
    g['equality_word_v3']=entry;a.world.runtime.set_snapshot_metadata(e.KEY,encode_metadata(g));return entry

def present(a,*,value,teacher=False,probe_lead=1):
    if type(value)is not int or not 42<=value<=123 or probe_lead not in(1,3)or type(teacher)is not bool:raise ValueError('Finite exact magnitude and physical probe lead1/3 required')
    entry=prepare(a);target=e.tick_at_or_after(a.tick,phase=3,lead=8);first=len(a.quantity.state['requests']);a.quantity.present_object(value,round_index=(target-70)//67);a.quantity.input('quantity.reader',7,target-1,True);req=[]
    name=entry['ports']['material_probe'+str(probe_lead)];r=a.world.probe(name,0,target+1-probe_lead);req.append({'port':name,'payload':0,'tick':target+1-probe_lead,'id':int(r.id)})
    if teacher:
        name=entry['ports']['word_cue'];r=a.world.submit(name,5,target+1);req.append({'port':name,'payload':5,'tick':target+1,'id':int(r.id)})
    a.run_until(target);comparison=e.obs(a,entry['center']);a.run_until(target+1);route=e.obs(a,entry['route_slot']);a.run_until(target+4);word=e.obs(a,entry['hub'])
    if teacher:
        g=e.prepare(a);g['equality_word_v3']['teaching_events'].append({'comparison_tick':target,'probe_lead':probe_lead,'word_cue_payload':5});a.world.runtime.set_snapshot_metadata(e.KEY,encode_metadata(g))
    return {'ENTORNO':{'current_magnitude':value,'format_cue':5},'ENTE':{'native_comparison':comparison,'native_route_product':route,'word_record':word},
        'INSTRUMENTO':{'comparison_tick':target,'word_tick':target+4,'teacher_label_supplied':teacher,'material_probe_lead':probe_lead,'requests':[e.receipt_at(a.world,r)for r in req],'quantity_requests':a.quantity.receipts()[first:]},
        'INTERPRETACION':'Active physical probing is declared. No Python equality test, target lookup or silent absence-to-NO translation.'}

def query(a,*,payload=7):
    entry=prepare(a)
    if type(payload)is not int or not 0<=payload<=65535:raise ValueError('Exact material payload required')
    target=e.tick_at_or_after(a.tick,phase=entry['phase'],lead=3);name=entry['ports']['word_query'];r=a.world.probe(name,payload,target-3);a.run_until(target);out=e.obs(a,entry['hub'])
    return {'ENTE':out,'SPANISH_DECODED':['igual']if e.valid(out,entry['signature'])else[],
        'INSTRUMENTO':{'query_tick':target,'request':e.receipt_at(a.world,{'port':name,'payload':payload,'tick':target-3,'id':int(r.id)})},'INTERPRETACION':'Recall of the acquired equality form, not a claim that the current scene is equal.'}

def context(a,*,value,probe_lead=1):
    entry=prepare(a);baseline=e.tick_at_or_after(a.tick,phase=entry['phase'])
    if baseline>a.tick:a.run_until(baseline)
    before=e.obs(a,entry['hub']);row=present(a,value=value,teacher=False,probe_lead=probe_lead);after=e.obs(a,entry['hub']);delta=after['s_reg']-before['s_reg']
    qualified=e.valid(before,entry['signature'])and e.valid(after,entry['signature'])and delta==7
    return {'ENTORNO':row['ENTORNO'],'ENTE':{**row['ENTE'],'prior_word_record':before,'current_word_record':after},'INSTRUMENTO':{**row['INSTRUMENTO'],'baseline_tick':baseline,'decoder':'Fixed native-word direction plus current material increment7, no value/reference comparison','native_word_increment':delta},
        'SPANISH_DECODED':['igual']if qualified else[],'INTERPRETACION':'Current physical equality consequence modulates an acquired signal. Empty decode remains indeterminate, never diferente/NO by default.'}

def context_renewable(a,*,value,sham_guards=False,require_learned=True):
    """Research R0 renewal circuit, conditional expression and exact orbit return.

    All direction-normalizer opportunities are supplied in both conditions.
    Zero-load normalizers are real material; no RAW/clock repair is used.
    """
    if type(value)is not int or not 42<=value<=123 or type(sham_guards)is not bool:raise ValueError('Finite magnitude/guard protocol domain')
    entry=prepare(a);g=e.prepare(a);entry=g['equality_word_v3'];baseline=e.tick_at_or_after(a.tick,phase=7)
    if baseline>a.tick:a.run_until(baseline)
    before=e.obs(a,entry['hub'])
    if require_learned and not e.valid(before,entry['signature']):raise ValueError('Acquired equality reader is currently unavailable; do not reconstruct it')
    target=baseline+67;comp=target-4;hub=entry['hub'];PE=e.move(hub,(1,-1,1),6);PN=e.move(hub,(1,0,1),6);J=e.move(hub,(3,-1,3),3);F=PE;req=[];ports={}
    known=entry.get('renewal_v1')
    if known and known['sham_guards']!=sham_guards:raise ValueError('Guard-control preparation cannot change silently in the same lived circuit')
    def port(role,site,v,semantic=1,lead=3):
        name='EF01.EQUALITY3.RENEW1.'+role
        if name not in a.world.runtime.channel_names:
            ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*e.move(site,v,-lead));ch.direction=d.Direction(*v);ch.state=1;ch.semantic=semantic;ch.allow_experience=True;ch.allow_probe=True
            p=d.InterfaceSpec();p.name=name;p.channel=ch;a.world.declare_interface(p)
        ports[role]=name;return name
    def send(name,payload,t,probe=False):
        r=(a.world.probe if probe else a.world.submit)(name,payload,t);req.append({'port':name,'payload':payload,'tick':t,'id':int(r.id)})
    xfirst=len(a.quantity.state['requests']);a.quantity.present_object(value,round_index=(comp-70)//67);a.quantity.input('quantity.reader',7,comp-1,True)
    send(entry['ports']['material_probe1'],0,comp,True)
    send(port('condition_reader',hub,(0,1,0)),7,target-3,True)
    for role,point,vector,dt in(('Eturn_a',PE,(1,1,0),6),('Eturn_b',PE,(-1,1,0),6),('Nturn',PN,(0,-1,0),6),
            ('Jturn_a',J,(1,1,0),9),('Jturn_b',J,(-1,1,0),9),('Fturn_a',F,(1,-1,0),73),('Fturn_b',F,(-1,-1,0),73)):
        send(port(role,point,vector),0,target+dt-3)
    guard_sites=[e.move(PE,(0,1,0),3),e.move(J,(0,1,0),3),e.move(F,(0,-1,0),3)]
    if sham_guards:guard_sites=[e.move(site,(0,0,1),9)for site in guard_sites]
    if not known:
        for j,site in enumerate(guard_sites):send(port('guard'+str(j),site,(0,0,0),4,lead=0),0,target+1)
    from app.native_tools import moore27,physical
    frames=[]
    stages=[(comp,'native_comparison',{'center':entry['center']}),(comp+1,'current_route',{'route':entry['route_slot']}),(target-1,'pre_conditional_read',{'hub':hub}),
        (target,'conditional_read',{'hub':hub}),(target+5,'pre_branch_turn',{'E':PE,'N':PN}),(target+6,'branch_turn',{'E':PE,'N':PN}),
        (target+8,'pre_rejoin',{'J':J}),(target+9,'rejoin',{'J':J}),(target+72,'pre_orbit_restore',{'F':F}),(target+73,'orbit_restore',{'F':F}),
        (target+133,'pre_return',{'hub':hub}),(target+134,'return',{'hub':hub})]
    for tick,label,sites in stages:
        a.run_until(tick);frames.append({'label':label,'tick':a.tick,'records':{key:e.obs(a,site)for key,site in sites.items()},'moore':{key:moore27(a.world,site)for key,site in sites.items()}})
    result=next(row['records']['hub']for row in frames if row['label']=='conditional_read');final=e.obs(a,hub)
    entry['renewal_v1']={'sham_guards':sham_guards,'guard_sites':guard_sites,'period_to_orbit_return':134,'last_query_tick':target,'last_return_tick':a.tick,'ports':ports,
        'prepared':'Two alternative physical branch turners, a common join, orbit-restoring turners and native zero-load residual absorbers. All opportunities supplied regardless of the answer.'}
    a.world.runtime.set_snapshot_metadata(e.KEY,encode_metadata(g))
    return {'ENTORNO':{'actual_magnitude':value,'format_cue':5,'teacher_label_supplied':False},'ENTE':{'initial_word':before,'conditional_emission':result,'restored_word':final,'frames':frames},
        'SPANISH_DECODED':['igual']if e.valid(result,entry['signature'])else[],
        'INSTRUMENTO':{'target':target,'requests':[e.receipt_at(a.world,r)for r in req],'quantity_requests':a.quantity.receipts()[xfirst:],'sham_guards':sham_guards,'actual_guard_records':[e.obs(a,site)for site in guard_sites],'returned_to_declared_reader':e.valid(final,entry['signature']),'basic_costs':{'query':7,'normalizer_packets_per_query':7,'normalizer_payload_each':0,'new_guards_first_cycle':0 if known else 3}},
        'INTERPRETACION':'Experimental fixed regulation of acquired equality access. Conditional native direction, not host arithmetic. Empty emission is indeterminate, not NO. A finite successful circuit would not establish autonomous policyR2 or unlimited access.'}
