"""Conserving query candidate: native return stored in the proven Y orbit.

The previous XYZ final turn made an XY record that did not survive. This new
T0 transport preparation returns B along -X, then a fixed zero XY cue makes
the acquired Y operand at137. No answer-reading callback selects a route.
"""
from consulta_conservada_r2 import prepare as previous_prepare,PreservedQueryR2Session
from consulta_adquirida import move
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata

def prepare(**options):
    recipe,g=previous_prepare(**options);c=g['center']
    ports=[p for p in recipe.interfaces if not p.name.startswith('route.')]
    turns=[('question_turn',move(c,(2,1,0)),77,(0,1,1),3),
           ('return_Zup',move(c,(4,-1,5)),82,(-1,1,0),3),
           ('return_Yup',move(c,(4,-1,27)),104,(0,1,-1),3),
           ('return_diagonal',move(c,(4,1,27)),106,(-1,-1,-1),3),
           ('return_Zdown',move(c,(3,1,26)),107,(1,0,0),3),
           ('return_Xminus',move(c,(3,1,0)),133,(-1,0,1),3),
           ('return_home',g['origin'],137,(1,1,0),1)]
    g['signatures']={k:v for k,v in g['signatures'].items()if not k.startswith('route.')}
    for name,target,tick,vector,lead in turns:
        channel=d.ChannelSpec();channel.name='route.'+name
        site=move(target,vector,-lead);channel.injection_site=d.Coordinate(*site)
        channel.direction=d.Direction(*vector);channel.state=1;channel.semantic=1
        channel.allow_probe=True;channel.allow_experience=True
        p=d.InterfaceSpec();p.name=channel.name;p.channel=channel;ports.append(p)
        g['signatures'][p.name]={'site':site,'direction':list(vector),'target':target,'lead':lead}
    recipe.interfaces=ports
    g['turns']=[{'id':n,'site':q,'tick':t,'direction':list(v),'lead':lead}for n,q,t,v,lead in turns]
    g.update(schema='CPC9.query.reference_Y.v3',
        prepared='Seven native quantity supports, fixed gradient and counterturns. Final zero XY cue is identical even without B; only actual B content can provide a nonzero acquired Y reference.',
        acquired='Local paired reference3 or actual B-derived reference137. The prepared comparator can use the preserved operand repeatedly; no general decision-policy learning asserted.',
        resources={**g['resources'],'interfaces':len(ports)})
    recipe.options={'CPC9.query.preserved.geometry':encode_metadata(g)}
    return recipe,g

class ReferenceQuerySession(PreservedQueryR2Session):
    @classmethod
    def create(cls,**options):
        recipe,g=prepare(**options);return cls(d.OrganizationalWorld.create(recipe),g)
    def curriculum(self,local='blank',remote='known',delay=0,local_load=11,remote_load=11):
        if self.tick!=0 or local not in('known','unknown','blank','unpaired')or remote not in('known','unknown','wrong','unpaired'):
            raise ValueError('Explicit fresh history required')
        self.geometry['delay']=delay
        if local!='blank':self.input('local.cue',5,delay)
        if local in('known','unpaired'):self.input('local.event',local_load,delay+int(local=='unpaired'))
        self.input('B.cue',5,10+delay)
        if remote!='unknown':self.input('B.event.plus'if remote=='wrong'else'B.event.minus',remote_load,10+delay+int(remote=='unpaired'))
        self.input('object.cue',0,65+delay);self.input('object.event',0,65+delay)
        for tick in self.geometry['local_query_ticks']:
            self.input('local.reader',7,tick-1+delay,True);self.input('answer.turn',0,tick-1+delay)
        for tick in self.geometry['question_ticks']:self.input('gate.opportunity',0,tick-3+delay)
        for turn in self.geometry['turns']:self.input('route.'+turn['id'],0,turn['tick']-turn['lead']+delay)
