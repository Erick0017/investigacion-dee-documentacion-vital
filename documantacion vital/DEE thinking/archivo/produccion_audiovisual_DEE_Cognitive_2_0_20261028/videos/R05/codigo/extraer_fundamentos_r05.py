"""Export already-existing evidence for R05. No engine import or simulation."""
from pathlib import Path
import datetime
import hashlib
import json
from leer_compendio_archivado import ArchivedCompendium, THINKING, ARCHIVE

HERE = Path(__file__).resolve().parents[1]
VIDEOS = HERE.parent
OUT = HERE / 'datos/evidencia_fundamentos_R05.json'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    arc = ArchivedCompendium()
    reference_path = 'cpc8/genealogia/fuentes/3867d6fa86a3b2c90b42.json'
    runner_path = 'cpc8/genealogia/fuentes/6f3babac1f303f340b0e.py'
    recovered = arc.recovered([reference_path, runner_path])
    reference = json.loads(recovered[reference_path])
    core_readings = [x for x in reference['transfer'] if x['query_direction'] == [1, 0, 0] and x['mode'] in ('trained', 'untrained')]
    core_transitions_path = 'sectores/core/verificaciones/CORE06_PRIMARY_TRANSITIONS.json'
    transitions = arc.json(core_transitions_path)
    selected_worlds = [{'index': i, **w} for i, w in enumerate(transitions['worlds'])
                       if w['case']['function'] == 'run_transfer' and w['case']['args'][0] == [1, 0, 0]
                       and w['case']['args'][1] in ('trained', 'untrained')]
    r04_path = VIDEOS / 'revision_R04_concepto_visual/fragmento_evidencia.json'
    r04_bytes = r04_path.read_bytes()
    r04 = json.loads(r04_bytes)
    g07_path = VIDEOS / 'produccion_cientifica/fuentes_g07/G07_EVIDENCIA_Y_GEOMETRIA.json'
    g07_bytes = g07_path.read_bytes()
    source_rows = [{'archive': str(ARCHIVE), 'logical_member': p, **arc.index[p]} for p in (reference_path, runner_path)]
    source_rows += [{'archive': str(ARCHIVE), 'logical_member': core_transitions_path, **arc.files[core_transitions_path]},
                    {'path': str(r04_path), 'sha256': sha(r04_bytes), 'bytes': len(r04_bytes)},
                    {'path': str(g07_path), 'sha256': sha(g07_bytes), 'bytes': len(g07_bytes)}]
    data = {
        'schema': 'DEE.video.R05.historical_evidence.v1',
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': {'native_imports': 0, 'new_ticks': 0, 'new_experiments': 0,
                  'meaning': 'Directed archival extraction; does not create missing physical frames.'},
        'scenes': {
            'S03': {
                'case': 'CORE06/run_transfer/+X/trained-versus-untrained', 'N': 41,
                'representation': 'B', 'label': 'Reconstrucción · CORE06',
                'not_current_life': True, 'tick_range': [0, 16],
                'events': [
                    {'tick': 0, 'kind': 'initial_recipe', 'carriers': [
                        {'id': 'cue', 'xyz': [16, 20, 20], 'direction': [1, 0, 0], 's_reg': 5},
                        {'id': 'teacher', 'xyz': [24, 16, 20], 'direction': [-1, 1, 0], 's_reg': 7}],
                     'applies_to': 'trained only', 'source': runner_path + ':L82-100'},
                    {'tick': 4, 'kind': 'documented_meeting', 'xyz': [20, 20, 20],
                     'functional_support': {'direction': [0, 1, 0], 's_reg': 12},
                     'status': 'Support fields derived from declared recipe/sector, not a retained T4 full RAW frame.'},
                    {'tick': 12, 'kind': 'new_query_injected', 'xyz': [16, 32, 20],
                     'direction': [1, 0, 0], 's_reg': 103, 'applies_to': 'both matched worlds',
                     'status': 'Exact external write verified in selected worlds100/101.'},
                    {'tick': 16, 'kind': 'local_observed_result', 'xyz': [20, 32, 20],
                     'trained': next(x['record'] for x in core_readings if x['mode'] == 'trained'),
                     'untrained': next(x['record'] for x in core_readings if x['mode'] == 'untrained'),
                     'status': 'Local primary read, reproduced in R01; teaching inputs5/7 differ from query103.'}],
                'readings': core_readings, 'exact_initial_and_final_digests': selected_worlds,
                'limits': ['No complete per-tick physical frames; use temporal cuts at unknown intervals.',
                           'The omitted control has no initial teaching carriers; it is not the same learned life.',
                           'Initial geometry, inputs, access time and interpretation are prepared; the encounter-dependent transformation is native.']},
            'S06_G07': {**r04['g07'], 'representation': 'B',
                        'source_geometry': json.loads(g07_bytes),
                        'do_not_use_control_as_G07': True},
            'S08_G08': {**r04['g08'], 'representation': 'B',
                        'label': 'Reconstrucción · G08 · N53'},
            'S07_IC01': {**r04['social'], 'representation': 'A for retained sampled points; B/C for gaps',
                         'no_unobserved_lineage': True}},
        'sources': source_rows,
        'pending_here': ['S05 Ingeniería05 exact sites and fields', 'S06 M014 order pair',
                         'S07 CPC9 query/use', 'S08 transfer/context and protection', 'S10 CP02 and Pensamiento01']}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'path': str(OUT), 'bytes': OUT.stat().st_size, 'sha256': sha(OUT.read_bytes()),
                      'scenes_ready': list(data['scenes']), 'native_ticks': 0}, ensure_ascii=False))

if __name__ == '__main__':
    main()
