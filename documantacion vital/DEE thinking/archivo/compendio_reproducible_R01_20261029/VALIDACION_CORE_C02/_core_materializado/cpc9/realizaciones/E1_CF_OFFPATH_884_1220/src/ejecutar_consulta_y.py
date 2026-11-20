"""Run reference-Y candidate in a fresh physical world."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src')]
import ejecutar_consulta_conservada as runner
from consulta_referencia_y import ReferenceQuerySession
runner.PreservedQuerySession=ReferenceQuerySession
if __name__=='__main__':runner.main()
