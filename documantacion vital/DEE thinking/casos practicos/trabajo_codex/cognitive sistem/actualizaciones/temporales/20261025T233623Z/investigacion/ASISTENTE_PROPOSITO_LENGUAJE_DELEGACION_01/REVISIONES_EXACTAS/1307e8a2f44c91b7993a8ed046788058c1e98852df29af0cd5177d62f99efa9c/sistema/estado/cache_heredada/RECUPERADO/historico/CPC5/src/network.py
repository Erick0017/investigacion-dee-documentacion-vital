"""CPC5 finite native communication graphs, not a second DEE implementation.

Every learned moving relation is produced by two admitted experiences.  A
connected graph carries the real output into the next encounter in ONE Runtime.
The auditor's arithmetic is evaluated only after trajectories, never injected.
"""
from __future__ import annotations

import argparse
from array import array
import hashlib
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
KEY = 'cpc5.native_graph.v1'


def put(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(path.name + '.pending.' + str(os.getpid()))
    pending.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(pending, path)


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            value.update(block)
    return value.hexdigest()


def moved(site, direction, count, n):
    return tuple((int(site[i]) + int(direction[i]) * count) % n for i in range(3))


def observe(world, site):
    import dee_thinking as d
    value = world.runtime.observe(d.Coordinate(*site))
    rec = value.record
    return {'tick': value.tick, 'site': list(site), 'RAW_hex': format(value.raw, '016x'),
            'clock_u64': str(value.clock), 'state': rec.state, 'semantic': rec.semantic,
            's_reg': rec.s_reg, 'direction': [rec.dx, rec.dy, rec.dz],
            'active': rec.state > 0 and rec.semantic != 5}


def physical(world):
    return {'tick': world.runtime.current_tick,
            'RAW_sha256': hashlib.sha256(array('Q', world.runtime.raw_copy()).tobytes()).hexdigest(),
            'clock_sha256': hashlib.sha256(array('Q', world.runtime.clock_copy()).tobytes()).hexdigest()}


def receipt(world, id):
    item = world.runtime.receipt(id)
    if item is None:
        return {'id': id, 'status': 'MISSING'}
    return {'id': item.id, 'requested_tick': item.requested_tick,
            'effective_tick': item.effective_tick, 'status': str(item.status),
            'kind': str(item.kind), 'channels': list(item.channels), 'reason': item.reason}


def interface(name, site, direction):
    import dee_thinking as d
    channel = d.ChannelSpec()
    channel.name = name
    channel.injection_site = d.Coordinate(*site)
    channel.direction = d.Direction(*direction)
    channel.state = 1
    channel.semantic = 1
    channel.allow_experience = True
    channel.allow_probe = True
    item = d.InterfaceSpec()
    item.name = name
    item.channel = channel
    return item


def geometry(case):
    """Each group is physically independent; its members are natively serial.

    Grouping does not magically integrate a population.  An independent group
    needs its own physical query, and that extra resource is explicitly counted.
    """
    n = case.get('N', 67)
    chains = list(case['chains'])
    if type(n) is not int or not 59 <= n <= 127:
        raise ValueError('Research graph N within 59..127 required')
    if not chains or len(chains) > 10 or any(type(x) is not int or not 1 <= x <= 8 for x in chains):
        raise ValueError('One to ten groups, each one to eight native stages')
    if sum(chains) > 10:
        raise ValueError('This finite research cut has at most ten components')
    translation = tuple(case.get('translation', (0, 0, 0)))
    if len(translation) != 3 or any(type(x) is not int for x in translation):
        raise ValueError('Three integer translation coordinates required')
    start = int(case.get('query_meeting', 11))
    if not 11 <= start <= 31:
        raise ValueError('Finite first read boundary 11..31')
    stages = []
    index = 0
    for group, depth in enumerate(chains):
        hub0 = moved((50, 15, 8 + group * 5), translation, 1, n)
        for local in range(depth):
            hub = moved(hub0, (-1, 0, 0), local * 5, n)
            meeting_tick = start + local * 5
            meet = moved(hub, (0, 1, 0), meeting_tick - 3, n)
            stages.append({'index': index, 'group': group, 'local': local,
                           'hub': list(hub), 'first_meeting': list(meet),
                           'meeting_tick': meeting_tick, 'outgoing': [-1, 1, 0],
                           'memory_direction': [0, 1, 0]})
            index += 1
    top_entities = []
    if case.get('compound_partition'):
        sizes = list(case['compound_partition'])
        if any(type(x) is not int or x < 1 for x in sizes) or sum(sizes) != len(stages):
            raise ValueError('Declared compound partition must cover all components')
        offset = 0
        for group, size in enumerate(sizes):
            top_entities.append({'id': 'U' + str(group + 1), 'components': list(range(offset, offset + size))})
            offset += size
    else:
        for group in range(len(chains)):
            top_entities.append({'id': 'G' + str(group), 'components': [s['index'] for s in stages if s['group'] == group]})
    links = [{'emitter_component': a['index'], 'receiver_component': b['index'],
              'emission_tick': a['meeting_tick'], 'reception_tick': b['meeting_tick'],
              'direction': [-1, 1, 0], 'covered_by': 'exact pre/post encounter neighborhoods; intermediate free-flight prediction'}
             for a, b in zip(stages, stages[1:]) if a['group'] == b['group']]
    return {'version': 1, 'recipe': 'cpc5.mobile_native_graph.v1', 'N': n,
            'chains': chains, 'stages': stages, 'translation': list(translation),
            'top_entities': top_entities, 'native_links': links,
            'training_collision_tick': 3, 'query_meeting': start,
            'scope': 'Finite moving learned relations and physical routes; labels do not create integration'}


def protocol(case, spec):
    count = len(spec['stages'])
    loads = case.get('loads', [[3, 9 + 2 * j] for j in range(count)])
    if len(loads) != count or any(len(v) != 2 or any(type(x) is not int or not 0 <= x <= 65535 for x in v) for v in loads):
        raise ValueError('One representable cue/report pair per component required')
    query = case.get('query', 13)
    if type(query) is not int or not 0 <= query <= 65535:
        raise ValueError('Representable query load required')
    omit = set(case.get('omit_training', []))
    unpaired = set(case.get('unpaired_training', []))
    if any(type(x) is not int or x not in range(count) for x in omit | unpaired):
        raise ValueError('Training controls must name actual components')
    entries = []
    for stage, pair in zip(spec['stages'], loads):
        i = stage['index']
        if i not in omit:
            entries.append({'channel': f'stage{i}.cue', 'tick': int(i in unpaired), 'load': pair[0],
                            'role': 'actual_external_cue_experience'})
            entries.append({'channel': f'stage{i}.report', 'tick': 0, 'load': pair[1],
                            'role': 'actual_external_report_experience'})
    for group in range(len(spec['chains'])):
        if group not in case.get('omit_query_groups', []):
            entries.append({'channel': f'group{group}.query', 'tick': spec['query_meeting'] - 5,
                            'load': query, 'role': 'common_physical_query'})
    return entries


def interfaces_for(spec):
    ports = []
    n = spec['N']
    for stage in spec['stages']:
        i, hub = stage['index'], stage['hub']
        for label, direction in (('cue', (-1, 0, 0)), ('report', (1, 1, 0))):
            ports.append(interface(f'stage{i}.{label}', moved(hub, direction, -3, n), direction))
        if stage['local'] == 0:
            ports.append(interface(f'group{stage["group"]}.query',
                                   moved(stage['first_meeting'], (-1, 0, 0), -5, n), (-1, 0, 0)))
    return ports


class NetworkWorld:
    def __init__(self, world, spec, state):
        self.world, self.spec, self.state = world, spec, state

    @classmethod
    def create(cls, case):
        import dee_thinking as d
        spec = geometry(case)
        rec = d.OrganizationRecipe.research(spec['N'], [], 0)
        rec.interfaces = interfaces_for(spec)
        rec.execution = d.TickOptions(d.Backend.LAZY, 1)
        world = d.OrganizationalWorld.create(rec)
        calls = []
        for item in protocol(case, spec):
            result = world.submit(item['channel'], item['load'], item['tick'])
            calls.append({**item, 'receipt_id': result.id, 'call_tick': 0,
                          'modality': 'EXPERIENCE_PROTOCOL'})
        state = {'version': 1, 'geometry': spec, 'tick': 0, 'inputs': calls,
                 'scope': 'Only physical recipe, declared external inputs and native receipt IDs; no expected answer'}
        session = cls(world, spec, state)
        session.commit()
        return session

    def commit(self):
        self.state['tick'] = self.world.runtime.current_tick
        self.world.runtime.set_snapshot_metadata(KEY, json.dumps(self.state, separators=(',', ':')))

    def run_until(self, tick):
        if type(tick) is not int or tick < self.world.runtime.current_tick or tick > 512:
            raise ValueError('Monotone finite absolute tick in 0..512 required')
        self.world.run_until(tick)
        if self.world.runtime.current_tick != tick:
            raise RuntimeError('Native execution did not reach the requested boundary')
        self.commit()

    def save(self, path):
        path = Path(path)
        if path.exists():
            raise FileExistsError(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.commit()
        self.world.save_snapshot(str(path))
        return {'path': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else path.name,
                'sha256': sha(path), 'physical': physical(self.world)}

    @classmethod
    def load(cls, path):
        import dee_thinking as d
        world = d.OrganizationalWorld.load_snapshot(str(path))
        text = world.runtime.snapshot_metadata(KEY)
        if not text or len(text) > 524288:
            raise ValueError('No finite CPC5 graph metadata')
        state = json.loads(text)
        if state.get('version') != 1 or state.get('tick') != world.runtime.current_tick:
            raise ValueError('Snapshot recipe/tick mismatch')
        spec = state['geometry']
        if world.runtime.dimension != spec['N'] or world.recipe.placements:
            raise ValueError('Changed dimension or unexpected prepared material')
        actual = {p.name: p.channel for p in world.interfaces}
        expected = interfaces_for(spec)
        if set(actual) != {p.name for p in expected}:
            raise ValueError('Changed graph interfaces')
        for item in expected:
            a, b = actual[item.name], item.channel
            point = lambda p: (p.x, p.y, p.z)
            direction = lambda p: (p.dx, p.dy, p.dz)
            if (point(a.injection_site), direction(a.direction), a.state, a.semantic) != (point(b.injection_site), direction(b.direction), b.state, b.semantic):
                raise ValueError('Changed physical port')
        for item in state['inputs']:
            rec = world.runtime.receipt(item['receipt_id'])
            if rec is None or rec.requested_tick != item['tick'] or list(rec.channels) != [item['channel']]:
                raise ValueError('Lost pending or applied operative receipt')
        return cls(world, spec, state)


def create(case):
    return NetworkWorld.create(case)


def neighborhood(world, site):
    n = world.runtime.dimension
    return [{'offset': [x, y, z], **observe(world, moved(site, (x, y, z), 1, n))}
            for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)]


def run_case(case, out):
    """Execute once with incremental evidence.  No world observation chooses an input."""
    import dee_thinking as d
    out = Path(out)
    if out.exists():
        raise FileExistsError('Completed or partial case protected: ' + str(out))
    out.mkdir(parents=True)
    started = time.monotonic()
    session = create(case)
    spec = session.spec
    identity = {'version': d.__version__, 'module': d.__file__, 'native_sha256': sha(d._native.__file__),
                'kernel': d.kernel_identity(), 'python': sys.executable}
    checkpoints = [session.save(out / 'T0.deetsnap')]
    trace, encounters, edits = [], [], []
    terminal = max(s['meeting_tick'] for s in spec['stages']) + 5
    boundaries = {0, 2, 3, terminal}
    for stage in spec['stages']:
        boundaries.update((stage['meeting_tick'] - 1, stage['meeting_tick']))
    if case.get('late_cut_stage') is not None:
        cut = case['late_cut_stage']
        if type(cut) is not int or cut not in range(len(spec['stages'])):
            raise ValueError('Cut names an actual stage')
        cut_stage = spec['stages'][cut]
        cut_tick = cut_stage['meeting_tick'] - 2
        boundaries.add(cut_tick)
    else:
        cut_tick = None
    edge_tick = None
    if case.get('edge_intervention'):
        item = case['edge_intervention']
        edge = item.get('after_stage')
        if type(edge) is not int or edge not in range(len(spec['stages']) - 1):
            raise ValueError('Native edge intervention requires a real preceding stage')
        stage = spec['stages'][edge]
        if spec['stages'][edge + 1]['group'] != stage['group']:
            raise ValueError('No native edge joins those independent groups')
        if item.get('kind') not in ('remove', 'direction', 'sham'):
            raise ValueError('Edge edit kind must be remove, direction or sham')
        edge_tick = stage['meeting_tick'] + 2
        boundaries.add(edge_tick)
    for tick in sorted(boundaries):
        session.run_until(tick)
        row = {'tick': tick, 'learned_segments': {}}
        for stage in spec['stages']:
            target = moved(stage['hub'], (0, 1, 0), max(0, tick - 3), spec['N'])
            row['learned_segments'][str(stage['index'])] = observe(session.world, target)
        trace.append(row)
        if tick == cut_tick:
            stage = spec['stages'][case['late_cut_stage']]
            site = moved(stage['hub'], (0, 1, 0), tick - 3, spec['N'])
            before = observe(session.world, site)
            edit = d.ResearchStateEdit()
            edit.coordinate = d.Coordinate(*site)
            edit.raw = 0
            edit.label = 'CPC5 selective learned moving relation removal after training'
            raw_before, clocks_before = session.world.runtime.raw_copy(), session.world.runtime.clock_copy()
            parent_hash = physical(session.world)
            child = session.world.diagnostic_fork([edit], True)
            changed = [i for i, (a, b) in enumerate(zip(raw_before, child.runtime.raw_copy())) if a != b]
            if len(changed) != int(before['RAW_hex'] != '0000000000000000') or child.runtime.clock_copy() != clocks_before:
                raise AssertionError('Diagnostic changes outside declared RAW site')
            if physical(session.world) != parent_hash:
                raise AssertionError('Parent mutated by diagnostic fork')
            session.world = child
            session.commit()
            edits.append({'tick': tick, 'site': list(site), 'before': before, 'after': observe(child, site),
                          'RAW_sites_changed': len(changed), 'clock_sites_changed': 0,
                          'parent_unchanged': True, 'modality': 'DIAGNOSTIC_FORK'})
        if tick == edge_tick:
            item = case['edge_intervention']
            stage = spec['stages'][item['after_stage']]
            site = moved(stage['first_meeting'], (-1, 1, 0), 2, spec['N'])
            before = observe(session.world, site)
            if not before['active'] or before['direction'] != [-1, 1, 0]:
                raise RuntimeError('The proposed edge carrier is absent; cannot perform declared intervention')
            if item['kind'] == 'remove':
                new_raw = 0
            elif item['kind'] == 'direction':
                new_raw = d.pack_record(before['state'], before['s_reg'], 1, 1, 0, before['semantic'])
            else:
                new_raw = int(before['RAW_hex'], 16)
            edit = d.ResearchStateEdit()
            edit.coordinate = d.Coordinate(*site)
            edit.raw = new_raw
            edit.label = 'CPC5 actual emitted inter-compound carrier ' + item['kind']
            raw_before, clocks_before = session.world.runtime.raw_copy(), session.world.runtime.clock_copy()
            parent_hash = physical(session.world)
            child = session.world.diagnostic_fork([edit], True)
            changed = [i for i, (a, b) in enumerate(zip(raw_before, child.runtime.raw_copy())) if a != b]
            if len(changed) != int(new_raw != int(before['RAW_hex'], 16)) or child.runtime.clock_copy() != clocks_before:
                raise AssertionError('Edge diagnostic changed undeclared fields')
            if physical(session.world) != parent_hash:
                raise AssertionError('Edge diagnostic changed parent')
            session.world = child
            session.commit()
            edits.append({'tick': tick, 'site': list(site), 'before': before, 'after': observe(child, site),
                          'RAW_sites_changed': len(changed), 'clock_sites_changed': 0,
                          'parent_unchanged': True, 'kind': item['kind'],
                          'field_change': 'direction only' if item['kind'] == 'direction' else ('none' if item['kind'] == 'sham' else 'RAW removal'),
                          'modality': 'DIAGNOSTIC_FORK'})
        for stage in spec['stages']:
            if tick in (stage['meeting_tick'] - 1, stage['meeting_tick']):
                target = stage['first_meeting']
                encounters.append({'stage': stage['index'], 'group': stage['group'], 'tick': tick,
                                   'phase': 'pre' if tick == stage['meeting_tick'] - 1 else 'post',
                                   'target': list(target), 'center': observe(session.world, target),
                                   'Moore26_plus_center': neighborhood(session.world, target),
                                   'coverage': 'Declared encounter window, not unique ancestry inferred from proximity'})
        if tick in (3, min(s['meeting_tick'] for s in spec['stages']) - 1, terminal):
            checkpoints.append(session.save(out / f'T{tick}.deetsnap'))
        put(out / 'PROGRESS.json', {'case_id': case['id'], 'tick': tick, 'trace': trace,
                                    'encounter_windows': encounters, 'diagnostic_edits': edits})
    # This is an auditor after the world has run, not a participant or policy.
    readouts = [entry for entry in encounters if entry['phase'] == 'post']
    calculations = []
    loads = case.get('loads', [[3, 9 + 2 * j] for j in range(len(spec['stages']))])
    by_stage = {entry['stage']: entry for entry in readouts}
    for stage in spec['stages']:
        measurement = by_stage[stage['index']]
        prior_stages = [s for s in spec['stages'] if s['group'] == stage['group'] and s['local'] <= stage['local']]
        expected = case.get('query', 13) + sum(sum(loads[s['index']]) for s in prior_stages)
        actual = measurement['center']
        calculations.append({'stage': stage['index'], 'group': stage['group'],
                             'formula': 'query + sum(cue+report for prior trained stages in this physical route)',
                             'ideal_additive_reference': expected, 'observed_load': actual['s_reg'] if actual['active'] else None,
                             'observed_direction': actual['direction'], 'observed_active': actual['active'],
                             'equals_full_training_reference': actual['active'] and actual['s_reg'] == expected,
                             'scope': 'Evaluation only; omitted/unpaired/cut cases deliberately need not match full-history reference'})
    receipts = [receipt(session.world, item['receipt_id']) for item in session.state['inputs']]
    unique_query_calls = [item for item in session.state['inputs'] if item['role'] == 'common_physical_query']
    resource = {'dimension': spec['N'], 'basic_buffer_bytes': 32 * spec['N'] ** 3,
                'components': len(spec['stages']), 'top_level_declared': case.get('top_level'),
                'training_input_calls': len(session.state['inputs']) - len(unique_query_calls),
                'query_input_calls': len(unique_query_calls), 'native_ticks': terminal,
                'training_payload_sum': sum(item['load'] for item in session.state['inputs'] if item['role'] != 'common_physical_query'),
                'query_payload_sum': sum(item['load'] for item in unique_query_calls)}
    result = {'case': case, 'code_sha256': sha(__file__), 'identity': identity, 'recipe': spec,
              'mode': 'EXPERIENCE_PROTOCOL + NATIVE_EVOLUTION' if not edits else 'DIAGNOSTIC_FORK',
              'initial_state': checkpoints[0]['physical'], 'final_state': physical(session.world),
              'inputs': session.state['inputs'], 'receipts': receipts,
              'trace': trace, 'encounter_windows': encounters, 'readouts': readouts,
              'calculations': calculations, 'diagnostic_edits': edits, 'resources': resource,
              'checkpoints': checkpoints, 'elapsed_seconds': time.monotonic() - started,
              'status': 'MEASURED',
              'scope': 'Consumable directional moving relations; not a claim of renewable memory or learned attention. No host callback copies a native output into another input.'}
    put(out / 'MEASUREMENTS.json', result)
    return result


def screen(config, out):
    config = dict(config)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    ledger = []
    for case in config['cases']:
        path = out / case['id']
        existing = path / 'MEASUREMENTS.json'
        if existing.exists():
            result = json.loads(existing.read_text(encoding='utf-8'))
            if result['case'] != case or result['code_sha256'] != sha(__file__):
                raise RuntimeError('Cannot silently reuse a different case or code')
        else:
            result = run_case(case, path)
        ledger.append({'id': case['id'], 'architecture': case['architecture'], 'status': result['status'],
                       'path': str(existing.relative_to(ROOT)) if existing.is_relative_to(ROOT) else str(existing),
                       'resources': result['resources'], 'calculations': result['calculations'],
                       'elapsed_seconds': result['elapsed_seconds']})
        put(out / 'INDEX.json', {'configuration': config, 'cases': ledger})
        print(json.dumps({'id': case['id'], 'seconds': result['elapsed_seconds'],
                          'readout_loads': [v['center']['s_reg'] if v['center']['active'] else None for v in result['readouts']]}), flush=True)
    return ledger


def regulate(case, out):
    """Exact frozen ABCD apparatus plus a declared preT0 zero-load source.

    Semantic4 preserves its record and can supply directional proposals to a
    neighboring empty site.  That does not make its routing learned.  Earlier
    interference is measured, not hidden by inserting the source at tick290.
    """
    import dee_thinking as d
    sys.path.insert(0, str(ROOT))
    from referencias.cpc4_red.regulated_session import describe, interfaces, protocol
    out = Path(out)
    if out.exists():
        raise FileExistsError(out)
    out.mkdir(parents=True)
    started = time.monotonic()
    mode = case['mode']
    if mode not in ('none', 'external_counterflow', 'internal_source', 'internal_sham', 'internal_reverse', 'learned_pulse', 'learned_pulse_opposite', 'learned_pulse_unpaired'):
        raise ValueError('Unknown frozen regulation mechanism')
    tr = tuple(case.get('translation', (0, 0, 0)))
    spec = describe(tr)
    external_case = {'id': case['id'], 'roles': True, 'A_history': case.get('A_history', 1),
                     'B_history': 1, 'C_history': case.get('C_history', -1), 'D_history': 1,
                     'neutralizer': 'counterflow' if mode == 'external_counterflow' else 'none'}
    placements = []
    additional_interfaces = []
    extra_protocol = []
    source_description = None
    if mode.startswith('internal_'):
        site = spec['regulation']['sham_source'] if mode == 'internal_sham' else spec['regulation']['counterflow_source']
        dr = (0, 0, -1) if mode == 'internal_reverse' else (0, 0, 1)
        value = d.InitialPlacement()
        value.site = d.Coordinate(*site)
        value.raw = d.pack_record(1, 0, *dr, 4)
        value.clock = 0
        value.role = 'Declared preT0 fixed stationary zero-load directional source'
        placements.append(value)
        source_description = {'site': list(site), 'semantic': 4, 'state': 1, 's_reg': 0,
                              'direction': list(dr), 'RAW_hex': format(value.raw, '016x'), 'clock_u64': '0',
                              'scope': 'Fixed source prepared beforeT0; not an experience-dependent policy'}
    elif mode.startswith('learned_pulse'):
        # A moving zero-load relation is acquired by two actual cue/report
        # experiences.  It can revisit the observed residual after four laps.
        # The direction varies by history; no output-dependent host selection.
        direction = (0, 0, -1) if mode == 'learned_pulse_opposite' else (0, 0, 1)
        meeting = spec['regulation']['meeting']
        hub = moved(meeting, (0, 0, 1), -(292 - 3), spec['N'])
        for label, dr in (('cue', (-1, 0, 0)), ('report', (1, 0, direction[2]))):
            additional_interfaces.append(interface('native_regulator.' + label, moved(hub, dr, -3, spec['N']), dr))
            extra_protocol.append({'channel': 'native_regulator.' + label,
                                   'load': 0, 'tick': int(label == 'cue' and mode == 'learned_pulse_unpaired'),
                                   'role': 'Actual neutral directional-regulator experience'})
        source_description = {'learned_hub': list(hub), 'nominal_direction_after_pairing': list(direction),
                              'intended_meeting_tick': 292, 'nominal_laps': 4,
                              'scope': 'Directional history is acquired from zero-load paired inputs; any later interference and actual trajectory are measured'}
    recipe = d.OrganizationRecipe.research(spec['N'], placements, 0)
    recipe.interfaces = interfaces(d, spec) + additional_interfaces
    recipe.execution = d.TickOptions(d.Backend.LAZY, 1)
    world = d.OrganizationalWorld.create(recipe)
    calls = []
    for item in protocol(external_case) + extra_protocol:
        rec = world.submit(item['channel'], item['load'], item['tick'])
        calls.append({**item, 'receipt_id': rec.id, 'call_tick': 0, 'modality': 'EXPERIENCE_PROTOCOL'})
    trace, captures, saved = [], {name: {} for name in spec['banks']}, []
    times = (0, 3, 13, 15, 27, 70, 80, 82, 86, 94, 161, 228, 290, 291, 292, 293, 294, 350, 417, 424, 430, 431, 437)
    for tick in times:
        world.run_until(tick)
        samples = {name: observe(world, site) for name, site in spec['centers'].items()}
        samples['counterflow_source'] = observe(world, spec['regulation']['counterflow_source'])
        samples['regulation_meeting'] = observe(world, spec['regulation']['meeting'])
        samples['role_turn'] = observe(world, spec['role']['turn_site'])
        if source_description and 'learned_hub' in source_description:
            hub = source_description['learned_hub']
            dr = source_description['nominal_direction_after_pairing']
            samples['nominal_regulator_segment'] = observe(world, moved(hub, dr, max(0, tick - 3), spec['N']))
        trace.append({'tick': tick, 'samples': samples})
        if tick in (291, 292, 293):
            trace[-1]['local_regulation_context'] = neighborhood(world, spec['regulation']['meeting'])
        for name, bank in spec['banks'].items():
            if tick == bank['resource_read']:
                captures[name]['resource'] = observe(world, bank['resource_receiver'])
            if tick == bank['function_read']:
                captures[name]['function'] = observe(world, bank['function_receiver'])
        if tick in (0, 292, 350, 437):
            path = out / f'T{tick}.deetsnap'
            world.save_snapshot(str(path))
            saved.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'physical': physical(world)})
        put(out / 'PROGRESS.json', {'case': case, 'trace': trace, 'captures': captures})
    profiles = {}
    for name, pair in captures.items():
        bank = spec['banks'][name]
        resource, function = pair['resource'], pair['function']
        f = int(function['active'] and function['s_reg'] == 7 and function['direction'] == list(bank['supply_direction']))
        r = int(resource['active'] and resource['s_reg'] == 3 and resource['direction'] == list(bank['resource_direction']))
        profiles[name] = {'F': f, 'R': r, 'external_utility': 2 * f + r}
    final = physical(world)
    restored = d.OrganizationalWorld.load_snapshot(str(out / 'T437.deetsnap'))
    restore_equal = physical(restored) == final
    restore_receipts = [receipt(restored, item['receipt_id']) for item in calls] == [receipt(world, item['receipt_id']) for item in calls]
    result = {'case': case, 'code_sha256': sha(__file__), 'modality': 'NATIVE_EVOLUTION after declared finite experiences',
              'source_preparation': source_description, 'input_calls': calls,
              'receipts': [receipt(world, item['receipt_id']) for item in calls],
              'trace': trace, 'captures': captures, 'profiles': profiles,
              'external_utility': sum(item['external_utility'] for item in profiles.values()),
              'checkpoints': saved, 'final_state': final,
              'technical': {'save_load_physical_equal': restore_equal, 'save_load_receipts_equal': restore_receipts,
                            'direct_RAW_clock_writes_after_T0': 0, 'source_placement_count': len(placements)},
              'scope': 'No learned-attention attribution. Internal semantic4 source is a fixed physical resource; learned pulse compares history-dependent directional matter, not feedback-dependent reinforcement.',
              'status': 'MEASURED', 'elapsed_seconds': time.monotonic() - started}
    put(out / 'MEASUREMENTS.json', result)
    print(json.dumps({'id': case['id'], 'mode': mode, 'utility': result['external_utility'], 'profiles': profiles,
                      'seconds': result['elapsed_seconds']}), flush=True)
    return result


def regulation_screen(config, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for case in config['cases']:
        result = regulate(case, out / case['id'])
        rows.append({'id': case['id'], 'mode': case['mode'], 'profiles': result['profiles'],
                     'external_utility': result['external_utility'], 'elapsed_seconds': result['elapsed_seconds'],
                     'path': str((out / case['id'] / 'MEASUREMENTS.json').relative_to(ROOT))})
        put(out / 'INDEX.json', {'configuration': config, 'cases': rows})
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['worker', 'screen', 'regulation'])
    parser.add_argument('--case', type=Path)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'worker':
        result = run_case(json.loads(args.case.read_text(encoding='utf-8')), args.out)
        print(json.dumps({'id': result['case']['id'], 'elapsed_seconds': result['elapsed_seconds']}))
    elif args.command == 'screen':
        screen(json.loads(args.config.read_text(encoding='utf-8')), args.out)
    else:
        regulation_screen(json.loads(args.config.read_text(encoding='utf-8')), args.out)


if __name__ == '__main__':
    main()
