"""Install the bounded validated opportunities on MAIN, not a copied future."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
command('MI01_190_MAIN_EXTENSION',['mi01-experiencia','--vida','E1_MI01_MAIN','--tipo','adquirir-ruta','--parametros',json.dumps({'episode':'MI01_MAIN_EXTENSION','contexts':[-1,1],'feedback':'paired','center':[40,35,55]})])
p=command('MI01_191_MAIN_PROTEGIDA',['mi01-experiencia','--vida','E1_MI01_MAIN','--tipo','pregunta-material','--parametros',json.dumps({'name':'MI01_MAIN_PROTEGIDA','private_value':20,'reader_guard':True,'late_protection':'full'})])
command('MI01_192_MAIN_RECIBE',['mi01-continuar','--vida','E1_MI01_MAIN','--hasta',str(p['result']['end_tick'])])
command('MI01_193_MAIN_UTILIZA',['integrado-externo','--vida','E1_MI01_MAIN','--pasos','4'])
