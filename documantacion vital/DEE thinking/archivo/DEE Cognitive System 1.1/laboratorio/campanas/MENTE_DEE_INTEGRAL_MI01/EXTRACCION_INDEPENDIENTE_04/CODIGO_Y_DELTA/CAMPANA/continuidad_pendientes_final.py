"""Complete pending sensor work from the real post-free external action."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
command('MI01_437_MAIN_PROCESA_ENTRADA_POST_LIBRE',['mi01-vivir','--vida','E1_MI01_MAIN','--habitat','MI01_EVALUACION_FIJADA','--hasta','28169'],timeout=600)
command('MI01_438_MAIN_CORTE_CONTINUABLE',['mi01-estado','--vida','E1_MI01_MAIN'])
