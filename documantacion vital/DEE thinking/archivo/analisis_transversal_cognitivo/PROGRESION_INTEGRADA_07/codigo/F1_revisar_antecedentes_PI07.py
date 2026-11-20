"""Directed frozen-document crosscheck. Standard library; never imports DEE."""
from pathlib import Path
import argparse, datetime, hashlib, json


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args()
    if args.salida.exists():
        raise FileExistsError(args.salida)
    p7 = Path(__file__).resolve().parents[1]
    corpus = p7.parent
    selected = [
        'PROGRESION_INTEGRADA_01/lecturas/CPC_Y_CAMPAÑAS/RECALCULO_DOCUMENTAL_AA33.json',
        'PROGRESION_INTEGRADA_02/lecturas/CONTRASTES/SINTESIS_Y_CONTROLES_PI02.md',
        'PROGRESION_INTEGRADA_02/lecturas/MECANISMOS/RESULTADO_CIENTIFICO_HABITAT_R04.md',
        'PROGRESION_INTEGRADA_03/lecturas/MATRIZ_MODALIDADES_Y_FALTANTES_PI03.json',
        'PROGRESION_INTEGRADA_03/lecturas/RECETA_O2_ACTUAL_PROPUESTA.json',
        'PROGRESION_INTEGRADA_03/lecturas/ANTECEDENTE_O2_RECALCULADO_PI03.json',
        'PROGRESION_INTEGRADA_03/lecturas/FUENTES_O2_APD01/actual/ruta_adquirida_apd_03.py',
        'PROGRESION_INTEGRADA_03/codigo/pi03_credito_generico_R01_BORRADOR.py',
        'PROGRESION_INTEGRADA_03/INFORME_CIENTIFICO_PI03.md',
        'PROGRESION_INTEGRADA_06/codigo/pi06_interrupcion_R02.py',
        'PROGRESION_INTEGRADA_06/control/RECALCULO_CAUSAL_INTERRUPCION_PI06_R02.json',
        'PROGRESION_INTEGRADA_06/fuentes/F1_COTA_CRISTALIZACION_PI06.json',
        'PROGRESION_INTEGRADA_06/fuentes/F1_TESTIGO_COPIA_Y_SUPERVIVENCIA_PI06.json',
    ]
    sources = []
    for rel in selected:
        path = corpus / rel
        data = path.read_bytes()
        sources.append({'relative_to_analisis_transversal': rel,
                        'absolute': str(path), 'bytes': len(data), 'sha256': sha(data),
                        'hash_scope': 'exact current bytes, not proof of complete semantic reading'})
    aa = json.loads((corpus / selected[0]).read_text(encoding='utf-8'))
    policies = []
    for row in aa['cases']:
        before, after = row['policy_first'], row['policy_second']
        policies.append({'case': row['case'], 'life': row['life'], 'prefix_tick': row['epoch'],
                         'member': row['member'], 'member_bytes': row['bytes'],
                         'member_sha256': row['sha256'],
                         'first': {k: before[k] for k in ['tick', 'site', 'raw', 'clock', 'direction']},
                         'second': {k: after[k] for k in ['tick', 'site', 'raw', 'clock', 'direction']},
                         'direction_changed': before['direction'] != after['direction'],
                         'current_requested': row['current_requested'],
                         'current_receipt_status': row['current_receipt_status'],
                         'missing_current_receipt_ids': row['missing_current_receipt_ids']})
    assert len(policies) == 14
    for row in policies:
        expected = not row['case'].endswith(('omit_feedback', 'unpaired'))
        assert row['direction_changed'] is expected, row['case']
    o2 = json.loads((corpus / selected[5]).read_text(encoding='utf-8'))
    o2_rows = {}
    for key in ('auxiliary_acquisition_controls', 'auxiliary_reversal_controls'):
        o2_rows[key] = [{k: row[k] for k in ('arm', 'routes', 'modelled_cost_total')}
                        for row in o2[key]]
    result = {
        'schema': 'DEE.PI07.F1.directed_documentary_crosscheck.v1',
        'inspection_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'new_Native_ticks': 0, 'DEE_imports': 0,
        'principal_modified': False,
        'scope': 'Recalculation of previously decoded selected policy fields and summary branches; not Native reproduction, not fresh full parsing of all historical primaries.',
        'sources': sources, 'AA33_policy_selected_fields': policies,
        'O2_selected_summary_fields': o2_rows,
        'O2_interpretation': o2['conclusion'],
        'new_PI07_design_status': 'PROPOSED_NOT_EXECUTED_NOT_VALIDATED',
        'script_sha256': sha(Path(__file__).read_bytes()),
    }
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'output': str(args.salida), 'bytes': args.salida.stat().st_size,
                      'sha256': sha(args.salida.read_bytes()), 'AA33_cases': len(policies),
                      'Native_ticks': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
