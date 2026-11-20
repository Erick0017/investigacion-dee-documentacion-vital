"""One genuine K65 bank is the endogenously accessed U0 LEFT store.

The factory contains no learned values. L17 and the LEFT bank are one physical
memory/interface, not two copies. No external L17 reader is scheduled before
the native question. All other K65 banks remain physically present.
"""
from copy import deepcopy
from .shared_world import build_geometry,SharedSession,GEOMETRY_KEY
from dee_thinking import _native as native
from dee_thinking.persistence import encode_metadata


def build_alias_geometry(*, guard_mode="treatment"):
    recipe,p,g=build_geometry(dimension=131,count=65,center=(35,70,29),translation=(7,25,0),guard_mode=guard_mode)
    actual=p.forms[16].hub;site=[actual.x,actual.y,actual.z]
    if site!=g['own_banks']['left']['hub']:
        raise ValueError('The declared L17/LEFT physical coincidence is absent')
    interfaces=[q for q in recipe.interfaces if not q.name.startswith('U.left.')]
    # Required canonical K65 ports already have exactly these physical fields.
    expected={q.name:q.channel for q in recipe.interfaces if q.name.startswith('U.left.')}
    found={q.name:q.channel for q in interfaces if q.name.startswith('L17.')}
    for suffix in('signal','event.plus','event.minus'):
        a=expected['U.left.'+suffix];b=found['L17.'+suffix]
        def sig(c):return (c.injection_site.x,c.injection_site.y,c.injection_site.z,c.direction.dx,c.direction.dy,c.direction.dz,c.state,c.semantic,c.allow_experience,c.allow_probe)
        if sig(a)!=sig(b):raise ValueError('Alias has unequal physical interfaces')
    recipe.interfaces=interfaces;g['own_banks']['left']['name']='L17';g['own_banks']['left']['alias_lower_index']=16
    g['alias']={'bank':'left','form':'L17','index':16,'hub':site,
        'learning_inputs':'Only the actual L17 cue/event exposures; no separate U.left teaching.',
        'reader':'Native LEFT comparison question direction(-1,0,0),T19→134; no external L17 probe131.',
        'scope':'A consumed/reorganized relation may remain usable through its later sign while its original scalar interface is unavailable.'}
    g['resources']['extra_own_relations']=1;g['resources']['total_prepared_relation_interfaces']=66;g['resources']['interfaces']=len(interfaces)
    g['scope']='Fresh N131 K65 research geometry with actual L17 reused by U0 LEFT; not a65-way native selector or universal semantics.'
    recipe.options={**dict(recipe.options),GEOMETRY_KEY:encode_metadata(g)};recipe.domain=g['scope']
    return recipe,p,g


class AliasSession(SharedSession):
    @classmethod
    def create(cls,*,identifier='CPC8_ALIAS_L17',guard_mode='treatment'):
        r,p,g=build_alias_geometry(guard_mode=guard_mode)
        return cls(native.OrganizationalWorld.create(r),p,g,identifier=identifier)
    def expose_extra_right(self,value):
        if type(value) is not int or value not in(-1,1) or self.tick!=0:raise ValueError('Fresh current right consequence required')
        return self.stimulate([{'port':'U.right.signal','payload':5,'tick':0,'origin':'EXTRA_RIGHT_OPAQUE_CUE'},
            {'port':'U.right.event.'+('plus' if value==1 else'minus'),'payload':11,'tick':0,'origin':'EXTRA_RIGHT_CURRENT_CONSEQUENCE'}])
    def expose_lower_first(self,values,*,alias_mode='paired'):
        if alias_mode not in('paired','unpaired','omitted','no_cue'):raise ValueError('Explicit L17 exposure condition required')
        self.experience_lower(values,[i for i in range(32) if i!=16],0)
        if alias_mode=='paired':return self.experience_lower(values,[16],0)
        if alias_mode=='omitted':return []
        v=values[16];entries=[{'port':'L17.event.'+('plus' if v==1 else'minus'),'payload':11,'tick':0,'origin':'L17_CURRENT_DIRECTIONAL_EVENT'}]
        if alias_mode=='unpaired':entries.insert(0,{'port':'L17.signal','payload':5,'tick':1,'origin':'L17_DISPLACED_OPAQUE_CUE'})
        return self.stimulate(entries)
