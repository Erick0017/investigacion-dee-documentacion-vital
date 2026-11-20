"""Directed static review of the three inherited code deltas requested by Root."""
from pathlib import Path
import ast
import datetime
import difflib
import hashlib
import json

P = Path(__file__).resolve().parents[1]
R = P.parents[2]
A = R / 'DEE Cognitive 2.0/sistema'
B = P / 'estados/candidato_R02/sistema'
FILES = ('app/cola_local.py', 'app/mundo_genesis_apd05.py', 'capacidades/pi03_suministro_explicito_R03.py')


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def funcs(text):
    result = {}
    for n in ast.parse(text).body:
        if isinstance(n, ast.FunctionDef): result[n.name] = ast.dump(n, include_attributes=False)
        elif isinstance(n, ast.ClassDef):
            for f in n.body:
                if isinstance(f, ast.FunctionDef): result[n.name + '.' + f.name] = ast.dump(f, include_attributes=False)
    return result


def main():
    out = P / 'control/REVISION_TRES_DELTAS_HEREDADOS_PI04.json'
    if out.exists(): raise ValueError('Preserve previous review')
    records = []
    for name in FILES:
        x, y = A / name, B / name
        hx, hy = sha(x), sha(y)
        xt, yt = x.read_text(encoding='utf-8-sig'), y.read_text(encoding='utf-8-sig')
        xf, yf = funcs(xt), funcs(yt)
        records.append({'file': name, 'product_path': str(x), 'candidate_path': str(y),
            'product_sha256': hx, 'candidate_sha256': hy,
            'changed_existing_functions': [k for k in xf if k in yf and xf[k] != yf[k]],
            'new_functions': sorted(set(yf)-set(xf)), 'removed_functions': sorted(set(xf)-set(yf)),
            'unified_diff': ''.join(difflib.unified_diff(xt.splitlines(True), yt.splitlines(True), fromfile='PRODUCT/' + name, tofile='S2/' + name, n=4)),
            'hashes_unchanged_after_read': sha(x) == hx and sha(y) == hy})
    assert all(r['hashes_unchanged_after_read'] and not r['removed_functions'] for r in records)
    review = {
        FILES[0]: {
            'change': 'One early explicit eci01-pi04-* literal-validation branch delegates to fixed pi04_dispatcher; all other transport code is unchanged.',
            'Native_contribution': 'No Native request or decision is computed. Dispatcher selects a plugin only from the requested instrument mode, not from an answer, target, result or policy.',
            'preserved': 'SQLite schema, FIFO/control precedence, IDs, deduplication, admission capacities and every old validation branch.',
            'risk_or_limit': 'PI04 literals now require the preserved dispatcher/plugin files. Missing or invalid modules refuse admission instead of falling through to old ECI01 validation.'},
        FILES[1]: {
            'change': 'Register PI04 dependencies/source hashes on open; route explicit PI04 validation/execution through dispatcher; expose dependency status and OR its uncertainty into the existing owner stop/pause condition.',
            'Native_contribution': 'Only an explicitly requested protocol can call Native through its original plugin. This hook does not select a capability by the environmental answer or synthesize a response.',
            'preserved': 'All existing PI03/ECI/old handlers and downstream Native laws. The before_mutation label PI04_EXPLICIT_DIAGNOSTIC_PROTOCOL is administrative, including later explicitly admitted uses.',
            'risk_or_limit': 'Opening/continuing a world with present PI04 metadata now requires its complete coherent journals/devices/code. A pending/uncertain PI04 future blocks automatic resume. This is a safety effect, not learned recovery. Product0tick reopen remains the required compatibility check.'},
        FILES[2]: {
            'change': 'Versioned metadata-size fix: preflight prospective encoded task metadata against the frozen1MiB value bound before journal append; compact only new resource_supply_history source entries into SHA-addressed FUENTES artifacts while retaining current_resource_source and all old full-source history.',
            'Native_contribution': 'Existing actual-source integer codec and optional explicit Native recalculation are unchanged. Neither a desired answer nor a policy is reconstructed from the deduplicated provenance.',
            'preserved': 'Old entries are not rewritten or deleted. Native source source_payload/callback, resource bytes/actual-payload codec, task opportunity/clock, results, schedules and counters are not reset.',
            'risk_or_limit': 'New FUENTES artifacts are indispensable continuity/provenance dependencies and must travel with a full pair. The size preflight can refuse a future supply instead of appending an uncommittable journal; it does not promise indefinite supply or remove past quota failures.'}}
    for row in records: row['review'] = review[row['file']]
    source = B / 'capacidades/pi04_dispatcher.py'
    text = source.read_text(encoding='utf8')
    dispatcher = {'path': str(source), 'sha256': sha(source),
        'read_complete_as_text': True, 'routing': 'PLUGINS fixed6 prefixes; _for uses row.modo prefix only',
        'dependency_behavior': 'operational_dependencies/uncertain aggregate present plugins; code_files hashes preserved modules',
        'no_actor_result_or_environment_target_used_for_routing': True}
    proof = {'schema': 'DEE.PI04.inherited_delta.static_review.v1',
        'inspected_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'mode': 'STATIC_SOURCE_REVIEW_NOT_NATIVE_OR_AUTOMATIC_ADOPTION', 'new_Native_ticks': 0,
        'read_scope': 'All bytes/text of the3 files parsed and compared programmatically. Semantic reading covered every changed hunk/function plus the complete fixed dispatcher and explicit-supply dispatch/validation helpers; unchanged legacy function bodies were not all reread.',
        'files': records, 'dispatcher': dispatcher,
        'conclusion': 'The3 deltas are bounded PI04 routing/safety/provenance integration. They must be explicit approved files in the final code diff, rather than silently assumed unchanged. Static review finds no hidden actor policy or kernel/Thinking rewrite in these deltas.',
        'required_operational_evidence': ['Actual immutable-capsule Native cold20 proof already obtained by Root',
            'Product complete-state import and0tick reopen with pending reconciliation after deployment',
            'Actual postcommit public CLI crossed23 use, with recorded true output/effect, before claiming operational closure'],
        'originals_modified_by_review': False,
        'limits': 'This review covers3 exact deltas and their fixed dispatcher, not every line of the19-file deployment or a general safety proof. Source and product code hashes were stable during this read; no claim of project-wide immutability.'}
    with out.open('x', encoding='utf8') as f: json.dump(proof, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps({'proof': str(out), 'sha256': sha(out), 'files':3,'Native_ticks':0,'no_hidden_decision_detected_in_scope':True},ensure_ascii=False))


if __name__ == '__main__': main()
