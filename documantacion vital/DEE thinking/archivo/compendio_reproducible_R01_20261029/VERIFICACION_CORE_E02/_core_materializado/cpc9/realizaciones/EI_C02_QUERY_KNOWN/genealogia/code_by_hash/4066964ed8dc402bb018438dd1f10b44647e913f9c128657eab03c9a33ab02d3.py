"""Second query family: acquired local operand survives repeated inhibition.

The native comparator is prepared. Its reference is acquired locally or through
the actual B return. An active zero object is acquired separately, not absence.
"""
from copy import deepcopy
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from consulta_adquirida import QuerySession,move
from integracion.quantity_core import prepare as prepare_quantity

def prepare(origin=(12,8,55)):
    c=list(origin);h=move(c,(-1,1,0));gate=move(c,(2,3,0));b=move(c,(2,1,3))
    recipe,qg=prepare_quantity(center=c,profile='transient',guards='on_path')
    initial=list(recipe.placements)
    for placement in initial:
        if [placement.site.x,placement.site.y,placement.site.z]==move(c,(1,10,0)):
            placement.site=d.Coordinate(*move(c,(10,10,10)))
    ports=[];signatures={}
    def port(name,target,v):
        injection=move(target,v,-3);ch=d.ChannelSpec();ch.name=name;ch.injection_site=d.Coordinate(*injection)
        ch.direction=d.Direction(*v);ch.state=1;ch.semantic=1;ch.allow_experience=True;ch.allow_probe=True
        p=d.InterfaceSpec();p.name=name;p.channel=ch;ports.append(p)
        signatures[name]={'site':injection,'direction':list(v),'target':target}
    for name,target,v in [('local.cue',h,(-1,0,0)),('local.event',h,(1,1,0)),
                         ('local.reader',c,(0,0,1)),('object.cue',qg['object_hub'],(-1,0,0)),
                         ('object.event',qg['object_hub'],(1,1,0)),('gate.opportunity',gate,(0,-1,0)),
                         ('answer.turn',move(c,(2,0,0)),(-1,1,0)),('B.cue',b,(1,0,1)),
                         ('B.event.minus',b,(0,-1,-1)),('B.event.plus',b,(0,1,-1))]:port(name,target,v)
    turns=[('question_turn',move(c,(2,1,0)),77,(0,1,1)),
           ('return_Zup',move(c,(4,-1,5)),82,(-1,1,0)),
           ('return_Xminus',move(c,(4,-1,27)),104,(-1,0,-1)),
           ('return_diagonal',move(c,(-1,-1,27)),109,(1,1,-1)),
           ('return_Zdown',move(c,(-1,0,26)),110,(0,-1,0)),
           ('return_home',move(c,(-1,0,0)),136,(0,1,1))]
    for name,q,t,v in turns:port('route.'+name,q,v)
    if len({p.name for p in ports})!=len(ports):raise ValueError('Duplicate preserved-query port')
    recipe.placements=initial;recipe.interfaces=ports
    g={'schema':'CPC9.query.preserved.v2','N':67,'origin':h,'center':c,'quantity':qg,'gate':gate,'B':b,
       'turns':[{'id':name,'site':q,'tick':t,'direction':list(v)}for name,q,t,v in turns],
       'signatures':signatures,'question_ticks':[75,142,209,276,343,410],
       'local_query_ticks':[70,137,204,271,338,405],
       'resources':{'initial_material':len(initial),'interfaces':len(ports),'basic_buffer_bytes':32*67**3},
       'prepared':'Native comparison with four supports and fixed guards; same offpath zero absorber; active zero object and all identical answer/query opportunities, six prepared zero-load transport turns.',
       'acquired':'Reference only from current local paired experience or a carrier formed through B acquired history80, returned137; no correct knowledge flag input.',
       'scope':'One finite content/routing channel and fixed opportunities, not general curiosity, policy acquisition or source exhaustion detection.'}
    recipe.options={'CPC9.query.preserved.geometry':encode_metadata(g)}
    return recipe,g


class PreservedQuerySession(QuerySession):
    @classmethod
    def create(cls,**options):r,g=prepare(**options);return cls(d.OrganizationalWorld.create(r),g)
    def curriculum(self,local='unknown',remote='known',delay=0,local_load=11,remote_load=11):
        if self.tick!=0 or local not in('known','unknown','blank','unpaired')or remote not in('known','unknown','wrong','unpaired'):
            raise ValueError('Fresh bounded history required')
        self.geometry['delay']=delay
        if local!='blank':self.input('local.cue',5,delay)
        if local in('known','unpaired'):self.input('local.event',local_load,delay+int(local=='unpaired'))
        self.input('B.cue',5,10+delay)
        if remote!='unknown':self.input('B.event.plus'if remote=='wrong'else'B.event.minus',remote_load,10+delay+int(remote=='unpaired'))
        # The right-hand operand is a genuine active zero material record.
        # Object channel lead here is explicitly three, hence input63 ->hub66.
        self.input('object.cue',0,63+delay);self.input('object.event',0,63+delay)
        for tick in self.geometry['local_query_ticks']:
            # Native gradient uses a reader in-place; declared lead3 channel
            # reaches the center at the pre-state, then gradient evolves.
            self.input('local.reader',7,tick-4+delay,True)
            self.input('answer.turn',0,tick-1+delay)
        for tick in self.geometry['question_ticks']:self.input('gate.opportunity',0,tick-3+delay)
        for turn in self.geometry['turns']:self.input('route.'+turn['id'],0,turn['tick']-3+delay)
    def view(self):
        r=super().view();q=self.geometry['quantity']
        r['quantity']={key:self.observe(q[key])for key in('center','reference_hub','reference_site','object_hub','object_site')}
        return r
