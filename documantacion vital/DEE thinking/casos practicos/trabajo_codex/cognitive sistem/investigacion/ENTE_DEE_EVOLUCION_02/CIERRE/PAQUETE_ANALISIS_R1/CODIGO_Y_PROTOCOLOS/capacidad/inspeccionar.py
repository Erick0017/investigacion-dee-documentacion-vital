"""Passive zero-tick geometric inspection, not participant memory."""
from pathlib import Path
import json,sys,hashlib
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store
from capacidades import arquitectura_distribuida_mi02_r8 as body
from app.native_tools import atomic_json,physical

def main():
    store=Store();rec,a=store.load('EO01_MAIN')
    before=physical(a.world);N=int(a.world.runtime.dimension)
    sensors=body.get(a)['external_sensors'];rows=[]
    for s in sensors:
        centers=[s['origin'],s['target']]
        for c in centers:
            neighbors=[]
            for x in(-1,0,1):
                for y in(-1,0,1):
                    for z in(-1,0,1):
                        if(x,y,z)==(0,0,0):continue
                        q=body.obs(a,body.xyz(a,c,(x,y,z)))
                        neighbors.append({'offset':[x,y,z],**q})
            rows.append({'sensor':s['name'],'center':c,'record':body.obs(a,c),'neighbors':neighbors})
    out={'source_life':rec['life_id'],'snapshot':rec['snapshot'],'snapshot_sha256':rec['snapshot_sha256'],
         'before':before,'sensors':sensors,'regions':rows,'after':physical(a.world),'new_ticks':0}
    path=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02/capacidad/INSPECCION_0_TICKS.json'
    atomic_json(path,out)
    print(json.dumps({'path':str(path),'sensors':sensors,'unchanged':out['before']==out['after'],
      'empty_neighbors':[{'sensor':r['sensor'],'center':r['center'],'raw_empty':[q['offset']for q in r['neighbors']if int(q['raw'])==0]}for r in rows]},ensure_ascii=False))
if __name__=='__main__':main()
