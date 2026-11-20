"""Passive exact records and explicit physical interfaces; no answer oracle."""
from array import array
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
WHEEL_SHA = '17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623'
PYD_SHA = '20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''): h.update(block)
    return h.hexdigest()


def put(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding='utf-8')


def identity():
    import dee_thinking as d
    assert sys.version_info[:2] == (3, 13) and sys.maxsize > 2**32
    assert d.__version__ == '4.0.0' and d.kernel_identity()['kernel_version'] == 27
    assert sha(d._native.__file__) == PYD_SHA
    assert sha(ROOT / 'runtime/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl') == WHEEL_SHA
    assert Path(d.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    return {'library': d.__version__, 'kernel': d.kernel_identity(), 'wheel_sha256': WHEEL_SHA,
            'native_sha256': PYD_SHA, 'module': d.__file__, 'python': sys.executable}


def record(world, site):
    import dee_thinking as d
    value = world.runtime.observe(d.Coordinate(*site)); r = value.record
    return {'tick': int(value.tick), 'site': list(site), 'raw': str(value.raw), 'clock': str(value.clock),
            'state': r.state, 's_reg': r.s_reg, 'semantic': r.semantic,
            'direction': [r.dx, r.dy, r.dz], 'active': bool(r.state > 0 and r.semantic != 5)}


def interface(name, site, direction, state=1, semantic=1):
    import dee_thinking as d
    channel = d.ChannelSpec(); channel.name = name; channel.injection_site = d.Coordinate(*site)
    channel.direction = d.Direction(*direction); channel.state = state; channel.semantic = semantic
    channel.allow_experience = True; channel.allow_probe = True
    item = d.InterfaceSpec(); item.name = name; item.channel = channel
    return item


def receipt(world, identifier):
    r = world.runtime.receipt(identifier)
    if r is None: return {'id': int(identifier), 'status': 'MISSING'}
    return {'id': int(r.id), 'status': str(r.status), 'channels': list(r.channels),
            'requested_tick': int(r.requested_tick), 'effective_tick': None if r.effective_tick is None else int(r.effective_tick),
            'kind': str(r.kind), 'reason': r.reason}


def digest(world):
    r = world.runtime
    return {'tick': int(r.current_tick), 'raw_sha256': hashlib.sha256(array('Q', r.raw_copy()).tobytes()).hexdigest(),
            'clock_sha256': hashlib.sha256(array('Q', r.clock_copy()).tobytes()).hexdigest()}


def operational(world):
    r = world.runtime
    return {'tick': int(r.current_tick), 'channels': list(r.channel_names),
            'receipts': [receipt(world, x.id) for x in r.receipts],
            'external_operations': list(world.external_operations),
            'protocols': [{'id': x.id, 'completed': x.completed, 'next_index': x.next_index} for x in world.protocols],
            'metadata': dict(r.snapshot_metadata_entries)}


def until(world, tick):
    if world.runtime.paused or tick < world.runtime.current_tick: raise ValueError('Nonmonotonic or paused MAIN')
    world.run_until(int(tick))
    assert world.runtime.current_tick == tick


def local_context(world, site):
    n = world.runtime.dimension
    return [record(world, tuple((site[i] + delta[i]) % n for i in range(3)))
            for delta in [(x, y, z) for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)]]


def gate(world, site):
    import dee_thinking as d
    value = d.inspect_write_gate(world.runtime, d.Coordinate(*site), False)
    fields = ('local_clock', 'center_available', 'n_active', 'hadron', 'rule_value', 'survives_material_rule',
              'semantic_protected', 'write_protected', 'k', 'period', 'phase_remainder',
              'ordinary_increment_condition', 'branch', 'demux_status')
    return {name: str(getattr(value, name)) if name == 'local_clock' else getattr(value, name) for name in fields}
