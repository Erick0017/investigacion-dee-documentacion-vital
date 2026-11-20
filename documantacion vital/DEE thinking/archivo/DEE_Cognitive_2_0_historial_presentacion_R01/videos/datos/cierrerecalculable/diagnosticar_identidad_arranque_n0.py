"""Directed APD05 startup diagnosis. Never creates a DEE Runtime or owner.

Reads the six archived HTTP observations and exercises the exact LocalTransport
method against synthetic files and mocked immutable queue metadata. The proposed
change is compiled in memory; the original system is not modified.
"""
from __future__ import annotations

import ast
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types


BASE = Path(__file__).resolve().parent
SOURCE = BASE.parent / 'documantacion vital/DEE thinking/DEE Cognitive System 1.1'
GUI = SOURCE / 'aplicacion/GENESIS/genesis.py'
HTTP = SOURCE / ('laboratorio/campanas/APD05_GENESIS_SIN_LLM/cierre/'
    'PRUEBA_FULL_GENESIS_APD05_R01/PHASE_0_OPEN_REVISION_RECORD_PENDING/HTTP_PRIMARIO.jsonl.gz')

OLD = """        if cache and active:
            from app.cola_local import QueueDB
            database = self.state_root / 'servicios_persistentes' / cache['world_id'] / 'cola.sqlite3'
            if database.is_file():
                published = QueueDB(database).get_meta('genesis_record_index')
                if published:
                    self._genesis_record = published
                    return published
            return cache
"""
NEW = """        if cache and cache.get('life_id') != life:
            raise ValueError('El índice en caché pertenece a otra vida; no se redirige su propietario.')
        if cache and active:
            from app.cola_local import QueueDB
            database = self.state_root / 'servicios_persistentes' / cache['world_id'] / 'cola.sqlite3'
            if database.is_file():
                published = QueueDB(database).get_meta('genesis_record_index')
                # Complete imports preserve prior metadata. Until this owner
                # publishes, an inherited parent index is not this copy's ID.
                if (published and published.get('life_id') == life
                        and published.get('world_id') == cache['world_id']):
                    self._genesis_record = published
                    return published
            return cache
"""


def local_class(text, label):
    spec = importlib.util.spec_from_loader(label, loader=None)
    module = importlib.util.module_from_spec(spec)
    module.__file__ = str(GUI)
    exec(compile(text, str(GUI), 'exec'), module.__dict__)
    return module.LocalTransport


def ast_without_record(text):
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == 'LocalTransport':
            node.body = [n for n in node.body if not (isinstance(n, ast.FunctionDef) and n.name == 'record')]
    return ast.dump(tree, include_attributes=False)


def exercise(klass, root, rows):
    class Process:
        active = True
        def poll(self):
            return None if self.active else 0

    backend = klass()
    backend.root = root
    backend.process = Process()
    backend._genesis_record = None
    backend.external_view_only = False
    child = 'DEE20_N0_SYNTHETIC_CHILD'
    world = child
    queue_path = root / 'sistema/estado/servicios_persistentes' / world / 'cola.sqlite3'
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.touch(exist_ok=True)
    life_path = root / 'sistema/estado/vidas' / child / 'VIDA.json'
    life_path.parent.mkdir(parents=True, exist_ok=True)
    card = {'life_id': child, 'world_id': world, 'physical': {'tick': 684418},
            'snapshot_sha256': 'unchanged-native-past', 'pending_material': None}
    life_path.write_text(json.dumps(card), encoding='utf8')
    immutable_before = hashlib.sha256(life_path.read_bytes()).hexdigest()
    backend.process.active = False
    loaded = backend.record(child)
    backend.process.active = True
    rows[world] = {'life_id': 'APD05_MAIN', 'world_id': 'APD05_MAIN',
                   'physical': {'tick': 684418}, 'snapshot_sha256': 'unchanged-native-past'}
    inherited = backend.record(child)
    second = backend.record(child)
    rows[world] = {**card, 'physical': {'tick': 684418}, 'published_by_current_owner': True}
    fresh = backend.record(child)
    result = {'first_loaded_id': loaded['life_id'], 'inherited_metadata_result_id': inherited['life_id'],
              'second_result_id': second['life_id'], 'fresh_result_id': fresh['life_id'],
              'fresh_publication_used': fresh.get('published_by_current_owner') is True,
              'life_file_unchanged': hashlib.sha256(life_path.read_bytes()).hexdigest() == immutable_before}
    if inherited['life_id'] == child:
        # A correct life name with a different world must still not hijack the
        # queue. No identity or pending request is written in either case.
        rows[world] = {**card, 'world_id': 'ANOTHER_WORLD'}
        result['wrong_world_ignored'] = backend.record(child)['world_id'] == world
        backend._genesis_record = {'life_id': 'ANOTHER_LIFE', 'world_id': world}
        try:
            backend.record(child)
        except ValueError:
            result['wrong_life_cache_rejected'] = True
        else:
            result['wrong_life_cache_rejected'] = False
    return result


def main():
    original_bytes = GUI.read_bytes()
    text = original_bytes.decode('utf8')
    if text.count(OLD) != 1:
        raise ValueError('Expected exact source block once; no broad or silent patch.')
    patched = text.replace(OLD, NEW, 1)
    assert ast_without_record(text) == ast_without_record(patched)
    archived = [json.loads(x) for x in gzip.open(HTTP, 'rt', encoding='utf8')]
    terminal = next(r for r in archived if r.get('event') == 'gui_job_terminal')
    current = terminal['status']
    evidence = {'rows': len(archived), 'http_sha256': hashlib.sha256(HTTP.read_bytes()).hexdigest(),
                'selected_life': current['life_id'],
                'returned_record_life': current['record']['life_id'],
                'returned_record_world': current['record']['world_id'],
                'owner_response': current['owner'], 'error': terminal['job']['error']}
    rows = {}
    fake = types.ModuleType('app.cola_local')
    class QueueDB:
        def __init__(self, path): self.world = Path(path).parent.name
        def get_meta(self, name):
            assert name == 'genesis_record_index'
            return rows.get(self.world)
    fake.QueueDB = QueueDB
    previous = sys.modules.get('app.cola_local')
    sys.modules['app.cola_local'] = fake
    try:
        with tempfile.TemporaryDirectory(prefix='identidad_n0_', dir=BASE) as name:
            root = Path(name)
            old_result = exercise(local_class(text, '_original_genesis_n0'), root / 'old', rows)
            rows.clear()
            new_result = exercise(local_class(patched, '_patched_genesis_n0'), root / 'new', rows)
    finally:
        if previous is None: sys.modules.pop('app.cola_local', None)
        else: sys.modules['app.cola_local'] = previous
    assert old_result['inherited_metadata_result_id'] == 'APD05_MAIN'
    assert not old_result['fresh_publication_used']
    assert new_result['inherited_metadata_result_id'] == 'DEE20_N0_SYNTHETIC_CHILD'
    assert new_result['fresh_publication_used'] and new_result['wrong_world_ignored']
    assert new_result['wrong_life_cache_rejected'] and new_result['life_file_unchanged']
    assert GUI.read_bytes() == original_bytes
    report = {'schema': 'DEE20.directed_startup_identity.N0.R01',
              'source_gui_sha256': hashlib.sha256(original_bytes).hexdigest(),
              'native_ticks': 0, 'native_worlds_created': 0, 'source_modified': False,
              'archived_primary': evidence, 'old_behavior_reproduced': old_result,
              'proposed_behavior': new_result,
              'scope': 'Readiness metadata identity only. No Native actor, agenda, queue-put, snapshot or RAW change.',
              'remaining_proof': 'Actual destination owner load, a bounded material use, save/stop/reopen remains Root-owned.'}
    output = BASE / 'DIAGNOSTICO_ARRANQUE_IDENTIDAD_N0_R01.json'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    (BASE / 'PARCHE_IDENTIDAD_LOCALTRANSPORT_R01.json').write_text(
        json.dumps({'file': 'aplicacion/GENESIS/genesis.py', 'old': OLD, 'new': NEW,
                    'source_sha256': report['source_gui_sha256']}, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
