"""Three finite historical replays on installed CPC6 DEE4; no campaign mains."""
from array import array
from datetime import datetime, timezone
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / 'genealogia'


def put(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def canonical(value):
    """JSON boundary only: tuples and lists have identical serialized meaning."""
    return json.loads(json.dumps(value))


def physical(world):
    r = world.runtime if hasattr(world, 'runtime') else world
    return {'tick': r.current_tick, 'raw_sha256': hashlib.sha256(array('Q', r.raw_copy()).tobytes()).hexdigest(), 'clock_sha256': hashlib.sha256(array('Q', r.clock_copy()).tobytes()).hexdigest()}


def identity():
    import dee_thinking as d
    actual = hashlib.sha256(Path(d._native.__file__).read_bytes()).hexdigest()
    assert d.__version__ == '4.0.0'
    assert d.build_info()['kernel_version'] == 27
    assert actual == '20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066'
    # The caller owns the isolated environment; it need not live in the payload.
    # Keep the exact native identity check above, without a private workspace path.
    assert Path(d.__file__).resolve().is_relative_to(Path(sys.prefix).resolve() / 'Lib' / 'site-packages')
    return {'python': sys.executable, 'module': d.__file__, 'version': d.__version__, 'native_sha256': actual, 'kernel': 27, 'wheel_sha256': '17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623'}


def compare_final(world, historical_path):
    import dee_thinking as d
    old = d.OrganizationalWorld.load_snapshot(str(historical_path))
    current, reference = physical(world), physical(old)
    result = {'current': current, 'historical': reference, 'RAW_full_equal': current['raw_sha256'] == reference['raw_sha256'], 'clocks_full_equal': current['clock_sha256'] == reference['clock_sha256'], 'tick_equal': current['tick'] == reference['tick'], 'metadata_compared_separately': True}
    assert result['RAW_full_equal'] and result['clocks_full_equal'] and result['tick_equal'], result
    return result


def cp02(out):
    sys.path.insert(0, str(GEN / 'CP02_B' / 'src'))
    from predictor import PredictorSession, PersistentTransportHabitat, AuditLog, physical as oldphysical
    s = PredictorSession.create()
    s.habitat = PersistentTransportHabitat(True)
    before = physical(s.world)
    s.save(out / 'T32.deetsnap')
    receipts = s.experience_past_results('paired')
    s.save(out / 'ACQUIRED_T34.deetsnap')
    log = AuditLog(out / 'PREDICCIONES.jsonl')
    emission = s.predict([60, 100, 150], log, 'CPC6_REFERENCE_CP02_GATE1', 7)
    s.save(out / 'EMISSION_T37.deetsnap')
    evaluations = [s.evaluate(t, log, 'CPC6_REFERENCE_CP02_GATE1') for t in (60, 100, 150)]
    s.save(out / 'FINAL_T150.deetsnap')
    old = load(GEN / 'CP02_B/resultados/PAIRED_gate1.json')
    checks = {'training_receipts_equal': receipts == old['training_receipts'], 'emission_output_equal': emission['physical_output'] == old['emission']['physical_output'], 'query_receipt_equal': emission['receipt'] == old['emission']['receipt'], 'emission_panel_equal': emission['panel_after'] == old['emission']['panel_after'], 'evaluation_panels_equal': [x['panel'] for x in evaluations] == [x['panel'] for x in old['evaluations']], 'prediction_set_equal': emission['prediction_set'] == old['emission']['prediction_set']}
    full = compare_final(s.world, GEN / 'CP02_B/checkpoints/PAIRED_gate1_FINAL.deetsnap')
    assert all(checks.values()), checks
    return {'case_id': 'CP02_B_PAIRED_gate1', 'kind': 'HISTORICAL_REPRODUCTION', 'initial': before, 'receipts': receipts, 'emission': emission, 'evaluations': evaluations, 'comparison': checks, 'full_state_comparison': full, 'scope': 'Finite persistence forecast; external barrier law independent of native output; historical3.5 physical trajectory reproduced by4.0.'}


def central(out):
    sys.path.insert(0, str(GEN / 'CPC3'))
    from core.entity import Entity
    from core.central_comparison import declare_comparison_channels, present_current_actual_report
    from core.comparison import observed, coordinate, plus
    e = declare_comparison_channels(Entity.create(initial_open=True, change_tick=80))
    e.save(out / 'T32.deetsnap')
    e.sense()
    prediction = e.predict(horizon=46)
    e.save(out / 'EMISSION_T37.deetsnap')
    e.advance(prediction['target_tick'] - e.tick)
    e.save(out / 'BEFORE_REPORT_T83.deetsnap')
    before = e.observe()
    event = present_current_actual_report(e)
    rows = []
    for t in range(e.tick, 91):
        e._advance_to(t)
        if t in (83, 84, 85, 86, 90):
            c = e.origin
            rows.append({'tick': t, 'observation': e.observe(), 'local_context': [observed(e.world.runtime.observe(coordinate(plus(c, (x, y, z))))) for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)]})
    e.save(out / 'FINAL_T90.deetsnap')
    old = load(GEN / 'CPC3/comparacion/central_discovery/open_changed/MEASUREMENTS.json')
    checks = {'emission_output_equal': canonical(prediction['physical_output']) == old['prediction']['physical_output'], 'emission_receipt_equal': canonical(prediction['receipt']) == old['prediction']['receipt'], 'before_report_panel_equal': canonical(before) == old['before_report'], 'report_receipt_equal': canonical(event['input_receipt']) == old['event']['input_receipt'], 'report_comparison_equal': canonical(event['comparison_decoder']) == old['event']['comparison_decoder'], 'full_local_trace_equal': canonical(rows) == old['trace']}
    full = compare_final(e.world, GEN / 'CPC3/comparacion/central_discovery/open_changed/FINAL.deetsnap')
    put(out / 'MEASUREMENTS.json', {'prediction': prediction, 'before_report': before, 'event': event, 'trace': rows, 'comparison': checks, 'full_state_comparison': full})
    assert all(checks.values()), checks
    return {'case_id': 'CPC3_CENTRAL_open_changed', 'kind': 'HISTORICAL_REPRODUCTION', 'prediction': prediction, 'before_report': before, 'event': event, 'trace': rows, 'operations': e.operation_calls, 'comparison': checks, 'full_state_comparison': full, 'scope': 'Forecast37 precedes target83; changed actual external outcome encoded alone; native directional discrepancy marker84, finite one-shot.'}


def sem01(out):
    # Namespace package under a unique parent; never import a historical main.
    sys.path.insert(0, str(GEN))
    experiment = importlib.import_module('SEM01.src.experiment')
    spec = load(GEN / 'SEM01/configuraciones/casos/A_future_UV.json')
    result = experiment.run_case(spec, out)
    old = load(GEN / 'SEM01/resultados/confirmacion/A_future_UV/MEASUREMENTS.json')
    import dee_thinking as d
    current = d.OrganizationalWorld.load_snapshot(str(out / 'MAIN_FINAL.deetsnap'))
    full = compare_final(current, GEN / 'SEM01/resultados/confirmacion/A_future_UV/MAIN_FINAL.deetsnap')
    scientific_old = {k: v for k, v in old.items() if k not in ('elapsed_seconds', 'identity', 'config_sha256', 'source_hashes')}
    checks = {'measurement_scientific_equal': canonical(result) == scientific_old, 'acquired_state_equal': result['teaching']['history_during_native_continuity'] == old['teaching']['history_during_native_continuity'], 'all_receipts_equal': canonical(result['teaching']['actual_receipts']) == old['teaching']['actual_receipts'], 'uses_exact_equal': canonical(result['uses']) == old['uses']}
    assert all(checks.values()), checks
    return {'case_id': 'SEM01_A_future_UV', 'kind': 'HISTORICAL_REPRODUCTION', 'comparison': checks, 'full_state_comparison': full, 'prediction_correct': [x['prediction_correct'] for x in result['uses']], 'final': result['final'], 'scope': result['scope']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', choices=('cp02', 'central', 'sem01'), required=True)
    parser.add_argument('--attempt', default='')
    parser.add_argument('--output', type=Path, help='Fresh directory for an independent technical replay; never overwrite previous results.')
    args = parser.parse_args()
    out = args.output.resolve() if args.output else ROOT / 'resultados' / 'referencias' / (args.case + args.attempt)
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    tool = identity()
    put(out / 'IDENTITY.json', tool)
    try:
        result = globals()[args.case](out)
    except Exception as error:
        import traceback
        put(out / 'ERROR.json', {'type': type(error).__name__, 'error': str(error), 'traceback': traceback.format_exc(), 'elapsed_seconds': time.monotonic() - start})
        raise
    result.update({'identity': tool, 'elapsed_seconds': time.monotonic() - start, 'utc_finished': datetime.now(timezone.utc).isoformat(), 'new_discovery_claimed': False, 'source_manifest': 'genealogia/SOURCE_MANIFEST.json'})
    put(out / 'REPLAY_CHECK.json', result)
    print(json.dumps({'case': args.case, 'elapsed_seconds': result['elapsed_seconds'], 'comparisons': result['comparison'], 'full_state': result['full_state_comparison']}, ensure_ascii=False), flush=True)
