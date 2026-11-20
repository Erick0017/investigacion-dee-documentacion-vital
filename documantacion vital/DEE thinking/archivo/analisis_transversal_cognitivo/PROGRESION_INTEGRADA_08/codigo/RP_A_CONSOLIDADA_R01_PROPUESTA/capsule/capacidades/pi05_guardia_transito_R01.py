"""Fixed P0 guard/sham experiment, legal RAW-empty birth only.

No DEE import/side effect on import. This is researcher-prepared routing support,
not a learned response or an edit of an occupied carrier. The old FI comparison
begins at the same age and retains all176 inputs/readers; one matched extra
SEM4/state0/zero-load stationary birth is scheduled two ticks ahead.
"""
from pathlib import Path
import hashlib,json

VERSION='DEE.PI05.legal_zero_carrier_guard_sham.R01'
GUARD='eci01-pi05-fiplus-guardia'
SHAM='eci01-pi05-fiplus-sham'
PREPARE_GUARD='eci01-pi05-guardia-preparar'
PREPARE_SHAM='eci01-pi05-sham-preparar'
PREPARATION_MODES={PREPARE_GUARD,PREPARE_SHAM}
MODES={GUARD,SHAM,*PREPARATION_MODES}
PROTOCOL=Path(__file__).with_name('PROTOCOLO_PI05_GUARDIA_R01.json')

def _sha(b):return hashlib.sha256(b).hexdigest()
def protocol():
    data=PROTOCOL.read_bytes();p=json.loads(data)
    if p.get('schema')!='DEE.PI05.P0_guard_sham.protocol.R01'or p.get('status')!='SEALED':raise ValueError('Frozen prospective guard/sham protocol only')
    if p['sites']!={'guard':[19,53,20],'sham':[21,53,20]}or p['birth']!={'state':0,'semantic':4,'s_reg':0,'direction':[0,0,0],'delay_ticks':2}:
        raise ValueError('Fixed matched raw-empty support geometry; no payload-selected route or fields')
    if p['source']['N']!=67 or p['source']['tick']!=817876:raise ValueError('Exact qualified causal parent required')
    for name,h in p['dependencies_sha256'].items():
        if Path(name).name!=name or _sha(Path(__file__).with_name(name).read_bytes())!=h:raise ValueError('Preserved guard dependency changed: '+name)
    return p,_sha(data)

def validate_literal(row):
    if isinstance(row,dict)and row.get('modo')in PREPARATION_MODES:
        if set(row)!={'modo'}:raise ValueError('Fixed one-time P0 support preparation only; no fields, site, time or answer argument')
        return
    if not isinstance(row,dict)or row.get('modo')not in MODES or set(row)!={'modo','izquierda','derecha','captura'}:
        raise ValueError('Explicit fixed guard/sham mode and independent public operands/capture condition only')
    if any(type(row[k])is not int or not 0<=row[k]<=20 for k in('izquierda','derecha')):raise ValueError('Original independent balance domain0..20')
    if row['captura']not in('normal','global','fragmentar'):raise ValueError('Predeclared capture condition only')

def validate(a,row):
    validate_literal(row);p,ph=protocol()
    from capacidades import pi05_transito_causal_R01 as baseline
    from app.native_tools import physical,observe
    identity=baseline._identity(a)
    # This first causal test is deliberately bound to one coherent frozen
    # source, not a runtime search for a favourable observation or geometry.
    source=physical(a.world)
    if row['modo']not in PREPARATION_MODES and any(source[k]!=p['source'][k]for k in('N','tick','RAW_sha256','clocks_sha256')):
        raise ValueError('Guard trial requires the unchanged full qualified source; no rewind or repair')
    condition='guard'if row['modo']in(GUARD,PREPARE_GUARD)else'sham'
    site=p['sites'][condition];channel='PI05.P0.zero_carrier.'+condition+'.R01'
    if int(observe(a.world,site)['raw'])!=0:raise ValueError('Support site is not RAW-empty; never replace a carrier')
    if channel in set(a.world.runtime.channel_names):raise ValueError('Guard/sham already declared; never reinstall or retry')
    if row['modo']not in PREPARATION_MODES:
        calendar=baseline._calendar(a)
        if calendar['input_tick']!=int(a.tick)+2:raise ValueError('Old FI input timing differs; no retiming or changed age')
    return p,ph,identity,condition,channel,source

def dispatch(a,row,*,actuator='closed',directory=None):
    if directory is None or actuator!='closed':raise ValueError('Existing bounded owner directory and closed actuator required')
    p,ph,identity,condition,channel,before=validate(a,row)
    from dee_thinking import _native as d
    from dee_thinking.consolidated import exact_receipt
    from capacidades import pi05_transito_causal_R01 as baseline
    from app.native_tools import physical,observe
    site=p['sites'][condition];pre=observe(a.world,site);tick=int(a.tick)+2
    c=d.ChannelSpec();c.name=channel;c.injection_site=d.Coordinate(*site);c.direction=d.Direction(0,0,0)
    c.state=0;c.semantic=4;c.allow_experience=True;c.allow_probe=False
    i=d.InterfaceSpec();i.name=channel;i.channel=c;a.world.declare_interface(i)
    rr=a.world.submit(channel,0,tick)
    scheduled={'id':int(rr.id),'port':channel,'site':site,'direction':[0,0,0],'tick':tick,'payload':0,
               'declared_state':0,'declared_semantic':4}
    after_scheduling=physical(a.world)
    if before!=after_scheduling:raise RuntimeError('Scheduling support changed RAW/clocks/age; preserve future')
    if row['modo']in PREPARATION_MODES:
        scheduled['receipt']=exact_receipt(a.world.runtime.receipt(scheduled['id']))
        return {'version':VERSION,'guard_protocol_sha256':ph,'condition':condition,'before_tick':int(a.tick),'after_tick':int(a.tick),
            'new_native_ticks':0,'new_inputs_scheduled':1,'support':{'site':site,'channel':channel,'request':scheduled,
                'before':pre,'after':observe(a.world,site),'physical_before_scheduling':before,'physical_after_scheduling':after_scheduling,
                'installation_is_pending_until_admitted':True,'expected_persistent_RAW_after_admission':str(4<<60),
                'host_RAW_or_clock_writes':0,'one_time_namespace_prevents_reinstallation':True},
            'scope':'Operator-prepared P0 support, scheduled through legal interface. Not yet an applied support or functional recovery. Advance only through subsequent declared official protocols; preserve pending agenda, never reinject.'}
    # No advance/callback/alternate reader here. The existing comparison drives
    # exactly the same official scheduler through its original198-tick horizon.
    result=baseline._fiplus(a,{'modo':baseline.FIPLUS,'izquierda':row['izquierda'],'derecha':row['derecha'],'captura':row['captura']},directory)
    scheduled['receipt']=exact_receipt(a.world.runtime.receipt(scheduled['id']))
    old_requests=result['requests'];requests=[scheduled,*old_requests];unique={}
    for request in requests:
        if request['id']in unique and request!=unique[request['id']]:raise ValueError('Contradictory request alias')
        unique[request['id']]=request
    statuses=[r['receipt']['status']for r in unique.values()]
    if len(old_requests)!=176:raise RuntimeError('Old protocol input count changed; preserve actual future')
    result.update({'version':VERSION,'intervention_condition':condition,'guard_protocol_sha256':ph,
        'requests':requests,'Native_inputs':{'unique_requested':len(unique),'applied':sum(x=='applied'for x in statuses),
            'rejected_or_other':sum(x!='applied'for x in statuses),'expected_old_protocol_count':176,'extra_support_count':1,'expected_total':177},
        'support':{'site':site,'channel':channel,'request':scheduled,'before':pre,'after':observe(a.world,site),
            'physical_before_scheduling':before,'physical_after_scheduling':after_scheduling,'no_tick_advance_to_prepare':True,
            'old_operand_codec_clock_or_reader_changed':False,'host_RAW_or_clock_writes':0,
            'birth_clock_contract':'Existing full clock word preserved by Runtime.apply_events_at_boundary; Native clock evolution remains enabled'},
        'scope':'Prepared P0 guard versus dose/phase-matched off-path sham. The native answer and causal effect remain empirical; this is not learned recovery, self-protection or a supplied arithmetic answer.'})
    return result

def code_files():return [Path(__file__),PROTOCOL]
