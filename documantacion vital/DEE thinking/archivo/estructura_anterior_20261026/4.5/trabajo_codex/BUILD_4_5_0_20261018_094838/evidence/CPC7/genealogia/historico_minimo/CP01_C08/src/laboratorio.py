"""Shared instruments. All transformations attributed to DEE use its native API."""
from array import array
import hashlib
import json
from pathlib import Path
import time
import dee_thinking as d


def coord(q):return [q.x,q.y,q.z]


def reading(o):
    r=o.record
    return {'tick':o.tick,'coordinate':coord(o.coordinate),'RAW':o.raw,'clock':o.clock,'state':r.state,'semantic':r.semantic,'s_reg':r.s_reg,'direction':[r.dx,r.dy,r.dz],
            'active':r.state>0 and r.semantic!=5}


def receipt(r):return {'id':r.id,'status':str(r.status),'requested_tick':r.requested_tick,'effective_tick':r.effective_tick,'channels':list(r.channels),'reason':r.reason}


def body_panel(w):
    f=w.view('body').observe()
    return {'tick':w.runtime.current_tick,'delta':f.delta,'axis_projection':f.axis_projection,'centers_available':f.centers_available,'supports_intact':f.supports_intact,
            'reader_available':f.reader_available,'observations':{k:reading(v) for k,v in f.observations.items()}}


def physical(w):
    r=w.runtime if hasattr(w,'runtime') else w
    return {'tick':r.current_tick,'dimension':r.dimension,'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),
            'clock_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}


def make_body(origin=(15,15,15),recipe='relational',event_state=1):
    w=d.create_organization(recipe,history=d.BasalHistory.H0,origin=origin)
    spec=w.view('body').spec
    for name,center,offset,direction in [('E_A',spec.a,(0,-1,0),(0,0,-1)),('E_B',spec.b,(0,1,0),(0,0,1))]:
        i=d.InterfaceSpec();i.name=name;ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*[(c+v)%w.runtime.dimension for c,v in zip(coord(center),offset)]);ch.state=event_state;ch.direction=d.Direction(*direction);ch.semantic=1;i.channel=ch;w.declare_interface(i)
    return w


def body_experience(w,events,start=None):
    begin=w.runtime.current_tick if start is None else start;ids=[]
    for j,key in enumerate(events):ids.append(w.submit('E_'+key,0,begin+j).id)
    w.run_until(begin+len(events))
    return [receipt(w.runtime.receipt(i)) for i in ids]


def body_probe(w,payload=7,in_fork=True):
    f=w.fork() if in_fork else w;before=body_panel(f);r=f.probe('body.common_query',payload,f.runtime.current_tick);f.advance(3)
    return {'before':before,'after':body_panel(f),'receipt':receipt(f.runtime.receipt(r.id)),'response':reading(f.observe('body','comparator')),'modality':'PHYSICAL_PROBE_IN_FORK' if in_fork else 'PHYSICAL_PROBE_ON_MAIN'},f


def learned_mobile(teachers=(7,11),cue=5,paired=True,origin=(0,0,0),online=True):
    w=d.create_organization('mobile_pair',origin=origin);ids=[]
    for j,ref in enumerate(teachers):
        ids.append(w.submit(f'l{j}.cue',cue,0).id)
        if paired:ids.append(w.submit(f'l{j}.teacher',ref,0).id)
        else:ids.append(w.submit(f'l{j}.teacher',ref,1).id)
    if online:w.advance();w.run_until(6)
    else:w.run_until(6)
    return w,[receipt(w.runtime.receipt(i)) for i in ids]


def mobile_query(w,value,in_fork=True,protocol='query'):
    f=w.fork() if in_fork else w;before=physical(f);f.start_mobile_sequence(protocol,[value],f.runtime.current_tick);f.advance(5)
    step=f.protocols[-1].steps[0]
    outputs=[reading(x) for x in step.captured]
    return {'before':before,'after':physical(f),'input':value,'responses':outputs,'receipt_ids':list(step.receipt_ids),'receipts':[receipt(f.runtime.receipt(i)) for i in step.receipt_ids],
            'query_consumes_main':not in_fork,'modality':'PHYSICAL_PROBE_IN_FORK' if in_fork else 'PHYSICAL_PROBE_ON_MAIN'},f


def edit_fork(w,site,raw,label):
    e=d.ResearchStateEdit();e.coordinate=site;e.raw=raw;e.label=label
    return w.diagnostic_fork([e],True)


class CaseEvidence:
    def __init__(self,root,case,config):
        self.root=Path(root).resolve();self.id=case;self.folder=self.root/'casos'/case;self.folder.mkdir(parents=True,exist_ok=True);self.config=config;self.started=time.monotonic();self.snapshots=[]
        self.json('CONFIG.json',config)
    def json(self,name,obj):
        p=self.folder/name;p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp');tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding='utf-8');tmp.replace(p)
    def snapshot(self,w,name):
        p=self.folder/(name+'.deetsnap');version=1
        while p.exists():version+=1;p=self.folder/(name+'_attempt'+str(version)+'.deetsnap')
        w.save_snapshot(str(p));item={'name':str(p.relative_to(self.root)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'state':physical(w)};self.snapshots.append(item);return item
    def finish(self,measurements,status='EJECUTADO',limits=None):
        result={'case':self.id,'configuration':self.config,'status':status,'duration_seconds':time.monotonic()-self.started,'measurements':measurements,'checkpoints':self.snapshots,'limits':limits or [],'runtime_version':d.__version__,'kernel':d.kernel_identity()}
        self.json('RESULTADOS.json',result);return result
