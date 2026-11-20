"""Passive records, declared input ports and immutable-instrument checks."""
from array import array
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import zipfile

WHEEL_SHA = '17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623'
NATIVE_SHA = '20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066'
KERNEL_SHA = 'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
PARENT_SHA = '1c10b8501ff0bb9756d6b1ebe5876a63ae7300ec4722d651e94dfe9e8f45a0f6'

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1048576), b''):
            h.update(part)
    return h.hexdigest()

def put(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding='utf-8')

def append(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, default=str) + '\n')
        stream.flush()

def runtime(world):
    return world.runtime if hasattr(world, 'runtime') else world

def digest(world):
    rt = runtime(world)
    return {'tick': rt.current_tick,
            'raw_sha256': hashlib.sha256(array('Q', rt.raw_copy()).tobytes()).hexdigest(),
            'clock_sha256': hashlib.sha256(array('Q', rt.clock_copy()).tobytes()).hexdigest()}

def record(value):
    r = value.record
    return {'tick': value.tick, 'site': [value.coordinate.x, value.coordinate.y, value.coordinate.z],
            'raw': value.raw, 'clock': value.clock, 'state': r.state, 'semantic': r.semantic,
            's_reg': r.s_reg, 'direction': [r.dx, r.dy, r.dz],
            'active': r.state > 0 and r.semantic != 5}

def observe(world, site):
    import dee_thinking as d
    return record(runtime(world).observe(d.Coordinate(*site)))

obs = observe

def receipt(world, value):
    r = runtime(world).receipt(value if isinstance(value, int) else value.id)
    if r is None:
        return {'id': value, 'status': 'MISSING'}
    return {'id': r.id, 'requested_tick': r.requested_tick, 'effective_tick': r.effective_tick,
            'status': str(r.status), 'kind': str(r.kind), 'channels': list(r.channels), 'reason': r.reason}

def interface(name, site, direction, state=1, semantic=1):
    import dee_thinking as d
    channel = d.ChannelSpec()
    channel.name = name
    channel.injection_site = d.Coordinate(*site)
    channel.direction = d.Direction(*direction)
    channel.state = state
    channel.semantic = semantic
    channel.allow_experience = True
    channel.allow_probe = True
    item = d.InterfaceSpec()
    item.name = name
    item.channel = channel
    return item

def create(n, interfaces=(), placements=()):
    import dee_thinking as d
    recipe = d.OrganizationRecipe.research(n, list(placements), 0)
    recipe.execution = d.TickOptions(d.Backend.LAZY, 1)
    recipe.interfaces = list(interfaces)
    return d.OrganizationalWorld.create(recipe)

def identity(wheel):
    import dee_thinking as d
    if d.__version__ != '4.0.0' or d.kernel_identity()['kernel_version'] != 27:
        raise RuntimeError('Immutable official DEE4/v27 required')
    assert sha(wheel) == WHEEL_SHA and sha(d._native.__file__) == NATIVE_SHA
    assert Path(d.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    assert 'site-packages' in str(Path(d.__file__).resolve())
    with zipfile.ZipFile(wheel) as z:
        assert z.testzip() is None
        for name in z.namelist():
            if name.startswith('dee_thinking/') and not name.endswith('/'):
                actual = Path(d.__file__).parent / Path(name).relative_to('dee_thinking')
                assert actual.read_bytes() == z.read(name), name
    forbidden = [name for name, module in sys.modules.items()
                 if name.startswith('dee_universe_v27') or ('CPC3' in str(getattr(module, '__file__', '')) and not str(getattr(module, '__file__', '')).startswith(str(Path(__file__).resolve().parents[1])))]
    assert not forbidden, forbidden
    return {'utc': datetime.now(timezone.utc).isoformat(), 'version': d.__version__, 'kernel': 27,
            'python': sys.executable, 'module': d.__file__, 'wheel_sha256': WHEEL_SHA,
            'native_sha256': NATIVE_SHA, 'installed_payload_identical': True,
            'old_implementation_imports': forbidden}
