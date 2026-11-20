"""Four fresh I02 continuities; an upstream event approaches a native context.

The inert upstream interface exists before T0. No RAW/clock/occupied-site edits
or learned-state transplantation occur. The event has one fixed trajectory,
not an error/answer selected by the host. This is EXPERIENCE_PROTOCOL, not an
autonomous learned policy. All fields and contexts remain integer-valued.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, sys, time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'src'))
from src.auditor.passive import digest, record, receipt, neighborhood
from src.auditor.susceptibility_pilot import gate
# Exact published I02 support patterns, also present in dual_sustained.py's
# sustained_regulation import. No old campaign is run to recover constants.
PA = ((-1, 0, 0), (-1, 1, 1), (0, 0, 1), (0, 1, 0))
PB = ((0, -1, 0), (0, 0, -1), (1, -1, -1), (1, 0, 0))


def interface(name, site, direction, state=1, semantic=1):
    # Same inert ChannelSpec construction as parent src/common.py:63-76.
    import dee_thinking as d
    channel = d.ChannelSpec(); channel.name = name; channel.injection_site = d.Coordinate(*site)
    channel.direction = d.Direction(*direction); channel.state = state; channel.semantic = semantic
    channel.allow_experience = True; channel.allow_probe = True
    item = d.InterfaceSpec(); item.name = name; item.channel = channel
    return item


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def prepare():
    """Exact dual_sustained body, with one additional inert declared interface."""
    import dee_thinking as d
    n = 47; placements = []; interfaces = []; spec = {}; occupied = set()

    def moved(q, v): return tuple((q[i] + v[i]) % n for i in range(3))

    def place(q, state, load, dr=(0, 0, 0), sem=4, clock=0, role='support'):
        if q in occupied: raise ValueError('Initial overlap')
        occupied.add(q); p = d.InitialPlacement(); p.site = d.Coordinate(*q)
        p.raw = d.pack_record(state, load, *dr, sem); p.clock = clock; p.role = role
        placements.append(p)

    for j, c in enumerate(((14, 14, 14), (32, 32, 32)), 1):
        a, b = moved(c, (-1, 0, 0)), moved(c, (1, 0, 0)); phase = 260 if j == 1 else 0
        place(a, 1000, 100, sem=1, clock=phase, role=f'memory{j}.A')
        place(b, 2000, 100, sem=1, clock=phase, role=f'memory{j}.B')
        for q, pat, state, clock in ((a, PA, 3000, 31), (b, PB, 4000, 41)):
            for i, v in enumerate(pat): place(moved(q, v), state + i, 0, clock=clock + i)
        if j == 1: place(moved(c, (0, -2, 0)), 6000, 7, (0, 1, 0), 4, 23, 'reader1')
        for name, q, offset, dr, state in (
                ('A', a, (0, -1, 0), (0, -1, 0), 5000),
                ('B', b, (0, 1, 0), (0, 1, 0), 5001)):
            interfaces.append(interface(f'm{j}.{name}', moved(q, offset), dr, state=state))
        interfaces.append(interface(f'm{j}.read', moved(c, (0, -1, 0)), (0, 1, 0)))
        spec[str(j)] = {'A': a, 'B': b, 'comparator': c,
                        'reader': moved(c, (0, -1, 0)), 'source': moved(c, (0, -2, 0))}
    interfaces.append(interface('upstream.B', (20, 15, 9), (-1, 0, 1), state=5001))
    recipe = d.OrganizationRecipe.research(n, placements, 0); recipe.interfaces = interfaces
    recipe.execution = d.TickOptions(d.Backend.LAZY, 1)
    return d.OrganizationalWorld.create(recipe), spec


def sample(w, spec):
    import dee_thinking as d
    memories = {}
    for name, ports in spec.items():
        current = {k: record(w.runtime.observe(d.Coordinate(*q))) for k, q in ports.items()}
        a, b = current['A'], current['B']
        memories[name] = {'delta': a['s_reg'] - b['s_reg'] if a['active'] and b['active'] else None,
                          'physical': current,
                          'gates': {k: gate(w, ports[k]) for k in ('A', 'B')}}
    t = w.runtime.current_tick
    expected = tuple((20 - max(0, t - 517), 15, 9 + max(0, t - 517)))
    expected = tuple(x % 47 for x in expected)
    observed = record(w.runtime.observe(d.Coordinate(*expected)))
    return {'tick': t, 'memories': memories, 'candidate_ballistic_site': list(expected),
            'candidate_ballistic_sample': observed,
            'event_target': record(w.runtime.observe(d.Coordinate(15, 15, 14))),
            'context1': {k: neighborhood(w, spec['1'][k]) for k in ('A', 'B')},
            'event_target_context': neighborhood(w, (15, 15, 14)),
            'tracking_scope': 'Predicted segment plus actual local records; a transformed/missing segment is not assigned unique descendants by load.'}


def main():
    import dee_thinking as d
    out = ROOT / 'resultados/auditor/NATIVE_PREEMPTION_PILOT'; out.mkdir(parents=True, exist_ok=False)
    config = {'id': 'CPC4_A02.I02_NATIVE_APPROACH.v1',
        'freeze_utc': datetime.now(timezone.utc).isoformat(), 'fresh_preparations': 4,
        'histories1': ['AB', 'BA'], 'history2': 'AB', 'arms': ['UPSTREAM_E', 'OMITTED_E'],
        'dimension': 47, 'centers': [[14, 14, 14], [32, 32, 32]], 'backend': 'Lazy', 'threads': 1,
        'upstream_interface_prepared_before_T0': {'name': 'upstream.B', 'site': [20, 15, 9],
            'state': 5001, 'semantic': 1, 'direction': [-1, 0, 1], 'load': 3, 'requested_tick': 517},
        'candidate_target': {'site': [15, 15, 14], 'arrival_tick_if_untransformed': 522,
                             'penultimate_site': [16, 15, 13], 'penultimate_tick': 521},
        'history_inputs': {'m1': [0, 1], 'm2': [260, 261]}, 'probes2': [262, 400],
        'horizon': 525, 'local_trace': list(range(517, 526)),
        'manual_RAW_or_clock_edits': 0, 'mode': 'EXPERIENCE_PROTOCOL_FRESH_THEN_NATIVE_EVOLUTION',
        'source_constructor': {'path': 'src/dual_sustained.py', 'sha256': sha(ROOT / 'src/dual_sustained.py')},
        'runner_sha256': sha(__file__),
        'freeze_prediction': 'Four initial RAW/clock states equal their original I02 bodies. E and omission match physically until the upstream event is applied. The event may encounter a pre-existing path/context; no guaranteed arrival or rewrite is assumed.',
        'decision_rule': 'Record real admission and all local fields. Stop after four arms even if blocked; no alternative-route search.',
        'scope': 'Separates host API admission at the distant site from subsequent native approach. The diagonal waveform differs from the earlier direct +Y injection pilot; not a replication of that waveform or autonomous susceptibility learning.'}
    put(out / 'EXPERIMENT_CONFIG.json', config); started = time.monotonic(); results = []
    for history in config['histories1']:
        prefix = None
        old_folder = ROOT / 'resultados/regulacion/DUAL_CONFIRMATION' / (history + '_AB')
        baseline0 = digest(d.OrganizationalWorld.load_snapshot(str(old_folder / 'T0.deetsnap')))
        baseline403 = digest(d.OrganizationalWorld.load_snapshot(str(old_folder / 'T403.deetsnap')))
        for arm in config['arms']:
            folder = out / (history + '__' + arm); folder.mkdir(); w, spec = prepare(); calls = []; ids = []
            initial = digest(w); assert initial == baseline0
            w.save_snapshot(str(folder / 'T0.deetsnap'))
            for j, h, start in ((1, history, 0), (2, 'AB', 260)):
                for i, label in enumerate(h):
                    r = w.submit(f'm{j}.{label}', 3, start + i); ids.append(r.id)
                    calls.append({'op': 'submit', 'channel': f'm{j}.{label}', 'load': 3, 'tick': start + i, 'id': r.id})
            for tick in (262, 400):
                r = w.probe('m2.read', 7, tick); ids.append(r.id)
                calls.append({'op': 'probe', 'channel': 'm2.read', 'load': 7, 'tick': tick, 'id': r.id})
            event = None
            if arm == 'UPSTREAM_E':
                event = w.submit('upstream.B', 3, 517); ids.append(event.id)
                calls.append({'op': 'submit', 'channel': 'upstream.B', 'load': 3, 'tick': 517, 'id': event.id})
            w.run_until(403); at403 = digest(w); assert at403 == baseline403
            w.run_until(517); at517 = digest(w)
            if prefix is None: prefix = at517
            else: assert at517 == prefix
            rows = []
            for tick in range(517, 526):
                rows.append(sample(w, spec))
                if tick in (517, 521, 522, 523, 525): w.save_snapshot(str(folder / f'T{tick}.deetsnap'))
                if tick < 525: w.advance()
            result = {'id': folder.name, 'history1': history, 'history2': 'AB', 'arm': arm,
                'mode': config['mode'], 'spec': spec, 'initial_matches_original_body': True,
                'T403_matches_original_body': True, 'matched_E_omission_prefix517': True,
                'initial_digest': initial, 'digest403': at403, 'digest517': at517,
                'final_digest': digest(w), 'calls': calls, 'trace': rows,
                'receipts': [receipt(w.runtime.receipt(i)) for i in ids],
                'upstream_receipt': None if event is None else receipt(w.runtime.receipt(event.id)),
                'external_operations': list(w.external_operations), 'manual_RAW_or_clock_edits': 0,
                'source_code_sha256': sha(__file__)}
            put(folder / 'MEASUREMENTS.json', result); results.append(result)
    contrasts = []
    for history in config['histories1']:
        full, omitted = [next(x for x in results if x['history1'] == history and x['arm'] == arm) for arm in config['arms']]
        def relation(r): return [(x['tick'], [x['memories']['1']['physical'][k]['s_reg'] for k in ('A', 'B')], x['memories']['1']['delta']) for x in r['trace']]
        def expression(r): return [(x['tick'], x['memories']['1']['physical']['comparator']['raw']) for x in r['trace']]
        contexts = []
        for a, b in zip(full['trace'], omitted['trace']):
            if a['context1'] != b['context1']: contexts.append(a['tick'])
        contrasts.append({'history1': history, 'upstream_receipt': full['upstream_receipt'],
            'same_effective_upstream_exposure': None,
            'relation_differs': relation(full) != relation(omitted),
            'expression_differs': expression(full) != expression(omitted),
            'context_difference_ticks': contexts, 'full_relation': relation(full), 'omitted_relation': relation(omitted),
            'candidate_segment': [{'tick': x['tick'], 'site': x['candidate_ballistic_site'], 'observed': x['candidate_ballistic_sample']} for x in full['trace']]})
    statuses = [str(x['upstream_receipt']['status']) for x in results if x['upstream_receipt'] is not None]
    same_exposure = all(x == 'applied' for x in statuses)
    for x in contrasts: x['same_effective_upstream_exposure'] = same_exposure
    summary = {'config_sha256': sha(out / 'EXPERIMENT_CONFIG.json'), 'fresh_preparations': 4,
        'forks': 0, 'horizon_each': 525, 'diagnostic_RAW_clock_edits': 0,
        'contrasts': contrasts, 'all_upstream_inputs_applied': same_exposure,
        'elapsed_seconds': time.monotonic() - started, 'source_code_sha256': sha(__file__),
        'scope': config['scope'], 'closed_reason': 'Four frozen fresh preparations completed; no parameter search.'}
    put(out / 'RUN_SUMMARY.json', summary)
    print(json.dumps({'fresh': 4, 'upstream_receipts': statuses, 'contrasts': [{k: x[k] for k in ('history1', 'relation_differs', 'expression_differs', 'context_difference_ticks')} for x in contrasts]}))


if __name__ == '__main__': main()
