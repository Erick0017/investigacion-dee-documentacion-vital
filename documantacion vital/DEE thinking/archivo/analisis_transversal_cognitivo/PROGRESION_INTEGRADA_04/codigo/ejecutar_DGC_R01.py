from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from servicio_ensayo_R02 import Owner
for suffix,mode in [('FULL01','full'),('COMPACT01','compact')]:
 life='ECI02_PI03_REPRO_PI04_C2CPASS_'+suffix;identifier='PI04_DGC_'+suffix
 with Owner(life,identifier)as owner:
  actual=owner.material(identifier,{'modo':'eci01-pi04-dgc-campo','condicion':'single','registro':mode},feedback='omit')
  owner.control('guardar')
 print(json.dumps({'id':identifier,'after_tick':actual['after_tick']}),flush=True)
