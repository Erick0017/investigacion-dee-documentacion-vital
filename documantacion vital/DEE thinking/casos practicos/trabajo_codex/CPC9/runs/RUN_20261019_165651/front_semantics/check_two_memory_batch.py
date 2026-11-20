"""New interpreter for every causal fork/continuation, bounded by supervisor."""
import argparse
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(exist_ok=False)
    for name,operand in(('TM_H01_R29_O17','R'),('TM_H02_R17_O29','O')):
        for mode in('cut','sham','restore'):
            subprocess.run([sys.executable,'-I','-B',str(ROOT/'check_two_memory.py'),'--parent',str(ROOT/'resultados/TWO_MEMORY_CONFIRMATORY'/name),
                '--out',str(a.out/(name+'_'+operand+'_'+mode.upper())),'--mode',mode,'--operand',operand],check=True,timeout=180)
