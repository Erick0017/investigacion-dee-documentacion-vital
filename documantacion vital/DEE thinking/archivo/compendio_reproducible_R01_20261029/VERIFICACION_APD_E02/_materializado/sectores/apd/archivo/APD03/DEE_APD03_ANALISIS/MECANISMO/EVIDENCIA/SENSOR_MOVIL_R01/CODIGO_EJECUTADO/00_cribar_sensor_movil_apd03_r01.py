"""Bounded AUX link screen; execution requires the Root's explicit GO token.

This is not a paired service continuation. It examines the existing complete
physical parent under its proper OrganizationalWorld owner, with no Main write.
"""
import argparse
import gc
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import time


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf8')
    with path.open('xb') as stream:
        stream.write(gzip.compress(data, mtime=0) if path.suffix == '.gz' else data)


def load_source(path):
    spec = importlib.util.spec_from_file_location('APD03_MOBILE_SENSOR_PROSPECTIVE_R01', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--system', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--root-go', required=True, choices=['APD03_SENSOR_AUX_R01_ONLY'])
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError('New evidence directory required; never replace an attempt')
    args.out.mkdir(parents=True)
    sys.path.insert(0, str(args.system.resolve()))
    from app.lives import load_adapter
    from app.native_tools import physical
    from app.process_control import protect_current, current_resources
    from capacidades import ruta_adaptativa_apd02_04 as route
    from capacidades import selector_acrecion_nativo as selector
    protect_current(output=args.out/'RECURSOS.json', memory_limit=512*1024*1024)
    here = Path(__file__).resolve().parent
    source = here/'sensor_movil_apd03_r01.py'
    protocol_path = here/'PRIMER_CRIBADO_SENSOR_MOVIL_R01.json'
    protocol = json.loads(protocol_path.read_bytes())
    snapshot = args.system/'estado/checkpoints/APD02_MAIN.T548407.1175587c1ab9.deetsnap.gz'
    if sha(snapshot) != protocol['parent_snapshot_sha256']:
        raise ValueError('Exact full physical parent changed; no alternate parent fallback')
    module = load_source(source)
    source_rows = []
    for index, path in enumerate((Path(__file__), source, protocol_path, Path(route.__file__), Path(selector.__file__), args.system/'app/lives.py', args.system/'app/native_tools.py', args.system/'app/process_control.py')):
        target = args.out/'CODIGO_EJECUTADO'/(str(index).zfill(2)+'_'+path.name)
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(path, target)
        source_rows.append({'source':str(path), 'file':target.relative_to(args.out).as_posix(), 'bytes':target.stat().st_size, 'sha256':sha(target)})
    emit(args.out/'ANTES_DEL_PRIMER_TICK.json', {
        'protocol':protocol, 'root_go':args.root_go, 'sources':source_rows,
        'source_snapshot_sha256':sha(snapshot), 'native_not_yet_loaded':True,
        'scope':'Exact native parent only, not an imported paired service life; no S or MAIN writes',
        'resources':current_resources(),
    })
    began = time.monotonic()
    deadline = began + protocol['budget_seconds']
    queries = 0
    families = []
    winning_family = None
    stopped = None
    exact_initial_witness = None

    class DeadlineAdapter:
        def __init__(self, adapter):
            self._adapter = adapter
            self.world = adapter.world
        @property
        def tick(self):
            return self._adapter.tick
        def save(self, path):
            return self._adapter.save(path)
        def run_until(self, tick):
            # Chunking uses the same owning World/protocol and every native
            # tick; it never advances Runtime behind the world's agenda.
            while self.tick < tick:
                if time.monotonic() >= deadline:
                    raise TimeoutError('Frozen screen wall limit reached; save actual partial future')
                self._adapter.run_until(min(tick, self.tick + 67))
            return None

    def capture(adapter):
        return [module.observation(adapter, route.at((x,y,z)))
            for x in range(-3,4) for y in range(-1,4) for z in range(-1,2)]

    try:
        for family in protocol['families_order']:
            arms = []
            for arm, sequence in enumerate(protocol['arm_sequences']):
                if queries >= protocol['maximum_material_queries'] or deadline-time.monotonic() < 60:
                    stopped = 'Guard/query limit before another complete opportunity'
                    break
                folder = args.out/family/('ARM'+str(arm))
                folder.mkdir(parents=True)
                base = load_adapter('fisica_directa', snapshot)
                adapter = DeadlineAdapter(base)
                events = []
                arm_error = None
                try:
                    initial = physical(adapter.world)
                    if adapter.tick != protocol['parent_tick']:
                        raise ValueError('Parent tick differs; no T0 or rewind')
                    route_metadata = route.get(adapter)
                    if route_metadata['pending_window'] is not None:
                        raise ValueError('Parent has an unfinished native action window; never overwrite or omit its future')
                    metadata = dict(adapter.world.runtime.snapshot_metadata_entries)
                    metadata_hash = hashlib.sha256(json.dumps(metadata,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()
                    initial_witness = {'physical':initial,'all_snapshot_metadata_sha256':metadata_hash,
                        'source_encoded_complete_snapshot_sha256':sha(snapshot),
                        'pending_R04_window':route_metadata['pending_window'],
                        'future_equality_basis':'Every arm loads these exact complete encoded bytes, including native agenda/interfaces/protocols, before its one declared new sensor interface. No filtered array reconstruction.'}
                    if exact_initial_witness is None:
                        exact_initial_witness = initial_witness
                    elif initial_witness != exact_initial_witness:
                        raise ValueError('Initial causal witness differs across arms; not an equal-future contrast')
                    emit(folder/'IGUALDAD_INICIAL.json',initial_witness)
                    adapter.save(folder/'ANTES_COMPLETO.deetsnap.gz')
                    screen = module.preflight(adapter, family)
                    emit(folder/'PREFLIGHT.json', screen)
                    if not screen['admissible']:
                        arms.append({'arm':arm, 'sequence':sequence, 'initial':initial, 'not_executed':'Current injection source has nonzero RAW', 'preflight':screen})
                        continue
                    preparation = module.declare(adapter, family)
                    for index, bit in enumerate(sequence):
                        if queries >= protocol['maximum_material_queries'] or deadline-time.monotonic() < 60:
                            stopped = 'Guard/query limit before another complete opportunity'
                            break
                        before = physical(adapter.world)
                        record = module.use(adapter, bit, family=family, capture=capture)
                        queries += 1
                        adapter.save(folder/('LECTURA_'+str(index)+'_COMPLETO.deetsnap.gz'))
                        finish = module.finish_without_feedback(adapter)
                        adapter.save(folder/('TRAS_VENTANA_'+str(index)+'_COMPLETO.deetsnap.gz'))
                        event = {'index':index, 'before':before, 'selection':record,
                            'calendar_only_no_quality':finish,
                            'source_after_window':module.observation(adapter,module.site(family)),
                            'after':physical(adapter.world)}
                        events.append(event)
                        emit(folder/('EVENTO_'+str(index)+'.json.gz'),event)
                        print(json.dumps({'family':family, 'arm':arm, 'index':index, 'bit':bit,
                            'status':record['sensory_request']['receipt']['status'],
                            'choice':record['reader']['choice'],
                            'source_after':event['source_after_window']['raw'],
                            'tick':adapter.tick}),flush=True)
                        if record['sensory_request']['receipt']['status'] != 'applied' or record['reader']['choice'] is None or int(event['source_after_window']['raw']):
                            break
                    arm_row={'arm':arm, 'sequence':sequence, 'initial':initial,
                        'preparation':preparation, 'events':events,
                        'final':physical(adapter.world)}
                    emit(folder/'RESULTADOS.json.gz',arm_row)
                    arms.append(arm_row)
                except Exception as error:
                    arm_error = {'type':type(error).__name__, 'detail':str(error),
                        'physical':physical(adapter.world), 'pending_native_trace':route.get(adapter)}
                    adapter.save(folder/'FUTURO_AL_FALLO_COMPLETO.deetsnap.gz')
                    emit(folder/'FALLO.json',arm_error)
                    arms.append({'arm':arm,'sequence':sequence,'events':events,'error':arm_error})
                    if isinstance(error,TimeoutError):
                        stopped='Frozen wall limit reached during one opportunity; partial future preserved'
                finally:
                    del adapter, base
                    gc.collect()
                if stopped:
                    break
            complete = [event for arm in arms for event in arm.get('events',[])]
            by_bit = {bit:[e['selection']['reader']['choice'] for e in complete if e['selection']['raw_observed_fact']==bit] for bit in (0,1)}
            repeated_sources_empty = all(int(e['selection']['source_before']['raw'])==0 for arm in arms for e in arm.get('events',[])[1:])
            applied = all(e['selection']['sensory_request']['receipt']['status']=='applied' for e in complete)
            valid = all(e['selection']['reader']['choice'] is not None for e in complete)
            success = len(complete)==6 and applied and valid and repeated_sources_empty and all(len(set(by_bit[bit]))==1 for bit in (0,1)) and by_bit[0][0]!=by_bit[1][0]
            families.append({'family':family,'arms':arms,'native_link_criterion':{
                'performed':len(complete),'applied':sum(e['selection']['sensory_request']['receipt']['status']=='applied' for e in complete),
                'valid_fixed_outputs':sum(e['selection']['reader']['choice'] is not None for e in complete),
                'choices_by_raw_bit':by_bit,'repeated_sources_empty':repeated_sources_empty,
                'reusable_prepared_link':success}})
            if success:
                winning_family=family
                break
            if stopped:
                break
    finally:
        emit(args.out/'RESULTADOS.json', {
            'schema':'APD03.mobile_context_screen.executed.R01','protocol':protocol,
            'sources':source_rows,'families':families,'material_queries':queries,
            'winning_family':winning_family,'stopped':stopped,
            'common_exact_initial_witness':exact_initial_witness,
            'elapsed_seconds':time.monotonic()-began,'resources':current_resources(),
            'scope':'Prepared sensor usability only; no task/quality/strategy-learning claim and no MAIN continuation',
        })
    return 0


if __name__=='__main__':
    raise SystemExit(main())
