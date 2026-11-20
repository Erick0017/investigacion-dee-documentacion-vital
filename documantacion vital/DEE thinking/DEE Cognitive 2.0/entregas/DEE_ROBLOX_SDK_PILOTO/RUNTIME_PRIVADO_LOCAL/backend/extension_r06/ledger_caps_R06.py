"""Capability reservations in the SAME R06 ledger, never fake SDK cycles."""
from pathlib import Path
import importlib.util
import json
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
_spec=importlib.util.spec_from_file_location('_sdk_r06_original_ledger',ROOT/'backend/r06/ledger_sdk.py')
_base=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_base)
sys.path.insert(0,str(ROOT/'backend/r06'))
from sdk_common import atomic
MODE='eci01-pi10-sdk-capability-r06'

class TickLedger(_base.TickLedger):
    def _scope(self):
        instance=self.life.removeprefix(_base.PREFIX)
        path=ROOT/'estado_demo/instancias'/instance/'sistema/capacidades/SDK_CAPABILITIES_SCOPE_R06.json'
        value=json.loads(path.read_text('utf8'))
        if value['lifeId']!=self.life or value['allowedLifeIds']!=[self.life] or value['sealed'] is not True:
            raise ValueError('Exact per-life capabilities authorization')
        return value
    def begin(self,life,identifier,mode):
        if mode!=MODE:return super().begin(life,identifier,mode)
        with self.lock():
            c=self._scope();value=self.read()
            if life!=self.life or value['intents'] or time.time()>=c['lastNewUtcEpoch']:
                raise RuntimeError('Exact serial capabilities admission before cutoff')
            world=value['worlds'][life]
            if (world['reserved'] or world['cycles']<2 or world.get('capability_events',0)>=c['maxEvents']):
                raise RuntimeError('Existing SDK episode/event or exhausted capability horizon')
            if value['validation_consumed']+sum(w['reserved'] for w in value['worlds'].values())+4096>40000:
                raise RuntimeError('Shared 40000 tick reservation cap')
            world['reserved']=4096
            value['intents'][life]={'life':life,'id':identifier,'mode':mode,'utc_epoch':time.time(),
                                   'capability_event':True,'not_new_sdk_cycle':True}
            atomic(self.path,value)
    def finish(self,life,identifier,before,after,mode):
        if mode!=MODE:return super().finish(life,identifier,before,after,mode)
        with self.lock():
            value=self.read();c=self._scope();intent=value['intents'].get(life);world=value['worlds'][life]
            if intent is None or (intent['life'],intent['id'],intent['mode'])!=(life,identifier,mode):
                raise RuntimeError('Exact original capability intent remains required')
            ticks=after-before
            if type(ticks) is not int or not 0<=ticks<=world['reserved']:
                raise RuntimeError('Capability ticks exceed reservation; intent preserved')
            value['consumed']+=ticks;value['validation_consumed']+=ticks
            world['consumed']+=ticks;world['validation_consumed']+=ticks;world['reserved']=0
            world['capability_events']=world.get('capability_events',0)+1
            world['last_completed']={**intent,'before_tick':before,'after_tick':after,'actual_ticks':ticks}
            value['last_completed']=world['last_completed'];del value['intents'][life]
            if value['validation_consumed']>40000 or world['capability_events']>c['maxEvents']:
                raise RuntimeError('Finite cap exceeded; no silent settlement')
            # cycles and validation_cycles remain EXACTLY unchanged.
            atomic(self.path,value)
