import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    for parent in('PT_P01_TWO','PT_P02_ONE_A','PT_P04_NONE'):
        for mode in('cut','sham','restore'):
            subprocess.run([sys.executable,'-I','-B',str(ROOT/'check_presence_remote.py'),'--parent',str(ROOT/'resultados/PRESENCE_REMOTE_V3'/parent),'--out',str(a.out/(parent+'_'+mode.upper())),'--mode',mode],check=True,timeout=180)
