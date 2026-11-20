"""Recalculable offline retention/access summary; no native calls or classifications fed back."""
import json
from pathlib import Path
from common import ROOT, put, sha


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def row_for(case, tick):
    return next(row for row in case['rows'] if row['tick'] == tick)


def active_information(row, field, directions):
    return {key: value for key, value in row['adapter'][field].items() if value['active'] and value['semantic'] == 1 and tuple(value['direction']) in directions}


def main():
    root = ROOT / 'resultados'
    d1 = [load(path) for path in sorted((root / 'RETENTION_D01').glob('*/MEASUREMENTS.json'))]
    d2 = [load(path) for path in sorted((root / 'RETENTION_D02_ALTERNATE_ACCESS').glob('*/MEASUREMENTS.json'))]
    c1 = [load(path) for path in sorted((root / 'RETENTION_C01_CAUSAL').glob('*/MEASUREMENTS.json'))]
    c2 = [load(path) for path in sorted((root / 'RETENTION_C02_FIELD').glob('*/MEASUREMENTS.json'))]
    assert (len(d1), len(d2), len(c1), len(c2)) == (8, 6, 4, 4)
    original = []
    for case in d1:
        original.append({'case_id': case['case']['id'], 'history': case['case']['history'], 'adapter': case['case']['adapter'], 'request_tick': case['case']['read_tick'], 'receipt': case['retention_receipt'], 'delta_before': case['delta_before'], 'delta_after': case['delta_after'], 'readout': case['retention_decode'], 'input_site_before': case['before_old_query']['emission'], 'gates': case['before_old_query_gates'], 'evidence': str((root / 'RETENTION_D01' / case['case']['id'] / 'MEASUREMENTS.json').relative_to(ROOT))})
    alternate = []
    for case in d2:
        before = case['before_query']
        at23 = row_for(case, 23)
        at33 = row_for(case, 33)
        alternate.append({'case_id': case['case']['id'], 'history': case['case']['history'], 'request_tick': case['case']['read_tick'], 'payload': case['case']['payload'], 'receipt': case['query_receipt'], 'delta_before': before['body']['delta'], 'input_site_before': before['reader'], 'first_post_query_reader': case['post_query_panel'][1]['reader'], 'post_query_reader_panel': [{'tick_after_query': row['tick_after_query'], 'reader': row['reader']} for row in case['post_query_panel']], 'prior_new_information23': active_information(at23, 'information', ((-1, -1, 0), (1, -1, 0))), 'prior_late_information_query33': active_information(at33, 'late_queries', ((-1, 0, 1), (1, 0, 1))), 'evidence': str((root / 'RETENTION_D02_ALTERNATE_ACCESS' / case['case']['id'] / 'MEASUREMENTS.json').relative_to(ROOT))})
    scalar = []
    for base in ('D_Z_AB_69', 'D_Z_BA_69'):
        arms = {case['arm']: case for case in c1 if case['base'] == base}
        cut = arms['equalize_A_to_B']
        sham = arms['sham_identical_A']
        scalar.append({'base': base, 'delta_cut': cut['intervention']['after_A']['s_reg'] - cut['intervention']['unchanged_B']['s_reg'], 'reader_panel_equal_after_equalization': [r['reader'] for r in cut['post_query_panel']] == [r['reader'] for r in sham['post_query_panel']], 'MAIN_unchanged_both': cut['MAIN_unchanged'] and sham['MAIN_unchanged'], 'evidence': [str((root / 'RETENTION_C01_CAUSAL' / (base + '_' + arm) / 'MEASUREMENTS.json').relative_to(ROOT)) for arm in arms]})
    local = []
    for base in ('D_Z_AB_69', 'D_Z_BA_69'):
        arms = {case['arm']: case for case in c2 if case['base'] == base}
        cut = arms['local_semantic1_field_cut']
        sham = arms['local_identical_sham']
        local.append({'base': base, 'edited_sites': len(cut['interventions']), 'A_B_relation_preserved': cut['panel'][0]['body']['delta'], 'query_receipts': {'cut': cut['query_receipt'], 'sham': sham['query_receipt']}, 'active_reader_ticks_after_query': {'cut': sum(r['reader']['active'] for r in cut['panel'][1:]), 'sham': sum(r['reader']['active'] for r in sham['panel'][1:])}, 'MAIN_unchanged_both': cut['MAIN_unchanged'] and sham['MAIN_unchanged'], 'evidence': [str((root / 'RETENTION_C02_FIELD' / (base + '_' + arm) / 'MEASUREMENTS.json').relative_to(ROOT)) for arm in arms]})
    summary = {'schema': 'CPC6.retention.access_summary.v1', 'preparations': 14, 'diagnostic_forks': 8, 'cases': 22, 'worlds_are_not_independent_replicates_of_one_sample': True, 'method_families': ['Original declared reader, three fixed request cadences with matched body-only/integrated worlds.', 'Alternate local physical reader declared inertly beforeT0; same uninterrupted integrated history.'], 'original_reader': {'attempts': len(original), 'rejected_occupied': sum(row['receipt']['status'] == 'rejected_occupied' for row in original), 'rows': original}, 'alternate_reader': {'cases': len(alternate), 'applied_queries': sum(row['receipt']['status'] == 'applied' for row in alternate), 'rejected_occupied': sum(row['receipt']['status'] == 'rejected_occupied' for row in alternate), 'no_pulse_shams': sum(row['receipt']['status'] == 'NOT_REQUESTED_SHAM' for row in alternate), 'rows': alternate}, 'scalar_relation_equalization': scalar, 'local_expression_field_cut': local, 'data_layer': 'Every RAW/clock field is a decimal string in the underlying measurements; complete snapshots and native field observations remain available.', 'calculation_layer': 'Counts use one row per preparation/fork, not ticks. Active window counts exclude pre-query tick. Equality compares exact recorded direction/load/RAW/clock; no derived labels are fed to MAIN.', 'provisional_reading': ['An applied fresh physical pulse can re-express a distinction between AB and BA histories in the same integrated world after source acquisition, selection and late data reading.', 'Original-port failures are admission failures; the measured relative distinction persists, but that fact alone does not demonstrate usable access.', 'The fresh z-reader needs the surviving local semantic1 expression context. Equalizing A/B charge alone does not remove its history-dependent answer; the A/B scalar relation is not a sufficient causal description of retained function.', 'The t136/payload13 reserve preserves different full vectors, but BA gives dy0 rather than dy+1. A scalar dy-sign language learned from69 does not automatically generalize to136.', 'The H0 control has a different occupied reader context and rejects the pulse. It is not a matched applied-probe negative nor a numeric zero answer.', 'Deleting local expression fields is diagnostic intervention only. Its extinction of the reader also alters access, so it does not uniquely localize semantic memory. MAIN has no deletion/reset/restore.'], 'open_local_objectives': ['A fixed decoder validated across additional phases without tuning from these same reserved observations.', 'A matched virgin-reader control with the same admitted access geometry but no R1 learning.', 'Native renewed access that survives both context-field perturbation and subsequent R2 queries.', 'Selective attribution among distributed memory, continuing expression context and the A/B scalar relation.'], 'source_hashes': {name: sha(ROOT / 'src' / name) for name in ('retention_probe.py', 'retention_access.py', 'retention_causal.py', 'retention_field.py', 'retention_analysis.py')}}
    put(root / 'RETENTION_SYNTHESIS.json', summary)
    print(json.dumps({'preparations': 14, 'diagnostic_forks': 8, 'cases': 22, 'original_reader_rejected': 8, 'alternate_applied': summary['alternate_reader']['applied_queries'], 'scalar_equalization_did_not_change_readers': all(row['reader_panel_equal_after_equalization'] for row in scalar), 'local_field_cut_extinguishes_after_applied_probe': all(row['active_reader_ticks_after_query'] == {'cut': 0, 'sham': 4} for row in local)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
