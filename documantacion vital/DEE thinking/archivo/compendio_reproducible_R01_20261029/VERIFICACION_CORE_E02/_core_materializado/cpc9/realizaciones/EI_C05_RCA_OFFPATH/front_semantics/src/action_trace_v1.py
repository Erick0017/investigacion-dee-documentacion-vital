"""Prepared native emitter leaves a local action trace; no host fan-out.

The command is an external opportunity, not an endogenous policy.  A supported
moving input both emits through empty-destination reducer and leaves stationary
material by the ordinary occupied-site rule. Both actors have the same ports,
supports and probes. A shared physical consequence is normalized in a common
supported site. These facts test access to causal origin, not linguistic deixis.
"""
from dee_thinking import _native as d
from integracion.quantity_core import QuantitySession, move


def prepare(*, command_load=11, translation=(0,0,0), trace_support='intact'):
    if trace_support not in ('intact','off_path'):
        raise ValueError('Frozen matched trace support condition')
    n=67
    def tr(q): return [(q[i]+translation[i])%n for i in range(3)]
    sites={'A':tr((15,30,30)), 'B':tr((35,30,30)), 'C':tr((25,36,30))}
    placements=[]; interfaces=[]; occupied=set()
    def put(q,load,v,sem,role):
        q=tuple(q)
        if q in occupied: raise ValueError('Initial overlap '+str(q))
        occupied.add(q);p=d.InitialPlacement();p.site=d.Coordinate(*q)
        p.raw=d.pack_record(1,load,*v,sem);p.clock=0;p.role=role;placements.append(p)
    def port(name,q,v):
        ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*q)
        ch.direction=d.Direction(*v);ch.state=1;ch.semantic=1
        ch.allow_probe=True;ch.allow_experience=True
        p=d.InterfaceSpec();p.name=name;p.channel=ch;interfaces.append(p)
    support_vectors=[(-1,-1,-1),(-1,-1,0),(-1,-1,1),(0,-1,-1),(0,-1,0),(0,-1,1),(1,-1,0)]
    for actor,origin in sites.items():
        # The common consequence uses the opposite half-plane so incoming
        # diagonals remain open while outgoing products meet existing supports.
        for v in support_vectors:
            vv=(v[0],-v[1] if actor=='C' else v[1],v[2])
            q=move(origin,vv)
            if actor!='C' and trace_support=='off_path':q=move(q,(0,-9,0))
            put(q,0,(0,0,0),4,'Prepared zero trace/feedback support '+actor)
        put(move(origin,(1,0,2)),0,(0,0,0),4,'Prepared extra reader support '+actor)
        port('trace.reader.'+actor,move(origin,(0,0,1)),(1,0,0))
        if actor!='C':
            v=(1,0,0) if actor=='A' else (-1,0,0)
            port('action.command.'+actor,origin,v)
            turn=move(origin,v,4)
            put(move(turn,(0,1,0),-4),0,(0,1,0),1,'Prepared symmetric common-world turn '+actor)
    recipe=d.OrganizationRecipe.research(n,placements,0)
    recipe.interfaces=interfaces;recipe.execution=d.TickOptions(d.Backend.LAZY,1)
    geometry={'schema':'CPC9.action_trace.v1','N':n,'sites':sites,'readers':{k:move(v,(0,0,1)) for k,v in sites.items()},
              'command_load':command_load,'translation':list(translation),'trace_support':trace_support,
              'initial_material':len(placements),'interfaces':len(interfaces),
              'prepared':'Symmetric emitters, occupied-site supports, two turns, common feedback stabilization and all readers.',
              'acquired':'A single commanded carrier creates local stationary trace and outgoing material natively; action source is not copied into another port.',
              'scope':'Externally requested action and finite causal-origin trace. Neither initiative, self-consciousness nor YO/TU is established.'}
    return recipe,geometry


class ActionTraceSession(QuantitySession):
    @classmethod
    def create(cls,**kwargs):
        r,g=prepare(**kwargs);return cls(d.OrganizationalWorld.create(r),g)
    def curriculum(self,actor='A',omit=False):
        if actor not in ('A','B') or self.tick!=0:raise ValueError('Fresh symmetric two-actor domain')
        if not omit:self.input('action.command.'+actor,self.geometry['command_load'],0)
        for tick in (15,30):
            for key in ('A','B','C'):self.input('trace.reader.'+key,7,tick,True)
    def capture(self):
        return {'tick':self.tick,'sites':{k:self.observe(v) for k,v in self.geometry['sites'].items()},
                'readers':{k:self.observe(v) for k,v in self.geometry['readers'].items()},
                'Moore27':{k:[self.observe(move(v,(x,y,z))) for x in (-1,0,1) for y in (-1,0,1) for z in (-1,0,1)] for k,v in self.geometry['sites'].items()}}
