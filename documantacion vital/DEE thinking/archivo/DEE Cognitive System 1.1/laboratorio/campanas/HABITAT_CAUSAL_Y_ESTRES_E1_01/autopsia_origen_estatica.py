"""Zero-tick extraction from the verified R4 replay trace; never imports engine."""
from pathlib import Path
from array import array
from collections import Counter
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
EV = ROOT / "evidencia/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01"
SOURCE = EV / "ORIGIN_REPLAY_11/TRAZA_T5200_T5296.jsonl.gz"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def coord(i):
    return [i // 4489, (i // 67) % 67, i % 67]


def idx(p):
    return (p[0] * 67 + p[1]) * 67 + p[2]


def fields(v):
    def signed(k):
        q = (v >> k) & 15
        return q - 16 if q & 8 else q
    return {"raw": str(v), "state": v & 0xffffffff, "s_reg": (v >> 32) & 65535,
            "direction": [signed(k) for k in (48, 52, 56)], "semantic": (v >> 60) & 15}


def arrays(f):
    raw = array('Q', [0]) * 300763
    clock = array('Q', [int(f['clock_default'])]) * 300763
    for i, v, c in f['rows']:
        raw[i] = int(v)
    for i, c in f['clock_exceptions']:
        clock[i] = int(c)
    assert hashlib.sha256(raw.tobytes()).hexdigest() == f['RAW_sha256']
    assert hashlib.sha256(clock.tobytes()).hexdigest() == f['clocks_sha256']
    return raw, clock


def record(raw, clock, p):
    i = idx(p)
    return {"site": p, "clock": str(clock[i]), **fields(raw[i])}


def incoming(f, destination):
    result = []
    for i, value, c in f['rows']:
        v = int(value)
        q = fields(v)
        if q['state'] == 0 or q['semantic'] != 1 or not any(q['direction']):
            continue
        if any(abs(x) > 1 for x in q['direction']):
            continue
        p = coord(i)
        if [(p[k] + q['direction'][k]) % 67 for k in range(3)] == destination:
            result.append({"site": p, "clock": c, **q})
    return result


def main():
    frames = {f['tick']: f for f in map(json.loads, gzip.open(SOURCE, 'rt', encoding='utf8'))}
    assert sorted(frames) == list(range(5200, 5297))
    pre, post = frames[5295], frames[5296]
    raw0, clock0 = arrays(pre)
    raw1, clock1 = arrays(post)
    center = [49, 36, 35]
    context = []
    for f, raw, clocks in ((pre, raw0, clock0), (post, raw1, clock1)):
        rows = [record(raw, clocks, [(center[0]+x)%67, (center[1]+y)%67, (center[2]+z)%67])
                for x in range(-3, 4) for y in range(-3, 4) for z in range(-3, 4)]
        context.append({"tick": f['tick'], "center": center, "radius": 3,
                        "metric": "toroidal_Chebyshev", "all_sites_included_even_RAW0": True,
                        "records": rows})
    path = []
    expected = 1292814598096814081
    counts = Counter()
    rejected_projection = []
    for tick in range(5200, 5296):
        offset = tick - 5200
        p = [(20 + offset) % 67, (65 - offset) % 67, (6 + offset) % 67]
        f = frames[tick]
        lookup = {i: (int(v), c) for i, v, c in f['rows']}
        value, clock = lookup.get(idx(p), (0, f['clock_default']))
        row = {"tick": tick, "site": p, "clock": clock, **fields(value),
               "matches_expected_RAW": value == expected}
        if tick < 5230:
            rejected_projection.append(row)
            continue
        if tick < 5295:
            dest = [(p[i] + [1,-1,1][i]) % 67 for i in range(3)]
            sources = incoming(f, dest)
            dest_pre = lookup.get(idx(dest), (0, None))[0]
            row['next_destination'] = dest
            row['incoming_count_at_next_destination'] = len(sources)
            row['unique_expected_predecessor'] = len(sources) == 1 and sources[0]['site'] == p
            row['next_destination_pre_RAW'] = str(dest_pre)
            counts['unique_predecessor_steps'] += row['unique_expected_predecessor']
            counts['empty_destination_steps'] += dest_pre == 0
        if tick > 5230:
            previous = path[-1]['site']
            for axis in range(3):
                if abs(p[axis] - previous[axis]) > 1:
                    counts['periodic_crossings_axis_' + str(axis)] += 1
        path.append(row)
    deltas = [{'site': coord(i), 'pre': str(x), 'post': str(y)}
              for i, (x, y) in enumerate(zip(raw0, raw1)) if x != y]
    birth_context = []
    for tick in (5229,5230):
        braw, bclock = arrays(frames[tick])
        bc = [50,35,36]
        birth_context.append({'tick':tick, 'center':bc, 'radius':3,
                              'all_sites_included_even_RAW0':True,
                              'records':[record(braw,bclock,[(bc[0]+x)%67,(bc[1]+y)%67,(bc[2]+z)%67])
                                         for x in range(-3,4) for y in range(-3,4) for z in range(-3,4)]})
    result = {"schema": "DCS1.1.HABITAT.static_collision_autopsy.r1",
              "native_ticks_executed": 0, "trace_file": str(SOURCE.relative_to(ROOT)),
              "trace_sha256": digest(SOURCE), "source_code_sha256": digest(__file__),
              "scope": "Confirmed recorded encounter and transport sequence; functional cause strength still depends on selective intervention/control. No global information-erasure conclusion.",
              "decisive_update": {"pre_tick": 5295, "post_tick": 5296,
                                   "destination_pre": record(raw0, clock0, center),
                                   "actual_ballistic_antecedents": incoming(pre, center),
                                   "destination_post": record(raw1, clock1, center),
                                   "interpretation": "Actual two-source convergence: Y78 and (1,-1,1)7 arrive at the same previously RAW-empty site; recorded post is (1,0,1)85. Not a lineage inferred solely from equal loads.",
                                   "other_relevant_pre": [record(raw0, clock0, p) for p in ([50,35,35], [50,35,36], [50,32,35])],
                                   "other_relevant_post": [record(raw1, clock1, p) for p in ([50,35,35], [50,35,36], [49,32,35])]},
              "global_delta": {"RAW_changed_sites": len(deltas),
                               "clock_changed_sites": sum(x != y for x, y in zip(clock0, clock1)),
                               "pre_RAW_sha256": pre['RAW_sha256'], "post_RAW_sha256": post['RAW_sha256'],
                               "pre_clock_sha256": pre['clocks_sha256'], "post_clock_sha256": post['clocks_sha256'],
                               "pre_occupied": pre['occupied'], "post_occupied": post['occupied'],
                               "all_RAW_differences": deltas},
              "full_local_context": context,
              "incoming_7_transport": {"window": [5230,5295], "path": path,
                                       "checks": dict(counts),
                                       "all_expected_RAW": all(x['matches_expected_RAW'] for x in path),
                                       "full_spatial_return_to_birth": "NOT_ESTABLISHED:66 observed frames and65 unambiguous transport steps precede the next collision. Each periodic boundary was crossed, but a full67-step return to the birth site was not completed.",
                                       "rejected_back_projection_5200_5229": rejected_projection,
                                       "birth_or_transformation": {'pre_tick':5229,'post_tick':5230,
                                                                  'site':[50,35,36], 'context':birth_context,
                                                                  'scope':'XYZ7 becomes observable here from a more complex local update. The instrument does not assign a single material ancestor merely because the load is7.'}},
              "cue0_1704": {"input_tick": 5293, "admission": "applied in original receipt",
                             "pre5295": record(raw0, clock0, [50,32,35]),
                             "post5296": record(raw1, clock1, [49,32,35]),
                             "conclusion": "Not a direct ballistic antecedent of the decisive destination. Indirect causality requires the omission/control, not assumed absent merely by distance."}}
    target = EV / 'AUTOPSIA_ORIGEN_CONFIRMADA_R1.json'
    if target.exists():
        raise FileExistsError('Do not overwrite a sealed static extraction')
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps({'file': str(target), 'sha256': digest(target),
                      'delta': {k:v for k,v in result['global_delta'].items() if k != 'all_RAW_differences'},
                      'incoming': result['decisive_update']['actual_ballistic_antecedents'],
                      'path_checks': result['incoming_7_transport']['checks'],
                      'all_expected_RAW': result['incoming_7_transport']['all_expected_RAW']}))


if __name__ == '__main__':
    main()
