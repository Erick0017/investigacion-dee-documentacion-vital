"""Run final repair as a separate life, keeping original measurements intact."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src')]
import ejecutar_consulta_conservada as runner
from consulta_conservada_r2 import PreservedQueryR2Session
runner.PreservedQuerySession=PreservedQueryR2Session
if __name__=='__main__':runner.main()
