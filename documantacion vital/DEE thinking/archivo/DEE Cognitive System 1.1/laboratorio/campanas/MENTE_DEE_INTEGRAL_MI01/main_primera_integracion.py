"""Real MAIN continuation through installed manager, no successful-state import."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
command('MI01_100_MAIN_COMPOSICION',['mi01-experiencia','--vida','E1_MI01_MAIN','--tipo','componer','--parametros',json.dumps({'episode':'MI01_MAIN_A','availability':[1,-1],'contents':[-1,1],'feedback':'paired'})])
command('MI01_101_MAIN_ESTADO',['mi01-estado','--vida','E1_MI01_MAIN'])
command('MI01_102_MAIN_EXTERNO',['integrado-externo','--vida','E1_MI01_MAIN','--pasos','4'])
command('MI01_103_MAIN_COMPOSICION_NUEVA',['mi01-experiencia','--vida','E1_MI01_MAIN','--tipo','componer','--parametros',json.dumps({'episode':'MI01_MAIN_B','availability':[-1,1],'contents':[1,-1],'feedback':'paired'})])
command('MI01_104_MAIN_EXTERNO',['integrado-externo','--vida','E1_MI01_MAIN','--pasos','4'])
