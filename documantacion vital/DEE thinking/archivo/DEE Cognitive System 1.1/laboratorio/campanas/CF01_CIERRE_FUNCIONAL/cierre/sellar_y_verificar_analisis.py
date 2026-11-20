"""Seal the immutable compact CF01 staging and verify its exact ZIP bytes.

Only Python stdlib. No DEE import, Runtime, ticks, staging edits or snapshot use.
The external proof identifies the final container without a circular hash.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STAGE = HERE / 'PAQUETE_ANALISIS'
DESTINATION = ROOT / 'entregas/DEE_COGNITIVE_CF01_CIERRE_FUNCIONAL_ANALISIS.zip'
PROOF = ROOT / 'entregas/VERIFICACION_ANALISIS_CF01_EXTERNA.json'
MANIFEST = 'MANIFIESTO_HASHES.json'
WORD = 'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_9_CF01_SIN_VALIDACION_VISUAL.docx'
WORD_SHA = 'a48eb2c28d26ce7162a851800e98d2fff82775a672aa3cd64cc62ec4f338269e'
MAXIMUM_BYTES = 16000000
SCRIPTS = ('recalcular_primarios_cf01.py', 'recalcular_tarea_cf01.py', 'recalcular_contexto_cf01.py',
           'recalcular_compuesto_cf01.py', 'recalcular_servicio_v3_cf01.py', 'recalcular_post_cal8_cf01.py')


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def put(path, value):
    temporary = path.with_name(path.name + '.pending.' + uuid.uuid4().hex)
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    os.replace(temporary, path)


def inventory(directory):
    result = {}
    for path in sorted(directory.rglob('*')):
        if path.is_symlink():
            raise ValueError('Symlink is not admitted in closed staging: ' + str(path))
        if path.is_file():
            relative = path.relative_to(directory).as_posix()
            result[relative] = {'bytes': path.stat().st_size, 'sha256': sha(path)}
    return result


def safe_member(name):
    relative = PurePosixPath(name)
    if relative.is_absolute() or '..' in relative.parts or '\\' in name or ':' in name:
        raise ValueError('Unsafe ZIP member: ' + name)
    return relative


def check_manifest(inv, manifest):
    assert manifest['self_hash_excluded'] is True
    rows = manifest['members']
    expected = {row['path']: {'bytes': row['bytes'], 'sha256': row['sha256']} for row in rows}
    assert len(expected) == len(rows), 'Duplicate manifest entry'
    assert set(inv) == set(expected) | {MANIFEST}, 'Manifest scope differs from staging members'
    assert {key: value for key, value in inv.items() if key != MANIFEST} == expected
    for name in inv:
        safe_member(name)
    assert len({name.casefold() for name in inv}) == len(inv), 'Case-insensitive name collision'
    assert inv[WORD]['sha256'] == WORD_SHA
    return len(expected)


def archive_existing(path, directory):
    if not path.exists():
        return None
    actual = sha(path)
    directory.mkdir(parents=True, exist_ok=True)
    saved = directory / (path.stem + '.' + actual + path.suffix)
    if saved.exists():
        assert sha(saved) == actual
    else:
        shutil.copy2(path, saved)
        assert sha(saved) == actual
    return {'original': str(path), 'sha256': actual, 'bytes': path.stat().st_size, 'preserved': str(saved)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tests-root', type=Path)
    args = parser.parse_args()
    started = time.monotonic()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:6]
    tests = args.tests_root.resolve() if args.tests_root else next(path for path in ROOT.parents if path.name == 'tests')
    extraction = tests / ('_cf01_analysis_verified_' + stamp)
    external = tests / ('_cf01_analysis_recalculated_' + stamp)
    assert extraction.resolve().is_relative_to(tests) and external.resolve().is_relative_to(tests)
    assert not extraction.exists() and not external.exists()
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    prior = archive_existing(DESTINATION, DESTINATION.parent / 'historico_cf01')
    prior_proof = archive_existing(PROOF, PROOF.parent / 'historico_cf01')
    original_destination_identity = sha(DESTINATION) if DESTINATION.exists() else None
    candidate = DESTINATION.with_name(DESTINATION.stem + '.candidate.' + stamp + '.zip')
    report = {'schema': 'CF01.exact_analysis_zip.external_verification.v1', 'started_utc': datetime.now(timezone.utc).isoformat(),
              'same_machine_new_extraction_only': True, 'new_native_ticks': 0, 'no_snapshots_or_DEE_imports': True,
              'original_staging': str(STAGE), 'extraction': str(extraction), 'recalculation_output': str(external),
              'prior_zip_preserved': prior, 'prior_proof_preserved': prior_proof, 'commands': []}
    try:
        initial = inventory(STAGE)
        manifest = json.loads((STAGE / MANIFEST).read_text(encoding='utf-8'))
        covered = check_manifest(initial, manifest)
        with zipfile.ZipFile(candidate, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9, allowZip64=True) as archive:
            for name in sorted(initial):
                archive.write(STAGE / name, name)
        assert candidate.stat().st_size <= MAXIMUM_BYTES, 'Compact analysis exceeds16000000bytes'
        with zipfile.ZipFile(candidate, 'r') as archive:
            assert archive.testzip() is None, 'ZIP CRC failure'
            assert archive.namelist() == sorted(initial), 'Member order/list mismatch'
            assert len(set(archive.namelist())) == len(initial)
            for name, expected in initial.items():
                data = archive.read(name)
                assert len(data) == expected['bytes'] and hashlib.sha256(data).hexdigest() == expected['sha256'], name
            assert json.loads(archive.read(MANIFEST)) == manifest
            extraction.mkdir()
            for name in archive.namelist():
                relative = safe_member(name)
                target = extraction.joinpath(*relative.parts)
                assert target.resolve().is_relative_to(extraction.resolve())
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(name) as source, target.open('xb') as output:
                    shutil.copyfileobj(source, output, 1024 * 1024)
        assert inventory(extraction) == initial, 'Exact extraction differs'
        assert sha(extraction / WORD) == WORD_SHA
        external.mkdir()
        evidence = external / 'evidence_with_materialized_source'
        evidence.mkdir()
        for path in sorted((extraction / 'EVIDENCIA_CAUSAL').glob('*.json.gz')):
            shutil.copyfile(path, evidence / path.name)
        materializer = extraction / 'RECALCULO/materializar_codigo_cf01.py'
        spec = importlib.util.spec_from_file_location('cf01_extracted_materializer', materializer)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        materialized = module.materialize(extraction / 'CODIGO_EJECUTADO/INDICE_CONTENIDOS.json', evidence / 'codigo_ejecutado')
        deadline = datetime.fromisoformat(json.loads((HERE.parent / 'PRESUPUESTO.json').read_text(encoding='utf-8'))['deadline_utc'])
        results = external / 'results'
        results.mkdir()
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        environment.pop('PYTHONPATH', None)
        for name in SCRIPTS:
            script = extraction / 'RECALCULO' / name
            output = results / (Path(name).stem + '.json')
            argv = [sys.executable, '-X', 'utf8', '-I', '-B', '-S', str(script), '--evidence', str(evidence), '--out', str(output)]
            remaining = (deadline - datetime.now(timezone.utc)).total_seconds() - 30
            if remaining <= 0:
                raise TimeoutError('Original CF01 deadline reached; no recalculation launched')
            before = time.monotonic()
            command = subprocess.run(argv, cwd=extraction, env=environment, capture_output=True, text=True,
                                     encoding='utf-8', timeout=min(120, remaining))
            row = {'argv': argv, 'cwd': str(extraction), 'returncode': command.returncode,
                   'stdout': command.stdout, 'stderr': command.stderr, 'seconds': time.monotonic() - before,
                   'result': str(output), 'result_sha256': sha(output) if output.exists() else None,
                   'site_packages_disabled_with_minus_S': True, 'new_native_ticks': 0}
            report['commands'].append(row)
            put(external / 'PROGRESS.json', report)
            if command.returncode:
                raise RuntimeError(name + ' failed: ' + command.stderr)
        load = lambda name: json.loads((results / (name + '.json')).read_text(encoding='utf-8'))
        primaries = load('recalcular_primarios_cf01')
        queue = load('recalcular_tarea_cf01')
        context = load('recalcular_contexto_cf01')
        old = load('recalcular_compuesto_cf01')
        service = load('recalcular_servicio_v3_cf01')
        post = load('recalcular_post_cal8_cf01')
        assert primaries['files_checked'] == 76 and primaries['observation_records_checked'] == 67360
        assert queue['totals_by_arm']['MAIN']['jobs_completed'] == 24 and queue['totals_by_arm']['MAIN']['attempts'] == 33
        assert queue['totals_by_arm']['SIN_RETORNO']['jobs_completed'] == 3
        assert queue['totals_by_arm']['ACCION_ANULADA']['jobs_completed'] == 0
        for arm, expected in [('MAIN',18),('B_SHAM',18),('B_CUT',16),('SERVICIO_ANULADO',0)]:
            assert service['totals_by_arm'][arm]['summary']['external_passed'] == expected
            assert service['totals_by_arm'][arm]['summary']['attempts'] == 18
        assert service['totals_by_arm']['MAIN']['summary']['reader_reasons'] == {'fixed_hold_one_tick':9,'current':9}
        assert post['summary']['CAL8_intact_passed'] == 4 and post['summary']['CAL8_omitted_passed'] == 2
        assert post['summary']['CAL8_opportunities_each'] == 5
        assert post['summary']['CAL8_final_intact_own'] == [175,171]
        assert post['summary']['all_context_7_5_and_B_61_19_retained_in_samples']
        assert inventory(STAGE) == initial, 'Closed staging changed during sealing'
        assert inventory(extraction) == initial, 'Extracted immutable files changed during recalculation'
        candidate_hash = sha(candidate)
        current_destination_identity = sha(DESTINATION) if DESTINATION.exists() else None
        if current_destination_identity != original_destination_identity:
            raise RuntimeError('Concurrent destination update: candidate retained, publication refused')
        os.replace(candidate, DESTINATION)
        assert sha(DESTINATION) == candidate_hash
        with zipfile.ZipFile(DESTINATION) as archive:
            assert archive.testzip() is None and len(archive.infolist()) == len(initial)
        report.update(status='VERIFIED_EXACT_PUBLISHED_ANALYSIS_ZIP', final_zip=str(DESTINATION),
                      zip_sha256=candidate_hash, zip_bytes=DESTINATION.stat().st_size,
                      maximum_zip_bytes=MAXIMUM_BYTES, expanded_bytes=sum(row['bytes'] for row in initial.values()),
                      members=len(initial), manifest_members_verified=covered, manifest_self_hash_excluded=True,
                      manifest_sha256=initial[MANIFEST]['sha256'], CRC='PASS', all_member_hashes='PASS',
                      exact_closed_staging_preserved=True, extracted_files_preserved=True,
                      final_zip_bytes_are_the_exact_extracted_and_tested_candidate=True,
                      word_sha256=WORD_SHA, word_visual_validation='NOT_INFERRED_FROM_CONTAINER_HASH',
                      source_materialization=materialized,
                      recalculated_primaries=76, packed_observation_occurrences_checked=67360,
                      queue_totals=queue['totals_by_arm'],
                      social_context_cases=[row['case'] for row in context['cases']],
                      old_compound_original_scores=[{'case':row['case'],'summary':row['summary']} for row in old['cases']],
                      service_metrics={arm:value['summary'] for arm,value in service['totals_by_arm'].items()},
                      POST_and_CAL8=post['summary'],
                      limitations=['Archived-field/receipt recalculation only, no native replay or full snapshot continuation.',
                                   'Extraction tested on the same Windows computer, not a second computer.',
                                   'Compact analysis is not the independent installable distribution.'],
                      finished_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.monotonic()-started)
        put(PROOF, report)
        print(json.dumps({key:report[key] for key in ('status','final_zip','zip_sha256','zip_bytes','expanded_bytes','members','extraction','recalculation_output','elapsed_seconds')}, ensure_ascii=False))
        print(json.dumps({'external_proof':str(PROOF),'proof_sha256':sha(PROOF)}, ensure_ascii=False))
        return 0
    except BaseException as error:
        report.update(status='FAILED_NOT_VERIFIED', error=repr(error), candidate=str(candidate),
                      candidate_sha256=sha(candidate) if candidate.exists() else None,
                      elapsed_seconds=time.monotonic()-started)
        put(PROOF.with_name(PROOF.stem + '.failed.' + stamp + '.json'), report)
        raise


if __name__ == '__main__':
    raise SystemExit(main())
