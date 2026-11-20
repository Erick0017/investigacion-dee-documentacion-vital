"""Each continuation uses another interpreter; bounded by outer supervisor."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    a.out.mkdir(exist_ok=False)
    for parent in ('CB_P01_TWO', 'CB_P03_ONE_B'):
        for mode in ('cut', 'sham', 'restore'):
            subprocess.run([sys.executable, '-I', '-B', str(ROOT / 'check_count_access.py'),
                '--parent', str(ROOT / 'resultados/COUNT_ACCESS_V2' / parent),
                '--out', str(a.out / (parent + '_' + mode.upper())), '--mode', mode], check=True, timeout=180)
