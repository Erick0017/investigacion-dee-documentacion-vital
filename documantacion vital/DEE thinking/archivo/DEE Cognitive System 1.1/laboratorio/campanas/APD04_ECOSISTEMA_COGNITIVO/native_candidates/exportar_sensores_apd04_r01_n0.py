"""Compact byte-exact sensory evidence plus a system-independent recalculation."""
from pathlib import Path
import copy
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
LAB = ROOT / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
BASE = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/SENSORES_Y_LEXICO_R01'
OUT = BASE / 'EVIDENCIA_PORTABLE'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def main():
    if OUT.exists():
        raise FileExistsError('Preserve the original essential export')
    OUT.mkdir()
    manifest = []
    def exact(source, name):
        target = OUT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        digest = sha(source)
        shutil.copyfile(source, target)
        if sha(source) != digest or sha(target) != digest:
            raise ValueError('Source changed or essential copy differs')
        manifest.append({'file': name, 'bytes': target.stat().st_size, 'sha256': digest,
                         'original': source.relative_to(ROOT).as_posix()})
    index = {'schema': 'APD04.portable_sensory_evidence.v1', 'families': {},
        'scope': 'Two shared-prefix sensory AUX, no task-feedback learning claim. '
                 'Operational Native snapshots, SQLite and full service archives are omitted; '
                 'this essential evidence is not a continuation backup.',
        'recalculation_command': 'python RECALCULAR.py --index INDICE.json --out RECALCULO_PORTABLE.json'}
    for family in ('R02', 'R03'):
        life = 'APD04_SENSOR_' + family + '_AUX'
        path = ROOT / 'sistema/estado/vidas' / life / 'VIDA.json'
        record = json.loads(path.read_text(encoding='utf8'))
        if record['physical']['tick'] != 617412:
            raise ValueError('Another continuation exists; export the original cut explicitly, never overwrite it')
        exact(path, family + '_VIDA_ORIGINAL.json')
        selected = {'life_id': life, 'parent': record['parent'],
            'physical': record['physical'], 'snapshot_sha256': record['snapshot_sha256'],
            'operations': []}
        operations = [r for r in record['operations'] if r['kind'] == 'PERSISTENT_SESION']
        if len(operations) != 2:
            raise ValueError('Both declared batches are required')
        for block, operation in enumerate(operations):
            source = ROOT / 'sistema/estado/servicios_persistentes' / life / operation['result_file']
            if sha(source) != operation['result_sha256']:
                raise ValueError('Original service pointer and exact primary disagree')
            filename = family + '_BLOQUE_' + str(block) + '.json'
            exact(source, filename)
            selected['operations'].append({**operation, 'result_file': filename,
                'original_system_result_file': operation['result_file']})
        index['families'][family] = {'record': selected,
            'record_is_declared_locator_view_not_modified_native_snapshot': True,
            'full_snapshot_omitted_local': record['snapshot']}
    exact(LAB / 'native_candidates/recalcular_sensores_apd04_r01_n0.py', 'RECALCULAR.py')
    frozen = LAB / 'revisiones/R04_SENSOR_Y_LEX_EJECUTADO/sistema/capacidades'
    for filename in ('sensor_componentes_apd04.py', 'sensor_balanceado_apd04.py',
                     'sensor_balanceado_apd03_r02.py', 'ruta_adaptativa_apd02_04.py',
                     'selector_acrecion_nativo.py'):
        exact(frozen / filename, 'CODIGO_EJECUTADO/' + filename)
    write(OUT / 'INDICE.json', index)
    write(OUT / 'MANIFIESTO_COPIAS_EXACTAS.json', {'members': manifest,
        'engine_or_WHL_included': False, 'new_native_ticks': 0})
    command = [sys.executable, '-I', '-B', str(OUT / 'RECALCULAR.py'),
        '--index', str(OUT / 'INDICE.json'), '--out', str(OUT / 'RECALCULO_PORTABLE.json')]
    process = subprocess.run(command, cwd=Path(sys.executable).parent,
        capture_output=True, text=True, encoding='utf8', timeout=30)
    if process.returncode:
        raise RuntimeError('Portable recalculation failed: ' + process.stderr)
    portable = json.loads((OUT / 'RECALCULO_PORTABLE.json').read_text(encoding='utf8'))
    reference = json.loads((BASE / 'RECALCULO_SENSORES.json').read_text(encoding='utf8'))
    def without_locator(value):
        result = copy.deepcopy(value)
        for family in result['families']:
            for source in family['sources']:
                source.pop('file')
        return result
    if without_locator(portable) != without_locator(reference):
        raise ValueError('Portable reconstruction changed computed values')
    write(OUT / 'VERIFICACION_PORTABLE.json', {'command': command, 'exit_code': process.returncode,
        'same_reconstructed_values_except_declared_source_locators': True,
        'native_engine_imported': False, 'new_native_ticks': 0,
        'source_records_not_used_as_response_tables_by_participant': True,
        'primary_bytes_verified': sum(row['bytes'] for row in manifest),
        'primary_copies': len(manifest)})
    print(json.dumps({'directory': str(OUT), 'files': len(list(OUT.rglob('*'))),
        'bytes': sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file()),
        'values_reconstructed_from_exported_RAW': True, 'new_native_ticks': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
