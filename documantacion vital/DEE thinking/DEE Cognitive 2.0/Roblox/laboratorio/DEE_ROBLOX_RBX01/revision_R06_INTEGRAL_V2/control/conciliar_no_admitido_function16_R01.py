"""Root-only correction of ONE proven pre-queue accounting intent; never Native.

Default --inspect reads a closed SQLite with immutable=1 and creates evidence.
--apply-root-only requires that exact proof/hash and modifies ONLY LEDGER_R06.json.
There is no enqueue, retry, owner, kernel, snapshot, RAW or clock operation here.
"""
from __future__ import annotations
import argparse, ast, copy, ctypes, datetime, hashlib, importlib.util, json, os
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT.parents[2]
DEST = ROOT / 'native/MAIN'
SYSTEM = DEST / 'sistema'
LIFE = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V2_MAIN'
SID = 'R06_MAIN_bb7e2b08e4ab445ca8bd'
TARGET = 'R06_' + SID + '_16_FUNCTION'
LAST_Q2 = 'R06_' + SID + '_16_QUERY_SENSOR'
TICK = 971233
PID = 17884
META_KEY = 'DEE.Cognitive.RBX01.async_native.INTEGRAL.V2.R01'
LEDGER = ROOT / 'control/LEDGER_R06.json'
DB = SYSTEM / 'estado/servicios_persistentes' / LIFE / 'cola.sqlite3'
CARD = SYSTEM / 'estado/vidas' / LIFE / 'VIDA.json'
EVENTS = ROOT / 'evidencia/NATIVE_BLOQUE_02_R02/EVENTS.jsonl'
ACTOR_LOG = SYSTEM / 'estado/servicios_locales' / LIFE / 'RBX06_NATIVE_INTEGRAL_V2/events.jsonl'
OWNER_LOG = DEST / 'ENSAYOS.jsonl'
OBSERVER_SHA = 'dbb2a5e15d70c64112d36505197f4aebf6ff7d4092972923e17cd60c10a1c873'
SNAPSHOT_SHA = 'fa3cce3c9d9e74d90ef428ab3a981eee86b5ee4e5ec5c67be6a59722f561b795'
RAW_SHA = 'b97102dabeaff8311215aa3b40c5bb79a5ddaf45e27aed289c63300216313082'
CLOCKS_SHA = 'a863e090cd78bbc36df23971938aa85c2f16a2cc6f604b52a860f813e1af67f2'

def need(value, message):
    if not value:
        raise RuntimeError(message)

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text('utf-8-sig'))

def rows(path):
    return [json.loads(s) for s in Path(path).read_text('utf8').splitlines() if s.strip()]

def safe(path, within=ROOT, exists=True):
    p = Path(path).absolute()
    need(p.is_relative_to(Path(within).absolute()), 'Path outside exact authorized root')
    for node in (p, *p.parents):
        if node.exists():
            need(not node.is_symlink() and not (getattr(node.lstat(), 'st_file_attributes', 0) & 1024),
                 'Linked/reparse paths are forbidden')
    if exists:
        need(p.exists(), 'Required path missing: ' + str(p))
    return p

def owner_pid_not_running():
    need(os.name == 'nt', 'This exact proof requires Windows process-state check')
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    k.OpenProcess.restype = ctypes.c_void_p
    k.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
    k.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = k.OpenProcess(0x1000, False, PID)
    if not handle:
        need(ctypes.get_last_error() == 87, 'Cannot establish that exact owner PID is absent')
        return 'PID_NOT_PRESENT'
    try:
        code = ctypes.c_ulong()
        need(k.GetExitCodeProcess(handle, ctypes.byref(code)), 'Cannot read owner exit status')
        need(code.value != 259, 'Exact owner PID is still active; no reconciliation')
        return 'EXITED_' + str(code.value)
    finally:
        k.CloseHandle(handle)

def build_proof():
    for p in (DEST, SYSTEM, LEDGER, DB, CARD, EVENTS, ACTOR_LOG, OWNER_LOG):
        safe(p)
    need(DEST.name == 'MAIN' and 'laboratorio' in DEST.parts, 'Diagnostic MAIN only')
    need(not (SYSTEM / 'estado/ACTIVO.json').exists(), 'Unexpected local ACTIVO; preserve')
    locks = safe(SYSTEM / 'estado/locks')
    need(not list(locks.iterdir()), 'Any Native owner lock forbids reconciliation')
    for suffix in ('-wal', '-journal', '-shm'):
        f = Path(str(DB) + suffix)
        need(not f.exists() or f.stat().st_size == 0, 'SQLite auxiliary is present/nonempty: ' + suffix)
    process = owner_pid_not_running()
    card = read_json(CARD)
    snapshot = safe(SYSTEM / card['snapshot'])
    need(sha(snapshot) == card['snapshot_sha256'] == SNAPSHOT_SHA, 'Exact closed snapshot changed')
    critical = [CARD, DB, snapshot, ACTOR_LOG, OWNER_LOG, EVENTS,
                DEST / 'CONTEXTO_EJECUCION.json', SYSTEM / 'app/cola_local.py',
                ROOT / 'native/bundle/rbx06_native_integral.py',
                ROOT / 'native/owner_support_integral_v2.py', Path(__file__)]
    hashes = {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in critical}
    owner_closed = [x for x in rows(OWNER_LOG) if x.get('kind') == 'OWNER_CLOSED'][-1]
    fs = owner_closed['final_status']
    need(owner_closed.get('pid') == PID and owner_closed.get('life') == LIFE and
         owner_closed.get('exit_code') == 0 and fs.get('running') is False and
         fs.get('life_id') == LIFE and fs.get('pid') == PID and
         fs.get('physical', {}).get('tick') == TICK, 'Latest OWNER_CLOSED is not exact known close')
    con = sqlite3.connect(DB.resolve().as_uri() + '?mode=ro&immutable=1', uri=True)
    con.row_factory = sqlite3.Row
    try:
        need(con.execute('PRAGMA integrity_check').fetchone()[0] == 'ok', 'SQLite integrity')
        counts = dict(con.execute('SELECT status,COUNT(*) FROM requests GROUP BY status'))
        need(all(counts.get(x, 0) == 0 for x in ('queued', 'processing', 'uncertain')), 'Unresolved Native requests')
        need(con.execute('SELECT COUNT(*) FROM requests WHERE id=?', (TARGET,)).fetchone()[0] == 0,
             'FUNCTION16 exists; this is NOT the known unadmitted case')
        q2 = con.execute('SELECT id,status,result,payload_sha FROM requests WHERE id=?', (LAST_Q2,)).fetchone()
        need(q2 and q2['status'] == 'completed', 'Last Q2 is not completed')
        result = json.loads(q2['result'])
        need(result['before_tick'] == 971211 and result['after_tick'] == TICK, 'Q2 physical interval mismatch')
        database_owner = json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
        need(database_owner.get('running') is False and database_owner.get('pid') == PID and
             database_owner.get('life_id') == LIFE and database_owner.get('physical', {}).get('tick') == TICK,
             'SQLite owner is not the exact closed owner')
    finally:
        con.close()
    observer = PRODUCT / 'reproducibilidad/observador_pasivo.py'
    safe(observer, within=PRODUCT)
    need(sha(observer) == OBSERVER_SHA, 'Known passive stdlib parser changed')
    spec = importlib.util.spec_from_file_location('_r06_passive_snapshot_parser', observer)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    view = module.snapshot_view(snapshot)
    need(view['physical'] == {'N': 67, 'tick': TICK, 'RAW_sha256': RAW_SHA, 'clocks_sha256': CLOCKS_SHA},
         'Exact physical state mismatch')
    actor = json.loads(view['metadata'][META_KEY]); pending = actor['pending']
    need(actor.get('phase') == 'AWAIT_WORLD_CONSEQUENCE' and actor.get('cycles') == 11 and
         actor.get('session_id') == SID and actor.get('uncertain') is False and
         actor.get('initial_tick') == 953651 and not pending.get('function_used') and
         pending.get('q2_reader', {}).get('tick') == 971229 and
         pending.get('context', {}).get('operation_id') == 'R06_' + SID + '_16_DECISION',
         'Actor phase/pending state does not match one unadmitted function')
    native_rows = rows(ACTOR_LOG)
    need(not any(x.get('context', {}).get('operation_id') == TARGET for x in native_rows),
         'Native actor already observed target intent')
    need(native_rows[-1].get('kind') == 'PHASE_COMPLETED' and native_rows[-1].get('tick') == TICK and
         native_rows[-1].get('mode') == 'eci01-rbx01-query-sensor', 'Native actor last phase differs')
    event_rows = rows(EVENTS)
    intents = [x for x in event_rows if x.get('kind') == 'NATIVE_INTENT' and
               x.get('context', {}).get('operation_id') == TARGET]
    need(len(intents) == 1 and event_rows[-1] == intents[0], 'Exact terminal host intent is not unique')
    need(not any(x.get('kind') == 'NATIVE_COMPLETED' and x.get('operation_id') == TARGET for x in event_rows),
         'Host reports a completed target')
    malformed = intents[0]['payload']['tool']
    need(malformed == {'kind': 'LESSON', 'items': {'1': {'form': 'luma', 'observedSign': -1},
                                                '2': {'form': 'nara', 'observedSign': 1}}},
         'Not the exact known Lua-array transport error')
    source = ROOT / 'native/bundle/rbx06_native_integral.py'
    validator = next(n for n in ast.parse(source.read_text('utf8')).body if isinstance(n, ast.FunctionDef) and n.name == 'validate_tool')
    isolated = {'need': need}
    exec(compile(ast.Module(body=[validator], type_ignores=[]), str(source) + ':isolated_validator_only', 'exec'), isolated)
    try:
        isolated['validate_tool'](malformed)
    except RuntimeError as error:
        need(str(error) == 'One or two environmental experiences', 'Unexpected validator rejection')
    else:
        raise RuntimeError('Exact malformed packet unexpectedly passed validator')
    v = read_json(LEDGER); intent = v.get('intents', {}).get(LIFE); w = v['worlds'][LIFE]
    need(v.get('schema') == 'DEE.RBX01.INTEGRAL.V2.prospective_native_budget.R01' and
         v.get('limit') == 100000 and v.get('max_worlds') == 6 and
         v['consumed'] == sum(x['consumed'] for x in v['worlds'].values()), 'Ledger identity/accounting')
    need(set(v['intents']) == {LIFE}, 'Another material intent exists; no global quiescence')
    need(intent == {'life': LIFE, 'id': TARGET, 'mode': 'eci01-rbx01-function', 'utc_epoch': 1794787989.4106941},
         'Ledger intent is not the exact known pre-admission intent')
    need((v['consumed'], w['consumed'], w['reserved'], w['cycles'], w['max_cycles']) == (17582, 17582, 3718, 11, 24),
         'Budget/cycle state changed')
    need(w['last_completed']['id'] == LAST_Q2 and w['last_completed']['after_tick'] == TICK and
         v['last_completed'] == w['last_completed'], 'Ledger last completed does not match Native')
    need(not any(x.get('id') == TARGET for x in v.get('rejected_before_queue', [])), 'Intent already reconciled')
    need(hashes == {k: sha(ROOT / k) for k in hashes}, 'Source changed during passive inspection')
    return {'schema': 'DEE.RBX06.known_not_admitted.FUNCTION16.R01', 'life': LIFE, 'session_id': SID,
            'target_id': TARGET, 'classification': 'REJECTED_BEFORE_QUEUE', 'native_target_row_present': False,
            'known_error': 'Lua array serialized as numeric-key object; isolated official validator rejects before QueueDB insertion',
            'owner_pid': PID, 'process': process, 'owner_running': False, 'owner_exit_code': 0,
            'queue_status_counts': counts, 'pending_or_uncertain': 0, 'last_completed_id': LAST_Q2,
            'physical': view['physical'], 'snapshot': str(snapshot.relative_to(ROOT)).replace('\\', '/'),
            'actor_phase': actor['phase'], 'actor_cycles': actor['cycles'], 'actor_function_used': False,
            'malformed_host_intent': intents[0], 'ledger_intent': intent,
            'ledger_sha256_before': sha(LEDGER), 'counters': {'consumed': v['consumed'], 'world_consumed': w['consumed'],
            'reserved': w['reserved'], 'cycles': w['cycles'], 'max_cycles': w['max_cycles']},
            'critical_sha256': hashes, 'passive_parser_sha256': OBSERVER_SHA,
            'source_locators': ['native/MAIN/sistema/app/cola_local.py:232-250',
                                'native/bundle/rbx06_native_integral.py:395-407',
                                'native/owner_support_integral_v2.py:FiniteOfficialOwner.material'],
            'new_native_ticks': 0, 'automatic_resend': False,
            'scope': 'Only a pre-queue host budget intent may be archived; no queue, state, owner, principal or physics edits.'}

def write_new(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())

def transform_ledger(value, proof, proof_path, proof_sha):
    after = copy.deepcopy(value)
    need(after['intents'].get(LIFE) == proof['ledger_intent'], 'Intent changed')
    archive = after.setdefault('rejected_before_queue', [])
    need(isinstance(archive, list), 'Archive must be a list')
    archive.append({**proof['ledger_intent'], 'classification': 'REJECTED_BEFORE_QUEUE',
                    'no_native_target_row': True, 'new_native_ticks': 0,
                    'proof_path': str(proof_path), 'proof_sha256': proof_sha,
                    'critical_sha256': proof['critical_sha256'],
                    'reconciled_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    'automatic_resend': False})
    del after['intents'][LIFE]
    expected = copy.deepcopy(after); expected.pop('rejected_before_queue')
    original = copy.deepcopy(value); original.pop('rejected_before_queue', None); original['intents'].pop(LIFE)
    need(expected == original, 'Any change beyond sole intent/archive is forbidden')
    return after

def main():
    p = argparse.ArgumentParser(description=__doc__)
    modes = p.add_mutually_exclusive_group(required=True)
    modes.add_argument('--inspect', action='store_true')
    modes.add_argument('--apply-root-only', action='store_true')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--proof', type=Path)
    p.add_argument('--expected-proof-sha256')
    a = p.parse_args(); output = safe(a.output, exists=False)
    need(not output.exists(), 'Output must be new and absent')
    if a.inspect:
        proof = build_proof(); output.mkdir(parents=True)
        target = output / 'PRUEBA_NO_ADMITIDO_FUNCTION16.json'; write_new(target, proof)
        print(json.dumps({'mode': 'INSPECT_ONLY', 'proof': str(target), 'sha256': sha(target),
                          'ledger_modified': False, 'new_native_ticks': 0})); return
    need(a.proof is not None and a.expected_proof_sha256, 'Apply requires reviewed exact proof and SHA256')
    proof_path = safe(a.proof)
    need(sha(proof_path) == a.expected_proof_sha256, 'Reviewed proof hash mismatch')
    proof = read_json(proof_path)
    need(build_proof() == proof, 'Closed-state proof changed since review')
    lock = LEDGER.with_name(LEDGER.name + '.LOCK')
    token = os.urandom(16).hex(); fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        with os.fdopen(fd, 'w', encoding='utf8') as f:
            json.dump({'pid': os.getpid(), 'token': token, 'life': LIFE, 'purpose': 'known_not_admitted_FUNCTION16'}, f)
            f.flush(); os.fsync(f.fileno())
        need(build_proof() == proof, 'Proof changed under exclusive accounting lock')
        output.mkdir(parents=True)
        original = LEDGER.read_bytes()
        need(hashlib.sha256(original).hexdigest() == proof['ledger_sha256_before'], 'Ledger changed')
        with (output / 'LEDGER_ANTES_LITERAL.json').open('xb') as f:
            f.write(original); f.flush(); os.fsync(f.fileno())
        after = transform_ledger(json.loads(original), proof, proof_path, a.expected_proof_sha256)
        temp = LEDGER.with_name(LEDGER.name + '.KNOWN_NOT_ADMITTED_WRITING')
        write_new(temp, after)
        need(sha(LEDGER) == proof['ledger_sha256_before'], 'Concurrent ledger change before commit')
        os.replace(temp, LEDGER)
        need(proof['critical_sha256'] == {k: sha(ROOT / k) for k in proof['critical_sha256']},
             'CRITICAL: Native/state bytes changed; preserve all evidence')
        receipt = {'schema': 'DEE.RBX06.known_not_admitted.applied.R01', 'life': LIFE, 'id': TARGET,
                   'proof_path': str(proof_path), 'proof_sha256': a.expected_proof_sha256,
                   'ledger_sha256_before': proof['ledger_sha256_before'], 'ledger_sha256_after': sha(LEDGER),
                   'critical_before_after_equal': True, 'counters_before_after_equal': True,
                   'intent_removed': TARGET, 'archived_in': 'rejected_before_queue',
                   'native_queue_edited': False, 'new_native_ticks': 0, 'automatic_resend': False}
        write_new(output / 'CONCILIACION_APLICADA.json', receipt)
        print(json.dumps(receipt))
    finally:
        if lock.exists() and read_json(lock).get('token') == token:
            lock.unlink()

if __name__ == '__main__':
    main()
