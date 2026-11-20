"""Execute ONE identified initial preparation from a frozen public configuration.

The outer process is the experimental generator. The physical participant is the
same native Session throughout; no terminal result, target or old snapshot is read.
"""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import put, sha
import residue_regulation


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--case-id', required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    configuration = json.loads(a.config.read_text(encoding='utf-8'))
    cases = [c for c in configuration['cases'] if c['id'] == a.case_id]
    if len(cases) != 1:
        raise ValueError('Se requiere un ID único en la configuración')
    case = cases[0]
    if case.get('parent_id'):
        raise ValueError('Esta entrada pública crea una preparación nueva; los forks históricos no se recrean silenciosamente')
    if len(case['bank_values']) != 16:
        raise ValueError('El contrato público requiere exactamente 16 valores; los intentos históricos no conformes permanecen en la evidencia')
    m = residue_regulation.execute_guarded(case, a.out.resolve(), sha(a.config))
    checks = {'schema': 'CPC7.public-case.checks.v1', 'case_id': case['id'],
              'native_questions': len(m['native_questions']),
              'native_information': len(m['native_selected_information']),
              'native_actions': len(m['native_actions']),
              'opaque_covered': m['calculations']['opaque_covered'],
              'lower': m['calculations']['lower_repertoire'],
              'same_runtime': m['same_RUNTIME_after_boundary'],
              'host_RAW_clock_writes_on_MAIN': m['host_RAW_clock_writes_on_MAIN'],
              'primary_sha256': sha(a.out / 'MEASUREMENTS.json'),
              'scope': 'Cálculos de auditor posteriores a la trayectoria, nunca devueltos al participante.'}
    put(a.out / 'CHECKS.json', checks)


if __name__ == '__main__':
    main()
