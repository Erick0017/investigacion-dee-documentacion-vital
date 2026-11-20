"""Second/final repair of family2, a new T0 preparation.

The lead3 object event crossed the circulating known reference64 and stole
it. Use the original quantity contract lead1 at65, and direct center readers
at69,136,... so circulating nonqualifying products cannot block a remote
reader injection site. No change to v27, no MAIN edits, no learned comparator.
"""
from consulta_conservada_r1 import prepare as previous_prepare
from consulta_conservada import PreservedQuerySession
from consulta_adquirida import move
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata

def prepare(**options):
    recipe,g=previous_prepare(**options)
    for port in recipe.interfaces:
        if port.name in ('object.cue','object.event','local.reader'):
            channel=port.channel;target=g['signatures'][port.name]['target']
            v=g['signatures'][port.name]['direction'];lead=0 if port.name=='local.reader'else 1
            site=move(target,v,-lead);channel.injection_site=d.Coordinate(*site);port.channel=channel
            g['signatures'][port.name]['site']=site;g['signatures'][port.name]['lead']=lead
    g.update(schema='CPC9.query.preserved.v2.r2',repair2='Object lead1/input65 avoids known-reference collision64; direct center readers avoid recurring occupied injection. Final repair, preserve all prior failed preparations.')
    recipe.options={'CPC9.query.preserved.geometry':encode_metadata(g)}
    return recipe,g

class PreservedQueryR2Session(PreservedQuerySession):
    @classmethod
    def create(cls,**options):
        recipe,g=prepare(**options);return cls(d.OrganizationalWorld.create(recipe),g)
    def curriculum(self,local='blank',remote='known',delay=0,local_load=11,remote_load=11):
        if self.tick!=0 or local not in('known','unknown','blank','unpaired')or remote not in('known','unknown','wrong','unpaired'):
            raise ValueError('Fresh bounded history required')
        self.geometry['delay']=delay
        if local!='blank':self.input('local.cue',5,delay)
        if local in('known','unpaired'):self.input('local.event',local_load,delay+int(local=='unpaired'))
        self.input('B.cue',5,10+delay)
        if remote!='unknown':self.input('B.event.plus'if remote=='wrong'else'B.event.minus',remote_load,10+delay+int(remote=='unpaired'))
        self.input('object.cue',0,65+delay);self.input('object.event',0,65+delay)
        for tick in self.geometry['local_query_ticks']:
            self.input('local.reader',7,tick-1+delay,True)
            self.input('answer.turn',0,tick-1+delay)
        for tick in self.geometry['question_ticks']:self.input('gate.opportunity',0,tick-3+delay)
        for turn in self.geometry['turns']:self.input('route.'+turn['id'],0,turn['tick']-3+delay)
