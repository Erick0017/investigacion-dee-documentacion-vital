"""Selecciona exclusivamente bytes existentes de APD05; no sella ni ejecuta física.

Produce un borrador para el ensamblador cerrado ya preparado. Root debe revisar
las afirmaciones y aprobarlo explícitamente antes de ensamblar/sellar. No importa
el motor, no abre SQLite, no actualiza Full ni modifica el Word.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--add', action='append', default=[], help='Archivo adicional relativo a Root; no directorios')
    ap.add_argument('--main-code', help='Recálculo MAIN cerrado, relativo a Root')
    ap.add_argument('--main-golden', help='Golden MAIN cerrado, relativo a Root')
    ap.add_argument('--root-approved', choices=['APD05_PARTIAL_RESULTS_APPROVED_FOR_ANALYSIS'])
    ap.add_argument('--extended-close', action='store_true', help='Cierre autorizado: incorpora el Word real; no inventa prueba Full')
    ap.add_argument('--full-proof', help='Carpeta Root-relativa de la prueba real Full ya cerrada')
    ap.add_argument('--png', type=Path, default=Path('D:/Descargas/GENESIS_APD05_MAIN_T683407_PASIVO.png'))
    args = ap.parse_args()
    root = args.root.resolve()
    lab = root / 'laboratorio/campanas/APD05_GENESIS_SIN_LLM'
    closing = lab / 'cierre'
    ev = root / 'evidencia/campanas/APD05_GENESIS_SIN_LLM'
    gui = root / 'aplicacion/GENESIS'
    files, components, omissions, jobs = [], [], [], []
    chosen, ids = {}, {}

    def add(path, destination, kind='closed_existing_primary', compress=False):
        path = path.resolve()
        if not path.is_relative_to(root) or not path.is_file() or path.is_symlink():
            raise ValueError('Only real Root files: ' + str(path))
        key = path.relative_to(root).as_posix()
        if key in chosen:
            return chosen[key]
        if path.stat().st_size == 0:
            omissions.append({'locator': key, 'sha256': sha(path), 'bytes': 0,
                              'reason': 'Salida vacía original; no se sustituye por contenido inventado.',
                              'scientific_consequence': 'Ningún dato primario omitido; el STDERR y la supervisión se incluyen cuando existen.'})
            return None
        forbidden = ('.zip', '.whl', '.pyd', '.dll', '.exe', '.db', '.sqlite', '.sqlite3', '.npy', '.npz', '.deetsnap', '.deetsnap.gz', '.pyc')
        if path.name.lower().endswith(forbidden):
            raise ValueError('Motor, base operativa o snapshot no permitido en análisis: ' + key)
        ident = 'F%04d' % (len(files) + 1)
        files.append({'id': ident, 'source': key, 'destination': destination,
                      'kind': kind, 'sha256': sha(path), 'compress_gzip': compress})
        chosen[key], ids[destination] = ident, ident
        return ident

    def tree(folder, destination):
        refs = []
        for path in sorted(folder.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                rel = path.relative_to(folder).as_posix()
                # Los CLIs RAW archivados leen JSONL exacto; el ZIP lo comprime
                # sin añadir un descompresor/adaptador nuevo al recálculo.
                compress = path.suffix == '.jsonl' and path.name != 'EVENTOS.jsonl'
                ident = add(path, destination + '/' + rel + ('.gz' if compress else ''), compress=compress)
                if ident:
                    refs.append(ident)
        if not refs:
            raise ValueError('No selected evidence in ' + str(folder))
        return refs

    def component(folder, destination, ident):
        manifest = folder / 'MANIFIESTO.json'
        value = json.loads(manifest.read_bytes())
        rows = value.get('members', value.get('files'))
        if not rows:
            raise ValueError('Closed manifest without members')
        components.append({'id': ident, 'source': folder.relative_to(root).as_posix(),
                           'destination': destination, 'manifest': 'MANIFIESTO.json',
                           'manifest_sha256': sha(manifest)})
        return ident

    ctl = component(ev / 'controles/REPOSO_Y_ACCESO_PORTABLE_N0_R02', 'EVIDENCIA_CAUSAL/CONTROLES', 'CONTROLES_CERRADOS')
    guiev = component(gui / 'pruebas/EXPORT_GUI_ESENCIAL_N0_R01', 'EVIDENCIA_CAUSAL/GUI_WALK', 'GUI_CERRADA')
    gui_tool = gui / 'pruebas/recalcular_export_gui_portable_n0_r01.py'
    gui_expected = gui / 'pruebas/RESULTADO_PORTABLE_GUI_N0_R01.json'
    add(gui_tool, 'RECALCULO/recalcular_export_gui_portable_n0_r01.py', 'executed_N0_recalculation')
    add(gui_expected, 'RECALCULO/REFERENCIA_GUI_N0.json', 'closed_recalculation_reference')
    jobs.extend([
        {'id': 'GUI_PORTABLE', 'base': '.', 'script': 'RECALCULO/recalcular_export_gui_portable_n0_r01.py',
         'args': ['--root', {'input': 'EVIDENCIA_CAUSAL/GUI_WALK'}, '--out', '{output}'],
         'expected': 'RECALCULO/REFERENCIA_GUI_N0.json', 'comparison': 'bytes', 'timeout_seconds': 60},
        {'id': 'CONTROLES_PORTABLE', 'base': '.',
         'script': 'EVIDENCIA_CAUSAL/CONTROLES/CODIGO/exportar_recalcular_controles_reposo_n0_r02.py',
         'args': ['--root', {'input': 'EVIDENCIA_CAUSAL/CONTROLES'}, '--out', '{output}'],
         'expected': 'EVIDENCIA_CAUSAL/CONTROLES/RECALCULO_N0.json', 'comparison': 'bytes', 'timeout_seconds': 90},
    ])
    r02 = tree(ev / 'RESERVA_INTEGRADA_60_R02', 'EVIDENCIA_CAUSAL/RESERVA_60_R02')
    r01 = tree(ev / 'RESERVA_INTEGRADA_60_R01', 'EVIDENCIA_CAUSAL/NEGATIVOS/RESERVA_60_R01')
    opening = tree(ev / 'ARRANQUE_Y_CADENA_MINIMA_R01', 'EVIDENCIA_CAUSAL/APERTURA')
    vig01 = tree(ev / 'MAIN_VIGENCIA_R01', 'EVIDENCIA_CAUSAL/NEGATIVOS/VIGENCIA_R01')
    vig02 = tree(ev / 'MAIN_VIGENCIA_R02', 'EVIDENCIA_CAUSAL/VIGENCIA_R02')
    frozen = tree(ev / 'GUI_R05_FUENTES_CONGELADAS', 'CODIGO_EJECUTADO/GUI_R05')
    recording = []
    for name in ('RECUPERACION_GRABACION_PARCIAL_N0.json', 'REPLAY_PREFIJO_PARCIAL_060123_A_065619.jsonl.gz'):
        recording.append(add(ev / 'GUI_GRABACION_PARCIAL_R01' / name,
                             'EVIDENCIA_CAUSAL/GRABACION_PARCIAL/' + name))
    broken_recording = ev / 'GUI_GRABACION_PARCIAL_R01/SESION_20261027T060123_ed72df4d.jsonl.gz'
    omissions.append({'locator': broken_recording.relative_to(root).as_posix(),
                      'sha256': sha(broken_recording), 'bytes': broken_recording.stat().st_size,
                      'reason': 'Gzip original truncado preservado localmente; viajan el prefijo derivado exacto y su procedimiento de recuperación.',
                      'scientific_consequence': 'El derivado contiene sólo 171 marcos existentes, no el resto de la sesión ni un vídeo de una hora.'})
    for name in ('genesis.py', 'propietario_genesis.py', 'visor_pasivo.py', 'index.html', 'style.css', 'app.js', 'pruebas_n0.py'):
        add(gui / name, 'CODIGO_ACTUAL_GUI/' + name, 'current_instrument_R06_not_retested_natively')
    add(root / 'ABRIR_GENESIS.bat', 'CODIGO_ACTUAL_GUI/ABRIR_GENESIS.bat', 'current_launcher')
    for name in ('INFORME_CIENTIFICO_CIERRE_PARCIAL.md', 'CIERRE_POR_BLOQUEO_DEL_NAVEGADOR.json',
                 'PRESUPUESTO_Y_PLAN_DE_CORTE.json', 'GUIA_ESCENAS_TECNICAS_GUI_R01.json'):
        destination = 'INFORME_CIENTIFICO.md' if args.extended_close and name == 'INFORME_CIENTIFICO_CIERRE_PARCIAL.md' else name
        add(lab / name, destination, 'root_authored_closed_result_or_limitation')
    add(closing / 'recuperar_prefijo_grabacion_gui_n0_r01.py', 'RECALCULO/recuperar_prefijo_grabacion_gui_n0_r01.py', 'executed_N0_instrument')
    add(Path(__file__), 'CODIGO_DE_CIERRE/' + Path(__file__).name, 'selection_instrument_no_Native')
    if not args.png.is_file():
        raise FileNotFoundError('La captura real falta; no se genera una imagen sustituta.')
    staged = closing / 'FUENTES_EXTERNAS' / args.png.name
    staged.parent.mkdir(exist_ok=True)
    if staged.exists():
        if sha(staged) != sha(args.png):
            raise ValueError('La copia de captura existente difiere; no sobrescribir.')
    else:
        shutil.copyfile(args.png, staged)
    pngid = add(staged, 'EVIDENCIA_CAUSAL/GENESIS_APD05_MAIN_T683407_PASIVO.png', 'actual_single_passive_GUI_capture')
    for rel in args.add:
        path = (root / rel).resolve()
        add(path, 'COMPLEMENTOS_CERRADOS/' + path.name, 'additional_closed_N0_result')
    if bool(args.main_code) != bool(args.main_golden):
        raise ValueError('MAIN code and golden must be supplied together')
    if args.main_code:
        code = (root / args.main_code).resolve()
        golden = (root / args.main_golden).resolve()
        add(code, 'RECALCULO/' + code.name, 'executed_MAIN_N0_recalculation')
        add(golden, 'RECALCULO/REFERENCIA_MAIN_N0.json', 'closed_MAIN_recalculation_reference')
        reader = code.with_name('recalcular_vigencia_apd05_r02.py')
        add(reader, 'RECALCULO/' + reader.name, 'executed_exact_RAW_reader_R02_preserved')
        jobs.append({'id': 'MAIN_PORTABLE', 'base': '.', 'script': 'RECALCULO/' + code.name,
                     'args': [{'input': 'EVIDENCIA_CAUSAL/RESERVA_60_R02/PRIMARIOS/EVENTOS.jsonl'}, '--output', '{output}'],
                     'expected': 'EVIDENCIA_CAUSAL/RESERVA_60_R02/RECALCULO_RAW_R03_RECIBOS_CON_ALIAS.json',
                     'comparison': 'bytes', 'timeout_seconds': 90})
        jobs.append({'id': 'VIGENCIA_754_RAW', 'base': '.', 'script': 'RECALCULO/' + reader.name,
                     'args': [{'input': 'EVIDENCIA_CAUSAL/VIGENCIA_R02/PRIMARIOS/EVENTOS.jsonl'}, '--output', '{output}'],
                     'expected': 'EVIDENCIA_CAUSAL/VIGENCIA_R02/RECALCULO_RAW_R02_GEOMETRIA_ESTRICTA.json',
                     'comparison': 'bytes', 'timeout_seconds': 90})
    closure = json.loads((ev / 'RESERVA_INTEGRADA_60_R02/PRIMARIOS/CIERRE_REAL.json').read_bytes())
    pair = closure['pair']
    physical = closure['physical']
    reportid = chosen[(lab / 'INFORME_CIENTIFICO_CIERRE_PARCIAL.md').relative_to(root).as_posix()]
    delayid = chosen[(lab / 'CIERRE_POR_BLOQUEO_DEL_NAVEGADOR.json').relative_to(root).as_posix()]
    closeid = chosen[(ev / 'RESERVA_INTEGRADA_60_R02/PRIMARIOS/CIERRE_REAL.json').relative_to(root).as_posix()]
    attempts = []
    for ident, role, status, scope, refs in (
        ('APERTURA', 'MAIN', 'CLOSED_RESULT', 'Importación real y siete peticiones de apertura; no nuevos conceptos por denominación.', opening),
        ('VIGENCIA_R01', 'MAIN', 'CLOSED_INSTRUMENT_FAILURE', 'Fallo de instrumento preservado; no se cuenta como éxito.', vig01),
        ('VIGENCIA_R02', 'MAIN', 'CLOSED_RESULT', 'Sensor y acceso preparados P0; contenido usado se verifica en sus primarios.', vig02),
        ('RESERVA_60_R01', 'MAIN', 'CLOSED_INSTRUMENT_FAILURE', 'Pausa heredada; cero ticks y tres peticiones conservadas. No una reserva de una hora.', r01),
        ('RESERVA_60_R02', 'MAIN', 'CLOSED_RESULT', 'Misma vida y tres IDs heredados; ventana física cerrada de 3603.173 s. Transporte no equivale a acierto.', r02),
        ('GUI_WALK', 'FORK', 'CLOSED_RESULT', 'Revisión y retención en vida GUI propia, no conocimientos importados a MAIN.', [guiev]),
        ('CONTROLES_REPOSO', 'CONTROL', 'CLOSED_RESULT', 'Controles comparables y negativos; cada genealogía se mantiene separada.', [ctl]),
        ('CAPTURA_Y_GRABACION', 'N0_INSTRUMENT', 'CLOSED_RESULT', 'Una captura real; replay derivado de prefijo parcial, no vídeo de 60 minutos.', recording + [pngid]),
        ('FULL_APD05', 'FULL_PROOF', 'NOT_EXECUTED', 'No se refrescó ni verificó un Full APD05 exacto.', []),
        ('WORD_1_19', 'EDITORIAL', 'NOT_EXECUTED', 'No se editó ni renderizó el Word 1.19. El manual 1.18 sigue vigente sin modificación.', []),
        ('CUA_BLOQUEADO', 'N0_INSTRUMENT', 'CLOSED_INSTRUMENT_FAILURE', 'Bloqueo externo fuera del presupuesto: no cuenta como evolución Native ni trabajo de laboratorio.', [delayid]),
    ):
        attempts.append({'id': ident, 'role': role, 'status': status, 'scope': scope, 'source_ids': refs})
    value = {
        'schema': 'APD05.final_analysis_selection.R01',
        'status': 'FINAL_RESULTS_APPROVED_FOR_ANALYSIS' if args.root_approved else 'DRAFT_NOT_APPROVED',
        'native_work_closed': True, 'zip_name': 'DEE_APD05_GENESIS_SIN_LLM_ANALISIS.zip',
        'full_status': 'NOT_EXECUTED_APD05_FULL_REFRESH_OR_EXACT_FULL_GUI_PROOF',
        'approval_required': 'Root debe revisar ciencia/recálculos, añadir sus incorporaciones y autorizar por separado el ensamblado y sello.',
        'attempts': attempts,
        'claims': [
            {'id': 'MAIN_CORTE_REAL', 'level': 'HECHO_COMPUTACIONAL', 'life': 'APD05_MAIN',
             'text': 'La reserva cerró un par físico completo con propietario detenido y sin pendientes; el ZIP no contiene ese par.',
             'scope': 'Corte real de R02, no estabilidad ilimitada ni 52 aprendizajes.', 'source_ids': [closeid],
             'limits': ['La corrección y utilidad se evalúan separadamente del transporte.', 'Los controles no se suman como biografía de MAIN.']},
            {'id': 'GUI_REVISION_LOCAL', 'level': 'CAPACIDAD_FUNCIONAL', 'life': 'APD05_GUI_WALK_R01',
             'text': 'Revisión de asociación y uso posterior con dos testigos conservados según primarios y recálculo exportado.',
             'scope': 'Vida GUI_WALK; gramática y anatomía preparadas. No aprendizaje de algoritmo ni lenguaje general.',
             'source_ids': [guiev], 'limits': ['No trasplanta recuerdos a MAIN.', 'Grabación y visor son instrumentos externos.']},
            {'id': 'CIERRE_PARCIAL_EXPLICITO', 'level': 'HECHO_COMPUTACIONAL', 'life': None,
             'text': 'El bloqueo CUA excedió el plazo; Full, Word y promoción final permanecen sin completar en este corte.',
             'scope': 'Limitación operativa explicitada, no fallo cognitivo del ente.', 'source_ids': [delayid, reportid],
             'limits': ['No se autoriza implícitamente nueva física, instalación o edición Word.']},
        ],
        'lives': [
            {'id': 'APD05_MAIN', 'parent': {'source_tick': 654959, 'source_snapshot_sha256': '52a35b4062bc843a74a115679ba7c6f76c9db1eab145926ac9d01d22390723fc'},
             'N': physical['N'], 'tick': physical['tick'], 'snapshot_sha256': pair['snapshot_sha256'],
             'status': 'CLOSED_LOCAL_COMPLETE_PAIR_NOT_IN_ANALYSIS', 'available': ['Trayectoria física y resultados consecutivos de MAIN documentados en el informe y primarios.'],
             'not_currently_proven': ['P2 general', 'Mente general', 'Full APD05 independiente', 'Promoción global'],
             'continuation': {'local_pair_locator': pair['directory'], 'manifest_sha256': pair['manifest_sha256'], 'bytes': pair['bytes']}},
            {'id': 'APD05_GUI_WALK_R01',
             'parent': {'life': 'APD05_MAIN', 'source_tick': 655557,
                        'source_snapshot_sha256': '02375730e29a3763fea52550820b89c3f31ba1ceda7348f12b13fe7f07b82b84',
                        'source_pair_manifest_sha256': '9f12f90ed7c53acc386893123716fb112cc0967aeda8092bcae8a30a5b19471a'},
             'seed_ancestor_tick': 654959, 'N': 67, 'tick': 656071,
             'snapshot_sha256': '4ed8d6a930f94597a3a6ccaea1bbe9d0501508225aabbd60ace181b28323511d',
             'status': 'SEPARATE_GUI_FORK', 'available': ['clasifica negativa después de revisión', 'luma positiva', 'nara negativa'],
             'not_currently_proven': ['Conocimiento transferido a MAIN', 'Generalidad lingüística'],
             'continuation': {'local_locator': 'sistema/estado/servicios_persistentes/APD05_GUI_WALK_R01', 'full_state_in_analysis': False}},
        ],
        'executed_revisions': [
            {'id': 'R02_FUENTES_REALES', 'scope': 'Bytes congelados del propietario, percepción, protocolo, transporte, drivers y GUI durante la reserva real.',
             'source_ids': r02, 'provenance': 'EV/RESERVA_INTEGRADA_60_R02/PRIMARIOS/FUENTES_EJECUTADAS; no se sustituyen por el código actual.'},
            {'id': 'GUI_R05', 'scope': 'GUI realmente utilizada; R06 es sólo una corrección posterior N0 del instrumento.',
             'source_ids': frozen + [guiev], 'provenance': 'Fuentes congeladas y controles GUI originales.'},
        ],
        'files': files, 'components': components, 'jobs': jobs, 'omissions': omissions,
        'main_recalculation_status': 'CLOSED_ADDITIONAL_SCRIPT_SUPPLIED_VERIFY_CLI' if args.main_code else 'PENDING_FINAL_N0_RECONCILIATION_DO_NOT_INVENT_COUNTS',
    }
    value['omissions'].extend([
        {'locator': pair['directory'], 'sha256': pair['manifest_sha256'], 'bytes': pair['bytes'],
         'reason': 'Snapshot y sidecars operativos completos quedan localmente; análisis no es respaldo.',
         'scientific_consequence': 'Se puede recalcular evidencia archivada, no continuar ni reproducir Native sólo con este ZIP.'},
        {'locator': 'motor/ y sistema/estado/', 'reason': 'No se redistribuyen motor, WHL, SQLite ni todos los checkpoints en un paquete de análisis.',
         'scientific_consequence': 'Las pruebas Full/Native no son sustituidas por recálculo sin ticks.'},
        {'locator': str(args.png.resolve()), 'sha256': sha(args.png), 'bytes': args.png.stat().st_size,
         'reason': 'Archivo externo original preservado; se incluye una copia exacta bajo un localizador Root seguro.',
         'scientific_consequence': 'Sólo una proyección pasiva en T683407; no demuestra observación posterior durante el bloqueo.'},
        {'locator': 'Manual Maestro vigente edición 1.18 de la raíz',
         'reason': 'No se efectuó una edición ni validación visual 1.19; el cierre lo declara en lugar de simular cumplimiento.',
         'scientific_consequence': 'Este paquete no puede afirmar actualización editorial del Manual Maestro.'},
    ])
    if args.extended_close:
        manual_name = 'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_19_APD05_GENESIS_SIN_VALIDACION_VISUAL.docx'
        manual_id = add(root / manual_name, 'MANUAL/' + manual_name, 'actual_structurally_updated_DOCX_not_visually_validated')
        editorial_id = add(lab / 'manual/VERIFICACION_MANUAL_1_19_R01.json',
                           'MANUAL/VERIFICACION_MANUAL_1_19_R01.json', 'actual_editorial_checks_and_render_failure')
        add(lab / 'manual/actualizar_manual_apd05_r01.py', 'MANUAL/CODIGO/actualizar_manual_apd05_r01.py', 'executed_editorial_instrument')
        add(lab / 'manual/funciones_ooxml_apd03_preservadas.py', 'MANUAL/CODIGO/funciones_ooxml_apd03_preservadas.py', 'preserved_editorial_helpers')
        for name in ('AUTORIZACION_CIERRE_ACOTADO_R01.json', 'APENDICE_CONTROLES_REPOSO_Y_ACCESO_N0_R01.md',
                     'INCORPORACIONES_APD05_CIERRE.md', 'CAMBIOS_MANUAL_APD05.md'):
            add(closing / name, name, 'root_approved_closure_result')
        add(root / 'CONTINUIDAD_APD05_GENESIS_SIN_LLM.json', 'CONTINUIDAD_APD05_GENESIS_SIN_LLM.json', 'actual_local_continuity')
        add(root / 'sistema/contratos/GENESIS_SELECCION_MAIN_APD05.json',
            'CONTRATOS/GENESIS_SELECCION_MAIN_APD05.json', 'optional_selected_actual_cut_not_ACTIVO')
        add(root / 'LEER_PRIMERO.md', 'MANUAL/LEER_PRIMERO_SISTEMA.md', 'actual_source_operating_guide')
        add(root / 'entregas/SELLO_DISTRIBUCION_APD05_R01.json', 'CONTRATOS/SELLO_DISTRIBUCION_APD05_R01.json',
            'closed_source_for_distribution_not_full_proof')
        full_package_id = add(closing / 'RESULTADO_FULL_DELTA_N0_R01.json',
            'CONTRATOS/RESULTADO_FULL_DELTA_N0_R01.json', 'actual_Full_ZIP_seal_not_Native_proof')
        value['omissions'] = [r for r in value['omissions'] if r['locator'] != 'Manual Maestro vigente edición 1.18 de la raíz']
        value['omissions'].append({'locator': manual_name, 'sha256': sha(root / manual_name),
            'reason': 'El Word actualizado está incluido; no hubo renderización disponible por ausencia de soffice.',
            'scientific_consequence': 'La edición estructural se comprobó; cero páginas de QA visual. No se afirma validación visual.'})
        for row in value['attempts']:
            if row['id'] == 'WORD_1_19':
                row.update(status='CLOSED_RESULT', source_ids=[manual_id, editorial_id],
                           scope='Word 1.19 realmente actualizado, preservación OOXML comprobada; renderización fallida por soffice ausente, cero páginas visuales.')
            if row['id'] == 'FULL_APD05':
                row.update(status='CLOSED_PACKAGE_NATIVE_PROOF_PENDING', source_ids=[full_package_id],
                           scope='Full APD05 realmente regenerado y sellado con CRC y hashes de miembros; su prueba Native/GUI exacta es una operación separada, pendiente hasta su recibo real.')
        value['full_status'] = 'FULL_REFRESH_EXACT_ZIP_SEALED_NATIVE_GUI_PROOF_PENDING'
        value['claims'] = [r for r in value['claims'] if r['id'] != 'CIERRE_PARCIAL_EXPLICITO']
        value['claims'].append({'id': 'CIERRE_EXTENSION_AUTORIZADA', 'level': 'HECHO_COMPUTACIONAL', 'life': None,
            'text': 'Tras el bloqueo se autorizó un cierre de 45 minutos, sin reiniciar la campaña. El Word 1.19 se actualizó estructuralmente, sin QA visual.',
            'scope': 'El cierre no certifica mente general ni promoción; Full se juzga por su prueba exacta independiente.',
            'source_ids': [delayid, reportid, manual_id, editorial_id], 'limits': ['Cero páginas de render verificadas.', 'No se reescriben resultados de la reserva.']})
        value['closure_scope'] = 'AUTHORIZED_45_MINUTE_CLOSURE_WORD_REAL_VISUAL_QA_UNAVAILABLE'
    if args.full_proof:
        if not args.extended_close:
            raise ValueError('La prueba Full posterior requiere cierre ampliado explícito')
        proof = (root / args.full_proof).resolve()
        proof_refs = tree(proof, 'EVIDENCIA_CAUSAL/FULL_GENESIS')
        result = json.loads((proof / 'VERIFICACION_FULL_GENESIS_EXTERNA.json').read_bytes())
        final_record = result.get('final_record')
        completed = result.get('zip_still_exact') is True and result.get('error') is None
        for row in value['attempts']:
            if row['id'] == 'FULL_APD05':
                row.update(status='CLOSED_RESULT' if completed else 'CLOSED_INSTRUMENT_FAILURE', source_ids=proof_refs,
                    scope='Intento real de prueba del ZIP Full exacto. El protocolo previó dos procesos, pero el recibo documenta qué partes se ejecutaron: apertura Timeout, resto NOT_EXECUTED. No es fallo cognitivo ni promoción de MAIN.')
        value['full_status'] = 'EXACT_ZIP_GUI_CONTINUITY_PROOF_CLOSED' if completed else 'INFRASTRUCTURE_PROOF_INCOMPLETE_NOT_COGNITIVE_FAILURE'
        if final_record:
            value['lives'].append({'id': final_record['life_id'],
                'parent': {'life': 'APD05_MAIN', 'source_tick': 684418, 'source_snapshot_sha256': pair['snapshot_sha256']},
                'N': final_record['physical']['N'], 'tick': final_record['physical']['tick'],
                'snapshot_sha256': final_record['snapshot_sha256'], 'status': 'EXTRACTED_FULL_PERSONAL_PROOF_FORK',
                'available': ['La admisión y las señales físicas se examinan en los primarios y el lector independiente.'],
                'not_currently_proven': ['Promoción a ACTIVO', 'Aprendizajes transferidos a MAIN', 'Mente general'],
                'continuation': {'extracted_root': result['extracted_root'], 'record': final_record['snapshot'], 'full_state_in_analysis': False}})
        add(closing / 'PROTOCOLO_FULL_GENESIS_APD05_CERRADO_R01.json',
            'CODIGO_DE_CIERRE/PROTOCOLO_FULL_GENESIS_APD05_CERRADO_R01.json', 'prospectively_frozen_Full_protocol')
        add(closing / 'verificar_full_genesis_apd05_r01.py', 'CODIGO_DE_CIERRE/verificar_full_genesis_apd05_r01.py',
            'executed_exact_Full_verification_driver_not_archived_recalc')
        add(closing / 'recalcular_prueba_full_genesis_raw_n0_r01.py',
            'RECALCULO/recalcular_prueba_full_genesis_raw_n0_r01.py', 'independent_partial_Full_RAW_reader_N0')
        add(closing / 'RECALCULO_FULL_PRIMARIOS_1625_N0_R02.json',
            'RECALCULO/REFERENCIA_FULL_PARCIAL_N0.json', 'actual_partial_Full_golden_NOT_EXECUTED_not_zero_score')
        jobs.append({'id': 'FULL_PARCIAL_N0', 'base': '.',
                     'script': 'RECALCULO/recalcular_prueba_full_genesis_raw_n0_r01.py',
                     'args': ['--root', {'input': 'EVIDENCIA_CAUSAL/FULL_GENESIS'},
                              '--protocol', {'input': 'CODIGO_DE_CIERRE/PROTOCOLO_FULL_GENESIS_APD05_CERRADO_R01.json'},
                              '--out', '{output}'],
                     'expected': 'RECALCULO/REFERENCIA_FULL_PARCIAL_N0.json',
                     'comparison': 'bytes', 'timeout_seconds': 60})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')
    expanded = sum((root / f['source']).stat().st_size for f in files)
    component_expanded = 0
    for row in components:
        folder = root / row['source']
        component_expanded += sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())
    print(json.dumps({'selection': str(args.out), 'sha256': sha(args.out), 'status': value['status'],
                      'individual_files': len(files), 'closed_components': len(components),
                      'selected_expanded_bytes': expanded + component_expanded, 'jobs': len(jobs),
                      'no_ZIP_created': True, 'new_native_ticks': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
