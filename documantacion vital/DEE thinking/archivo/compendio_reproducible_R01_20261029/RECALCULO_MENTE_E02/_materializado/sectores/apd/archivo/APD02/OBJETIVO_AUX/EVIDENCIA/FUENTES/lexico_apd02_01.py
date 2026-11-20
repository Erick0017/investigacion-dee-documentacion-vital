"""Two additional learned requests; prepared common access, not Spanish parsing.

The new cues can select current native comparison or an explicitly supplied
historical context. Context addressing remains operator assistance. All old
and new gates are read together; no expected sign enters the reader.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata
from capacidades import mente_acumulativa_r02 as ma
from capacidades import lexico_apd_extendido_04 as old
from app.native_tools import physical

KEY='DEE.Cognitive.System.1.1.APD02.lexical_requests.R01'
VERSION='APD02.lexical_requests.R01.common28'
N=67;H=(47,17,47)
NEW_FORMS={'compara':(1,0,0),'recuerda':(0,1,0)}
FORM_CODEC={**old.FORM_CODEC,**{f:(H,v)for f,v in NEW_FORMS.items()}}

def get(a):
    old.get(a);e=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in e:raise ValueError('Explicit APD02 language anatomy not admitted')
    return decode_metadata(e[KEY])
def save(a,m):a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))
def pos(origin,v,k,z=0):return tuple((origin[i]+k*v[i]+(z if i==2 else 0))%N for i in range(3))

def prepare(a):
    old.get(a)
    if KEY in dict(a.world.runtime.snapshot_metadata_entries):raise ValueError('Already admitted; no resetting lessons')
    rows=[{'form':f,'site':list(pos(H,v,k,z*sg))}for f,v in NEW_FORMS.items()for sg in(-1,1)for k,z in((2,1),(2,2),(5,3))]
    for r in rows:
        r['pre']=ma.view(a,r['site'])
        if int(r['pre']['raw'])!=0:raise ValueError('Nonzero RAW is not free: '+str(r['site']))
    at=int(a.tick)+2;requests=[]
    for j,r in enumerate(rows):
        name='APD02.LEX.R01.prepare.'+str(j)
        if name in set(a.world.runtime.channel_names):raise ValueError('Preparation interface exists')
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*r['site']);c.direction=d.Direction(0,0,0);c.state=0;c.semantic=4;c.allow_experience=True;c.allow_probe=False
        it=d.InterfaceSpec();it.name=name;it.channel=c;a.world.declare_interface(it)
        rid=a.world.submit(name,0,at);requests.append({'id':int(rid.id),'channel':name,'site':r['site'],'direction':[0,0,0],'state':0,'semantic':4,'value':0,'tick':at})
    a.run_until(at+1);receipts=ma.receipts(a,requests)
    for r in rows:r['post']=ma.view(a,r['site'])
    if any(r['receipt']['status']!='applied'for r in receipts):raise ValueError('Incomplete preparation preserved; no overwrite/retry')
    m={'version':VERSION,'prepared_at':at,'origin':list(H),'forms':{f:list(v)for f,v in NEW_FORMS.items()},'teaching_episodes':0,'use_episodes':0,'sign_or_meaning_in_metadata':False,'request_initiative':'operator','scope':'Prepared physical opportunities only; two signs select two prepared functional interactions after teaching.'}
    save(a,m);return{'kind':'external_P0_lexical_extension','rows':rows,'requests':receipts,'physical':physical(a.world),'metadata':m}

def fixed_read(a):
    panel=[];candidates=[]
    for origin,v in FORM_CODEC.values():
        for sg in(-1,1):
            o=ma.view(a,pos(origin,v,4,sg));panel.append(o)
            if o['state']>0 and o['semantic']==1 and o['direction']==[0,0,sg]:candidates.append({'site':o['site'],'sign':sg,'s_reg':o['s_reg']})
    return{'panel':panel,'candidates':candidates,'formed_native_command':candidates[0]['sign']if len(candidates)==1 else None,'ambiguous':len(candidates)>1,'reader_uses_target_or_token':False,'reader_sites':28}

def query(a,form,*,detailed=False):
    m=get(a)
    if form not in FORM_CODEC:raise ValueError('Unknown literal physical cue')
    origin,v=FORM_CODEC[form];t=ma.phase(a.tick);req=[];before=physical(a.world)
    ma.submit(a,'APD02.LEX.R01.cue.'+form,origin,v,5,t,req)
    for sg in(-1,1):
        for stage,k,z,di,arrival in(('select',4,1,-1,4),('back',4,2,-1,5),('restore',3,3,1,6)):
            dv=(di*v[0],di*v[1],0);dest=pos(origin,v,k,z*sg)
            ma.submit(a,'APD02.LEX.R01.generic.'+form+'.'+stage+'.'+str(sg),ma.add(dest,dv,-2),dv,7,t+arrival-2,req)
    frames=[];answer=None
    for q in range(t,t+8):
        a.run_until(q)
        if detailed:frames.append({'tick':q,'gates':[ma.view(a,pos(o,w,4,sg))for o,w in FORM_CODEC.values()for sg in(-1,1)]})
        if q==t+4:answer=fixed_read(a)
    m['use_episodes']+=1;save(a,m)
    return{'kind':'APD02_common_lexical_query','form':form,'input_tick':t,'read_tick':t+4,'end_tick':a.tick,'before':before,'after':physical(a.world),'reader':answer,'requests':ma.receipts(a,req),'frames':frames,'teacher_or_expected_operation_supplied':False}

def teach(a,form,sign,*,revision=False,mode='paired'):
    m=get(a)
    if form not in NEW_FORMS or type(sign)is not int or sign not in(-1,1):raise ValueError('Explicit signed lesson for a new APD02 form required')
    if mode not in('paired','omitted','desync'):raise ValueError('Frozen lesson modalities')
    origin,v=FORM_CODEC[form];t=ma.phase(a.tick);tt=t+(11 if mode=='desync'else 0);req=[];before=physical(a.world)
    ma.submit(a,'APD02.LEX.R01.cue.'+form,origin,v,5,t,req)
    if mode!='omitted':
        h=pos(origin,v,3);dv=(-v[0],-v[1],sign)
        ma.submit(a,'APD02.LEX.R01.teacher.'+form+'.'+str(sign),ma.add(h,dv,-3),dv,11,tt,req)
        if revision:
            zz=(0,0,sign);ma.submit(a,'APD02.LEX.R01.revision.'+form+'.'+str(sign),ma.add(h,zz,-3),zz,11,tt,req)
    a.run_until(tt+3);m['teaching_episodes']+=1;save(a,m)
    return{'kind':'explicit_APD02_revision'if revision else'explicit_APD02_lesson','form':form,'teacher_sign':sign,'teacher_mode':mode,'before':before,'after':physical(a.world),'input_tick':t,'teacher_tick':None if mode=='omitted'else tt,'hub':ma.view(a,pos(origin,v,3)),'requests':ma.receipts(a,req),'lesson_is_external':True}

def use_relation(a,form,datum,context,*,detailed=False):
    from capacidades import mente_unificada_01 as mu
    if form not in NEW_FORMS or type(datum)is not int or not 0<=datum<=512 or context not in ma.codec(a):raise ValueError('Literal admitted cue, datum0..512 and explicit existing context required')
    word=query(a,form,detailed=detailed);sign=word['reader']['formed_native_command'];r=None
    if sign==1:r=mu.current(a,datum,detail=detailed)
    elif sign==-1:r=ma.query(a,context,detail=detailed)
    return{'kind':'APD02_acquired_function_request','literal_form':form,'public_datum':datum,'operator_supplied_context':context,'word':word,'native_function_choice':sign,'interaction':r,'scope':'Physical acquired sign selects current native scalar comparison or historical native context access. The two interactions and context addressing are prepared; no learned parser, free Spanish, temporal concept or autonomous bank choice is claimed.'}
