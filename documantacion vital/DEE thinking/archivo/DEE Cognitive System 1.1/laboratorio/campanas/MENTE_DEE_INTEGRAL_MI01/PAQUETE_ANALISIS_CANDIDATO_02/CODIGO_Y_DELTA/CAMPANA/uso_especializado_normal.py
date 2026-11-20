"""Operate a bounded specialization without promoting/replacing MAIN."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
life='MI01_ESPECIALIZACION_OPERATIVA_495';fork('MI01_CONTEXTO_B_344',life)
command('MI01_495_ESPECIALIZACION_CARGA',['mi01-estado','--vida',life])
command('MI01_496_ESPECIALIZACION_USO',['mi01-externo','--vida',life,'--pasos','2','--transicion','--codec-motor','signed_selector'],timeout=600)
command('MI01_497_ESPECIALIZACION_RECARGA',['mi01-estado','--vida',life])
command('MI01_498_ESPECIALIZACION_CONTINUA',['mi01-externo','--vida',life,'--pasos','1','--codec-motor','signed_selector'],timeout=600)
command('MI01_499_ESPECIALIZACION_ESTADO',['mi01-estado','--vida',life])
