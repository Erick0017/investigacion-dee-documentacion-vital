"""Passive finalization of an ACTUAL closed cold C2C20 replay; no Native.

Refuses RUNNING/partial results. Recounts direct receipts and checks actual
product files. Writes one campaign witness, never edits recipe/selection.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import sys

P = Path(__file__).resolve().parents[1]


def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def primary(root, name):
    r = Path(name)
    if r.is_absolute() or '..' in r.parts: raise ValueError('Relative primary only')
    p = root / r
    if p.is_symlink() or not p.resolve(strict=True).is_relative_to(root.resolve()): raise ValueError('Unsafe primary')
    return p


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--resultado', type=Path, default=P / 'estados/RP_C2C_COLD20_OP2/RESULTADO_REPRODUCCION.json')
    ap.add_argument('--salida', type=Path, default=P / 'control/C2C_COLD20_NATIVE_VERIFICADA_R01.json')
    a = ap.parse_args(); file = a.resultado.resolve(strict=True); root = file.parent
    if not root.is_relative_to((P / 'estados').resolve()) or file.name != 'RESULTADO_REPRODUCCION.json':
        raise ValueError('Exact PI04 diagnostic result only')
    result = read(file); context = read(root / 'CONTEXTO_EJECUCION.json'); imported = read(root / 'IMPORTACION_DIAGNOSTICA.json')
    if result.get('status') != 'COMPLETED' or result.get('owner_closed_coherently') is not True or result.get('criteria_met') is not True:
        raise ValueError('Actual full closed fixed-criterion replay is not available yet; no premature verification')
    if result['recipe'] != 'pi04_c2c_adquisicion_20_R01' or result['variant'] != 'real' or result['life'] != context['life']:
        raise ValueError('Only the genuine current cold C2C20 real case')
    if result['batches_closed'] != 2 or len(result['rows']) != 23 or result['last_tick'] != 816019:
        raise ValueError('Full actual prepare/admit/20/final-state trajectory required')
    if imported['new_native_ticks'] != 0 or imported['result']['physical']['tick'] != 800379 or not imported['comparison']['physical_equal'] or not imported['comparison']['causal_prefix_equal']:
        raise ValueError('Genuine coherent pre-C2C800379 prefix import is not demonstrated')
    if sha(Path(context['prefix']) / 'EXPORTACION_SERVICIO.json') != context['prefix_manifest_sha256']:
        raise ValueError('Original full prefix identity changed')
    sys.path.insert(0, str(P / 'codigo'))
    from pi04_verificacion_cli_publica_R01 import native_groups
    rows = []; ids = {}; products = []; final = None
    for transport in result['rows']:
        p = primary(root, transport['primary']); raw = read(p)
        if raw['id'] != transport['transport_id'] or raw['status'] != 'completed': raise ValueError('Primary request mismatch')
        actual = json.loads(raw['result']) if isinstance(raw['result'], str) else raw['result']
        if transport['step'] == 'final_state': final = actual; continue
        if not transport['step'].startswith('opportunity_'):
            if actual['before_tick'] != actual['after_tick']: raise ValueError('Administrative prefix step advanced time')
            continue
        r = actual['result']['rows'][0]; summary = native_groups(r)
        left, right = r['spec']['left'], r['spec']['right']
        expected_number = left + right if r['selected_operation'] == 'suma' else left - right if r['selected_operation'] == 'diferencia' else None
        arithmetic_correct = type(r['actual_numeric_result']) is int and r['actual_numeric_result'] == expected_number
        if not arithmetic_correct: raise ValueError('Actual Native arithmetic differs; preserve the discrepancy')
        if r['ordinal'] != len(rows) or r['first_NULL_preserved'] or r['first_rejected_preserved']:
            raise ValueError('Partial/NULL/rejected scientific future must remain preserved, not verified20')
        if summary['unique_requested'] != summary['applied'] or summary['rejected_or_other']:
            raise ValueError('Incomplete direct Native admission')
        for group in (r['requests'], r['native_arithmetic']['native_operation']['native_trial']['requests'], r['second_native_use']['requests']):
            for q in group:
                rid = q['id']; receipt = q['receipt']
                if rid in ids and ids[rid] != receipt: raise ValueError('Native alias changed')
                ids[rid] = receipt
        product = r['actual_effect']['product']
        if r['useful_product'] is not (product is not None): raise ValueError('Product counter differs from real effect')
        if product is not None:
            f = root / 'sistema/estado/servicios_locales' / result['life'] / 'PI04_C2C_COORDINACION_R01/dispositivo' / product['path']
            b = f.read_bytes()
            if len(b) != product['bytes'] or sha(f) != product['sha256'] or int.from_bytes(b[:2], 'little') != r['actual_numeric_result']:
                raise ValueError('Actual64-byte output does not carry the actual Native result')
            products.append({'ordinal': r['ordinal'], 'bytes': len(b), 'sha256': sha(f), 'actual_integer': r['actual_numeric_result']})
        rows.append({'ordinal': r['ordinal'], 'before_tick': r['before_tick'], 'after_tick': r['after_tick'],
            'useful_product': r['useful_product'], 'actual_integer': r['actual_numeric_result'],
            'arithmetic_correct': arithmetic_correct,
            'first_choice': r['first_reader']['choice'], 'second_choice': r['second_native_use']['reader']['choice'],
            'Native_inputs': summary, 'primary_sha256': sha(p)})
    if len(rows) != 20 or len(products) != 19 or sum(r['useful_product'] for r in rows[12:20]) != 8 or len(ids) != 3720 or any(r['status'] != 'applied' for r in ids.values()):
        raise ValueError('Observed original20 invariants differ; preserve discrepancy')
    if final is None: raise ValueError('No actual final state primary')
    phys = final['committed_snapshot']['physical']
    if phys['N'] != 67 or phys['tick'] != 816019 or final['result']['rows'][0]['progress']['ordinal'] != 20:
        raise ValueError('Exact final cold physical/counter cut differs')
    checks = result['final_checks']
    if len(checks) != 50 or not all(c['criterion_met'] is True for c in checks): raise ValueError('The frozen checks are incomplete')
    events = [json.loads(line) for line in (root / 'ENSAYOS.jsonl').read_text(encoding='utf8').splitlines() if line.strip()]
    starts = {r['run']: r for r in events if r.get('kind') == 'OWNER_STARTED' and r.get('life') == result['life']}
    closes = {r['run']: r for r in events if r.get('kind') == 'OWNER_CLOSED' and r.get('life') == result['life']}
    if set(starts) != set(closes) or len(closes) != 2 or any(r['exit_code'] != 0 for r in closes.values()):
        raise ValueError('The two actual owners have not both closed exit0')
    witness = {'schema': 'DEE.PI04.C2C.cold_Native_replay.verified.v1',
        'status': 'NATIVE_REPLAY_VERIFIED', 'checked_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'Native_executed': True, 'verification_new_Native_ticks': 0, 'life_id': result['life'], 'N': 67,
        'initial_tick': 800379, 'final_tick': 816019, 'actual_replay_Native_ticks': 15640,
        'closed': True, 'owner_closed_coherently': True, 'owners_closed_exit0': len(closes),
        'opportunities': 20, 'products': 19, 'reserved_opportunities': 8, 'reserved_products': 8,
        'arithmetic_correct': 20,
        'Native_inputs_unique': 3720, 'Native_inputs_applied': 3720, 'Native_inputs_rejected_or_other': 0,
        'fixed_checks': 50, 'fixed_checks_met': 50, 'final_physical': phys,
        'original_expected_Native_RAW_clocks_matched': True, 'rows': rows, 'actual_products': products,
        'recipe': result['recipe'], 'recipe_sha256_at_run': context['recipe_sha256'],
        'source_capsule_key': context['source_code_capsule_key'],
        'source_capsule_manifest_sha256': context['source_code_manifest_sha256'],
        'source_prefix_manifest_sha256': context['prefix_manifest_sha256'],
        'result': {'path': str(file), 'sha256': sha(file)},
        'context': {'path': str(root / 'CONTEXTO_EJECUCION.json'), 'sha256': sha(root / 'CONTEXTO_EJECUCION.json')},
        'no_principal_promotion_or_recipe_edit': True,
        'limits': 'One actual deterministic replay from a genuine shared prefix, not an independent organism or general agency. Public-manager OP3 transport correction is a separate instrument delta; this replay used its immutable OP2 direct runner/owner capsule.'}
    out = a.salida.resolve()
    if not out.is_relative_to((P / 'control').resolve()) or out.exists(): raise ValueError('NEW campaign control witness only')
    with out.open('x', encoding='utf8') as f: json.dump(witness, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps({'proof': str(out), 'sha256': sha(out), 'status': witness['status'], 'verification_Native_ticks': 0}))


if __name__ == '__main__': main()
