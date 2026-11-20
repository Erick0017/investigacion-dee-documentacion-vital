"""Estima DEFLATE en memoria: no crea ZIP, no importa motor ni lee vidas vivas."""
import argparse
import hashlib
import json
from pathlib import Path
import zlib


GROUPS = [
    ('01_main_instrumento_y_prefijos', [
        'MAIN_PILOTO_R01', 'MAIN_PILOTO_R02', 'MAIN_PREPARACION_R03',
        'MAIN_ADQUISICION_R01', 'MAIN_CONTENIDO_Y_CARGA_R01',
        'CONTINUABLE_OPERATIVO_R01', 'FORK_CONTINUABLE_R01']),
    ('02_controles_lexico_y_referencias', [
        'CONTROLES_LEXICO_REFERENCIA_AUX_R01', 'CONTROLES_DOCENTE_B_AUX_R01',
        'CONTROLES_REFERENCIAS_RESTANTES_AUX_R02']),
    ('03_autopsia_supervision', ['DIAGNOSTICO_SUPERVISION_MAIN_R01']),
    ('04_recalculo_main_y_panel_heredado', [
        'RECALCULO_MAIN_CERRADO_PREFIJO_Y_ADVERSO_R01',
        'BORRADOR_CIENTIFICO_PREFIJO_CERRADO_N0_R01', 'PANEL_HEREDADO_RAW_N0_R01']),
    ('05_sensores_y_control_ABC', [
        'ATENCION_CONSECUENCIAS_AUX_R02_BC/EVIDENCIA_PORTABLE_R02',
        'SENSORES_Y_LEXICO_R01/EVIDENCIA_PORTABLE',
        'C_DENSIFICACION_CONTEXTOS_R02_N0', 'HANDOFF_NATIVE_FINAL_N0_R02']),
    ('06_r04_adverso_cerrado', ['CIERRE_SENSOR_R04_N0_R04']),
    ('07_actuador_R02_REAL_OMIT_y_correccion', [
        'ACTUADOR_R02_AUX_R01/EVIDENCIA_PORTABLE_R01',
        'ACTUADOR_R02_AUX_R01/CORRECCION_Y_DOSSIER_N0_R02']),
    ('08_reserva_prefijo_parcial_2_completadas', ['RESERVA60_PREFIJO_WORK02_N0_R01']),
]
FORBIDDEN = ('.deetsnap', '.sqlite', '.whl', '.pyd', '.zip', '.exe', '.dll')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    ev = args.root / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
    lab = args.root / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO'
    assert not args.out.exists(), 'No overwrite'
    assert args.out.resolve().is_relative_to(lab.resolve())
    seen_paths, seen_hashes, rows, excluded = set(), {}, [], []
    for group_id, folders in GROUPS:
        group = {'id': group_id, 'files': [], 'bytes': 0, 'deflate_payload_bytes': 0,
                 'estimated_headers_bytes': 0, 'byte_dedup_savings_if_materialized': 0}
        for folder in folders:
            base = ev / folder
            assert base.is_dir(), str(base)
            for source in sorted(base.rglob('*')):
                if not source.is_file() or source in seen_paths:
                    continue
                assert not source.is_symlink(), str(source)
                seen_paths.add(source)
                rel = source.relative_to(args.root).as_posix()
                if any(marker in source.name.lower() for marker in FORBIDDEN):
                    excluded.append({'path': rel, 'reason': 'Operational snapshot, database, engine or archive excluded from analysis proposal'})
                    continue
                before = source.stat()
                data = source.read_bytes()
                after = source.stat()
                assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns), rel
                digest = hashlib.sha256(data).hexdigest()
                compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
                size = len(compressor.compress(data) + compressor.flush())
                # ZIP local+central directory with a conservative destination filename allowance.
                overhead = 98 + 2 * (len(rel.encode('utf8')) + 48)
                row = {'path': rel, 'bytes': len(data), 'sha256': digest,
                       'deflate_payload_bytes': size, 'estimated_zip_headers_bytes': overhead}
                if digest in seen_hashes:
                    row['same_bytes_as'] = seen_hashes[digest]
                    group['byte_dedup_savings_if_materialized'] += size + overhead
                else:
                    seen_hashes[digest] = rel
                group['files'].append(row)
                group['bytes'] += len(data)
                group['deflate_payload_bytes'] += size
                group['estimated_headers_bytes'] += overhead
        group['file_count'] = len(group['files'])
        group['estimated_zip_bytes_without_path_dedup'] = group['deflate_payload_bytes'] + group['estimated_headers_bytes']
        rows.append(group)
    closed_estimate = sum(r['estimated_zip_bytes_without_path_dedup'] for r in rows) + 22
    reservations = [
        {'id': 'four_brief_cohorts', 'bytes_budget': 2000000, 'status': 'Pending Root/controls closure; include all four, including incomplete/adverse results; do not infer executed coverage'},
        {'id': 'remaining_reserve_and_optional_R03_WAIT', 'bytes_budget': 3000000, 'status': 'Reserve active; R03 WAIT preparation is not Native evidence. Replace partial prefix by complete component only after closure, retain partial provenance'},
        {'id': 'Word_scientific_report_selected_exact_code_Full_proof_and_index', 'bytes_budget': 2000000, 'status': 'Not created/approved here; no Full archive or engine; exact code revisions remain distinct unless byte-identical'}]
    total = closed_estimate + sum(x['bytes_budget'] for x in reservations)
    report = {'schema': 'APD04.analysis.components_and_deflate_estimate.N0.R01',
              'status': 'PROPOSAL_ONLY_NOT_ASSEMBLED_NOT_SEALED', 'new_native_ticks': 0,
              'created_zip_count': 0, 'groups': rows, 'excluded_operational_files': excluded,
              'closed_groups_expanded_bytes': sum(r['bytes'] for r in rows),
              'closed_groups_file_count': sum(r['file_count'] for r in rows),
              'estimated_zip_bytes_closed_without_dedup': closed_estimate,
              'future_budget_reservations_not_measured_evidence': reservations,
              'estimated_total_with_future_reservations': total,
              'strict_limit': 16000000, 'headroom_after_reserved_budgets': 16000000 - total,
              'limits': ['Deflate payloads measured in memory; ZIP headers conservatively estimated, no archive was created.',
                         'All current closed positives, negatives, instrument failures and exact revisions are proposed, not merely successful branches.',
                         'Future budgets are placeholders, not measured files or executed results.',
                         'Duplicate bytes are reported but not removed: do not break code/import or evidence member paths without verified materialization.',
                         'No motor, WHL, binary, full snapshot, historical ZIP, live journal or database included.']}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(report, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')
    print(json.dumps({k: report[k] for k in ('status', 'closed_groups_file_count', 'closed_groups_expanded_bytes',
          'estimated_zip_bytes_closed_without_dedup', 'estimated_total_with_future_reservations',
          'headroom_after_reserved_budgets', 'created_zip_count')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
