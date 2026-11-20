"""Frozen independent-history controls and complete held-out combinations."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
cases=[('EI_C01_NO_COUNT_FORM',['--count-form','omitted']),('EI_C02_QUERY_KNOWN',['--query-local','known']),
       ('EI_C03_NO_ORDER_A',['--tile-omit','A']),('EI_C04_NO_TM_R',['--two-omit','R']),
       ('EI_C05_RCA_OFFPATH',['--regulation','offpath']),
       ('EI_R31_REVERSED_COMBINATION',['--tile-order','BA','--tile-interval','3','--source','17','--first-object','27','--two-reference','11','--two-object','31','--contact-medium','3']),
       ('EI_R32_NEW_COMBINATION',['--tile-order','AB','--tile-interval','1','--tile-a-load','13','--tile-b-load','17','--query-delay','2','--query-remote-load','17','--contact-medium','3','--two-reference','23','--two-object','41'])]
for case,options in cases:
    command=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'tools/supervisor.py'),'--name',case,'--memory-mib','512','--timeout','300','--',sys.executable,'-I','-B','-X','utf8',str(ROOT/'src/ejecutar_vida_integral.py'),'--case',case,'--out',str(ROOT/'resultados/vida_integral'/case),*options]
    result=subprocess.run(command,timeout=1000)
    if result.returncode:raise SystemExit(result.returncode)
