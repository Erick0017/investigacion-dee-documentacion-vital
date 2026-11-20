"""Experimental arbitrary Spanish marker binding to native relation encounters.

The decoder reads acquired X sign, never the bank's semantic name or target.
Y/Z must come from physical experience, not the teacher or the +Y reader.
Phase spacing is an explicit protocol resource, not autonomous attention.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from capacidades import espanol_funcional_01 as e,ensenanza_relacional_02 as base

def prepare(a,*,frame,mode='relative_path',origin=(38,50,8)):
    entry=base.prepare(a,frame=frame,mode=mode,origin=origin);g=e.prepare(a);entry=g['relational_words_v2'][frame]
    if 'lexical_v3'in entry:return entry
    for b in entry['banks']:
        for sign in(-1,1):
            name='EF01.LX3.'+frame+'.'+b['id']+'.'+str(sign);v=(sign,1,0)
            ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*e.move(b['hub'],v,-3));ch.direction=d.Direction(*v);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True
            p=d.InterfaceSpec();p.name=name;p.channel=ch;a.world.declare_interface(p);b['lexical_cue_'+str(sign)]=name
    entry['lexical_v3']={'schema':'DCS1.1.EF01.arbitrary_word_marker.r3','learned_phases':[],'after_comprehension':False,
        'codebook':{'1':'cerca'if mode=='relative_path'else'antes','-1':'lejos'if mode=='relative_path'else'después'},
        'decoder':'Native state1SEM1, Y=Z=1, abs(X)=1; X sign selects the fixed Spanish token, never bank ID or a teaching log.',
        'scope':'Relative path to prepared B pattern or two event-shape orders. Phase/frame/cue code are prepared, association content must be acquired.'}
    a.world.runtime.set_snapshot_metadata(e.KEY,encode_metadata(g));return entry

def teach(a,*,frame,parameter=3,word='cerca',phase_shift=0,signal=True,event_a=True,event_b=True,offroute=False,load=3):
    g=e.prepare(a)
    if frame not in g.get('relational_words_v2',{})or'lexical_v3'not in g['relational_words_v2'][frame]:raise ValueError('Prepare a lexical physical frame first')
    entry=g['relational_words_v2'][frame];lex=entry['lexical_v3'];code=lex['codebook'];reverse={v:int(k)for k,v in code.items()}
    if word not in reverse or parameter not in(-5,-3,-1,1,3,5)or phase_shift not in(0,4)or load not in(3,5):raise ValueError('Finite declared lexical teaching domain')
    if lex['after_comprehension']:raise ValueError('Consumptive word-use state cannot be silently reconstructed')
    start=e.tick_at_or_after(a.tick,phase=phase_shift,lead=5);target=start+13;req=[];sign=reverse[word]
    def send(name,payload,t):
        r=a.world.submit(name,payload,t);req.append({'port':name,'payload':payload,'tick':t,'id':int(r.id)})
    if entry['mode']=='relative_path':at=bt=start;ap=entry['ports']['A_positions'][str(parameter)]
    else:at=start+max(0,-parameter);bt=start+max(0,parameter);ap=entry['ports']['A']
    if event_a:send(ap,load,at)
    if event_b:
        for row in entry['ports']['B']:send(row['off'if offroute else'on'],load,bt)
    if signal:
        for b in entry['banks']:send(b['lexical_cue_'+str(sign)],5,start+10)
    a.run_until(target-1);pre={b['id']:e.obs(a,b['hub'])for b in entry['banks']};a.run_until(target);post={b['id']:e.obs(a,b['hub'])for b in entry['banks']}
    if target%67 not in lex['learned_phases']:lex['learned_phases'].append(target%67)
    entry['experiences'].append({'start':start,'A_tick':at,'B_tick':bt,'A_port':ap,'teacher_token':word,'signal':signal,'phase':target%67})
    a.world.runtime.set_snapshot_metadata(e.KEY,encode_metadata(g))
    return {'ENTORNO':{'actual_A_port':ap,'A_tick':at,'B_tick':bt,'load_each':load,'B_carriers':6},'ENTE':{'pre_signal':pre,'post_signal':post},
        'INSTRUMENTO':{'teacher_token':word,'teacher_marker_X':sign,'phase_shift':phase_shift,'all_six_banks_receive_same_word':signal,'requests':[e.receipt_at(a.world,r)for r in req]},
        'INTERPRETACION':'Teacher token is supplied only in acquisition. Native event location/content and the later arbitrary marker must meet; decoder does not infer a word from event parameter.'}

def decode(records,entry):
    found=[]
    for key,row in records.items():
        if row['active']and row['state']==1 and row['semantic']==1 and row['direction'][1:]==[1,1]and row['direction'][0]in(-1,1):
            found.append({'text':entry['lexical_v3']['codebook'][str(row['direction'][0])],'bank':key,'native_X':row['direction'][0]})
    return found

def query(a,*,frame,phase=None,payload=7):
    g=e.prepare(a);entry=g.get('relational_words_v2',{}).get(frame)
    if entry is None or'lexical_v3'not in entry or entry['lexical_v3']['after_comprehension']:raise ValueError('Admitted lived lexical frame required')
    phases=entry['lexical_v3']['learned_phases'];selected=phases if phase is None else[phase]
    if any(t not in phases for t in selected)or type(payload)is not int or not 0<=payload<=65535:raise ValueError('Explicit acquired protocol phase and exact query resource required')
    rows=[]
    for p in selected:
        target=e.tick_at_or_after(a.tick,phase=p,lead=3);req=[]
        for b in entry['banks']:
            r=a.world.probe(b['query'],payload,target-3);req.append({'port':b['query'],'payload':payload,'tick':target-3,'id':int(r.id)})
        a.run_until(target);records={b['id']:e.obs(a,b['hub'])for b in entry['banks']}
        rows.append({'phase':p,'tick':a.tick,'records':records,'SPANISH_DECODED':decode(records,entry),'requests':[e.receipt_at(a.world,r)for r in req]})
    return {'ENTE':rows,'SPANISH_DECODED':[r for row in rows for r in row['SPANISH_DECODED']],
        'INSTRUMENTO':{'all_protocol_phases_equal_opportunities':phase is None,'phases':selected,'material_queries':True},
        'INTERPRETACION':'Historical learned-form recall, not a statement that every recalled word is true in one current situation.'}

def context(a,*,frame,parameter=3,load=3,phase=None):
    g=e.prepare(a);entry=g.get('relational_words_v2',{}).get(frame)
    if entry is None or'lexical_v3'not in entry or entry['lexical_v3']['after_comprehension']:raise ValueError('Lived pre-use lexical frame required')
    phases=entry['lexical_v3']['learned_phases'];selected=phases if phase is None else[phase]
    if parameter not in(-5,-3,-1,1,3,5)or load not in(3,5)or any(p not in phases for p in selected):raise ValueError('Current physical position/time and protocol phase domain')
    rows=[]
    for p in selected:
        baseline=e.tick_at_or_after(a.tick,phase=p)
        if baseline>a.tick:a.run_until(baseline)
        before={b['id']:e.obs(a,b['hub'])for b in entry['banks']};target=baseline+67;start=target-13;req=[]
        def send(name,payload,t,probe=False):
            r=(a.world.probe if probe else a.world.submit)(name,payload,t);req.append({'port':name,'payload':payload,'tick':t,'id':int(r.id)})
        if entry['mode']=='relative_path':at=bt=start;ap=entry['ports']['A_positions'][str(parameter)]
        else:at=start+max(0,-parameter);bt=start+max(0,parameter);ap=entry['ports']['A']
        send(ap,load,at)
        for b in entry['ports']['B']:send(b['on'],load,bt)
        for b in entry['banks']:send(b['query'],7,target-3,True)
        a.run_until(target);after={b['id']:e.obs(a,b['hub'])for b in entry['banks']};qualified=[];increments={}
        for b in entry['banks']:
            key=b['id'];delta=after[key]['s_reg']-before[key]['s_reg']-7;increments[key]=delta
            if delta in(6,10)and decode({key:before[key]},entry)and decode({key:after[key]},entry):qualified.extend(decode({key:after[key]},entry))
        rows.append({'phase':p,'baseline_tick':baseline,'tick':a.tick,'before':before,'after':after,'native_increments_after_query_dose':increments,'SPANISH_DECODED':qualified,'requests':[e.receipt_at(a.world,r)for r in req]})
    return {'ENTORNO':{'actual_parameter':parameter,'load_each':load,'teacher_token_supplied':False,'repeated_actual_experiences':len(selected)},'ENTE':rows,'SPANISH_DECODED':[r for row in rows for r in row['SPANISH_DECODED']],
        'INSTRUMENTO':{'decoder':'Acquired X marker plus current increment6/10 after subtracting fixed query-dose7. No sign/position/time comparison used by decoder.'},
        'INTERPRETACION':'Current context production in a finite trained frame. When all acquired phases are used the physical scene is presented once per phase; that cost is not hidden or endogenous.'}

def comprehend(a,*,frame,word,phase=None):
    g=e.prepare(a);entry=g.get('relational_words_v2',{}).get(frame)
    if entry is None or'lexical_v3'not in entry or entry['lexical_v3']['after_comprehension']:raise ValueError('Lived pre-use lexical frame required')
    lex=entry['lexical_v3'];reverse={v:int(k)for k,v in lex['codebook'].items()}
    if word not in reverse:raise ValueError('Unknown token; no free-language completion')
    phases=lex['learned_phases'];selected=phases if phase is None else[phase]
    if any(p not in phases for p in selected):raise ValueError('Unknown acquired phase')
    direction=(-reverse[word],1,0);results=[]
    def port(role,site,v):
        name='EF01.LX3.USE.'+frame+'.'+role
        if name in a.world.runtime.channel_names:return name
        ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*e.move(site,v,-3));ch.direction=d.Direction(*v);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=name;p.channel=ch;a.world.declare_interface(p);return name
    for p in selected:
        target=e.tick_at_or_after(a.tick,phase=p,lead=3);req=[];effects={}
        for b in entry['banks']:
            name=port(b['id']+'.token'+str(reverse[word]),b['hub'],direction);r=a.world.probe(name,7,target-3);req.append({'port':name,'payload':7,'tick':target-3,'id':int(r.id)})
            effect=e.move(b['hub'],(0,1,1),6);effects[b['id']]=effect;name=port(b['id']+'.act',effect,(0,-1,0));r=a.world.submit(name,11,target+3);req.append({'port':name,'payload':11,'tick':target+3,'id':int(r.id)})
        a.run_until(target);read={b['id']:e.obs(a,b['hub'])for b in entry['banks']};a.run_until(target+6);output={key:e.obs(a,site)for key,site in effects.items()}
        results.append({'phase':p,'tick':a.tick,'read':read,'effects':output,'action_banks':[key for key,row in output.items()if e.valid(row,(0,0,1))],'requests':[e.receipt_at(a.world,r)for r in req]})
    lex['after_comprehension']=True;a.world.runtime.set_snapshot_metadata(e.KEY,encode_metadata(g))
    return {'ENTE':results,'INSTRUMENTO':{'recognized_token':word,'fixed_token_probe':list(direction),'all_banks_and_selected_phases_supplied_equally':True,'consumptive':True},
        'INTERPRETACION':'Token recognition supplies a fixed physical cue; acquired X determines which native relation can reach the common action opportunity. Consumes/transforms the old marker; no subsequent old-reader continuity claimed.'}
