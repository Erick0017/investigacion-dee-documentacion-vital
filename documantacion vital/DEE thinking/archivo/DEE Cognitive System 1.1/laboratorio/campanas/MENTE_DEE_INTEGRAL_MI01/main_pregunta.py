"""Actual new MAIN experiences and material question, no branch substitution."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
command('MI01_120_MAIN_RUTA',['mi01-experiencia','--vida','E1_MI01_MAIN','--tipo','adquirir-ruta','--parametros',json.dumps({'episode':'MI01_MAIN_CONSULTA_A','contexts':[-1,1],'feedback':'paired'})])
p=command('MI01_121_MAIN_PREGUNTA',['mi01-experiencia','--vida','E1_MI01_MAIN','--tipo','pregunta-material','--parametros',json.dumps({'name':'MI01_MAIN_QUERY_A','private_value':20})])
end=p['result']['end_tick']
command('MI01_122_MAIN_RESPUESTA',['mi01-continuar','--vida','E1_MI01_MAIN','--hasta',str(end)])
command('MI01_123_MAIN_USO_EXTERNO',['integrado-externo','--vida','E1_MI01_MAIN','--pasos','4'])
