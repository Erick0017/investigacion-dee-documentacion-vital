"""Comprobación de utilización real entre procesos, no repetición científica."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
s=Store();parent=s.record('E1_INTEGRADO_RECUPERACION_01')
fork('E1_INTEGRADO_RECUPERACION_01','E1_CICLO02_MAIN',kind='CANDIDATE')
command('C02_001_CARGA_MAIN',['integrado-estado','--vida','E1_CICLO02_MAIN'])
command('C02_002_USO_Y_GUARDADO',['integrado-externo','--vida','E1_CICLO02_MAIN','--pasos','1'])
command('C02_003_RECARGA',['integrado-estado','--vida','E1_CICLO02_MAIN'])
command('C02_004_CONTINUACION',['integrado-externo','--vida','E1_CICLO02_MAIN','--pasos','1'])
atomic_json(EV/'C02_ADMISION_OPERATIVA_IC01.json',{
    'scope':'Load/use/save/reload/continue in separate ordinary fenced manager processes. Not a repeat of causal IC01 campaigns.',
    'parent':parent,'main':s.record('E1_CICLO02_MAIN'),'active':s.record(),
    'capabilities_admitted':['IC01_DECISION_NATIVA_POR_CONSECUENCIAS','IC01_REFERENCIA_ADQUIRIDA_DE_CONSECUENCIA_REAL','IC01_RELACION_SOCIAL_RETENIDA_Y_ACTUALIZADA','IC01_RECUPERACION_SOCIAL_GENERICA_PREPARADA','IC01_PUENTE_INTEGRADO_Y_CONTINUIDAD'],
    'native_selector':'Executable finite profile; NOT current usable knowledge of this MAIN',
    'generic_recovery':'Assisted P0/R0, original causal controls reused, current parallel readout actually used',
    'main_scope':'Acquired quantity reference and recovered social content used together in fixed external actuator. No competent Pendulum policy claim.'})
