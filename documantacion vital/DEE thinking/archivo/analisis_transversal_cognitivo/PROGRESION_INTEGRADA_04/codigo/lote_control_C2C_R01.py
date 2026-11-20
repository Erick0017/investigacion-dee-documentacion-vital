"""One explicit control per invocation; Native subprocesses always sequential."""
from pathlib import Path
import argparse,subprocess
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';PY=C/'motor/python313/python.exe';code=P/'codigo'
p=argparse.ArgumentParser();p.add_argument('--brazo',choices=['none','yoked','context_cut','link_cut'],required=True);a=p.parse_args()
settings={'none':('C2C_NONE_01','PI03_PI04_C2B_STOP_T800379',20,'PI04_C2C_NONE20_R01'),
 'yoked':('C2C_YOKE_01','PI03_PI04_C2B_STOP_T800379',20,'PI04_C2C_YOKE20_R01'),
 'context_cut':('C2C_CTX_CUT_01','PI03_PI04_C2C_POST_DEV_T809763',16,'PI04_C2C_CTX_CUT4_R01'),
 'link_cut':('C2C_LINK_CUT_01','PI03_PI04_C2B_STOP_T800379',1,'PI04_C2C_LINK_CUT1_R01')}
suffix,alias,end,tag=settings[a.brazo];life='ECI02_PI03_REPRO_PI04_'+suffix
base=[str(PY),'-I','-B','-X','utf8']
subprocess.run(base+[str(code/'clonar_PI04_R02.py'),'--par',str(C/'reproducibilidad/materiales'/alias),'--vida',life],check=True)
cmd=base+[str(code/'ejecutar_C2C_R01.py'),'--vida',life,'--brazo',a.brazo,'--hasta',str(end),'--tag',tag]
if a.brazo=='context_cut':cmd+=['--cortar-contexto']
else:cmd+=['--preparar','--admitir']
if a.brazo=='yoked':cmd+=['--plan',str(P/'control/PLAN_C2C_YOKE20_R01.json')]
subprocess.run(cmd,check=True)
