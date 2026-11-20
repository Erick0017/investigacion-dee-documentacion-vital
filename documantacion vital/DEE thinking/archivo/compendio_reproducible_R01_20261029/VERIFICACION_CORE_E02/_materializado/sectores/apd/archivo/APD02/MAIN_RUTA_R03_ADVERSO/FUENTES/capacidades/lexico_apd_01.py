"""APD01 candidate: two new opaque cues in the lived MA02/R3 N67 world.

No Runtime is created here. All evolution goes through the supplied owner.
The codec encodes a form, never its desired operation. Only native emissions
can subsequently be transduced into an action. Teaching signs are not stored
in metadata or consulted by the fixed reader. Not validated merely by import.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata, decode_metadata
from capacidades import mente_acumulativa_r02 as ma
from app.native_tools import physical

KEY = 'DEE.Cognitive.System.1.1.APD01.lexical_forms.R01'
REVISION = 'APD01.lexical_forms.R01'
N = 67
I = (33, 33, 33)
# Fixed arbitrary input-form encoding; there is deliberately no word->action map.
FORMS = {'suma': (-1, 0, 0), 'diferencia': (0, -1, 0)}
ALL_DIRECTIONS = ((1,0,0),(0,1,0),(1,1,0),(-1,1,0),
                  (1,-1,0),(-1,-1,0),(-1,0,0),(0,-1,0))


def get(a):
    ma.get(a)
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:
        raise ValueError('Explicit lexical anatomical preparation is required')
    return decode_metadata(entries[KEY])


def preparation_sites():
    return [{'form': form, 'site': list(ma.pos(v,k,z*sg))}
            for form,v in FORMS.items() for sg in (-1,1)
            for k,z in ((2,1),(2,2),(5,3))]


def prepare(a):
    """P0-only extension via12 legal inert SEM4 inputs; no learned content copy."""
    ma.get(a)
    if KEY in dict(a.world.runtime.snapshot_metadata_entries):
        raise ValueError('Already prepared; refuse silent reinstallation')
    rows = preparation_sites()
    # Check every site before declaring or enqueueing anything.
    for row in rows:
        row['pre'] = ma.view(a, row['site'])
        if int(row['pre']['raw']) != 0:
            raise ValueError('Nonzero RAW cannot be overwritten, including inactive: '
                             + str(row['site']))
    at = int(a.tick)+2
    requests = []
    for j,row in enumerate(rows):
        name = 'APD01.LEX.R01.preparation.'+str(j)
        if name in set(a.world.runtime.channel_names):
            raise ValueError('Preparation channel already exists')
        c=d.ChannelSpec(); c.name=name; c.injection_site=d.Coordinate(*row['site'])
        c.direction=d.Direction(0,0,0); c.state=0; c.semantic=4
        c.allow_experience=True; c.allow_probe=False
        it=d.InterfaceSpec(); it.name=name; it.channel=c
        a.world.declare_interface(it)
        r=a.world.submit(name,0,at)
        requests.append({'id':int(r.id),'channel':name,'site':row['site'],
                         'direction':[0,0,0],'value':0,'state':0,'semantic':4,'tick':at})
    a.run_until(at+1)
    rs=ma.receipts(a,requests)
    for row in rows:
        row['post']=ma.view(a,row['site'])
    if any(row['receipt']['status']!='applied' for row in rs):
        raise ValueError('Incomplete preparation: preserve actual reached state; no retry/clear')
    meta={'revision':REVISION,'forms':{k:list(v) for k,v in FORMS.items()},
          'prepared_at':at,'request_count':len(requests),'teaching_episodes':0,
          'use_episodes':0,'meaning_or_expected_action_stored':False,
          'assistance':'Prepared cue addressing, common generic resources and phase; operator initiates use.'}
    a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(meta))
    return {'kind':'external_P0_anatomical_extension','rows':rows,'requests':rs,
            'physical':physical(a.world,occupation=True),'metadata':meta}


def _save(a,m):
    a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))


def _form(form):
    if form not in FORMS:
        raise ValueError('Only the two frozen physical input forms; no text-to-tool inference')
    return FORMS[form]


def fixed_read(a):
    """All16 gates, not the bank named by the current input form or its target."""
    panel=[]; candidates=[]
    for v in ALL_DIRECTIONS:
        for sg in (-1,1):
            o=ma.view(a,ma.pos(v,4,sg)); panel.append(o)
            if o['state']>0 and o['semantic']==1 and o['direction']==[0,0,sg]:
                candidates.append({'site':o['site'],'sign':sg,'s_reg':o['s_reg']})
    return {'panel':panel,'candidates':candidates,
            'formed_native_command':candidates[0]['sign'] if len(candidates)==1 else None,
            'ambiguous':len(candidates)>1,'reader_uses_target_or_token':False}


def teach(a,form,sign,*,teacher_mode='paired',revision=False):
    """Explicit lessons, or dose-preserving +11tick unpaired / omitted controls.

    The desired sign is a training input only. Evaluation query has no sign.
    A delayed teacher can still affect the world and must not be called a sham.
    """
    m=get(a); v=_form(form)
    if type(sign) is not int or sign not in (-1,1):
        raise ValueError('Explicit signed teacher experience required')
    if teacher_mode not in ('paired','unpaired','omitted'):
        raise ValueError('Frozen declared teaching/control modes')
    t=ma.phase(a.tick); req=[]; pre=physical(a.world)
    ma.submit(a,'APD01.LEX.R01.cue.'+form,I,v,5,t,req)
    tt=t+(11 if teacher_mode=='unpaired' else 0)
    if teacher_mode!='omitted':
        h=ma.pos(v,3); dv=(-v[0],-v[1],sign)
        ma.submit(a,'APD01.LEX.R01.teacher.'+form+'.'+str(sign),
                  ma.add(h,dv,-3),dv,11,tt,req)
        if revision:
            zz=(0,0,sign)
            ma.submit(a,'APD01.LEX.R01.second.'+form+'.'+str(sign),
                      ma.add(h,zz,-3),zz,11,tt,req)
    a.run_until(tt+3)
    m['teaching_episodes']+=1; m['request_count']+=len(req); _save(a,m)
    return {'kind':'explicit_teaching' if not revision else 'explicit_revision',
            'form':form,'teacher_sign':sign,'teacher_mode':teacher_mode,
            'input_tick':t,'teacher_tick':tt if teacher_mode!='omitted' else None,
            'before':pre,'after':physical(a.world),'hub':ma.view(a,ma.pos(v,3)),
            'requests':ma.receipts(a,req),'end_tick':a.tick,
            'scope':'Externally supplied lesson; no acquired action or policy claimed from preparation alone'}


def query(a,form,*,detailed=False):
    m=get(a); v=_form(form); t=ma.phase(a.tick); req=[]; pre=physical(a.world)
    ma.submit(a,'APD01.LEX.R01.cue.'+form,I,v,5,t,req)
    for sg in (-1,1):
        for stage,k,z,di,arrival in (('select',4,1,-1,4),('back',4,2,-1,5),('restore',3,3,1,6)):
            dv=(di*v[0],di*v[1],0); dest=ma.pos(v,k,z*sg)
            ma.submit(a,'APD01.LEX.R01.generic.'+form+'.'+stage+'.'+str(sg),
                      ma.add(dest,dv,-2),dv,7,t+arrival-2,req)
    frames=[]; answer=None
    for q in range(t,t+8):
        a.run_until(q)
        if detailed:
            pts={ma.pos(vv,k,z) for vv in ALL_DIRECTIONS
                 for k in (2,3,4,5) for z in range(-4,5)}
            frames.append({'tick':q,'sites':[ma.view(a,p) for p in sorted(pts)]})
        if q==t+4:
            answer=fixed_read(a)
    m['use_episodes']+=1; m['request_count']+=len(req); _save(a,m)
    return {'kind':'lexical_query','form':form,'input_tick':t,'read_tick':t+4,
            'end_tick':a.tick,'before':pre,'after':physical(a.world),
            'reader':answer,'requests':ma.receipts(a,req),'frames':frames,
            'teacher_or_expected_operation_supplied':False,
            'scope':'Form retrieves an acquired physical sign through prepared common access; not general Spanish or learned syntax'}


def sequence(a,forms,*,detailed=False):
    """Literal temporal exposure only, not a host parser or native syntax claim."""
    if not isinstance(forms,list) or not 1<=len(forms)<=8:
        raise ValueError('A finite frozen sequence of known forms is required')
    for form in forms:
        _form(form)
    rows=[query(a,form,detailed=detailed) for form in forms]
    return {'rows':rows,'order_is_experimental_input':True,
            'native_syntax_or_phrase_composition_demonstrated':False,
            'scope':'This preserves order of physical cue uses only; a downstream host must not reinterpret the phrase as a solved task'}
