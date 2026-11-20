import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    for mode in('cut_A','cut_B','cut_both','sham','restore'):
        subprocess.run([sys.executable,'-I','-B',str(ROOT/'check_presence_count.py'),'--parent',str(ROOT/'resultados/PRESENCE_COUNT_V3/PQ_P01_TWO_DOSE3_5'),
                        '--out',str(a.out/mode.upper()),'--mode',mode],check=True,timeout=180)
