"""0tick screen of one fixed additional hub; not a native placement or trial."""
import argparse,hashlib,importlib.util,json
from pathlib import Path

def run(system,snapshot):
    sp=importlib.util.spec_from_file_location('apd01_observer',system/'capacidades/observador_causal_retrospectivo_01.py')
    obs=importlib.util.module_from_spec(sp);sp.loader.exec_module(obs);s=obs.Snapshot(snapshot)
    if s.N!=67:raise ValueError('No extrapolation beyond admittedN67')
    origin=(47,47,47);forms={'agrega':(-1,0,0),'resta':(0,-1,0)}
    def pos(v,k,z=0):return tuple((origin[j]+k*v[j]+(z if j==2 else 0))%67 for j in range(3))
    prep=[{'form':f,'site':list(pos(v,k,z*sg)),'observation':s.observation(list(pos(v,k,z*sg)))}
          for f,v in forms.items() for sg in(-1,1) for k,z in((2,1),(2,2),(5,3))]
    roi=set();columns=set()
    for v in forms.values():
        roi.update(pos(v,k,z) for k in range(0,8) for z in range(-6,7))
        columns.update(pos(v,3,z) for z in range(67))
    channels_roi=[{'name':name,**c} for name,c in s.channels.items() if tuple(c['site']) in roi]
    channels_columns=[{'name':name,**c} for name,c in s.channels.items() if tuple(c['site']) in columns]
    return {'schema':'APD01.second_hub_screen.R02','snapshot':str(snapshot),'snapshot_sha256':s.encoded_sha256,
            'tick':s.tick,'N':s.N,'checksum_valid':s.checksum_valid,'origin':list(origin),'forms':forms,
            'preparation':prep,'preparation12_RAW_zero':all(int(r['observation']['raw'])==0 for r in prep),
            'ROI_sites':len(roi),'ROI_nonzero_RAW':[s.observation(list(p)) for p in sorted(roi) if s.raw[obs.index(p,67)]],
            'memory_column_sites':len(columns),'memory_columns_nonzero_RAW':[s.observation(list(p)) for p in sorted(columns) if s.raw[obs.index(p,67)]],
            'existing_channels_in_ROI':channels_roi,'existing_channels_on_memory_columns':channels_columns,
            'common_reader_gate_count':20,'native_ticks_executed':0,
            'limits':'Static RAW and interface-origin screen only. Future routes may enter from outside. No learned content, isolation, syntax or new operation is thereby demonstrated.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sistema',type=Path,required=True);p.add_argument('--snapshot',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args();r=run(a.sistema,a.snapshot);b=(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
    with a.salida.open('xb') as f:f.write(b)
    print(json.dumps({'snapshot_sha256':r['snapshot_sha256'],'tick':r['tick'],'origin':r['origin'],
                      'preparation12_RAW_zero':r['preparation12_RAW_zero'],'ROI_nonzero_RAW':len(r['ROI_nonzero_RAW']),
                      'memory_columns_nonzero_RAW':len(r['memory_columns_nonzero_RAW']),
                      'channels_in_ROI':len(r['existing_channels_in_ROI']),'channels_on_memory_columns':len(r['existing_channels_on_memory_columns']),
                      'output_sha256':hashlib.sha256(b).hexdigest(),'native_ticks_executed':0}))
