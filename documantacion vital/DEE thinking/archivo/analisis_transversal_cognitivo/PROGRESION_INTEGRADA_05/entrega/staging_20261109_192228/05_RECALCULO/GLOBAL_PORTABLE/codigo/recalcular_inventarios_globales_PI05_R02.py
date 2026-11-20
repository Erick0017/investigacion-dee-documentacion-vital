"""Portable exact global differences from sparse hashed RAW inventories.

Zero-filled complete RAW and uniform complete clocks are reconstructed and
checked against each original Native-buffer SHA. No engine/original path is
opened. Nonuniform clocks are explicitly unsupported by this compact recipe.
"""
from pathlib import Path
from array import array
import argparse,contextlib,csv,gzip,hashlib,io,json,struct,sys
N=67;COUNT=N**3

def sha(b):return hashlib.sha256(b).hexdigest()
def file_sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def decode(v):
    d=[(v>>s)&15 for s in(48,52,56)]
    return {'state':v&0xffffffff,'s_reg':(v>>32)&65535,'semantic':(v>>60)&15,'direction':[x-16 if x&8 else x for x in d]}
def site(i):return[i//4489,(i//67)%67,i%67]
def lebytes(a):
    if a.itemsize!=8:raise ValueError('uint64 width')
    if sys.byteorder!='little':a.byteswap()
    return a.tobytes()
def info(p):return {'file':Path(p).name,'bytes':Path(p).stat().st_size,'sha256':file_sha(p)}
@contextlib.contextmanager
def gztext(p):
    with Path(p).open('xb')as f:
        with gzip.GzipFile(fileobj=f,mode='wb',mtime=0,filename='')as g:
            with io.TextIOWrapper(g,encoding='utf-8',newline='')as t:yield t
def new_destination(p):
    p=Path(p).absolute()
    if p.exists():raise FileExistsError('A new destination is required')
    for x in(p,*p.parents):
        if x.exists()and(x.is_symlink()or getattr(x.lstat(),'st_file_attributes',0)&1024):raise ValueError('Linked destination')
    p.mkdir(parents=True);return p
def validate_inventory(root):
    root=Path(root);manifest=read(root/'MANIFIESTO_SHA256.json')
    for row in manifest['files']:
        if Path(row['file']).name!=row['file']:raise ValueError('Only local leaf members')
        p=root/row['file']
        if p.stat().st_size!=row['bytes']or file_sha(p)!=row['sha256']:raise ValueError('Input manifest mismatch: '+p.name)
    summary=read(root/'RESUMEN_GLOBAL.json')
    if not summary['complete_N67_each_frame']or not summary['all_reconstructed_frame_hashes_verified']:raise ValueError('Exact complete inventory required')
    return summary
def frames(root,summary):
    count=0;previous=None
    with gzip.open(Path(root)/'RAW_NO_NULO_GLOBAL.jsonl.gz','rt',encoding='utf-8')as f:
        for line in f:
            if len(line)>16777216:raise ValueError('Inventory row exceeds bound')
            row=json.loads(line);s=summary['frames'][count];tick=row['tick']
            if tick!=s['tick']or(previous is not None and tick<=previous):raise ValueError('Fixed increasing absolute ticks')
            if row['RAW_sha256']!=s['RAW_sha256']or row['clocks_sha256']!=s['clocks_sha256']:raise ValueError('Summary/member hashes differ')
            raw=array('Q',[0])*COUNT;values={}
            for r in row['nonzero_RAW_records']:
                i=r['index'];v=int(r['raw'])
                if type(i)is not int or not 0<=i<COUNT or i in values or not 0<v<2**64 or r['site']!=site(i):raise ValueError('Malformed/duplicate sparse record')
                d=decode(v)
                if any(r[k]!=d[k]for k in d):raise ValueError('Decoded fields do not match exact RAW')
                values[i]=v;raw[i]=v
            if len(values)!=s['raw_nonzero']or sha(lebytes(raw))!=row['RAW_sha256']:raise ValueError('Complete zero-filled RAW reconstruction differs')
            if s['all_clocks_min']!=s['all_clocks_max']:raise ValueError('Nonuniform clocks need original frame codec; never infer missing clocks')
            clock=int(s['all_clocks_min'])
            if not 0<=clock<2**64 or sha(lebytes(array('Q',[clock])*COUNT))!=row['clocks_sha256']:raise ValueError('Complete uniform clock reconstruction differs')
            if any(int(r['clock'])!=clock for r in row['nonzero_RAW_records']):raise ValueError('Recorded site clock differs')
            yield {'tick':tick,'values':values,'clock':clock,'summary':s}
            previous=tick;count+=1
    if count!=summary['frame_count']:raise ValueError('Inventory frame count mismatch')
def events(summary):
    v=summary.get('actual_requests')
    return None if v is None else v['events']
def event_diff(a,b):
    aa=events(a);bb=events(b)
    if aa is None or bb is None:return {'available':False}
    def key(x):return(x['channel'],x['tick'])
    ma={};mb={}
    for origin,target in((aa,ma),(bb,mb)):
        for x in origin:
            k=key(x)
            if k in target:raise ValueError('Ambiguous repeated channel/tick; do not guess event pairing')
            target[k]=x
    common=sorted(set(ma)&set(mb));d=[];receipts=[];identical=0
    fields=('channel','tick','site','direction','payload');rk=('kind','status','requested_tick','effective_tick','channels','reason')
    for k in common:
        x=ma[k];y=mb[k]
        if any(x[f]!=y[f]for f in fields):d.append({'a':{f:x[f]for f in fields},'b':{f:y[f]for f in fields}})
        else:identical+=1
        if any(x['receipt'].get(f)!=y['receipt'].get(f)for f in rk):receipts.append({'channel':x['channel'],'tick':x['tick'],'a':{f:x['receipt'].get(f)for f in rk},'b':{f:y['receipt'].get(f)for f in rk}})
    def extra(mapping,keys):return[{**{f:mapping[k][f]for f in fields},'Native_id':mapping[k]['Native_id'],'receipt':mapping[k]['receipt']}for k in sorted(keys)]
    return {'available':True,'count_a':len(aa),'count_b':len(bb),'same_count':len(aa)==len(bb),'pairing':'Unique actual channel+tick, never list-position or expected result','common_channel_tick_events':len(common),'identical_common_requests':identical,'request_differences':d,'events_only_a':extra(ma,set(ma)-set(mb)),'events_only_b':extra(mb,set(mb)-set(ma)),'receipt_outcome_differences':receipts,'Native_IDs_not_compared_as_independent_events':True,'missing_geometry_a':a['actual_requests']['missing_physical_sources_not_invented'],'missing_geometry_b':b['actual_requests']['missing_physical_sources_not_invented']}

def compare(a,b,dest):
    a=Path(a);b=Path(b);sa=validate_inventory(a);sb=validate_inventory(b);root=new_destination(dest)
    ia=iter(frames(a,sa));ib=iter(frames(b,sb));sentinel=object();rows=[];first=None;last=None;initial=None
    with gztext(root/'DIFERENCIAS_RAW_GLOBALES.csv.gz')as f:
        w=csv.writer(f);w.writerow(['tick','index','x','y','z','RAW_a','RAW_b','RAW_xor','clock_both','state_a','s_reg_a','semantic_a','direction_a','state_b','s_reg_b','semantic_b','direction_b'])
        while True:
            x=next(ia,sentinel);y=next(ib,sentinel)
            if x is sentinel and y is sentinel:break
            if x is sentinel or y is sentinel or x['tick']!=y['tick']:raise ValueError('Exact same frame calendar required')
            if x['clock']!=y['clock']:raise ValueError('This compact mode supports equal uniform complete clocks; use original codec for global clock differences')
            union=sorted(set(x['values'])|set(y['values']));different=[i for i in union if x['values'].get(i,0)!=y['values'].get(i,0)]
            if initial is None:initial={'tick':x['tick'],'RAW_difference_count':len(different),'RAW_difference_sites':[site(i)for i in different],'clocks_exact':True}
            if different:
                if first is None:first=x['tick']
                last=x['tick']
            for i in different:
                av=x['values'].get(i,0);bv=y['values'].get(i,0);da=decode(av);db=decode(bv)
                w.writerow([x['tick'],i,*site(i),str(av),str(bv),str(av^bv),str(x['clock']),da['state'],da['s_reg'],da['semantic'],str(da['direction']),db['state'],db['s_reg'],db['semantic'],str(db['direction'])])
            h=hashlib.sha256()
            for i in different:h.update(struct.pack('<I',i))
            rows.append({'tick':x['tick'],'RAW_difference_sites':len(different),'clocks_difference_sites':0,'RAW_difference_index_uint32LE_sha256':h.hexdigest(),'RAW_a_sha256':x['summary']['RAW_sha256'],'RAW_b_sha256':y['summary']['RAW_sha256'],'clocks_a_sha256':x['summary']['clocks_sha256'],'clocks_b_sha256':y['summary']['clocks_sha256']})
    result={'schema':'DEE.PI05.sparse_features.exact_global_recalculation.R02','mode':'RECALCULATION_ONLY_NO_NATIVE','Native_ticks':0,'input_a':{'directory':a.name,'manifest':info(a/'MANIFIESTO_SHA256.json')},'input_b':{'directory':b.name,'manifest':info(b/'MANIFIESTO_SHA256.json')},'frames':rows,'frame_count':len(rows),'initial_physical_difference':initial,'first_observed_RAW_difference_tick':first,'last_observed_RAW_difference_tick':last,'all_complete_RAW_clocks_original_hashes_reconstructed':True,'all_clock_fields_reconstructed_uniform_and_verified':True,'actual_event_comparison':event_diff(sa,sb),'scope':'Exact D(T) across all300763sites per original-hash-verified RAW/clocks buffers. This is a portable documentary recalculation, not Native replay, operational-state equality, memory-erasure proof, lineage or a new sensor supplied to the actor.'}
    out=root/'RECALCULO_GLOBAL_PORTABLE.json'
    with out.open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    manifest={'schema':'DEE.PI05.portable_recalculation.member_manifest.R02','files':[info(p)for p in sorted(root.iterdir())if p.is_file()]}
    with(root/'MANIFIESTO_SHA256.json').open('x',encoding='utf-8')as f:json.dump(manifest,f,ensure_ascii=False,indent=2);f.write('\n')
    return out
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--inventario-a',required=True,type=Path);ap.add_argument('--inventario-b',required=True,type=Path);ap.add_argument('--destino',required=True,type=Path);a=ap.parse_args()
    out=compare(a.inventario_a,a.inventario_b,a.destino);print(json.dumps({'output':str(out.resolve()),'bytes':out.stat().st_size,'sha256':file_sha(out),'Native_ticks':0}))
if __name__=='__main__':main()
