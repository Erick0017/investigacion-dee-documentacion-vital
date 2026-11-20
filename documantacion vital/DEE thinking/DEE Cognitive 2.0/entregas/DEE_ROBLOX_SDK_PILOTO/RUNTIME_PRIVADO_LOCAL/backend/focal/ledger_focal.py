"""FOCAL6 role on the unchanged shared40k ledger; never resets demo counters."""
from pathlib import Path
import hashlib
import json
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ledger_sdk as base

class TickLedger(base.TickLedger):
    def __init__(self, path, life, max_cycles, role=None):
        self.path = Path(path).resolve(); self.life = life; self.role = 'focal'; self.max_cycles = max_cycles
        if self.path != base.ROOT / 'estado_demo/LEDGER_SDK.json': raise ValueError('SAME_SHARED_SDK_LEDGER_REQUIRED')
        prefix = base.PREFIX
        if not life.startswith(prefix) or re.fullmatch(r'SDK_DEMO_[0-9A-F]{16}', life.removeprefix(prefix)) is None:
            raise ValueError('EXACT_FOCAL_DIAGNOSTIC_LIFE')
        cfg = json.loads((base.ROOT / 'estado_demo/instancias' / life.removeprefix(prefix) / 'INSTANCE.json').read_text('utf8'))
        if cfg.get('profile') != 'FOCAL' or cfg['lifeId'] != life or max_cycles != 6 or role not in (None, 'focal'):
            raise ValueError('EXPLICIT_FOCAL6_PROFILE_ONLY')
        if not self.path.is_file(): raise RuntimeError('NO_LEDGER_RESET_OR_NEW_FOCAL_BUDGET')
        self.read()

    def register_lease(self, lease, *, expected_sha256):
        with self.lock():
            if hashlib.sha256(self.path.read_bytes()).hexdigest() != expected_sha256: raise RuntimeError('SHARED_LEDGER_CHANGED')
            value = self.read()
            if value['intents']: raise RuntimeError('PRESERVE_EXISTING_NATIVE_INTENT')
            world = value['worlds'].get(self.life)
            if world is None:
                if len(value['worlds']) >= 6: raise RuntimeError('SHARED_SIX_WORLD_CAP')
                world = value['worlds'][self.life] = {'consumed': 0, 'validation_consumed': 0,
                    'validation_cycles': 0, 'reserved': 0, 'cycles': 0, 'role': 'focal', 'max_cycles': 6}
            if world['role'] != 'focal' or world['max_cycles'] != 6 or world['reserved']:
                raise RuntimeError('FOCAL_SUPPLY_OR_RESERVATION_MUST_NOT_RESET')
            if world['cycles'] != lease['startingCompletedCycles'] or world['consumed'] != lease['startingConsumedTicks']:
                raise RuntimeError('ACTUAL_FOCAL_COUNTERS_REQUIRED')
            if not (1 <= lease['additionalCycles'] <= 6 and lease['cumulativeCycleCap'] == world['cycles'] + lease['additionalCycles'] <= 6):
                raise ValueError('CUMULATIVE_FOCAL6_CAP')
            if not lease['validationCampaign']: raise ValueError('FOCAL_EXPERIMENT_REQUIRES_CURRENT_CAMPAIGN_CLIP')
            old = value['leases'].get(self.life)
            if old is not None: value['lease_history'].append({'life': self.life, 'lease': old})
            value['leases'][self.life] = lease
            base.write(self.path, value)
