"""Byte-exact decisive A/B/C primaries and portable RAW recalculation; zero ticks."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import sqlite3
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
LAB = ROOT / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
EVIDENCE = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
OUT = EVIDENCE / 'ATENCION_CONSECUENCIAS_AUX_R02_BC/EVIDENCIA_PORTABLE_R02'
LIVES = [('A', 'APD04_ATENCION_REAL_AUX'), ('B', 'APD04_ATENCION_OMIT_AUX'),
         ('C', 'APD04_ATENCION_SENSOR02_AUX')]


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def write(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def main():
    if OUT.exists():
        raise FileExistsError('Portable extraction already exists; no overwrite')
    if not (EVIDENCE / 'ATENCION_CONSECUENCIAS_AUX_R02_BC/CIERRE_BC_DRIVER.json').is_file():
        raise ValueError('The B/C driver must close before collecting final states')
    c_run = EVIDENCE / 'ATENCION_SENSOR02_C_R03'
    if not any((c_run / name).is_file() for name in ('CIERRE_CONTRASTES.json', 'DRIVER_FAILURE_PRESERVED.json', 'CIERRE_REASIGNACION_ROOT.json')):
        raise ValueError('The declared extended-wait C owner has not reached a closure')
    OUT.mkdir()
    members = []

    def copy(source, relative):
        encoded = source.read_bytes()
        destination = OUT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        digest = hashlib.sha256(encoded).hexdigest()
        if hashlib.sha256(destination.read_bytes()).hexdigest() != digest:
            raise ValueError('Exported bytes differ')
        members.append({'source': source.relative_to(ROOT).as_posix(), 'exported': relative,
            'sha256': digest, 'bytes': len(encoded)})

    index = {'schema': 'APD04.attention_portable_primary.v1', 'branches': {},
        'scope': 'Not a complete world backup. A has an interrupted uncommitted future and no final common probe. '
                 'All branches inherit exactly one complete T639374 parent, not independent learners. '
                 'Targets and environmental caches remain auditor/environmental data, never Native memory.'}
    for label, life in LIVES:
        vida = ROOT / 'sistema/estado/vidas' / life / 'VIDA.json'
        if not vida.is_file():
            continue
        record = read(vida)
        copy(vida, label + '/VIDA_ORIGINAL.json')
        for extra in ('FUTURO_INTERRUMPIDO.json',):
            if (vida.parent / extra).is_file():
                copy(vida.parent / extra, label + '/' + extra)
        protocol = ROOT / 'sistema/estado/entrada_sencilla/vidas' / life / 'PROTOCOLO.json'
        if protocol.is_file():
            copy(protocol, label + '/PROTOCOLO_ORIGINAL.json')
        declaration = {'life': life, 'record': label + '/VIDA_ORIGINAL.json', 'primaries': {},
            'interrupted_future_marker_present': (vida.parent / 'FUTURO_INTERRUMPIDO.json').is_file()}
        database = ROOT / 'sistema/estado/servicios_persistentes' / life / 'cola.sqlite3'
        with sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True) as connection:
            connection.row_factory = sqlite3.Row
            transports = [dict(row) for row in connection.execute(
                'select id,payload,payload_sha,status,started_utc,finished_utc,error from requests where id like ? order by seq',
                ('apd04_attention_' + label + '_%',))]
        declaration['transport_rows_from_read_only_SQLite'] = transports
        declaration['transport_database_original'] = {'source': database.relative_to(ROOT).as_posix(),
            'bytes': database.stat().st_size, 'sha256': hashlib.sha256(database.read_bytes()).hexdigest(),
            'scope': 'Closed/interrupted local journal; only selected exact rows exported, no whole database backup.'}
        for row in record['operations']:
            if row['kind'] != 'PERSISTENT_SESION':
                continue
            source = ROOT / 'sistema/estado/servicios_persistentes' / life / row['result_file']
            relative = label + '/PRIMARIOS/' + source.name
            if hashlib.sha256(source.read_bytes()).hexdigest() != row['result_sha256']:
                raise ValueError('A committed primary differs before export')
            copy(source, relative)
            declaration['primaries'][row['result_file']] = relative
        index['branches'][label] = declaration
    incident = EVIDENCE / 'ATENCION_CONSECUENCIAS_AUX_R01/INCIDENCIA_INSTRUMENTAL_PRESERVADA_N0'
    for source in incident.iterdir():
        if source.is_file():
            copy(source, 'INCIDENCIA_A/' + source.name)
    for branch in ('B', 'C'):
        folder = (EVIDENCE / 'ATENCION_CONSECUENCIAS_AUX_R02_BC/RUN_B' if branch == 'B' else c_run)
        for name in ('OWNER_HANDLE_START.json', 'OWNER_HANDLE_EXIT.json', 'DRIVER_FAILURE_PRESERVED.json',
                     'RECURSOS_DRIVER.json', 'CIERRE_CONTRASTES.json', 'HOST_HANDLE_MUESTRAS_PASIVAS.jsonl',
                     'REVISION_SUPERVISION_ANTES_MATERIAL.json', 'FIN_POR_PRESUPUESTO_PROPIO.json',
                     'OWNED_EXIT_AFTER_BUDGET.json', 'HOST_PYSPY_MUESTRA.json',
                     'HOST_PYSPY_STDOUT.txt', 'HOST_PYSPY_STDERR.txt',
                     'CIERRE_REASIGNACION_ROOT.json', 'CIERRE_REASIGNACION_INTENCION.json',
                     'CIERRE_STOP_STDOUT.json', 'CIERRE_STOP_STDERR.txt', 'DRIVER_C_EJECUTADO.py'):
            if (folder / name).is_file():
                copy(folder / name, branch + '/INSTRUMENTO/' + name)
    for name in ('recalcular_atencion_apd04_r01_n0.py', 'recalcular_sensores_apd04_r01_n0.py',
                 'ejecutar_atencion_consecuencias_apd04_r01.py', 'ejecutar_atencion_bc_apd04_r02.py',
                 'ejecutar_atencion_c_apd04_r03.py', 'vigilar_owner_c_apd04_pasivo.py',
                 'contrastar_cortes_t658k_apd04_n0.py',
                 'diferencias_cortes_ab_apd04_n0.py', 'capturar_pila_host_c_apd04_pasiva.py',
                 'cerrar_c_por_reasignacion_root_r01.py',
                 'extraer_campos_expansion_c_n0.py',
                 'sensor_dos_pares_balanceados_apd04_r04.py', 'SENSOR_R04_DISENO_Y_LIMITES.md'):
        copy(LAB / 'native_candidates' / name, name)
    for revision in ('R05_ATENCION_AUX_EJECUTADO', 'R06_ATENCION_BC_B_EJECUTADO', 'R07_ATENCION_C_ESPERA_EJECUTADO'):
        freeze = LAB / 'revisiones' / revision
        if not freeze.is_dir():
            continue
        for relative in ('sistema/capacidades/ecosistema_apd04.py',
                         'sistema/capacidades/sensor_balanceado_apd04.py',
                         'sistema/capacidades/sensor_componentes_apd04.py',
                         'sistema/capacidades/ruta_adaptativa_apd02_04.py'):
            copy(freeze / relative, 'FUENTES_EJECUTADAS/' + revision + '/' + relative)
    copy(EVIDENCE / 'PREFLIGHT_SENSOR_R04_N0.json', 'PREFLIGHT_SENSOR_R04_N0.json')
    copy(EVIDENCE / 'CONTRASTE_CORTES_T658K_N0.json', 'CONTRASTE_CORTES_T658K_N0.json')
    copy(EVIDENCE / 'DIFERENCIAS_CORTES_AB_T658068_N0.json', 'DIFERENCIAS_CORTES_AB_T658068_N0.json')
    for source in (EVIDENCE / 'C_EXPANSION_CAMPOS_EXACTOS_N0').iterdir():
        if source.is_file():
            copy(source, 'C_CAMPOS_EXACTOS/' + source.name)
    copy(EVIDENCE / 'ATENCION_CONSECUENCIAS_AUX_R02_BC/ACLARACION_AGREGADOR_RECHAZOS_PORTABLE_R01.json',
         'ACLARACION_AGREGADOR_RECHAZOS_PORTABLE_R01.json')
    write(OUT / 'INDICE.json', index)
    result = subprocess.run([sys.executable, '-I', '-B', '-X', 'utf8',
        str(OUT / 'recalcular_atencion_apd04_r01_n0.py'), '--index', str(OUT / 'INDICE.json'),
        '--out', str(OUT / 'RECALCULO_PORTABLE.json')], capture_output=True, text=True, encoding='utf8')
    if result.returncode:
        raise RuntimeError(result.stderr)
    recalculated = read(OUT / 'RECALCULO_PORTABLE.json')
    if recalculated['discrepancies']:
        raise ValueError('RAW recalculation reports mismatches')
    fields = subprocess.run([sys.executable, '-I', '-B', '-X', 'utf8',
        str(OUT / 'extraer_campos_expansion_c_n0.py'), '--index', str(OUT / 'C_CAMPOS_EXACTOS/INDICE_CAMPOS.json'),
        '--out', str(OUT / 'RECALCULO_CAMPOS_PORTABLE.json')], capture_output=True, text=True, encoding='utf8')
    if fields.returncode:
        raise RuntimeError(fields.stderr)
    write(OUT / 'MANIFIESTO_MIEMBROS_ORIGINALES.json', {'members': members, 'Native_ticks': 0,
        'original_primary_and_source_bytes_preserved': True,
        'scope': 'Hash list excludes itself, generated recalculation and generated portable index.'})
    print(json.dumps({'destination': str(OUT), 'members': len(list(OUT.rglob('*'))),
        'bytes': sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file()),
        'RAW_recalculation_discrepancies': recalculated['discrepancies'], 'native_ticks': 0}, indent=2))


if __name__ == '__main__':
    main()
