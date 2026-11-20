"""Independent standard-library transport audit. Never imports the DEE engine."""
from __future__ import annotations
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import time
import zipfile

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent
DELIVERY = RUNS / 'resultados'
WORK = RUNS / 'RUN_20261019_165651'
SCRATCH = Path.cwd() / '_cpc9_union_final_audit'
BLOCK = 1024 * 1024
EXPECTED = {
    'DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip': (73601685, '412a6819e36203a0086790003301a13722bd14fd3a3213b03681d827f7cca1a2'),
    'CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip': (65870122, '917a559b917388fc63a6948762d73c3e87a00c30199c5b65c635a8d39bf96bad'),
}

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(BLOCK), b''):
            h.update(b)
    return h.hexdigest()

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def dump(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')

def identity(path):
    return {'bytes': path.stat().st_size, 'sha256': sha(path)}

def inventory(folder):
    return {p.name: identity(p) for p in sorted(folder.iterdir()) if p.is_file()}

def compare(a, b):
    count = 0
    with a.open('rb') as left, b.open('rb') as right:
        while True:
            x, y = left.read(BLOCK), right.read(BLOCK)
            require(x == y, 'Byte mismatch: ' + a.name)
            if not x:
                return count
            count += len(x)

def zip_hashes(path):
    with zipfile.ZipFile(path) as z:
        names = [x.filename for x in z.infolist() if not x.is_dir()]
        require(len(names) == len(set(names)), 'Duplicate ZIP entries')
        hash_names = [n for n in names if n.endswith('/HASHES.sha256')]
        require(len(hash_names) == 1, 'Exactly one internal hash index required')
        hash_name = hash_names[0]
        prefix = hash_name.removesuffix('HASHES.sha256')
        expected = {}
        for line in z.read(hash_name).decode('utf-8-sig').splitlines():
            if not line.strip() or line.startswith('#'):
                continue
            digest, rel = line.split('  ', 1)
            require(rel not in expected and not PurePosixPath(rel).is_absolute() and '..' not in PurePosixPath(rel).parts, 'Unsafe/duplicate hash row')
            expected[rel] = digest
        actual = {}
        total = 0
        for name in names:
            require(name.startswith(prefix), 'Unexpected ZIP root')
            h = hashlib.sha256()
            size = 0
            with z.open(name) as f:
                for block in iter(lambda: f.read(BLOCK), b''):
                    h.update(block)
                    size += len(block)
            actual[name[len(prefix):]] = {'sha256': h.hexdigest(), 'bytes': size}
            total += size
        require(set(expected) == set(actual) - {'HASHES.sha256'}, 'Internal HASHES coverage differs')
        for rel, digest in expected.items():
            require(actual[rel]['sha256'] == digest, 'Internal HASHES mismatch: ' + rel)
        if prefix + 'MANIFEST.json' in names:
            manifest = json.loads(z.read(prefix + 'MANIFEST.json'))
            for row in manifest['files']:
                require(actual[row['path']] == {'sha256': row['sha256'], 'bytes': row['bytes']}, 'Member differs from internal manifest: ' + row['path'])
        return {'zip_members': len(z.infolist()), 'expanded_bytes': total, 'hash_index_entries_verified': len(expected),
                'all_members_streamed_with_zip_crc_check': True, 'internal_hash_index_exact_coverage': True}

def main():
    started = time.monotonic()
    require(not SCRATCH.exists(), 'Scratch must be new: ' + str(SCRATCH))
    require(not (HERE / 'UNION_REAL_FINAL.json').exists() and not (HERE / 'AUDITORIA_ENTREGA_INDEPENDIENTE.json').exists(), 'Audit output already exists')
    before = inventory(DELIVERY)
    record = load(DELIVERY / 'VERIFICACION_FINAL.json')
    require(record['status'] == 'TWO_EXACT_ZIPS_VERIFIED_TRANSPORT_PENDING', 'Expected preclosure PENDING state')
    require(not (DELIVERY / 'HASHES_ENTREGA.sha256').exists(), 'Hash index should be issued by later closure')
    transport = load(DELIVERY / 'PARTES.json')
    require(transport['maximum_part_bytes'] == 16000000 and len(transport['archives']) == 2, 'Transport scope/limit')
    require({x['name'] for x in transport['archives']} == set(EXPECTED), 'Canonical names differ')
    tool = WORK / 'tools/dividir_verificar_entrega.py'
    tree = ast.parse(tool.read_text(encoding='utf-8'))
    merger = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'MERGER' for t in n.targets))
    require((DELIVERY / 'REUNIR_ENTREGA.py').read_bytes() == merger.encode('utf-8'), 'Delivered helper differs from sealed tool')
    part_rows = []
    for entry in transport['archives']:
        size, digest = EXPECTED[entry['name']]
        require((entry['bytes'], entry['sha256']) == (size, digest), 'Manifest canonical identity')
        require(before[entry['name']] == {'bytes': size, 'sha256': digest}, 'Published canonical identity')
        require([p['index'] for p in entry['parts']] == [1, 2, 3, 4, 5], 'Expected five consecutive parts')
        require(sum(p['bytes'] for p in entry['parts']) == size, 'Sum of part bytes')
        for part in entry['parts']:
            require(Path(part['name']).name == part['name'] and '/' not in part['name'] and '\\' not in part['name'] and ':' not in part['name'], 'Unsafe part name')
            require(0 < part['bytes'] <= 16000000, 'Part exceeds transfer limit')
            require(before[part['name']] == {'bytes': part['bytes'], 'sha256': part['sha256']}, 'Delivered part differs')
            part_rows.append(dict(part, actual_sha256=before[part['name']]['sha256'], actual_bytes=before[part['name']]['bytes']))
    require(len(part_rows) == 10 and len({p['name'] for p in part_rows}) == 10, 'Ten unique parts required')
    oversized = [name for name, row in before.items() if row['bytes'] > 16000000 and name not in EXPECTED]
    require(not oversized, 'Oversized noncanonical delivery files')
    cp = load(DELIVERY / 'PRUEBA_RECUPERACION_DESDE_CERO.json')
    ce = load(DELIVERY / 'VERIFICACION_CORE_FINAL_EXTERNA.json')
    ep = load(DELIVERY / 'VERIFICACION_CPC9_FINAL_EXTERNA.json')
    es = load(DELIVERY / 'SUPERVISION_FINAL_CPC9.json')
    for key in ('Core_proof', 'CPC9_proof'):
        proof = record[key]
        require(before[proof['file']]['sha256'] == proof['sha256'], 'Publication proof hash differs')
    core_sha = EXPECTED['DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip'][1]
    cpc9_sha = EXPECTED['CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip'][1]
    require(cp['status'] == ce['status'] == 'PASS' and cp['artifact_sha256'] == ce['artifact_sha256'] == core_sha, 'Core clean proof identity/status')
    require(ce['clean_recovery_proof_sha256'] == before['PRUEBA_RECUPERACION_DESDE_CERO.json']['sha256'], 'Core external proof link')
    require(len(cp['family_results']) == ce['family_count'] == 34 and all(v['status'] == 'PASS' for v in cp['family_results'].values()), 'Core 34-family results')
    require(all(c['status'] == 'PASS' and c['exit_code'] == 0 for c in cp['commands']), 'Core commands')
    require(cp['no_artifact_changes'] and cp['all_requested_families_passed'] and cp['blocked_external_reads'] == 0, 'Core proof limits')
    require(ep['status'] == 'VERIFIED_EXACT_ZIP' and ep['zip_sha256'] == ep['zip_sha256_after'] == cpc9_sha, 'CPC9 exact proof identity/status')
    require(len(ep['commands']) == 9 and all(c['exit_code'] == 0 for c in ep['commands']), 'CPC9 command exit codes')
    require({p['proof'] for p in ep['proofs']} == {'parser', 'demo', 'control', 'reference-baseline', 'reference-restored', 'integral', 'recalculate'}, 'CPC9 seven proof scope')
    require(all(p['status'] == 'PASSED' and not p['denied_operations'] for p in ep['proofs']), 'CPC9 proofs')
    require(not ep['manifest_failures_before'] and not ep['manifest_failures_after'], 'CPC9 sealed member proof')
    for supervision in (ce['supervision'], es):
        require(supervision['status'] == 'COMPLETED' and supervision['exit_code'] == 0 and supervision['owned_worker_waited'] and supervision['owned_job_closed'], 'Owned worker not closed')
    original_cpc9 = Path(es['argv'][es['argv'].index('--zip') + 1])
    originals = [(Path(cp['artifact']), core_sha), (original_cpc9, cpc9_sha)]
    originals += [(Path(x['path']), x['expected_sha256']) for x in record['protected_ancestors_rechecked']]
    original_rows = []
    for path, expected in originals:
        actual = identity(path)
        require(actual['sha256'] == expected, 'Protected original changed: ' + str(path))
        original_rows.append({'path': str(path), **actual, 'expected_sha256': expected, 'unchanged': True})
    errata = load(DELIVERY / 'ERRATAS_EDITORIALES_EXTERNAS.json')
    require(len(errata['entries']) == 1, 'Unexpected editorial scope')
    erratum = errata['entries'][0]
    text = (DELIVERY / erratum['file']).read_text(encoding='utf-8')
    require(erratum['corrected_text'] in text and erratum['previous_text'] not in text, 'External erratum not reflected')
    require(not erratum['scientific_measurements_changed'] and not erratum['sealed_archives_changed'] and not erratum['operational_code_changed'], 'Erratum scope changed')
    SCRATCH.mkdir()
    command = [sys.executable, '-I', '-B', str(DELIVERY / 'REUNIR_ENTREGA.py'), '--manifest', str(DELIVERY / 'PARTES.json'), '--out', str(SCRATCH)]
    run = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
    require(run.returncode == 0, 'Actual merger failed: ' + run.stderr)
    union_rows = []
    for name, (size, digest) in EXPECTED.items():
        rebuilt = SCRATCH / name
        require(identity(rebuilt) == {'bytes': size, 'sha256': digest}, 'Actual reconstructed identity')
        compared = compare(DELIVERY / name, rebuilt)
        require(compared == size, 'Incomplete byte comparison')
        internal = zip_hashes(rebuilt)
        published = next(a for a in record['artifacts'] if a['name'] == name)
        require(internal['zip_members'] == published['zip_members'] and internal['expanded_bytes'] == published['expanded_bytes'], 'ZIP contents differ from publication receipt')
        union_rows.append({'name': name, 'bytes': size, 'sha256': digest, 'byte_comparison_count': compared, 'full_byte_comparison_verified': True, **internal})
    rebuilt_before = inventory(SCRATCH)
    rerun = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
    require(rerun.returncode == 0 and inventory(SCRATCH) == rebuilt_before, 'Exact existing output changed')
    conflict_dir = SCRATCH / 'conflicting_destination'
    conflict_dir.mkdir()
    first = next(iter(EXPECTED))
    sentinel = conflict_dir / first
    with sentinel.open('xb') as f:
        f.write(b'INDEPENDENT AUDIT SENTINEL: PRESERVE EXISTING OUTPUT\n')
    sentinel_before = identity(sentinel)
    conflicting_command = command[:-1] + [str(conflict_dir), '--archivo', first]
    conflict = subprocess.run(conflicting_command, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
    require(conflict.returncode != 0 and identity(sentinel) == sentinel_before, 'Conflicting existing output was replaced')
    require(inventory(DELIVERY) == before, 'Delivery bytes changed during independent audit')
    for row in original_rows:
        require(identity(Path(row['path'])) == {'bytes': row['bytes'], 'sha256': row['sha256']}, 'Original changed during audit')
    union = {'schema': 'CPC9.independent.actual.union.v1', 'status': 'PASS', 'verified_utc': datetime.now(timezone.utc).isoformat(),
             'helper': {'path': str(DELIVERY / 'REUNIR_ENTREGA.py'), **before['REUNIR_ENTREGA.py'], 'equals_sealed_splitter_merger': True},
             'manifest': {'path': str(DELIVERY / 'PARTES.json'), **before['PARTES.json']},
             'command': command, 'returncode': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr,
             'scratch': str(SCRATCH), 'archives': union_rows, 'total_bytes_compared': sum(x['byte_comparison_count'] for x in union_rows),
             'existing_exact_outputs_verified_unchanged': {'returncode': rerun.returncode, 'stdout': rerun.stdout, 'passed': True},
             'conflicting_existing_output_preserved': {'returncode': conflict.returncode, 'stderr': conflict.stderr, 'sentinel': str(sentinel), **sentinel_before, 'passed': True},
             'scientific_runtime_executed': False, 'delivery_files_changed': False, 'originals_changed': False}
    union_path = HERE / 'UNION_REAL_FINAL.json'
    dump(union_path, union)
    audit = {'schema': 'CPC9.independent.actual.delivery.audit.v1', 'status': 'APPROVED_FOR_EXTERNAL_CLOSURE',
             'verified_utc': datetime.now(timezone.utc).isoformat(), 'delivery': str(DELIVERY),
             'scope': 'Transport identity, actual helper reconstruction, complete byte comparison, ZIP member hashes/CRC and recorded proof identity only; no new scientific claim or scientific runtime execution.',
             'preclosure_status': record['status'], 'preclosure_pending_is_expected': True,
             'final_delivery_hash_index': 'Not yet issued; expected only at subsequent external closure. Existing per-part/internal/proof hashes verified now.',
             'union_report': {'path': str(union_path), **identity(union_path)},
             'part_count': len(part_rows), 'maximum_allowed_part_bytes': 16000000, 'maximum_actual_part_bytes': max(p['bytes'] for p in part_rows),
             'parts': part_rows, 'canonical_archives': union_rows, 'delivery_inventory_before_and_after_equal': before,
             'protected_originals_before_and_after': original_rows,
             'proof_receipts': {'Core': {'status': cp['status'], 'families': len(cp['family_results']), 'commands': len(cp['commands']), 'proof_sha256': before['PRUEBA_RECUPERACION_DESDE_CERO.json']['sha256'], 'external_attestation_sha256': before['VERIFICACION_CORE_FINAL_EXTERNA.json']['sha256']},
                                'CPC9': {'status': ep['status'], 'commands': len(ep['commands']), 'proofs': len(ep['proofs']), 'proof_sha256': before['VERIFICACION_CPC9_FINAL_EXTERNA.json']['sha256'], 'supervision_sha256': before['SUPERVISION_FINAL_CPC9.json']['sha256']},
                                'owned_workers_completed_waited_jobs_closed': True},
             'external_editorial_errata_verified': {'file': 'ERRATAS_EDITORIALES_EXTERNAS.json', **before['ERRATAS_EDITORIALES_EXTERNAS.json'], 'entries': errata['entries']},
             'all_noncanonical_transfer_files_under_limit': True, 'sealed_work_and_delivery_mutated_by_auditor': False,
             'elapsed_seconds': time.monotonic() - started, 'remaining_required_step': 'Run external CERRAR_ENTREGA_CPC9.py to issue final receipt and final delivery hash index.'}
    audit_path = HERE / 'AUDITORIA_ENTREGA_INDEPENDIENTE.json'
    dump(audit_path, audit)
    print(json.dumps({'status': audit['status'], 'parts': len(part_rows), 'max_part_bytes': audit['maximum_actual_part_bytes'], 'byte_comparison_count': union['total_bytes_compared'],
                      'reports': [{'path': str(p), **identity(p)} for p in (union_path, audit_path)], 'elapsed_seconds': audit['elapsed_seconds']}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
