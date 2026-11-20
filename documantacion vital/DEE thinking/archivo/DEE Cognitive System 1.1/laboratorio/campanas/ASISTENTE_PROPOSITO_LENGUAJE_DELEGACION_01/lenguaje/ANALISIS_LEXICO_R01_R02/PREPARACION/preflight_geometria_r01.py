"""Pure snapshot decoding and geometry screening, no native import/Runtime/ticks."""
import argparse,hashlib,importlib.util,json
from pathlib import Path

def run(system,snapshot):
    observer=system/'capacidades/observador_causal_retrospectivo_01.py'
    sp=importlib.util.spec_from_file_location('apd01_observer',observer)
    obs=importlib.util.module_from_spec(sp); sp.loader.exec_module(obs)
    s=obs.Snapshot(snapshot)
    if s.N!=67:
        raise ValueError('No geometry extrapolation outside N67')
    origin=(33,33,33)
    forms={'suma':(-1,0,0),'diferencia':(0,-1,0)}
    def pos(v,k,z=0):return tuple((origin[j]+k*v[j]+(z if j==2 else 0))%67 for j in range(3))
    rows=[]; footprint=[]
    for form,v in forms.items():
        for sg in (-1,1):
            for k,z in ((2,1),(2,2),(5,3)):
                p=pos(v,k,z*sg); rows.append({'form':form,'site':list(p),'observation':s.observation(list(p))})
        points={pos(v,k,z) for k in range(1,8) for z in range(-6,7)}
        nonzero=[s.observation(list(p)) for p in sorted(points) if s.raw[obs.index(p,s.N)]]
        footprint.append({'form':form,'screened_sites':len(points),'nonzero_RAW':nonzero})
    return {'schema':'APD01.lexical_geometry_screen.R01','snapshot':str(snapshot),
            'snapshot_sha256':s.encoded_sha256,'N':s.N,'tick':s.tick,
            'checksum_valid':s.checksum_valid,'pending_native_count':len(s.pending),
            'preparation_sites':rows,'all12_preparation_RAW_zero':all(int(x['observation']['raw'])==0 for x in rows),
            'partial_route_ROI':footprint,'native_ticks_executed':0,
            'limits':'Static local geometry screen. Future interference, admission and learning remain untested; RAW0 now is not proof of lasting isolation.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sistema',type=Path,required=True)
    p.add_argument('--snapshot',type=Path,required=True);p.add_argument('--salida',type=Path)
    a=p.parse_args();result=run(a.sistema,a.snapshot)
    b=(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
    if a.salida:
        if a.salida.exists():raise FileExistsError('Refuse overwrite')
        a.salida.write_bytes(b)
    print(json.dumps({'all12_preparation_RAW_zero':result['all12_preparation_RAW_zero'],
                      'snapshot_sha256':result['snapshot_sha256'],'tick':result['tick'],
                      'route_nonzero_counts':{r['form']:len(r['nonzero_RAW']) for r in result['partial_route_ROI']},
                      'output_sha256':hashlib.sha256(b).hexdigest(),'native_ticks_executed':0}))
