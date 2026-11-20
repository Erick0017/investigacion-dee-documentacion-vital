"""Fixed-counterflow query candidate, native state never read to schedule."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src')]
import ejecutar_consulta_conservada as runner
from consulta_referencia_y_r2 import CounterflowReferenceQuerySession
runner.PreservedQuerySession=CounterflowReferenceQuerySession
if __name__=='__main__':runner.main()
