"""Sólo adapta salida a archivo del recálculo archivado R03, sin Native."""
import argparse
import importlib.util
from pathlib import Path

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidence', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    script = a.evidence / 'exportar_y_recalcular_wait_r03_post10_n0_r01.py'
    spec = importlib.util.spec_from_file_location('archived_wait_recalculate_only', script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.emit(a.out, module.recalculate(a.evidence))
