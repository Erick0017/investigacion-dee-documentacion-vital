"""New reserves after local causal explanation of the two old load failures."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
for case,value,obj in [('RET_V3_R31_SOURCE23_OBJECT16',23,16),('RET_V3_R32_SOURCE23_OBJECT35',23,35)]:
    command=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'tools/supervisor.py'),'--name',case+'_ARGFIX1','--memory-mib','512','--timeout','180','--',sys.executable,'-I','-B','-X','utf8',str(ROOT/'src/ejecutar_retorno.py'),'--case',case,'--source',str(value),'--first-object',str(obj),'--out',str(ROOT/'resultados/retorno'/case)]
    result=subprocess.run(command,timeout=850)
    if result.returncode:raise SystemExit(result.returncode)
