import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
d=command('C02_SELECTOR_150_ESTADO',['integrado-estado','--vida','IC01_SISTEMA_NATIVO_163'])
print(json.dumps(d['body'],ensure_ascii=False))
