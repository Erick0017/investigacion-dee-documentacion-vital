from pathlib import Path
import subprocess
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';PY=C/'motor/python313/python.exe'
for suffix in('FULL01','COMPACT01'):
 life='ECI02_PI03_REPRO_PI04_C2CPASS_'+suffix
 subprocess.run([str(PY),'-I','-B','-X','utf8',str(P/'codigo/clonar_PI04_R02.py'),'--par',str(C/'reproducibilidad/materiales/PI03_PI04_C2B_STOP_T800379'),'--vida',life],check=True)
