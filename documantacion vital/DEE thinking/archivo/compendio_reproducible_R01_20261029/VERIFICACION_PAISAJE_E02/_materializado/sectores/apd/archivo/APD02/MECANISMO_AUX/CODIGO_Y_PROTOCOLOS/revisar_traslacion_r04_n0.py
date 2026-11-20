"""Read only two fixed candidate ROIs from one complete saved main snapshot.

Loads one Runtime for passive observations only; no step, input, life write or
world save. This geometric screen cannot prove future functional independence.
"""
import argparse,gzip,hashlib,json,sys
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--system',type=Path,required=True);p.add_argument('--snapshot',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    if args.out.exists():raise FileExistsError('Fresh passive report only')
    args.out.parent.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(args.system.resolve()))
    from app.process_control import protect_current,current_resources
    protect_current(memory_limit=512*1024*1024)
    from dee_thinking.persistence import load_world_snapshot
    from dee_thinking import _native as d
    from dee_thinking.consolidated import exact_observation
    from app.native_tools import physical
    from capacidades import selector_acrecion_nativo as sel
    before_sha=sha(args.snapshot);world,proof=load_world_snapshot(args.snapshot);pre=physical(world,occupation=True);N=67
    result=[]
    for O in((45,15,45),(15,45,45)):
        def at(v):return sel.at(O,v,N)
        rows={tuple(r['site'])for r in sel.geometry(O,N)}-{at((-3,3,0)),at((3,3,0))}
        stops=[(-1,-2,-1)]
        for x in(-1,0,1):stops += [(5*x,5,0),(4*x,4,-3),(6*x,6,0),(11*x,11,-1),(10*x,10,0),(10*x,10,10)]
        rows|={at(v)for v in stops};loop={at((x*k,k,-2))for x in(-1,0,1)for k in range(67)}
        sources=[]
        for pos,v in sel.ports(O,N,'roi').values():sources.append((pos,v))
        for x in(-1,0,1):
            sources += [(at((4*x,4,1)),(0,0,-1)),(at((6*x,6,-3)),(0,0,1)),(at((10*x,10,-3)),(0,0,1))]
            target=(2*x,-2,-2);v=(0,0,1)if x else(-1,0,1);source=tuple(target[i]-v[i]for i in range(3));sources.append((at(source),v))
        paths=set()
        for pos,v in sources:
            for k in range(9):paths.add(tuple((pos[i]+k*v[i])%N for i in range(3)))
        critical=rows|loop|paths;roi=set(critical)
        for pos in critical:
            for dx in(-1,0,1):
                for dy in(-1,0,1):
                    for dz in(-1,0,1):roi.add(tuple((pos[i]+(dx,dy,dz)[i])%N for i in range(3)))
        observations={pos:exact_observation(world.runtime.observe(d.Coordinate(*pos)))for pos in sorted(roi)}
        nonzero=[v for v in observations.values()if int(v['raw'])]
        conflict_geometry=[observations[pos]for pos in sorted(rows)if int(observations[pos]['raw'])]
        conflict_loop=[observations[pos]for pos in sorted(loop)if int(observations[pos]['raw'])]
        H=(47,17,47)
        def dist(pos):return max(min((pos[i]-H[i])%N,(H[i]-pos[i])%N)for i in range(3))
        result.append({'origin':O,'geometry_sites':len(rows),'loop_sites':len(loop),'principal_source_path_sites':len(paths),'ROI_sites_covered':len(roi),
                       'nonzero_geometry_conflicts':conflict_geometry,'nonzero_loop_conflicts':conflict_loop,
                       'nonzero_principal_path_sites':[observations[pos]for pos in sorted(paths)if int(observations[pos]['raw'])],
                       'nonzero_in_radius1_context':nonzero,'all_critical_exact_RAW_and_clocks':[observations[pos]for pos in sorted(critical)],
                       'minimum_toroidal_Chebyshev_distance_to_new_hub_H':{'geometry':min(map(dist,rows)),'loop':min(map(dist,loop)),'principal_paths':min(map(dist,paths))},
                       'scope':'Point/one-neighborhood passive screen only. No future query, timing, retention, longer full-tick causal neighborhood or quality claim.'})
    post=physical(world,occupation=True)
    report={'schema':'APD02.R03_R04.preparation_ROI.passive_screen.v1','snapshot':str(args.snapshot),'snapshot_sha256':before_sha,
            'storage':proof,'physical_before':pre,'physical_after':post,'equal_physical_fields':pre==post,
            'source_snapshot_bytes_unchanged':sha(args.snapshot)==before_sha,'new_ticks':0,'inputs_submitted':0,'world_saved':False,
            'candidate_ROIs':result,'resources':current_resources(),'source_code_sha256':sha(Path(__file__))}
    data=json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2).encode('utf8')+b'\n'
    with args.out.open('xb')as f:f.write(gzip.compress(data,mtime=0))
    print(json.dumps({'tick':pre['tick'],'new_ticks':0,'equal_physical':pre==post,'summary':[{'origin':r['origin'],'geometry_conflicts':len(r['nonzero_geometry_conflicts']),'loop_conflicts':len(r['nonzero_loop_conflicts']),'path_nonzero':len(r['nonzero_principal_path_sites']),'context_nonzero':len(r['nonzero_in_radius1_context']),'distance_H':r['minimum_toroidal_Chebyshev_distance_to_new_hub_H']}for r in result],'report_sha256':sha(args.out)}))
    return 0
if __name__=='__main__':raise SystemExit(main())
