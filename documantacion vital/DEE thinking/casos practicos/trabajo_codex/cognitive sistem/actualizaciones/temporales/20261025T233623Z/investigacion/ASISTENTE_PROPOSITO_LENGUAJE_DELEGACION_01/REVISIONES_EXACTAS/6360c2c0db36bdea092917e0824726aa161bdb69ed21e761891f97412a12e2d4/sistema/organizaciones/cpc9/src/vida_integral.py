"""Fresh life with temporal current-event learning and a physical query loop.

Preparation precedes the sole Runtime. Historic MCTS, later contact, count,
two acquired quantities, regulation, return learning and current-event order
are not summed across worlds. Their coexistence is measured in this world.
"""
from pathlib import Path
from copy import deepcopy
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata,save_world_snapshot,load_world_snapshot
from vida_e1 import LifeSession,prepare_life
from cpc9_integrado import compact_observation_histories
from consulta_adquirida import QuerySession,prepare as prepare_query
from tiled_order_parallel import component as prepare_order,schedule as order_curriculum
from count_access import mount_component
KEY='CPC9.integral.N67.v1'

class MappedQuery(QuerySession):
    def __init__(self,world,g,aliases,state=None):super().__init__(world,g,state);self.aliases=aliases
    def input(self,name,payload,tick,probe=False):return super().input(self.aliases[name],payload,tick,probe)

def prepare(*,query_origin=(12,8,55),order_origin=(12,45,45),**options):
    recipe,g=prepare_life(**options)
    component,qg=prepare_query(origin=query_origin)
    recipe,aliases=mount_component(recipe,component,prefix='Q9.')
    ports,og=prepare_order(origin=order_origin)
    recipe.interfaces=list(recipe.interfaces)+ports
    if len({p.name for p in recipe.interfaces})!=len(recipe.interfaces):raise ValueError('Integral interface collision')
    g['tiled_order']=og
    g['cpc9_integral']={'schema':KEY,'query':{'geometry':qg,'aliases':aliases},
        'scope':'All components present from T0; query access consumable, fixed current-event order apparatus; integration requires measured causal function, not shared library.'}
    g['resources']['initial_material_sites']=len(recipe.placements);g['resources']['interfaces']=len(recipe.interfaces)
    recipe.options={'CPC8R.relational_pair.geometry':encode_metadata(g)}
    return recipe,g

class IntegralLifeSession(LifeSession):
    def __init__(self,*args,**options):
        super().__init__(*args,**options);entry=self.geometry['cpc9_integral']['query']
        self.query_loop=MappedQuery(self.world,entry['geometry'],entry['aliases'],self.state.get('cpc9_query_loop'))
    @classmethod
    def create(cls,identifier='CPC9_INTEGRAL_CANDIDATE',**options):
        recipe,g=prepare(**options);return cls(d.OrganizationalWorld.create(recipe),g,identifier=identifier)
    def curriculum(self,*,query_local='unknown',query_remote='known',query_delay=0,query_remote_load=11,
                   tile_order='AB',tile_interval=5,tile_a_load=3,tile_b_load=3,tile_event_a=True,tile_event_b=True,tile_form='paired',**options):
        super().curriculum(**options)
        self.query_loop.curriculum(query_local,query_remote,query_delay,remote_load=query_remote_load)
        order_curriculum(self,tile_order=tile_order,interval=tile_interval,a_load=tile_a_load,b_load=tile_b_load,
                         event_a=tile_event_a,event_b=tile_event_b,form=tile_form)
    def view(self):
        result=super().view();result['cpc9_query_loop']=self.query_loop.view()
        result['cpc9_current_order']=[{'id':entry['id'],'delta':entry['delta'],
            'hub':self.observe(entry['hub']),'effect':self.observe(entry['effect'])}for entry in self.geometry['tiled_order']['surfaces']]
        return result
    def receipts(self):return super().receipts()+self.query_loop.receipts()
    def save(self,path):
        state=deepcopy(self.state)
        for name,obj in (('mode',self.mode),('quantity',self.quantity),('initiative',self.initiative),
            ('transferred_quantity',self.transferred_quantity),('cpc9_count',self.count),('two_memory',self.two_memory),('cpc9_query_loop',self.query_loop)):
            if obj:state[name]=deepcopy(obj.state)
        if self.regulator:
            state['cpc9_regulator']=deepcopy(self.regulator.state)
            state['cpc9_regulator']['quantity']=deepcopy(self.regulator.quantity.state)
        g=deepcopy(self.geometry);g['cpc9_integral']['query']['geometry']=deepcopy(self.query_loop.geometry)
        g['cpc9_life']['two_memory']['geometry']=deepcopy(self.two_memory.geometry)
        self.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'identifier':self.identifier,'geometry':g,
            'state':compact_observation_histories(state),'tick':self.tick,'channels':sorted(self.world.runtime.channel_names)}))
        return save_world_snapshot(self.world,path,compress=True)
    @classmethod
    def load(cls,path):
        w,_=load_world_snapshot(path,max_bytes=1024**3);m=decode_metadata(dict(w.runtime.snapshot_metadata_entries)[KEY])
        if m['tick']!=int(w.runtime.current_tick)or m['channels']!=sorted(w.runtime.channel_names):raise ValueError('Integral continuity mismatch')
        return cls(w,m['geometry'],m['state'],m['identifier'])
