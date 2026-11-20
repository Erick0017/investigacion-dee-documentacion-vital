"""Passive laboratory observations. No state writes or response selection."""
import hashlib
import json
from array import array
from pathlib import Path
import dee_thinking as dt

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''): h.update(b)
    return h.hexdigest()

def dump(path, obj):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.partial')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    tmp.replace(path)

def coord(q): return [q.x, q.y, q.z]
def c(q): return dt.Coordinate(*q)
def add(q, d, k, n): return tuple((q[i] + k*d[i]) % n for i in range(3))
def record(o):
    r = o.record
    return {'tick': o.tick, 'position': coord(o.coordinate), 'raw': o.raw,
            'clock_uint64': o.clock, 'state': r.state, 's_reg': r.s_reg,
            'direction': [r.dx, r.dy, r.dz], 'semantic': r.semantic,
            'raw_present': r.raw_present, 'occupied': r.occupied}

def receipt(r):
    return {'id': r.id, 'kind': str(r.kind), 'status': str(r.status),
            'requested_tick': r.requested_tick, 'effective_tick': r.effective_tick,
            'channels': r.channels, 'reason': r.reason}

def gate(rt, site):
    g = dt.inspect_write_gate(rt, c(site), False)
    return {'position': list(site), 'tick': g.absolute_tick, 'clock_uint64': g.local_clock,
            'n_active': g.n_active, 'tetra_pattern': g.tetra_pattern,
            'direction_sum': [g.direction_sum.dx,g.direction_sum.dy,g.direction_sum.dz],
            'survival': g.survives_material_rule, 'protected': g.write_protected,
            'semantic_protected': g.semantic_protected, 'k': g.k,
            'period': g.period, 'phase_remainder': g.phase_remainder,
            'ordinary_increment_condition': g.ordinary_increment_condition,
            'branch': g.branch, 'demux': g.demux_status}

def full_hash(rt):
    return {x: hashlib.sha256(array('Q', getattr(rt,x+'_copy')()).tobytes()).hexdigest()
            for x in ('raw','clock')}

def state_equal(a,b):
    return a.current_tick == b.current_tick and a.raw_copy()==b.raw_copy() and a.clock_copy()==b.clock_copy()

def basal_read(w):
    o=w.observe()
    return {'tick':o.absolute_tick,'relative_tick':o.relative_tick,'delta':o.delta,
            'axis_projection':o.axis_projection,'availability':str(o.availability),
            'A':None if o.a is None else record(o.a),'B':None if o.b is None else record(o.b),
            'comparator':None if o.comparator is None else record(o.comparator),
            'supports': [record(x) for x in o.supports]}

def trace(rt, sites, start, end, cadence=1):
    """Sites may be ballistic predictions; every returned record is a real observation."""
    result=[]
    for t in range(start,end+1):
        rt.run_until(t)
        if t == end or (t-start)%cadence == 0:
            resolved={name:(q(t) if callable(q) else q) for name,q in sites.items()}
            result.append({'tick':t,'sites':{name:record(rt.observe(c(q))) for name,q in resolved.items()},
                           'tick_info':{k:getattr(rt.last_tick_info,k) for k in
                                        ('overflows','genesis','evaluated','used_threads','total_ns')},
                           'backend':str(rt.last_tick_info.used_backend)})
    return result

def signature(r):
    return [r['state']>0,r['s_reg'],*r['direction'],r['semantic']]

def moving_read(rt, birth, initial, direction):
    t=rt.current_tick; n=rt.dimension
    pos=add(initial,direction,t-birth,n)
    observed=record(rt.observe(c(pos)))
    observed.update({'identity_criterion':'declared ballistic segment; actual site observed; no universal genealogy',
                     'predicted_unwrapped':[initial[i]+direction[i]*(t-birth) for i in range(3)],
                     'birth_tick':birth,'correspondence_uncertainty':
                     'possible other contributor at intersection; see physical recipe and cuts'})
    return observed
