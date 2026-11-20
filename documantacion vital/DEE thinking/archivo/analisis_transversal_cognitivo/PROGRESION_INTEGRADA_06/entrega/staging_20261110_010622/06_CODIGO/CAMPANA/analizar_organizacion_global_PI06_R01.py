"""Descriptores pasivos de capturas PI06; stdlib, sin importar/ejecutar DEE.

RAW repetido no equivale al mismo estado causal: se conservan clocks y alcance.
"""
from pathlib import Path
from collections import Counter
from array import array
import argparse, hashlib, importlib.util, json, sys

P=Path(__file__).resolve().parents[1]
OBSERVER=P.parents[2]/'DEE Cognitive 2.0/sistema/capacidades/observador_global_PI05_R01.py'
POINTS={
    'FI_C':[12,17,18], 'FI_S':[14,15,16], 'FI_E':[15,15,15],
    'Q':[19,54,5], 'Q_A':[18,53,5], 'Q_B':[20,53,5],
    'MU_A':[14,14,15], 'MU_B':[16,14,15],
    'eligibility_hub':[19,53,3], 'guard_PI05':[19,53,20], 'guard_PI03':[19,57,5],
    'left_source':[52,48,56], 'left_parent':[52,48,58],
    'right_source':[19,53,23], 'right_parent':[19,53,25], 'sham_source':[60,48,56]}


def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def coords(i,n):return [i//(n*n),(i//n)%n,i%n]
def index(p,n):return (p[0]*n+p[1])*n+p[2]
def decode(v):
    direction=[(v>>k)&15 for k in (48,52,56)]
    return {'RAW':str(v),'state':v&0xffffffff,'s_reg':(v>>32)&65535,'semantic':v>>60,
            'direction':[x-16 if x&8 else x for x in direction]}
def buffers(frame,n):
    raw=array('Q');clock=array('Q');raw.frombytes(frame['raw_bytes']);clock.frombytes(frame['clocks_bytes'])
    if sys.byteorder!='little':raw.byteswap();clock.byteswap()
    if len(raw)!=n**3 or len(clock)!=n**3:raise ValueError('Complete buffers only')
    return raw,clock
def components(support,n):
    remaining=set(support);parts=[]
    while remaining:
        seed=min(remaining);remaining.remove(seed);todo=[seed];part=[]
        while todo:
            i=todo.pop();part.append(i);x,y,z=coords(i,n)
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    for dz in (-1,0,1):
                        if dx==dy==dz==0:continue
                        j=index(((x+dx)%n,(y+dy)%n,(z+dz)%n),n)
                        if j in remaining:remaining.remove(j);todo.append(j)
        parts.append({'size':len(part),'lexicographic_first_site':coords(min(part),n),
                      'sites':sorted((coords(i,n)for i in part)) if len(part)<=16 else None})
    return sorted(parts,key=lambda x:(-x['size'],x['lexicographic_first_site']))
def descriptor(frame,n):
    raw,clock=buffers(frame,n);support={i for i,v in enumerate(raw)if v!=0};active={i for i in support if raw[i]&0xffffffff}
    records=[decode(raw[i])for i in support]
    return {'tick':frame['tick'],'hashes':frame['hashes'],'RAW_support_count':len(support),
        'state_positive_count':len(active),'state0_nonzero_RAW_count':len(support-active),
        'semantic_counts_RAW_support':dict(sorted(Counter(str(x['semantic'])for x in records).items())),
        'semantic_counts_state_positive':dict(sorted(Counter(str(raw[i]>>60)for i in active).items())),
        'direction_zero_RAW_support':sum(x['direction']==[0,0,0]for x in records),
        'direction_nonzero_RAW_support':sum(x['direction']!=[0,0,0]for x in records),
        's_reg_sum_RAW_support':sum(x['s_reg']for x in records),
        's_reg_sum_state_positive':sum((raw[i]>>32)&65535 for i in active),
        's_reg_max':max((x['s_reg']for x in records),default=0),
        'Moore1_toroidal_components_RAW_support':components(support,n),
        'Moore1_toroidal_components_state_positive':components(active,n),
        'fixed_points':{name:{'site':site,'clock':int(clock[index(site,n)]),**decode(raw[index(site,n)])}for name,site in POINTS.items()},
        'direction_is_encoded_orientation_not_measured_trajectory':True},raw,clock
def difference(left,right,n):
    li,lr,lc=left;ri,rr,rc=right
    changed=[i for i,(a,b)in enumerate(zip(lr,rr))if a!=b]
    clocks=[i for i,(a,b)in enumerate(zip(lc,rc))if a!=b]
    return {'from_tick':li['tick'],'to_tick':ri['tick'],'elapsed_ticks':ri['tick']-li['tick'],
        'RAW_changed_sites':len(changed),'clock_changed_sites':len(clocks),
        'RAW_equal':not changed,'clocks_equal':not clocks,
        'RAW_changed_sites_first64':[{'site':coords(i,n),'before':decode(lr[i]),'after':decode(rr[i]),
                                      'clock_before':int(lc[i]),'clock_after':int(rc[i])}for i in changed[:64]],
        'changed_site_list_truncated':len(changed)>64}


def main(a):
    source=Path(a.captura).resolve(strict=True)
    if not source.is_relative_to(P.resolve()):raise ValueError('Only PI06 captured files in this campaign')
    for node in (source,*source.parents):
        if node.exists()and(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&0x400):raise ValueError('No reparse input')
    out=Path(a.salida).absolute()
    if not out.parent.resolve(strict=True).is_relative_to((P/'control').resolve()):raise ValueError('New control proof only')
    if out.exists():raise FileExistsError('Preserve earlier analysis')
    spec=importlib.util.spec_from_file_location('PI06_passive_frame_codec',OBSERVER)
    observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
    if any(x=='dee_thinking'or x.startswith('dee_thinking.')for x in sys.modules):raise RuntimeError('No DEE imports permitted')
    cfg=read(source/'CAPTURA.json');n=cfg['N']
    if n!=67:raise ValueError('Fixed N67 recording only')
    items=[];steps=[];lag67=[];first=None;previous=None;lag={}
    for frame in observer.iter_frames(source):
        current=descriptor(frame,n);items.append(current[0])
        if first is None:first=current
        if previous is not None:steps.append(difference(previous,current,n))
        if frame['tick']-67 in lag:
            row=difference(lag[frame['tick']-67],current,n)
            row['RAW_recurrence_is_not_causal_state_recurrence']=True;lag67.append(row)
        lag[frame['tick']]=current
        # At most the currently needed67tick history and the initial frame.
        for tick in list(lag):
            if tick<frame['tick']-67:del lag[tick]
        previous=current
    if first is None:raise ValueError('No frames')
    sourceproof={f:{'bytes':(source/f).stat().st_size,'sha256':sha((source/f).read_bytes())}for f in ('CAPTURA.json','FRAMES.jsonl','INDEX.json')}
    value={'schema':'DEE.PI06.global_organization.passive_descriptors.R01',
        'capture_directory':str(source),'source_files':sourceproof,'observer_sha256':sha(OBSERVER.read_bytes()),
        'configuration':cfg,'frame_count':len(items),'frames':items,'consecutive_observed_differences':steps,
        'first_last_difference':difference(first,previous,n),'exact_recorded_pairs_67ticks_apart':lag67,
        'Native_executed':False,'new_Native_ticks':0,'new_material_queries':0,
        'limits':['Each full RAW/clocks frame is verified by the published lossless codec. It is not a full operational life.',
            'Components are geometric adjacency descriptors, not demonstrated functional modules or carrier ancestry.',
            'Direction encodes orientation; it is not a measured particle velocity or unique trajectory.',
            'RAW recurrence with different clocks is not a periodic complete causal state.',
            'No descriptor alone demonstrates useful memory, learning, self-regulation or recovery. Fixed functional challenges and matched controls remain necessary.']}
    with out.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':str(out),'sha256':sha(out.read_bytes()),'frames':len(items),
        'RAW_first_last_equal':value['first_last_difference']['RAW_equal'],
        'clock_first_last_equal':value['first_last_difference']['clocks_equal'],'Native_executed':False}))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--captura',required=True);ap.add_argument('--salida',required=True)
    main(ap.parse_args())
