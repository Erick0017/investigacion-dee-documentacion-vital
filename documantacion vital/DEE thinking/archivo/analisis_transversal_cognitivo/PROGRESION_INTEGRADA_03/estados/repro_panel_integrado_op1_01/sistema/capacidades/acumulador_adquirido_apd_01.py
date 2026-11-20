"""APD01 bounded learned offset followed by native accumulation, candidate.

One existing N67 complete life, legal peripheral channels only. The caller
owns evolution/persistence; this module never creates/replaces a Runtime,
edits RAW/clocks, computes delta or keeps an answer table. Prepared trajectory
progress is metadata, not the acquired scalar. The latter remains physical.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata, decode_metadata
from dee_thinking.consolidated import exact_observation, exact_receipt

KEY = 'DEE.Cognitive.System.1.1.APD01.affine_accumulator.candidate.R1'
VERSION = 'APD01.learned_offset_native_accumulator.candidate.R1'
N = 67
BASE = 4096
J = (20, 15, 30)
MAX_USES = 5


def at(origin, direction, steps=1):
    return tuple((origin[k] + direction[k] * steps) % N for k in range(3))


def obs(a, site):
    return exact_observation(a.world.runtime.observe(d.Coordinate(*site)))


def get(a):
    if int(a.world.runtime.dimension) != N:
        raise ValueError('Existing N67 life only; no resize or T0 substitute')
    entries = dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:
        raise ValueError('Explicit protocol admission required')
    return decode_metadata(entries[KEY])


def save(a, metadata):
    a.world.runtime.set_snapshot_metadata(KEY, encode_metadata(metadata))


def declare(a, name, site, direction):
    old = next((i for i in a.world.interfaces if i.name == name), None)
    if old is not None:
        c = old.channel
        current = ([c.injection_site.x, c.injection_site.y, c.injection_site.z],
                   [c.direction.dx, c.direction.dy, c.direction.dz], c.state, c.semantic)
        if current != (list(site), list(direction), 1, 1):
            raise ValueError('An existing physical channel has another contract')
        return
    channel = d.ChannelSpec()
    channel.name = name
    channel.injection_site = d.Coordinate(*site)
    channel.direction = d.Direction(*direction)
    channel.state = 1
    channel.semantic = 1
    channel.allow_experience = True
    channel.allow_probe = False
    interface = d.InterfaceSpec()
    interface.name = name
    interface.channel = channel
    a.world.declare_interface(interface)


def geometry():
    sources = [
        {'name': 'APD.offset.key', 'site': at(J, (1, 0, 0), -5), 'direction': (1, 0, 0)},
        {'name': 'APD.offset.teacher', 'site': at(J, (-1, 1, 0), -5), 'direction': (-1, 1, 0)},
        {'name': 'APD.offset.teacher_sham', 'site': at(at(J, (0, 0, 1), 4), (-1, 1, 0), -5), 'direction': (-1, 1, 0)},
        {'name': 'APD.offset.cut', 'site': at(J, (0, 1, 0), 8), 'direction': (0, -1, 0)},
        {'name': 'APD.offset.cut_sham', 'site': at(at(J, (0, 0, 1), 4), (0, 1, 0), 8), 'direction': (0, -1, 0)}
    ]
    rounds = []
    for k in range(MAX_USES):
        query = at(J, (1, 8, 0), k)
        query = at(query, (0, 1, 0), 8)
        qname = 'APD.offset.query.' + str(k)
        tname = 'APD.offset.turn.' + str(k)
        sources.extend([
            {'name': qname, 'site': at(query, (1, 0, 0), -5), 'direction': (1, 0, 0)},
            {'name': tname, 'site': at(query, (2, 1, 0)), 'direction': (-1, 0, 0)}
        ])
        rounds.append({'step': k, 'query_site': query, 'query_port': qname,
                       'turn_port': tname, 'reader_site': at(query, (1, 2, 0)),
                       'relative_arrival': 8 * (k + 1)})
    sites = {J}
    for source in sources:
        length = 5 if source['name'].startswith(('APD.offset.key', 'APD.offset.teacher', 'APD.offset.query')) else 4
        for n in range(length + 1):
            sites.add(at(source['site'], source['direction'], n))
    # This is the finite nominal memory corridor, not a complete causal cone.
    for k in range(MAX_USES):
        query = rounds[k]['query_site']
        for n in range(9):
            sites.add(at(query, (0, 1, 0), n))
        sites.add(at(query, (1, 1, 0)))
        sites.add(at(query, (1, 2, 0)))
    for n in range(9):
        sites.add(at(J, (0, 1, 0), n))
    return {'sources': sources, 'rounds': rounds, 'nominal_sites': sorted(sites)}


def prepare(a):
    if int(a.world.runtime.dimension) != N:
        raise ValueError('Existing N67 world required')
    if KEY in dict(a.world.runtime.snapshot_metadata_entries):
        raise ValueError('Already admitted; never reset a lived protocol')
    g = geometry()
    observations = [obs(a, p) for p in g['nominal_sites']]
    blocked = [o for o in observations if int(o['raw']) != 0]
    if blocked:
        raise ValueError('Fixed nominal corridor intersects nonzero RAW; no clearing or relocation: ' + str(blocked[:6]))
    for source in g['sources']:
        declare(a, source['name'], source['site'], source['direction'])
    m = {'version': VERSION, 'prepared_tick': a.tick, 'training_arrival': None,
         'uses': 0, 'status': 'ADMITTED_NOT_TAUGHT',
         'assistance': 'Fixed peripheral channels, finite moving query/turn schedule '
                       'and payload-minus4096 decoder. No stored teacher numbers, '
                       'delta, cumulative total, target or worker answer.'}
    save(a, m)
    return {'version': VERSION, 'new_native_ticks': 0, 'geometry': g,
            'nominal_corridor_before': observations,
            'classification': 'Prepared peripheral protocol P0; no content learned by admission',
            'coverage': 'Nominal sources/paths checked RAW0 now, not future vacancy or complete context isolation'}


def submit(a, name, value, tick):
    receipt = a.world.submit(name, value, tick)
    return {'id': int(receipt.id), 'port': name, 'payload': value, 'tick': tick}


def receipts(a, requests):
    return [{**r, 'receipt': exact_receipt(a.world.runtime.receipt(r['id']))} for r in requests]


def teach(a, x, y, *, teacher='paired', intervention='none'):
    m = get(a)
    if m['status'] != 'ADMITTED_NOT_TAUGHT':
        raise ValueError('One explicit lesson per admitted history; no silent re-teaching')
    if any(type(v) is not int or not 0 <= v <= 32 for v in (x, y)):
        raise ValueError('Initial teaching domain exact x,y0..32')
    if teacher not in ('paired', 'omitted', 'decoupled') or intervention not in ('none', 'cut', 'sham'):
        raise ValueError('Frozen teacher/control modalities only')
    arrival = a.tick + 7
    requests = [submit(a, 'APD.offset.key', BASE - x, arrival - 5)]
    if teacher != 'omitted':
        requests.append(submit(a, 'APD.offset.teacher' if teacher == 'paired' else 'APD.offset.teacher_sham', y, arrival - 5))
    if intervention != 'none':
        requests.append(submit(a, 'APD.offset.cut' if intervention == 'cut' else 'APD.offset.cut_sham', 0, arrival))
    frames = []
    for tick in (arrival - 1, arrival):
        a.run_until(tick)
        frames.append({'tick': a.tick, 'junction': obs(a, J),
                       'source_context': [obs(a, at(J, direction, -1)) for direction in ((1, 0, 0), (-1, 1, 0))]})
    # x/y remain only in this scientific returned receipt, not protocol metadata.
    m['training_arrival'] = arrival
    m['status'] = 'ONE_LESSON_REACHED'
    save(a, m)
    return {'version': VERSION, 'kind': 'explicit_affine_training', 'teacher': teacher,
            'intervention': intervention, 'teaching_pair': [x, y], 'arrival': arrival,
            'frames': frames, 'requests': receipts(a, requests),
            'scope': 'Two separately coded teaching contributions. No delta field or learned rule is written by host; supplied teacher result is declared acquisition assistance.'}


def accumulate(a, value):
    m = get(a)
    if m['status'] != 'ONE_LESSON_REACHED' or m['uses'] >= MAX_USES:
        raise ValueError('Declared finite five-use horizon only; no implicit reset or generic reuse claim')
    if type(value) is not int or not 0 <= value <= 32:
        raise ValueError('One exact query increment0..32')
    g = geometry()
    step = m['uses']
    route = g['rounds'][step]
    arrival = m['training_arrival'] + route['relative_arrival']
    if a.tick >= arrival - 5:
        raise ValueError('Missed this prepared opportunity; no clock rewind or target-based rescheduling')
    requests = [submit(a, route['query_port'], value, arrival - 5),
                submit(a, route['turn_port'], 0, arrival)]
    frames = []
    for tick in (arrival - 1, arrival, arrival + 1, arrival + 2):
        a.run_until(tick)
        frames.append({'tick': a.tick, 'query_site': obs(a, route['query_site']),
                       'turn_site': obs(a, at(route['query_site'], (1, 1, 0))),
                       'reader_site': obs(a, route['reader_site'])})
    gate = frames[-1]['reader_site']
    record = int(gate['raw'])
    direction = [((record >> shift) & 15) - (16 if ((record >> shift) & 15) >= 8 else 0)
                 for shift in (48, 52, 56)]
    valid = (bool(record & 0xffffffff) and ((record >> 60) & 15) == 1
             and direction == [0, 1, 0] and gate['site'] == list(route['reader_site']))
    m['uses'] += 1
    save(a, m)
    return {'version': VERSION, 'kind': 'native_bounded_accumulation', 'step': step,
            'current_increment': value, 'arrival': arrival, 'read_tick': arrival + 2,
            'route': route, 'frames': frames, 'requests': receipts(a, requests),
            'numeric_result': (((record >> 32) & 65535) - BASE) if valid else None,
            'abstention': not valid,
            'scope': 'Prepared generic turns preserve the evolved physical payload; '
                     'the output is a learned offset plus accumulated query increments, '
                     'not independent repeated n+delta or an acquired binary algorithm. '
                     'No numeric history is read from protocol metadata.'}
