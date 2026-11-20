"""Add the actually closed service to the pending APD analysis, without sealing.

This is a standard-library metadata/byte-index operation, not a scientific
recalculation or a DEE continuation. Source observations are not a final freeze.
"""
import argparse, copy, hashlib, json, zlib
from pathlib import Path


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def emit(path, value):
    with path.open('x', encoding='utf8') as handle:
        json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--close', type=Path, required=True)
    parser.add_argument('--system', type=Path, required=True)
    parser.add_argument('--cut', type=Path, required=True)
    parser.add_argument('--six-stage-cas', type=Path, required=True)
    args = parser.parse_args()
    close = args.close.resolve(strict=True)
    service = close / 'SERVICIO_APD01_R01'
    manifest_path = service / 'MANIFIESTO.json'
    expected_manifest = '3dbdaa2dfa3d007133dcba36f649dca544ea3f8779c61e3419a008fa2bde3a03'
    if sha(manifest_path) != expected_manifest:
        raise ValueError('Closed service manifest differs from the approved notice')
    manifest = read(manifest_path)
    members = {row['file']: row for row in manifest['members']}
    actual = {p.relative_to(service).as_posix() for p in service.rglob('*') if p.is_file()}
    if len(members) != len(manifest['members']) or actual != set(members) | {'MANIFIESTO.json'}:
        raise ValueError('Closed service has missing, duplicated or additional members')
    # Verify bytes once, without executing any of its thirteen scientific cases.
    for name, row in members.items():
        path = service / name
        if path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
            raise ValueError('Closed service changed: ' + name)
    jobs = read(service / 'PLAN_RECALCULO.json')['jobs']
    if len(jobs) != 13 or len({j['name'] for j in jobs}) != 13:
        raise ValueError('Exactly thirteen uniquely named closed service cases are required')
    cut = read(args.cut)
    persistent = cut['persistent_service']
    if cut['issues'] or not persistent['owner_stopped'] or persistent['pending_or_uncertain']:
        raise ValueError('Expected an actual stopped cut with no unresolved queue or integrity issue')
    final_cut = {'source_local_locator': str(args.cut.resolve()), 'sha256': sha(args.cut),
                 'main': cut['main'], 'paired_export': cut['paired_export'],
                 'clean_closure': persistent['clean_closure'],
                 'operational_issues': cut['operational_issues'],
                 'epoch_closed': persistent['epoch_closed'],
                 'last_panel_scope': persistent['last_panel_scope']}

    previous_path = close / 'CONFIG_ANALISIS_CANDIDATA_APD01_R06.json'
    config = read(previous_path)
    if config['status'] != 'PREPARACION_NO_FINAL' or len(config['stages']) != 6:
        raise ValueError('Preserve the existing six-stage preparation unchanged')
    config['previous_configuration_sha256'] = sha(previous_path)
    config['configuration_revision'] = 'R07_actual_closed_service13_and_six_closed_stages14; final documents, system metadata and exact Full proof still pending'
    config['stages'].append({'namespace': 'SERVICIO_APD01', 'source': str(service),
                             'manifest': 'MANIFIESTO.json', 'plan': 'PLAN_RECALCULO.json',
                             'approved_manifest_sha256': expected_manifest})
    config['known_closed_cases'] = 27
    config['provisional_final_cases_if_expected_service_and_fullproof_close'] = 28
    config['R04_final_state_not_captured'] = False
    config['actual_saved_campaign_cut'] = final_cut
    config['candidate_stage_slots'] = [s for s in config['candidate_stage_slots']
                                        if s['namespace'] not in ('SERVICIO_APD01', 'SERVICIO_APD01_R04_UN_OWNER')]
    for item in config['candidate_stage_slots']:
        if item['namespace'] == 'POST_RESERVA_APD01':
            item['status'] = 'UNEXECUTED_PROPOSAL_SUPERSEDED_BY_ACTUALLY_EXECUTED_R04'
            item['scope'] = 'Historical two-request draft was not executed. Actual R04 results and its final panels are included once inside SERVICIO_APD01.'
    config['pending_components'] = [item for item in config['pending_components']
                                      if item['id'] not in ('SERVICIO_RESERVADO_UNA_HORA', 'PANEL_POST_RESERVA_Y_CORTE_REAL_FINAL')]
    for item in config['pending_components']:
        if item['id'] == 'INFORME_CIENTIFICO_ROOT_Y_CONTINUIDAD':
            item['status'] = 'WAIT_FOR_ROOT_INSTALLED_REPORT_AND_CONTINUITY_FROM_ACTUAL_R04_CUT'
    config['no_scientific_case_recalculated_by_this_preparation'] = True
    emit(close / 'CONFIG_ANALISIS_CANDIDATA_APD01_R07.json', config)

    before_index = close / 'INDICE_FUENTES_Y_OMISIONES_CANDIDATO_APD01_R02.json'
    index = read(before_index)
    index['schema'] = 'APD01.final_sources_and_omissions.template.v3'
    index['previous_template_sha256'] = sha(before_index)
    index['closed_sources_exact'].append({
        'namespace': 'SERVICIO_APD01', 'source_local_locator': str(service),
        'manifest_relative': 'MANIFIESTO.json', 'manifest_sha256': expected_manifest,
        'manifest_members_without_self': len(members), 'selected_cases': 13,
        'new_archived_recalculation_repeated_by_this_preparation': False,
        'check_scope': 'Exact closed manifest, membership, sizes and SHA256 checked; the existing thirteen portable scientific cases were not repeated.'})
    index['currently_closed_recalculation_cases'] = 27
    index['prospective_cases_after_service_before_postpanel_or_fullproof'] = 27
    index['prospective_case_count_scope'] = '27 cases are actually closed (six namespaces14 plus service13). One additional exact Full proof remains pending, for a possible28; no Full outcome presumed.'
    index['future_sources_not_yet_closed'] = [s for s in index['future_sources_not_yet_closed']
                                              if s['namespace'] not in ('SERVICIO_APD01', 'SERVICIO_APD01_R04_UN_OWNER')]
    index['final_campaign_cut'] = final_cut
    index['final_paired_state_locator'] = cut['paired_export']
    index['final_seal_authorized'] = False
    index['service_negative_scope'] = 'R01/R02 technical interruptions and queued histories, R03 clean=false and its incomplete actor source map, both N0 Job fixtures, and unexecuted pre-poll sources remain in the exact closed service stage. R04 single-owner evidence does not rewrite or add minutes to them.'
    for name, row in sorted(members.items()):
        if 'OMISION' in name.upper() or 'ESTADOS_COMPLETOS' in name.upper():
            index['original_omission_indexes_to_preserve'].append({
                'namespace': 'SERVICIO_APD01', 'relative_path': name, 'bytes': row['bytes'],
                'sha256': row['sha256'],
                'scope': 'Preserve this original local-state/deep-data omission index exactly; the analysis is not a paired operational backup.'})
    emit(close / 'INDICE_FUENTES_Y_OMISIONES_CANDIDATO_APD01_R03.json', index)

    old_delta_path = close / 'PLAN_DELTA_CANDIDATO_APD01_R02.json'
    delta = read(old_delta_path)
    delta['previous_template_sha256'] = sha(old_delta_path)
    delta['schema'] = 'APD01.system_delta_candidate.v3'
    delta['source_system_local_locator'] = str(args.system.resolve(strict=True))
    delta['source_capture_is_not_final_freeze'] = True
    delta['no_delta_stage_or_manifest_or_seal_created'] = True
    for item in delta['files_observed']:
        path = args.system / item['relative_system_path']
        data = path.read_bytes()
        item['previous_observation_sha256'] = item['sha256_observed_not_final_freeze']
        item['sha256_observed_not_final_freeze'] = hashlib.sha256(data).hexdigest()
        item['bytes_observed'] = len(data)
        item['final_selection_status'] = 'OBSERVED_AFTER_SERVICE_FREE_WAIT_FOR_ROOT_FINAL_METADATA_AND_FREEZE'
    delta['pending_metadata_paths'] = [
        'contratos/ASISTENTE_PROPOSITO_01.json',
        'documentacion/GUIA_ASISTENTE_APD01.md',
        'capacidades/CATALOGO_CAPACIDADES.json']
    delta['pending_root_document_paths'] = [
        'CONTINUIDAD_ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION.json',
        'Manual Maestro edition1.15 actual Word path supplied by Root',
        'Final scientific report and capability tables supplied by Root']
    emit(close / 'PLAN_DELTA_CANDIDATO_APD01_R03.json', delta)

    old_objects = read(args.six_stage_cas / 'INDICE_OBJETOS_Y_ALIASES.json')['objects']
    known = set(old_objects)
    new_objects = {}
    for path in sorted(service.rglob('*')):
        if path.is_file():
            data = path.read_bytes(); digest = hashlib.sha256(data).hexdigest()
            if digest not in known and digest not in new_objects:
                new_objects[digest] = {'bytes': len(data), 'deflate_estimate': len(zlib.compress(data, 9))}
    six_base = 5011586
    additional = sum(row['deflate_estimate'] for row in new_objects.values())
    sizing = {'status': 'PREPARACION_NO_FINAL', 'native_ticks': 0, 'ZIP_generated': False,
              'scientific_recalculations_repeated': 0, 'closed_cases': 27,
              'six_stage_existing_measured_deflate_estimate': six_base,
              'service_manifest_sha256': expected_manifest,
              'closed_service_logical_files': len(actual),
              'closed_service_logical_bytes': sum(p.stat().st_size for p in service.rglob('*') if p.is_file()),
              'additional_service_unique_objects': len(new_objects),
              'additional_service_deflate_estimate': additional,
              'known_seven_stage_estimate_before_new_CAS_metadata': six_base + additional,
              'remaining_to16000000_before_final_unknowns': 16000000 - six_base - additional,
              'unmeasured': ['exact Full proof future', 'root final Word/report/continuity/capability tables',
                             'final installed source/contract/guide/catalog delta', 'new CAS/ZIP index and central directory overhead'],
              'scope': 'Read-only exact-content sizing, not final ZIP size or a repeated scientific proof. No unique negative excluded.'}
    emit(close / 'PLAN_TAMANOS_CAS_SIETE_CERRADOS_APD01_N0.json', sizing)
    print(json.dumps({'closed_stages': 7, 'closed_cases': 27,
                      'Full_case_future': 1, 'actual_cut_tick': cut['main']['tick'],
                      'service_files': len(actual), 'service_manifest': expected_manifest,
                      'known_estimate': sizing['known_seven_stage_estimate_before_new_CAS_metadata'],
                      'native_ticks': 0, 'ZIP_generated': False,
                      'source_files_observed_not_frozen': len(delta['files_observed'])}))


if __name__ == '__main__':
    main()
