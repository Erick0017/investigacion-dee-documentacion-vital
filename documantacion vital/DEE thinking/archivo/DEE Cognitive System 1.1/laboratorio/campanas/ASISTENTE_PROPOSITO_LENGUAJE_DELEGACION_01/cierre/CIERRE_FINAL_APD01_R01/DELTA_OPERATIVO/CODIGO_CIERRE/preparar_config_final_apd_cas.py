"""Freeze an explicitly approved APD analysis configuration, without ZIP/native work.

Run only after Root has installed the final metadata and the exact Full proof is
closed. This creates a fresh local analysis delta, never changes the system,
never imports DEE, and never asserts a native result from documentary copying.
"""
import argparse, copy, hashlib, json, shutil
from pathlib import Path, PurePosixPath


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8') as handle:
        json.dump(value, handle, sort_keys=True, ensure_ascii=False, indent=2)
        handle.write('\n')


def rel(name):
    if not isinstance(name, str) or '\\' in name or ':' in name:
        raise ValueError('Portable relative target required')
    value = PurePosixPath(name)
    if value.is_absolute() or any(v in ('', '.', '..') for v in value.parts):
        raise ValueError('Unsafe target')
    return value.as_posix()


def cp(source, target):
    source = source.resolve(strict=True)
    if source.is_symlink() or getattr(source.stat(follow_symlinks=False), 'st_file_attributes', 0) & 0x400:
        raise ValueError('No reparse/symlink source')
    data = source.read_bytes(); digest = hashlib.sha256(data).hexdigest()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as handle:
        handle.write(data)
    if source.read_bytes() != data or sha(target) != digest:
        raise ValueError('Source changed during final capture: ' + str(source))
    return {'source_local_locator': str(source), 'bytes': len(data), 'sha256': digest}


def verified_stage(stage):
    root = Path(stage['source']).resolve(strict=True)
    name = stage.get('manifest', 'MANIFIESTO.json')
    if stage.get('approved_manifest_sha256') and sha(root/name) != stage['approved_manifest_sha256']:
        raise ValueError('Closed manifest differs from the approved record')
    manifest = read(root / name)
    expected = {}
    for row in manifest['members']:
        member = rel(row.get('file', row.get('path')))
        if member in expected:
            raise ValueError('Repeated closed-stage member')
        expected[member] = row
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    if actual != set(expected) | {name}:
        raise ValueError('Closed stage has missing/additional files: ' + str(root))
    for member, row in expected.items():
        path = root / member
        if path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
            raise ValueError('Closed bytes changed: ' + str(path))
    plan = read(root / stage.get('plan', 'PLAN_RECALCULO.json'))
    jobs = plan.get('jobs', plan.get('cases'))
    if not isinstance(jobs, list):
        raise ValueError('Unknown closed-stage plan')
    return {'namespace': stage['namespace'], 'source_local_locator': str(root),
            'manifest_sha256': sha(root / name), 'logical_files': len(actual),
            'case_count': len(jobs) + len(stage.get('extra_cases', []))}


def without_nulls(value):
    if isinstance(value, dict):
        return {k: without_nulls(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [without_nulls(v) for v in value if v is not None]
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('root', 'close', 'full-stage', 'public-map', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--approved-by-root', action='store_true', required=True)
    args = parser.parse_args()
    root = args.root.resolve(strict=True); close = args.close.resolve(strict=True)
    out = args.out.resolve()
    if out.parent != close or out.exists():
        raise ValueError('A fresh direct child of the current closure directory is required')
    pending_config = close / 'CONFIG_ANALISIS_CANDIDATA_APD01_R07.json'
    previous = read(pending_config)
    if previous['status'] != 'PREPARACION_NO_FINAL' or previous['known_closed_cases'] != 27:
        raise ValueError('Expected the approved seven-stage/27-case preparation')
    stages = copy.deepcopy(previous['stages'])
    full = {'namespace': 'PRUEBA_PAQUETE_EXACTO', 'source': str(args.full_stage.resolve(strict=True)),
            'manifest': 'MANIFIESTO.json', 'plan': 'PLAN_RECALCULO.json'}
    closed = [verified_stage(stage) for stage in stages + [full]]
    if closed[-1]['case_count'] != 1 or sum(row['case_count'] for row in closed) != 28:
        raise ValueError('Exactly27 prior cases and one actually closed Full proof required')
    material_index = read(args.public_map)
    items = material_index['files']
    targets = [rel(item['to']) for item in items]
    if len(targets) != len(set(targets)):
        raise ValueError('Public target collision')
    required = {'INFORME_CIENTIFICO.md', 'CAPACIDADES_POR_VIDA.csv', 'COBERTURA.json',
                'INCORPORACIONES.md', 'CONTINUIDAD_ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION.json',
                'MANUAL_MAESTRO_APD01.docx', 'DOCUMENTOS/EDICION_MANUAL_APD01.json',
                'GUIA_ASISTENTE_APD01.md'}
    if not required.issubset(targets):
        raise ValueError('Missing approved final public documents: ' + str(sorted(required-set(targets))))
    editorial = read(next(Path(item['source']) for item in items if item['to'] == 'DOCUMENTOS/EDICION_MANUAL_APD01.json'))
    word = next(Path(item['source']) for item in items if item['to'] == 'MANUAL_MAESTRO_APD01.docx')
    if sha(word) != editorial['sha256'] or word.stat().st_size != editorial['bytes']:
        raise ValueError('Word does not match its real editorial record')
    if editorial['sha256'] != '2cc8c39640a5926963459ec648f6c3bc446be9b10e5edb6402fd2d74bf429a70':
        raise ValueError('Word is not the explicitly approved edition1.15 bytes')
    continuity_item = next(item for item in items if item['to'] == 'CONTINUIDAD_ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION.json')
    continuity = read(Path(continuity_item['source']))
    if 'PROPOSAL' in continuity.get('status', '').upper() or 'CANDIDATE' in continuity.get('status', '').upper():
        raise ValueError('Use installed final continuity, not its proposal')
    installed_expected = {
        root/'sistema/contratos/ASISTENTE_PROPOSITO_01.json': '757f39e2ef7a532e7c06e73ef7f61257715215dc34a1dc221c7d3abab7e142e2',
        root/'sistema/documentacion/GUIA_ASISTENTE_APD01.md': '62d3aa12cf1d47dd4d20beee6884f301a65d117ccbcda89a1a0a786b4a9bc9b3',
        root/'CONTINUIDAD_ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION.json': 'd9739e6714c0ff42c2be8bd0b3b721a943b8586e0baf9d46642e47e417feeeb9'}
    for path, digest in installed_expected.items():
        if sha(path) != digest:
            raise ValueError('Installed metadata differs from the explicitly approved Root revision: '+str(path))

    out.mkdir()
    public_files = []; captured = []
    for item in items:
        target = rel(item['to']); source = Path(item['source'])
        if item.get('sha256') and sha(source) != item['sha256']:
            raise ValueError('Approved public source changed: ' + str(source))
        frozen = out / 'PUBLICOS' / target
        record = cp(source, frozen); record['analysis_target'] = target; captured.append(record)
        public_files.append({'source': str(frozen), 'to': target})

    delta = out / 'DELTA_OPERATIVO'
    delta.mkdir()
    planned = read(close / 'PLAN_DELTA_CANDIDATO_APD01_R03.json')
    system_paths = [row['relative_system_path'] for row in planned['files_observed']]
    system_paths += ['app/process_control.py', 'app/cliente_mente_unificada.py',
                     'app/importacion_emparejada.py', 'contratos/ASISTENTE_PROPOSITO_01.json',
                     'documentacion/GUIA_ASISTENTE_APD01.md', 'capacidades/CATALOGO_CAPACIDADES.json']
    delta_records = []
    for name in dict.fromkeys(system_paths):
        record = cp(root / 'sistema' / name, delta / 'sistema' / name)
        record['relative_system_path'] = name; delta_records.append(record)
    for name in ('LEER_PRIMERO.md', 'PROYECTO.json', 'REANUDACION.json',
                 'CONTINUIDAD_ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION.json'):
        record = cp(root / name, delta / 'RAIZ' / name)
        record['scope'] = 'Actual installed root metadata; no native learned content inserted'
        delta_records.append(record)
    preimages = close / 'ANTES_PUBLICACION_APD01'
    for name in ('LEER_PRIMERO.md', 'PROYECTO.json', 'REANUDACION.json',
                 'sistema/capacidades/CATALOGO_CAPACIDADES.json'):
        record = cp(preimages / name, delta / 'ANTES_PUBLICACION' / name)
        record['scope'] = 'Exact pre-publication metadata image, not the current operational source'
        delta_records.append(record)
    close_sources = [
        close / 'proponer_cierre_apd_desde_corte_n0.py',
        close / 'preparar_config_final_apd_cas.py',
        close / 'ensamblar_analisis_apd_cas_R03.py',
        close / 'repetir_todo_apd_cas.py',
        close / 'verificar_protegidos_apd01.py',
        close / 'sellar_verificacion_externa_apd01.py',
        close.parent / 'documentos/actualizar_manual_apd01.py',
        close / 'BORRADOR_CIENTIFICO_APD01/cerrar_ciencia_r04_n0.py',
        close / 'BORRADOR_CIENTIFICO_APD01/pulir_texto_manual_final_n0.py',
        close / 'BORRADOR_CIENTIFICO_APD01/incorporar_word_real_n0.py',
        close / 'BORRADOR_CIENTIFICO_APD01/validar_ciencia_final_r04_n0.py']
    for source in close_sources:
        record = cp(source, delta / 'CODIGO_CIERRE' / source.name)
        record['scope'] = 'Exact N0/editorial/assembly source, not a native capability'
        delta_records.append(record)
    write(delta / 'FUENTES_EXACTAS.json', {'schema': 'APD01.final_analysis_code_delta.v1',
          'sources': delta_records, 'new_native_ticks': 0,
          'scope': 'Selected exact Cognitive source/contract/guide/catalog delta and closure/editorial code. Not an installer, motor, learned memory transfer, OS sandbox proof or operational backup.'})
    write(delta / 'PLAN_RECALCULO.json', {'schema': 'DEE.portable_recalculation.plan.v1', 'jobs': [],
          'scope': 'Exact source/documentary delta; no new independent scientific case claimed.'})
    delta_members = [{'file': p.relative_to(delta).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)}
                     for p in sorted(delta.rglob('*')) if p.is_file()]
    write(delta / 'MANIFIESTO.json', {'members': delta_members, 'self_exclusion': 'MANIFIESTO.json only'})
    stages += [full, {'namespace': 'DELTA_OPERATIVO', 'source': str(delta),
                      'manifest': 'MANIFIESTO.json', 'plan': 'PLAN_RECALCULO.json'}]
    closed.append(verified_stage(stages[-1]))

    omissions = read(close / 'INDICE_FUENTES_Y_OMISIONES_CANDIDATO_APD01_R03.json')
    for key in ('future_sources_not_yet_closed', 'public_document_slots', 'previous_template_sha256',
                'prospective_case_count_scope', 'prospective_cases_after_service_before_postpanel_or_fullproof'):
        omissions.pop(key, None)
    omissions.update({'status': 'CLOSED_APPROVED_FOR_ANALYSIS', 'closed_sources_exact': closed,
                      'currently_closed_recalculation_cases': 28, 'final_seal_authorized': True,
                      'public_documents_exact': captured, 'new_native_ticks': 0,
                      'capture_precedes_archive_creation': True,
                      'archive_identity_scope': 'Root explicitly authorizes sealing. This capture precedes ZIP creation; the exact ZIP SHA256 and its extract-and-recalculate proof belong in the external final verification, never inside the same archive hash cycle.',
                      'full_proof_is_closed_archived_operational_evidence_not_a_new_MAIN_capability': True,
                      'Word_visual_validation_scope': editorial['visual_validation']})
    omission_path = out / 'INDICE_FUENTES_Y_OMISIONES.json'
    write(omission_path, omissions)
    public_files.append({'source': str(omission_path), 'to': 'INDICE_FUENTES_Y_OMISIONES.json'})
    config = without_nulls({'schema': 'APD01.analysis_assembly_config.v1',
              'status': 'CLOSED_APPROVED_FOR_ANALYSIS', 'stages': stages, 'public_files': public_files,
              'approved_closed_cases': 28, 'new_native_ticks': 0,
              'approval_scope': 'Root explicitly approved final source/documents and one closed Full proof; ZIP seal and exact-archive verification remain separate later operations.',
              'source_preparation_sha256': sha(pending_config), 'public_approval_map_sha256': sha(args.public_map)})
    config_path = out / 'CONFIG_ANALISIS_FINAL.json'
    write(config_path, config)
    record = {'new_native_ticks': 0, 'ZIP_generated': False, 'source_actor_modified': False,
              'closed_namespaces': len(stages), 'closed_cases': 28,
              'config_sha256': sha(config_path), 'delta_manifest_sha256': sha(delta/'MANIFIESTO.json'),
              'Word_sha256': editorial['sha256'], 'Word_visual_validation': editorial['visual_validation'],
              'public_file_count': len(public_files)}
    write(out / 'REGISTRO_PREPARACION_FINAL_N0.json', record)
    print(json.dumps(record))


if __name__ == '__main__':
    main()
