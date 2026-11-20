"""Coordinate-free finite public sessions. No target/result files are read."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import identity,interface,record,receipt,digest,operational,put,sha,until
from order_stream import prepare as order_prepare
from architectures import geometry as arch_geometry
from dialogue import DialogueSession

KEY='cpc5.extension.public.session.v1'

class FiniteSession:
    def __init__(self,world,spec,kind,calls=None):self.world,self.spec,self.kind,self.calls=world,spec,kind,list(calls or [])
    def submit(self,port,payload,tick,probe=False):
        if type(payload)is not int or not 0<=payload<=65535:raise ValueError('Carga uint16 requerida')
        if type(tick)is not int or tick<self.world.runtime.current_tick:raise ValueError('Tick absoluto actual o futuro requerido')
        r=(self.world.probe if probe else self.world.submit)(port,payload,tick)
        self.calls.append({'id':int(r.id),'port':port,'payload':payload,'tick':tick,'probe':probe})
        return receipt(self.world,r.id)
    def run_until(self,tick):until(self.world,tick)
    def observe(self):
        if self.kind=='orden':
            a,b=record(self.world,self.spec['A']),record(self.world,self.spec['B'])
            return {'tick':self.world.runtime.current_tick,'A':a,'B':b,'delta':a['s_reg']-b['s_reg'] if a['active'] and b['active'] else None,
                    'named_output':{k:record(self.world,q) for k,q in self.spec['query_sites'].items()},
                    'context':{k:record(self.world,q) for k,q in self.spec['context_sites'].items()}}
        return {'tick':self.world.runtime.current_tick,'groups':self.spec['groups'],
                'stage_meetings':{str(s['index']):record(self.world,s['meeting']) for s in self.spec['stages']},
                'consequence':record(self.world,self.spec['consequence_site_round1'])}
    def save(self,path):
        path=Path(path)
        if path.exists():raise FileExistsError(path)
        path.parent.mkdir(parents=True,exist_ok=True)
        self.world.runtime.set_snapshot_metadata(KEY,json.dumps({'schema':1,'kind':self.kind,'geometry':self.spec,'calls':self.calls,'tick':self.world.runtime.current_tick},separators=(',',':')))
        self.world.save_snapshot(str(path));return {'file':path.name,'sha256':sha(path),'physical':digest(self.world)}
    @classmethod
    def create_order(cls):
        identity();w,s=order_prepare({})
        # Preserve the public v1 descriptor when optional diagnostic access is
        # absent; this does not remove any physical field or interface.
        if s.get('alternate_sites')=={}:s.pop('alternate_sites')
        return cls(w,s,'orden')
    @classmethod
    def create_architecture(cls,groups):
        import dee_thinking as d
        identity();s,ports=arch_geometry({'groups':groups})
        recipe=d.OrganizationRecipe.research(s['N'],[],0);recipe.interfaces=ports;recipe.execution=d.TickOptions(d.Backend.LAZY,1)
        return cls(d.OrganizationalWorld.create(recipe),s,'A'+str(groups))
    @classmethod
    def load(cls,path):
        import dee_thinking as d
        identity();w=d.OrganizationalWorld.load_snapshot(str(path));text=w.runtime.snapshot_metadata(KEY)
        if not text:
            from network_session import NetworkSession,KEY as NETWORK_KEY
            if w.runtime.snapshot_metadata(NETWORK_KEY):return NetworkSession.load(path)
            return DialogueSession.load(path)
        value=json.loads(text)
        if value['schema']!=1 or value['tick']!=w.runtime.current_tick:raise ValueError('Metadata inconsistente')
        kind=value['kind'];spec=value['geometry']
        if kind not in ('orden','A1','A2','A3','A4') or spec['N']!=w.runtime.dimension:raise ValueError('Dominio desconocido')
        for call in value['calls']:
            r=w.runtime.receipt(call['id'])
            if r is None or r.requested_tick!=call['tick'] or list(r.channels)!=[call['port']]:raise ValueError('Recibo operativo perdido')
        return cls(w,spec,kind,value['calls'])

def kind_of(session):
    if isinstance(session,FiniteSession):return session.kind
    from network_session import NetworkSession
    return 'red' if isinstance(session,NetworkSession) else 'dialogo'
