"""Replay archivado convencional; no nueva ejecución, recursos ni Native."""
import argparse
import importlib.util
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();assert not a.out.exists()
    script=a.evidence/'ejecutar_recalcular_referencias_niveles_n0_r03.py'
    spec=importlib.util.spec_from_file_location('archived_conventional_references',script)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.dump(a.out,m.replay(a.evidence))


if __name__=='__main__':main()
