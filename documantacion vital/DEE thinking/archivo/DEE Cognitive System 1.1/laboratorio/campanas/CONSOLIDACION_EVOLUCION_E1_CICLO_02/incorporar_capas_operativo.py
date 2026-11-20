"""Brief normal-manager use of the admitted two-layer mechanism.
Not an independent scientific replicate of the deterministic parent history.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
name='C02_CAPAS_200_OPERATIVO'
command('C02_CAPAS_200_FORK',['bifurcar','E1_INTEGRADO_CONTINUABLE_01',name,'--modalidad','CANDIDATE'])
p=command('C02_CAPAS_201_PREPARAR',['integrado-experiencia','--vida',name,'--tipo','acceso-previo','--parametros',json.dumps({'name':'CAPAS200','layers':2})])['result']
for index,t in enumerate((p['anchor_tick']+134,p['anchor_tick']+268)):
    command('C02_CAPAS_202_QUERY'+str(index),['integrado-experiencia','--vida',name,'--tipo','acceso-consultar','--parametros',json.dumps({'name':'CAPAS200_Q'+str(index),'query_tick':t,'scope':'base-and-first'})])
command('C02_CAPAS_203_AVANCE',['integrado-continuar','--vida',name,'--hasta',str(p['anchor_tick']+271)])
command('C02_CAPAS_204_USO',['integrado-externo','--vida',name,'--pasos','4'])
command('C02_CAPAS_205_GUARDAR',['guardar','--vida',name])
command('C02_CAPAS_206_RECARGA',['integrado-estado','--vida',name])
r=Store().record(name);other=Store().record('C02_REPET_190_DOS_CAPAS')
atomic_json(EV/'CAPAS_INCORPORACION_OPERATIVA_206.json',{'life':name,'tick':r['physical']['tick'],'snapshot':r['snapshot'],'sha256':r['snapshot_sha256'],
  'physical_equal_to_exploratory190':r['physical']['RAW_sha256']==other['physical']['RAW_sha256']and r['physical']['clocks_sha256']==other['physical']['clocks_sha256'],
  'scope':'Same manager, exact live parent, explicit prepared finite anatomy and common queries; technical reproduction/admission, not new independent learner or P2.'})
