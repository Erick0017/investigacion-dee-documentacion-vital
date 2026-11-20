"""External local rule reconstruction from saved26contexts; no Native calls."""
from pathlib import Path
import hashlib, json

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'resultados/auditor/V3_MESSAGE_RECONSTRUCTION/MESSAGE_RECONSTRUCTION.json'
KERNEL = ROOT.parents[1] / 'referencias/fuentes/fuentes/producto4/source/src/kernel_v27.cpp'


def main():
    source = json.loads(SOURCE.read_text(encoding='utf-8')); kernel_hash = hashlib.sha256(KERNEL.read_bytes()).hexdigest()
    assert kernel_hash == 'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
    original = json.loads((ROOT / 'resultados/red/confirmacion03/FULL_U/MEASUREMENTS.json').read_text(encoding='utf-8'))
    input_ticks = {x['requested_tick'] for x in original['actual_protocol_receipts']}
    rows = []
    for item in source['encounters']:
        context = item['pre_context']; neighbors = context['moore26']; grad = [0, 0, 0]
        for key, record in neighbors.items():
            if record['state'] > 0:
                offset = [int(x) for x in key.split(',')]
                for i in range(3): grad[i] -= offset[i] * record['s_reg']
        grad_L1 = sum(abs(x) for x in grad); active = sum(r['active'] for r in neighbors.values())
        pairs = []
        for key, record in neighbors.items():
            off = tuple(int(x) for x in key.split(','))
            if next(x for x in off if x) < 0: continue
            opposite = neighbors[','.join(str(-x) for x in off)]
            pairs.append(record['active'] == opposite['active'])
        genesis_gradient = grad_L1 // 19665 >= int(9.887 ** 3)
        xnor = all(pairs) and active >= 8
        maximum = max(r['s_reg'] for r in neighbors.values())
        demux_excluded = maximum + 1 < 19665
        no_boundary_input = item['configuration']['pre'] not in input_ticks
        assert no_boundary_input
        # A post-step DEMUX increment can come only from an immediately
        # neighboring overflow center. Such a center can increment its own
        # pre-step load by at most1 before the overflow comparison; the saved
        # complete26 contains every possible source's actual pre-step load.
        branch = ('VOID_DIRECTIONAL_REDUCER_THEN_NO_INCOMING_DEMUX' if context['center']['state'] == 0
                  and not genesis_gradient and not xnor and demux_excluded
                  and no_boundary_input
                  and item['observed_post_matches_local_proposal_sum_and_direction'] else 'PARTIALLY_RECONSTRUCTED')
        rows.append({'id': item['configuration']['id'], 'pre_tick': item['configuration']['pre'],
            'post_tick': item['configuration']['post'], 'target': item['configuration']['site'],
            'pre_state': context['center']['state'], 'active_neighbors': active,
            'no_external_input_applies_at_transition_start': no_boundary_input,
            'gradient': grad, 'gradient_L1': grad_L1, 'gradient_div_P': grad_L1 // 19665,
            'crystallization_threshold': int(9.887 ** 3), 'crystallization_condition': genesis_gradient,
            'xnor13_all_symmetric': all(pairs), 'xnor_min_active': 8, 'xnor_condition': xnor,
            'directional_proposals': context['directional_proposals_without_activity_prefilter'],
            'maximum_possible_neighbor_ordinary_provisional_load': maximum + 1,
            'no_neighbor_can_overflow_to_target': demux_excluded,
            'resolved_branch': branch, 'post': item['post'],
            'counterfactual_necessity_tested_here': False})
    result = {'mode': 'READ_ONLY_RULE_RECONSTRUCTION_FROM_EXACT_SAVED_CONTEXTS',
        'source': SOURCE.relative_to(ROOT).as_posix(), 'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'kernel_source': KERNEL.relative_to(ROOT.parents[1]).as_posix(), 'kernel_sha256': kernel_hash,
        'events': rows, 'resolved_count': sum(x['resolved_branch'] == 'VOID_DIRECTIONAL_REDUCER_THEN_NO_INCOMING_DEMUX' for x in rows),
        'scope': 'Uses actual empty-center branch ordering, all26presences/absences and local load bounds. Reducer is not DEMUX. No native rule replaced, no response returned to any organization, no counterfactual necessity inferred.'}
    target = SOURCE.with_name('MESSAGE_BRANCH_RECONSTRUCTION.json')
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'resolved_events': result['resolved_count'], 'events': len(rows)}))


if __name__ == '__main__': main()
