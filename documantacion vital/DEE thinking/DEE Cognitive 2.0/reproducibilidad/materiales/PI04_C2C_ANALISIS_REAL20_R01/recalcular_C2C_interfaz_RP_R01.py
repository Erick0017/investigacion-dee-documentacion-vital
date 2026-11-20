"""Thin stdlib adapter for the preserved C2C documentary recalculation.

Only reads an explicit evidence directory and writes an explicit NEW output.
It does not import DEE, open a world, send a query or change recipe criteria.
"""
from pathlib import Path
import argparse
import runpy
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--out-dir', type=Path, required=True)
    args = ap.parse_args()
    root = args.root.resolve(strict=True)
    dest = args.out_dir.resolve()
    if not root.is_dir() or root.is_symlink():
        raise ValueError('An explicit regular evidence directory is required')
    if dest.exists() or dest == root or dest.is_relative_to(root):
        raise ValueError('Output must be a NEW directory outside the evidence')
    script = root / 'RECALCULAR_C2C_R01.py'
    if not script.is_file() or script.is_symlink():
        raise ValueError('The exact preserved documentary script is required')
    before = list(sys.argv)
    try:
        sys.argv = [str(script), 'recalculate', '--evidence', str(root), '--out', str(dest)]
        runpy.run_path(str(script), run_name='__main__')
    finally:
        sys.argv = before


if __name__ == '__main__':
    main()
