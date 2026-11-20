"""Spanish functional signals on the finite CPC9 N67 magnitude apparatus.

This optional system-layer component does not alter thinking4.5 or kernel27.
Native reference, comparison and acquired carriers precede translation.
The fixed external demodulator is instrument assistance, not learned grammar.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from dee_thinking.consolidated import exact_receipt,exact_observation

KEY='DEE.Cognitive.System.1.1.ESPANOL_FUNCIONAL_01.v1'
WORDS={'menos':(1,1,-1),'más':(-1,-1,1)}
ALIAS={'mas':'más','más':'más','menos':'menos'}

def move(p,v,k=1):return[(p[i]+v[i]*k)%67 for i in range(3)]
def obs(a,site):return exact_observation(a.world.runtime.observe(d.Coordinate(*site)))
def valid(row,vector):return row['active'] and row['state']==1 and row['semantic']==1 and row['direction']==list(vector)
def tick_at_or_after(tick,phase=6,lead=0):
    return phase+67*max(0,(int(tick)+lead-phase+66)//67)
def receipt_at(world,entry):return {**entry,'receipt':exact_receipt(world.runtime.receipt(entry['id']))}

def prepare(a):
    if int(a.world.runtime.dimension)!=67 or not hasattr(a,'quantity'):
        raise ValueError('EF01 requires the declared CPC9 N67 quantity apparatus, not an arbitrary runtime or transplanted memory')
    c=a.quantity.geometry['center'];w=a.world
    g={'schema':'DCS1.1.EF01.magnitude.words.r6','center':c,'period':67,'phase':6,'words':{},
       'prepared':'Fixed physical frame, channels and comparator operation; empty interface registration does not teach words',
       'learned':'Only native encounters after actual experience can establish the acquired signature',
       'decoder':'External fixed direct-channel demodulator; not native general Spanish grammar',
       'scope':'Relative magnitude, fixed format cue5, declared phase, acquired reference; not cardinality or deictic perspective'}
    existing={p.name:p for p in w.interfaces}
    for word,v in WORDS.items():
        code='mas'if word=='más'else'menos';hub=move(c,(v[0],0,0),3);ports={}
        for role,vector in [('cue',(0,v[1],v[2])),('query_plus',(0,0,1)),('query_minus',(0,0,-1))]:
            name='EF01.R1.'+code+'.'+role;injection=move(hub,vector,-3);ports[role]=name
            if name in existing:
                channel=existing[name].channel
                actual=([channel.injection_site.x,channel.injection_site.y,channel.injection_site.z],[channel.direction.dx,channel.direction.dy,channel.direction.dz])
                if actual!=(injection,list(vector)):
                    raise ValueError('EF01 interface identity mismatch; do not reinterpret an earlier failed geometry as R6')
            else:
                ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*injection);ch.direction=d.Direction(*vector);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True
                p=d.InterfaceSpec();p.name=name;p.channel=ch;w.declare_interface(p)
        g['words'][word]={'hub':hub,'signature':list(v),'ports':ports}
    prior=dict(w.runtime.snapshot_metadata_entries)
    if KEY in prior:
        old=decode_metadata(prior[KEY])
        if old['center']!=c or old['words']!=g['words']:raise ValueError('Stored Spanish protocol geometry differs')
        return old
    w.runtime.set_snapshot_metadata(KEY,encode_metadata(g));return g

def current_signals(a,g=None):
    g=g or prepare(a)
    return {word:obs(a,item['hub'])for word,item in g['words'].items()}

def teach(a,*,word,value,delay=0,object_query=True):
    word=ALIAS.get(word)
    if word is None:raise ValueError('Only explicit Spanish comparison cue tokens are admitted in revisionR6')
    if type(value)is not int or not 42<=value<=123 or delay not in(0,1,2):
        raise ValueError('Exact magnitude and declared cue delay required')
    g=prepare(a);target=tick_at_or_after(a.tick,lead=9);center=target-3
    if center<70:raise ValueError('Requires an already operating inherited quantity protocol, not a fresh empty grammar')
    first=len(a.quantity.state['requests'])
    a.quantity.present_object(value,round_index=(center-70)//67)
    if object_query:a.quantity.input('quantity.reader',7,center-1,True)
    rr=a.world.submit(g['words'][word]['ports']['cue'],5,target-3+delay)
    a.run_until(target+delay)
    return {'ENTORNO':{'actual_magnitude':value,'format_cue':5},
        'INSTRUMENTO':{'teacher_word':word,'teacher_is_external':True,'current_comparison_tick':center,'cue_encounter_tick':target+delay,
                       'new_word_receipt':exact_receipt(a.world.runtime.receipt(rr.id)),
                       'quantity_receipts':a.quantity.receipts()[first:]},
        'ENTE':current_signals(a,g),
        'INTERPRETACION':'This is a teaching attempt. Token recognition or a changed record alone does not certify acquisition; use and controls are required.'}

def query_words(a,*,words=None,payload=7):
    g=prepare(a);selected=list(g['words'])if words is None else[ALIAS.get(x)for x in words]
    if not selected or any(x not in g['words']for x in selected):raise ValueError('Unknown token; no free-language completion')
    if type(payload)is not int or not 0<=payload<=65535:raise ValueError('Exact material payload required')
    target=tick_at_or_after(a.tick,lead=3);requests=[]
    for word in selected:
        item=g['words'][word];port=item['ports']['query_minus'if item['signature'][2]==-1 else'query_plus']
        r=a.world.probe(port,payload,target-3);requests.append({'word':word,'port':port,'payload':payload,'tick':target-3,'id':int(r.id)})
    a.run_until(target);signals=current_signals(a,g)
    return {'ENTE':signals,'INSTRUMENTO':{'material_query':True,'tick':target,'requests':[receipt_at(a.world,r)for r in requests]},
        'FORMAS_ACCESIBLES':[w for w in selected if valid(signals[w],g['words'][w]['signature'])],
        'INTERPRETACION':'Acquired comparison-form retrieval only. This is not a claim that the current situation satisfies every recalled word.'}

def demodulate(before,after,geometry,word_probe_dose=0):
    decoded=[];detail={}
    for word,item in geometry['words'].items():
        previous,current=before[word],after[word];delta=current['s_reg']-previous['s_reg']
        detail[word]={'prior_valid':valid(previous,item['signature']),'current_valid':valid(current,item['signature']),
            'native_material_delta':delta,'declared_word_probe_dose':word_probe_dose,'modulation_delta':delta-word_probe_dose}
        if detail[word]['prior_valid'] and detail[word]['current_valid'] and delta-word_probe_dose==7:decoded.append(word)
    return {'SPANISH_DECODED':decoded,'SIGNAL_DETAILS':detail,
        'status':'OBSERVED_COMPARATIVE_MODULATION'if len(decoded)==1 else'INDETERMINATE_OR_NO_COMPARATIVE_PREDICATION',
        'decoder_role':'INSTRUMENTO external fixed demodulation; no object/reference arithmetic or target lookup',
        'not_equal_or_no_hay':not decoded}

def context(a,*,value,method='B',ask=True):
    if type(value)is not int or not 42<=value<=123 or method not in('A','B'):
        raise ValueError('Exact actual magnitude and admitted A/B protocol required')
    g=prepare(a);baseline_tick=tick_at_or_after(a.tick)
    if baseline_tick>a.tick:a.run_until(baseline_tick)
    before=current_signals(a,g);target=baseline_tick+67;center=target-3
    first=len(a.quantity.state['requests'])
    a.quantity.present_object(value,round_index=(center-70)//67)
    if ask:a.quantity.input('quantity.reader',7,center-1,True)
    requested=[];dose=7 if method=='A'else 0
    if dose:
        for word,item in g['words'].items():
            port=item['ports']['query_minus'if item['signature'][2]==-1 else'query_plus']
            r=a.world.probe(port,dose,target-3);requested.append({'word':word,'port':port,'payload':dose,'tick':target-3,'id':int(r.id)})
    a.run_until(center);comparison=obs(a,g['center']);a.run_until(target);after=current_signals(a,g)
    return {'ENTORNO':{'actual_object_magnitude':value,'format_cue':5,'teacher_label_supplied':False},
        'ENTE':{'native_comparison':comparison,'previous_word_signal':before,'current_word_signal':after},
        'INSTRUMENTO':{'baseline_tick':baseline_tick,'comparison_tick':center,'word_tick':target,'method':method,
                       'query_requested':ask,'word_requests':[receipt_at(a.world,r)for r in requested],'quantity_requests':a.quantity.receipts()[first:]},
        'TRADUCCION':demodulate(before,after,g,dose),
        'INTERPRETACION':'Finite context-conditioned signal use after acquired form learning. No free dialogue, equal/absence inference, learned routing or new NSM-level claim.'}

def contact_prepare(a,*,frame,base=(28,34,54)):
    """Register empty contact opportunities in an existing world, no RAW edit."""
    if not isinstance(frame,str)or not frame.isascii()or not frame.replace('_','').isalnum():
        raise ValueError('Explicit ASCII frame identifier required')
    if len(base)!=3 or any(type(v)is not int or not 0<=v<67 for v in base):
        raise ValueError('N67 declared physical reference required')
    g=prepare(a);frames=g.setdefault('contact_frames',{})
    if frame in frames:
        if frames[frame]['base']!=list(base):raise ValueError('Existing frame identity cannot be moved silently')
        return frames[frame]
    w=a.world;ports={};banks={};base=list(base);join=move(base,(0,0,-1))
    def port(role,site,vector,state=1,lead=0):
        name='EF01.C.'+frame+'.'+role
        if name in w.runtime.channel_names:raise ValueError('Unexpected contact interface collision')
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*move(site,vector,-lead));c.direction=d.Direction(*vector);c.state=state;c.semantic=1;c.allow_experience=True;c.allow_probe=True
        p=d.InterfaceSpec();p.name=name;p.channel=c;w.declare_interface(p);return name
    for state in(1,17):
        ports['actor.'+str(state)]=port('actor.'+str(state),move(join,(1,0,0),-4),(1,0,0),state)
        ports['actor.off.'+str(state)]=port('actor.off.'+str(state),move(move(join,(1,0,0),-4),(0,1,0),12),(1,0,0),state)
    ports['common']=port('common',move(join,(-1,0,1),-4),(-1,0,1))
    ports['medium']=port('medium',move(base,(1,1,-1),-5),(1,1,-1))
    for axis in(-1,1):
        for z,word in((0,'toca'),(-1,'no toca')):
            name=('toca'if z==0 else'no_toca')+('_izq'if axis==-1 else'_der');hub=move(base,(axis,1,z),4);effect=move(hub,(-axis,1,z),6)
            banks[name]={'word':word,'axis':axis,'z':z,'hub':hub,'effect':effect,
                'cue':port(name+'.cue',hub,(-axis,0,0),lead=3),
                'query':port(name+'.query',hub,(-axis,0,0),lead=3),
                'use':port(name+'.use',effect,(axis,0,0),lead=3)}
    entry={'base':base,'join':join,'ports':ports,'banks':banks,'acquired_at':None,
        'after_functional_use':False,'scope':'Contact/free flight of these physical actors only. no toca is a positive free-flight signature, not general NO.',
        'frame_prepared_externally':True,'new_matter_on_registration':0}
    frames[frame]=entry;a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(g));return entry

def contact_teach(a,*,frame,present=True,medium=1,actor_state=1,signal=True,delay=0,start=None):
    g=prepare(a)
    if frame not in g.get('contact_frames',{}):raise ValueError('Prepare an explicit physical contact frame first')
    entry=g['contact_frames'][frame]
    if entry['acquired_at']is not None:raise ValueError('This finite frame has a lived history; use an explicitly new frame, not a hidden reset')
    if type(present)is not bool or medium not in(1,3,5)or actor_state not in(1,17)or delay not in(0,1):raise ValueError('Outside declared contact experience domain')
    start=tick_at_or_after(a.tick,phase=64,lead=4)if start is None else start
    if type(start)is not int or start<a.tick+3:raise ValueError('Future monotonic contact boundary required')
    w=a.world;req=[]
    def send(port,payload,t):
        r=w.submit(port,payload,t);req.append({'port':port,'payload':payload,'tick':t,'id':int(r.id)})
    send(entry['ports'][('actor.'if present else'actor.off.')+str(actor_state)],0,start)
    send(entry['ports']['common'],0,start);send(entry['ports']['medium'],medium,start)
    if signal:
        for b in entry['banks'].values():send(b['cue'],5,start+6+delay)
    a.run_until(start+5);event=obs(a,entry['base'])
    a.run_until(start+9+delay)
    entry.update(acquired_at=start+9+delay,teacher_signal_supplied=signal,last_operation='CURRENT_CONTACT_EXPERIENCE')
    w.runtime.set_snapshot_metadata(KEY,encode_metadata(g))
    return {'ENTORNO':{'actual_actor_route':'contact_opportunity'if present else'offpath_actor','medium_payload':medium,'actor_state':actor_state},
        'ENTE':{'current_contact_event':event,'memory':{k:obs(a,b['hub'])for k,b in entry['banks'].items()}},
        'INSTRUMENTO':{'frame':frame,'start':start,'signal_after_event':signal,'requests':[receipt_at(w,r)for r in req]},
        'INTERPRETACION':'Teaching attempt, not automatic certification of Spanish acquisition. All class banks receive identical cues.'}

def contact_query(a,*,frame,word=None,use=False,payload=5):
    g=prepare(a)
    if frame not in g.get('contact_frames',{}):raise ValueError('Unknown physical contact frame')
    entry=g['contact_frames'][frame]
    if entry['acquired_at']is None:raise ValueError('No contact experience was presented in this frame')
    if entry['after_functional_use']:raise ValueError('The original reader is not validated after functional-use transformation. The lived state is preserved, never repaired/reset here.')
    if word not in(None,'toca','no toca')or type(use)is not bool or type(payload)is not int or not 0<=payload<=65535:raise ValueError('Explicit admitted contact query required')
    target=tick_at_or_after(a.tick,phase=entry['acquired_at']%67,lead=3);requests=[]
    selected={k:b for k,b in entry['banks'].items()if word is None or word==b['word']}
    for key,b in selected.items():
        r=a.world.probe(b['query'],payload,target-3);requests.append({'bank':key,'port':b['query'],'payload':payload,'tick':target-3,'id':int(r.id)})
        if use:
            r=a.world.submit(b['use'],7,target+3);requests.append({'bank':key,'port':b['use'],'payload':7,'tick':target+3,'id':int(r.id)})
    a.run_until(target);readings={k:obs(a,b['hub'])for k,b in selected.items()}
    if use:a.run_until(target+6)
    outputs={k:obs(a,b['effect']if use else b['hub'])for k,b in selected.items()}
    labels=[]
    for key,b in selected.items():
        expected=[0 if use else-b['axis'],1,b['z']]
        if valid(outputs[key],expected):labels.append(b['word'])
    entry.update(last_operation='FUNCTIONAL_USE'if use else'MATERIAL_FORM_QUERY',last_query_tick=target,after_functional_use=use)
    a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(g))
    return {'ENTE':{'read':readings,'output':outputs},'SPANISH_DECODED':list(dict.fromkeys(labels)),
        'INSTRUMENTO':{'frame':frame,'query_tick':target,'functional_use_requested':use,'requests':[receipt_at(a.world,r)for r in requests]},
        'INTERPRETACION':'Finite learned contact/free-flight expression. Repeated material queries may themselves teach/transform; functional use is explicitly consumptive for this reader.'}

def temporal_prepare(a,*,frame,origin=(8,8,22)):
    """Inert registration of the recovered parallel native event-shape protocol."""
    if not isinstance(frame,str)or not frame.isascii()or not frame.replace('_','').isalnum():raise ValueError('Explicit frame identifier required')
    if len(origin)!=3 or any(type(v)is not int or not 0<=v<67 for v in origin):raise ValueError('Explicit N67 physical origin required')
    g=prepare(a);frames=g.setdefault('temporal_frames',{})
    if frame in frames:
        if frames[frame]['origin']!=list(origin):raise ValueError('Lived temporal frame cannot move under the same identity')
        return frames[frame]
    from pathlib import Path
    import sys
    path=Path(__file__).resolve().parents[1]/'organizaciones/cpc9/front_relations/src'
    if str(path)not in sys.path:sys.path.insert(0,str(path))
    from tiled_order_parallel import component
    ports,entry=component(origin=tuple(origin));prefix='EF01.T.'+frame+'.';aliases={}
    for port in ports:
        old=port.name;new=prefix+old
        if new in a.world.runtime.channel_names:raise ValueError('Temporal channel collision')
        c=port.channel;c.name=new;q=d.InterfaceSpec();q.name=new;q.channel=c;a.world.declare_interface(q);aliases[old]=new
    entry.update(aliases=aliases,acquired_at=None,after_functional_use=False,spanish_codebook='Positive delta: A antes de B; negative delta: A después de B. External fixed bank translation, not learned free grammar.',
        scope='Two declared current physical event shapes, interval1/3/5, fixed accessible frame. New experiences establish physical signal carriers; the discrimination geometry is prepared.')
    frames[frame]=entry;a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(g));return entry

def temporal_experience(a,*,frame,order='AB',interval=5,a_load=3,b_load=3,signal=True,delay=0,event_a=True,event_b=True,offroute=False,additional=False):
    g=prepare(a)
    if frame not in g.get('temporal_frames',{}):raise ValueError('Prepare a physical temporal frame first')
    entry=g['temporal_frames'][frame]
    if entry['acquired_at']is not None and not additional:raise ValueError('Explicit additional=True required to add experience without resetting the lived frame')
    if entry['after_functional_use']:raise ValueError('Additional teaching after the consumptive use protocol is not validated')
    if order not in('AB','BA')or interval not in(1,3,5)or a_load not in(3,5)or b_load not in(3,5)or delay not in(0,1):raise ValueError('Outside the declared finite temporal protocol')
    start=tick_at_or_after(a.tick,phase=0,lead=4);times={order[0]:start,order[1]:start+interval};req=[]
    def send(old,payload,t):
        name=entry['aliases'][old];r=a.world.submit(name,payload,t);req.append({'port':name,'payload':payload,'tick':t,'id':int(r.id)})
    if event_a:send(entry['a_port'],a_load,times['A'])
    if event_b:
        for row in entry['b_ports']:send(row['offroute_port'if offroute else'port'],b_load,times['B'])
    if signal:
        for b in entry['surfaces']:send(b['record_port'],5,start+10+delay)
    a.run_until(start+12);pre={b['id']:obs(a,b['hub'])for b in entry['surfaces']}
    a.run_until(start+13+delay);post={b['id']:obs(a,b['hub'])for b in entry['surfaces']}
    entry.setdefault('experience_boundaries',[]).append({'start':start,'last_signal_tick':start+13+delay,'additional':additional})
    entry.update(acquired_at=start+13+delay,last_operation='CURRENT_TWO_EVENT_EXPERIENCE')
    a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(g))
    return {'ENTORNO':{'actual_event_schedule':times,'A_load':a_load,'B_shape_load_each':b_load,'B_shape_carriers':6,'event_a':event_a,'event_b':event_b,'offroute':offroute},
        'ENTE':{'pre_signal':pre,'post_signal':post},'INSTRUMENTO':{'start':start,'signal_after_events':signal,'all_six_banks_cued_equally':True,'requests':[receipt_at(a.world,r)for r in req]},
        'INTERPRETACION':'Native event encounters plus acquired opaque forms in a prepared order-discrimination geometry. Not acquisition of a universal temporal rule.'}

def temporal_query(a,*,frame,use=False,payload=7):
    g=prepare(a)
    if frame not in g.get('temporal_frames',{}):raise ValueError('Unknown temporal frame')
    entry=g['temporal_frames'][frame]
    if entry['acquired_at']is None:raise ValueError('No actual temporal experience yet')
    if entry['after_functional_use']:raise ValueError('Original reader after use is not validated; no silent reconstruction')
    if type(use)is not bool or type(payload)is not int or not 0<=payload<=65535:raise ValueError('Exact query resource required')
    target=tick_at_or_after(a.tick,phase=entry['acquired_at']%67,lead=3);req=[]
    for b in entry['surfaces']:
        name=entry['aliases'][b['read_port']];r=a.world.probe(name,payload,target-3);req.append({'port':name,'payload':payload,'tick':target-3,'id':int(r.id)})
        if use:
            name=entry['aliases'][b['use_port']];r=a.world.submit(name,11,target+3);req.append({'port':name,'payload':11,'tick':target+3,'id':int(r.id)})
    a.run_until(target);readings={b['id']:obs(a,b['hub'])for b in entry['surfaces']}
    if use:a.run_until(target+6)
    outputs={b['id']:obs(a,b['effect']if use else b['hub'])for b in entry['surfaces']};labels=[]
    for b in entry['surfaces']:
        if valid(outputs[b['id']],(0,0,1)if use else(0,1,1)):
            labels.append({'text':'A antes de B'if b['delta']>0 else'A después de B','bank':b['id'],'delta_bin':b['delta']})
    entry.update(last_query_tick=target,after_functional_use=use,last_operation='FUNCTIONAL_USE'if use else'MATERIAL_TEMPORAL_FORM_QUERY')
    a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(g))
    return {'ENTE':{'read':readings,'output':outputs},'SPANISH_DECODED':labels,'INSTRUMENTO':{'frame':frame,'query_tick':target,'use_requested':use,'requests':[receipt_at(a.world,r)for r in req]},
        'INTERPRETACION':'Finite native acquired current-event order forms. Bank-to-Spanish translation is fixed; no absolute tick is a response token and no target chooses the queried bank.'}

def contact_social(a,*,source_frame,communication,use=False,omit_B_cue=False,omit_C_cue=False,cut_message=False,sham=False,distance=5,trace_receiver=False):
    """Prepared native opportunities, source acquired history determines content.

    Two right-hand class channels are always supplied equally. B and C are
    physical regions of this one runtime, not hidden cross-world callbacks.
    """
    if not isinstance(communication,str)or not communication.isascii()or not communication.replace('_','').isalnum():raise ValueError('Explicit communication identity required')
    if distance not in(5,7,9):raise ValueError('Social channel distance requires separate validation at5/7/9')
    g=prepare(a)
    if source_frame not in g.get('contact_frames',{}):raise ValueError('Unknown lived source frame')
    source=g['contact_frames'][source_frame]
    if source['acquired_at']is None or source['after_functional_use']:raise ValueError('Source is not in the admitted pre-use contact protocol')
    communications=g.setdefault('social_contacts',{})
    if communication in communications:raise ValueError('Communication history already exists; query or continue it, never silently reconstruct')
    w=a.world;req=[];channels=[];target=tick_at_or_after(a.tick,phase=source['acquired_at']%67,lead=5)
    def declare(role,site,vector,semantic=1):
        name='EF01.S.'+communication+'.'+role
        if name in w.runtime.channel_names:raise ValueError('Social channel collision')
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(*vector);c.state=1;c.semantic=semantic;c.allow_experience=True;c.allow_probe=True
        p=d.InterfaceSpec();p.name=name;p.channel=c;w.declare_interface(p);return name
    def send(port,payload,t,probe=False):
        r=(w.probe if probe else w.submit)(port,payload,t);req.append({'port':port,'payload':payload,'tick':t,'id':int(r.id),'probe':probe})
    for key,b in source['banks'].items():
        if b['axis']!=1:continue
        v=(-1,1,b['z']);B=move(b['hub'],v,distance);C=move(B,v,6);effect=move(C,v,6);item={'id':key,'word':b['word'],'z':b['z'],'source_hub':b['hub'],'B_hub':B,'C_hub':C,'effect':effect,'ports':{}}
        for role,site,vector in(('Bcue',B,(1,0,0)),('Bread',B,(-1,0,0)),('Ccue',C,(1,0,0)),('Cread',C,(-1,0,0)),('use',effect,(1,0,0))):
            item['ports'][role]=declare(key+'.'+role,move(site,vector,-3),vector)
        cutsite=move(b['hub'],v,3)
        if sham:cutsite=move(cutsite,(0,0,1),9)
        item['cut_site']=cutsite;item['ports']['cut']=declare(key+'.cut',cutsite,(0,0,0),4)
        send(b['query'],5,target-3,True)
        if cut_message or sham:send(item['ports']['cut'],0,target+1)
        if not omit_B_cue:send(item['ports']['Bcue'],5,target+distance-3)
        send(item['ports']['Bread'],5,target+distance+64,True)
        if not omit_C_cue:send(item['ports']['Ccue'],5,target+distance+70)
        send(item['ports']['Cread'],5,target+distance+137,True)
        if use:send(item['ports']['use'],7,target+distance+143)
        channels.append(item)
    frames=[];trace=[]
    stages=[(0,'source_read','source_hub'),(2,'before_message_cut','cut_site'),(3,'after_message_cut','cut_site'),(distance,'B_acquisition','B_hub'),(distance+67,'B_query','B_hub'),(distance+73,'C_return_acquisition','C_hub'),(distance+140,'C_query','C_hub')]
    events={dt:(label,sitekey)for dt,label,sitekey in stages}
    for dt in sorted(set(events)|set(range(distance+1,distance+67)if trace_receiver else())):
        if trace_receiver and distance<dt<distance+67:
            from app.native_tools import moore27
            sites={b['id']:move(b['B_hub'],(0,1,b['z']),dt-distance)for b in channels}
            before={key:moore27(w,site)for key,site in sites.items()}
        a.run_until(target+dt)
        if dt in events:
            label,sitekey=events[dt];frames.append({'label':label,'tick':a.tick,'records':{b['id']:obs(a,b[sitekey])for b in channels}})
        if trace_receiver and distance<dt<distance+67:
            trace.append({'tick':a.tick,'hypothesized_native_B_route':sites,'pre_neighbors':before,'post_neighbors':{key:moore27(w,site)for key,site in sites.items()},'records':{key:obs(a,site)for key,site in sites.items()},'lineage_warning':'Route prediction is not alone a proof of identity; pre/post neighbors and actual encounters must be reviewed.'})
    if use:
        a.run_until(target+distance+146);frames.append({'label':'C_use','tick':a.tick,'records':{b['id']:obs(a,b['effect'])for b in channels}})
    outputs=frames[-1]['records'];labels=[b['word']for b in channels if valid(outputs[b['id']],(0 if use else-1,1,b['z']))]
    entry={'source_frame':source_frame,'channels':channels,'source_read_tick':target,'last_C_query_tick':target+distance+140,'distance':distance,'after_functional_use':use,'same_runtime_native_transport':True,
        'scope':'Prepared channel and recipient, acquired content. B is a physical receiver, not a complete second mind. Original source-reader continuity after transfer is not promised.'}
    communications[communication]=entry;w.runtime.set_snapshot_metadata(KEY,encode_metadata(g))
    return {'ENTE':frames,'TRACE':trace,'SPANISH_DECODED':labels,'INSTRUMENTO':{'communication':communication,'channels':channels,'requests':[receipt_at(w,r)for r in req],'cut_message':cut_message,'sham':sham,'omit_B_cue':omit_B_cue,'omit_C_cue':omit_C_cue,'use':use,'distance':distance},
        'INTERPRETACION':'Actual native communication and subsequent receptor query/use, not external copy of the source response. Physical transfer may change the old reader; content-preserving source replication is not claimed.'}

def contact_social_query(a,*,communication,use=False):
    g=prepare(a)
    if communication not in g.get('social_contacts',{}):raise ValueError('Unknown native communication')
    entry=g['social_contacts'][communication]
    if entry['after_functional_use']:raise ValueError('Post-use transformed social reader not validated')
    target=tick_at_or_after(a.tick,phase=entry['last_C_query_tick']%67,lead=3);req=[]
    for b in entry['channels']:
        r=a.world.probe(b['ports']['Cread'],5,target-3);req.append({'port':b['ports']['Cread'],'payload':5,'tick':target-3,'id':int(r.id)})
        if use:
            r=a.world.submit(b['ports']['use'],7,target+3);req.append({'port':b['ports']['use'],'payload':7,'tick':target+3,'id':int(r.id)})
    a.run_until(target);readings={b['id']:obs(a,b['C_hub'])for b in entry['channels']}
    if use:a.run_until(target+6)
    outputs={b['id']:obs(a,b['effect']if use else b['C_hub'])for b in entry['channels']};labels=[b['word']for b in entry['channels']if valid(outputs[b['id']],(0 if use else-1,1,b['z']))]
    entry.update(last_C_query_tick=target,after_functional_use=use);a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(g))
    return {'ENTE':{'read':readings,'output':outputs},'SPANISH_DECODED':labels,'INSTRUMENTO':{'query_tick':target,'requests':[receipt_at(a.world,r)for r in req],'material_probe':True,'use':use},'INTERPRETACION':'Later use of the acquired returned content; not a fresh transmission or externally completed response.'}

def compose_contact_temporal(a,*,contact_frame,temporal_frame):
    """Finite consumptive native composer, not a general grammatical operation."""
    g=prepare(a)
    if contact_frame not in g.get('contact_frames',{})or temporal_frame not in g.get('temporal_frames',{}):raise ValueError('Both lived physical frames required')
    c=g['contact_frames'][contact_frame];t=g['temporal_frames'][temporal_frame]
    if c['base']!=[28,34,54]or t['origin']!=[5,32,28]or c['acquired_at']%67!=6 or t['acquired_at']%67!=13:
        raise ValueError('This fixed composer is validated only for the declared frames/phases, not arbitrary relocated bodies')
    if c['after_functional_use']or t['after_functional_use']:raise ValueError('A prior consumptive operation invalidates the old composer contract')
    target=tick_at_or_after(a.tick,phase=13,lead=11);cq=target-7;req=[];J=[12,58,54];effect=[6,64,60]
    for b in c['banks'].values():
        r=a.world.probe(b['query'],5,cq-3);req.append({'port':b['query'],'payload':5,'tick':cq-3,'id':int(r.id)})
    for b in t['surfaces']:
        name=t['aliases'][b['read_port']];r=a.world.probe(name,7,target-3);req.append({'port':name,'payload':7,'tick':target-3,'id':int(r.id)})
    name='EF01.COMPOSE.PUBLISHED.'+contact_frame+'.'+temporal_frame
    if name in a.world.runtime.channel_names:raise ValueError('One-shot composer already used; preserve its lived outcome')
    ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*move(effect,(1,0,0),-3));ch.direction=d.Direction(1,0,0);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True
    p=d.InterfaceSpec();p.name=name;p.channel=ch;a.world.declare_interface(p);r=a.world.submit(name,7,target+16);req.append({'port':name,'payload':7,'tick':target+16,'id':int(r.id)})
    a.run_until(target+12);pre=obs(a,J);a.run_until(target+13);joint=obs(a,J);a.run_until(target+19);output=obs(a,effect)
    c['after_functional_use']=True;t['after_functional_use']=True
    g.setdefault('compositions',[]).append({'contact_frame':contact_frame,'temporal_frame':temporal_frame,'tick':a.tick,'join_tick':target+13,'effect_tick':target+19,'one_shot_consumptive':True})
    a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(g))
    return {'ENTE':{'pre_join':pre,'joint':joint,'consequence':output},'COMPOSITION_OBSERVED':valid(joint,(-1,1,1))and valid(output,(0,1,1)),
        'INSTRUMENTO':{'join_site':J,'effect_site':effect,'requests':[receipt_at(a.world,r)for r in req]},
        'INTERPRETACION':'Prepared coincidence/action apparatus uses acquired contact and a new temporal form. Not learned grammar or arbitrary relational composition. Original readers are explicitly marked post-use unvalidated; no silent repair.'}

def produce_relations(a,*,frame,bridge,parameter,load=3,legacy_word_probes=True,bridge_word_probe=True):
    """Use every declared legacy phase and the admitted alternative route.

    Coordinator repeats a physical scene, never selects a source from its
    correct answer. Conflicting native emissions remain visible.
    """
    from capacidades import ensenanza_lexica_03 as f,puente_lexico_10 as z
    if type(legacy_word_probes)is not bool or type(bridge_word_probe)is not bool:raise ValueError('Explicit physical probe choices required')
    legacy=f.context(a,frame=frame,parameter=parameter,load=load,decoder='strict',emit_word_queries=legacy_word_probes)
    alternative=z.context(a,bridge=bridge,parameter=parameter,load=load,probe=bridge_word_probe)
    words=sorted(set([r['text']for r in legacy['SPANISH_DECODED']]+alternative['SPANISH_DECODED']))
    return {'ENTORNO':{'actual_parameter':parameter,'load_each':load,'physical_scene_presentations':len(legacy['ENTE'])+1,'teacher_word_supplied':False},
        'ENTE':{'legacy':legacy,'alternative':alternative},'SPANISH_DECODED':words,
        'INSTRUMENTO':{'coordination':'All acquired legacy phases and the alternative bridge are used for every scene. No target-based source choice.','legacy_word_probes':legacy_word_probes,'bridge_word_probe':bridge_word_probe,'status':'ONE_OBSERVED_WORD'if len(words)==1 else('INDETERMINATE'if not words else'CONFLICTING_NATIVE_WORDS')},
        'INTERPRETACION':'A connected prepared protocol, not learned routing or free dialogue. Input scenes are repeated and all their physical costs are counted.'}


