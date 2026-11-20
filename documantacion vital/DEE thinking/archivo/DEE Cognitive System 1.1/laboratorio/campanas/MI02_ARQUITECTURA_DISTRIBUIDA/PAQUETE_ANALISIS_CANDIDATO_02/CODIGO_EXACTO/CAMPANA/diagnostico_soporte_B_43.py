"""Saved-state neighbourhood calculation only. No Runtime instantiation/ticks."""
import json,hashlib,importlib.util
from pathlib import Path
L=Path(__file__).resolve().parent;R=L.parents[2];S=R/'sistema';E=R/'evidencia/campanas/MI02_ARQUITECTURA_DISTRIBUIDA'
spec=importlib.util.spec_from_file_location('obs',S/'capacidades/observador_causal_retrospectivo_01.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows=[]
for life,recipe in[('MI02_SOCIAL_EFIMERO_220','MI02_SOCIAL_EFIMERO_220.RECETA_T0.json'),('MI02_SOCIAL_NEUTRO_230','MI02_SOCIAL_NEUTRO_230.RECETA_T0.json')]:
    rec=json.loads((S/'estado/vidas'/life/'VIDA.json').read_bytes());x=m.Snapshot(S/rec['snapshot']);g=json.loads((E/recipe).read_bytes())['geometry'];B=g['B'];near=[]
    initial=m.Snapshot(E/(life+'.PREPARACION_T0.deetsnap.gz'))
    for dx in(-1,0,1):
        for dy in(-1,0,1):
            for dz in(-1,0,1):
                if(dx,dy,dz)==(0,0,0):continue
                p=[(B[i]+(dx,dy,dz)[i])%x.N for i in range(3)];before=initial.observation(p);after=x.observation(p)
                near.append({'offset':[dx,dy,dz],'initial':before,'final':after,'newly_alive_from_initial_state0':before['state']==0 and after['state']>0})
    rows.append({'life':life,'snapshot':rec['snapshot'],'snapshot_sha256':rec['snapshot_sha256'],'tick':x.tick,'reader':x.observation(B),'initially_alive_neighbours':sum(v['initial']['state']>0 for v in near),'currently_alive_neighbours':sum(v['final']['state']>0 for v in near),'newly_alive_neighbours':sum(v['newly_alive_from_initial_state0']for v in near),'neighbours':near,'initial_includes_no_acquired_private_fields':True})
out={'scope':'Saved-state calculation only. New alive sites are not assigned a unique lineage from payload coincidence. The comparison localizes the failed five-neighbour assumption; causal resolution uses later separately declared new preparations.','native_ticks':0,'rows':rows}
(E/'DIAGNOSTICO_SOPORTE43.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps([{k:r[k]for k in['life','tick','initially_alive_neighbours','currently_alive_neighbours','newly_alive_neighbours']}for r in rows]))
