"""Offline late-access contrasts; site absence is never a semantic answer."""
import json
from pathlib import Path
from common import ROOT, put, sha


def main():
    directory = ROOT / 'resultados/LATE_ACCESS_01'
    index = json.loads((directory / 'INDEX.json').read_text(encoding='utf-8'))
    data = [json.loads((ROOT / item['evidence']).read_text(encoding='utf-8')) for item in index]
    assert len(data) == 6
    rows = []
    for item in data:
        query_tick = item['query_tick']
        panel = item['rows']
        last = panel[-1]
        rows.append({'parent': item['parent'], 'arm': item['arm'], 'evidence': str((directory / (item['parent'] + '_' + item['arm']) / 'MEASUREMENTS.json').relative_to(ROOT)), 'query_tick': query_tick, 'receipt': item['query_receipt'], 'original_R1_delta_before': panel[0]['body_R1']['delta'], 'original_R1_delta_after': last['body_R1']['delta'], 'R2_right_delta_before': panel[0]['R2_right']['delta'], 'R2_left_delta_before': panel[0]['R2_left']['delta'], 'R2_right_delta_after': last['R2_right']['delta'], 'R2_left_delta_after': last['R2_left']['delta'], 'new_reader_active_ticks': [row['tick'] for row in panel if row['new_reader']['active']], 'input_site_panel': [row['new_reader'] for row in panel], 'payload17_in_recorded_neighborhood': [{'tick': row['tick'], 'records': [r for r in row['reader_neighborhood'] if r['active'] and r['s_reg'] == 17]} for row in panel]})
    ab110 = next(r for r in rows if r['parent'] == 'B01_AB_Qminus' and r['arm'] == 'probe110')
    ba110 = next(r for r in rows if r['parent'] == 'B03_BA_Qminus' and r['arm'] == 'probe110')
    ab_at111 = next(r for r in ab110['input_site_panel'] if r['tick'] == 111)
    ba_at111 = next(r for r in ba110['input_site_panel'] if r['tick'] == 111)
    ab_next = next(row['records'] for row in ab110['payload17_in_recorded_neighborhood'] if row['tick'] == 112)
    specific = [r for r in ab_next if r['site'] == [32, 24, 30] and r['direction'] == [-1, -1, -1]]
    assert specific, 'The AB pulse must not be described as destroyed merely because its input site becomes empty.'
    result = {'schema': 'CPC6.late_access.calculations.v1', 'source_sha256': sha(__file__), 'parent_initial_preparations_reused': 2, 'controlled_continuations': 6, 'native_probe_continuations': 4, 'no_query_shams': 2, 'new_initial_preparations': 0, 'all_probes_applied': all(item['query_receipt']['status'] == 'applied' for item in data if item['query_tick'] is not None), 'all_shams_input_site_empty': all(not any(row['new_reader']['active'] for row in item['rows']) for item in data if item['query_tick'] is None), 'interface_declaration_did_not_write_RAW_clocks': all(item['declaration_physical_identity_verified'] for item in data), 'comparison110': {'same_first_native_direction_at111': ab_at111['direction'] == ba_at111['direction'], 'common_first_direction': ab_at111['direction'], 'AB_input_site_active_ticks': ab110['new_reader_active_ticks'], 'BA_input_site_active_ticks': ba110['new_reader_active_ticks'], 'AB_next_local_record112': specific, 'meaning': 'Different subsequent trajectory/persistence profiles, not different first scalar answers and not a native absence predicate.'}, 'rows': rows, 'provisional_reading': ['A genuinely new fixed physical pulse can interact with the original learned local context after secondary native acquisition90 and query97; no prior body is recreated or re-taught.', 'Same-age parents retain the same new Q- content as delta+1 in different prepared receiver banks, while R1 histories and local contexts differ. The result identifies whole-history-dependent use, not unique causal attribution to one scalar or semantic predicate.', 'The common empty site was selected by a frozen geometric priority from three passive candidates, never by the later correct answer. Its inert declaration preserved full RAW/clocks.', 'Both probe timings110/111 are admitted. AB produces an outgoing17 record in the observed corner; BA additionally sustains records at the input site. No-query shams remain empty.', 'Absence at the original input site is not destruction of the signal, loss of all memory or learned NO. The AB111->112 segment is covered locally; later genealogy outside the Moore window remains unassigned.', 'This is the third/final access family. It establishes a bounded new late interaction after R2, not an unlimited reusable semantic reader or a general learned routing policy.'], 'evaluations_never_return_to_participant': True}
    put(ROOT / 'resultados/LATE_ACCESS_CALCULATIONS.json', result)
    print(json.dumps({'continuations': 6, 'all4probesApplied': result['all_probes_applied'], 'bothShamsEmpty': result['all_shams_input_site_empty'], 'AB_local_motion112': specific[0], 'R1_R2_delta_preserved': all(r['original_R1_delta_before'] == r['original_R1_delta_after'] and r['R2_right_delta_before'] == r['R2_right_delta_after'] and r['R2_left_delta_before'] == r['R2_left_delta_after'] for r in rows)}))


if __name__ == '__main__':
    main()
