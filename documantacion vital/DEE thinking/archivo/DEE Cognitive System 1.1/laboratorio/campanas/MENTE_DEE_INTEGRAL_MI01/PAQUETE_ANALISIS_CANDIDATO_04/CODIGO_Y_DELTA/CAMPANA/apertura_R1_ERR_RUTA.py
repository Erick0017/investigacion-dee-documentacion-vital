"""Small actual inherited-use window, not the historical family suite."""
from comun import *
fork('E1_CICLO02_SEPARACION_TRIPLE_01','MI01_BASE_001')
command('MI01_001_BASE_EXTERNO',['integrado-externo','--vida','MI01_BASE_001','--pasos','1'])
command('MI01_002_MAIN_EXTERNO',['integrado-externo','--vida','E1_MI01_MAIN','--pasos','1'])
command('MI01_003_MAIN_RECARGA',['integrado-estado','--vida','E1_MI01_MAIN'])
command('MI01_004_BASE_PANEL',['integrado-panel','--vida','MI01_BASE_001','--breve'])
