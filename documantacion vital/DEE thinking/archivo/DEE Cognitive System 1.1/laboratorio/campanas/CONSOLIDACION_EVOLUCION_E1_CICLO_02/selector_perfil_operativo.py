import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
s=Store();old=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
source=json.loads((old/'MAIN_OWN_ACQUISITION_37.json').read_text(encoding='utf8'))['INSTRUMENTO']['snapshot_sha256']
path=next(p for p in(s.root/'estado/checkpoints').glob('E1_INTEGRADO_MAIN.T3312.*')if digest_file(p)==source)
command('C02_SELECTOR_151_CONSERVAR',['bifurcar','E1_INTEGRADO_MAIN','E1_SELECTOR_CONSERVADO_C02','--modalidad','CANDIDATE','--checkpoint-relativo',str(path.relative_to(s.root))])
command('C02_SELECTOR_152_COPIA_USO',['bifurcar','E1_SELECTOR_CONSERVADO_C02','C02_SELECTOR_USO_151','--modalidad','DIAGNOSTIC_COPY'])
p=command('C02_SELECTOR_153_PROGRAMAR',['integrado-experiencia','--vida','C02_SELECTOR_USO_151','--tipo','programar','--parametros',json.dumps({'name':'C02_SELECTOR_USE','contexts':[1],'shunt':'a_only'})])
command('C02_SELECTOR_154_USO',['integrado-continuar','--vida','C02_SELECTOR_USO_151','--hasta',str(p['result']['end_tick'])])
command('C02_SELECTOR_155_GUARDAR',['guardar','--vida','C02_SELECTOR_USO_151'])
command('C02_SELECTOR_156_RECARGA',['integrado-estado','--vida','C02_SELECTOR_USO_151'])
atomic_json(EV/'SELECTOR_CONSERVACION_OPERATIVA.json',{'preserved_learned_source':s.record('E1_SELECTOR_CONSERVADO_C02'),
    'actual_use_life':s.record('C02_SELECTOR_USO_151'),'historical_exhausted_life':s.record('IC01_SISTEMA_NATIVO_163')['physical'],
    'no_new_learning_claim':'Exact lived fork fromT3312; one brief ordinary operational use, not a repeat of IC01 scientific suites and not learning imported into MAIN.',
    'no_default_promotion':True})
