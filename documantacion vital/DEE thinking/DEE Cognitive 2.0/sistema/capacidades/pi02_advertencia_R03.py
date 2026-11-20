"""PI02 R03 experimental warning-association preparation for an existing N67 life.

Only legal declared inputs and the existing owner's run_until are used.
Importing this module imports no DEE module and does not inspect or advance a world.
No valve, job selection, expected answer, automatic repair, or autonomy verdict lives
here. Metadata holds protocol progress and its external phase calendar; the decoder
reads only an observation's physical fields. A paired request is not evidence that
an acquired relation actually formed.
"""
from __future__ import annotations

from itertools import product

VERSION = 'PI02.warning_association.R03.experimental.v2'
KEY = 'DEE.Cognitive.System.1.1.PI02.warning_association.R03.v1'
N = 67
H = (4, 34, 24)
CLOSE_DIRECTION = (-1, 1, 0)
WARNING_LOAD = 7
REPORT_LOAD = 11
NORMALIZER_LOAD = 0

PORTS = {
    'W': {'name': 'PI02.R03.warning', 'site': (12, 34, 24),
          'direction': (-1, 0, 0), 'distance': 8},
    'U': {'name': 'PI02.R03.alteration_report', 'site': (1, 31, 24),
          'direction': (1, 1, 0), 'distance': 3},
    'G': {'name': 'PI02.R03.normalizer', 'site': (1, 34, 24),
          'direction': (1, 0, 0), 'distance': 3},
}


def _native():
    from dee_thinking import _native
    return _native


def _observation(a, site):
    from dee_thinking.consolidated import exact_observation
    native = _native()
    return exact_observation(a.world.runtime.observe(native.Coordinate(*site)))


def _physical(a):
    from app.native_tools import physical
    return physical(a.world, occupation=True)


def _save(a, metadata):
    from dee_thinking.persistence import encode_metadata
    a.world.runtime.set_snapshot_metadata(KEY, encode_metadata(metadata))


def _get(a):
    from dee_thinking.persistence import decode_metadata
    if int(a.world.runtime.dimension) != N:
        raise ValueError('R03 is an existing N67-life variant; no resize or substitute world')
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:
        raise ValueError('Explicit R03 interface preparation required; no implicit anatomy')
    metadata = decode_metadata(entries[KEY])
    if metadata.get('version') != VERSION or tuple(metadata.get('hub', ())) != H:
        raise ValueError('R03 protocol or fixed hub mismatch')
    if metadata.get('uncertain') or metadata.get('in_progress'):
        raise ValueError('Preserved incomplete R03 future: reconcile; never replay an uncertain request')
    if not metadata.get('interfaces_prepared'):
        raise ValueError('R03 interfaces not completely prepared')
    return metadata


def _receipt(a, identifier):
    from dee_thinking.consolidated import exact_receipt
    return exact_receipt(a.world.runtime.receipt(int(identifier)))


# Public protocol accessor for the existing wrapper; no alternative reader/API.
get = _get


def _submit(a, label, payload, at_tick):
    port = PORTS[label]
    at_tick = int(at_tick)
    if at_tick <= int(a.tick):
        raise ValueError('R03 input boundary must be future; no phase rescue')
    receipt = a.world.submit(port['name'], int(payload), at_tick)
    return {'id': int(receipt.id), 'channel': port['name'],
            'site': list(port['site']), 'direction': list(port['direction']),
            'payload': int(payload), 'requested_tick': at_tick,
            'nominal_arrival_tick': at_tick + port['distance'],
            'state': 1, 'semantic': 1, 'modality': 'LEGAL_EXPERIENCE_INPUT'}


def _receipts(a, requests):
    return [{**request, 'receipt': _receipt(a, request['id'])}
            for request in requests]


def decode_fixed(observation):
    """One frozen physical signature; no target, history label or fallback."""
    valid = (int(observation['state']) > 0
             and int(observation['semantic']) == 1
             and tuple(observation['direction']) == CLOSE_DIRECTION)
    return 'CLOSE' if valid else None


def _roi(a):
    rows = []
    for offset in product(range(-3, 4), repeat=3):
        site = tuple((H[j] + offset[j]) % N for j in range(3))
        # All fields, including nonzero RAW at state0, remain visible.
        rows.append(_observation(a, site))
    return rows


def _frame(a, encounters):
    tick = int(a.tick)
    observation = _observation(a, H)
    row = {'tick': tick, 'hub': observation,
           'fixed_signature_diagnostic': decode_fixed(observation)}
    if any(abs(tick - int(encounter)) <= 2 for encounter in encounters):
        row['context_radius3'] = _roi(a)
    return row


def _observe_until(a, end_tick, encounters):
    """Owner-preserving one-tick advance, never Runtime.run_until directly."""
    end_tick = int(end_tick)
    if end_tick < int(a.tick):
        raise ValueError('No rewind to an earlier observation')
    frames = [_frame(a, encounters)]
    for tick in range(int(a.tick) + 1, end_tick + 1):
        a.run_until(tick)
        if int(a.tick) != tick:
            raise RuntimeError('Owner did not reach the declared observation boundary')
        frames.append(_frame(a, encounters))
    return frames


def _pending(receipts):
    # A terminal rejection remains a rejected input, never an applied experience.
    # In particular, do not retry it just because its name is rejected_occupied.
    statuses = (str(row['receipt'].get('status', '')).lower() for row in receipts)
    return any(status not in ('applied', 'rejected')
               and not status.startswith('rejected_') for status in statuses)


def prepare(a):
    """Declare three fixed interfaces; do not seed/clear RAW or edit clocks."""
    if int(a.world.runtime.dimension) != N:
        raise ValueError('R03 requires the inherited N67 world')
    if KEY in dict(a.world.runtime.snapshot_metadata_entries):
        raise ValueError('R03 already has history/progress; never reinstall its preparation')
    names = {item.name for item in a.world.interfaces}
    if any(port['name'] in names for port in PORTS.values()):
        raise ValueError('R03 port names already exist without matching progress; preserve and inspect')
    before = _physical(a)
    preflight = {'hub': _observation(a, H),
                 'sources': {label: _observation(a, port['site'])
                             for label, port in PORTS.items()}}
    if any(int(row['raw']) != 0
           for row in [preflight['hub'], *preflight['sources'].values()]):
        raise ValueError('Nonzero RAW at fixed R03 hub/source; no overwrite or relocation by outcome')
    metadata = {'version': VERSION, 'hub': list(H), 'prepared_tick': int(a.tick),
                'interfaces_prepared': False, 'training': None, 'probes': [],
                'in_progress': {'operation': 'prepare_interfaces'},
                'uncertain': False,
                'calendar_scope': 'External protocol calendar, not an acquired answer or cognitive policy',
                'history_scope': 'Training labels and input IDs record research provenance only; decoder never reads them',
                'anatomy': 'External fixed three-port opportunity, not self-built anatomy',
                'normalizer_load': NORMALIZER_LOAD}
    _save(a, metadata)
    declared = []
    try:
        native = _native()
        for label, port in PORTS.items():
            channel = native.ChannelSpec()
            channel.name = port['name']
            channel.injection_site = native.Coordinate(*port['site'])
            channel.direction = native.Direction(*port['direction'])
            channel.state = 1
            channel.semantic = 1
            channel.allow_experience = True
            channel.allow_probe = False
            interface = native.InterfaceSpec()
            interface.name = port['name']
            interface.channel = channel
            a.world.declare_interface(interface)
            declared.append({'label': label, **port,
                             'state': 1, 'semantic': 1,
                             'allow_experience': True, 'allow_probe': False})
        metadata['interfaces_prepared'] = True
        metadata['in_progress'] = None
        _save(a, metadata)
    except BaseException:
        metadata['uncertain'] = True
        metadata['declared_before_failure'] = declared
        _save(a, metadata)
        raise
    return {'version': VERSION, 'operation': 'prepare_interfaces',
            'before': before, 'after': _physical(a), 'preflight': preflight,
            'declared': declared, 'new_material_inputs': 0,
            'raw_or_clock_edits': 0, 'seed_inserted': False,
            'scope': 'External anatomical opportunity only; no acquired relation inferred'}


def train(a, history='paired'):
    """One finite W/U experience, with phase/admission controls declared in v2.

    paired: W(t),U(t+5); unpaired: W(t+1),U(t+5); omit: W(t) only;
    no_training: neither input; report_only: U(t+5) only. Every branch shares
    anchor(t+8) and end(anchor+2N+3). The unpaired W shift avoids deliberately
    filling the later W admission site at its fixed phase; all actual rejections
    and residual interactions remain data, not missing semantic answers.
    """
    if history not in ('paired', 'unpaired', 'omit', 'no_training', 'report_only'):
        raise ValueError('Unknown declared R03 v2 experience history')
    metadata = _get(a)
    if metadata.get('training') is not None:
        raise ValueError('R03 training already lived; do not reset or replay it')
    before = _physical(a)
    t = int(a.tick) + 2
    anchor = t + 8
    end_tick = anchor + 2 * N + 3
    w_input_tick = (t + 1 if history == 'unpaired' else t) \
        if history in ('paired', 'unpaired', 'omit') else None
    u_input_tick = t + 5 \
        if history in ('paired', 'unpaired', 'report_only') else None
    requests = []
    metadata['in_progress'] = {'operation': 'train', 'started_tick': int(a.tick),
                               'W_input_tick': w_input_tick,
                               'U_input_tick': u_input_tick, 'anchor_external': anchor,
                               'end_tick': end_tick, 'history_record_only': history}
    _save(a, metadata)
    try:
        if w_input_tick is not None:
            requests.append(_submit(a, 'W', WARNING_LOAD, w_input_tick))
        if u_input_tick is not None:
            requests.append(_submit(a, 'U', REPORT_LOAD, u_input_tick))
        metadata['in_progress']['request_ids'] = [row['id'] for row in requests]
        _save(a, metadata)
        frames = _observe_until(a, end_tick, (anchor, anchor + 1))
        receipts = _receipts(a, requests)
        uncertain = _pending(receipts)
        metadata['training'] = {'history_record_only': history,
                                'W_input_tick': w_input_tick,
                                'U_input_tick': u_input_tick, 'anchor_external': anchor,
                                'end_tick': int(a.tick),
                                'request_ids': [row['id'] for row in requests],
                                'meaning': 'Lived protocol record only; acquired relation requires physical evidence'}
        metadata['uncertain'] = uncertain
        metadata['in_progress'] = None if not uncertain else {
            'operation': 'train', 'reason': 'Input receipt not terminal at fixed horizon'}
        _save(a, metadata)
    except BaseException:
        metadata['uncertain'] = True
        _save(a, metadata)
        raise
    return {'version': VERSION, 'operation': 'train',
            'history_record_only': history, 'before': before,
            'W_input_tick': w_input_tick, 'U_input_tick': u_input_tick,
            'nominal_pairing_tick': anchor,
            'anchor_external': anchor, 'fixed_end_tick': end_tick,
            'requests': receipts, 'frames': frames, 'after': _physical(a),
            'uncertain': uncertain,
            'direct_RAW_writes': 0, 'direct_clock_writes': 0,
            'no_acquisition_verdict_from_admission': True,
            'scope': 'Prepared temporal/spatial experience; all histories share the final horizon; unpaired residual context is retained'}


def probe(a, periods=2, warning=True):
    """Fixed-q observation; never select a better frame/reader after seeing output."""
    if type(periods) is not int or periods not in (2, 3, 5):
        raise ValueError('R03 periods fixed to the declared2/3/5 domain')
    if type(warning) is not bool:
        raise ValueError('R03 warning is an explicit environmental Boolean')
    metadata = _get(a)
    training = metadata.get('training')
    if training is None:
        raise ValueError('No lived R03 experience/calendar; do not silently seed one')
    anchor = int(training['anchor_external'])
    before = _physical(a)
    q = anchor + ((int(a.tick) + 10 - anchor + N - 1) // N) * N + periods * N
    normalizer_arrival = q + N
    end_tick = normalizer_arrival + 3
    requests = []
    metadata['in_progress'] = {'operation': 'probe', 'started_tick': int(a.tick),
                               'q_external': q, 'normalizer_arrival_external': normalizer_arrival,
                               'end_tick': end_tick, 'warning_offered': warning}
    _save(a, metadata)
    try:
        if warning:
            requests.append(_submit(a, 'W', WARNING_LOAD, q - 8))
            # Generic resource depends only on the offered warning, not its result.
            # Even payload0 is a real material input and is fully recorded.
            requests.append(_submit(a, 'G', NORMALIZER_LOAD, normalizer_arrival - 3))
        metadata['in_progress']['request_ids'] = [row['id'] for row in requests]
        _save(a, metadata)
        frames = _observe_until(a, end_tick, (q, normalizer_arrival))
        fixed = next(row['hub'] for row in frames if row['tick'] == q)
        command = decode_fixed(fixed)
        receipts = _receipts(a, requests)
        uncertain = _pending(receipts)
        index = len(metadata['probes'])
        metadata['probes'].append({'index': index, 'q_external': q,
                                   'end_tick': int(a.tick), 'periods_external': periods,
                                   'warning_offered': warning,
                                   'request_ids': [row['id'] for row in requests]})
        metadata['uncertain'] = uncertain
        metadata['in_progress'] = None if not uncertain else {
            'operation': 'probe', 'reason': 'Input receipt not terminal at fixed horizon'}
        _save(a, metadata)
    except BaseException:
        metadata['uncertain'] = True
        _save(a, metadata)
        raise
    return {'version': VERSION, 'operation': 'probe', 'index': index,
            'before': before, 'periods_external': periods,
            'warning_offered': warning, 'fixed_query_tick': q,
            'fixed_read_tick': q, 'fixed_read_window_radius': 0,
            'fixed_observation': fixed, 'fixed_command': command,
            'normalizer_arrival_external': normalizer_arrival if warning else None,
            'fixed_end_tick': end_tick, 'requests': receipts,
            'frames': frames, 'after': _physical(a), 'uncertain': uncertain,
            'all_signature_events_diagnostic_only': [
                {'tick': row['tick'], 'hub': row['hub']}
                for row in frames if row['fixed_signature_diagnostic'] == 'CLOSE'],
            'decoder_contract': {'site': list(H), 'time': 'exactqonly',
                                 'active': 'state>0', 'semantic': 1,
                                 'direction': list(CLOSE_DIRECTION),
                                 'output': 'CLOSE; all other observations NULL',
                                 'history_or_expected_answer_read': False},
            'assistance': 'Prepared phase calendar, interfaces and generic normalization; no valve/jobs or policy substitution here',
            'scope': 'Current observation plus lived physical history. Other close signatures are diagnostics, never a replacement for fixedq. No autonomy or acquired-association verdict is automatic.'}
