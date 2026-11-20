"""Run repair1 as a separate identified preparation; original attempt retained."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src')]
import ejecutar_consulta_conservada as runner
from consulta_conservada_r1 import PreservedQueryR1Session
runner.PreservedQuerySession=PreservedQueryR1Session
if __name__=='__main__':runner.main()
