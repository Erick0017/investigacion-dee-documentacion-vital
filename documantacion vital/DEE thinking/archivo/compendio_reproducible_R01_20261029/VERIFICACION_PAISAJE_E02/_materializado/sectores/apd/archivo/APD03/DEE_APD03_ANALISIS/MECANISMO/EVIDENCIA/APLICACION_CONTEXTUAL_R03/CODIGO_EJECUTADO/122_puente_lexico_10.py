"""Optional native normalization bridge for one blocked lexical trajectory.

Original banks remain unchanged. A fixed -Y opportunity transforms the
native Y/Z perceptual carrier into a +Z bus before a separate word site.
No current parameter or expected answer selects the bridge at test time.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from app.native_tools import moore27
from capacidades import espanol_funcional_01 as e,ensenanza_lexica_03 as f

def prepare(a,*,bridge,source_frame='lexical05',source_bank='d5',phase_shift=0):
    if not bridge.isascii()or not bridge.replace('_','').isalnum():raise ValueError('Explicit bridge identity required')
    g=e.prepare(a);entry=g.get('relational_words_v2',{}).get(source_frame)
    if entry is None or'lexical_v3'not in entry:raise ValueError('Existing lexical/perceptual source frame required')
    bridges=g.setdefault('lexical_bridges_v10',{})
    if bridge in bridges:
        old=bridges[bridge]
        if old['source_frame']!=source_frame or old['source_bank']!=source_bank or old.get('source_phase',0)!=phase_shift:raise ValueError('Existing bridge cannot move or change source phase silently')
        return old
    b=next((b for b in entry['banks']if b['id']==source_bank),None)
    if b is None:raise ValueError('Physical source bank absent')
    P=e.move(b['hub'],(0,1,1),-4);hub=e.move(P,(0,0,1),5);ports={};guards=[]
    def port(role,target,v,sem=1,lead=3):
        name='EF01.BRIDGE10.'+bridge+'.'+role
        if name in a.world.runtime.channel_names:raise ValueError('Lexical bridge channel collision')
        ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*e.move(target,v,-lead));ch.direction=d.Direction(*v);ch.state=1;ch.semantic=sem;ch.allow_experience=True;ch.allow_probe=True
        p=d.InterfaceSpec();p.name=name;p.channel=ch;a.world.declare_interface(p);ports[role]=name;return name
    port('normalize',P,(0,-1,0));port('query',hub,(0,1,0))
    for sign in(-1,1):port('cue'+str(sign),hub,(sign,1,0))
    guard_sites=[e.move(P,(0,-1,0),3),e.move(hub,(1,1,0),3),e.move(hub,(-1,1,0),3),e.move(hub,(0,1,0),3)]
    for j,site in enumerate(guard_sites):port('guard'+str(j),site,(0,0,0),4,0);guards.append(site)
    port('cut',e.move(P,(0,0,1),2),(0,0,0),4,0);port('sham',e.move(e.move(P,(0,0,1),2),(1,0,0),9),(0,0,0),4,0)
    if phase_shift not in(0,8,12):raise ValueError('Separate declared source phase0/8/12 required')
    value={'schema':'DCS1.1.EF01.lexical_bridge.r10','source_frame':source_frame,'source_bank':source_bank,'source_phase':phase_shift,'normalize_site':P,'hub':hub,'ports':ports,'guard_sites':guards,'guard_installation':False,'word_phase':(14+phase_shift)%67,'taught':False,
        'codebook':entry['lexical_v3']['codebook'],'signature_rule':'state1SEM1, abs(X)=1,Y=Z=1, word solely from nativeX sign',
        'scope':'One prepared alternative native access path to the same physical event-shape branch. Not an autonomous selection of reader or a universal lexical abstraction.'}
    bridges[bridge]=value;a.world.runtime.set_snapshot_metadata(e.KEY,encode_metadata(g));return value

def _send(a,req,name,payload,t,probe=False):
    r=(a.world.probe if probe else a.world.submit)(name,payload,t);req.append({'port':name,'payload':payload,'tick':t,'id':int(r.id)})

def _event(a,entry,parameter,load,start,req,event_a=True,event_b=True,offroute=False):
    source=e.prepare(a)['relational_words_v2'][entry['source_frame']]
    if source['mode']!='relative_path'or parameter not in(-5,-3,-1,1,3,5)or load not in(3,5):raise ValueError('Finite relative-path source domain')
    if event_a:_send(a,req,source['ports']['A_positions'][str(parameter)],load,start)
    if event_b:
        for row in source['ports']['B']:_send(a,req,row['off'if offroute else'on'],load,start)

def teach(a,*,bridge,word='cerca',parameter=5,signal=True,cut=False,sham=False):
    g=e.prepare(a);entry=g.get('lexical_bridges_v10',{}).get(bridge)
    if entry is None:raise ValueError('Prepare a bridge first')
    if entry['taught']:raise ValueError('Bridge already lived a teaching attempt; preserve it, never reset')
    reverse={v:int(k)for k,v in entry['codebook'].items()}
    if word not in reverse:raise ValueError('Unknown explicit teacher token')
    start=e.tick_at_or_after(a.tick,phase=entry.get('source_phase',0),lead=5);req=[];_event(a,entry,parameter,3,start,req)
    _send(a,req,entry['ports']['normalize'],0,start+6)
    if signal:_send(a,req,entry['ports']['cue'+str(reverse[word])],5,start+11)
    if cut or sham:_send(a,req,entry['ports']['cut'if cut else'sham'],0,start+10)
    if not entry['guard_installation']:
        for j in range(4):_send(a,req,entry['ports']['guard'+str(j)],0,start)
        entry['guard_installation']=True
    frames=[]
    for dt,label,site in((8,'pre_normalize',entry['normalize_site']),(9,'normalize',entry['normalize_site']),(11,'bus',e.move(entry['normalize_site'],(0,0,1),2)),(13,'pre_word',entry['hub']),(14,'word',entry['hub'])):
        a.run_until(start+dt);frames.append({'label':label,'tick':a.tick,'record':e.obs(a,site),'moore':moore27(a.world,site)})
    entry['taught']=True;entry['teaching_boundary']=a.tick;a.world.runtime.set_snapshot_metadata(e.KEY,encode_metadata(g))
    return {'ENTORNO':{'actual_parameter':parameter,'current_source_frame':entry['source_frame']},'ENTE':frames,'INSTRUMENTO':{'teacher_word':word,'same_fixed_native_normalizer':True,'requests':[e.receipt_at(a.world,r)for r in req],'cut':cut,'sham':sham,'signal':signal},
        'INTERPRETACION':'A new signal association uses actual native information after normalization. It does not import a learned snapshot or rewrite original memory fields.'}

def _decode(record,entry):
    if record['active']and record['state']==1 and record['semantic']==1 and record['direction'][1:]==[1,1]and record['direction'][0]in(-1,1):return entry['codebook'][str(record['direction'][0])]
    return None

def query(a,*,bridge,payload=7):
    entry=e.prepare(a).get('lexical_bridges_v10',{}).get(bridge)
    if entry is None or not entry['taught']or entry.get('after_comprehension',False):raise ValueError('Lived pre-use bridge required; the consumptive reader is not repaired automatically')
    target=e.tick_at_or_after(a.tick,phase=entry['word_phase'],lead=3);req=[];_send(a,req,entry['ports']['query'],payload,target-3,True);a.run_until(target);out=e.obs(a,entry['hub']);word=_decode(out,entry)
    return {'ENTE':out,'SPANISH_DECODED':[]if word is None else[word],'INSTRUMENTO':{'tick':target,'requests':[e.receipt_at(a.world,r)for r in req]},'INTERPRETACION':'Material recall via the alternative site; no word is read from the teacher log or bank name.'}

def context(a,*,bridge,parameter=5,load=3,probe=True,event_a=True,event_b=True,offroute=False):
    entry=e.prepare(a).get('lexical_bridges_v10',{}).get(bridge)
    if entry is None or not entry['taught']or entry.get('after_comprehension',False):raise ValueError('Lived pre-use bridge required')
    baseline=e.tick_at_or_after(a.tick,phase=entry['word_phase'])
    if baseline>a.tick:a.run_until(baseline)
    before=e.obs(a,entry['hub']);target=baseline+67;start=target-14;req=[]
    _event(a,entry,parameter,load,start,req,event_a,event_b,offroute);_send(a,req,entry['ports']['normalize'],0,start+6)
    if probe:_send(a,req,entry['ports']['query'],7,target-3,True)
    a.run_until(start+9);bus=e.obs(a,entry['normalize_site']);a.run_until(target);after=e.obs(a,entry['hub']);delta=after['s_reg']-before['s_reg']-(7 if probe else 0);oldword=_decode(before,entry);newword=_decode(after,entry)
    strict=[newword]if oldword==newword and newword is not None and delta in(6,10)else[];band=[newword]if oldword==newword and newword is not None and delta in(6,7,8,10,11,12)else[]
    return {'ENTORNO':{'actual_parameter':parameter,'load_each':load,'teacher_word_supplied':False,'event_a':event_a,'event_b':event_b,'offroute':offroute},'ENTE':{'before':before,'after':after,'normalized_current_bus':bus},
        'SPANISH_DECODED':strict,'BOUNDED_PROVISION_DECODED':band,'INSTRUMENTO':{'baseline_tick':baseline,'word_tick':target,'word_increment_after_query_dose':delta,'probe':probe,'requests':[e.receipt_at(a.world,r)for r in req]},
        'INTERPRETACION':'Contextual modulation of an acquired alternative word carrier. Strict and bounded decoders fixed before this cut; no environment-parameter sign is used to choose the token.'}

def comprehend(a,*,bridge,word):
    g=e.prepare(a);entry=g.get('lexical_bridges_v10',{}).get(bridge)
    if entry is None or not entry['taught']or entry.get('after_comprehension',False):raise ValueError('Lived pre-use bridge required')
    reverse={v:int(k)for k,v in entry['codebook'].items()}
    if word not in reverse:raise ValueError('Unknown token; no language completion')
    direction=(-reverse[word],1,0);effect=e.move(entry['hub'],(0,1,1),6);ports={}
    for role,site,v in(('token'+str(reverse[word]),entry['hub'],direction),('action',effect,(0,-1,0))):
        name='EF01.BRIDGE10.USE.'+bridge+'.'+role
        if name not in a.world.runtime.channel_names:
            ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*e.move(site,v,-3));ch.direction=d.Direction(*v);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=name;p.channel=ch;a.world.declare_interface(p)
        ports[role]=name
    target=e.tick_at_or_after(a.tick,phase=entry['word_phase'],lead=3);req=[];_send(a,req,ports['token'+str(reverse[word])],7,target-3,True);_send(a,req,ports['action'],11,target+3)
    a.run_until(target);read=e.obs(a,entry['hub']);a.run_until(target+6);output=e.obs(a,effect);entry['after_comprehension']=True;a.world.runtime.set_snapshot_metadata(e.KEY,encode_metadata(g))
    return {'ENTE':{'read':read,'effect':output},'NATIVE_ACTION_OBSERVED':e.valid(output,(0,0,1)),
        'INSTRUMENTO':{'recognized_token':word,'fixed_physical_token':list(direction),'effect_site':effect,'requests':[e.receipt_at(a.world,r)for r in req],'consumptive':True},
        'INTERPRETACION':'Prepared word cue and action path; acquired X marker determines success. Old lexical reader is explicitly post-use unvalidated.'}

def communicate(a,*,bridge,communication,cut=False,sham=False,omit_receiver_cue=False,request_word=None):
    """E1 learned lexical form enters a physical B region, stored then queried.

    Optional request_word tests consumptive native matching/action. None
    preserves the full marker and later checks the original E1 reader.
    """
    g=e.prepare(a);source=g.get('lexical_bridges_v10',{}).get(bridge)
    if source is None or not source['taught']or source.get('after_comprehension',False):raise ValueError('Admitted lived lexical source required')
    communications=g.setdefault('lexical_social_v13',{})
    if communication in communications:raise ValueError('Lived social channel cannot be reconstructed silently')
    reverse={v:int(k)for k,v in source['codebook'].items()}
    if request_word is not None and request_word not in reverse:raise ValueError('Unknown receiver token')
    req=[];branches=[];target=e.tick_at_or_after(a.tick,phase=source['word_phase'],lead=5)
    def port(role,target_site,v,sem=1,lead=3):
        name='EF01.LXSOC13.'+communication+'.'+role
        ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*e.move(target_site,v,-lead));ch.direction=d.Direction(*v);ch.state=1;ch.semantic=sem;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=name;p.channel=ch;a.world.declare_interface(p);return name
    _send(a,req,source['ports']['query'],7,target-3,True)
    for sign in(-1,1):
        B=e.move(source['hub'],(sign,1,1),5);cutsite=e.move(source['hub'],(sign,1,1),3)
        if sham:cutsite=e.move(cutsite,(0,1,0),9)
        row={'sign':sign,'B_hub':B,'cut_site':cutsite,'effect':e.move(B,(0,1,1),6),'ports':{}}
        row['ports']['cue']=port(str(sign)+'.cue',B,(0,-1,-1));row['ports']['query']=port(str(sign)+'.query',B,(0,1,1))
        row['ports']['cut']=port(str(sign)+'.cut',cutsite,(0,0,0),4,0)
        if cut or sham:_send(a,req,row['ports']['cut'],0,target+1)
        if not omit_receiver_cue:_send(a,req,row['ports']['cue'],5,target+2)
        _send(a,req,row['ports']['query'],7,target+69,True)
        if request_word is not None:
            row['ports']['token']=port(str(sign)+'.token',B,(-reverse[request_word],1,0));row['ports']['action']=port(str(sign)+'.action',row['effect'],(0,-1,0))
            _send(a,req,row['ports']['token'],7,target+136,True);_send(a,req,row['ports']['action'],11,target+142)
        branches.append(row)
    frames=[]
    for dt,label in((0,'E1_source'),(4,'pre_receiver'),(5,'B_acquisition'),(71,'pre_B_query'),(72,'B_query')):
        a.run_until(target+dt);sites={'E1':source['hub']}if dt==0 else{str(b['sign']):b['B_hub']for b in branches}
        frames.append({'label':label,'tick':a.tick,'records':{k:e.obs(a,p)for k,p in sites.items()},'moore':{k:moore27(a.world,p)for k,p in sites.items()}})
    Bwords=[source['codebook'][str(row['direction'][0])]for row in frames[-1]['records'].values()if row['active']and row['state']==1 and row['semantic']==1 and row['direction'][1:]==[1,1]and row['direction'][0]in(-1,1)]
    if request_word is None:
        _send(a,req,source['ports']['query'],7,target+131,True);a.run_until(target+134);frames.append({'label':'E1_returned_source_query','tick':a.tick,'records':{'E1':e.obs(a,source['hub'])},'moore':{'E1':moore27(a.world,source['hub'])}})
    else:
        a.run_until(target+139);frames.append({'label':'B_token_match','tick':a.tick,'records':{str(b['sign']):e.obs(a,b['B_hub'])for b in branches}})
        a.run_until(target+145);frames.append({'label':'B_action','tick':a.tick,'records':{str(b['sign']):e.obs(a,b['effect'])for b in branches}});source['after_comprehension']=True
    communications[communication]={'source_bridge':bridge,'B_branches':branches,'target':target,'B_word_query_tick':target+72,'same_runtime':True,'B_role':'Native receiver region with acquired marker, not a complete second mind or independent perceptual acquisition.'}
    a.world.runtime.set_snapshot_metadata(e.KEY,encode_metadata(g))
    return {'ENTE':frames,'B_WORDS_DECODED':Bwords,'B_NATIVE_ACTION_BRANCHES':[]if request_word is None else[k for k,row in frames[-1]['records'].items()if e.valid(row,(0,0,1))],
        'INSTRUMENTO':{'request_word':request_word,'branches':branches,'cut':cut,'sham':sham,'omit_receiver_cue':omit_receiver_cue,'requests':[e.receipt_at(a.world,r)for r in req],'consumptive':request_word is not None},
        'INTERPRETACION':'Real native learned-code transmission/storage/use. Fixed recipients and codebook; no role-relativeYO/TU, autonomous partner choice, or E5human-distance meaning is inferred.'}
