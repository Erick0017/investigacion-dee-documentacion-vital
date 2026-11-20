"""New finite SDK accounting, not a reset of the inherited physical history."""
from pathlib import Path
from contextlib import contextmanager
import json
import os
import re
import time
import hashlib

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_'
SCHEMA = 'DEE.Roblox.SDK.budget.0.1.0'
MODES = {'eci01-rbx01-decision','eci01-rbx01-query-sensor','eci01-rbx01-function','eci01-rbx01-feedback','eci01-rbx01-estado'}

def write(path, value):
    tmp = path.with_name(path.name + '.WRITING')
    with tmp.open('x', encoding='utf8') as out:
        json.dump(value, out, sort_keys=True, ensure_ascii=False, indent=2); out.write('\n'); out.flush(); os.fsync(out.fileno())
    os.replace(tmp, path)

def role_for(life):
    if re.fullmatch(re.escape(PREFIX) + r'SDK_(DEMO|MAP5)_[0-9A-F]{16}', life): return 'pilot'
    if re.fullmatch(re.escape(PREFIX) + r'SDK_(OC|OA)_[0-9A-F]{16}', life): return 'control'
    raise ValueError('PRIVATE_SDK_DIAGNOSTIC_LIFE_ONLY')

def initialize(path, window):
    path = Path(path)
    if path.exists(): raise FileExistsError('A ledger is never reset')
    path.parent.mkdir(parents=True, exist_ok=True)
    write(path, {'schema': SCHEMA, 'limit': 40000, 'max_worlds': 6, 'sdk_global_cycles': 3,
                 'consumed': 0, 'validation_consumed': 0, 'worlds': {}, 'intents': {}, 'leases': {}, 'lease_history': [],
                 'last_new_episode_epoch': window['lastNewUtcEpoch'], 'cutoff_epoch': window['hardFinishUtcEpoch'],
                 'source_tick_per_new_life': 991187, 'physical_history_not_reset': True})

class TickLedger:
    def __init__(self, path, life, max_cycles, role=None):
        self.path = Path(path).resolve(); self.life = life; self.role = role_for(life); self.max_cycles = max_cycles
        if self.path != ROOT / 'estado_demo/LEDGER_SDK.json': raise ValueError('ONE_PRIVATE_SDK_LEDGER')
        if role not in (None, self.role) or max_cycles != {'pilot': 3, 'control': 6}[self.role]:
            raise ValueError('EXPLICIT_ROLE_CAP')
        if not self.path.exists(): raise RuntimeError('EXPLICIT_NEW_SDK_LEDGER_INITIALIZATION_REQUIRED')
        self.read()

    @contextmanager
    def lock(self):
        path = self.path.with_name(self.path.name + '.LOCK'); token = os.urandom(16).hex()
        deadline = time.monotonic() + 60
        while True:
            try: fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY); break
            except FileExistsError:
                if time.monotonic() >= deadline: raise RuntimeError('LOCK_PRESERVED_NO_STALE_DELETE')
                time.sleep(.02)
        try:
            with os.fdopen(fd, 'w', encoding='utf8') as out:
                json.dump({'pid': os.getpid(), 'life': self.life, 'token': token}, out); out.flush(); os.fsync(out.fileno())
            yield
        finally:
            if path.exists() and json.loads(path.read_text('utf8')).get('token') == token: path.unlink()

    def read(self):
        value = json.loads(self.path.read_text('utf8'))
        window = json.loads((ROOT / 'configuracion/VENTANA_CONGELADA.json').read_text('utf8'))
        if value.get('schema') != SCHEMA or value.get('limit') != 40000 or value.get('max_worlds') != 6 or value.get('sdk_global_cycles') != 3:
            raise ValueError('FROZEN_SDK_BUDGET')
        if not isinstance(value.get('intents'), dict) or value['consumed'] != sum(w['consumed'] for w in value['worlds'].values()):
            raise ValueError('EXACT_ACCOUNTING_REQUIRED')
        return value

    def register_lease(self, lease, *, expected_sha256):
        with self.lock():
            if hashlib.sha256(self.path.read_bytes()).hexdigest() != expected_sha256:
                raise RuntimeError('LEDGER_CHANGED_BEFORE_CLOSED_ADMIN_TRANSACTION')
            value = self.read()
            if value['intents']: raise RuntimeError('ANY_PENDING_MATERIAL_INTENT_BLOCKS_LEASE_ADMIN')
            world = value['worlds'].get(self.life)
            if world is None:
                if len(value['worlds']) >= 6: raise RuntimeError('SIX_DIAGNOSTIC_WORLD_CAP')
                world = value['worlds'][self.life] = {'consumed': 0, 'validation_consumed': 0,
                    'validation_cycles': 0, 'reserved': 0, 'cycles': 0, 'role': self.role, 'max_cycles': self.max_cycles}
            if world['reserved'] or world['cycles'] != lease['startingCompletedCycles'] or world['consumed'] != lease['startingConsumedTicks']:
                raise RuntimeError('ACTUAL_COUNTERS_AND_EMPTY_RESERVATION_REQUIRED')
            if not (1 <= lease['additionalCycles'] <= 3 and lease['cumulativeCycleCap'] == world['cycles'] + lease['additionalCycles'] <= self.max_cycles):
                raise ValueError('CUMULATIVE_PROFILE_CAP_NOT_RESET')
            old = value['leases'].get(self.life)
            if old is not None: value['lease_history'].append({'life': self.life, 'lease': old})
            value['leases'][self.life] = lease
            write(self.path, value)

    def begin(self, life, identifier, mode):
        with self.lock():
            value = self.read()
            if life != self.life or life in value['intents']: raise RuntimeError('PRIOR_INTENT_PRESERVED_NO_REPLAY')
            if mode not in MODES: raise ValueError('CLOSED_NATIVE_MODE')
            lease = value['leases'].get(life)
            if lease is None: raise RuntimeError('EXPLICIT_CLOSED_OPERATIONAL_LEASE_REQUIRED')
            if life not in value['worlds']:
                if len(value['worlds']) >= 6: raise RuntimeError('SIX_DIAGNOSTIC_WORLD_CAP')
                value['worlds'][life] = {'consumed': 0, 'validation_consumed': 0, 'validation_cycles': 0,
                    'reserved': 0, 'cycles': 0, 'role': self.role, 'max_cycles': self.max_cycles}
            world = value['worlds'][life]
            if (world['role'], world['max_cycles']) != (self.role, self.max_cycles): raise ValueError('SUPPLY_NEVER_RESET')
            if mode == 'eci01-rbx01-decision':
                if time.time() >= lease['lastNewUtcEpoch']: raise RuntimeError('LAST_NEW_Q1_CUTOFF')
                if world['reserved'] or world['cycles'] >= min(self.max_cycles, lease['cumulativeCycleCap']): raise RuntimeError('PENDING_OR_EXHAUSTED_SUPPLY')
                sdk_used = sum(w.get('validation_cycles', 0) + int(w['reserved'] > 0) for w in value['worlds'].values() if w['role'] == 'pilot')
                if lease['validationCampaign'] and self.role == 'pilot' and sdk_used >= 3: raise RuntimeError('THREE_SDK_VALIDATION_EPISODES_CAP')
                world['reserved'] = 4096
                if lease['validationCampaign'] and value['validation_consumed'] + sum(w['reserved'] for w in value['worlds'].values()) > 40000:
                    raise RuntimeError('GLOBAL_TICK_RESERVATION_CAP')
            elif mode != 'eci01-rbx01-estado' and not world['reserved']: raise RuntimeError('EXISTING_EPISODE_RESERVATION_REQUIRED')
            if time.time() >= lease['hardFinishUtcEpoch']: raise RuntimeError('HARD_NATIVE_CUTOFF')
            value['intents'][life] = {'life': life, 'id': identifier, 'mode': mode, 'utc_epoch': time.time()}
            write(self.path, value)

    def finish(self, life, identifier, before, after, mode):
        with self.lock():
            value = self.read(); world = value['worlds'][life]; intent = value['intents'].get(life)
            if intent is None or (intent['life'], intent['id'], intent['mode']) != (life, identifier, mode):
                raise RuntimeError('EXACT_ACTUAL_INTENT_REQUIRED')
            ticks = after - before
            if type(ticks) is not int or not (0 <= ticks <= world['reserved'] or mode == 'eci01-rbx01-estado' and ticks == 0):
                raise RuntimeError('UNEXPECTED_TICKS_INTENT_PRESERVED')
            value['consumed'] += ticks; world['consumed'] += ticks; world['reserved'] -= ticks
            validation = value['leases'][life]['validationCampaign']
            if validation: value['validation_consumed'] += ticks; world['validation_consumed'] += ticks
            if mode == 'eci01-rbx01-feedback':
                world['reserved'] = 0; world['cycles'] += 1
                if validation: world['validation_cycles'] += 1
            if world['consumed'] > self.max_cycles * 4096 or validation and value['validation_consumed'] > 40000: raise RuntimeError('CAP_EXCEEDED_PRESERVED')
            world['last_completed'] = {**intent, 'before_tick': before, 'after_tick': after, 'actual_ticks': ticks}
            value['last_completed'] = world['last_completed']; del value['intents'][life]; write(self.path, value)
