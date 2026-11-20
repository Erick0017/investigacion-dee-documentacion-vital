"""One progressive world per history, not summed independent repertoires."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
for case,mode in [('KN_D02_K65','paired'),('KN_C03_K65_NO_EVENT','no_event'),('KN_C04_K65_UNPAIRED','unpaired'),('KN_R31_K65_OPPOSITE','opposite')]:
    command=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'tools/supervisor.py'),'--name',case,'--memory-mib','256','--timeout','240','--',sys.executable,'-I','-B','-X','utf8',str(ROOT/'src/ejecutar_repertorio_n67.py'),'--case',case,'--mode',mode,'--k','65','--out',str(ROOT/'resultados/repertorio_n67'/case)]
    result=subprocess.run(command,timeout=950)
    if result.returncode:raise SystemExit(result.returncode)
