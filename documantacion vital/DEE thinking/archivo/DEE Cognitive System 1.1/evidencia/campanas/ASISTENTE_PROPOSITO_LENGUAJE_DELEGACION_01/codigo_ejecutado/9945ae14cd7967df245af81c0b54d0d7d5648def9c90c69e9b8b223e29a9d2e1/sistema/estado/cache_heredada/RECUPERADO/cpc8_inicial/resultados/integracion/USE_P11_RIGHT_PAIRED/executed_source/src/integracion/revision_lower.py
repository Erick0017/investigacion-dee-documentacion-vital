"""Same third geometry with four inert-beforeT0 L01 revision interfaces.

M1 is an explicit physical experience protocol from4.5, not autonomous choice
of what/when to revise. The current consequence drives fixed teacher ports;
no previous response is read or compensated by this code.
"""
from .relocated_lower import build_relocated_geometry,RelocatedSession
from .shared_world import GEOMETRY_KEY,move,sign
from dee_thinking import _native as native
from dee_thinking.persistence import encode_metadata


def build_revision_geometry(*,guard_mode='treatment'):
    recipe,_,g=build_relocated_geometry(guard_mode=guard_mode)
    o=native.RepertoireOptions();o.dimension=131;o.forms=65;o.translation=native.Coordinate(60,60,0)
    o.revision_interfaces=True;o.revision_form=0;template=native.prepare_repertoire(o)
    candidates={p.name:p for p in template.recipe.interfaces};ports={};interfaces=list(recipe.interfaces)
    for value,label in((-1,'minus'),(1,'plus')):
        name=template.ports['revision.teacher2.treatment.'+label];original=candidates[name]
        interfaces.append(original);ports['treatment.'+label]=name
        source=original.channel;c=native.ChannelSpec();c.name='revision.teacher2.offpath_xy.'+label
        q=move([source.injection_site.x,source.injection_site.y,source.injection_site.z],(40,17,0),1,131)
        c.injection_site=native.Coordinate(*q);c.direction=source.direction;c.state=source.state;c.semantic=source.semantic
        c.allow_experience=source.allow_experience;c.allow_probe=source.allow_probe
        p=native.InterfaceSpec();p.name=c.name;p.channel=c;interfaces.append(p);ports['offpath_sham.'+label]=p.name
    recipe.interfaces=interfaces;recipe.parameters={**dict(recipe.parameters),'interfaces':len(interfaces)}
    g['resources']['interfaces']=len(interfaces)
    g['revision_profile']={'schema':'CPC8.integration.finite_L01_M1.v1','form':'L01','hub':g['lower_forms'][0]['hub'],
        'input_tick':524,'contact_tick':527,'post_query_input':655,'post_read':658,'ports':ports,
        'neutral_interfaces_beforeT0':4,'extra_initial_material':0,'offpath_shift':[40,17,0],
        'protocol':'Current cue5 + current event11 + fixed second teacher11. Same native directions as4.5double_teacher.',
        'offpath_scope':'Prepared XY control. Unlike +Z10 it does not land on another populated bank; XY invariants23/57 exclude the L01 target for both teacher directions. Later world consequences are still measured.',
        'modality':'EXPERIENCE_PROTOCOL; native execution; not a learned update schedule'}
    recipe.options={**dict(recipe.options),GEOMETRY_KEY:encode_metadata(g)}
    return recipe,None,g


class RevisableRelocatedSession(RelocatedSession):
    @classmethod
    def create(cls,*,identifier='CPC8_REVISION_L01',guard_mode='treatment'):
        recipe,_,geometry=build_revision_geometry(guard_mode=guard_mode)
        return cls(native.OrganizationalWorld.create(recipe),None,geometry,identifier=identifier)
    def revise_l01(self,current_sign,*,mode='treatment',tick=524):
        sign(current_sign)
        if tick!=524 or self.tick>tick or mode not in('treatment','offpath_sham','ordinary_only','no_update'):
            raise ValueError('Finite published L01 revision at524 with explicit mode required')
        if 'revision_profile' not in self.geometry:raise ValueError('Revision interfaces were not prepared atT0')
        if mode=='no_update':return []
        label='plus' if current_sign==1 else'minus'
        entries=[{'port':'L01.signal','payload':5,'tick':tick,'origin':'CURRENT_OPAQUE_CUE'},
            {'port':'L01.event.'+label,'payload':11,'tick':tick,'origin':'CURRENT_OBSERVED_DIRECTIONAL_CONSEQUENCE'}]
        if mode!='ordinary_only':entries.append({'port':self.geometry['revision_profile']['ports'][mode+'.'+label],
            'payload':11,'tick':tick,'origin':'CURRENT_CONSEQUENCE_FIXED_SECOND_TEACHER_CODEC'})
        return self.stimulate(entries)
    @classmethod
    def load(cls,path):
        result=super().load(path)
        if result.geometry.get('revision_profile',{}).get('schema')!='CPC8.integration.finite_L01_M1.v1':
            raise ValueError('Not a revision-enabled operational snapshot')
        return result
