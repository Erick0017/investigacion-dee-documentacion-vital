"""Public finite 1..4 participant session over the measured native template.

Routing is an explicit fixed interface contract, not a host search for who knows
an answer. Every experience, request, resource and probe is admitted by Runtime.
"""
from pathlib import Path
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from network_dialogue import prepare, submit
from dialogue import interfaces_for
from common import identity, sha, record, digest, operational, until

KEY='cpc5.extension.network_session.v1'


class NetworkSession:
    def __init__(self,world,spec,state):
        self.world,self.spec,self.state=world,spec,state

    @classmethod
    def create(cls,m=2):
        identity()
        world,spec,state=prepare({'participants':m})
        state['public_session_version']=1
        session=cls(world,spec,state);session.commit();return session

    def actor(self,actor):
        if isinstance(actor,str) and actor.startswith('U') and actor[1:].isdigit():actor=int(actor[1:])
        if type(actor) is not int or not 1<=actor<=len(self.spec['actors']):raise ValueError('Actor U1..Um required')
        return actor-1

    def loop_for(self,actor,kind):
        i=self.actor(actor)
        if kind=='context':return self.spec['loops'][i]
        if kind=='memory':return self.spec['loops'][(i-1)%len(self.spec['actors'])]
        raise ValueError('memory/context required')

    def commit(self):
        self.state['tick']=self.world.runtime.current_tick
        self.world.runtime.set_snapshot_metadata(KEY,json.dumps(self.state,separators=(',',':')))

    def input(self,port,payload,tick,probe=False,origin='USER_INDUCED_PHYSICAL_INPUT'):
        if type(tick) is not int or not self.world.runtime.current_tick<=tick<=512:raise ValueError('Monotone absolute tick0..512 required')
        if port not in {x.name for x in self.world.interfaces}:raise ValueError('Undeclared interface')
        identifier=submit(self.world,self.state,port,payload,tick,probe,origin);self.commit();return identifier

    def experience(self,actor,kind='memory',payloads=(3,9),sign=1,tick=0,backup=True):
        if not isinstance(payloads,(list,tuple)) or len(payloads)!=2 or any(type(v) is not int or not 0<=v<=65535 for v in payloads):raise ValueError('Two uint16 experience loads required')
        if sign not in (-1,1):raise ValueError('Direction sign +/-1 required')
        loop=self.loop_for(actor,kind);base='U2.memory' if kind=='memory' else 'U1.context'
        components=[base]+([base+'.backup'] if backup else [])
        ids=[]
        for component in components:
            ids.append(self.input(loop['prefix']+component+'.cue',payloads[0],tick,False,'OPAQUE_LOCAL_CUE_EXPERIENCE'))
            ids.append(self.input(loop['prefix']+component+('.plus' if sign>0 else '.minus'),payloads[1],tick,False,'CURRENT_LOCAL_DIRECTIONAL_EVENT'))
        return ids

    def relay(self,actor,turn,tick=0):
        if type(turn) is not int or turn not in (1,2):raise ValueError('Relay turn1/2 required')
        loop=self.loop_for(actor,'memory');base=loop['prefix']+'U2.turn'+str(turn)
        return [self.input(base+'.cue',0,tick,False,'ACTUAL_ZERO_LOAD_ROUTING_CUE'),
                self.input(base+'.report',0,tick,False,'ACTUAL_ZERO_LOAD_ROUTING_CONSEQUENCE')]

    def request(self,actor,payload=13,tick=50):
        loop=self.loop_for(actor,'context')
        return self.input(loop['prefix']+'U1.request',payload,tick,True,'HUMAN_INDUCED_NEIGHBOR_REQUEST')

    def resource(self,actor,payload=7,tick=72):
        loop=self.loop_for(actor,'context')
        return [self.input(loop['prefix']+'environment.'+bank,payload,tick,False,'EQUAL_TWO_BANK_ENVIRONMENTAL_OPPORTUNITY') for bank in ('lower','upper')]

    def support(self,actor,kind='memory',payload=5,tick=201):
        loop=self.loop_for(actor,kind);component='U2.memory.backup' if kind=='memory' else 'U1.context.backup'
        return self.input(loop['prefix']+component+'.query',payload,tick,True,'USER_INDUCED_RETAINED_SUPPORT_QUERY')

    def form(self,actor,payload=5,tick=83,probe=False):
        """Fixed two-pulse opaque form, never selecting a bank from a reading."""
        loop=self.loop_for(actor,'context')
        base=loop['prefix']+('form.N0.query.' if probe else 'form.N0.')
        return [self.input(base+bank,payload,tick,probe,
                    'USER_INDUCED_OPAQUE_FORM_QUERY' if probe else 'POST_NATIVE_OPAQUE_FORM_EXPOSURE') for bank in ('lower','upper')]

    def run_until(self,tick):
        if type(tick) is not int or not self.world.runtime.current_tick<=tick<=512:raise ValueError('Monotone finite absolute tick0..512 required')
        until(self.world,tick);self.commit()

    def observe(self):
        loops=[]
        for loop in self.spec['loops']:
            g=loop['geometry']
            loops.append({'loop':loop['index'],'requester':loop['requester'],'responder':loop['responder'],
                          'encounter_sites':{x['id']:record(self.world,x['target']) for x in g['stages']},
                          'banks':{name:record(self.world,q) for name,q in g['banks'].items()},
                          'name_hubs':{name:record(self.world,q) for name,q in g['name_hubs'].items()},
                          'name_query_targets':{name:record(self.world,q) for name,q in g['name_query_targets'].items()},
                          'retained_supports':{x['id']:record(self.world,x['hub']) for x in g['backups']}})
        return {'tick':self.world.runtime.current_tick,'participants':len(self.spec['actors']),'loops':loops,
                'origin':'INSTRUMENTO: exact fields of ENTE native records',
                'scope':'Fixed declared sites. Silence outside the prepared windows is not a memory-loss verdict. No cached or expected answer is decoded.'}

    def save(self,path):
        path=Path(path)
        if path.exists():raise FileExistsError(path)
        path.parent.mkdir(parents=True,exist_ok=True);self.commit();self.world.save_snapshot(str(path))
        return {'file':path.name,'sha256':sha(path),'physical':digest(self.world)}

    @classmethod
    def load(cls,path):
        import dee_thinking as d
        identity();world=d.OrganizationalWorld.load_snapshot(str(path));text=world.runtime.snapshot_metadata(KEY)
        if not text or len(text)>2097152:raise ValueError('No bounded network session metadata')
        state=json.loads(text);spec=state['geometry']
        if state.get('version')!=1 or state.get('public_session_version')!=1 or state['tick']!=world.runtime.current_tick:raise ValueError('Network session/tick mismatch')
        m=len(spec['actors'])
        if m not in (1,2,3,4) or world.runtime.dimension!=67 or world.recipe.placements:raise ValueError('Changed research preparation')
        expected={}
        for loop in spec['loops']:
            for item in interfaces_for(loop['geometry']):expected[loop['prefix']+item.name]=item.channel
        actual={x.name:x.channel for x in world.interfaces}
        if set(expected)!=set(actual):raise ValueError('Changed network interfaces')
        for name,a in actual.items():
            b=expected[name]
            coordinates=lambda x:(x.x,x.y,x.z)
            direction=lambda x:(x.dx,x.dy,x.dz)
            if (coordinates(a.injection_site),direction(a.direction),a.state,a.semantic,a.allow_experience,a.allow_probe)!=(coordinates(b.injection_site),direction(b.direction),b.state,b.semantic,b.allow_experience,b.allow_probe):raise ValueError('Changed interface field')
        for c in state['calls']:
            r=world.runtime.receipt(c['id'])
            if r is None or r.requested_tick!=c['requested_tick'] or list(r.channels)!=[c['port']]:raise ValueError('Lost pending/completed input')
        return cls(world,spec,state)


def operative_without_framework_cache(world):
    """Technical comparison only; preserve and report opaque cache separately."""
    op=operational(world)
    opaque={k:v for k,v in op['metadata'].items() if k.startswith('dee_thinking.organizational.')}
    op['metadata']={k:v for k,v in op['metadata'].items() if not k.startswith('dee_thinking.organizational.')}
    return op,opaque
