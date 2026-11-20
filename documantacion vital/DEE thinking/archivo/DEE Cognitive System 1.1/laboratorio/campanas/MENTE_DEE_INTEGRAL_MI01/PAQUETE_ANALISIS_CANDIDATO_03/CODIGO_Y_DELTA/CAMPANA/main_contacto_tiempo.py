"""Actual MAIN acquisition and novel combination through the SAME manager."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
rows=[('MI01_310_MAIN_CONTACTO_PREP','espanol-contacto-preparar',{'frame':'MI01_MAIN_C','base':[28,34,54]}),('MI01_311_MAIN_CONTACTO','espanol-contacto-ensenar',{'frame':'MI01_MAIN_C','present':True,'medium':3,'signal':True}),('MI01_312_MAIN_TIEMPO_PREP','espanol-tiempo-preparar',{'frame':'MI01_MAIN_T','origin':[5,32,28]}),('MI01_313_MAIN_TIEMPO','espanol-tiempo-ensenar',{'frame':'MI01_MAIN_T','order':'AB','interval':3,'event_b':True,'signal':True}),('MI01_314_MAIN_COMBINACION','espanol-componer',{'contact_frame':'MI01_MAIN_C','temporal_frame':'MI01_MAIN_T'})]
for id,kind,options in rows:command(id,['experiencia','--vida','E1_MI01_MAIN',kind,'--parametros',json.dumps(options)])
command('MI01_315_MAIN_RETENCION_EXTERNA',['integrado-externo','--vida','E1_MI01_MAIN','--pasos','2'])
