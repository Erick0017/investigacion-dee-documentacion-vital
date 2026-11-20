"""External post-trajectory snapshot comparison; never called by a participant."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import digest, operational, put, sha
from integrated import Session


def interfaces(world):
    rows = []
    for item in world.interfaces:
        c = item.channel; p = c.injection_site; v = c.direction; codec = item.codec
        rows.append({'name': item.name, 'channel': {'name': c.name,
           'site': [p.x, p.y, p.z], 'direction': [v.dx, v.dy, v.dz], 'state': c.state,
           'semantic': c.semantic, 'allow_experience': c.allow_experience, 'allow_probe': c.allow_probe},
           'codec': {'type': str(codec.type), 'minimum': codec.minimum, 'maximum': codec.maximum,
                     'injective': codec.injective, 'version': codec.version, 'symbols': dict(codec.symbols)},
           'admission': item.admission, 'meaning_location': item.meaning_location})
    return rows


def compare(actual_path, expected_path):
    actual, expected = Session.load(actual_path), Session.load(expected_path)
    a, e = actual.world.runtime, expected.world.runtime
    checks = {'N': a.dimension == e.dimension, 'tick': a.current_tick == e.current_tick,
              'RAW_complete': a.raw_copy() == e.raw_copy(),
              'clocks_complete': a.clock_copy() == e.clock_copy(),
              'identity': actual.identity == expected.identity,
              'geometry_JSON_values': json.loads(json.dumps(actual.geometry)) == json.loads(json.dumps(expected.geometry)),
              'request_history': actual.requests == expected.requests,
              'native_interface_definitions_and_codecs': interfaces(actual.world) == interfaces(expected.world),
              'paused': a.paused == e.paused,
              'organization_ids': list(actual.world.organization_ids) == list(expected.world.organization_ids)}
    op_a, op_e = operational(actual.world), operational(expected.world); caches = []
    for op in (op_a, op_e):
        caches.append({k: v for k, v in op['metadata'].items() if k.startswith('dee_thinking.organizational.')})
        op['metadata'] = {k: v for k, v in op['metadata'].items() if not k.startswith('dee_thinking.organizational.')}
    checks['operative_except_framework_cache'] = op_a == op_e
    return {'schema': 'CPC6.snapshot-equivalence.v1', 'verified': all(checks.values()),
            'classification': 'POST_TRAJECTORY_INSTRUMENT', 'checks': checks,
            'actual': {'sha256': sha(actual_path), 'physical': digest(actual.world)},
            'reference': {'sha256': sha(expected_path), 'physical': digest(expected.world)},
            'framework_serialization_cache_equal_separately': caches[0] == caches[1],
            'geometry_Python_container_equal_separately': actual.geometry == expected.geometry,
            'scope': 'RAW/clocks are complete uint64 arrays without normalization. Only opaque framework serialization cache is separate; JSON geometry values, receipt/queue/protocol state and own session metadata must agree. Reference is read after both trajectories and never fed into MAIN.'}


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--actual', type=Path, required=True)
    p.add_argument('--expected', type=Path, required=True); p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    result = compare(a.actual, a.expected); put(a.output, result)
    print(json.dumps({'verified': result['verified'], 'checks': result['checks']}))
    assert result['verified']


if __name__ == '__main__': main()
