"""Sequential independent checks; at most one native writer, no new manager."""
import sys,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
for filename in('uso_operativo_selector.py','relaciones_compuestas.py','recuerdo_para_continuar.py'):
    budget();print('EJECUCION_ACOTADA '+filename,flush=True)
    r=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(L/filename)],cwd=L)
    if r.returncode:raise RuntimeError('Preserved failure, no automatic repeat: '+filename)
