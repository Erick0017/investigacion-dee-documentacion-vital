"""Actual MAIN uses its own acquired message, no new teacher or memory copy."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
command('MI01_320_MAIN_REUSO_PREP',['mi01-experiencia','--vida','E1_MI01_MAIN','--tipo','reusar-contenido','--parametros',json.dumps({'name':'MI01_MAIN_REUSO','mode':'intact','common':False})])
command('MI01_321_MAIN_REUSO',['mi01-reusar','--vida','E1_MI01_MAIN','--nombre','MI01_MAIN_REUSO'])
command('MI01_322_MAIN_ESTADO',['mi01-estado','--vida','E1_MI01_MAIN'])
