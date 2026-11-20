"""Brief true manager load/use/save/reload of the admitted acquired decision."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
fork('MI01_OPERATIVO_250_plus','MI01_OPERATIVO_252_plus')
fork('MI01_OPERATIVO_251_minus','MI01_OPERATIVO_253_minus')
for number,life in [(252,'MI01_OPERATIVO_252_plus'),(253,'MI01_OPERATIVO_253_minus')]:
    command('MI01_'+str(number)+'_MOTOR',['mi01-externo','--vida',life,'--pasos','3','--transicion'])
    command('MI01_'+str(number)+'_RECARGA',['mi01-estado','--vida',life])
    command('MI01_'+str(number)+'_CONTINUA',['mi01-externo','--vida',life,'--pasos','1'])
