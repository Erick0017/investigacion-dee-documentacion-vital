"""Portable bounded DEETSNP1/v2 analysis, stdlib only, never loads a world.

Reader layout is the preserved passive PI03 parser. Structured causal prefix
follows comparar_reproduccion_PI10_R03.native_structure. Only strings exactly
equal to each declared current transport ID may normalize. RAW/clocks and
all other parsed fixed bytes remain exact. This does NOT check omitted
SQLite, artifacts, code capsules or whole operational correspondence.
Gzip CRC and manifest SHA256 are checked; internal FNV is not recomputed.
"""
from pathlib import Path,PurePosixPath
import argparse,gzip,hashlib,io,json,struct
MAX=128_000_000
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
class Reader:
    def __init__(self,b):self.b=b;self.i=0
    def take(self,n):
        need(0<=n<=len(self.b)-self.i,'Truncated snapshot');value=self.b[self.i:self.i+n];self.i+=n;return value
    def u8(self):return self.take(1)[0]
    def u32(self):return struct.unpack('<I',self.take(4))[0]
    def u64(self):return struct.unpack('<Q',self.take(8))[0]
    def count(self):
        n=self.u32();need(n<=1_000_000,'Bounded collection');return n
    def text(self):
        n=self.u32();need(n<=16*1024**2,'Bounded UTF8 text');return self.take(n).decode('utf8')
def safe(root,name):
    pp=PurePosixPath(name);need(not pp.is_absolute()and '..'not in pp.parts and ':'not in name and '\\'not in name,'Bundle-relative snapshot only')
    path=root.joinpath(*pp.parts);need(path.resolve().is_relative_to(root.resolve())and path.is_file(),'Existing bundle member inside boundary')
    for p in(path,*path.parents):need(not p.is_symlink()and not(getattr(p.lstat(),'st_file_attributes',0)&1024),'No linked snapshot')
    return path
def parse(encoded,life):
    need(len(encoded)<=32_000_000,'Encoded snapshot bound')
    if encoded[:2]==b'\x1f\x8b':
        with gzip.GzipFile(fileobj=io.BytesIO(encoded))as g:data=g.read(MAX+1)
    else:data=encoded
    need(8<len(data)<=MAX,'Bounded decompressed snapshot');r=Reader(data[:-8])
    need(r.take(8)==b'DEETSNP1'and r.u32()==2,'Exact known native snapshot v2')
    n=r.u32();tick=r.u64();flags=r.take(17).hex();phase=r.text();total=r.u64();need(n==67 and total==n**3,'This package contains N67 analysis only')
    raw=r.take(total*8);clocks=r.take(total*8)
    value={'N':n,'tick':tick,'header_fixed_bytes_hex':flags,'phase':phase,'total_sites':total,'RAW_sha256':sha(raw),'clocks_sha256':sha(clocks),'interfaces':[],'pending':[],'receipts':[]}
    for _ in range(r.count()):value['interfaces'].append({'name':r.text(),'all_fixed_bytes_hex':r.take(31).hex()})
    for _ in range(r.count()):
        row={'all_fixed_bytes_hex':r.take(33).hex(),'tags':[r.text()for _ in range(r.count())]};row['all_spatial_payload_bytes_hex']=[r.take(20).hex()for _ in range(r.count())];value['pending'].append(row)
    for _ in range(r.count()):
        row={'all_fixed_bytes_hex':r.take(18).hex()};flag=r.u8();need(flag in(0,1),'Known applied tick flag');row['applied_tick_flag']=flag;row['applied_tick_bytes_hex']=r.take(8).hex()if flag else None
        row['tags']=[r.text()for _ in range(r.count())];row['detail']=r.text();value['receipts'].append(row)
    value['trailing_fixed_bytes_hex']=r.take(9).hex();prefix=r.i;metadata={}
    for _ in range(r.count()):
        key=r.text();need(key not in metadata,'Duplicate metadata key');metadata[key]=r.text()
    need(r.i==len(data)-8,'Uninterpreted trailing native data');paths=[]
    def normal(v,path=''):
        if isinstance(v,dict):return{k:normal(x,path+'/'+k)for k,x in v.items()}
        if isinstance(v,list):return[normal(x,path+'/'+str(i))for i,x in enumerate(v)]
        if isinstance(v,str)and v==life:paths.append(path);return'__EXACT_CURRENT_TRANSPORT_LABEL__'
        return v
    norm=normal(value)
    def field(site):
        x,y,z=site;offset=((x*n+y)*n+z)*8;word=struct.unpack_from('<Q',raw,offset)[0];ds=[(word>>s)&15 for s in(48,52,56)]
        return {'site':site,'RAW':str(word),'clock':str(struct.unpack_from('<Q',clocks,offset)[0]),'state':word&0xffffffff,'s_reg':(word>>32)&65535,'semantic':word>>60,'direction':[v-16 if v>=8 else v for v in ds]}
    own=metadata.get('DEE.Cognitive.PI10.adaptive_query.two_native_traces.R02');progress=json.loads(own)if own else None
    view={'physical':{k:value[k]for k in('N','tick','RAW_sha256','clocks_sha256')},'encoded_sha256':sha(encoded),'gzip_CRC_checked':encoded[:2]==b'\x1f\x8b',
      'causal_prefix_sha256':sha(data[:prefix]),'interfaces':len(value['interfaces']),'pending_Native':len(value['pending']),'Native_receipts':len(value['receipts']),
      'phase':phase,'exact_transport_label_paths':paths,'metadata_strings_sha256':{k:sha(v.encode('utf8'))for k,v in metadata.items()},
      'q1_references':[field([23,11,12]),field([25,11,12])],'q2_references':[field([7,39,50]),field([9,39,50])],
      'postread_guards':[field([30,40,32]),field([32,40,32])],
      'PI10_progress_subset':None if progress is None else{k:progress.get(k)for k in('version','preparation_life_id','preparation_protocol_sha256','protocol_sha256','admitted','ordinal','pending','uncertain')},
      'internal_FNV_recomputed':False,'complete_operational_state_verified':False}
    return view,norm
def diff(a,b,path=''):
    if type(a)is not type(b):return[path]
    if isinstance(a,dict):
        if set(a)!=set(b):return[path+'/keys']
        return[p for k in a for p in diff(a[k],b[k],path+'/'+k)]
    if isinstance(a,list):
        if len(a)!=len(b):return[path+'/length']
        return[p for i,(x,y)in enumerate(zip(a,b))for p in diff(x,y,path+'/'+str(i))]
    return[]if a==b else[path]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--indice',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);args=p.parse_args();need(not args.salida.exists(),'No overwrite of an earlier snapshot analysis')
    ib=args.indice.read_bytes();index=json.loads(ib);need(index['schema']=='DEE.PI10.three_snapshot_analysis.R01','Explicit three-snapshot analysis index')
    views={};norms={};omitted_optional=[]
    for item in index['snapshots']:
        role=item['role'];need(role in('neutral','learned','replay','principal_final')and role not in views,'Unique declared snapshot role')
        if item.get('optional_analysis_role')is True:
            need(role=='principal_final','Only final-principal extra snapshot is an optional analysis role')
            pp=PurePosixPath(item['file']);need(not pp.is_absolute()and '..'not in pp.parts and ':'not in item['file']and '\\'not in item['file'],'Safe optional member')
            if not args.indice.parent.joinpath(*pp.parts).exists():omitted_optional.append(role);continue
        file=safe(args.indice.parent,item['file']);encoded=file.read_bytes();need(sha(encoded)==item['sha256'],'Exact whole compressed snapshot bytes')
        view,norm=parse(encoded,item['life_id']);expected=item.get('expected_physical')
        if expected is not None:need(all(view['physical'][k]==v for k,v in expected.items()),'Declared physical identity must match actual bytes')
        views[role]=view;norms[role]=norm
    need({'neutral','learned','replay'}<=set(views),'All three Native snapshots required for this analysis')
    differences=diff(norms['learned'],norms['replay']);raw_equal=views['learned']['physical']==views['replay']['physical'];binary_equal=views['learned']['causal_prefix_sha256']==views['replay']['causal_prefix_sha256']
    result={'schema':'DEE.PI10.portable_snapshot_prefix_analysis.R01','Native_executed':False,'DEE_imported':False,'index_sha256':sha(ib),'snapshots':views,'optional_snapshot_roles_not_transported':omitted_optional,
      'learned_replay_comparison':{'physical_equal':raw_equal,'binary_causal_prefix_equal':binary_equal,'structured_equal_after_exact_transport_labels':not differences,
        'unexplained_different_paths':differences,'all_other_parsed_fields_and_fixed_bytes_checked':True},
      'scope':'Archived bytes only. No snapshot loaded, world advanced, SQLite opened or full code/artifact/environment state compared. Actual cold Native reproduction and full local operational verification remain separate evidence. Current-label normalization is explicit and never described as binary equality.'}
    with args.salida.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'file':str(args.salida),'sha256':sha(args.salida.read_bytes()),'physical_equal':raw_equal,'structured_equal':not differences,'Native_executed':False}))
if __name__=='__main__':main()
