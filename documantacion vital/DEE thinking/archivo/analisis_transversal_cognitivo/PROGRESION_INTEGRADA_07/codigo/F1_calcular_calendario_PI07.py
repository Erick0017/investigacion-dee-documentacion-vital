"""Conditional integer geometry, not a DEE simulation or Native replay."""
from pathlib import Path
import argparse, hashlib, json

N = 67


def first_common_site(z_old, z_new, birth, horizon=2*N):
    # Hypothesis only: each contribution keeps its unit direction until contact.
    for tick in range(birth, horizon+1):
        old = (z_old+tick) % N
        new = (z_new-(tick-birth)) % N
        if old == new:
            return {'relative_tick': tick, 'z': old,
                    'at_birth': tick == birth,
                    'scope': 'Conditional free unit-direction trajectories, not Native lineage.'}
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args()
    if args.salida.exists():
        raise FileExistsError(args.salida)
    p7 = Path(__file__).resolve().parents[1]
    atc = p7.parent
    c = atc.parent.parent / 'DEE Cognitive 2.0'
    sources = [
        atc/'PROGRESION_INTEGRADA_06/control/RECALCULO_CAUSAL_INTERRUPCION_PI06_R02.json',
        atc/'PROGRESION_INTEGRADA_06/codigo/pi06_interrupcion_R02.py',
        atc/'PROGRESION_INTEGRADA_05/codigo/pi05_transito_causal_R01.py',
        c/'sistema/capacidades/percepcion_cruda_fi01.py',
        c/'sistema/capacidades/mente_unificada_01.py',
    ]
    refs = [{'path': str(p), 'bytes': p.stat().st_size,
             'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources]
    historical = first_common_site(47, 51, 2)
    assert historical['relative_tick'] == 3 and historical['z'] == 50
    measured = json.loads(sources[0].read_text(encoding='utf-8'))
    case = next(x for x in measured['cases'] if x['rows'][0]['condition'] == 'contraflujo')
    row = case['rows'][0]
    contact = row['capture_inspection']['frames'][-1]
    assert contact['tick'] - row['before_tick'] == 3
    assert contact['contact']['site'] == [52, 48, 50]
    assert contact['contact']['direction'] == [0, 0, 0]
    current = first_common_site(47, 51, 8)
    assert current['relative_tick'] == 73 and current['z'] == 53
    phases = []
    for offset in (135, 136, 137):
        # S=qsel-1. The unchanged FI128 leaf is start+2, root=start+21,
        # datum=start+59, requested query=start+56.
        qsel = 763  # A modulo782 representative, not a real-world tick.
        fi_start = qsel + offset
        requested = fi_start + 56
        # Exact current frontend source algebra: calendar_query_timing.
        boundary = ((requested-2)//391+1)*391
        effective = boundary+2 if boundary <= requested+8 else requested
        shift = effective-requested
        parent = effective-48
        rel_parent = parent-(qsel-1)
        phases.append({'phase': offset-136, 'FI_start_minus_qsel': offset,
                       'requested_FI_query_minus_qsel': offset+56,
                       'FI_calendar_shift': shift,
                       'parent_frame_minus_sensor_S': rel_parent,
                       'old_plusZ_z_at_parent_frame_if_uninterrupted': (47+rel_parent)%N,
                       'unopposed_minusZ_z_at_parent_frame_if_pulse': (51-(rel_parent-8))%N,
                       'conditional_contact_precedes_parent': current['relative_tick'] < rel_parent,
                       'prediction_only': True})
    result = {
        'schema': 'DEE.PI07.F1.prospective_sensor_actuator_integer_geometry.v1',
        'new_Native_ticks': 0, 'Native_experiment_or_replay': False,
        'status': 'PROPOSED_NOT_EXECUTED_NOT_VALIDATED', 'sources': refs,
        'N': N, 'sensor_site': [52,48,47],
        'sensor_contract': 'STATE low2bits of exact RAW at S=qsel-1; supplied by I4 design, not tested by this script.',
        'selector_schedule': {'query': 'qsel', 'datum': 'qsel+3', 'read': 'qsel+4',
                              'hold_until': 'qsel+6', 'actor_birth': 'qsel+7=S+8'},
        'fixed_actor': {'site':[52,48,51], 'state':1, 'semantic':1,
                        's_reg':0, 'direction':[0,0,-1]},
        'historical_PI06_integer_prediction': historical,
        'historical_PI06_measured_contact_frame': contact['tick'],
        'historical_PI06_measured_contact_RAW': contact['contact']['RAW'],
        'new_PI07_conditional_first_contact': current,
        'old_plusZ_parent58_visits_relative_S': [11,78,145],
        'qsel_required_mod782_for_this_table': 763,
        'FI128_no_shift_offset_verified_from_source': 56,
        'three_prospective_external_viability_phases_only': phases,
        'limitations': [
            'Free unit motion and survival until contact are hypotheses, not a simulated DEE response.',
            'Both injection site and neighbouring fields need actual closed-state preflight; no RAW clearing.',
            'Same STATE at the sensor supplies no information about a future host-chosen FI delay; these phases are not a contextual learning reserve.',
            'No-hazard counterpulse absence from the parent at one frame does not prove global innocence or absence of later effects.',
            'The new schedule is recovery of a formed circulating contribution, not anticipation of its first passage.',
            'A physical input, receipt, cost and effect must remain distinct; NULL is not abstention.'
        ],
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(args.salida),'bytes':args.salida.stat().st_size,
                      'sha256':hashlib.sha256(args.salida.read_bytes()).hexdigest(),
                      'contact_conditional':current,'Native_ticks':0},ensure_ascii=False))


if __name__ == '__main__':
    main()
