"""Prospective APD02 P0 access extension; no Runtime creation or scalar cache.

The legacy carrier, if it actually survives, circulates in +Y. A fixed pair
of adjacent columns receives opposite transverse query directions. Generic
zero-content turns are intended to return the summed carrier to +Y after
each encounter, alternating columns without an unbounded spatial corridor.
This is designed maintenance, not autonomous selection or memory recovery.

No caller may change a scalar from an expected answer. The sole legacy edit
is its monotonically increasing operational use counter, never a reset.
"""
from capacidades import acumulador_adquirido_apd_01 as old
from dee_thinking.persistence import decode_metadata, encode_metadata

KEY='DEE.Cognitive.System.1.1.APD02.recirculating_accumulator.R1'
VERSION='APD02.recirculating_accumulator.prospective.R1'
PERIOD=67
QUERY_Y=(old.J[1]+8)%PERIOD
PREFIX='APD02.offset.recirculating.R1'


def geometry(base_column):
    c0=base_column%PERIOD;c1=(c0+1)%PERIOD;z=old.J[2]
    columns=[c0,c1]
    qsites=[(c0,QUERY_Y,z),(c1,QUERY_Y,z)]
    directions=[(1,0,0),(-1,0,0)]
    sources=[]
    for bank,(site,direction)in enumerate(zip(qsites,directions)):
        # A zero turn meets the diagonal product one tick after the query.
        turn_site=old.at(site,(direction[0]*2,1,0))
        turn_direction=(-direction[0],0,0)
        sources.extend([
            {'name':PREFIX+'.query.'+str(bank),'site':old.at(site,direction,-5),'direction':direction},
            {'name':PREFIX+'.turn.'+str(bank),'site':turn_site,'direction':turn_direction},
            {'name':PREFIX+'.sham.'+str(bank),'site':old.at(turn_site,(0,0,1),4),'direction':turn_direction},
        ])
    readers=[(col,(QUERY_Y+2)%PERIOD,z)for col in columns]
    nominal={*qsites,*readers}
    for src in sources:
        for n in range(6 if '.query.'in src['name']else 3):
            nominal.add(old.at(src['site'],src['direction'],n))
    return {'columns':columns,'query_sites':qsites,'reader_sites':readers,
        'sources':sources,'nominal_sites':sorted(nominal)}


def _save(a,m):
    a.world.runtime.set_snapshot_metadata(KEY,encode_metadata(m))


def get(a):
    if int(a.world.runtime.dimension)!=PERIOD:
        raise ValueError('Existing N67 life only; no resizing or transplanted state')
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:raise ValueError('Explicit extension admission required')
    m=decode_metadata(entries[KEY]);legacy=old.get(a)
    if legacy['uses']<m['start_legacy_uses']:
        raise ValueError('Legacy cursor moved backwards; no reset accepted')
    if legacy['training_arrival']!=m['training_arrival']:
        raise ValueError('Legacy lesson changed; do not inherit another history silently')
    return m,legacy


def admit(a):
    """Declare interfaces only; never overwrite matter or teach the scalar."""
    if int(a.world.runtime.dimension)!=PERIOD:raise ValueError('N67 required')
    if KEY in dict(a.world.runtime.snapshot_metadata_entries):
        raise ValueError('Already extended; no restart or reset')
    legacy=old.get(a)
    if legacy['status']!='ONE_LESSON_REACHED':raise ValueError('Existing explicit lesson required')
    uses=legacy['uses']
    if type(uses)is not int or not 0<=uses<=old.MAX_USES:
        raise ValueError('Only an actual legacy position0..5 can seed this prospective extension')
    g=geometry(old.J[0]+uses)
    observed=[old.obs(a,p)for p in g['nominal_sites']]
    for src in g['sources']:old.declare(a,src['name'],src['site'],src['direction'])
    m={'version':VERSION,'admitted_tick':a.tick,'start_legacy_uses':uses,
        'training_arrival':legacy['training_arrival'],'base_column':g['columns'][0],
        'native_state_inserted':False,'legacy_cursor_reset':False,
        'assistance':'P0 fixed alternating transverse routes, zero-material turns, N67 phase schedule and shared two-gate reader. No scalar or answer in metadata.'}
    _save(a,m)
    return {'kind':'prospective_recirculating_access_admission','version':VERSION,
        'new_native_ticks':0,'legacy_uses_preserved':uses,'geometry':g,
        'nominal_context_before':observed,
        'coverage':'Interfaces declare legal future entry only. Nonzero RAW is recorded, never cleared; no continuing carrier or functional recovery is presumed.'}


def _read(a,g):
    observed=[old.obs(a,p)for p in g['reader_sites']]
    candidates=[]
    for o in observed:
        raw=int(o['raw'])
        direction=[((raw>>s)&15)-(16 if((raw>>s)&15)>=8 else 0)for s in(48,52,56)]
        if (raw&0xffffffff) and ((raw>>60)&15)==1 and direction==[0,1,0]:
            candidates.append({'site':o['site'],'value':((raw>>32)&65535)-old.BASE,'raw':str(raw)})
    valid=len(candidates)==1
    return {'sites':observed,'candidates':candidates,'valid':valid,
        'value':candidates[0]['value']if valid else None,
        'scope':'Same two physical gates every use; no expected value, teacher, selected bank or answer-history input'}


def accumulate(a,value,*,delay_periods=0,maintenance='real'):
    """One prospective use. Failed attempts also consume monotonic progress."""
    if type(value)is not int or not 0<=value<=32:raise ValueError('Exact increment0..32')
    if type(delay_periods)is not int or not 0<=delay_periods<=8:raise ValueError('Declared finite delay0..8 periods')
    if maintenance not in('real','omit','sham'):raise ValueError('Frozen maintenance/control modality')
    m,legacy=get(a);g=geometry(m['base_column'])
    progress=legacy['uses']-m['start_legacy_uses'];bank=progress%2
    # Every fixed query plane has the same toroidal Y phase. Scheduling is
    # external apparatus; the phase formula cannot access learned content.
    anchor=m['training_arrival']+8
    earliest=a.tick+7
    arrival=anchor+max(0,(earliest-anchor+PERIOD-1)//PERIOD)*PERIOD+delay_periods*PERIOD
    requests=[old.submit(a,PREFIX+'.query.'+str(bank),value,arrival-5)]
    if maintenance!='omit':
        role='turn'if maintenance=='real'else'sham'
        requests.append(old.submit(a,PREFIX+'.'+role+'.'+str(bank),0,arrival))
    frames=[]
    for tick in(arrival-1,arrival,arrival+1,arrival+2):
        a.run_until(tick)
        frames.append({'tick':a.tick,'query_sites':[old.obs(a,p)for p in g['query_sites']],
            'reader':_read(a,g)})
    legacy_before=legacy['uses'];legacy['uses']+=1
    old.save(a,legacy)
    return {'kind':'native_recirculating_accumulation_candidate','version':VERSION,
        'legacy_uses_before':legacy_before,'legacy_uses_after':legacy['uses'],
        'increment':value,'delay_periods':delay_periods,'prepared_bank':bank,
        'maintenance':maintenance,'arrival':arrival,'read_tick':arrival+2,
        'frames':frames,'requests':old.receipts(a,requests),
        'numeric_result':frames[-1]['reader']['value'],'abstention':not frames[-1]['reader']['valid'],
        'scope':'Designed P0 resources and timing. Physical inherited content must be demonstrated by opposite/absent teaching controls. No cursor reset, reconstructed payload, expected answer or autonomous-maintenance claim.'}
