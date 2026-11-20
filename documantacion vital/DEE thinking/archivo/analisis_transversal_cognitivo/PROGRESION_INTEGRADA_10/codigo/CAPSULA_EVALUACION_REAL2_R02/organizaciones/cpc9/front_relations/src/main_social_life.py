"""Late external receptor introduction to an exact living E1 continuation.

No constructor is called and no matter/RAW/clock is inserted on registration.
Interfaces and supply schedules are instruments, not claimed native growth.
"""
from pathlib import Path
from copy import deepcopy
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from dee_thinking import _native as d
from vida_integral import IntegralLifeSession
from integracion.relational_pair import move


def receiver_interfaces(geometry):
    ports=[];banks=[]
    def port(name,site,direction):
        c=d.ChannelSpec();c.name=name;c.injection_site=d.Coordinate(*site)
        c.direction=d.Direction(*direction);c.state=1;c.semantic=1;c.allow_experience=True;c.allow_probe=True
        spec=d.InterfaceSpec();spec.name=name;spec.channel=c;ports.append(spec)
        return {"name":name,"site":site,"direction":list(direction),"state":1,"semantic":1}
    for old in geometry['tiled_order']['surfaces']:
        hub=move(old['effect'],(0,-1,1),6);effect=move(hub,(0,1,1),6);label=old['id']
        banks.append({'id':label,'source_effect':old['effect'],'source_port':old['use_port'],'hub':hub,'effect':effect,
            'cue':port('late_E2.cue.'+label,move(hub,(0,1,0),-3),(0,1,0)),
            'probe':port('late_E2.probe.'+label,move(hub,(0,1,0),-3),(0,1,0)),
            'use':port('late_E2.use.'+label,move(effect,(0,0,-1),-3),(0,0,-1))})
    return ports,{'schema':'CPC9.E1.late_E2.v1','introduced_at_tick':1220,'introduction':'EXTERNAL_INSTRUMENTAL_INTERFACE_EXTENSION; no native architectural growth claimed',
        'banks':banks,'resources':{'new_interfaces':18,'new_initial_material':0},'ticks':{'E1_read':1292,'E2_record':1298,'E2_query':1365,'E2_use':1371}}


class MainSocialSession(IntegralLifeSession):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.state.setdefault('late_E2_observations',[])
    def view(self):
        result=super().view()
        if'late_E2'in self.geometry:result['late_E2']=[{'id':item['id'],'hub':self.observe(item['hub']),'effect':self.observe(item['effect'])}for item in self.geometry['late_E2']['banks']]
        return result
    def capture_E2(self,stage):
        rows=[]
        for item in self.geometry['late_E2']['banks']:
            site=item['source_effect']if stage.endswith('source')else item['effect']if stage.endswith('use')else item['hub']
            rows.append({'id':item['id'],'physical':self.observe(site),'Moore27':[self.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
        self.state['late_E2_observations'].append({'tick':self.tick,'stage':stage,'banks':rows})
    def run_until(self,tick):
        stages={1291:'pre_source',1292:'source',1297:'pre_record',1298:'record',1364:'pre_read',1365:'read',1370:'pre_use',1371:'use'}
        for value in sorted(t for t in stages if self.tick<t<=tick):super().run_until(value);self.capture_E2(stages[value])
        return super().run_until(tick)


def schedule(session,*,receiver_cue=True):
    g=session.geometry['late_E2']
    for item in g['banks']:
        session.input(item['source_port'],7,1289,'probe','PREDECLARED_IDENTICAL_OLD_E1_ORDER_READ_ALL_BANKS')
        if receiver_cue:session.input(item['cue']['name'],5,1295,origin='EXTERNAL_E2_POST_ARRIVAL_IDENTICAL_CUES')
        session.input(item['probe']['name'],7,1362,'probe','LATER_E2_ONLY_SIGNAL_QUERY_ALL_BANKS')
        session.input(item['use']['name'],11,1368,origin='E2_CURRENT_USE_RESOURCE_ALL_BANKS')
    for tick in(1284,1351):
        for name in sorted({item['plus_port']for item in session.geometry['cpc9_life']['count_repeated_readers']}):
            session.input(name,7,tick,'probe','INSTRUMENTAL_RENEWAL_DECLARED_PLUS_PROBE_NO_RAW_CLOCK_EDIT')
    for tick in(1283,1350):
        for item in session.geometry['joint_names'].values():session.input(item['query_port'],17,tick,'probe','OLD_JOINT_NO_RETEACHING')
    for tick in(1277,1344):session.two_memory.input('quantity.reader',7,tick,True)
