"""Causal contrasts and timing/dose reserves for the original finite query."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
cases=[('QA_C02_LOCAL_KNOWN','known','known',0,11),('QA_C03_REMOTE_ABSENT','unknown','unknown',0,11),
       ('QA_C04_WRONG_CONTENT','unknown','wrong',0,11),('QA_C05_UNPAIRED_B','unknown','unpaired',0,11),
       ('QA_C06_UNPAIRED_LOCAL','unpaired','known',0,11),('QA_R31_DELAY2_DOSE17','unknown','known',2,17),
       ('QA_R32_DELAY5_DOSE23','unknown','known',5,23)]
for case,local,remote,delay,load in cases:
    command=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'tools/supervisor.py'),'--name',case,'--timeout','180','--',sys.executable,'-I','-B','-X','utf8',str(ROOT/'src/ejecutar_consulta.py'),'--case',case,'--local',local,'--remote',remote,'--delay',str(delay),'--remote-load',str(load),'--out',str(ROOT/'resultados/consulta'/case)]
    result=subprocess.run(command,timeout=800)
    if result.returncode:raise SystemExit(result.returncode)
