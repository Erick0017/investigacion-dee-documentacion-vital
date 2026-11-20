import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
for case in ['C02_SOCIAL_012_RUTA_MINUS','C02_SOCIAL_013_RUTA_PLUS','C02_SOCIAL_014_RUTA_SIN_B']:
    command(case+'_USO',['integrado-externo','--vida',case,'--pasos','2','--reiniciar-entorno','--semilla','82021'])
    command(case+'_RECARGA',['integrado-estado','--vida',case])
