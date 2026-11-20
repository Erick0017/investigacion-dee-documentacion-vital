"""Explicit native reference re-acquisition after diagnosed access loss.

Optional experimental system layer. Does not restore history, edit fields,
read audit results, or silently refill a failed memory. R0 guard is prepared.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from app.native_tools import moore27
from capacidades import espanol_funcional_01 as e

def reacquire(a,*,value=86,guard='on_route',teaching='paired'):
    if type(value)is not int or not 42<=value<=123 or guard not in('on_route','sham','none')or teaching not in('paired','unpaired','omitted'):raise ValueError('Exact explicit experience, finite value and declared R0 control required')
    g=e.prepare(a)
    if g.get('magnitude_reacquisition_r26'):raise ValueError('This intervention already lived; never reset or refill it silently')
    site=[47,38,33]if guard=='on_route'else[47,38,42];requests=[];start=e.tick_at_or_after(a.tick,phase=0,lead=5);pre=moore27(a.world,a.quantity.geometry['reference_hub'])
    if guard!='none':
        name='EF01.REF26.'+guard;ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*site);ch.direction=d.Direction(0,0,0);ch.state=1;ch.semantic=4;ch.allow_experience=True;ch.allow_probe=True;p=d.InterfaceSpec();p.name=name;p.channel=ch;a.world.declare_interface(p)
        r=a.world.submit(name,0,int(a.tick)+1);requests.append({'port':name,'id':int(r.id),'payload':0,'tick':int(a.tick)+1})
    first=len(a.quantity.state['requests'])
    if teaching!='omitted':a.quantity.experience_reference(value,tick=start,mode=teaching)
    a.run_until(start+3);post=e.obs(a,a.quantity.geometry['reference_hub']);g['magnitude_reacquisition_r26']={'schema':'DCS1.1.EF01.reference_reacquisition.r26','guard':guard,'guard_site':site if guard!='none'else None,'teaching':teaching,'experience_tick':start,'new_actual_value':value,'not_retention':'Explicit new experience, not recovery of an unchanged old biography or hidden restoration','R_level':'R0 prepared, not learned policy'};a.world.runtime.set_snapshot_metadata(e.KEY,encode_metadata(g))
    return {'ENTORNO':{'explicit_new_reference_value':value,'fixed_format_cue':5,'teaching':teaching},'ENTE':{'pre_reference_moore':pre,'post_reference':post,'post_reference_moore':moore27(a.world,a.quantity.geometry['reference_hub'])},
        'INSTRUMENTO':{'guard':guard,'guard_site':site if guard!='none'else None,'guard_requests':[e.receipt_at(a.world,r)for r in requests],'reference_requests':a.quantity.receipts()[first:]},
        'INTERPRETACION':'Native additional reference experience plus optional R0 route protection. Words are not re-taught and old state is not restored; later use and collateral effects require their own tests.'}
