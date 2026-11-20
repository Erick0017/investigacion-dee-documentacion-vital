"""Noneditable installation, isolated public walkthrough, and process restore.

The import guard makes accidental laboratory delegation fail.  It does not
change the native Runtime and is enabled only in this validation process.
"""
import argparse
from array import array
import hashlib
import importlib.abc
import json
from pathlib import Path
import runpy
import subprocess
import sys


class NoLaboratoryImports(importlib.abc.MetaPathFinder):
    names = {"apparatus", "frontiers", "branches", "observations", "dee_universe_v27"}
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in self.names:
            raise ImportError("Product validation prohibits laboratory module: " + fullname)
        return None


def state(w):
    r = w.runtime
    return {"tick": r.current_tick,
            "raw": hashlib.sha256(array('Q', r.raw_copy()).tobytes()).hexdigest(),
            "clocks": hashlib.sha256(array('Q', r.clock_copy()).tobytes()).hexdigest(),
            "channels": r.channel_names,
            "receipts": [(x.id, str(x.status), x.requested_tick, x.effective_tick, list(x.channels)) for x in r.receipts],
            "protocols": [(p.id, p.next_capture, [[(o.raw, o.clock, o.tick) for o in s.captured] for s in p.steps]) for p in w.protocols]}


def main(a):
    sys.meta_path.insert(0, NoLaboratoryImports())
    import dee_thinking as d
    import dee_thinking._native as native
    folder = Path(a.output).resolve(); folder.mkdir(parents=True, exist_ok=True)
    module = Path(d.__file__).resolve(); binary = Path(native.__file__).resolve()
    assert 'site-packages' in module.parts and module.is_relative_to(Path(sys.prefix).resolve())
    assert d.__version__ == '3.5.0' and native.__version__ == '3.5.0'
    assert d.kernel_identity()['kernel_version'] == 27
    assert 'dee_universe_v27' not in sys.modules
    assert not any(n in sys.modules for n in NoLaboratoryImports.names)
    runpy.run_path(str(Path(a.example).resolve()))['example'](folder)
    w = d.OrganizationalWorld.load_snapshot(str(folder/'public_mid_protocol.deetsnap'))
    reference = w.fork(); reference.run_until(21)
    destination = folder/'RESTORED_OTHER_PROCESS.deetsnap'
    argv = [sys.executable, '-I', '-B', '-c',
            'import sys,dee_thinking as d; w=d.OrganizationalWorld.load_snapshot(sys.argv[1]); w.run_until(21); w.save_snapshot(sys.argv[2])',
            str(folder/'public_mid_protocol.deetsnap'), str(destination)]
    r = subprocess.run(argv, cwd=folder, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    restored = d.OrganizationalWorld.load_snapshot(str(destination))
    assert state(restored) == state(reference)
    decoder = d.OutputDecoder()
    before = state(restored); restored.decode('q0', 'response', decoder); assert state(restored) == before
    result = {'version': d.__version__, 'kernel': d.kernel_identity(), 'build_info': d.build_info(),
              'module': str(module), 'native_module': str(binary),
              'native_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
              'wheel_sha256': hashlib.sha256(Path(a.wheel).read_bytes()).hexdigest(),
              'python': sys.version, 'executable': sys.executable, 'prefix': sys.prefix,
              'sys_path': sys.path, 'laboratory_modules_blocked': sorted(NoLaboratoryImports.names),
              'public_example': str(Path(a.example).resolve()), 'noneditable_site_packages': True,
              'other_process_command': argv, 'other_process_exit_code': r.returncode,
              'cross_process_operational_future_equal': True, 'decode_passive': True,
              'continued_state': state(restored),
              'checkpoints': [{'name': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in folder.glob('*.deetsnap')]}
    (folder/'INSTALLATION_RESULT.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2)); return 0


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--wheel', required=True); p.add_argument('--example', required=True); p.add_argument('--output', required=True)
    raise SystemExit(main(p.parse_args()))
