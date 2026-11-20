"""Root-only orchestration helpers for the existing bounded public CLI.

Imports stdlib only. It never computes an actor answer or retries a request.
Actual evaluative checks occur after the existing owner produces the result.
"""
from pathlib import Path
import hashlib
import json
import sqlite3
import subprocess


def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def fresh_queue_ids(system, life, identifiers, *, absent_historical=()):
    card = read(Path(system) / 'estado/vidas' / life / 'VIDA.json')
    if card['life_id'] != life: raise ValueError('Existing life identity differs')
    db = Path(system) / 'estado/servicios_persistentes' / card['world_id'] / 'cola.sqlite3'
    if not db.is_file(): raise ValueError('No existing transport to continue; no implicit creation')
    expanded = [name + suffix for name in identifiers for suffix in ('', '_resume', '_pause', '_save')]
    with sqlite3.connect(db.resolve().as_uri() + '?mode=ro', uri=True) as c:
        for name in [*expanded, *absent_historical]:
            if c.execute('SELECT id FROM requests WHERE id=?', (name,)).fetchone() is not None:
                raise ValueError('ID already exists: inspect its actual result, never resend: ' + name)
        unresolved = c.execute("SELECT id,status FROM requests WHERE status IN ('queued','processing','uncertain')").fetchall()
        if unresolved: raise ValueError('Unresolved prior transport preserved: ' + repr(unresolved))
    return {'queue': str(db), 'read_only_SQLite': True, 'fresh_ids_and_suffixes': expanded,
        'historical_ids_proved_absent': list(absent_historical), 'unresolved': []}


def cli_request(python, system, life, command, identifier, output, *, diagnostic=False, material=False):
    if command not in ('pi04-coordinacion-estado', 'pi04-coordinacion-oportunidad'):
        raise ValueError('Only the two existing fixed transport commands')
    output = Path(output)
    stdout = output / (identifier + '.stdout.txt'); stderr = output / (identifier + '.stderr.txt')
    if stdout.exists() or stderr.exists(): raise ValueError('Prior CLI attempt preserved; no overwrite/repeat')
    args = [str(python), '-I', '-B', '-X', 'utf8', str(Path(system) / 'gestionar.py'),
        '--system-root', str(system), command, '--vida', life, '--id', identifier]
    if diagnostic: args.append('--diagnostico')
    if material: args.append('--material')
    r = subprocess.run(args, capture_output=True, text=True, encoding='utf8', errors='strict', timeout=660)
    stdout.write_text(r.stdout, encoding='utf8'); stderr.write_text(r.stderr, encoding='utf8')
    if r.returncode:
        raise RuntimeError('CLI stopped; preserve and inspect the SAME ID without resubmitting: ' + identifier + ', exit=' + str(r.returncode))
    value = json.loads(r.stdout)
    if value.get('status') != 'completed' or value.get('saved_and_paused') is not True:
        raise ValueError('Actual CLI is incomplete; do not repeat a material request')
    return {'command': args, 'returncode': r.returncode, 'result': value,
        'stdout': {'path': str(stdout), 'sha256': sha(stdout)}, 'stderr': {'path': str(stderr), 'sha256': sha(stderr)}}


def native_groups(row):
    groups = {'outer': row['requests']}
    arithmetic = row.get('native_arithmetic')
    if arithmetic is not None: groups['FI'] = arithmetic['native_operation']['native_trial']['requests']
    second = row.get('second_native_use')
    if second is not None and 'requests' in second: groups['MU'] = second['requests']
    unique = {}
    for label, items in groups.items():
        for req in items:
            receipt = req['receipt']; rid = req['id']
            if type(rid) is not int or rid != receipt['id'] or not row['before_tick'] <= receipt['requested_tick'] <= row['after_tick']:
                raise ValueError('Invalid/inherited Native receipt')
            if rid in unique and unique[rid] != receipt: raise ValueError('Contradictory receipt alias')
            unique[rid] = receipt
    statuses = [r['status'] for r in unique.values()]
    summary = {'unique_requested': len(unique), 'applied': sum(v == 'applied' for v in statuses),
        'rejected_or_other': sum(v != 'applied' for v in statuses), 'groups_raw_counts': {k: len(v) for k, v in groups.items()},
        'expected_outer': len(groups['outer']), 'context_samples': int(row['context_input_supplied'])}
    controller = row['native_input_summary']
    if controller['unique_requested'] != len(unique) or controller['applied'] != summary['applied']:
        raise ValueError('Controller/direct new Native receipt denominators disagree')
    return summary


def recorded_row(actual, primary):
    row = actual['result']['rows'][0]
    op = row['selected_operation']; left, right = row['spec']['left'], row['spec']['right']
    reference = left + right if op == 'suma' else left - right if op == 'diferencia' else None
    second = row.get('second_native_use') or {}
    return {'ordinal': row['ordinal'], 'stage': row['spec']['stage'], 'context': row['spec']['context'],
        'operands': [left, right], 'before_tick': actual['before_tick'], 'after_tick': actual['after_tick'],
        'first_choice': row['first_reader']['choice'], 'operation': op, 'actual_number': row['actual_numeric_result'],
        'offline_arithmetic_reference': reference, 'arithmetic_attempted': row['native_arithmetic'] is not None,
        'arithmetic_correct': type(row['actual_numeric_result']) is int and row['actual_numeric_result'] == reference,
        'second_choice': None if second.get('reader') is None else second['reader']['choice'],
        'actual_route': row['applied_route'], 'useful_product': row['useful_product'],
        'actual_failed': row['actual_failed'], 'returned_failed': row['returned_failed'],
        'reference_delta_before': row['bank_before'][0]['s_reg'] - row['bank_before'][1]['s_reg'],
        'reference_delta_after': row['bank_after'][0]['s_reg'] - row['bank_after'][1]['s_reg'],
        'first_NULL_preserved': row['first_NULL_preserved'], 'first_rejected_preserved': row['first_rejected_preserved'],
        'normalized_calendar': row['normalized_calendar'], 'primary': str(primary),
        'Native_inputs': native_groups(row), 'controller_native_input_summary': row['native_input_summary']}
