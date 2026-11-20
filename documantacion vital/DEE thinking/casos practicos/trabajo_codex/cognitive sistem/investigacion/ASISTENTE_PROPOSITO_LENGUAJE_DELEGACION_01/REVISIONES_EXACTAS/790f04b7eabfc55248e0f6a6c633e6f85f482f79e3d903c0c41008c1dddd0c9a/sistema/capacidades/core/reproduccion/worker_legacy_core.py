"""Exact historical experiment logic, native4.5 transition adapter, no archives.

The historical experiments use directly writable RAW/clock arrays, not Runtime
channels or queues. This adapter ports that contract, NOT a cognitive session:
each externally changed array is imported with its exact continuing tick and
clocks. All evolution is one native official Runtime.advance transition. No
response, expected result or historical output feeds the world.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import time
import weakref

P = argparse.ArgumentParser()
P.add_argument('--materialized', type=Path, required=True)
P.add_argument('--out', type=Path, required=True)
P.add_argument('--numpy-root', type=Path, required=True)
P.add_argument('--family', choices=('core06', 'core07'), required=True)
P.add_argument('--pilot', action='store_true')
A = P.parse_args()
MAT = A.materialized.resolve()
OUT = A.out.resolve()
OUT.mkdir(parents=True, exist_ok=False)
NP_ROOT = A.numpy_root.resolve()
START = time.monotonic()
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from app.process_control import protect_current
protect_current(output=OUT/'RECURSOS_DEL_TRABAJADOR.json')

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def emit(name, obj):
    p = OUT/name
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf8')

DENIED = []
ALLOWED = [MAT, OUT, Path(__file__).resolve().parent, Path(sys.prefix).resolve(),
           Path(sys.base_prefix).resolve(), NP_ROOT, Path(os.environ.get('WINDIR', 'C:/Windows')).resolve()]
def audit(event, args):
    if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(args[0])).resolve()
    if not any(path == r or path.is_relative_to(r) for r in ALLOWED):
        DENIED.append(str(path))
        raise PermissionError('Undeclared read/write: '+str(path))
sys.addaudithook(audit)

import dee_thinking as d
import dee_thinking._native as native
assert sys.version_info[:2] == (3, 13) and platform.architecture()[0] == '64bit'
assert d.__version__ == '4.5.0'
assert Path(d.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
assert sha(native.__file__) == '17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
assert d.build_info()['kernel_source_sha256'] == 'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
sys.path.append(str(NP_ROOT))
import numpy as np
assert np.__version__ == '2.2.6', np.__version__
assert Path(np.__file__).resolve().is_relative_to(NP_ROOT)
IDENTITY = {'python': sys.version, 'python_executable': sys.executable,
    'dee_version': d.__version__, 'dee_path': d.__file__, 'native_path': native.__file__,
    'pyd_sha256': sha(native.__file__), 'kernel_identity': d.kernel_identity(),
    'build_info': d.build_info(), 'numpy': np.__version__, 'numpy_path': np.__file__,
    'numpy_init_sha256': sha(np.__file__), 'numpy_root_explicit': str(NP_ROOT),
    'adapter': 'direct-array physical-transition port; no historical Runtime queues claimed'}
emit('IDENTITY.json', IDENTITY)

GEN = MAT/'cpc8/genealogia/fuentes'
BASE = MAT/'historico/CPC3/experimentos/SEM01_SIGNIFICADO_ADQUIRIDO/fuentes'
H = {'core06': ('CORE06/RUNNERS/native_core.py', 'native_core',
        '6f3babac1f303f340b0e.py', '6f3babac1f303f340b0e83c134ac65a223cd647c5da5fcf81c5bbb9a45ee7ae9'),
     'core07': ('CORE07/RUNNERS/core07_common.py', 'core07_common',
        'f4390ffab1cc3101ae02.py', 'f4390ffab1cc3101ae0200c3065869b589f9562b4c9622446c3066b8b108f78f')}

def load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(sp)
    sys.modules[name] = mod
    sp.loader.exec_module(mod)
    return mod

HELPER, MODNAME, SOURCE, SHASH = H[A.family]
assert sha(GEN/SOURCE) == SHASH
helper = load(MODNAME, BASE/HELPER)
runner = load('selected_historical_runner', GEN/SOURCE)
STATE = {'case': None, 'worlds': [], 'transitions': 0, 'imports': 0}

def sparse(raw, clock):
    mask = (raw != np.uint64(0)) | (clock != np.uint64(0))
    return [{'i': int(i), 'raw': str(int(raw.ravel()[i])), 'clock': str(int(clock.ravel()[i]))}
            for i in np.flatnonzero(mask)]

class OfficialTransition:
    def __init__(self):
        self.live = {}
    def tick_universo_lazy(self, raw_a, raw_b, clock_a, clock_b, n, threads):
        for k in [k for k, v in self.live.items() if v['weak']() is None]:
            del self.live[k]
        key = id(raw_a)
        holder = self.live.get(key)
        if holder is None or holder['weak']() is not raw_a:
            row = {'case': STATE['case'], 'N': n, 'backend': 'LAZY',
                   'initial': sparse(raw_a, clock_a), 'external_writes': [], 'tick': 0}
            holder = {'weak': weakref.ref(raw_a), 'runtime': None, 'row': row,
                      'hash': None, 'previous_raw': None, 'previous_clock': None}
            self.live[key] = holder
            STATE['worlds'].append(row)
        row = holder['row']
        raw_hash = hashlib.sha256(raw_a.tobytes()).hexdigest()
        clock_hash = hashlib.sha256(clock_a.tobytes()).hexdigest()
        if holder['hash'] != (raw_hash, clock_hash):
            if holder['runtime'] is not None:
                oldr, oldc = holder['previous_raw'], holder['previous_clock']
                changed = np.flatnonzero((raw_a != oldr) | (clock_a != oldc))
                row['external_writes'].append({'tick': row['tick'], 'sites': [
                    {'i': int(i), 'raw_before': str(int(oldr.ravel()[i])),
                     'raw_after': str(int(raw_a.ravel()[i])), 'clock_before': str(int(oldc.ravel()[i])),
                     'clock_after': str(int(clock_a.ravel()[i]))} for i in changed]})
            rt = d.Runtime.import_research_state(n, row['tick'], raw_a.ravel(), clock_a.ravel())
            rt.execution_options = d.TickOptions(d.Backend.LAZY, 1)
            holder['runtime'] = rt
            STATE['imports'] += 1
        rt = holder['runtime']
        assert rt.current_tick == row['tick']
        rt.advance(1)
        raw_a[...] = np.asarray(rt.raw_copy(), dtype=np.uint64).reshape(raw_a.shape)
        clock_a[...] = np.asarray(rt.clock_copy(), dtype=np.uint64).reshape(clock_a.shape)
        raw_b[...] = raw_a
        clock_b[...] = clock_a
        row['tick'] += 1
        row['terminal_raw_sha256'] = hashlib.sha256(raw_a.tobytes()).hexdigest()
        row['terminal_clock_sha256'] = hashlib.sha256(clock_a.tobytes()).hexdigest()
        # Empty sites have meaningful continuing clocks too. Expanding their
        # entire terminal lattice into Python dictionaries wastes memory and
        # is not a sparse checkpoint. Keep exact complete-array hashes; the
        # original local primary observations are archived separately.
        row['terminal_raw_nonzero_sites'] = int(np.count_nonzero(raw_a))
        row['terminal_clock_nonzero_sites'] = int(np.count_nonzero(clock_a))
        holder['hash'] = (row['terminal_raw_sha256'], row['terminal_clock_sha256'])
        holder['previous_raw'], holder['previous_clock'] = raw_a.copy(), clock_a.copy()
        STATE['transitions'] += 1
        # Free completed worlds at case boundary; no independent life is inferred.
        for k in [k for k, v in self.live.items() if v['weak']() is None]:
            del self.live[k]
        return {'tick_index': row['tick'], 'transition': 'official4.5LAZY'}

KERNEL = OfficialTransition()
runner.verify_and_load_kernel = lambda threads=1: (KERNEL, IDENTITY)

def wrap(name):
    original = getattr(runner, name)
    def call(*args, **kwargs):
        STATE['case'] = {'function': name, 'args': [x for x in args[1:]], 'kwargs': kwargs}
        result = original(*args, **kwargs)
        print(json.dumps({'case_completed': STATE['case'], 'transitions': STATE['transitions']}, ensure_ascii=False), flush=True)
        return result
    setattr(runner, name, call)

if A.family == 'core06':
    for name in ('run_transfer', 'run_extinction', 'run_reversal'):
        wrap(name)
    runner.OUT = OUT/'OBSERVED.json'
    if A.pilot:
        observed = {'transfer': [runner.run_transfer(KERNEL, (1, 0, 0), mode)
                     for mode in ('trained', 'untrained', 'matched_exposure')],
                    'extinction': [runner.run_extinction(KERNEL, 'cue_only')],
                    'reversal_and_reacquisition': [runner.run_reversal(KERNEL, 'full', 'C')]}
        emit('OBSERVED.json', observed)
    else:
        runner.main()
    # Reference read ONLY after the physical worlds above have completed.
    refpath = GEN/'3867d6fa86a3b2c90b42.json'
    reference = json.loads(refpath.read_text(encoding='utf8'))
    observed = json.loads((OUT/'OBSERVED.json').read_text(encoding='utf8'))
    if A.pilot:
        diffs = []
        for family, cases in observed.items():
            for case in cases:
                keys = ('mode', 'query_direction') if family == 'transfer' else ('mode',) if family == 'extinction' else ('variant', 'teacher_kind')
                match = next(c for c in reference[family] if all(c[k] == case[k] for k in keys))
                if match != case: diffs.append({'family': family, 'observed': case, 'reference': match})
    else:
        diffs = [key for key in ('summary', 'transfer', 'extinction', 'reversal_and_reacquisition')
                 if observed[key] != reference[key]]
else:
    runner.LOCK = MAT/'cores/CORE07/HOLDOUT_LOCKS/C7H03_REPROGRAMMABLE_FUNCTIONAL_MATTER.json'
    assert sha(runner.LOCK) == runner.EXPECTED_LOCK_SHA256
    runner.OUT = OUT/'OBSERVED.json'
    wrap('simulate')
    if A.pilot:
        # The frozen initial configuration is recovered separately from outcomes;
        # importing cells here would read the historical output before evolution.
        # Generate the exact source main, restrict only the enumerated lock modes.
        raise RuntimeError('CORE07 pilot not implemented: run frozen144-case panel')
    runner.main()
    refpath = MAT/'cores/CORE07/RESULTS/C7H03_reprogrammable_functional_matter.json'
    reference = json.loads(refpath.read_text(encoding='utf8'))
    observed = json.loads((OUT/'OBSERVED.json').read_text(encoding='utf8'))
    diffs = [key for key in ('sample_sizes', 'rates', 'pass_conditions', 'verdict', 'cells', 'cases')
             if observed[key] != reference[key]]

emit('PRIMARY_TRANSITIONS.json', {'schema': 'CPC9.core-recovery.native-transitions.v1',
     'family': A.family, 'worlds': STATE['worlds'], 'transitions': STATE['transitions'],
     'physical_imports': STATE['imports'], 'all_uint64_decimal_strings': True,
     'state_coverage': 'initial sparse exact state, complete terminal RAW/clocks hashes and every external array write. Local primary observations in OBSERVED.json; no expanded dense terminal clocks.'})
REPORT = {'family': A.family, 'status': 'PASS' if not diffs else 'FAIL',
    'source_sha256': SHASH, 'helper_sha256': sha(BASE/HELPER),
    'reference_sha256': sha(refpath), 'observed_sha256': sha(OUT/'OBSERVED.json'),
    'differences': diffs, 'identity': IDENTITY, 'elapsed_seconds': time.monotonic()-START,
    'cases': len(STATE['worlds']), 'native_transitions': STATE['transitions'],
    'historical_full_state_comparison': 'UNAVAILABLE: historical result includes exact local field records, not complete terminal state hashes.',
    'scope': 'Exact original local observations, outcomes and controls; official4.5 transition port of original direct arrays, not Runtime queue/session compatibility.',
    'scientific_replication': 'Deterministic technical reproduction, not independent sample.',
    'historical_reads_denied': DENIED, 'allowed_read_roots': [str(x) for x in ALLOWED]}
emit('RECOVERY.json', REPORT)
print(json.dumps({'status': REPORT['status'], 'cases': REPORT['cases'], 'elapsed_seconds': REPORT['elapsed_seconds']}, ensure_ascii=False), flush=True)
raise SystemExit(0 if not diffs else 2)
