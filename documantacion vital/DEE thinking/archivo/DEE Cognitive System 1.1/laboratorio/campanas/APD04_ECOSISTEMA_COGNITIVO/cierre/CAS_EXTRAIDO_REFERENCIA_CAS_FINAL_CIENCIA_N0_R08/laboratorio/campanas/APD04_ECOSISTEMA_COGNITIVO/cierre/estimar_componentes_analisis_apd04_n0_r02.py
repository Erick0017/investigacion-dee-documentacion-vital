"""Amplía estimación R01 cerrada; sólo lee selección explícita y mide DEFLATE."""
import argparse
import hashlib
import json
from pathlib import Path
import zlib


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    lab = root / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
    ev = root / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
    prior_path = lab / 'cierre/PROPUESTA_COMPONENTES_Y_TAMANOS_N0_R01.json'
    prior_bytes = prior_path.read_bytes()
    prior = json.loads(prior_bytes)
    seen = {x['path'] for g in prior['groups'] for x in g['files']}
    seen_hashes = {x['sha256']: x['path'] for g in prior['groups'] for x in g['files']}
    assert not args.out.exists()
    assert args.out.resolve().is_relative_to(lab)
    groups = []
    definitions = [
        ('09_ABC_dosis_completa', [(ev / 'ATENCION_ABC_DOSIS_COMPLETA_N0_R02', True)], 'Closed N0 correction; 246/276/123 all Native inputs, including channel records'),
        ('10_arranque_admision_calibracion_e_incidencias', [(ev / name, name != 'ADMISION_LEXICA_R01') for name in
          ('ARRANQUE_R01', 'ADMISION_LEXICA_R01', 'CALIBRACION_R01', 'CALIBRACION_R02',
           'ATENCION_CONSECUENCIAS_AUX_R01', 'ACTUADOR_R02_PREPARACION_N0_R01',
           'ACTUADOR_R02_SUPERVISION_N0_R01', 'ACTUADOR_R02_SUPERVISION_R01')],
         'Include all attempted variants/instrument failures. ADMISION includes root files only: the full inherited worker/snapshot tree is an indexed local omission, not new APD04 evidence.'),
        ('11_revisiones_driver_y_planes', [(lab / 'ejecucion', True)],
         'Exact source revisions and plans, including byte-confirmed reconstructed failed R01; plans do not prove completion.'),
        ('12_propuestas_NO_NATIVE', [(lab / 'native_candidates/PROPUESTA_ACTUADOR_R03_R02', True),
          (lab / 'controles_diseno/PROPUESTA_DOS_AUX_WAIT_R03_SAFE_N0_R05', True)],
         'Prospective WAIT preparation and N0 tests only, not executed Native or acquired capacity.'),
        ('13_borradores_cientificos_y_herramientas_recalculo', [(lab / 'cierre', False)],
         'Existing R01-R07 scientific revisions and portable calculators; final report may supersede drafts but the corrections remain traceable.')]
    forbidden = ('.deetsnap', '.sqlite', '.whl', '.pyd', '.zip', '.exe', '.dll', '.pyc')
    excluded = []
    for group_id, sources, status in definitions:
        group = {'id': group_id, 'status': status, 'files': [], 'bytes': 0, 'deflate_payload_bytes': 0,
                 'estimated_headers_bytes': 0, 'byte_dedup_savings_if_materialized': 0}
        for base, recursive in sources:
            assert base.is_dir(), str(base)
            files = base.rglob('*') if recursive else base.iterdir()
            for path in sorted(files):
                if not path.is_file():
                    continue
                rel = path.relative_to(root).as_posix()
                if rel in seen or path == args.out or path.name.startswith('PROPUESTA_COMPONENTES_Y_TAMANOS'):
                    continue
                if any(x in path.name.lower() for x in forbidden) or '__pycache__' in path.parts:
                    excluded.append({'path': rel, 'reason': 'Not part of compact analysis'})
                    continue
                assert not path.is_symlink()
                before = path.stat()
                data = path.read_bytes()
                after = path.stat()
                assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns), rel
                digest = hashlib.sha256(data).hexdigest()
                compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
                size = len(compressor.compress(data) + compressor.flush())
                overhead = 98 + 2 * (len(rel.encode('utf8')) + 48)
                row = {'path': rel, 'bytes': len(data), 'sha256': digest,
                       'deflate_payload_bytes': size, 'estimated_zip_headers_bytes': overhead}
                if digest in seen_hashes:
                    row['same_bytes_as'] = seen_hashes[digest]
                    group['byte_dedup_savings_if_materialized'] += size + overhead
                else:
                    seen_hashes[digest] = rel
                seen.add(rel)
                group['files'].append(row)
                group['bytes'] += len(data)
                group['deflate_payload_bytes'] += size
                group['estimated_headers_bytes'] += overhead
        group['file_count'] = len(group['files'])
        group['estimated_zip_bytes_without_path_dedup'] = group['deflate_payload_bytes'] + group['estimated_headers_bytes']
        groups.append(group)
    all_groups = prior['groups'] + groups
    current = sum(g['estimated_zip_bytes_without_path_dedup'] for g in all_groups) + 22
    future = [
        {'id': 'four_brief_cohorts_complete', 'bytes_budget': 1600000, 'status': 'Only N2 closed per Controls; include all four regardless outcome after their closure; estimated 100-300k gzip/branch plus code, budget not quota'},
        {'id': 'remaining_reserve_and_possible_R03_NATIVE', 'bytes_budget': 2600000, 'status': 'Active reserve; R03 not yet Native. Preserve all outcomes. RAW-equal cuts may be deduplicated losslessly only after exact regeneration checks'},
        {'id': 'Word_final_report_capability_tables_Full_exact_proof_and_final_index', 'bytes_budget': 1200000, 'status': 'Pending authorization/closure. Exclude actual Full archive and engine from analysis, not its verification evidence'}]
    total = current + sum(x['bytes_budget'] for x in future)
    result = {'schema': 'APD04.analysis.components_and_deflate_estimate.N0.R02',
              'status': 'PROPOSAL_ONLY_NOT_ASSEMBLED_NOT_SEALED', 'new_native_ticks': 0, 'created_zip_count': 0,
              'prior_estimate': {'path': prior_path.relative_to(root).as_posix(), 'sha256': hashlib.sha256(prior_bytes).hexdigest(),
                                 'reused_measured_payloads_without_reauditing_originals': True},
              'groups': all_groups, 'excluded_additional_files': excluded,
              'proposed_expanded_bytes': sum(g['bytes'] for g in all_groups),
              'proposed_files': sum(g['file_count'] for g in all_groups),
              'estimated_current_zip_bytes_without_dedup': current,
              'future_budget_reservations_not_measured_evidence': future,
              'estimated_total_with_future_budgets': total, 'strict_limit': 16000000,
              'headroom_after_future_budgets': 16000000 - total,
              'limits': prior['limits'] + [
                  'R02 totals 246/276/123 and ACT 211/140 supersede port-only counts; no causal claim or original primary bytes changed.',
                  'Do not deduplicate different source revisions or omit negative branches to meet transfer size.',
                  'Native full snapshots and inherited worker archives remain local, with exact source manifests/indexes; array excerpts do not replace those operative states.',
                  'Reserved future budgets are estimates, never truncation limits for indispensable evidence; exact final ZIP size must be verified.']}
    with args.out.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(result, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps({k: result[k] for k in ('status', 'proposed_files', 'proposed_expanded_bytes',
          'estimated_current_zip_bytes_without_dedup', 'estimated_total_with_future_budgets',
          'headroom_after_future_budgets', 'created_zip_count')}))


if __name__ == '__main__':
    main()
