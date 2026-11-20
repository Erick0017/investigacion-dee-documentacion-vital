"""A private action product teaches a fresh mobile receiver in one Runtime.

This is a declared NEW preparation, not an extension by copying trained matter.
The fixed four-lane interface never chooses a lane from an output or target.
Current context is a separate local resource carrier. All outcomes are v27.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation
from dee_thinking.persistence import encode_metadata
from integracion.shared_world import SharedSession, build_geometry, move, GEOMETRY_KEY, physical


def build_social_geometry(*, dimension=131, count=65, guard_mode="none", delay=17):
    if dimension!=131 or type(delay) is not int or delay not in(17,23):
        raise ValueError("Frozen first social family is N131, delays17/23")
    recipe,prep,g=build_geometry(dimension=dimension,count=count,guard_mode=guard_mode)
    ports=list(recipe.interfaces);parts={};n=dimension;action=g['ticks']['action'];teach=action+4
    read=teach+delay;use=read+4;delivery=use+5
    def port(name,site,dr):
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(*dr)
        c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True
        p=d.InterfaceSpec();p.name=name;p.channel=c;ports.append(p)
    for sx,lane in((-1,'left'),(1,'right')):
        for value,label in((-1,'minus'),(1,'plus')):
            key=lane+'.'+label;source=g['actions']['own.use.'+label]['site'];dr=(sx,value,1)
            hub=move(source,dr,4,n);cue=(-sx,0,-1);querysite=move(hub,(0,value,0),delay,n)
            effect=move(querysite,(0,value,1),4,n)
            base='B.social.'+key
            port(base+'.teach',move(hub,cue,-3,n),cue)
            port(base+'.query',move(querysite,(0,0,1),-3,n),(0,0,1))
            for context,suffix in((-1,'minus'),(1,'plus')):
                port(base+'.context.'+suffix,move(effect,(context,0,0),-3,n),(context,0,0))
            parts[key]={'lane':lane,'sx':sx,'value_axis':value,'source_action':source,
                'source_direction':list(dr),'hub':hub,'cue_direction':list(cue),
                'teach_port':base+'.teach','query_port':base+'.query','query_site':querysite,
                'effect_site':effect,'context_ports':{str(c):base+'.context.'+('plus' if c>0 else'minus') for c in(-1,1)},
                'delivery_sites':{str(c):move(effect,(c,value,1),5,n) for c in(-1,1)}}
    if len({x.name for x in ports})!=len(ports):raise ValueError("Duplicate social interface")
    g['social']={'schema':'CPC8.social_channel.geometry.v1','parts':parts,'delay':delay,
        'ticks':{'action':action,'before_message':action+2,'teaching':teach,'teach_input':teach-3,
                 'query':read,'query_input':read-3,'effect':use,'context_input':use-3,'delivery':delivery},
        'participants':{'A':'Original fresh U0 body plus its separately acquired own banks',
                        'B':'Fresh four-lane recipient; its opaque cue, renewed query and local context resource',
                        'lower_supports':'Native65 prepared interfaces, no inherited learned state'},
        'prepared':'Fixed routes, equal-dose receiver cues and all-candidate queries; context sensor transports current context on x axis',
        'acquired':'Receiver y-direction can only be acquired through the arriving native action product meeting its cue',
        'scope':'Directional social association plus prepared two-axis use, not a universal NSM meaning or adaptive routing claim',
        'old_name_protocol':'Not scheduled in this cohort; its original interfaces remain inert fromT0'}
    recipe.interfaces=ports;recipe.options={**dict(recipe.options),GEOMETRY_KEY:encode_metadata(g)}
    org=d.OrganizationSpec();org.id='B_SOCIAL';org.recipe_id='CPC8.social_recipient.v1'
    org.ports={key:d.Coordinate(*v['hub']) for key,v in parts.items()}
    recipe.organizations=list(recipe.organizations)+[org]
    return recipe,prep,g


class SocialSession(SharedSession):
    @classmethod
    def create(cls,**options):
        identifier=options.pop('identifier','CPC8_SOCIAL');recipe,p,g=build_social_geometry(**options)
        state={'schema':1,'requests':[],'queries':[],'reads':[],'frames':[],'parent':None,
               'social_queries':[],'social_captures':[]}
        return cls(d.OrganizationalWorld.create(recipe),p,g,state,identifier)
    def teach_receiver(self,mode='paired',payload=5):
        if mode not in('paired','unpaired','omitted'):raise ValueError("Receiver teaching mode")
        if mode=='omitted':return []
        t=self.geometry['social']['ticks']['teach_input']+int(mode=='unpaired')
        return self.stimulate([{'port':p['teach_port'],'payload':payload,'tick':t,
              'origin':'B_PRIVATE_OPAQUE_CUE_EQUAL_ON_ALL_CANDIDATES'} for p in self.geometry['social']['parts'].values()])
    def query_receiver(self,*,at_tick=None,payload=7,context=1,context_payload=9):
        if context not in(-1,1) or type(context) is not int:raise ValueError("Current local context is +/-1")
        sg=self.geometry['social'];t=sg['ticks']['query_input'] if at_tick is None else at_tick
        entries=[]
        for p in sg['parts'].values():
            entries.append({'port':p['query_port'],'payload':payload,'tick':t,'kind':'probe','origin':'B_ALL_CANDIDATE_QUERY'})
            entries.append({'port':p['context_ports'][str(context)],'payload':context_payload,'tick':t+4,
                            'kind':'probe','origin':'CURRENT_LOCAL_CONTEXT_RESOURCE_NOT_ACTION_POLICY'})
        self.stimulate(entries)
        self.state.setdefault('social_queries',[]).append({'input_tick':t,'read_tick':t+3,'effect_tick':t+7,
            'delivery_tick':t+12,'context':context,'payload':payload,'captured':[]})
    def _at_site(self,q):return exact_observation(self.world.runtime.observe(d.Coordinate(*q)))
    def social_view(self):
        sg=self.geometry['social'];t=sg['ticks'];now=self.tick
        return {'tick':now,'hubs':{k:self._at_site(p['hub']) for k,p in sg['parts'].items()},
                'nominal_mobile_lines':{k:self._at_site(move(p['hub'],(0,p['value_axis'],0),now-t['teaching'],self.geometry['N']))
                    for k,p in sg['parts'].items()},
                'query_targets':{k:self._at_site(p['query_site']) for k,p in sg['parts'].items()},
                'effect_targets':{k:self._at_site(p['effect_site']) for k,p in sg['parts'].items()},
                'delivery_targets':{k+'.context'+str(c):self._at_site(p['delivery_sites'][str(c)])
                    for k,p in sg['parts'].items() for c in(-1,1)},
                'coverage':'Fixed declared sites and nominal lines only. A nearby record is not assigned a unique genealogy.'}
    def observe(self):return {**super().observe(),'social':self.social_view()}
    def _capture_social(self,query,stage):
        field={'read_tick':'query_targets','effect_tick':'effect_targets','delivery_tick':'delivery_targets'}[stage]
        rows=self.social_view()[field];valid=[]
        for key,r in rows.items():
            v=r['direction'];active=r['active'] and r['semantic']==1
            if stage=='read_tick':covered=active and v[0]==0 and v[1] in(-1,1) and v[2]==1
            else:covered=active and v[0] in(-1,1) and v[1] in(-1,1) and v[2]==1
            if covered:valid.append({'location':key,'physical':r,'content_class':v[1],
                'context_class':None if stage=='read_tick' else v[0]})
        record={'tick':self.tick,'stage':stage,'observations':rows,'decoded':valid,
            'scope':'Fixed physical vector projection. Admission is reported separately; no scalar-zero substitution or inferred unique lineage.'}
        query['captured'].append(record);self.state.setdefault('social_captures',[]).append(deepcopy(record))
    def run_until(self,tick):
        if type(tick) is not int or tick<self.tick:raise ValueError("Monotone exact tick required")
        sg=self.geometry['social'];critical={sg['ticks']['before_message'],sg['ticks']['teaching']-1,sg['ticks']['teaching']}
        for q in self.state.get('social_queries',[]):critical.update(q[k] for k in('read_tick','effect_tick','delivery_tick'))
        for boundary in sorted(v for v in critical if self.tick<v<=tick):
            super().run_until(boundary)
            for q in self.state.get('social_queries',[]):
                for stage in('read_tick','effect_tick','delivery_tick'):
                    if q[stage]==boundary and not any(x['stage']==stage for x in q['captured']):self._capture_social(q,stage)
        return super().run_until(tick)
    def diagnostic_message(self,sham=False):
        t=self.geometry['social']['ticks'];n=self.geometry['N']
        if self.tick!=t['before_message']:raise ValueError("Fixed diagnostic before-message frontier")
        edits=[]
        for p in self.geometry['social']['parts'].values():
            site=move(p['source_action'],p['source_direction'],2,n);o=self.world.runtime.observe(d.Coordinate(*site))
            edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site);edit.raw=o.raw if sham else 0
            edit.label='CPC8 message path '+('sham' if sham else'cut');edits.append(edit)
        before=physical(self.world);child=self.world.diagnostic_fork(edits,True)
        if physical(self.world)!=before:raise AssertionError("Diagnostic altered MAIN")
        state=deepcopy(self.state);state['parent']={'identifier':self.identifier,'physical':before,'modality':'DIAGNOSTIC_FORK'}
        return type(self)(child,d.preparation_for_world(child),self.geometry,state,self.identifier+('.sham' if sham else'.cut'))
