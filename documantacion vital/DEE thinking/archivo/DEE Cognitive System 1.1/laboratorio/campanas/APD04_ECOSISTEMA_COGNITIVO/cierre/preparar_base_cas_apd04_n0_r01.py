"""Extracción maestra CAS separada: conserva cada byte y cada ruta de la base R02.

No es un ZIP ni el sello final. Deduplicación por SHA exacto, no por semejanza.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zlib


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')


def deflate(data):
    compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
    return len(compressor.compress(data) + compressor.flush())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.out.resolve()
    lab = root / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
    assert out.is_relative_to(lab) and not out.exists() and not args.report.exists()
    prior = lab / 'cierre/PROPUESTA_COMPONENTES_Y_TAMANOS_N0_R02.json'
    prior_bytes = prior.read_bytes()
    selection = json.loads(prior_bytes)
    out.mkdir(parents=True, exist_ok=False)
    unique, sources = {}, []
    for group in selection['groups']:
        for row in group['files']:
            source = root / row['path']
            before = source.stat()
            data = source.read_bytes()
            after = source.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise ValueError('Source changed during read: ' + row['path'])
            digest = sha(data)
            if len(data) != row['bytes'] or digest != row['sha256']:
                raise ValueError('Closed proposal source identity differs: ' + row['path'])
            object_name = 'OBJETOS/' + digest[:2] + '/' + digest[2:] + '.bin'
            if digest not in unique:
                target = out / object_name
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('xb') as stream:
                    stream.write(data)
                unique[digest] = {'object': object_name, 'bytes': len(data), 'sha256': digest}
            sources.append({'source_original': row['path'], 'object': object_name, 'bytes': len(data),
                            'sha256': digest, 'component': group['id']})
    if len({x['source_original'] for x in sources}) != len(sources):
        raise ValueError('Duplicate logical route')
    dump(out / 'RUTAS_Y_HASHES.json', {'schema': 'APD04.exact_content_addressed_evidence.N0.R01',
         'status': 'BASE_EXTRACTION_ONLY_NOT_FINAL_ANALYSIS',
         'selection_locator': prior.relative_to(root).as_posix(), 'selection_sha256': sha(prior_bytes),
         'source_count': len(sources), 'unique_object_count': len(unique), 'sources': sources,
         'new_native_ticks': 0, 'omitted_selected_source_paths': []})
    copy_tools = [('materializar_cas_analisis_apd04_n0_r01.py', 'RESTAURAR_Y_RECALCULAR_CAS.py'),
                  ('recalcular_analisis_apd04_n0_r01.py', 'recalcular_todo_CONGELADO.py')]
    for filename, destination in copy_tools:
        shutil.copyfile(lab / 'cierre' / filename, out / destination)
    base_ev = 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/'
    base_lab = 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/cierre/'
    jobs = []
    for job_id, script, evidence, expected in [
        ('R04_CERRADO', base_lab + 'exportar_cierre_r04_n0_r04.py', base_ev + 'CIERRE_SENSOR_R04_N0_R04', 'RECALCULO_CIERRE_R04_N0.json'),
        ('RESERVA_PREFIJO02', base_lab + 'exportar_reserva_prefijo_completado_n0_r01.py', base_ev + 'RESERVA60_PREFIJO_WORK02_N0_R01', 'RECALCULO_PREFIJO_RESERVA_N0.json'),
        ('PANEL_HEREDADO', base_lab + 'extraer_panel_heredado_apd04_n0_r01.py', base_ev + 'PANEL_HEREDADO_RAW_N0_R01', 'RECALCULO_PANEL_HEREDADO.json')]:
        expected_path = evidence + '/' + expected
        lookup = {x['source_original']: x for x in sources}
        jobs.append({'id': job_id, 'base': '.', 'script': script,
                     'script_sha256': lookup[script]['sha256'],
                     'args': ['recalc', '--evidence', {'input': evidence}, '--out', '{output}'],
                     'expected': expected_path, 'expected_sha256': lookup[expected_path]['sha256'],
                     'comparison': 'bytes', 'timeout_seconds': 900})
    dump(out / 'PLAN_GLOBAL_CAS.json', {'schema': 'APD04.CAS.selected_archived_recalculations.N0.R01',
         'jobs': jobs, 'scope': 'Archived exact evidence only, no Native, no Full proof, no final reserve closure'})
    text = ('# Base CAS de evidencia APD04, no sistema operativo\n\n'
            'Cada ruta fuente seleccionada está en RUTAS_Y_HASHES.json y remite a un objeto SHA-256 exacto. '
            'Los duplicados usan un solo objeto; no se cambió ni omitió ningún byte seleccionado. '
            'Esta es una extracción N0 de la base medida, no el informe final, no un ZIP, ni un respaldo de vidas.\n\n'
            'Para restaurar en una ruta nueva: python -I -B RESTAURAR_Y_RECALCULAR_CAS.py '
            '--out RUTA_NUEVA --proof PRUEBA_NUEVA.json --recalculate\n\n'
            'El comando escribe sólo evidencia extraída y recálculos. No lee los históricos, no importa el motor '
            'ni continúa una vida. Tres CLIs stdlib verifican R04 adverso, reserva parcial de dos oportunidades '
            'y panel ancestral. Sus resultados deben ser byte-idénticos a los archivados. '
            'Los demás primarios, negativos y código de la selección también se restauran íntegros; '
            'no afirmar que esos tres CLIs cubren todos los contratos científicos.\n')
    with (out / 'LEER_CAS.md').open('x', encoding='utf8', newline='\n') as stream:
        stream.write(text)
    members = []
    for path in sorted(out.rglob('*')):
        if path.is_file():
            data = path.read_bytes()
            members.append({'file': path.relative_to(out).as_posix(), 'bytes': len(data), 'sha256': sha(data)})
    dump(out / 'MANIFIESTO_CAS.json', {'schema': 'APD04.CAS.members.N0.R01', 'members': members,
         'source_count': len(sources), 'unique_objects': len(unique), 'no_source_bytes_omitted': True})
    estimates = []
    for path in sorted(out.rglob('*')):
        if path.is_file():
            rel = path.relative_to(out).as_posix()
            data = path.read_bytes()
            # Destination may add EVIDENCIA_CAS/ in a final analysis, accounted for below.
            overhead = 98 + 2 * (len(rel.encode('utf8')) + 20)
            estimates.append({'file': rel, 'bytes': len(data), 'sha256': sha(data),
                              'deflate_payload': deflate(data), 'estimated_headers': overhead})
    estimated = 22 + sum(x['deflate_payload'] + x['estimated_headers'] for x in estimates)
    report = {'schema': 'APD04.exact_CAS_base_size.N0.R01', 'status': 'NO_ZIP_CREATED_BASE_ONLY',
              'selection_sha256': sha(prior_bytes), 'source_paths': len(sources), 'objects': len(unique),
              'byte_identical_duplicate_paths': len(sources) - len(unique),
              'source_bytes': sum(x['bytes'] for x in sources),
              'unique_source_bytes': sum(x['bytes'] for x in unique.values()),
              'estimated_zip_bytes': estimated, 'base_target_bytes': 9000000,
              'under_base_target': estimated <= 9000000,
              'prior_estimated_zip_bytes': selection['estimated_current_zip_bytes_without_dedup'],
              'estimated_saving': selection['estimated_current_zip_bytes_without_dedup'] - estimated,
              'source_components_modified': False, 'source_paths_or_bytes_omitted': [],
              'new_native_ticks': 0, 'created_zip_count': 0, 'members': estimates}
    dump(args.report, report)
    print(json.dumps({key: value for key, value in report.items() if key != 'members'}))


if __name__ == '__main__':
    main()
