"""Reconcile technical release evidence; never feeds a participant or changes a wheel."""
from __future__ import annotations
import hashlib
import json
import ctypes
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
WHL = '09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
PYD = '17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'

def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8-sig'))

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def put(name, data):
    p = ROOT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    inherited = read('validation/INHERITED_PYTHON_FINAL.json')
    new = read('validation/installed_new_suites_final6_01/RESULT.json')
    differential = read('validation/TECHNICAL_DIFFERENTIAL_SUMMARY_final6.json')
    wheel = read('validation/WHEEL_INSPECTION_FINAL.json')
    sources = read('validation/SOURCE_DIFF.json')
    api = read('validation/API_DIFF_final6.json')
    assert inherited['tests_run'] == 61 and inherited['failures'] == inherited['errors'] == 0
    assert new['tests_run'] == new['passed'] == 21 and new['failures'] == new['errors'] == new['skipped'] == 0
    assert inherited['native_sha256'] == new['native_sha256'] == PYD
    assert new['wheel_sha256'] == wheel['wheel_sha256'] == WHL
    assert differential['status'] == 'PASS' and sources['kernel_byte_identical']
    assert api['name_surface_preserved'] and not api['removed_public_class_attributes']
    stages = []
    latest = {}
    for name in ('ctest.xml', 'ctest_directed.xml', 'ctest_final_affected.xml'):
        path = ROOT / 'candidate_final/validation' / name
        root = ET.parse(path).getroot()
        records = []
        for t in root.iter('testcase'):
            failure = t.find('failure')
            record = {'test': t.attrib['name'], 'seconds': float(t.attrib.get('time', '0')),
                      'status': 'FAIL' if failure is not None else 'SKIP' if t.find('skipped') is not None else 'PASS'}
            latest[record['test']] = record
            records.append(record)
        stages.append({'member': 'validation/native-build/' + name, 'sha256': sha(path), 'results': records})
    assert len(latest) == 23 and all(x['status'] == 'PASS' for x in latest.values())
    assert len(stages[-1]['results']) == 9 and all(x['status'] == 'PASS' for x in stages[-1]['results'])
    legacy = read('validation/legacy_actual_cpc7_final6_01/RESULT.json')
    assert all(legacy['checks'].values())
    remote = read('validation/remote_port45_final6_01/RESULT.json')
    assert sum(len(x['frames']) for x in remote['cases']) == 38
    absence = read('validation/absence_port45_final6_01/RESULT.json')
    assert absence['status'] == 'PASS' and absence['native_sha256'] == PYD
    assert sum(len(x['frames']) for x in absence['cases']) == 35
    report = {
      'schema': 'DEE45.validation-release.v1',
      'technical_status': 'FUNCTIONAL_CANDIDATE_VALIDATED; exact-ZIP release proof is external',
      'version': '4.5.0', 'kernel_version': 27,
      'final_wheel_sha256': WHL, 'final_native_sha256': PYD,
      'interpretation': 'A real compiled product with finite supported recipes and separate experimental Python profiles; no new scientific cognition claim.',
      'publication_gate': 'RELEASE_VERIFIED only when the delivered VERIFICACION_FINAL_EXTERNA.json identifies this exact ZIP and all bounded clean executions/assertions pass.',
      'identity_and_source': {'kernel_byte_identical': True, 'kernel_sha256': sources['kernel_sha256'],
        'source_audit': 'validation/SOURCE_DIFF.json', 'diff': 'validation/SOURCE_CHANGES.patch',
        'four_inherited_source_changes': 'Only UTF-8 filesystem conversion in Runtime and TraceSession I/O; exactly reversed by audit to recover all other inherited C++ source bytes.',
        'build': 'BUILD_INFO.json', 'wheel_RECORD_and_payload': 'validation/WHEEL_INSPECTION_FINAL.json'},
      'python': {'inherited': {'run': 61, 'passed': 61, 'failures': 0, 'errors': 0,
          'seconds': inherited['elapsed_seconds'], 'evidence': 'validation/INHERITED_PYTHON_FINAL.json'},
        'new': {'run': 21, 'passed': 21, 'failures': 0, 'errors': 0, 'skipped': 0,
          'groups': {'consolidated': 9, 'remote': 5, 'absence': 5, 'acquired_regulation': 2},
          'seconds': new['wall_seconds'], 'evidence': 'validation/installed_new_suites_final6_01/RESULT.json'}},
      'cpp': {'unique_completed_suites': 23, 'latest_passed': 23, 'final_affected_suites_passed': 9,
        'stages': stages, 'latest_by_suite': sorted(latest.values(), key=lambda x: x['test']),
        'scope': 'All23 completed successfully over directed stages. Nine affected suites rerun on final native source. Not a claim that all23 were rerun on final binary.',
        'primary': 'evidence/CPP_FINAL/OBSERVATIONS_CPP.jsonl',
        'external_consumer': 'Both new C++ API and byte-identical 4.0 consumer are in the exact-ZIP clean plan; their execution proof is external.'},
      'differential': {'neutral_runtime_cases': 48, 'cpc_ports': 10, 'finite_revision_ports': 6,
        'experimental_regulation_ports': 4, 'total_trajectories': 68,
        'backends_each_version': 32, 'cross_process_cross_version_continuations': 4,
        'result': 'PASS', 'source': 'validation/TECHNICAL_DIFFERENTIAL_SUMMARY_final6.json',
        'binary_binding': 'validation/FINAL6_ARTIFACT_BINDING.json',
        'objects': ['RAW uint64 arrays', 'clock uint64 arrays', 'tick', 'receipts', 'queues', 'channels', 'readouts', 'operational state'],
        'metadata_exclusions': differential['documental_exclusions'],
        'scope': 'These are finite tests and deterministic reproductions, not independent scientific replicas or exhaustive proof of all v27 states.'},
      'additional_ports': {'remote': {'histories': 3, 'full_frontiers': 38,
          'source': 'validation/remote_port45_final6_01/RESULT.json'},
        'absence': {'cases': 5, 'full_frontiers': 35,
          'source': 'validation/absence_port45_final6_01/RESULT.json',
          'scope': 'Five complete frozen4.0 comparisons repeated using the exact final6 native binary, plus installed API tests.'},
        'real_CPC7_snapshot': {'from_tick': 204, 'to_tick': 472,
          'source': 'validation/legacy_actual_cpc7_final6_01/RESULT.json',
          'physical_and_operative_exact': True,
          'limitation': 'Does not reconstruct external Python journal/captures; no historical original modified.'},
        'spanish_event_examples': {'passed': 3, 'source': 'validation/examples_final6/', 'fresh_executions_not_transcripts': True}},
      'new_recipe_panel': {
        'K65': {'rounds': 3, 'observations': 195, 'paired_directional_matches': 195,
          'blocks': [32, 33], 'domain': 'N131/gap2 finite cadence; 65 opaque forms, two directional classes; not65NSMmeanings',
          'no_event': '195 occupation rejections, not195 zeros',
          'unpaired': '130/195 later matches; queries can teach through residual encounters. First and later rounds retained.'},
        'selective_revision': {'methods': ['double_teacher', 'symmetric_counterflow'],
          'resources': 'Second teacher or two counterflows explicitly supplied; offpath controls may interfere with another memory.'},
        'U0': {'constructor': 'No target teaching map', 'sequence': 'history/comparison/question/access/action/post-name/new relation/revision',
          'question': 'State-conditioned prepared comparison/opportunity, not learned general curiosity'},
        'remote': 'Experimental N67 finite supply/read cadence, not open-ended access',
        'absence': 'Experimental separate prepared protocol, not fused with discrepancy profile',
        'regulation': 'Experimental directional acquired pulse/contact292/use437; paired/reserve useful5, unpaired/opposite4; not learned regulation-by-consequence policy'},
      'preserved_incidents': differential['instrumental_incidents'] + [
        {'kind': 'CPP_initial_timeout', 'count': 3, 'resolution': 'Directed larger bounded timeout, no test removed'},
        {'kind': 'CPP_version_literal', 'resolution': 'One assertion still expected4.0; changed expected version only; all66 organization checks pass'},
        {'kind': 'native_Unicode_IO', 'resolution': 'Four UTF8path conversions; Runtime+gzip+Trace Unicode cases in final clean plan'},
        {'kind': 'helper_partial_submission', 'resolution': 'Batch preflight before any submit; six invalid custom-world cases remain byte-exact'},
        {'kind': 'summary_instrument_key', 'resolution': differential['summary_instrument_repair']},
        {'kind': 'smoke_geometry_metadata', 'resolution': 'Exclude only inert initial_state_available descriptor flag; retain full physical and operative comparisons'},
        {'kind': 'example_call_signature', 'resolution': 'Caller advance(count, options) corrected to advance(count); no engine change'}],
      'remaining_limits': [
        'Only Windows x64 CPython3.13 regular cp313 and tested MSVC static C++ install supported here; no universal ABI promise.',
        'C++ paths use UTF-8; locale-encoded non-ASCII strings require explicit conversion.',
        'Use a short extraction path for Windows DLL loading. A deep launcher fixture failed while the same code/binario/events succeeded in the short-path fixture; the nominal260 check is not a universal guarantee.',
        'Remote/absence/acquired-regulation profiles are experimental bounded Python recipes, not new consolidated native constructors.',
        'Remote metadata validation is scoped to self-produced snapshots; no claim of fully hardened arbitrary application metadata.',
        'The native format retains inherited parser contracts; compression adds bounded validation, not arbitrary-code deserialization.',
        'Access and retention are finite and query-dependent; queries are physical interventions.',
        'NSM65 catalogue is distributed with evidence scopes, not a claim that65meanings were learned.'],
      'data_calculations_interpretation': {'data': 'evidence/, validation/*/RESULT.json, exact uint64 binaries and observations',
        'calculations': 'validation/tools/*, paired diffs, full array comparisons, explicit metadata normalization',
        'interpretation': 'INFORME_TECNICO.md; no automated scientific global verdict'}
    }
    report['delivery_engineering'] = {
        'metadata': 'Packaging verifier parses valid CRLF wheel METADATA using email.parser; final WHL bytes unchanged.',
        'launcher': 'SHA256 uses .NET rather than optional Get-FileHash. Same launcher passed short-path creation/offline install/two queries/save/load; all four earlier preflights retained.',
        'launcher_evidence': 'validation/launcher_preflight05_short/LAUNCHER_REPORT.json',
        'data_layout': 'validation/REVIEW_DATA_LAYOUT.json',
        'layout_decision': 'Keep complete per-case/version primary arrays and direct comparator paths. Their exact duplicates are measured and disclosed; no venv/toolchain or per-tick dense dump is packaged. Lossless ZIP compression keeps the delivery compact.'}
    clean_member = 'validation/clean_preliminary/CLEAN_REPORT.json'
    if (ROOT / clean_member).is_file():
        clean = read(clean_member)
        assert clean['status'] == 'VERIFIED' and len(clean['commands']) == 7
        assert len(clean['posttrajectory_assertions']) == 4
        assert all(c['status'] == 'COMPLETED' and c['exit_code'] == 0 for c in clean['commands'])
        report['preliminary_clean'] = {'status': 'VERIFIED', 'member': clean_member,
            'proof_sha256': sha(ROOT / clean_member), 'candidate_zip_sha256': clean['candidate_sha256'],
            'commands': 7, 'assertion_blocks': 4, 'seconds': clean['elapsed_seconds'],
            'scope': 'Exact PRE ZIP; current final executable source, installed wheel, C++ install and immutable plan. Subsequent changes are documentation/evidence only. Final exact ZIP still requires external proof.'}
    put('VALIDATION_REPORT.json', report)
    put('API_DIFF.json', dict(api, native_api='include/dee_thinking/consolidated.hpp',
        typing='source/python/dee_thinking/consolidated_native.pyi and Python facade .pyi',
        source_diff='validation/SOURCE_CHANGES.patch',
        cpp_compatibility='Source consumer4.0 compiled against installed4.5 in exact-ZIP proof; not binary ABI equivalence'))
    references = read('evidence/REFERENCES.json')
    put('PROVENANCE.json', {'schema': 'DEE45.provenance.v1', 'project': 'DEE Universe / INVESTIGACION DEE',
        'author': 'Ivan Erick Tlaltecatl Morales', 'task': 'Product consolidation4.0→4.5, private local build',
        'budget': read('BUDGET.json'), 'references': references,
        'final_wheel_sha256': WHL, 'final_native_sha256': PYD,
        'frozen_kernel_sha256': sources['kernel_sha256'],
        'source': 'Exact private build source under source/; inherited origins in evidence/SOURCE40_MANIFEST.json and source diff.',
        'selected_historical_members': 'evidence/ contains selected hashed source, configurations, fixtures and snapshots; complete historical ZIPs are NOT embedded.',
        'external_historical_requirements': 'Rerunning original4.0 requires its official WHL separately. Frozen neutral arrays/readouts are included for recalculation; final4.5 use needs only includedWHL.',
        'preservation': 'Original archives/products/manuals are never edited. Final publication rechecks reference hashes before/after.',
        'not_created': ['new definitive Maestro', 'Libro Blanco', 'Manual', 'Fisica DEE', 'remote publication', 'new kernel law'],
        'not_packaged': ['virtual environments', 'toolchains', 'historical ZIPs', 'intermediate candidate wheels'],
        'licensing': 'Existing notices retained; no new licence or third-party redistribution right invented.',
        'privacy': 'Private reconstructive artifact; includes scientific internals and is not an external-review-safe export.'})
    evidence_names = ['VALIDATION_REPORT.json', 'API_DIFF.json', 'BUILD_INFO.json',
        'validation/INHERITED_PYTHON_FINAL.json', 'validation/installed_new_suites_final6_01/RESULT.json',
        'validation/TECHNICAL_DIFFERENTIAL_SUMMARY_final6.json', 'validation/FINAL6_ARTIFACT_BINDING.json',
        'validation/SOURCE_DIFF.json', 'validation/WHEEL_INSPECTION_FINAL.json',
        'validation/remote_port45_final6_01/RESULT.json', 'validation/absence_port45_final6_01/RESULT.json',
        'validation/legacy_actual_cpc7_final6_01/RESULT.json']
    if (ROOT / clean_member).is_file():
        evidence_names.append(clean_member)
    put('revision/INDICE_EVIDENCIA.json', {'schema': 'DEE45.review-index.v1', 'files': [
        {'path': n, 'sha256': sha(ROOT / n), 'bytes': (ROOT / n).stat().st_size} for n in evidence_names],
        'cpp_reports': 'validation/native-build/ctest*.xml and evidence/CPP_FINAL/',
        'scope': 'Hashes of selected review inputs only; MANIFEST.json covers the complete delivered member set.'})
    budget = read('BUDGET.json')
    qpc = ctypes.c_longlong()
    if not ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(qpc)):
        raise OSError('Cannot read original monotonic clock')
    elapsed = (qpc.value - budget['start_qpc']) / budget['qpc_frequency']
    put('REANUDACION.json', {'schema': 'DEE45.work-checkpoint.v1', 'utc': datetime.now(timezone.utc).isoformat(),
        'budget': budget, 'elapsed_original_monotonic_seconds': elapsed,
        'physical_and_operational_states': ['evidence/CPP_FINAL/', 'evidence/legacy_CPC7_demo03/', 'validation/'],
        'source_audit_sha256': sha(ROOT / 'validation/SOURCE_DIFF.json'),
        'wheel_sha256': WHL, 'native_sha256': PYD,
        'last_complete_task': 'Final6 installed validation and finite differentials reconciled; scientific source and binary frozen.',
        'next_task_at_seal': 'Final exact-ZIP extraction and external proof, atomic publication; PRE clean already passed.' if (ROOT / clean_member).is_file() else 'Fresh PRE extraction/install, then final exact-ZIP extraction and external proof, atomic publication.',
        'final_completion_record': 'Delivered VERIFICACION_FINAL_EXTERNA.json and external publication proof supersede this pre-seal work checkpoint.',
        'resume_policy': 'No indefinite background work; a future campaign requires user authorization and a new explicit budget.'})
    print(json.dumps({'status': 'RECONCILED', 'cpp_unique_latest_pass': len(latest), 'python': 82,
                      'trajectories': 68, 'wheel_sha256': WHL}))

if __name__ == '__main__':
    main()
