"""N0 comparison of prospective fixed route anatomy, never a response oracle."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument('--sistema',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();s=a.sistema.resolve();sys.path.insert(0,str(s))
    from app.lives import Store
    from app.native_tools import physical,observe
    from capacidades import selector_acrecion_nativo as sel
    from dee_thinking import _native as d
    store=Store(s);rec,w=store.load('APD02_MAIN');before=physical(w.world);rows=[]
    for origin in((45,15,45),(15,45,45)):
        at=lambda v:sel.at(origin,v,67)
        geometry={tuple(r['site']):r for r in sel.geometry(origin,67)if tuple(r['site'])not in(at((-3,3,0)),at((3,3,0)))}
        stops=[(-1,-2,-1)]
        for x in(-1,0,1):stops += [(5*x,5,0),(4*x,4,-3),(6*x,6,0),(11*x,11,-1),(10*x,10,0),(10*x,10,10)]
        for v in stops:geometry[at(v)]={'site':at(v)}
        loop={at((x*k,k,-2))for x in(-1,0,1)for k in range(67)}
        selected=set(geometry)|loop
        exact=[observe(w.world,p)for p in sorted(selected)]
        neighbors={tuple((p[i]+v[i])%67 for i in range(3))for p in selected for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)for v in[(x,y,z)]}-selected
        near=[o for o in(observe(w.world,p)for p in sorted(neighbors))if int(o['raw'])!=0]
        rows.append({'origin':origin,'exact_sites_examined':len(exact),'preparation_collision':[o for o in exact if int(o['raw'])!=0],'neighbor_sites_examined':len(neighbors),'nonzero_near_routes':near,'coverage':'Only fixed preparation/loop and their Moore26 spatial neighbor sites at current snapshot. Does not establish full-tick causal isolation or future noninterference.'})
    result={'schema':'APD02.route_geometry_N0.v1','life':rec['life_id'],'snapshot':rec['snapshot'],'snapshot_sha256':rec['snapshot_sha256'],'before':before,'after':physical(w.world),'new_ticks':0,'rows':rows}
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8');print(json.dumps({'cut':before,'new_ticks':0,'candidates':[(r['origin'],len(r['preparation_collision']),len(r['nonzero_near_routes']))for r in rows]}))
if __name__=='__main__':main()
