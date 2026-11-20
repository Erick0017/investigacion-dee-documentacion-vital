"""CPC9 longer fresh life with retained and newly acquired operands.

This is a new preparation, not a restored or grafted MCTS/COUNT/RCA individual.
All extra readers and the relocated second-operand absorber exist before T0.
"""
from pathlib import Path
from copy import deepcopy
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata,decode_metadata,save_world_snapshot,load_world_snapshot
from cpc9_integrado import CPC9Session,prepare as prepare_integrated,compact_observation_histories
from count_access import mount_component
from two_memory import prepare as prepare_two,TwoMemorySession
from contact_access_g import prepare_remote_contact,schedule_remote
from retorno_social import port
KEY='CPC9.life.N67.v1'


class MappedTwo(TwoMemorySession):
    def __init__(self,world,g,aliases,state=None):
        super().__init__(world,g,state);self.aliases=aliases
    def input(self,name,payload,tick,probe=False):
        return super().input(self.aliases[name],payload,tick,probe)


def prepare_life(*,two_center=(8,52,10),two_absorber='off_path',remote_regulation='onpath',**options):
    recipe,g=prepare_integrated(**options)
    addition,tg=prepare_two(center=two_center,absorber=two_absorber)
    recipe,aliases=mount_component(recipe,addition,prefix='TM.')
    # Build only an inert second recipe; extract the added interfaces/geometry.
    remote,rg=prepare_remote_contact(remote_phase=3,remote_regulation=remote_regulation)
    existing=list(recipe.interfaces)
    for item in remote.interfaces:
        if item.name.startswith('remote_contact.'):existing.append(item)
    g['remote_contact']=deepcopy(rg['remote_contact'])
    g['cpc9_life']={'schema':KEY,'two_memory':{'geometry':tg,'aliases':aliases},
                    'long_quantity':'Actual new material update603→606, then new actual objects and old-word queries; fixed external curriculum',
                    'count_repeated_readers':[],'from_T0':'No trained memory or target answers in preparation'}
    unique={}
    if 'count'in g['cpc9_integrated']:
        cg=g['cpc9_integrated']['count']['geometry']
        for entry in cg['fixed_readers']:
            q=entry['query2']['site']
            for vector in ((0,0,1),(0,0,-1)):
                target=tuple(q),tuple(vector)
                if target not in unique:
                    name='repeat_count.'+str(len(unique));unique[target]=name
                    injection=[(q[i]-vector[i]*3)%67 for i in range(3)]
                    existing.append(port(name,injection,vector))
            g['cpc9_life']['count_repeated_readers'].append({'site':q,'heading':entry['heading'],
                    'route':entry['route_axis_candidate'],'plus_port':unique[(tuple(q),(0,0,1))],
                    'minus_port':unique[(tuple(q),(0,0,-1))]})
    if len({p.name for p in existing})!=len(existing):raise ValueError('Fresh-life interface collision')
    recipe.interfaces=existing
    g['resources']['initial_material_sites']=len(recipe.placements)
    g['resources']['interfaces']=len(existing)
    g['finite_protocol']='CPC9.life.0_to884.discovery.v1'
    recipe.options={'CPC8R.relational_pair.geometry':encode_metadata(g)}
    return recipe,g


class LifeSession(CPC9Session):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        tg=self.geometry['cpc9_life']['two_memory']
        self.two_memory=MappedTwo(self.world,tg['geometry'],tg['aliases'],self.state.get('two_memory'))

    @classmethod
    def create(cls,identifier='CPC9_E1_CANDIDATE',**options):
        recipe,g=prepare_life(**options)
        return cls(d.OrganizationalWorld.create(recipe),g,identifier=identifier)

    def curriculum(self,*,two_reference=31,two_object=11,two_omit=None,two_order='O_first',
                   remote_name='paired',remote_cue=5,remote_probe=5,remote_use=7,
                   extended_quantity=True,extended_count=True,extra_quantity_addition=7,**options):
        super().curriculum(**options)
        self.two_memory.curriculum(two_reference,two_object,omit=two_omit,order=two_order)
        schedule_remote(self,remote_name=remote_name,remote_cue=remote_cue,remote_probe=remote_probe,remote_use=remote_use)
        if extended_count:
            for index,tick in enumerate((215,282,349,416,483,550,617,684,751,818)):
                names={row['plus_port']if index%2==0 else row['minus_port']for row in self.geometry['cpc9_life']['count_repeated_readers']}
                for name in sorted(names):self.input(name,7,tick-3,'probe','FIXED_ALL_BANK_RECURRENT_WORD_READER')
        if extended_quantity:
            self.quantity.input('quantity.reference.cue',0,603)
            self.quantity.input('quantity.reference.resource',extra_quantity_addition,603)
            for index,value in enumerate((47,48,40,54),start=8):
                self.quantity.present_object(value,round_index=index)
                self.quantity.input('quantity.reader',7,69+67*index,True)
            for tick in (683,750,817,884):
                for bank in self.geometry['joint_names'].values():
                    self.input(bank['query_port'],17,tick-3,'probe','LATER_OLD_JOINT_FORM_NO_RETEACHING')

    def view(self):
        v=super().view()
        if hasattr(self,'two_memory'):
            v['two_memory']={key:self.two_memory.observe(self.two_memory.geometry[key])
                             for key in('center','reference_site','object_site','reference_hub','object_hub','auxiliary_hub')}
        v['remote_contact']=[{'id':x['id'],**{field:self.observe(x[field])for field in('hub','effect','renewed','renewed_effect')}}
                              for x in self.geometry['remote_contact']['surfaces']]
        v['count_repeated']=[{**row,'physical':self.observe(row['site'])}for row in self.geometry['cpc9_life']['count_repeated_readers']]
        return v

    def receipts(self):
        return super().receipts()+(self.two_memory.receipts()if hasattr(self,'two_memory')else[])

    def save(self,path):
        # Persist all operative child histories and aliases; passive caches are
        # bounded independently from the physical/queue snapshot.
        state=deepcopy(self.state)
        for key,obj in (('mode',self.mode),('quantity',self.quantity),('initiative',self.initiative),
                        ('transferred_quantity',self.transferred_quantity),('cpc9_count',self.count),('two_memory',self.two_memory)):
            if obj:state[key]=deepcopy(obj.state)
        if self.regulator:
            state['cpc9_regulator']=deepcopy(self.regulator.state)
            state['cpc9_regulator']['quantity']=deepcopy(self.regulator.quantity.state)
        state=compact_observation_histories(state)
        geometry=deepcopy(self.geometry)
        geometry['cpc9_life']['two_memory']['geometry']=deepcopy(self.two_memory.geometry)
        self.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'identifier':self.identifier,'geometry':geometry,
             'state':state,'tick':self.tick,'channels':sorted(self.world.runtime.channel_names)}))
        return save_world_snapshot(self.world,path,compress=True)

    @classmethod
    def load(cls,path):
        w,_=load_world_snapshot(path,max_bytes=1024**3)
        m=decode_metadata(dict(w.runtime.snapshot_metadata_entries)[KEY])
        if m['tick']!=int(w.runtime.current_tick)or m['channels']!=sorted(w.runtime.channel_names):raise ValueError('Life continuity mismatch')
        return cls(w,m['geometry'],m['state'],m['identifier'])
