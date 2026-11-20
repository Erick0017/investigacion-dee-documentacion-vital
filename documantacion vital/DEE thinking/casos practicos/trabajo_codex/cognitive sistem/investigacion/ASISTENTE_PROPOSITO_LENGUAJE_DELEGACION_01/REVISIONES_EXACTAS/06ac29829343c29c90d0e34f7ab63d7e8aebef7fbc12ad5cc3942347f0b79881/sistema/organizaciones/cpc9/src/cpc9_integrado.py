"""Fresh N67 organization: MCTS, bidirectional return, count access and RCA.

All components are prepared before the sole Runtime is constructed. No trained
states are loaded. Coexistence, interaction and retained functions are measured
by the runner, not inferred from library membership.
"""
from copy import deepcopy
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src')]
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata,save_world_snapshot,load_world_snapshot
from retorno_social import ReturnSession,prepare_return
from count_access import prepare_component as prepare_count,mount_component,CountAccessSession,curriculum as count_curriculum
from regulacion_acoplada.aparato import prepare as prepare_regulation,CoupledRegulationSession
from regulacion_acoplada.mcts import PrefixedQuantitySession
KEY='CPC9.integrated.fresh.v1'


class MappedCount(CountAccessSession):
    def __init__(self,world,geometry,aliases,state=None):
        super().__init__(world,geometry,state);self.aliases=aliases
    def input(self,name,payload,tick,probe=False):
        return super().input(self.aliases[name],payload,tick,probe)


def prepare(*,enable_count=True,enable_regulation=True,regulation_medium=1,regulation_route='onpath',
            count_contacts=('A','B'),count_actor_load=0,**options):
    recipe,g=prepare_return(**options)
    extra={'schema':KEY,'enabled':{'count':enable_count,'regulation':enable_regulation},
           'initial_target_memories':'No target associations transplanted; all learned operands/signs follow current experiences'}
    if enable_regulation:
        component,cg=prepare_regulation(medium=regulation_medium,routing=regulation_route)
        recipe,aliases=mount_component(recipe,component,prefix='R.')
        extra['regulation']={'geometry':cg,'aliases':aliases}
    if enable_count:
        cc={'id':'INTEGRATED_FRESH_COUNT','contacts':list(count_contacts),'actor_load':count_actor_load,'bridge_guard':'onpath'}
        component,cg=prepare_count(cc)
        recipe,aliases=mount_component(recipe,component,prefix='C9COUNT.')
        extra['count']={'geometry':cg,'aliases':aliases,'case':cc}
    g['cpc9_integrated']=extra
    g['resources']['initial_material_sites']=len(recipe.placements)
    g['resources']['interfaces']=len(recipe.interfaces)
    g['resources']['basic_buffer_bytes']=32*67**3
    g['finite_protocol']='CPC9.fresh.MCTS_return_count_RCA.0_to616.v1'
    recipe.options={'CPC8R.relational_pair.geometry':encode_metadata(g)}
    recipe.domain='Experimental same-Runtime integration, N67 fixed. Integration claims require observed independent function panel.'
    return recipe,g


def compact_observation_histories(value):
    """Remove only passive caches from metadata copies, retaining empty keys.

    Physical arrays/clocks, pending inputs, receipts, protocol state, interface
    aliases and curriculum progress are not touched. Primary traces live outside
    the session metadata and are not used as participant memory.
    """
    if isinstance(value,dict):
        out={}
        for k,v in value.items():
            passive=(k in ('captures','frames','observations','windows') or
                     k.endswith(('_captures','_observations','_windows')))
            out[k]=[] if passive and isinstance(v,list) else compact_observation_histories(v)
        return out
    if isinstance(value,list):return[compact_observation_histories(v)for v in value]
    return deepcopy(value)


class CPC9Session(ReturnSession):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        g=self.geometry['cpc9_integrated']
        self.count=None;self.regulator=None
        if g['enabled']['count']:
            self.count=MappedCount(self.world,g['count']['geometry'],g['count']['aliases'],self.state.get('cpc9_count'))
        if g['enabled']['regulation']:
            self.regulator=CoupledRegulationSession(self.world,g['regulation']['geometry'],self.state.get('cpc9_regulator'))
            self.regulator.quantity=PrefixedQuantitySession(self.world,g['regulation']['geometry']['quantity'],self.regulator.state.get('quantity'))

    @classmethod
    def create(cls,identifier='CPC9_FRESH_E1',**options):
        recipe,g=prepare(**options)
        return cls(d.OrganizationalWorld.create(recipe),g,identifier=identifier)

    def curriculum(self,*,count_form='paired',count_route=True,count_query=True,
                   regulation_reference=31,regulation_objects=(16,37),**options):
        super().curriculum(**options)
        if self.count:count_curriculum(self.count,form=count_form,route=count_route,query=count_query)
        if self.regulator:self.regulator.curriculum(regulation_reference,regulation_objects)

    def view(self):
        result=super().view()
        result['return']=self.return_view()
        if getattr(self,'count',None):result['cpc9_count']=self.count.view()
        if getattr(self,'regulator',None):
            result['cpc9_regulator']=self.regulator.capture()
            self.regulator.state['frames']=[]
        result['mode'].pop('captures',None);result['mode'].pop('social_captures',None)
        return result

    def receipts(self):
        return super().receipts()+(self.count.receipts()if self.count else[])+(self.regulator.receipts()if self.regulator else[])

    def save(self,path):
        state=deepcopy(self.state)
        for key,component in (('mode',self.mode),('quantity',self.quantity),('initiative',self.initiative),
                              ('transferred_quantity',self.transferred_quantity),('cpc9_count',self.count)):
            if component:state[key]=deepcopy(component.state)
        if self.regulator:
            state['cpc9_regulator']=deepcopy(self.regulator.state)
            state['cpc9_regulator']['quantity']=deepcopy(self.regulator.quantity.state)
        state=compact_observation_histories(state)
        self.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'identifier':self.identifier,'geometry':self.geometry,
            'state':state,'tick':self.tick,'channels':sorted(self.world.runtime.channel_names),
            'passive_caches':'Not operative; exact primary traces are stored externally'}))
        return save_world_snapshot(self.world,path,compress=True)

    @classmethod
    def load(cls,path):
        w,_=load_world_snapshot(path,max_bytes=1024**3)
        m=decode_metadata(dict(w.runtime.snapshot_metadata_entries)[KEY])
        if m['tick']!=int(w.runtime.current_tick)or m['channels']!=sorted(w.runtime.channel_names):
            raise ValueError('Physical/operative identity mismatch')
        return cls(w,m['geometry'],m['state'],m['identifier'])
