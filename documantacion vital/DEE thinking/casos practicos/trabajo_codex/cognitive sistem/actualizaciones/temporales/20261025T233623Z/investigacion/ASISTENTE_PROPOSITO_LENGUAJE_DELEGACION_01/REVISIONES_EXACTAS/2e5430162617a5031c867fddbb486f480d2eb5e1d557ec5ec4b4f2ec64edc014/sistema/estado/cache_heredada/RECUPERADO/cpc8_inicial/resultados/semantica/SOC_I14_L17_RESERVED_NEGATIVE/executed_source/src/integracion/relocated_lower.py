"""Third/final integration family: only L17 relocated into the native LEFT path.

All65 are freshly taught. Other64 banks stay in the distant column validated
by E1. The generic C++ directional reader receives actual declared sites; the
old fixed-form C++ descriptor is deliberately NOT asserted for this geometry.
"""
from copy import deepcopy
from .shared_world import build_geometry,SharedSession,GEOMETRY_KEY,SESSION_KEY,move,physical,exact_int,sign
from .alias_lower import AliasSession
from dee_thinking import _native as native
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import encode_metadata,decode_metadata,load_world_snapshot


def build_relocated_geometry(*,guard_mode='treatment'):
    recipe,p,g=build_geometry(dimension=131,count=65,center=(35,70,29),translation=(60,60,0),guard_mode=guard_mode)
    template={q.name:q for q in recipe.interfaces if q.name.startswith('U.left.')}
    interfaces=[q for q in recipe.interfaces if not q.name.startswith(('U.left.','L17.'))]
    for suffix in('signal','event.plus','event.minus'):
        source=template['U.left.'+suffix].channel;c=native.ChannelSpec();c.name='L17.'+suffix
        c.injection_site=source.injection_site;c.direction=source.direction;c.state=source.state;c.semantic=source.semantic
        c.allow_experience=source.allow_experience;c.allow_probe=source.allow_probe
        i=native.InterfaceSpec();i.name=c.name;i.channel=c;interfaces.append(i)
    old=deepcopy(g['lower_forms'][16]['hub']);hub=deepcopy(g['own_banks']['left']['hub'])
    g['lower_forms'][16]['hub']=hub;g['own_banks']['left']['name']='L17';g['own_banks']['left']['alias_lower_index']=16
    g['alias']={'bank':'left','form':'L17','index':16,'hub':hub,'old_isolated_form_hub':old,
        'learning_inputs':'Only actual L17 cue/event exposures. No copy, trained transplant or duplicate U.left teaching.',
        'reader':'Native LEFT questionT19→134; external L17 reader131 deliberately omitted.',
        'relocation':'Initial interface geometry only. No trained material moved;65banks have no initial material.'}
    g['integration_family']='SELECTIVE_L17_RELOCATION_THIRD_AND_FINAL'
    g['resources']['extra_own_relations']=1;g['resources']['total_prepared_relation_interfaces']=66;g['resources']['interfaces']=len(interfaces)
    g['scope']='New Research preparation:64distant native-derived banks plus actual L17 inU0LEFT, one extraRIGHT. Field readout is native; not the unchanged factoryK65 geometry or65-way native routing.'
    recipe.interfaces=interfaces
    # Do not persist a native fixed-form descriptor with the old L17 landmark.
    options=dict(recipe.options)
    options.pop('dee_thinking.consolidated.descriptor.v1',None);options.pop('consolidated_profile',None)
    options[GEOMETRY_KEY]=encode_metadata(g);options['CPC8.integration.reader_profile']='GENERIC_NATIVE_DIRECTIONAL_AT_DECLARED_RESEARCH_SITES'
    recipe.options=options;recipe.domain=g['scope']
    recipe.parameters={**dict(recipe.parameters),'initial_material_sites':len(recipe.placements),'interfaces':len(interfaces)}
    organizations=[o for o in recipe.organizations if o.id!='organization']
    o=native.OrganizationSpec();o.id='repertoire_CPC8';o.recipe_id='CPC8.relocated_repertoire.v1'
    o.ports={'form.'+f['name']:native.Coordinate(*f['hub']) for f in g['lower_forms']};organizations.append(o);recipe.organizations=organizations
    return recipe,None,g


class RelocatedSession(AliasSession):
    @classmethod
    def create(cls,*,identifier='CPC8_RELOCATED_L17',guard_mode='treatment'):
        r,p,g=build_relocated_geometry(guard_mode=guard_mode)
        return cls(native.OrganizationalWorld.create(r),None,g,identifier=identifier)
    def experience_lower(self,values,indices,at_tick):
        exact_int(at_tick,'acquisition tick',self.tick);entries=[]
        for k in list(indices):
            exact_int(k,'form index',0,64);v=sign(values[k]);name=self.geometry['lower_forms'][k]['name']
            entries.extend([{'port':name+'.signal','payload':5,'tick':at_tick,'origin':'CURRENT_OPAQUE_CUE'},
                {'port':name+'.event.'+('plus' if v==1 else'minus'),'payload':11,'tick':at_tick,'origin':'CURRENT_DIRECTIONAL_EVENT'}])
        return self.stimulate(entries)
    def query_lower(self,indices,at_tick,payload=9):
        exact_int(at_tick,'query tick',self.tick);exact_int(payload,'probe payload',0,65535);items=[]
        indices=list(indices)
        for k in indices:exact_int(k,'form index',0,64)
        for k in indices:
            name=self.geometry['lower_forms'][k]['name'];r=self.world.probe(name+'.signal',payload,at_tick)
            self._remember(r,name+'.signal',payload,at_tick,'probe','DECLARED_LOWER_PANEL');items.append({'index':k,'receipt_id':int(r.id)})
        self.state['queries'].append({'kind':'lower','input_tick':at_tick,'read_tick':at_tick+3,'payload':payload,'items':items,'captured':None})
    def run_until(self,tick):
        exact_int(tick,'absolute target',self.tick);t=self.geometry['ticks']
        critical={5,15,19,20,t['information']-1,t['information'],t['action'],t['association']-1,t['association'],t['name_read']-1,t['name_read']}
        critical.update(q['read_tick'] for q in self.state['queries'] if q['captured'] is None)
        for boundary in sorted(q for q in critical if self.tick<q<=tick):
            self.world.run_until(boundary);self.state['frames'].append(self.observe())
            for q in self.state['queries']:
                if q['captured'] is None and q['read_tick']==boundary:
                    rows=[]
                    for item in q['items']:
                        if q['kind']=='lower':f=self.geometry['lower_forms'][item['index']];site=f['hub'];name=f['name'];channel=name+'.signal'
                        else:site=item['site'];name=item['key'];channel=self.geometry['names'][name]['query_port']
                        r=native.read_directional_response(self.world,native.Coordinate(*site),item['receipt_id'],q['payload'],boundary)
                        correct_channel=r.receipt is not None and channel in list(r.receipt.channels)
                        rows.append({'name':name,'physical':exact_observation(r.physical),'receipt':exact_receipt(r.receipt),
                            'coverage':bool(r.covered and correct_channel),'value':r.value if correct_channel else None,
                            'status':r.status if correct_channel else'RECEIPT_FOR_DIFFERENT_INTERFACE','provenance':'ENTE'})
                    q['captured']={'tick':boundary,'kind':q['kind'],'responses':rows};self.state['reads'].append(deepcopy(q['captured']))
        self.world.run_until(tick);return self.observe()
    @classmethod
    def load(cls,path):
        world,proof=load_world_snapshot(path,max_bytes=1024**3);meta=dict(world.runtime.snapshot_metadata_entries)
        v=decode_metadata(meta[SESSION_KEY],max_bytes=8*1024**2);g=decode_metadata(world.recipe.options[GEOMETRY_KEY])
        if g.get('integration_family')!='SELECTIVE_L17_RELOCATION_THIRD_AND_FINAL' or v['tick']!=int(world.runtime.current_tick) or v['channels']!=sorted(world.runtime.channel_names):raise ValueError('Incompatible relocated Research snapshot')
        return cls(world,None,g,v['state'],v['identifier'])
    def diagnostic_question(self,sham=False):
        if self.tick!=20 or type(sham) is not bool:raise ValueError('Fixed external diagnosticT20 only')
        edits=[]
        for p in self.geometry['questions'].values():
            if p['dx']:
                q=move(p['site'],(p['dx'],0,0),1,131);o=self.world.runtime.observe(native.Coordinate(*q))
                e=native.ResearchStateEdit();e.coordinate=native.Coordinate(*q);e.raw=o.raw if sham else 0;e.label='CPC8 relocated question '+('sham' if sham else'cut');edits.append(e)
        before=physical(self.world);child=self.world.diagnostic_fork(edits,True)
        if physical(self.world)!=before:raise AssertionError('Diagnostic changed MAIN')
        state=deepcopy(self.state);state['parent']={'identifier':self.identifier,'physical':before,'modality':'DIAGNOSTIC_FORK'}
        return type(self)(child,None,self.geometry,state,self.identifier+('.sham' if sham else'.cut'))
