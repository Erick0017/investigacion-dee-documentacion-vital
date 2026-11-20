"""Lossless included PI07 captures only; stdlib and no original-path access."""
from pathlib import Path
import argparse, hashlib, json, runpy, struct


def sha(b):return hashlib.sha256(b).hexdigest()


def safe(root,name):
    p=(root/name).resolve(strict=True)
    if not p.is_relative_to(root.resolve())or not p.is_file():raise ValueError('Bundle path escape')
    return p


def decoded(raw,clock,site,N):
    index=(site[0]*N+site[1])*N+site[2]
    v=struct.unpack_from('<Q',raw,index*8)[0];c=struct.unpack_from('<Q',clock,index*8)[0]
    directions=[(v>>k)&15 for k in(48,52,56)]
    return{'site':list(site),'RAW':str(v),'clock':str(c),'state':v&0xffffffff,
           's_reg':(v>>32)&65535,'semantic':v>>60,
           'direction':[x-16 if x&8 else x for x in directions]}


def verify(bundle):
    bundle=Path(bundle).resolve(strict=True);index=json.loads((bundle/'CASOS.json').read_text(encoding='utf-8'))
    if index['schema']!='DEE.PI07.lossless_global_portable_manifest.v1':raise ValueError('Manifest schema')
    for row in index['files']:
        b=safe(bundle,row['file']).read_bytes()
        if len(b)!=row['bytes']or sha(b)!=row['sha256']:raise ValueError('Literal portable file differs:'+row['file'])
    module=runpy.run_path(str(safe(bundle,'codec.py')),run_name='pure_lossless_frame_reader')
    cases=[];total=0
    for case in index['captures']:
        directory=bundle/case['directory'];frames=[]
        for f in module['iter_frames'](directory):
            N=f['config']['N'];raw=f['raw_bytes'];clocks=f['clocks_bytes']
            lane=[decoded(raw,clocks,(52,48,z),N)for z in range(N)]
            frames.append({'tick':f['tick'],'hashes':f['hashes'],
              'lane52_48_nonzero_RAW':[r for r in lane if int(r['RAW'])!=0],
              'TC_banks':[decoded(raw,clocks,p,N)for p in((7,39,50),(9,39,50))],
              'fixed_cost_readers':[decoded(raw,clocks,p,N)for p in((53,48,51),(53,48,57),(54,48,56))],
              'R03_deflection_fixed_sites':[decoded(raw,clocks,p,N)for p in
                ((53,48,56),(52,48,56),(51,48,57),(50,48,58),(52,48,55),
                 (52,48,57),(52,48,58),(54,48,56),(56,48,56))]})
        if len(frames)!=case['captured_frames']:raise ValueError('Capture frame count differs')
        total+=len(frames);cases.append({'id':case['id'],'source_references':case['source_references'],
          'captured_frames':len(frames),'missing_planned_ticks':case['missing_planned_ticks'],
          'frames':frames,'scope':'All included full buffers reconstructed/hash-checked; only declared lane/banks/readers decoded as observations. No interpolation or unique Native lineage.'})
    return{'schema':'DEE.PI07.lossless_portable_buffers_recalculation.v1','Native_executed':False,
           'DEE_imports':False,'new_Native_ticks':0,'all_complete_buffer_hashes_match':True,
           'captures':len(cases),'total_frames':total,'cases':cases,
           'original_directories_followed':False,'not_a_full_operational_backup':True}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    if args.out.exists():raise FileExistsError(args.out)
    result=verify(args.bundle);args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'captures':result['captures'],'frames':result['total_frames'],'Native_ticks':0},ensure_ascii=False))


if __name__=='__main__':main()
