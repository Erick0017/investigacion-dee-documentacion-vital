"""Third lexical curriculum: two extra forms, one fixed24gate reader.

External anatomy enables two additional associations to existing sign classes.
No Runtime is constructed on import; no signs, targets or word meanings are
stored in operational metadata. This module does not mutate the R02 codec.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from capacidades import mente_acumulativa_r02 as ma
from app.native_tools import physical

KEY='DEE.Cognitive.System.1.1.APD01.lexical_forms.R04'
R02_KEY='DEE.Cognitive.System.1.1.APD01.lexical_forms.R02'
REVISION='APD01.lexical_forms.R04.third_curriculum_common24'
I=(33,33,33);J=(47,47,47);N=67
OLD_I={'alfa':(1,0,0),'beta':(0,1,0),'gamma':(1,1,0),'delta':(-1,1,0),
       'epsilon':(1,-1,0),'zeta':(-1,-1,0),'suma':(-1,0,0),'diferencia':(0,-1,0)}
OLD_J={'agrega':(-1,0,0),'resta':(0,-1,0)}
NEW_FORMS={'total':(1,0,0),'quita':(0,1,0)}
FORM_CODEC={**{f:(I,v)for f,v in OLD_I.items()},
            **{f:(J,v)for f,v in OLD_J.items()},**{f:(J,v)for f,v in NEW_FORMS.items()}}

def pos(origin,v,k,z=0):
    return tuple((origin[j]+k*v[j]+(z if j==2 else 0))%N for j in range(3))

def _prior(a):
    m=ma.get(a);e=dict(a.world.runtime.snapshot_metadata_entries)
    if any(f not in m.get('enabled_contexts',[])for f in('alfa','beta','gamma','delta','epsilon','zeta')):
        raise ValueError('Requires the existing six admitted physical contexts')
    if R02_KEY not in e:raise ValueError('Second lexical curriculum must already be prepared in this life')
    r=decode_metadata(e[R02_KEY])
    if r.get('second_origin')!=list(J)or r.get('forms')!={f:list(v)for f,v in OLD_J.items()}:
        raise ValueError('Existing second-hub codec differs; no silent reinterpretation')
    return m

def get(a):
    _prior(a);e=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in e:raise ValueError('Explicit third-curriculum preparation required')
    return decode_metadata(e[KEY])

def _save(a,m):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))

def preparation_sites():
    return [{'form':f,'site':list(pos(J,v,k,z*sg))}for f,v in NEW_FORMS.items()
            for sg in(-1,1)for k,z in((2,1),(2,2),(5,3))]

def prepare(a):
    _prior(a)
    if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('No duplicate preparation')
    rows=preparation_sites()
    for row in rows:
        row['pre']=ma.view(a,row['site'])
        if int(row['pre']['raw'])!=0:raise ValueError('Will not overwrite any nonzero RAW: '+str(row['site']))
    t=int(a.tick)+2;req=[]
    for j,row in enumerate(rows):
        name='APD01.LEX.R04.prepare.'+str(j)
        if name in set(a.world.runtime.channel_names):raise ValueError('Existing preparation interface')
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*row['site'])
        c.direction=d.Direction(0,0,0);c.state=0;c.semantic=4;c.allow_experience=True;c.allow_probe=False
        it=d.InterfaceSpec();it.name=name;it.channel=c;a.world.declare_interface(it)
        rid=a.world.submit(name,0,t);req.append({'id':int(rid.id),'channel':name,'site':row['site'],
            'direction':[0,0,0],'value':0,'state':0,'semantic':4,'tick':t})
    a.run_until(t+1);receipts=ma.receipts(a,req)
    for row in rows:row['post']=ma.view(a,row['site'])
    if any(r['receipt']['status']!='applied'for r in receipts):
        raise ValueError('Incomplete preparation; preserve reached future without retry or clearing')
    m={'revision':REVISION,'origin':list(J),'forms':{f:list(v)for f,v in NEW_FORMS.items()},
       'prepared_at':t,'request_count':len(req),'teaching_episodes':0,'use_episodes':0,
       'learned_signs_or_expected_operations_stored':False,'same_runtime_as_previous_hubs':True,
       'reader':'One fixed24gate decoder for all twelve context forms'}
    _save(a,m)
    return {'kind':'external_P0_third_curriculum','rows':rows,'requests':receipts,
            'physical':physical(a.world,occupation=True),'metadata':m,
            'not_claimed':'Autonomous growth, two new operations, twelve procedures, syntax or NSM meanings'}

def fixed_read(a):
    panel=[];candidates=[]
    for origin,v in FORM_CODEC.values():
        for sg in(-1,1):
            o=ma.view(a,pos(origin,v,4,sg));panel.append(o)
            if o['state']>0 and o['semantic']==1 and o['direction']==[0,0,sg]:
                candidates.append({'site':o['site'],'sign':sg,'s_reg':o['s_reg']})
    return {'panel':panel,'candidates':candidates,'formed_native_command':candidates[0]['sign']if len(candidates)==1 else None,
            'ambiguous':len(candidates)>1,'reader_uses_target_or_token':False,'reader_sites':24}

def teach(a,form,sign,*,teacher_mode='paired'):
    m=get(a)
    if form not in NEW_FORMS:raise ValueError('R04 teaching only adds its two new forms')
    if type(sign)is not int or sign not in(-1,1):raise ValueError('Signed explicit lesson required')
    if teacher_mode not in('paired','omitted'):raise ValueError('Only frozen paired/omitted controls admitted')
    origin,v=FORM_CODEC[form];t=ma.phase(a.tick);req=[];before=physical(a.world)
    ma.submit(a,'APD01.LEX.R04.cue.'+form,origin,v,5,t,req)
    if teacher_mode!='omitted':
        hub=pos(origin,v,3);dv=(-v[0],-v[1],sign)
        ma.submit(a,'APD01.LEX.R04.teacher.'+form+'.'+str(sign),ma.add(hub,dv,-3),dv,11,t,req)
    a.run_until(t+3);m['teaching_episodes']+=1;m['request_count']+=len(req);_save(a,m)
    return {'kind':'explicit_teaching','form':form,'teacher_sign':sign,'teacher_mode':teacher_mode,
            'input_tick':t,'teacher_tick':t if teacher_mode!='omitted'else None,'end_tick':a.tick,
            'before':before,'after':physical(a.world),'hub':ma.view(a,pos(origin,v,3)),
            'requests':ma.receipts(a,req),'scope':'Two extra acquired signal associations to existing sign classes'}

def query(a,form,*,detailed=False):
    m=get(a)
    if form not in FORM_CODEC:raise ValueError('Unknown raw form; no free-language parser')
    origin,v=FORM_CODEC[form];t=ma.phase(a.tick);req=[];before=physical(a.world)
    ma.submit(a,'APD01.LEX.R04.cue.'+form,origin,v,5,t,req)
    for sg in(-1,1):
        for stage,k,z,di,arrival in(('select',4,1,-1,4),('back',4,2,-1,5),('restore',3,3,1,6)):
            dv=(di*v[0],di*v[1],0);destination=pos(origin,v,k,z*sg)
            ma.submit(a,'APD01.LEX.R04.generic.'+form+'.'+stage+'.'+str(sg),ma.add(destination,dv,-2),dv,7,t+arrival-2,req)
    frames=[];answer=None
    for q in range(t,t+8):
        a.run_until(q)
        if detailed:
            sites={pos(o,vv,k,z)for o,vv in FORM_CODEC.values()for k in(2,3,4,5)for z in range(-4,5)}
            frames.append({'tick':q,'sites':[ma.view(a,p)for p in sorted(sites)]})
        if q==t+4:answer=fixed_read(a)
    m['use_episodes']+=1;m['request_count']+=len(req);_save(a,m)
    return {'kind':'lexical_query','form':form,'input_tick':t,'read_tick':t+4,'end_tick':a.tick,
            'before':before,'after':physical(a.world),'reader':answer,'requests':ma.receipts(a,req),'frames':frames,
            'teacher_or_expected_operation_supplied':False,
            'scope':'One fixed24gate reader for all twelve old/new forms; not a learned arithmetic algorithm'}

def sequence(a,forms,*,detailed=False):
    if not isinstance(forms,list)or not 1<=len(forms)<=16 or any(f not in FORM_CODEC for f in forms):
        raise ValueError('Finite known-form sequence required')
    return {'rows':[query(a,f,detailed=detailed)for f in forms],
            'scope':'Successive material uses; not a claim of compositional grammar'}
