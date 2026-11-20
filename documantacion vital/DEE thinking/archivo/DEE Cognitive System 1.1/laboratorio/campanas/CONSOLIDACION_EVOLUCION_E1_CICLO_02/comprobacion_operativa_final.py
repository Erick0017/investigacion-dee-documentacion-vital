"""New interactions on admitted current lives, no protected-state queries."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
for base,name in((320,'E1_CICLO02_RETENCION_01'),(323,'E1_CICLO02_COMUNICACION_01'),(326,'E1_CICLO02_LATERAL_LOCAL_01')):
    command('C02_FINAL_'+str(base)+'_USO',['integrado-externo','--vida',name,'--pasos','1'])
    command('C02_FINAL_'+str(base+1)+'_GUARDAR',['guardar','--vida',name])
    command('C02_FINAL_'+str(base+2)+'_RECARGA',['integrado-estado','--vida',name])
atomic_json(EV/'COMPROBACION_OPERATIVA_FINAL_328.json',{'lives':[{k:Store().record(name)[k]for k in('life_id','physical','snapshot','snapshot_sha256')}for name in('E1_CICLO02_MAIN','E1_CICLO02_RETENCION_01','E1_CICLO02_COMUNICACION_01','E1_CICLO02_LATERAL_LOCAL_01','C02_CAPAS_210_OPERATIVO_R2')],
 'active':Store().record()['life_id'],'scope':'Actual newly reached snapshots, not maxima, no global promotion.'})
