"""Explicit PI05 FI128 observation/age instruments; no answer policy.

Imports stdlib only. The exact old comparison is called on the existing world;
only prospective global observation/segmentation is added. No Runtime advance,
field/clock edits, material markers, anatomy, reset or main selection.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import uuid

VERSION='DEE.Cognitive.PI05.causal_transit_instrument.R01'
FIPLUS='eci01-pi05-fiplus'
WAIT='eci01-pi05-esperar'
EXTEND='eci01-pi05-yoke-extender'
MODES={FIPLUS,WAIT,EXTEND}
PROTOCOL=Path(__file__).with_name('PROTOCOLO_PI05_TRANSITO_R01.json')
SYSTEM_KEY='DEE.Cognitive.System.1.1.life.v1'
_CAPTURE=None


def _sha(b):return hashlib.sha256(b).hexdigest()
def _canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf8')
def _capture_module():
    global _CAPTURE
    if _CAPTURE is None:
        p=Path(__file__).with_name('observador_global_PI05_R01.py')
        spec=importlib.util.spec_from_file_location('PI05_fixed_global_recorder',p)
        _CAPTURE=importlib.util.module_from_spec(spec);spec.loader.exec_module(_CAPTURE)
    return _CAPTURE


def protocol():
    data=PROTOCOL.read_bytes();p=json.loads(data)
    if p.get('schema')!='DEE.PI05.transit.protocol.v1'or p.get('status')not in('DRAFT','SEALED')or p.get('N')!=67:
        raise ValueError('Exact declared PI05 protocol only')
    for name,h in p['dependencies_sha256'].items():
        if Path(name).name!=name or _sha(Path(__file__).with_name(name).read_bytes())!=h:
            raise ValueError('Fixed PI05 dependency changed: '+name)
    offsets=p['capture_offsets_q'];anchors=p['anchor_offsets_q']
    if not isinstance(offsets,list)or not offsets or len(set(offsets))!=len(offsets)or not all(type(x)is int for x in offsets):
        raise ValueError('Finite prospective unique integer capture offsets required')
    if not set(anchors)<=set(offsets)or len(anchors)>40 or len(offsets)>1440:
        raise ValueError('PI05 capture budget exceeded')
    return p,_sha(data)


def validate_literal(row):
    if not isinstance(row,dict)or row.get('modo')not in MODES:raise ValueError('Explicit PI05 mode only')
    if row['modo']==FIPLUS:
        if set(row)!={'modo','izquierda','derecha','captura'}:raise ValueError('Exact public independent operands and fixed capture mode only')
        if any(type(row[k])is not int or not 0<=row[k]<=20 for k in('izquierda','derecha')):raise ValueError('Old independent balance domain0..20, bias20; not arithmetic bias32')
        if row['captura']not in('normal','global','fragmentar'):raise ValueError('Prospective observation condition only')
    elif row['modo']==WAIT:
        if set(row)!={'modo','ticks'}or type(row['ticks'])is not int or not 1<=row['ticks']<=20000:raise ValueError('Explicit legal wait1..20000ticks only')
    elif set(row)!={'modo'}:raise ValueError('Yoked extension has no target, signal, route, path or answer argument')
    return row


def _identity(a):
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if SYSTEM_KEY not in entries or int(a.world.runtime.dimension)!=67:raise ValueError('Existing complete N67 life required')
    m=json.loads(entries[SYSTEM_KEY]);life=m.get('life_id','')
    if not life.startswith('ECI02_PI03_REPRO_')or'PI05_'not in life:raise ValueError('Explicit PI05 diagnostic identity only; never current principal')
    if m.get('profile')!='fisica_directa':raise ValueError('The inherited direct physical profile is required')
    return m


def validate(a,row):
    validate_literal(row);_identity(a);p,_=protocol()
    if p['status']!='SEALED':raise ValueError('Root must freeze PI05 before Native evaluation')
    return True


def _calendar(a):
    # Literal same geometry/timing as old perception.frame, not an answer.
    from capacidades import percepcion_cruda_fi01 as raw
    from capacidades import mente_unificada_01 as mu
    m=raw.get(a)
    if m['level']!=128:raise ValueError('Existing FI128 preparation required; never install another body')
    g=raw.geometry(m['level']);leaf=int(a.tick)+2;root=leaf-g['raw_relative_tick'];datum=root+38
    timing=mu.query_timing(a,int(datum-3));shift=timing['wait_ticks'];q=timing['effective_query_tick']
    return {'before_tick':int(a.tick),'input_tick':leaf+shift,'query_tick':q,'C_tick':q+1,'S_tick':q+3,
        'early_reader_tick':q+4,'old_reader_tick':q+6,'horizon_tick':q+8+2*67,'timing':timing}


def _fiplus(a,row,directory):
    from capacidades import acceso_eci01 as old
    p,ph=protocol();identity=_identity(a);calendar=_calendar(a);q=calendar['query_tick']
    ticks=sorted({q+x for x in p['capture_offsets_q']if calendar['before_tick']<=q+x<=calendar['horizon_tick']})
    anchors={q+x for x in p['anchor_offsets_q']} & set(ticks)
    recorder=None;used=a
    if row['captura']in('global','fragmentar'):
        capture=_capture_module()
        if row['captura']=='global':
            # Fixed source-system location, no payload-supplied path; excluded
            # from worker/outbox export and never read to choose an action.
            system=Path(__file__).resolve().parents[1]
            target=system/'estado/observacion_pasiva'/identity['life_id']/('PI05_'+uuid.uuid4().hex)
            recorder=capture.GlobalRecorder(target,N=67,ticks=ticks,anchor_ticks=anchors,
                provenance={'life_id':identity['life_id'],'protocol_sha256':ph,'module_version':VERSION,
                    'old_protocol':'acceso_eci01.balance -> acciones_nativas_apd04.balance -> FI128.frame',
                    'calendar':calendar,'public_operands':{'left':row['izquierda'],'right':row['derecha']},
                    'source_provenance':p.get('source_provenance',{}),
                    'capture_mode':'global','actor_answers_or_expected_results':False},
                max_frames=p['max_frames_per_trial'],max_compressed_bytes=p['max_compressed_bytes_per_trial'])
        used=capture.CapturingAdapter(a,ticks=ticks,recorder=recorder)
    # No new reader: both original q+4 and q+6 observations are returned intact.
    result=old.balance(used,row['izquierda'],row['derecha'])
    capture_result=None if recorder is None else recorder.close()
    if result['query_tick']!=q:raise RuntimeError('Original scheduler differs from prospective capture calendar; preserve the actual future')
    requests=result['all_material_receipts'];ids={}
    for r in requests:
        receipt=r['receipt'];rid=r['id']
        if rid in ids and ids[rid]!=receipt:raise ValueError('Contradictory Native alias')
        ids[rid]=receipt
    statuses=[r['status']for r in ids.values()]
    return {'version':VERSION,'instrument':'old_FIplus_with_prospective_global_capture','capture_mode':row['captura'],
        'before_tick':calendar['before_tick'],'after_tick':int(a.tick),'calendar':calendar,
        'legacy_result':result,'early_physical_choice':result['early_physical_choice'],'old_q6_choice':result['old_q6_choice'],
        'requests':requests,'Native_inputs':{'unique_requested':len(ids),'applied':sum(s=='applied'for s in statuses),
            'rejected_or_other':sum(s!='applied'for s in statuses),'expected_old_protocol_count':176},
        'external_global_capture':capture_result,'fragmented_boundaries':None if used is a else used.boundaries,
        'scope':'Original physical comparison, operands/codec/176-input protocol/readers retained. Global arrays are external observation, not participant memory or a learned access strategy.'}


def dispatch(a,row,*,actuator='closed',directory=None):
    validate(a,row)
    if actuator!='closed'or directory is None:raise ValueError('Existing owned directory and original actuator contract required')
    if row['modo']==FIPLUS:return _fiplus(a,row,directory)
    if row['modo']==WAIT:
        start=int(a.tick);a.run_until(start+row['ticks'])
        return {'version':VERSION,'legal_wait':row['ticks'],'before_tick':start,'after_tick':int(a.tick),
            'scope':'Official adapter/world scheduler advance; not a clock edit or learned initiative'}
    if row['modo']==EXTEND:
        from capacidades import pi04_coordinacion_central_C2C as c2c
        from capacidades import pi05_yoke_futuros_R01 as future
        return future.prepare(a,c2c,directory)
    raise ValueError('No other PI05 operation')


def operational_dependencies(a,directory):
    return {'version':VERSION,'present':False,'new_native_ticks':0,
        'scope':'No new cognitive metadata key. External capture files are not required to decide or continue; diagnostic effects use the existing owner contract.'}
def uncertain(a):return False


def code_files():
    return [Path(__file__),PROTOCOL,Path(__file__).with_name('observador_global_PI05_R01.py'),
            Path(__file__).with_name('pi05_yoke_futuros_R01.py')]
