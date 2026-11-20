"""Untrained geometry-only public preparation for the executed integrated U0.

No bank values, history or future consequence is required by this constructor.
The small interface assembly below mirrors the frozen scientific constructor;
equivalence is verified explicitly by verify_geometry(), not assumed by a name.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import interface
from integrated import Session
import residue_regulation as regulation
import comparison_need as need


def prepare_geometry(guard_mode='treatment',center=(33,25,42),backend='LAZY'):
    if guard_mode not in ('treatment','sham'):raise ValueError('Explicit guard preparation mode')
    p=regulation.guard_geometry({'guard_mode':guard_mode,'center':list(center),'backend':backend});g=p['geometry'];hub=g['forms'][2]['hub'];ports={}
    for mode,shift in (('treatment',(0,0,0)),('offpath_sham',(0,0,55))):
        for value,label in ((-1,'minus'),(1,'plus')):
            direction=(-1,value,0);target=need.moved(hub,shift,1);site=need.moved(target,direction,-3)
            name='revision.second.'+mode+'.'+label;p['interfaces'].append(interface(name,site,direction));ports[mode+'.'+label]=name
    g['interfaces']=len(p['interfaces']);g['integrated_revision']={'schema':'CPC7.integrated_revision.geometry.v1',
        'form':'L03','hub':hub,'input_tick':402,'revision_contact':405,'next_panel_input':469,'next_panel_read':472,
        'auxiliary_ports':ports,'auxiliary_sham_shift':[0,0,55],'auxiliary_sham_plane':60,
        'fixed_protocol':'Current opaque cue5 + current ordinary event11 + second teacher11 through a declared direction(-1,current_sign,0).',
        'scope':'One directed consequence update, not a host-computed correction from the old memory. All four empty ports present beforeT0 in every world.'}
    return p


def create_untrained(identifier='U0',guard_mode='treatment',center=(33,25,42),backend='LAZY'):
    import dee_thinking as d
    p=prepare_geometry(guard_mode,center,backend);r=d.OrganizationRecipe.research(67,p['placements'],0);r.interfaces=p['interfaces']
    b=getattr(d.Backend,backend);r.execution=d.TickOptions(b,2 if b==d.Backend.DENSE_PARALLEL else 1)
    return Session(d.OrganizationalWorld.create(r),p['geometry'],identity=identifier)


def revision_experience(geometry,current_sign,tick=402,mode='treatment'):
    if type(current_sign) is not int or current_sign not in (-1,1):raise ValueError('Actual current consequence must be +/-1')
    if tick!=402 or mode not in ('treatment','offpath_sham'):raise ValueError('Published finite revision contract')
    label='plus' if current_sign==1 else 'minus'
    return [{'port':'L03.signal','payload':5,'tick':tick,'kind':'submit','origin':'CURRENT_OPAQUE_FORM'},
        {'port':'L03.event.'+label,'payload':11,'tick':tick,'kind':'submit','origin':'CURRENT_OBSERVED_DIRECTIONAL_CONSEQUENCE'},
        {'port':geometry['integrated_revision']['auxiliary_ports'][mode+'.'+label],'payload':11,'tick':tick,
            'kind':'submit','origin':'CURRENT_CONSEQUENCE_FIXED_SECOND_TEACHER_CODEC'}]


def verify_geometry():
    import integrated_revision as frozen
    def signature(p):
        return {'placements':[(v.site.x,v.site.y,v.site.z,str(v.raw),str(v.clock),v.role) for v in p['placements']],
            'ports':[(v.name,v.channel.injection_site.x,v.channel.injection_site.y,v.channel.injection_site.z,
                v.channel.direction.dx,v.channel.direction.dy,v.channel.direction.dz,v.channel.state,v.channel.semantic,
                v.channel.allow_experience,v.channel.allow_probe) for v in p['interfaces']], 'geometry':p['geometry']}
    checks=[]
    for mode in ('treatment','sham'):
        case={'guard_mode':mode,'revision_mode':'treatment','bank_values':[1,-1]*8,'new_sign':1}
        equal=signature(prepare_geometry(mode))==signature(frozen.prepare_geometry(case));assert equal
        checks.append({'guard_mode':mode,'exact_placements_interfaces_geometry_equal_frozen_constructor':equal})
    return {'checks':checks,'engine_evolution_calls':0,'participant_response_or_target_used':False,
        'scope':'Mechanical preparation equivalence only; no new scientific trajectory or learned function.'}
