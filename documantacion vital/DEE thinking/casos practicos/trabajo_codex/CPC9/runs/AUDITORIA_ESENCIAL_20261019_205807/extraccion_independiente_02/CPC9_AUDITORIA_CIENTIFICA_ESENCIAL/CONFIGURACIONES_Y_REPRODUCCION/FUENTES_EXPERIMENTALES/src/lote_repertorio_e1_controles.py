"""Matched original1907 counterfactuals; never write an answer back to MAIN."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def main():
    for name,flag in(('E1_CF_K65_NO_EVENT','--omit-events'),('E1_CF_K65_UNPAIRED','--unpaired')):
        command=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'tools/supervisor.py'),'--name',name,'--memory-mib','256','--timeout','300','--',sys.executable,'-I','-B','-X','utf8',str(ROOT/'src/continuar_repertorio_e1.py'),
          '--parent',str(ROOT/'front_relations/resultados/E1_MAIN_1639_1907/T1907.deetsnap.gz'),'--case',name,'--out',str(ROOT/'resultados/continuacion'/name),flag]
        subprocess.run(command,check=True)
if __name__=='__main__':main()
