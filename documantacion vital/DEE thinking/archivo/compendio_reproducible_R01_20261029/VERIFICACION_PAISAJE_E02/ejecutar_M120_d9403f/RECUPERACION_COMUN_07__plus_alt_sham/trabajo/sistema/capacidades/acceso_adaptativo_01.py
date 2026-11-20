"""Private finite AA01 protocols on an existing lived N67 world.

Preparation, learned native routing and translation are separate. No reports,
laboratory files, expected answers or old trained states choose the response.
"""
import re,time
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from dee_thinking.consolidated import exact_receipt
from capacidades import espanol_funcional_01 as e
from capacidades.conductos_acceso_aa01 import routes_for_common_arrival

KEY='DEE.Cognitive.System.1.1.AA01.operations.v1'
S=[32,32,49]

def _configuration(a):
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if int(a.world.runtime.dimension)!=67 or e.KEY not in entries or not hasattr(a,'quantity'):raise ValueError('AA01 requires an existing complete N67 Spanish/CPC9 world; no substitute is prepared')
    return decode_metadata(entries[KEY])if KEY in entries else{'schema':'DCS1.1.AA01.operational.v1','episodes':{},'current':None}

def _save(a,cfg):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(cfg))
def _move(q,v,k):return[(q[i]+v[i]*k)%67 for i in range(3)]

def _submit(a,name,site,vector,tick,payload=0,semantic=1):
    if type(tick)is not int or tick<a.tick or type(payload)is not int or not 0<=payload<=65535:raise ValueError('Exact future tick and uint16 material input required')
    existing=next((p for p in a.world.interfaces if p.name==name),None)
    wanted=(list(site),list(vector),1,semantic)
    if existing is None:
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(*vector);c.state=1;c.semantic=semantic;c.allow_experience=True;c.allow_probe=True;p=d.InterfaceSpec();p.name=name;p.channel=c;a.world.declare_interface(p)
    else:
        c=existing.channel;actual=([c.injection_site.x,c.injection_site.y,c.injection_site.z],[c.direction.dx,c.direction.dy,c.direction.dz],c.state,c.semantic)
        if actual!=wanted:raise ValueError('Existing interface has another physical contract')
    receipt=a.world.submit(name,payload,tick)
    return{'id':int(receipt.id),'port':name,'site':list(site),'direction':list(vector),'tick':tick,'payload':payload,'semantic':semantic,'receipt':exact_receipt(receipt)}

def _advance(a,target,seconds=120):
    if target<a.tick:raise ValueError('Protocol window already passed; no rewind or old transcript is returned')
    began=time.perf_counter()
    while a.tick<target:
        a.run_until(min(target,a.tick+4))
        if a.tick<target and time.perf_counter()-began>seconds:raise TimeoutError('AA01 cooperative advance limit; preserve actual reached state and continue explicitly, never retry from an old checkpoint')

def _native_code(row):
    if e.valid(row,(1,1,-1)):return'menos'
    if e.valid(row,(1,1,1)):return'más'
    return None

def state(a):
    cfg=_configuration(a)
    site=cfg['episodes'][cfg['current']]['policy_site']if cfg['current']else S
    return{'INSTRUMENTO':{'tick':a.tick,'current_episode':cfg['current'],'episodes':{k:{q:v.get(q)for q in('kind','epoch','goal_tick','end_tick','mode','last_stage')}for k,v in cfg['episodes'].items()},'passive':True,'last_stage_is_instrument_call_progress_not_a_knowledge_certificate':True},'ENTE':{'policy_site_now':e.obs(a,site)},'INTERPRETACION':'Current fields/progress only, not a certificate of retained knowledge. Off-phase absence is not forgetting.'}

def prepare_episode(a,*,episode,availability=(1,-1),mode='read_only',delay=0,query=True,feedback='paired'):
    cfg=_configuration(a)
    if not isinstance(episode,str)or not re.fullmatch(r'[A-Za-z0-9_.-]{1,32}',episode):raise ValueError('Explicit short episode ID required')
    if episode in cfg['episodes']:raise ValueError('Episode already exists; advance its actual state or start a genuinely new episode')
    if cfg['current']and a.tick<cfg['episodes'][cfg['current']]['end_tick']:raise ValueError('Previous finite protocol still has scheduled interactions')
    if not isinstance(availability,(tuple,list))or len(availability)!=2 or any(type(v)is not int or v not in(-1,1)for v in availability):raise ValueError('Two external physical route-availability contexts +/-1 required, not a target word')
    if mode not in('read_only','consumptive')or type(delay)is not int or not 0<=delay<=134 or type(query)is not bool or feedback not in('paired','omit_second','unpaired_second'):raise ValueError('Outside finite AA01 contract')
    words=e.prepare(a)['words'];start=a.tick+delay;prefix='DCS.AA01.'+episode;requests=[];supports=[];training={}
    def send(role,site,v,t,payload=0,semantic=1):
        row=_submit(a,prefix+'.'+role,site,v,t,payload,semantic);requests.append(row);return row
    def arrive(role,site,v,t,payload=0):return send(role,_move(site,v,-3),v,t-3,payload)
    for j in(-1,1):
        for r in(-1,1):
            E=_move(_move(S,(j,0,0),-10),(0,r,0),10);Q=_move(E,(j,r,1),-4);H=_move(Q,(0,0,1),-6);key=str(j)+','+str(r);training[key]={'j':j,'r':r,'outcome':E,'query':Q,'source':H}
            for label,site,t in(('pulse',_move(Q,(1,0,0),6),13),('feedback',_move(E,(0,-r,-1),4),16)):
                record=e.obs(a,site)
                if record['state']==1 and record['semantic']==4 and record['direction']==[0,0,0]:supports.append({'site':site,'reused_prepared_support':True,'native_observation':record})
                else:supports.append({'site':site,'new_input':send('SUPPORT.'+key+'.'+label,site,(0,0,0),start+t,0,4),'no_occupied_input_retry':True})
    for number,(offset,available)in enumerate(((0,availability[0]),(67,availability[1]))):
        for key,z in training.items():
            r=z['r'];j=z['j'];tag=str(number)+'.'+key
            arrive('LEARN.'+tag+'.cue',z['source'],(-1,0,0),start+offset+3,5);arrive('LEARN.'+tag+'.sample',z['source'],(1,0,1),start+offset+3,11)
            if r!=available:send('ENV.'+tag,z['query'],(1,0,0),start+offset+8,3)
            arrive('EXPLORE.'+tag,z['query'],(j,r,0),start+offset+9,5)
            if number and feedback=='omit_second':continue
            shift=1 if number and feedback=='unpaired_second'else 0
            arrive('CONSEQUENCE.'+tag+'.1',z['outcome'],(0,-r,-1),start+offset+13+shift,7);arrive('CONSEQUENCE.'+tag+'.2',z['outcome'],(0,-r,0),start+offset+13+shift,7)
    if query:arrive('COMMON_QUERY',S,(1,0,0),start+157,5)
    mapping={'1':'menos','-1':'más'};starts={};ends={}
    for key,word in mapping.items():
        p=int(key);signature=words[word]['signature'];starts[key]={'site':_move(S,(1,p,0),4),'direction':[1,p,0]};ends[key]={'site':words[word]['hub'],'direction':[-signature[0],-signature[1],0]if mode=='consumptive'else[0,0,signature[2]]}
    plans=routes_for_common_arrival(starts,ends,start+161,phase=6);goal=plans['1']['arrival_tick']
    for key,plan in plans.items():
        for j,turn in enumerate(plan['turns']):
            for k,pulse in enumerate(turn['pulses']):arrive('RELAY.'+key+'.'+str(j)+'.'+str(k),turn['site'],pulse['direction'],turn['tick'],pulse['payload'])
    B={}
    if mode=='consumptive':
        for word,item in words.items():
            for z in(-1,1):
                hub=_move(item['hub'],(0,0,z),4);key=word+'.'+str(z);effect=_move(hub,(1,1,z),4);B[key]={'hub':hub,'z':z,'effect':effect,'query_tick':goal+71}
                arrive('B.ACQUIRE.'+key,hub,(1,0,0),goal+4,5);arrive('B.QUERY.'+key,hub,(0,1,0),goal+71,7);arrive('B.USE.'+key,effect,(-1,-1,0),goal+75,5)
    ep={'schema':'AA01.connected_episode.v1','epoch':start,'goal_tick':goal,'end_tick':goal+75 if B else goal,'mode':mode,'policy_site':S,'training':training,'source_forms':words,'source_mapping':mapping,'endpoints':ends,'plans':plans,'recipient':B,'prepared_supports':supports,'scheduled_requests':requests,'last_stage':'QUEUED_UNTRAINED','assistance':'Timing, opportunities, feedback, transport geometry and recipient are prepared. Native state determines the branch. No automatic P2/semantic verdict.'}
    cfg['episodes'][episode]=ep;cfg['current']=episode
    if B:cfg['recipient_layout']={'B':B,'phase':(goal+75)%67,'old_phase':(goal+71)%67,'origin_episode':episode}
    _save(a,cfg)
    return{'INSTRUMENTO':{'episode':episode,'epoch':start,'goal_tick':goal,'end_tick':ep['end_tick'],'requests':requests,'supports':supports,'query_initiated_by':'EXTERNAL_DECLARED_PROTOCOL'if query else'OMITTED_CONTROL','native_advance':0},'INTERPRETACION':'Pending experiences/preparation, not a trained individual or an answer map.'}

def advance_episode(a,*,stage='learned',max_seconds=120):
    cfg=_configuration(a)
    if cfg['current']is None:raise ValueError('No existing episode; never build a substitute implicitly')
    if cfg['episodes'][cfg['current']].get('kind')=='LOCAL_S50':return advance_local_episode(a,stage=stage,max_seconds=max_seconds)
    ep=cfg['episodes'][cfg['current']];ticks={'first':ep['epoch']+23,'learned':ep['epoch']+90,'access':ep['goal_tick']}
    if ep['recipient']:ticks.update(received=ep['goal_tick']+4,social=ep['goal_tick']+71,use=ep['goal_tick']+75)
    if stage not in ticks or type(max_seconds)is not int or not 5<=max_seconds<=240:raise ValueError('Explicit supported stage and bounded time limit required')
    target=ticks[stage];pre=None;started_at=a.tick
    if stage=='access'and a.tick<=target-1:
        _advance(a,target-1,max_seconds)
        pre={word:{'memory':e.obs(a,_move(ep['source_forms'][word]['hub'],ep['source_forms'][word]['signature'],-1)),'query':e.obs(a,_move(ep['source_forms'][word]['hub'],ep['endpoints'][key]['direction'],-1))}for key,word in ep['source_mapping'].items()}
    _advance(a,target,max_seconds);native={'policy':e.obs(a,S)};decoded=[];details={}
    if stage=='access':
        native['forms']={word:e.obs(a,item['hub'])for word,item in ep['source_forms'].items()}
        for key,word in ep['source_mapping'].items():
            row=native['forms'][word]
            if ep['mode']=='consumptive':
                if e.valid(row,(0,0,-1)):decoded.append('menos')
                elif e.valid(row,(0,0,1)):decoded.append('más')
            elif pre is not None:
                old=pre[word]['memory'];query=pre[word]['query'];signature=ep['source_forms'][word]['signature'];qdirection=ep['endpoints'][key]['direction'];increment=row['s_reg']-old['s_reg'];qualified=e.valid(old,signature)and e.valid(row,signature)and query['raw']!='0'and query['direction']==qdirection and query['s_reg']>0 and increment==query['s_reg']
                details[word]={'pre_memory':old,'pre_query':query,'material_increment':increment,'qualified_material_access':qualified}
                if qualified:decoded.append(word)
    elif stage in('received','social','use'):
        native['B']={key:e.obs(a,item['effect']if stage=='use'else item['hub'])for key,item in ep['recipient'].items()}
        if stage=='social':decoded=[word for row in native['B'].values()if(word:=_native_code(row))is not None]
        elif stage=='use':
            for row in native['B'].values():
                if e.valid(row,(0,0,-1)):decoded.append('menos')
                elif e.valid(row,(0,0,1)):decoded.append('más')
    ep['last_stage']=stage;_save(a,cfg);decoded=sorted(set(decoded))
    return{'ENTE':native,'SPANISH_DECODED':decoded,'INSTRUMENTO':{'episode':cfg['current'],'stage':stage,'tick':a.tick,'advanced_ticks':a.tick-started_at,'material_access_details':details,'pre_access_observation_available':pre is not None,'status':'ONE_OBSERVED_CODE'if len(decoded)==1 else'CONFLICTING_CODES'if len(decoded)>1 else'NO_QUALIFIED_CODE','no_historical_response_replayed':True},'INTERPRETACION':'Finite prepared mechanism. Code recall/use is not current comparative truth or general autonomy; a selection can be consumed.'}

def recover_recipient(a,*,old_reader=True,payload=7,max_seconds=120):
    cfg=_configuration(a)
    if type(old_reader)is not bool or type(payload)is not int or payload!=7:raise ValueError('Common recovery: old-reader option and payload7; no target word')
    layout=cfg.get('recipient_layout');entries=dict(a.world.runtime.snapshot_metadata_entries)
    if layout is None and'DEE.Cognitive.System.1.1.AA01.B_recovery14'in entries:
        old=decode_metadata(entries['DEE.Cognitive.System.1.1.AA01.B_recovery14']);layout={'B':old['B'],'phase':old['phase'],'old_phase':old['old_phase']}
    if layout is None:raise ValueError('No complete lived recipient layout; no substitute receiver/knowledge is created')
    if layout.get('reader')=='NONE_IMMEDIATE_ONLY':raise ValueError('OUT_OF_VALIDATED_RECURRENT_READER_DOMAIN: this finite protocol has only immediate native use. No old response is replayed or a long-lived memory invented')
    if layout.get('reader')=='balanced_x':return recover_balanced_recipient(a,cfg,layout,old_reader=old_reader,max_seconds=max_seconds)
    B=layout['B'];old_tick=e.tick_at_or_after(a.tick,phase=layout['old_phase'],lead=8);target=e.tick_at_or_after(old_tick,phase=layout['phase']);requests=[]
    for key,item in B.items():
        if old_reader:requests.append(_submit(a,'DCS.AA01.B.OLD.'+key,_move(item['hub'],(0,1,0),-3),(0,1,0),old_tick-3,payload))
        requests.append(_submit(a,'DCS.AA01.B.ALTERNATE.'+key,_move(item['effect'],(1,1,0),-3),(1,1,0),target-3,payload))
    _advance(a,old_tick,max_seconds);before={key:e.obs(a,item['hub'])for key,item in B.items()};_advance(a,target,max_seconds);after={key:e.obs(a,item['effect'])for key,item in B.items()};decoded=sorted(set(word for row in after.values()if(word:=_native_code(row))is not None));cfg['recipient_layout']=layout;_save(a,cfg)
    opaque=layout.get('codebook')=='OPAQUE_Z';contents=[('Z-'if word=='menos'else'Z+')for word in decoded]if opaque else[]
    return{'ENTE':{'old':before,'alternative':after},'SPANISH_DECODED':[]if opaque else decoded,'CONTENT_CODES':contents,'INSTRUMENTO':{'old_reader_supplied':old_reader,'old_tick':old_tick,'alternative_tick':target,'requests':[{**row,'receipt':exact_receipt(a.world.runtime.receipt(row['id']))}for row in requests],'no_Z_content_supplied':True,'prepared_reader_not_self_selected':True,'codebook':layout.get('codebook','INHERITED_SPANISH_SOURCE_FORM')},'INTERPRETACION':'Recovery of retained received code, not current comparative truth. Opaque local codes are not promoted to Spanish words or NSM meanings. Empty/rejected/conflicting readings are never filled.'}

def prepare_local_episode(a,*,episode,availability=(1,-1),contents=(1,-1),feedback='paired',delay=0,recipient_mode='legacy_z'):
    """Finite S50 recipe; new physical samples, never old learned-field copies."""
    cfg=_configuration(a)
    if not isinstance(episode,str)or not re.fullmatch(r'[A-Za-z0-9_.-]{1,32}',episode)or episode in cfg['episodes']:raise ValueError('New explicit local episode ID required')
    if cfg['current']and a.tick<cfg['episodes'][cfg['current']]['end_tick']:raise ValueError('Earlier episode has pending interactions')
    if not isinstance(availability,(list,tuple))or len(availability)!=2 or any(type(v)is not int or v not in(-1,1)for v in availability):raise ValueError('Two declared physical utility contexts +/-1 required')
    if contents is not None and(not isinstance(contents,(list,tuple))or len(contents)!=2 or any(v is not None and(type(v)is not int or v not in(-1,1))for v in contents)):raise ValueError('Two actual material sample orientations or explicit omissions required; contents=None never reloads an old target')
    if feedback not in('paired','omit_second','unpaired_second','omit_all')or type(delay)is not int or not 0<=delay<=134:raise ValueError('Outside the finite local teaching contract')
    if recipient_mode not in('legacy_z','short_yz','immediate_yz'):raise ValueError('Explicit admitted finite recipient geometry required')
    start=a.tick+delay
    if start%67!=6:raise ValueError('S50 protocol validated at epoch phase6 only. Explicitly declare a future phase delay; no learned phase selection is claimed')
    center=[15,15,50];prefix='DCS.AA01.LOCAL.'+episode;requests=[];supports=[];training={};memories={str(r):_move(center,(1,r,0),4)for r in(-1,1)};B={}
    def send(role,site,vector,t,payload=0,semantic=1):
        row=_submit(a,prefix+'.'+role,site,vector,start+t,payload,semantic);requests.append(row);return row
    def arrive(role,site,vector,t,payload=0):return send(role,_move(site,vector,-3),vector,t-3,payload)
    for j in(-1,1):
        for r in(-1,1):
            E=_move(_move(center,(j,0,0),-10),(0,r,0),10);Q=_move(E,(j,r,1),-4);H=_move(Q,(0,0,1),-6);key=str(j)+','+str(r);training[key]={'j':j,'r':r,'outcome':E,'query':Q,'source':H}
            for label,site,t in(('pulse',_move(Q,(1,0,0),6),13),('feedback',_move(E,(0,-r,-1),4),16)):
                old=e.obs(a,site)
                if old['state']==1 and old['semantic']==4 and old['direction']==[0,0,0]:supports.append({'site':site,'reused_prepared_support':True,'observation':old})
                else:supports.append({'site':site,'new_input':send('SUPPORT.'+key+'.'+label,site,(0,0,0),t,0,4)})
    for k,(offset,available)in enumerate(((0,availability[0]),(67,availability[1]))):
        for key,z in training.items():
            r=z['r'];j=z['j'];tag=str(k)+'.'+key
            arrive('LEARN.'+tag+'.cue',z['source'],(-1,0,0),offset+3,5);arrive('LEARN.'+tag+'.event',z['source'],(1,0,1),offset+3,11)
            if r!=available:send('ENV.'+tag,z['query'],(1,0,0),offset+8,3)
            arrive('EXPLORE.'+tag,z['query'],(j,r,0),offset+9,5)
            if feedback=='omit_all'or k and feedback=='omit_second':continue
            shift=1 if k and feedback=='unpaired_second'else 0
            arrive('CONSEQUENCE.'+tag+'.1',z['outcome'],(0,-r,-1),offset+13+shift,7);arrive('CONSEQUENCE.'+tag+'.2',z['outcome'],(0,-r,0),offset+13+shift,7)
    if contents is not None:
        for key,M in memories.items():
            z=contents[0 if int(key)<0 else 1]
            if z is not None:arrive('NEW.'+key+'.cue',M,(-1,0,0),94,5);arrive('NEW.'+key+'.event',M,(1,0,z),94,11)
    arrive('COMMON_QUERY',center,(1,0,0),157,5)
    for key,M in memories.items():
        r=int(key)
        for z in(-1,1):
            if recipient_mode=='legacy_z':
                out=_move(M,(1,r,z),4);hub=_move(out,(0,0,z),4);effect=_move(hub,(1,1,z),4);keyB=key+','+str(z);B[keyB]={'hub':hub,'effect':effect,'z':z,'source_outcome':out}
                arrive('B.NORMALIZE_X.'+keyB,out,(-1,0,0),165,0);arrive('B.NORMALIZE_Y.'+keyB,out,(0,-r,0),165,5);arrive('B.ACQUIRE.'+keyB,hub,(1,0,0),169,7);arrive('B.RECALL.'+keyB,hub,(0,1,0),236,7);arrive('B.USE.'+keyB,effect,(-1,-1,0),240,5)
            elif recipient_mode=='short_yz':
                out=_move(M,(1,r,z),2);hub=_move(out,(1,0,z),4);effect=_move(hub,(1,1,z),4);keyB=key+','+str(z);B[keyB]={'hub':hub,'effect':effect,'z':z,'source_outcome':out}
                arrive('B.NORMALIZE_Y.'+keyB,out,(0,-r,0),163,7);arrive('B.ACQUIRE.'+keyB,hub,(0,1,0),167,7);arrive('B.RECALL.'+keyB,hub,(0,1,0),234,7);arrive('B.USE.'+keyB,effect,(-1,0,0),238,5)
            else:
                hub=_move(M,(1,r,z),1);effect=_move(M,(1,r,z),2);keyB=key+','+str(z);B[keyB]={'hub':hub,'effect':effect,'z':z,'r':r,'source_outcome':M}
                arrive('B.IMMEDIATE_RECEIVE.'+keyB,hub,(1,0,0),162,9);arrive('B.IMMEDIATE_USE.'+keyB,effect,(-1,0,0),163,5)
    timing={'first':23,'learned':90,'content':94,'access':161,'transformed':165,'received':169,'social':236,'use':240}if recipient_mode=='legacy_z'else{'first':23,'learned':90,'content':94,'access':161,'transformed':163,'received':167,'social':234,'use':238}if recipient_mode=='short_yz'else{'first':23,'learned':90,'content':94,'access':161,'received':162,'use':163}
    ep={'schema':'AA01.local_episode.S50.v1','kind':'LOCAL_S50','epoch':start,'goal_tick':start+161,'end_tick':start+timing['use'],'mode':'OPAQUE_CONTENT_LOCAL_ACCESS','recipient_mode':recipient_mode,'timing':timing,'policy_site':center,'training':training,'memories':memories,'recipient':B,'scheduled_requests':requests,'prepared_supports':supports,'content_teaching_omitted':contents is None,'feedback_mode':feedback,'last_stage':'QUEUED_UNTRAINED','assistance':'Fixed geometry, contexts, feedback opportunities, resources, clocks and B. Native state selects the route. No new Spanish/NSM meaning from opaque sample codes. Explicit content omissions are not repaired from recorded targets.'}
    layout={'B':B,'phase':(start+timing['use'])%67,'old_phase':(start+timing.get('social',timing['received']))%67,'origin_episode':episode,'codebook':'OPAQUE_Z'}
    if recipient_mode=='short_yz':layout.update(reader='balanced_x',reader_prefix='DCS.AA01.B.SHORT_YZ',balanced_vectors=[[0,1,-1],[0,1,1]])
    if recipient_mode=='immediate_yz':layout.update(reader='NONE_IMMEDIATE_ONLY',not_a_recurrent_communication_memory=True)
    cfg['episodes'][episode]=ep;cfg['current']=episode;cfg['recipient_layout']=layout;_save(a,cfg)
    return{'INSTRUMENTO':{'episode':episode,'kind':'LOCAL_S50','recipient_mode':recipient_mode,'epoch':start,'end_tick':ep['end_tick'],'native_advance':0,'requests':requests,'supports':supports},'INTERPRETACION':'A queued curriculum is not trained knowledge. Material contents are external experiences, not evaluation answers.'}

def advance_local_episode(a,*,stage='learned',max_seconds=120):
    cfg=_configuration(a)
    if not cfg['current']or cfg['episodes'][cfg['current']].get('kind')!='LOCAL_S50':raise ValueError('No current complete local episode; never construct one silently')
    ep=cfg['episodes'][cfg['current']];offsets=ep.get('timing',{'first':23,'learned':90,'content':94,'access':161,'transformed':165,'received':169,'social':236,'use':240})
    if stage not in offsets or type(max_seconds)is not int or not 5<=max_seconds<=240:raise ValueError('Supported local stage and bounded wall window required')
    began=a.tick;_advance(a,ep['epoch']+offsets[stage],max_seconds);native={'policy':e.obs(a,ep['policy_site'])};codes=[]
    if stage in('content','access'):
        native['memories']={key:e.obs(a,M)for key,M in ep['memories'].items()}
        if stage=='access':
            for key,row in native['memories'].items():
                for z in(-1,1):
                    if e.valid(row,(1,int(key),z)):codes.append('Z-'if z<0 else'Z+')
    if stage in('transformed','received','social','use'):
        field='source_outcome'if stage=='transformed'else'effect'if stage=='use'else'hub';native['B']={key:e.obs(a,item[field])for key,item in ep['recipient'].items()}
        for key,row in native['B'].items():
            if ep.get('recipient_mode')=='immediate_yz':
                r=ep['recipient'][key]['r']
                for z in(-1,1):
                    vector=(1,r,z)if stage=='received'else(0,r,z)
                    if e.valid(row,vector):codes.append('Z-'if z<0 else'Z+')
            elif ep.get('recipient_mode')=='short_yz':
                for z in(-1,1):
                    vector=(1,0,z)if stage=='transformed'else(0,1,z)if stage=='use'else(1,1,z)
                    if e.valid(row,vector):codes.append('Z-'if z<0 else'Z+')
            else:
                z=ep['recipient'][key]['z'];vector=(0,0,z)if stage in('transformed','use')else(1,1,z)if stage=='social'else(1,0,z)
                if e.valid(row,vector):codes.append('Z-'if z<0 else'Z+')
    ep['last_stage']=stage;_save(a,cfg);codes=sorted(set(codes))
    return{'ENTE':native,'CONTENT_CODES':codes,'SPANISH_DECODED':[],'INSTRUMENTO':{'episode':cfg['current'],'kind':'LOCAL_S50','recipient_mode':ep.get('recipient_mode','legacy_z'),'stage':stage,'tick':a.tick,'advanced_ticks':a.tick-began,'codebook':'OPAQUE_Z','no_content_or_strategy_supplied_during_final_query':True,'status':'ONE_OBSERVED_CODE'if len(codes)==1 else'CONFLICTING_CODES'if len(codes)>1 else'NO_QUALIFIED_CODE'},'INTERPRETACION':'Prepared execution mechanics with acquired route state and new physical content. A local code and its use are not acquired Spanish meanings or general autonomy.'}

def recover_balanced_recipient(a,cfg,layout,*,old_reader=True,max_seconds=120):
    """Prepared direction-balanced resource reader, not passive observation/P2."""
    if type(max_seconds)is not int or not 5<=max_seconds<=240:raise ValueError('Finite explicit advance bound required')
    vectors=layout.get('balanced_vectors')
    if vectors!=[[0,1,-1],[0,1,1]]:raise ValueError('Unvalidated balanced-reader vector schema; no code is invented')
    B=layout['B'];old=e.tick_at_or_after(a.tick,phase=layout['old_phase'],lead=8);target=e.tick_at_or_after(old,phase=layout['phase']);prefix=layout['reader_prefix'];requests=[]
    for key,item in B.items():
        if old_reader:requests.append(_submit(a,prefix+'.OLD.'+key,_move(item['hub'],(0,1,0),-3),(0,1,0),old-3,7))
        for sign in(-1,1):requests.append(_submit(a,prefix+'.BALANCE.'+str(sign)+'.'+key,_move(item['effect'],(sign,0,0),-3),(sign,0,0),target-3,7))
    _advance(a,old,max_seconds);old_reads={key:e.obs(a,item['hub'])for key,item in B.items()};_advance(a,target-1,max_seconds);before={key:{str(v):e.obs(a,_move(item['effect'],v,-1))for v in vectors}for key,item in B.items()};_advance(a,target,max_seconds);after={key:e.obs(a,item['effect'])for key,item in B.items()};codes=[];details={}
    for key,row in after.items():
        details[key]=[]
        for v in vectors:
            prior=before[key][str(v)];increment=row['s_reg']-prior['s_reg'];qualified=e.valid(prior,v)and e.valid(row,v)and increment==14;details[key].append({'incoming_vector':v,'material_increment':increment,'qualified_native_interaction':qualified})
            if qualified:codes.append('Z-'if v[2]<0 else'Z+')
    cfg['recipient_layout']=layout;_save(a,cfg);codes=sorted(set(codes))
    return{'ENTE':{'old':old_reads,'before_incoming':before,'alternative':after},'CONTENT_CODES':codes,'SPANISH_DECODED':[],'INSTRUMENTO':{'method':'balanced_x','codebook':'OPAQUE_Z','old_reader_supplied':old_reader,'old_tick':old,'alternative_tick':target,'no_Z_content_supplied':True,'prepared_reader_not_self_selected':True,'direction_preserved_not_nonintervention':True,'total_material_payload_per_potential_receiver':14,'fixed_material_interaction_details':details,'requests':[{**r,'receipt':exact_receipt(a.world.runtime.receipt(r['id']))}for r in requests],'status':'ONE_OBSERVED_CODE'if len(codes)==1 else'CONFLICTING_CODES'if len(codes)>1 else'NO_QUALIFIED_CODE'},'INTERPRETACION':'Fixed balanced native reader. Direction preservation is measured, not guaranteed. This is not a learned choice of reader or a new Spanish meaning.'}
