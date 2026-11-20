"""New identified technical branch after rejected duplicate-interface R1.
The failed R1 life, partial pending input and exact source remain preserved.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
name='C02_CAPAS_210_OPERATIVO_R2'
command('C02_CAPAS_210_FORK',['bifurcar','E1_INTEGRADO_CONTINUABLE_01',name,'--modalidad','CANDIDATE'])
p=command('C02_CAPAS_211_PREPARAR',['integrado-experiencia','--vida',name,'--tipo','acceso-previo','--parametros',json.dumps({'name':'CAPAS210','layers':2})])['result']
for index,t in enumerate((p['anchor_tick']+134,p['anchor_tick']+268)):
    command('C02_CAPAS_212_QUERY'+str(index),['integrado-experiencia','--vida',name,'--tipo','acceso-consultar','--parametros',json.dumps({'name':'CAPAS210_Q'+str(index),'query_tick':t,'scope':'base-and-first'})])
command('C02_CAPAS_213_AVANCE',['integrado-continuar','--vida',name,'--hasta',str(p['anchor_tick']+271)])
command('C02_CAPAS_214_USO',['integrado-externo','--vida',name,'--pasos','4'])
command('C02_CAPAS_215_GUARDAR',['guardar','--vida',name])
command('C02_CAPAS_216_RECARGA',['integrado-estado','--vida',name])
r=Store().record(name);other=Store().record('C02_REPET_190_DOS_CAPAS')
atomic_json(EV/'CAPAS_INCORPORACION_OPERATIVA_216.json',{'life':name,'tick':r['physical']['tick'],'snapshot':r['snapshot'],'sha256':r['snapshot_sha256'],
  'physical_equal_to_exploratory190':r['physical']['RAW_sha256']==other['physical']['RAW_sha256']and r['physical']['clocks_sha256']==other['physical']['clocks_sha256'],
  'scope':'Same manager, exact live parent, explicit finite anatomy and common queries; technical reproduction/admission, not independent learner or P2.',
  'previous_failed_life':'C02_CAPAS_200_OPERATIVO preserved at16485; no rollback or deletion of its partial pending request.'})
