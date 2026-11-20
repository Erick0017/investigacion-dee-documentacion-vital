"""Explicit discovery controls of the fixed repair1 apparatus."""
from pathlib import Path
import subprocess,sys,json
ROOT=Path(__file__).resolve().parents[1]
cases=[('QP_R1_D02_LOCAL','known','known',0,11),('QP_R1_D03_BLANK','blank','known',0,11),
       ('QP_R1_C04_NOB','blank','unknown',0,11),('QP_R1_C05_WRONG','blank','wrong',0,11),
       ('QP_R1_C06_UNPAIRED','blank','unpaired',0,11)]
for case,local,remote,delay,load in cases:
    command=[sys.executable,'-I','-B','-X','utf8',str(ROOT/'tools/supervisor.py'),'--name',case,'--timeout','180','--',sys.executable,'-I','-B','-X','utf8',str(ROOT/'src/ejecutar_consulta_r1.py'),'--case',case,'--local',local,'--remote',remote,'--delay',str(delay),'--remote-load',str(load),'--out',str(ROOT/'resultados/consulta_conservada'/case)]
    result=subprocess.run(command,timeout=800)
    if result.returncode:raise SystemExit(result.returncode)
