"""Continue after the zero-tick external permission-contract error, not replay."""
import sys,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
for filename in('uso_operativo_selector.py','recuerdo_para_continuar.py','diagnostico_consulta_fallo.py'):
    budget();print('EJECUCION_ACOTADA '+filename,flush=True)
    r=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(L/filename)],cwd=L)
    if r.returncode:raise RuntimeError('Preserved new failure, no automatic repetition: '+filename)
