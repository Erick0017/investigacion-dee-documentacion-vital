"""Read saved evidence and source only; no physical evolution or interventions."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.auditor.passive import digest, record


def load(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def put(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2), encoding='utf-8')


def interaction_review():
    import dee_thinking as d
    out = ROOT / 'resultados/auditor'; source = out / 'NATIVE_PREEMPTION_PILOT'
    summary = load(source / 'RUN_SUMMARY.json'); rows = []
    for history in ('AB', 'BA'):
        full = load(source / (history + '__UPSTREAM_E') / 'MEASUREMENTS.json')
        omitted = load(source / (history + '__OMITTED_E') / 'MEASUREMENTS.json')
        pre = next(x for x in full['trace'] if x['tick'] == 521)
        post = next(x for x in full['trace'] if x['tick'] == 522)
        rt = d.OrganizationalWorld.load_snapshot(str(source / (history + '__UPSTREAM_E') / 'T521.deetsnap'))
        before = digest(rt); g = d.inspect_write_gate(rt.runtime, d.Coordinate(15, 15, 14), False)
        target_gate = {k: getattr(g, k) for k in ('local_clock', 'center_available', 'n_active', 'hadron',
            'rule_value', 'survives_material_rule', 'semantic_protected', 'write_protected', 'k',
            'period', 'phase_remainder', 'ordinary_increment_condition', 'branch', 'demux_status')}
        assert digest(rt) == before
        context = pre['event_target_context']; grad = [0, 0, 0]
        for offset, r in context['moore26'].items():
            if r['state'] > 0:
                off = [int(x) for x in offset.split(',')]
                for i in range(3): grad[i] -= off[i] * r['s_reg']
        direction = [1 if x > 0 else -1 if x < 0 else 0 for x in grad]
        cmp_rows = []
        for a, b in zip(full['trace'], omitted['trace']):
            left = a['memories']['1']; right = b['memories']['1']
            cmp_rows.append({'tick': a['tick'], 'full_comparator': left['physical']['comparator'],
                'omitted_comparator': right['physical']['comparator'],
                'full_A_B': [left['physical'][k]['s_reg'] for k in ('A', 'B')],
                'omitted_A_B': [right['physical'][k]['s_reg'] for k in ('A', 'B')],
                'full_B_gate': left['gates']['B'], 'omitted_B_gate': right['gates']['B']})
        rows.append({'history1': history, 'receipt': full['upstream_receipt'],
            'target_before521': pre['event_target'], 'target_after522': post['event_target'],
            'incoming_before521': pre['candidate_ballistic_sample'], 'target_passive_gate521': target_gate,
            'gradient_from_all_existing_Moore26': grad, 'gradient_sign': direction,
            'actual_direction_equals_gradient_sign': post['event_target']['direction'] == direction,
            'context_differences_start': next((a['tick'] for a, b in zip(full['trace'], omitted['trace']) if a['context1'] != b['context1']), None),
            'observed_interpretation': ('Occupied normal target follows the material branch, preserving its own load7 while context changes direction. This is not a host rejection and not reducer load10.' if history == 'AB' else
                'Empty target receives the physically approaching load3. The observed segment continues beyond target and later changes local reader expression.'),
            'comparisons': cmp_rows,
            'coverage': 'Local transition and fields reconstructed. No unique ancestry beyond transformed segments or global minimal-cause claim.'})
    result = {'utc': datetime.now(timezone.utc).isoformat(), 'type': 'A_READ_ONLY_RECONSTRUCTION_OF_NEW_EXPERIMENT',
        'source': rel(source / 'RUN_SUMMARY.json'), 'source_sha256': sha(source / 'RUN_SUMMARY.json'),
        'fresh_preparations': 4, 'continuation_forks': 0, 'horizon': 525,
        'native_time': summary['elapsed_seconds'], 'manual_raw_clock_edits': 0,
        'initial_403_and_prefix517_checks': 'All explicit asserts completed; added interface is physically inert before the declared upstream input.',
        'rows': rows, 'scope': [
            'Both upstream experience receipts actually Applied at517, unlike the previous direct522 pilot with an AB rejected input.',
            'At equal upstream exposure, the two histories produce different local interaction and expression effects.',
            'All four A/B loads and deltas are unchanged517-525: AB101/100,+1; BA100/101,-1. No new relational write observed.',
            'This is experience-dependent accessibility/expression under fixed prepared support, not autonomous learned regulation or a learned policy.',
            'The histories also differ in their full local expression context; this does not isolate scalar delta as the only cause.',
            'The earlier direct+Y pulse and new diagonal native approach are separate declared protocols, not identical waveforms.'],
        'technical_attempts': [{'job': 'jobs/auditor_native_preemption01', 'error': 'Import namespace conflict before any preparation or freeze; no native trajectory'},
            {'job': 'jobs/auditor_native_preemption02', 'correction': 'Use actual copied inert interface construction and support constants instead of importing the old package namespace', 'exit_code': 0}],
        'sham_followup': 'Not added: native approach effects localized with equal prefix and field transitions; existing direct-pilot offpath sham remains distinct evidence, not a sham of this new waveform.'}
    put(out / 'NATIVE_PREEMPTION_RECONSTRUCTION.json', result)
    return result


def language_review():
    root = ROOT / 'resultados/lenguaje/continuous02'; config = load(root / 'EXPERIMENT_CONFIG.json')
    compact = []
    for case in config['cases']:
        p = root / case['id'] / 'MEASUREMENTS.json'
        if not p.exists():
            compact.append({'id': case['id'], 'status': 'NOT_YET_SAVED_AT_REVIEW'}); continue
        data = load(p); reads = []
        for x in data['readouts']:
            if 'readout' in x:
                r = x['readout']; reads.append({'tick': x['tick'], 'form': x['form'], 'sign': r['class_sign'],
                    'valid': r['valid'], 'load': r['physical']['s_reg'], 'direction': r['physical']['direction'],
                    'receipts': x['receipts']})
            else:
                reads.append({'tick': x['tick'], 'actual_sensor_profile': x['sensor']['profile'],
                    'global_forms': x['emitted_forms'], 'local_forms': x.get('locally_emitted_forms'),
                    'per_lane': {lane: {'valid': item['valid'], 'form': item['form'],
                        'load': item['physical']['s_reg'], 'direction': item['physical']['direction'],
                        'receipts': item['receipts']} for lane, item in x.get('local_region_decoder', {}).items()}})
        compact.append({'id': case['id'], 'new_preparation': data['new_preparation'],
            'profiles': [x['sensor']['profile'] for x in data['experiences']], 'readouts': reads,
            'source_hashes_match_frozen_config': all(config['sources'][n] == v for n, v in data['source_sha256'].items()),
            'manual_RAW_clock_edits': data['raw_clock_edits'], 'evidence': rel(p), 'sha256': sha(p)})
    review = {'utc': datetime.now(timezone.utc).isoformat(), 'mode': 'READ_ONLY_SOURCE_AND_SAVED_EVIDENCE_REVIEW_NO_NEW_NATIVE_JOB',
        'config': rel(root / 'EXPERIMENT_CONFIG.json'), 'config_sha256': sha(root / 'EXPERIMENT_CONFIG.json'),
        'source_hashes_current_match_config': {n: sha(ROOT / n) == v for n, v in config['sources'].items()},
        'implementation': {
            'attach': 'Associates inert protocol view and neutral progress metadata with the existing same Runtime at1431 (or431); no prepared learned body installed.',
            'sensor': 'profile() reads CURRENT F7/+supply-direction and R3/resource-direction packets at declared moving physical positions. It derives task-relative +/- only from those observations, not case.event, expected utility or filenames.',
            'experience': 'The selected external form is paired with actual sensed report; the report is identical at every one of four lexical regions. Form choice belongs to teaching protocol, not native selection.',
            'word_response': 'Fixed signal probe; current physical21 diagonal yields direction sign. Neither preset AB/BA nor a word-class lookup table produces the response.',
            'inverse_response': 'Same current sensory report and signal sent to all four regions. Decoder accepts only current physical26 vertical plus the TWO Applied receipts local to that region.',
            'persistent_state': 'Metadata retains forms, external protocol cursor, call receipts and timing, not learned class map or cached answer. Load restores native World then validates actual boundary and receipts.',
            'modalities': ['EXPERIENCE_PROTOCOL', 'EXTERNAL_FIXED_CURRENT_PACKET_TRANSDUCER', 'NATIVE_EVOLUTION', 'PHYSICAL_PROBE', 'PASSIVE_OBSERVATION']},
        'limits_and_contrasts': [
            'Eight arms restore copies of the same real1431 genealogy; only two reserved translated worlds are fresh complete0-1529 preparations. Not ten independent training genealogies.',
            'The report-omitted arm has rejected occupied query inputs. Its missing21 is not evidence from equal effective probe exposure; preserve actual5 and receipts.',
            'Unpaired+1 and signal-omitted controls have Applied queries but actual16 vertical, not valid21 diagonal. These provide cleaner local readout contrasts.',
            'The common-profile global decoder conservatively requires all regional receipts. A valid26 in one region may coexist with a rejected unrelated region. The local observer fixes only this attribution, not the world.',
            'Two finite new form associations to task-relative F/R profiles; not acquisition of the full semantics of universal good/bad, all65NSM primes, arbitrary grammar or unlimited renewal.',
            'The second opportunity is external fixed input, not caused by the agent or an autonomously selected teaching action. Learned responses themselves are native fields.',
            'Sources are reviewed, not an exhaustive malformed-snapshot security audit. Protocol requires valid finite cursor and native receipt continuity.'],
        'cases': compact, 'unexpected_hidden_oracle_found': False,
        'meaning_of_last_boolean': 'No response chooser or cached class table was found in the reviewed source paths; not a proof about all possible external applications.'}
    put(ROOT / 'resultados/auditor/LANGUAGE_CONTINUITY_REVIEW.json', review)
    return review


if __name__ == '__main__':
    a = interaction_review(); b = language_review()
    print(json.dumps({'interaction_histories': len(a['rows']), 'language_saved_cases': sum('evidence' in x for x in b['cases'])}))
