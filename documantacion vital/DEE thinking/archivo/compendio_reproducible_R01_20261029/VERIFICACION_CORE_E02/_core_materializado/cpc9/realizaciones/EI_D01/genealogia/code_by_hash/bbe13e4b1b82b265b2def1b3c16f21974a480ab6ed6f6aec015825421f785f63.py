"""Run guard-controlled reference-Y candidate."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src')]
import ejecutar_consulta_conservada as runner
from consulta_referencia_y_r1 import GuardedReferenceQuerySession
runner.PreservedQuerySession=GuardedReferenceQuerySession
if __name__=='__main__':runner.main()
