"""Exact finite geometry calculation for two prospective R04 placements. N0."""
import argparse,json,sys
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument('--sistema',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.sistema))
    from app.lives import Store
    from app.native_tools import physical,observe
    from capacidades import selector_acrecion_nativo as sel
    from capacidades import lexico_apd02_01 as words
    rec,w=Store(a.sistema).load('APD02_MAIN');before=physical(w.world)
    if before['tick']!=391957:raise ValueError('Pinned adverse MAIN R03cut required')
    columns=[{'form':f,'xy':list(words.pos(o,v,3)[:2])}for f,(o,v)in words.FORM_CODEC.items()]
    def axis(x,y):return min((x-y)%67,(y-x)%67)
    rows=[]
    for origin in((15,45,53),(25,13,53)):
        at=lambda v:sel.at(origin,v,67)
        geometry={tuple(r['site'])for r in sel.geometry(origin,67)if tuple(r['site'])not in(at((-3,3,0)),at((3,3,0)))}
        stops=[(-1,-2,-1)]
        for x in(-1,0,1):stops += [(5*x,5,0),(4*x,4,-3),(6*x,6,0),(11*x,11,-1),(10*x,10,0),(10*x,10,10)]
        geometry.update(at(v)for v in stops)
        ports={name:pos for name,(pos,_)in sel.ports(origin,67,'R04').items()}
        for x in(-1,0,1):
            ports.update({f'divert{x}':at((4*x,4,1)),f'flatten{x}':at((6*x,6,-3)),f'clear{x}':at((10*x,10,-3))})
            target=(2*x,-2,-2);direction=(0,0,1)if x else(-1,0,1);source=tuple(target[i]-direction[i]for i in range(3))
            ports[f'failure{x}']=at(source);ports[f'sham{x}']=at((source[0],source[1],source[2]+8))
        loops={x:[at((x*k,k,-2))for k in range(67)]for x in(-1,0,1)}
        exact=set(geometry)|set(ports.values())|{p for ps in loops.values()for p in ps}
        occupied=[o for o in(observe(w.world,p)for p in sorted(exact))if int(o['raw'])!=0]
        distances=[{'form':c['form'],'column_xy':c['xy'],'trace_class':x,'minimum_toroidal_xy_chebyshev':min(max(axis(p[0],c['xy'][0]),axis(p[1],c['xy'][1]))for p in ps)}for c in columns for x,ps in loops.items()]
        rows.append({'origin':origin,'ports':ports,'planned_geometry_intersects_own_ports':[{'port':name,'site':p}for name,p in ports.items()if p in geometry],'exact_sites_examined':len(exact),'nonzero_at_proposed_sites':occupied,'loop_to_nominal_memory_column_distances':distances,'minimum_nominal_column_distance':min(q['minimum_toroidal_xy_chebyshev']for q in distances)})
    result={'schema':'APD02.prospective_geometry_R04.N0','initial':before,'after':physical(w.world),'snapshot_sha256':rec['snapshot_sha256'],'new_ticks':0,'nominal_memory_columns':columns,'candidates':rows,'scope':'Finite initial-state and nominal route calculation. No target/answer consulted, no field changed, no future isolation or general causal-radius claim. Inactive nonzero RAW counts as occupied for port compatibility.'}
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8');print(json.dumps([(r['origin'],len(r['nonzero_at_proposed_sites']),len(r['planned_geometry_intersects_own_ports']),r['minimum_nominal_column_distance'])for r in rows]))
if __name__=='__main__':main()
