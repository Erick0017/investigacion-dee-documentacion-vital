"""APD03 candidate: two generic empty lexical slots, one fixed32gate reader.

Geometry is P0 and installed once before teaching. No signed association,
correct operation or expected answer is written into metadata. Tokens only
select an arbitrary raw cue. Root must review and authorize Native execution.
Importing this file for geometry inspection does not import or advance DEE.
"""
KEY='DEE.Cognitive.System.1.1.APD03.generic_lexicon.R01'
VERSION='APD03.generic_lexicon.R01.common32'
N=67
I=(33,33,33);J=(47,47,47);H=(47,17,47)
LEGACY_I={'alfa':(1,0,0),'beta':(0,1,0),'gamma':(1,1,0),'delta':(-1,1,0),
          'epsilon':(1,-1,0),'zeta':(-1,-1,0),'suma':(-1,0,0),'diferencia':(0,-1,0)}
LEGACY_J={'agrega':(-1,0,0),'resta':(0,-1,0),'total':(1,0,0),'quita':(0,1,0)}
LEGACY_H={'compara':(1,0,0),'recuerda':(0,1,0)}
NEW_FORMS={'luma':(-1,0,0),'nara':(0,-1,0)}
FORM_CODEC={**{f:(I,v)for f,v in LEGACY_I.items()},
            **{f:(J,v)for f,v in LEGACY_J.items()},
            **{f:(H,v)for f,v in LEGACY_H.items()},
            **{f:(H,v)for f,v in NEW_FORMS.items()}}


def pos(origin,v,k,z=0):
    return tuple((origin[i]+k*v[i]+(z if i==2 else 0))%N for i in range(3))


def geometry():
    """Pure integer design inventory, not an observation of current RAW."""
    preparations=[];ports=[];readers=[]
    for form,v in NEW_FORMS.items():
        ports.append({'form':form,'role':'cue','site':list(H),'direction':list(v)})
        for sign in(-1,1):
            for k,z in((2,1),(2,2),(5,3)):
                preparations.append({'form':form,'sign_arm':sign,'site':list(pos(H,v,k,z*sign)),
                    'prepared_state':0,'prepared_semantic':4,'prepared_value':0})
            teacher_direction=(-v[0],-v[1],sign)
            ports.append({'form':form,'role':'teacher','sign_arm':sign,
                'site':list(tuple((pos(H,v,3)[i]-3*teacher_direction[i])%N for i in range(3))),
                'direction':list(teacher_direction)})
            for stage,k,z,di,arrival in(('select',4,1,-1,4),('back',4,2,-1,5),('restore',3,3,1,6)):
                dv=(di*v[0],di*v[1],0);destination=pos(H,v,k,z*sign)
                ports.append({'form':form,'role':stage,'sign_arm':sign,
                    'site':list(tuple((destination[i]-2*dv[i])%N for i in range(3))),
                    'direction':list(dv),'arrival_offset':arrival})
    for form,(origin,v) in FORM_CODEC.items():
        for sign in(-1,1):
            readers.append({'form':form,'sign_arm':sign,'site':list(pos(origin,v,4,sign))})
    new_pre={tuple(r['site']) for r in preparations}
    source_sites={tuple(r['site']) for r in ports}
    legacy_read={tuple(r['site']) for r in readers if r['form'] not in NEW_FORMS}
    duplicate_pre=len(preparations)-len(new_pre)
    return {'version':VERSION,'N':N,'origin':list(H),'new_slots':list(NEW_FORMS),
        'preparation_sites':preparations,'new_ports':ports,'common_reader':readers,
        'new_preparation_duplicate_count':duplicate_pre,
        'new_preparation_overlap_injection_sources':[list(p)for p in sorted(new_pre & source_sites)],
        'new_preparation_overlap_legacy_readers':[list(p) for p in sorted(new_pre & legacy_read)],
        'physical_occupancy_not_checked':True,
        'scope':'Design geometry only. Lack of static overlap does not establish dynamic isolation or vacancy.'}


def preflight(a):
    """Complete sources and readers, including state0/nonzero RAW fields.

    New sources, hubs, output gates and preparation sites require RAW0. The
    shared H cue source is intentionally inherited, as are old read-only
    gates; those observations are recorded but never cleared or rewritten.
    """
    _,_,_,ma,prior,_=_libraries();prior.get(a)
    design=geometry();rows=[]
    for item in design['preparation_sites']:
        rows.append({**item,'role':'prepare_terminator','requires_RAW_zero':True})
    for item in design['new_ports']:
        shared=item['role']=='cue'and tuple(item['site'])==H
        rows.append({**item,'requires_RAW_zero':not shared,
            'intentional_exception':'Inherited shared APD02 cue source H; no clearing or answer-specific port'if shared else None})
    for form,v in NEW_FORMS.items():
        rows.append({'form':form,'role':'new_hub','site':list(pos(H,v,3)),
            'requires_RAW_zero':True})
    for item in design['common_reader']:
        new=item['form']in NEW_FORMS
        rows.append({**item,'role':'new_output_gate'if new else'old_read_only_gate',
            'requires_RAW_zero':new,
            'intentional_exception':None if new else'Existing historical read-only gate, not preparation vacancy'})
    for row in rows:row['observation']=ma.view(a,row['site'])
    conflicts=[row for row in rows if row['requires_RAW_zero']and int(row['observation']['raw'])!=0]
    design_conflict=bool(design['new_preparation_duplicate_count']or
        design['new_preparation_overlap_legacy_readers']or design['new_preparation_overlap_injection_sources'])
    return {'version':VERSION,'tick':int(a.tick),'rows':rows,'geometry':design,
        'required_RAW_zero_conflicts':conflicts,'design_conflict':design_conflict,
        'admissible':not conflicts and not design_conflict,
        'state_zero_not_treated_as_vacant':True,
        'scope':'Current complete RAW at every declared new injection source/hub/gate plus all old32 read sites. Not a guarantee about future arriving material.'}


def _libraries():
    from dee_thinking import _native as d
    from dee_thinking.persistence import encode_metadata,decode_metadata
    from capacidades import mente_acumulativa_r02 as ma
    from capacidades import lexico_apd02_01 as prior
    from app.native_tools import physical
    legacy={k:v for k,v in FORM_CODEC.items() if k not in NEW_FORMS}
    if prior.FORM_CODEC!=legacy:
        raise ValueError('Frozen APD02 legacy codec differs; no silent reader reinterpretation')
    return d,encode_metadata,decode_metadata,ma,prior,physical


def get(a):
    _,_,decode,_,prior,_=_libraries();prior.get(a)
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:raise ValueError('APD03 generic lexical preparation not admitted')
    if int(a.world.runtime.dimension)!=N:raise ValueError('APD03 lexical domain is N67')
    return decode(entries[KEY])


def _save(a,m):
    _,encode,_,_,_,_=_libraries()
    a.world.runtime.set_snapshot_metadata(KEY,encode(m))


def prepare(a):
    d,_,_,ma,prior,physical=_libraries();prior.get(a)
    if KEY in dict(a.world.runtime.snapshot_metadata_entries):
        raise ValueError('Both generic slots already admitted; no resetting lessons')
    screen=preflight(a);design=screen['geometry'];rows=design['preparation_sites']
    if not screen['admissible']:
        raise ValueError('Complete-source preflight rejected; no Runtime writes, clearing or alternate site: '+
            str([row['site']for row in screen['required_RAW_zero_conflicts']]))
    # Existing shared cue H follows the admitted APD02 interface. Only new
    # terminators are installed. Reader/teacher/resource observations remain
    # explicit diagnostics; no site is cleared because state happens to be0.
    for row in rows:
        row['pre']=ma.view(a,row['site'])
        if int(row['pre']['raw'])!=0:
            raise ValueError('Generic lexical preparation refuses nonzero RAW: '+str(row['site']))
    t=int(a.tick)+2;requests=[]
    for j,row in enumerate(rows):
        name='APD03.LEX.R01.prepare.'+str(j)
        if name in set(a.world.runtime.channel_names):raise ValueError('Preparation interface already exists')
        channel=d.ChannelSpec();channel.name=name;channel.injection_site=d.Coordinate(*row['site'])
        channel.direction=d.Direction(0,0,0);channel.state=0;channel.semantic=4
        channel.allow_experience=True;channel.allow_probe=False
        interface=d.InterfaceSpec();interface.name=name;interface.channel=channel
        a.world.declare_interface(interface)
        rid=a.world.submit(name,0,t)
        requests.append({'id':int(rid.id),'channel':name,'site':row['site'],
            'direction':[0,0,0],'state':0,'semantic':4,'value':0,'tick':t})
    a.run_until(t+1);receipts=ma.receipts(a,requests)
    for row in rows:row['post']=ma.view(a,row['site'])
    if any(r['receipt']['status']!='applied' for r in receipts):
        raise ValueError('Preparation incomplete; preserve reached future, no retry/clear')
    metadata={'version':VERSION,'origin':list(H),'forms':{f:list(v)for f,v in NEW_FORMS.items()},
        'prepared_at':t,'teaching_episodes':0,'use_episodes':0,
        'learned_signs_or_expected_operations_stored':False,
        'reader_sites':32,'request_initiative':'operator',
        'scope':'Two finite generic P0 slots, not new algorithms or autonomous structural growth'}
    _save(a,metadata)
    return {'kind':'external_P0_generic_lexical_preparation','rows':rows,
        'complete_preflight':screen,'requests':receipts,
        'physical':physical(a.world),'metadata':metadata,'geometry':design}


def fixed_read(a):
    _,_,_,ma,_,_=_libraries();get(a)
    panel=[];candidates=[]
    for origin,v in FORM_CODEC.values():
        for sign in(-1,1):
            observation=ma.view(a,pos(origin,v,4,sign));panel.append(observation)
            if observation['state']>0 and observation['semantic']==1 and observation['direction']==[0,0,sign]:
                candidates.append({'site':observation['site'],'sign':sign,'s_reg':observation['s_reg']})
    return {'panel':panel,'candidates':candidates,
        'formed_native_command':candidates[0]['sign']if len(candidates)==1 else None,
        'ambiguous':len(candidates)>1,'reader_uses_target_or_token':False,'reader_sites':32}


def teach(a,form,sign,*,mode='paired',revision=False):
    _,_,_,ma,_,physical=_libraries();m=get(a)
    if form not in NEW_FORMS or type(sign)is not int or sign not in(-1,1):
        raise ValueError('An admitted arbitrary cue and an explicit signed physical lesson are required')
    if mode not in('paired','omitted','desync'):raise ValueError('Frozen teacher modes required')
    origin,v=FORM_CODEC[form];t=ma.phase(a.tick);tt=t+(11 if mode=='desync' else 0)
    requests=[];before=physical(a.world)
    ma.submit(a,'APD03.LEX.R01.cue.'+form,origin,v,5,t,requests)
    if mode!='omitted':
        hub=pos(origin,v,3);dv=(-v[0],-v[1],sign)
        ma.submit(a,'APD03.LEX.R01.teacher.'+form+'.'+str(sign),ma.add(hub,dv,-3),dv,11,tt,requests)
        if revision:
            zz=(0,0,sign)
            ma.submit(a,'APD03.LEX.R01.revision.'+form+'.'+str(sign),ma.add(hub,zz,-3),zz,11,tt,requests)
    a.run_until(tt+3);m['teaching_episodes']+=1;_save(a,m)
    return {'kind':'explicit_generic_revision'if revision else'explicit_generic_lesson',
        'form':form,'teacher_sign':sign,'teacher_mode':mode,'input_tick':t,
        'teacher_tick':None if mode=='omitted'else tt,'end_tick':a.tick,
        'before':before,'after':physical(a.world),'hub':ma.view(a,pos(origin,v,3)),
        'requests':ma.receipts(a,requests),'lesson_is_external':True}


def query(a,form,*,detailed=False):
    _,_,_,ma,_,physical=_libraries();m=get(a)
    if form not in FORM_CODEC:raise ValueError('No parser for unadmitted words')
    origin,v=FORM_CODEC[form];t=ma.phase(a.tick);requests=[];before=physical(a.world)
    ma.submit(a,'APD03.LEX.R01.cue.'+form,origin,v,5,t,requests)
    for sign in(-1,1):
        for stage,k,z,di,arrival in(('select',4,1,-1,4),('back',4,2,-1,5),('restore',3,3,1,6)):
            dv=(di*v[0],di*v[1],0);destination=pos(origin,v,k,z*sign)
            ma.submit(a,'APD03.LEX.R01.generic.'+form+'.'+stage+'.'+str(sign),
                ma.add(destination,dv,-2),dv,7,t+arrival-2,requests)
    frames=[];answer=None
    for tick in range(t,t+8):
        a.run_until(tick)
        if detailed:
            frames.append({'tick':tick,'gates':[ma.view(a,pos(o,w,4,sign))
                for o,w in FORM_CODEC.values()for sign in(-1,1)]})
        if tick==t+4:answer=fixed_read(a)
    m['use_episodes']+=1;_save(a,m)
    return {'kind':'APD03_common_lexical_query','form':form,'input_tick':t,
        'read_tick':t+4,'end_tick':a.tick,'before':before,'after':physical(a.world),
        'reader':answer,'requests':ma.receipts(a,requests),'frames':frames,
        'teacher_or_expected_operation_supplied':False}


def use_relation(a,form,datum,context,*,detailed=False):
    _,_,_,ma,_,_=_libraries()
    from capacidades import mente_unificada_01 as mu
    if form not in NEW_FORMS or type(datum)is not int or not 0<=datum<=512 or context not in ma.codec(a):
        raise ValueError('Generic cue, raw datum0..512 and explicit existing context required')
    word=query(a,form,detailed=detailed);sign=word['reader']['formed_native_command'];interaction=None
    if sign==1:interaction=mu.current(a,datum,detail=detailed)
    elif sign==-1:interaction=ma.query(a,context,detail=detailed)
    return {'kind':'APD03_generic_acquired_request','literal_form':form,'public_datum':datum,
        'operator_supplied_context':context,'word':word,'native_function_choice':sign,
        'interaction':interaction,
        'scope':'Acquired cue sign chooses one of two prepared native interactions. Context addressing and opportunity are operator-provided; no autonomous plan or new Spanish meaning is claimed.'}
