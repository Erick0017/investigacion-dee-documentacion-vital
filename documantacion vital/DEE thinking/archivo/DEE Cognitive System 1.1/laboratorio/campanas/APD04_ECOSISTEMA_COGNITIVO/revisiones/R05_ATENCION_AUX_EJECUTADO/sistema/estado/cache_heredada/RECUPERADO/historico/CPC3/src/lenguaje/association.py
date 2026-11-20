"""Asociación relacional y composición DEE por API pública 3.5.

Las formas textuales sólo seleccionan puertos físicos estables. El producto
cue+teacher lo forma v27 por encuentro, no un diccionario del interlocutor.
Esta familia realiza transformaciones aditivas, no una semántica arbitraria.
"""
import hashlib
import json
from array import array
from pathlib import Path
import dee_thinking as d


def observation(o):
    r=o.record
    return {'tick':o.tick,'site':[o.coordinate.x,o.coordinate.y,o.coordinate.z],
            'RAW':o.raw,'clock':o.clock,'state':r.state,'semantic':r.semantic,
            's_reg':r.s_reg,'direction':[r.dx,r.dy,r.dz],
            'active':r.state>0 and r.semantic!=5}


def receipt(r):
    return {'id':r.id,'status':str(r.status),'requested_tick':r.requested_tick,
            'effective_tick':r.effective_tick,'channels':list(r.channels),'reason':r.reason}


def physical(w):
    return {'tick':w.runtime.current_tick,
            'RAW_sha256':hashlib.sha256(array('Q',w.runtime.raw_copy()).tobytes()).hexdigest(),
            'clock_sha256':hashlib.sha256(array('Q',w.runtime.clock_copy()).tobytes()).hexdigest()}


def fixed_decode(o):
    return o['s_reg'] if o['active'] else None


class AssociationSession:
    """Dos señales de ruta fija, relaciones adquiridas y consulta consumible."""
    def __init__(self,world,forms):self.world=world;self.forms=dict(forms);self.log=[]
    @classmethod
    def create(cls,forms=None,translation=(0,0,0)):
        forms=forms or {'tavu':0,'neko':1}
        if sorted(forms.values())!=[0,1]:raise ValueError('Se requieren dos formas con dos IDs físicos distintos')
        return cls(d.create_organization('mobile_pair',origin=translation),forms)
    def train(self,teachers=(7,11),cue=5,mode='paired'):
        if self.world.runtime.current_tick!=0:raise ValueError('Esta receta de adquisición requiere frontera inicial cero; no reconstruye individuos')
        if mode not in ('paired','omitted','unpaired'):raise ValueError('Tratamiento no admitido')
        receipts=[]
        for j,teacher in enumerate(teachers):
            if mode!='omitted':
                receipts.append(self.world.submit(f'l{j}.cue',cue,0).id)
                receipts.append(self.world.submit(f'l{j}.teacher',teacher,1 if mode=='unpaired' else 0).id)
        self.world.run_until(6)
        item={'operation':'acquisition','modality':'EXPERIENCE_PROTOCOL','mode':mode,
              'cue':cue,'teachers':list(teachers),'receipts':[receipt(self.world.runtime.receipt(i)) for i in receipts],
              'physical':physical(self.world),'meaning_scope':'fixed route form; cue/teacher relation is acquired by native collision'}
        self.log.append(item);return item
    def query(self,form,payload=13):
        if form not in self.forms:raise ValueError('Forma no registrada; no se inventa una asociación')
        j=self.forms[form];t=self.world.runtime.current_tick
        r=self.world.probe(f'q{j}.query',payload,t)
        self.world.advance(5)
        o=observation(self.world.observe(f'q{j}','response'))
        item={'operation':'query','modality':'PHYSICAL_PROBE_ON_MAIN','form':form,'stable_port_id':j,
              'query_payload':payload,'input_tick':t,'physical_output':o,
              'decoded':fixed_decode(o),'receipt':receipt(self.world.runtime.receipt(r.id)),
              'consumable_query':True,'physical':physical(self.world)}
        self.log.append(item);return item
    def query_simultaneous(self,payload=13):
        t=self.world.runtime.current_tick;ids=[]
        for j in range(2):ids.append(self.world.probe(f'q{j}.query',payload,t).id)
        self.world.advance(5)
        outputs={form:observation(self.world.observe(f'q{j}','response')) for form,j in self.forms.items()}
        result={'operation':'query_panel','modality':'PHYSICAL_PROBE_ON_MAIN','input_tick':t,'query_payload':payload,
                'outputs':outputs,'decoded':{f:fixed_decode(o) for f,o in outputs.items()},
                'receipts':[receipt(self.world.runtime.receipt(i)) for i in ids], 'physical':physical(self.world)}
        self.log.append(result);return result
    def start_sequence(self,payloads):
        self.world.start_mobile_sequence('language_sequence',list(payloads))
        self.world.run_until(6+5*len(payloads))
        p=self.world.protocols[-1]
        item={'operation':'sequential_physical_probes','modality':'PHYSICAL_PROBE_ON_MAIN',
              'steps':[{'input':s.input,'input_tick':s.input_tick,'read_tick':s.read_tick,
                        'physical':[observation(o) for o in s.captured]} for s in p.steps],
              'consequence':'queries can modify the mobile relation; later outputs are not cached first answers',
              'physical':physical(self.world)}
        self.log.append(item);return item
    def save(self,path):
        data={'schema':1,'forms':self.forms,'log':self.log,'scope':'external forms only; no answer dictionary'}
        self.world.runtime.set_snapshot_metadata('cpc3.language.association',json.dumps(data,separators=(',',':')))
        self.world.save_snapshot(str(path))
    @classmethod
    def load(cls,path):
        w=d.OrganizationalWorld.load_snapshot(str(path));data=json.loads(w.runtime.snapshot_metadata('cpc3.language.association'))
        if data['schema']!=1:raise ValueError('Formato de asociación desconocido')
        s=cls(w,data['forms']);s.log=data['log'];return s


def composition_world(depth=2,translation=(0,0,0)):
    """Published empty cascade plus declared online experience interfaces."""
    w=d.create_organization('cascade',depth=depth,origin=translation,source_absent=1)
    n=w.runtime.dimension
    for j in range(depth):
        hub=w.view(f'stage{j}').spec.ports['hub']
        for role,offset,dr in [('cue',(3,0,0),(-1,0,0)),('teacher',(-3,-3,0),(1,1,0))]:
            i=d.InterfaceSpec();i.name=f'experience.{j}.{role}';c=d.ChannelSpec();c.name=i.name
            c.injection_site=d.Coordinate(*[(a+b)%n for a,b in zip((hub.x,hub.y,hub.z),offset)])
            c.direction=d.Direction(*dr);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=False;i.channel=c
            w.declare_interface(i)
    return w


def experience_composition(w,pairs,omit=None):
    ids=[]
    for j,(cue,teacher) in enumerate(pairs):
        if j==omit:continue
        ids.extend([w.submit(f'experience.{j}.cue',cue,0).id,w.submit(f'experience.{j}.teacher',teacher,0).id])
    w.run_until(6)
    return [receipt(w.runtime.receipt(i)) for i in ids]


def query_composition(w,payload):
    depth=len(w.organization_ids);t=w.runtime.current_tick;r=w.probe('query',payload,t)
    out=[]
    for j in range(depth):
        w.run_until(t+5*(j+1));out.append(observation(w.observe(f'stage{j}','response')))
    return {'modality':'PHYSICAL_PROBE_ON_MAIN','query':payload,'input_tick':t,'outputs':out,
            'decoded':[fixed_decode(o) for o in out],'receipt':receipt(w.runtime.receipt(r.id)),
            'physical':physical(w),'scope':'native additive composition of learned relations, not grammar acquisition'}
