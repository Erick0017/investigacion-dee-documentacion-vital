"""Experimental, finite native remote-reader session (CPC6 reference domain).

The installed module assembles a declared research recipe beforeT0. It does not
import a laboratory, its runners or stored answers. The microscopic evolution
is exclusively the same native Runtime. This profile is separate from CPC7U0.
Python's fixed vector projections below are interface decoders, not a predictor
or a policy. Their successful reference window is162, not arbitrary recurrence.
"""
from copy import deepcopy
import json
from . import _native as native
from ._remote_preparation import build, moved
from .consolidated import _integer, _sign, exact_observation, exact_receipt
from .persistence import (encode_metadata,decode_metadata,load_world_snapshot,
                         save_world_snapshot,DEFAULT_MAX_SNAPSHOT_BYTES)

KEY="dee_thinking.remote_reader.session.v1"
GEOMETRY_KEY="dee_thinking.remote_reader.geometry.v1"


class RemoteReaderSession:
    """Research recipe with one MAIN and three explicitly prepared stores."""
    session_kind='remote_reader_experimental'
    def __init__(self,world,geometry,state=None,identifier="REMOTE_READER"):
        self.world=world;self.geometry=deepcopy(geometry);self.identifier=identifier
        self.state=deepcopy(state) if state is not None else {"schema":1,"requests":[],"reads":[],"aliases":[]}
        encode_metadata(self.state)
        self.storage_proof=None

    @classmethod
    def create(cls,*,backend="LAZY",threads=1,identifier="REMOTE_READER"):
        _integer(threads,"threads",1,1024)
        recipe,g=build(backend,threads)
        return cls(native.OrganizationalWorld.create(recipe),g,identifier=identifier)

    @property
    def tick(self):return int(self.world.runtime.current_tick)

    def stimulate(self,requests):
        """Deduplicate only identical physical requests, never based on RAW."""
        specs={p.name:p.channel for p in self.world.interfaces};seen={};groups=[]
        if not isinstance(requests,list):raise TypeError("Explicit request list required")
        if len(self.state['requests'])+len(requests)>20000:raise ValueError("Bounded research journal full")
        for request in requests:
            port=request['port'];payload=_integer(request['payload'],'payload',0,65535)
            tick=_integer(request['tick'],'absolute tick');kind=request.get('kind','submit')
            if tick<self.tick or port not in specs or kind not in('submit','probe'):
                raise ValueError("Invalid/past undeclared request")
            c=specs[port];q=c.injection_site;v=c.direction
            key=(q.x,q.y,q.z,v.dx,v.dy,v.dz,c.state,c.semantic,tick,payload,kind)
            if key in seen:groups[seen[key]]['logical_aliases'].append(port)
            else:seen[key]=len(groups);groups.append({**request,'logical_aliases':[port]})
        result=[]
        for q in groups:
            r=getattr(self.world,q.get('kind','submit'))(q['port'],q['payload'],q['tick'])
            row={**q,'id':int(r.id),'call_tick':self.tick};self.state['requests'].append(row)
            result.append(exact_receipt(r))
        self.state['aliases'].append({'tick':self.tick,'logical_count':len(requests),'physical_count':len(groups),
            'scope':'Public interface identity only; no physical readout or history selected admission'})
        return result

    def experience_order(self,order,*,event_payload=5,reader=True):
        if self.tick!=0 or order not in('AB','BA'):raise ValueError("Fixed order protocol AB/BA starts atT0")
        _integer(event_payload,'event payload',0,65535)
        if type(reader) is not bool:raise TypeError("reader must be explicit boolean")
        entries=[{'port':'event.'+event,'payload':event_payload,'tick':i} for i,event in enumerate(order)]
        if reader:entries.append({'port':'order.read','payload':7,'tick':2,'kind':'probe'})
        return self.stimulate(entries)

    def acquire_sources(self,p=1,q=-1,*,mode='paired'):
        if self.tick!=0:raise ValueError("Published source-acquisition protocol starts atT0")
        _sign(p);_sign(q)
        if mode not in('paired','unpaired','omitted'):raise ValueError("Source mode paired/unpaired/omitted")
        if mode=='omitted':return []
        g=self.geometry['adapter'];entries=[]
        def part(item):
            for label,load in zip(('cue','event'),item['loads']):
                entries.append({'port':item['base']+'.'+label,'payload':load,
                    'tick':int(mode=='unpaired') if label=='cue' else 0,'kind':'submit'})
        for key,parts in g['source_codecs'].items():
            source=parts[0]['source'];value=parts[0]['value_direction']
            if source=='P' and value==p:
                for item in parts:part(item)
            elif source=='Q' and q==1 and value==1:
                for item in parts:part(item)
        if q==-1:
            for key,item in self.geometry['balanced_source_codec']['parts'].items():
                part(g['source_codecs'][key+'.Q.positive'][0]);part(item)
        return self.stimulate(entries)

    def consequence(self,value,*,tick=11,payload=17):
        _sign(value)
        if tick!=11:raise ValueError("Fixed actual-event sensor inputT11")
        return self.stimulate([{'port':'feedback.actual.'+lane+'.'+('plus' if value==1 else'minus'),
            'payload':payload,'tick':tick} for lane in('left','right')])

    def late_use(self,*,payload=13):
        return self.stimulate([{'port':name,'payload':payload,'tick':item['request_tick'],'kind':'probe'}
                              for name,item in self.geometry['adapter']['late_queries'].items()])

    def teach_first_form(self,*,mode='paired',payload=5):
        if mode not in('paired','unpaired','omitted'):raise ValueError("Teaching mode")
        if mode=='omitted':return []
        return self.stimulate([{'port':p['teach_port'],'payload':payload,
            'tick':p['teach_request_tick']+int(mode=='unpaired')} for p in self.geometry['language']['items'].values()])

    def _read_boundary(self,kind,tick):
        self.state['reads'].append({'kind':kind,'tick':tick,'captured':None})

    def query_first_form(self,*,tick=50,payload=11,remote_reader=True):
        _integer(tick,'query tick')
        entries=[{'port':p['query_port'],'payload':payload,'tick':tick,'kind':'probe'}
                 for p in self.geometry['language']['items'].values()]
        if remote_reader:
            entries += [{'port':p['port'],'payload':payload,'tick':tick,'kind':'probe'}
                        for p in self.geometry['word_bus']['parts'].values()]
        rr=self.stimulate(entries);self._read_boundary('first_form',tick+3)
        if remote_reader:self._read_boundary('remote_reader',tick+45)
        return rr

    def learn_second_form(self,*,mode='paired'):
        """Renew original history, then introduce a second opaque form later."""
        if mode not in('paired','unpaired','omitted'):raise ValueError("Teaching mode")
        entries=[{'port':self.geometry['renewed_interfaces']['original']['port'],'payload':11,'tick':69,'kind':'probe'}]
        if mode!='omitted':entries += [{'port':p['teach_port'],'payload':5,'tick':77+int(mode=='unpaired')}
                                      for p in self.geometry['order_language']['items'].values()]
        entries += [{'port':p['query_port'],'payload':7,'tick':87,'kind':'probe'}
                    for p in self.geometry['order_language']['items'].values()]
        rr=self.stimulate(entries);self._read_boundary('second_form',90);return rr

    def _at(self,site):return exact_observation(self.world.runtime.observe(native.Coordinate(*site)))

    def observe(self):
        return {'tick':self.tick,'body':{k:self._at(self.geometry['body'][k]) for k in('A','B','center','emission_site')},
            'first_form':{k:self._at(v['query_site']) for k,v in self.geometry['language']['items'].items()},
            'second_form':{k:self._at(v['query_site']) for k,v in self.geometry['order_language']['items'].items()},
            'remote_reader':{k:self._at(v['target']) for k,v in self.geometry['word_bus']['parts'].items()},
            'modality':'PASSIVE_OBSERVATION','scope':'Selected current sites; no inferred unique genealogy across unobserved segments'}

    def _capture(self,kind):
        view=self.observe();field={'first_form':'first_form','second_form':'second_form','remote_reader':'remote_reader'}[kind]
        outputs=[]
        for key,r in view[field].items():
            dr=r['direction'];valid=r['active'] and r['semantic']==1
            if kind=='first_form':valid=valid and dr[0] in(-1,1) and dr[1:]==[0,1];value=dr[0]
            elif kind=='second_form':valid=valid and dr[0]==1 and dr[1] in(-1,1) and dr[2]==-1;value=dr[1]
            else:valid=valid and self.tick==162 and dr[0] in(-1,1) and dr[1:]==[0,-1];value=dr[0]
            status='MEASURED_PATTERN' if valid else 'NO_PATTERN_IN_FIXED_WINDOW'
            if kind=='remote_reader' and self.tick!=162:status='OUTSIDE_VALIDATED_REMOTE_WINDOW'
            outputs.append({'location':key,'physical':r,'covered':bool(valid),'value':value if valid else None,'status':status})
        return {'tick':self.tick,'kind':kind,'responses':outputs,'modality':'INSTRUMENTAL_READ_AT_PHYSICAL_QUERY_BOUNDARY',
                'scope':'Experimental fixed output-pattern decoder. covered means this physical pattern was observed, not that a particular request was admitted or that its unique genealogy was established. Exact admission remains in receipts; no general semantic classifier is asserted.'}

    def read_current_reader(self):
        value=self._capture('remote_reader')
        value['modality']='PASSIVE_OBSERVATION'
        value['scope']='Current reader-pattern observation; it is not asserted to be a response to an admitted new request.'
        return value

    def run_until(self,tick):
        _integer(tick,'absolute tick')
        if tick<self.tick:raise ValueError("Cannot reverse MAIN time")
        for boundary in sorted({r['tick'] for r in self.state['reads'] if r['captured'] is None and self.tick<=r['tick']<=tick}):
            self.world.run_until(boundary)
            for r in self.state['reads']:
                if r['captured'] is None and r['tick']==boundary:r['captured']=self._capture(r['kind'])
        self.world.run_until(tick)
        return self.observe()

    def receipts(self):
        return [{**deepcopy(q),'receipt':exact_receipt(self.world.runtime.receipt(q['id']),q['id'])} for q in self.state['requests']]

    @property
    def readings(self):return deepcopy(self.state['reads'])

    def save_snapshot(self,path,*,compress=None,overwrite=False):
        self.world.runtime.set_snapshot_metadata(KEY,encode_metadata({'schema':1,'tick':self.tick,
            'identifier':self.identifier,'state':self.state,'channels':sorted(self.world.runtime.channel_names)}))
        return save_world_snapshot(self.world,path,compress=compress,overwrite=overwrite)

    @classmethod
    def load_snapshot(cls,path,*,max_bytes=DEFAULT_MAX_SNAPSHOT_BYTES,expected_sha256=None):
        world,proof=load_world_snapshot(path,max_bytes=max_bytes,expected_sha256=expected_sha256)
        metadata=dict(world.runtime.snapshot_metadata_entries)
        if KEY not in metadata or GEOMETRY_KEY not in world.recipe.options:raise ValueError("Not a remote-reader operational snapshot")
        v=decode_metadata(metadata[KEY]);g=decode_metadata(world.recipe.options[GEOMETRY_KEY])
        if v['schema']!=1 or v['tick']!=int(world.runtime.current_tick) or v['channels']!=sorted(world.runtime.channel_names):
            raise ValueError("Stale/incompatible remote-reader snapshot")
        result=cls(world,g,v['state'],v['identifier']);result.storage_proof=proof;return result

    def fork(self,*,identifier=None):
        return type(self)(self.world.fork(),self.geometry,self.state,identifier or self.identifier+'.fork')

    def diagnostic_remote_cut(self,*,sham=False):
        """At160, cut/sham the declared incoming bus on an explicit fork only."""
        if self.tick!=160:raise ValueError("Fixed diagnostic route windowT160")
        if type(sham) is not bool:raise TypeError("sham must be boolean")
        edits=[]
        for p in self.geometry['word_bus']['parts'].values():
            q=moved(p['target'],(0,0,1),-1);o=self.world.runtime.observe(native.Coordinate(*q))
            edit=native.ResearchStateEdit();edit.coordinate=native.Coordinate(*q)
            edit.raw=o.raw if sham else 0;edit.label='Explicit remote-reader route sham' if sham else'Explicit remote-reader route cut'
            edits.append(edit)
        child=self.world.diagnostic_fork(edits,True)
        return type(self)(child,self.geometry,self.state,self.identifier+('.sham' if sham else'.cut'))
