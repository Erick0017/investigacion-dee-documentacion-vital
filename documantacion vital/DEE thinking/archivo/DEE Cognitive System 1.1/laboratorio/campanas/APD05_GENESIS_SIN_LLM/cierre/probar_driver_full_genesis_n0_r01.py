"""Synthetic parser/archive/frame checks; never runs a Full or GUI owner."""
import argparse
import ast
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if a.out.exists() or not a.out.resolve().is_relative_to(HERE):
        raise ValueError('Fresh LAB output required')
    a.out.mkdir(parents=True)
    path = HERE / 'verificar_full_genesis_apd05_r01.py'
    ast.parse(path.read_text(encoding='utf8'))
    spec = importlib.util.spec_from_file_location('apd05_full_driver_helpers_only', path)
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    checks = [{'id': 'AST_ONLY_NO_EXECUTION', 'ok': True}]
    good = io.BytesIO()
    with zipfile.ZipFile(good, 'w') as archive:
        archive.writestr('cognitive sistem/example.txt', 'SYNTHETIC_NOT_DEE')
    with zipfile.ZipFile(good) as archive:
        assert driver.archive_members(archive) == ['cognitive sistem/example.txt']
    checks.append({'id': 'CANONICAL_SYNTHETIC_ARCHIVE', 'ok': True})
    for bad in ('../outside', 'other_root/file.txt', 'cognitive sistem/../outside',
                'cognitive sistem/C:/outside', 'cognitive sistem/a\\b'):
        value = io.BytesIO()
        with zipfile.ZipFile(value, 'w') as archive:
            archive.writestr(bad, 'SYNTHETIC_BAD_PATH')
        try:
            with zipfile.ZipFile(value) as archive:
                driver.archive_members(archive)
        except ValueError:
            checks.append({'id': 'REJECT_ARCHIVE_PATH_' + bad, 'ok': True})
        else:
            raise ValueError('Unsafe archive accepted')
    raw = (1 << 60) | (65535 << 32) | 7
    frame = {'available': True, 'coherent_tick': True, 'life_id': 'SYNTHETIC_NOT_DEE',
             'N': 2, 'tick': '654959', 'counts': {'sites': 8},
             'RAW_sha256': 'a' * 64, 'clocks_sha256': 'b' * 64,
             'cells': [{'raw': str(raw), 'clock': str(2 ** 64 - 1), 'state': 7,
                        's_reg': 65535, 'semantic': 1, 'xyz': [1, 0, 1], 'index': 5}],
             'coordinate_proof': {'official_observe_samples': [{'official_observe_matches': True}]},
             'coverage': {'synthetic_fixture': True}}
    driver.validate_frame(frame, 'SYNTHETIC_NOT_DEE', 2)
    checks.append({'id': 'EXACT_UINT64_STRINGS_NO_FLOAT', 'ok': True})
    frame['cells'][0]['clock'] = 2 ** 64 - 1
    try:
        driver.validate_frame(frame, 'SYNTHETIC_NOT_DEE', 2)
    except ValueError:
        checks.append({'id': 'INTEGER_NOT_ACCEPTED_AS_TRANSMITTED_UINT64', 'ok': True})
    else:
        raise ValueError('Non-string uint64 boundary accepted')
    for protocol in ({'schema': 'APD05.exact_full_gui.prospective_protocol.R01', 'status': 'DRAFT'},
                     {'schema': 'APD04.old_protocol', 'status': 'CLOSED_FOR_EXACT_FULL_APD05_GUI_PROOF'}):
        try:
            driver.validate_protocol(protocol)
        except ValueError:
            checks.append({'id': 'UNAPPROVED_OR_OTHER_PROTOCOL_REJECTED', 'ok': True})
        else:
            raise ValueError('Unapproved protocol accepted')
    report = {'schema': 'APD05.Full_driver.synthetic_checks.N0.R01',
              'driver_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'checks': checks, 'issues': [], 'Full_extracted': False, 'HTTP_started': False,
              'native_imports': 0, 'new_native_ticks': 0,
              'scope': 'Synthetic archive/frame/protocol helper checks only; no scientific or real GUI result.'}
    with (a.out / 'PRUEBA_DRIVER_N0.json').open('x', encoding='utf8', newline='\n') as f:
        json.dump(report, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write('\n')
    print(json.dumps({'checks': len(checks), 'issues': 0, 'new_native_ticks': 0,
                      'Full_or_GUI_executed': False}))


if __name__ == '__main__':
    main()
