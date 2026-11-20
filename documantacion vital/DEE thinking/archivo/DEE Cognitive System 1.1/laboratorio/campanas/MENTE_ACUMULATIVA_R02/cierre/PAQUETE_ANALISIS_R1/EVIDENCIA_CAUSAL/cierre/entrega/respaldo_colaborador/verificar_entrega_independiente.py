"""Prueba práctica del ZIP exacto en otra ruta de la misma computadora.

No es una campaña científica. Sólo se ejecuta cuando el responsable proporciona
el alias de un corte cerrado y una secuencia nueva dentro del contrato vigente.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone


def sha(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''): result.update(block)
    return result.hexdigest()


def read(path): return json.loads(Path(path).read_text(encoding='utf8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', type=Path, required=True)
    parser.add_argument('--destino', type=Path, required=True, help='Carpeta nueva, corta y ASCII.')
    parser.add_argument('--salida', type=Path, required=True, help='Recibo fuera de la extracción y del ZIP.')
    parser.add_argument('--alias', required=True, help='Alias real del catálogo cerrado.')
    parser.add_argument('--vida', required=True, help='Identidad nueva para esta prueba de entrega.')
    parser.add_argument('--campana', default='CF01', help='Identificador del corte comprobado; no cambia el protocolo nativo ni la secuencia.')
    parser.add_argument('--rehidratar-c2', action='store_true', help='EO02: conservar aparte los outputs externos propios después de guardar un C2 pendiente y verificar restauración desde sus bytes completos.')
    parser.add_argument('--comprobar-default-mente', action='store_true', help='MA: abrir sin identidad una importación explícita del corte principal y bifurcar desde ella, sin ticks de preparación.')
    parser.add_argument('--secuencia', type=Path, required=True, help='JSON: operations y continuation con argv explícitos del gestor.')
    parser.add_argument('--original', type=Path, action='append', default=[], help='Archivo original que debe conservar su hash; se puede repetir.')
    args = parser.parse_args()
    archive = args.zip.resolve(strict=True)
    destination = args.destino.resolve()
    if destination.exists(): raise ValueError('No se sobreescribe una extracción anterior; use otra carpeta nueva.')
    if not str(destination).isascii(): raise ValueError('Use una ruta ASCII para los temporales del motor.')
    sequence = read(args.secuencia)
    if not isinstance(sequence.get('operations'), list) or not sequence['operations'] or not isinstance(sequence.get('continuation'), list):
        raise ValueError('La secuencia debe declarar operaciones nuevas y un comando de continuación en otro proceso.')
    originals = {str(path.resolve(strict=True)): sha(path) for path in args.original}
    proof = {'schema': 'DEE.independent_delivery.v2', 'campaign': args.campana, 'started_utc': datetime.now(timezone.utc).isoformat(),
             'zip': str(archive), 'zip_sha256': sha(archive), 'zip_bytes': archive.stat().st_size,
             'destination': str(destination), 'scope': 'Other path on the same Windows computer, not another computer.',
             'originals_before': originals, 'commands': [], 'new_scientific_campaign': False}
    output = args.salida.resolve()
    if output.is_relative_to(destination): raise ValueError('El recibo debe quedar fuera de la extracción examinada.')
    try:
        with zipfile.ZipFile(archive) as source:
            if source.testzip() is not None: raise ValueError('CRC del ZIP no válido.')
            names = source.namelist()
            if len(names) != len(set(names)): raise ValueError('Miembros duplicados.')
            prefix = 'cognitive sistem/'
            for name in names:
                path = PurePosixPath(name)
                if not name.startswith(prefix) or path.is_absolute() or '..' in path.parts or ':' in name or '\\' in name:
                    raise ValueError('Ruta no segura en el ZIP: ' + name)
                relative = name[len(prefix):]
                if relative.startswith('entregas/'): raise ValueError('El ZIP contiene entregas/ anidada.')
                if relative.startswith('trabajo_personal/') and relative != 'trabajo_personal/LEER_PRIMERO.md':
                    raise ValueError('El ZIP contiene experimentos personales del creador.')
            manifest = json.loads(source.read(prefix + 'actualizaciones/ARCHIVOS_GESTIONADOS.json'))
            declared = {prefix + name for name in manifest['members']} | {prefix + 'actualizaciones/ARCHIVOS_GESTIONADOS.json', prefix + 'actualizaciones/CAMBIOS.jsonl'}
            if set(names) != declared:
                raise ValueError('El ZIP tiene miembros no declarados o faltantes frente al manifiesto.')
            checked = 0
            for name, row in manifest['members'].items():
                data = source.read(prefix + name)
                if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
                    raise ValueError('Miembro no coincide con su manifiesto: ' + name)
                checked += 1
            source.extractall(destination)
        root = destination / 'cognitive sistem'
        manual = read(root / 'documentos/MANUAL_VIGENTE.json')
        if sha(root / manual['file']) != manual['sha256'] or sha(root / 'documentos' / manual['file']) != manual['sha256']:
            raise ValueError('El Word de la raíz y su copia documental no son idénticos al corte publicado.')
        proof['archive'] = {'crc': 'verified', 'manifest_members_checked': checked, 'no_entregas_members': True,
                            'manual_root_and_documentos_identical': True}
        python = root / 'motor/python313/python.exe'
        launcher = root / 'actualizaciones/arrancar.py'
        substitutions = {'$LIFE': args.vida, '$IMPORTED': args.vida + '_IMPORTADA', '$ROOT': str(root)}

        def call(label, argv, require_fence=False):
            if not isinstance(argv, list) or not all(isinstance(x, str) for x in argv): raise ValueError('argv debe ser una lista de cadenas explícitas.')
            rendered = [substitutions.get(x, x) for x in argv]
            command = [str(python), '-I', '-B', '-X', 'utf8', str(launcher), *rendered]
            started = time.perf_counter()
            process = subprocess.run(command, cwd=root, text=True, encoding='utf8', capture_output=True, timeout=240)
            row = {'label': label, 'argv': command, 'exit_code': process.returncode,
                   'host_seconds': time.perf_counter() - started, 'stdout': process.stdout, 'stderr': process.stderr}
            proof['commands'].append(row)
            if process.returncode: raise RuntimeError('Falló el comando de entrega: ' + label)
            # Los recibos del gestor son evidencia del perímetro de lectura
            # aplicado a la operación, no un sandbox del sistema operativo.
            # El lanzador no calcula la respuesta ni recibe targets históricos.
            if require_fence:
                value = json.loads(process.stdout)
                fence = value.get('INSTRUMENTO_FENCE')
                if not isinstance(fence, dict) or fence.get('denied') or fence.get('no_lab_evidence_or_history_reads_allowed') is not True:
                    raise ValueError('Falta el perímetro operativo o hubo un acceso no declarado: ' + label)
                row['operational_fence_verified'] = fence
            return process.stdout

        call('prepare_local_dependencies_no_new_universe', ['preparar'])
        version = json.loads(call('copied_manager_engine_identity', ['gestor', 'version']))
        engine = version['INSTRUMENTO']['engine']
        for field in ('executable', 'imported', 'native'):
            if not Path(engine[field]).resolve().is_relative_to(root): raise ValueError('El motor resolvió fuera de esta distribución: ' + field)
        proof['engine_from_this_extraction'] = engine
        if args.comprobar_default_mente:
            if args.alias != 'MENTE_ACUMULATIVA': raise ValueError('La prueba predeterminada sólo admite el alias principal explícito.')
            call('default_entry_without_life_explicit_complete_continuity_import', ['mente'])
            active = read(root/'trabajo_personal/estado/ACTIVO.json')
            imported_id = active['life_id']
            imported_record = read(root/'trabajo_personal/estado/vidas'/imported_id/'VIDA.json')
            chosen = next(q for q in read(root/'entes/CATALOGO.json')['cuts'] if q['alias'] == args.alias)
            keys = ('N', 'tick', 'RAW_sha256', 'clocks_sha256')
            if ({k:imported_record['physical'][k] for k in keys} != {k:chosen['physical'][k] for k in keys}
                or imported_record['branch'] != 'EXPLICIT_IMPORTED_CONTINUITY'
                or imported_record['parent']['encoded_sha256'] != chosen['snapshot_sha256']):
                raise ValueError('El inicio predeterminado no importó el estado aprendido seleccionado exactamente.')
            proof['default_research_import'] = {'alias': args.alias, 'source_life': chosen['source_life'],
                'source_tick': chosen['tick'], 'source_snapshot_sha256': chosen['snapshot_sha256'],
                'imported_life_id': imported_id, 'created_utc': imported_record['created_utc'],
                'branch': imported_record['branch'], 'before_any_input_physical': imported_record['physical'],
                'physical_identical_to_selected_cut': True, 'new_T0_preparation': False}
            substitutions['$IMPORTED'] = imported_id
        else:
            call('open_complete_learned_state_as_explicit_copy', ['abrir', args.alias, substitutions['$IMPORTED']])
        call('fork_working_life', ['gestor', 'bifurcar', substitutions['$IMPORTED'], args.vida])
        call('select_this_working_fork_not_another_profile', ['gestor', 'activar', args.vida])
        if args.comprobar_default_mente:
            call('default_entry_loads_same_personal_active_without_reimport', ['mente'], True)
        call('before_new_user_sequence', ['gestor', 'estado', '--vida', args.vida])
        for index, item in enumerate(sequence['operations']):
            if not isinstance(item, dict): raise ValueError('Cada operación requiere label y argv.')
            call(item.get('label', 'new_operation_' + str(index)), item['argv'], item.get('require_fence', False))
        call('save_complete_state', ['gestor', 'guardar', '--vida', args.vida])
        state_path = root / 'trabajo_personal/estado/vidas' / args.vida / 'VIDA.json'
        before = read(state_path)
        substitutions['$NEXT_TICK'] = str(int(before['physical']['tick']) + 3)
        proof['before_cross_process_continuation'] = {'tick': before['physical']['tick'], 'snapshot_sha256': before['snapshot_sha256'],
                                                     'life_id': before['life_id'], 'world_id': before['world_id']}
        if args.rehidratar_c2:
            observed = json.loads(call('passive_C2_pending_before_external_relocation', ['gestor', 'evolucion-estado', '--vida', args.vida]))
            pending = observed['service']['environments']['transaccion'].get('pending_transaction')
            if not pending or 'prepared_output_base64' not in pending: raise ValueError('No hay C2 preparado completo: no se simula una restauración desde otro estado favorable.')
            source_folder = (root / 'trabajo_personal/estado/servicios_locales' / args.vida).resolve(strict=True)
            backup_folder = root / 'trabajo_personal/resultados' / (args.vida + '_external_before_restore')
            personal_root = (root / 'trabajo_personal').resolve(strict=True)
            if not source_folder.is_relative_to(personal_root) or not backup_folder.resolve().is_relative_to(personal_root) or backup_folder.exists():
                raise ValueError('La copia externa debe quedar en una carpeta personal nueva y recuperable.')
            previous_files = {path.relative_to(source_folder).as_posix(): sha(path) for path in source_folder.rglob('*') if path.is_file()}
            backup_folder.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_folder), str(backup_folder))
            proof['C2_external_artifacts_relocated'] = {'source': str(source_folder), 'recoverable_backup': str(backup_folder), 'files_sha256': previous_files,
                'pending': pending, 'native_state_not_modified': True, 'purpose': 'Only the experimental external outputs are moved after complete save; the next process must restore exact snapshot-carried bytes, not recompute a target.'}
        call('continue_in_another_process', sequence['continuation'], sequence.get('continuation_requires_fence', False))
        call('load_and_observe_continued_life_in_another_process', ['gestor', 'estado', '--vida', args.vida])
        after = read(state_path)
        if after['life_id'] != before['life_id'] or after['world_id'] != before['world_id'] or after['physical']['tick'] <= before['physical']['tick']:
            raise ValueError('La continuación no preservó identidad y avance; no se certifica un reemplazo desde T0.')
        snapshot = (root / 'sistema' / after['snapshot']).resolve(strict=True)
        if not snapshot.is_relative_to(root / 'trabajo_personal') or sha(snapshot) != after['snapshot_sha256']:
            raise ValueError('El estado continuado no quedó íntegro en trabajo_personal/.')
        proof['continued_state'] = {'life_id': after['life_id'], 'world_id': after['world_id'], 'tick': after['physical']['tick'],
                                    'snapshot': str(snapshot), 'snapshot_sha256': after['snapshot_sha256'], 'parent': after.get('parent')}
        proof['status'] = 'COMPLETED_WITH_RECORDED_SCOPE'
    except Exception as error:
        proof['status'] = 'FAILED_WITH_STATE_PRESERVED'
        proof['error'] = {'type': type(error).__name__, 'detail': str(error)}
    finally:
        proof['originals_after'] = {path: sha(path) for path in originals}
        proof['originals_unchanged'] = proof['originals_after'] == originals
        proof['zip_unchanged'] = sha(archive) == proof['zip_sha256']
        if not proof['originals_unchanged'] or not proof['zip_unchanged']: proof['status'] = 'FAILED_ORIGINAL_OR_ARCHIVE_CHANGED'
        proof['finished_utc'] = datetime.now(timezone.utc).isoformat()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(proof, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf8')
    print(json.dumps({'status': proof['status'], 'proof': str(output), 'zip_sha256': proof['zip_sha256']}, ensure_ascii=False))
    return 0 if proof['status'] == 'COMPLETED_WITH_RECORDED_SCOPE' else 2


if __name__ == '__main__': raise SystemExit(main())
