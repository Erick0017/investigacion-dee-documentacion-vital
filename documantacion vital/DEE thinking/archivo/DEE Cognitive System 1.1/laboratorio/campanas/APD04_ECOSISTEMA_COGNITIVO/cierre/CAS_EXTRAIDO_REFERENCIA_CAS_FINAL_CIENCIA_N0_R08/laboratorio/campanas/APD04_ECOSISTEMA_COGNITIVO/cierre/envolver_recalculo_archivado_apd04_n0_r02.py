"""Adapta dos calculadores cerrados a salida JSON, sin Runtime ni nuevos ticks."""
import argparse
import importlib.util
from pathlib import Path

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidence',type=Path,required=True)
    p.add_argument('--script',choices=['exportar_y_recalcular_wait_r03_post10_n0_r01.py','dossier_primera_divergencia_wait_r03_n0_r01.py'],required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    spec=importlib.util.spec_from_file_location('archived_recalculation_only',a.evidence/a.script)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.emit(a.out,m.recalculate(a.evidence))
