from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from servicio_ensayo_R02 import Owner
P=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('--vida',required=True);p.add_argument('--condicion',choices=['single','symmetric'],required=True);p.add_argument('--registro',choices=['full','compact'],required=True);p.add_argument('--id',required=True);a=p.parse_args()
with Owner(a.vida,a.id)as owner:
    result=owner.material(a.id,{'modo':'eci01-pi04-dg-campo','condicion':a.condicion,'registro':a.registro},feedback='omit')
    saved=owner.control('guardar')
print(json.dumps({'id':a.id,'after_tick':result['after_tick'],'record':str(P/'ensayos'/(a.id+'.json'))}))
