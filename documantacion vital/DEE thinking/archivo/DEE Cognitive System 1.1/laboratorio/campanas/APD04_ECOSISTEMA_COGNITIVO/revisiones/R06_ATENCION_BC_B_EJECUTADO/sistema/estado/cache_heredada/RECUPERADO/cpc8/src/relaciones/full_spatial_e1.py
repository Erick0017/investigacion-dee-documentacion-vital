"""Fresh shared Runtime: public longitudinal E1 plus actual spatial communication.

No acquired state is transplanted. All sensing arrays and interfaces are installed
beforeT0. The spatial chain is coupled to its own native receiver/context; sharing
the world does not by itself turn it into a third operand of the old206 join.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from integracion.complete_e1 import prepare_complete
from integracion.longitudinal_e1 import LongitudinalE1Session
from comunicacion.spatial_context import prepare_spatial_context_geometry,SpatialContextSession

def prepare_full_spatial(*,spatial_origin=(20,20,20),reference_state=17,object_states=(99,171),context_state=233,**options):
    recipe,g=prepare_complete(**options)
    spatial,sg=prepare_spatial_context_geometry(origin=spatial_origin,reference_state=reference_state,object_states=object_states,context_state=context_state,port_prefix='spx.')
    unique={};merged=[];shared=[];conflicts=[]
    for owner,source in(('BASE_E1',recipe.placements),('SPX',spatial.placements)):
        for p in source:
            q=(p.site.x,p.site.y,p.site.z);v=(int(p.raw),int(p.clock))
            if q in unique:
                if unique[q]['value']!=v:conflicts.append({'site':list(q),'first':unique[q],'second':{'owner':owner,'value':[str(v[0]),str(v[1])]}})
                else:shared.append({'site':list(q),'owners':[unique[q]['owner'],owner],'raw':str(v[0]),'clock':str(v[1])})
            else:unique[q]={'owner':owner,'value':v};merged.append(p)
    if conflicts:raise ValueError('Fresh T0 conflicting initial supports: '+str(conflicts))
    ports=list(recipe.interfaces)+list(spatial.interfaces)
    if len({p.name for p in ports})!=len(ports):raise ValueError('Duplicate fresh interface names')
    organizations=list(recipe.organizations)+list(spatial.organizations)
    if len({p.id for p in organizations})!=len(organizations):raise ValueError('Duplicate participant organization IDs')
    recipe.placements=merged;recipe.interfaces=ports;recipe.organizations=organizations
    g['spatial']=sg
    g['spatial_merge']={'rule':'Only byte-identical RAW/clock at identical sites may share initial support. Different values reject before Runtime creation.','shared_initial_supports':shared,'base_material':len(merged)-len(spatial.placements)+len(shared),'spatial_material':len(spatial.placements),'added_material':len(spatial.placements)-len(shared),'origin':list(spatial_origin),'runtime_count':1,'snapshot_merges':0}
    g['resources']['initial_material_sites']=len(merged);g['resources']['interfaces']=len(ports)
    g['finite_protocol']='CPC8R.longitudinalE1_plus_SPX.fresh0_to549.v1'
    g['ensemble_scope']='Fresh single N67 world. Old order/contact join, MODEsocial, quantity and native spatial reference/receiver/context chain share continuous evolution. Spatial use is not asserted part of the old206 join.'
    recipe.options={'CPC8R.relational_pair.geometry':encode_metadata(g)}
    return recipe,g

class FullSpatialE1Session(LongitudinalE1Session):
    def __init__(self,w,g,state=None,identifier='FULL_SPATIAL_E1'):
        super().__init__(w,g,state,identifier)
        self.spatial=SpatialContextSession(w,g['spatial'],self.state.get('spatial'))
        self.state.setdefault('spatial_captured_ticks',[])
    @classmethod
    def create(cls,identifier='FULL_SPATIAL_E1',**options):
        r,g=prepare_full_spatial(**options);return cls(d.OrganizationalWorld.create(r),g,identifier=identifier)
    def curriculum(self,*,spatial_reference_axis=1,spatial_objects=(1,-1),spatial_reference='paired',spatial_loads=(11,11,19),spatial_form='paired',spatial_context=1,spatial_context_objects=True,spatial_query=True,spatial_context_load=11,**options):
        if len(spatial_objects)!=2:raise ValueError('Two current spatial encounters')
        super().curriculum(**options)
        self.spatial.context_curriculum(spatial_reference_axis,*spatial_objects,spatial_context,reference=spatial_reference,loads=spatial_loads,form=spatial_form,query=spatial_query,context_objects=spatial_context_objects,context_load=spatial_context_load)
    def run_until(self,tick):
        if type(tick)is not int or tick<self.tick:raise ValueError('One monotone Runtime writer')
        for t in sorted(x for x in self.spatial.critical_ticks()if self.tick<x<=tick):
            super().run_until(t)
            if t not in self.state['spatial_captured_ticks']:
                self.spatial.capture(t);self.state['spatial_captured_ticks'].append(t)
        super().run_until(tick);return self.view()
    def view(self):
        v=super().view()
        if hasattr(self,'spatial'):v['spatial']={'reference_sensor':self.spatial.observe(self.geometry['spatial']['reference_sensor']),'social_captures':deepcopy(self.spatial.state.get('social_captures',[]))}
        return v
    def receipts(self):return super().receipts()+self.spatial.receipts()
    def save(self,path):
        self.state['spatial']=deepcopy(self.spatial.state)
        return super().save(path)
