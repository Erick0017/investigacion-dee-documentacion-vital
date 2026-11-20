"""Portable F1 q8 NativeSnapshot documentary comparison, stdlib only.
Parser extracted from the already sealed F1 instrument; no capacidades/DEE
imports, no world load, no Native replay or behavior claim. All paths indexed
below --raiz. Snapshot gzip CRC/full format is checked; Native internal FNV
not recomputed. Whole RAW/clocks are compared, including state0 RAW fields.
"""
from pathlib import Path,PurePosixPath
import argparse,gzip,hashlib,json,struct
PARSER_SOURCE_WRAPPER_SHA='6f1b3f524f0429881104ca437606f5cf868525718a58840edbab8af19fc2f0cc'
SITE=(52,48,56)
def sha(b):return hashlib.sha256(b).hexdigest()
def need(b,t):
    if not b:raise ValueError(t)
def local(root,e):
    name=e['file'];need(isinstance(name,str)and name and '\\'not in name and ':'not in name,'Portable indexed relative path')
    rel=PurePosixPath(name);need(not rel.is_absolute()and not any(x in ('.','..')for x in rel.parts),'Escaping path')
    q=root.joinpath(*rel.parts)
    for node in(q,*q.parents):
        if node==root.parent:break
        need(not node.is_symlink()and not(getattr(node.lstat(),'st_file_attributes',0)&1024),'No link/reparse')
    q=q.resolve(strict=True);need(q.is_relative_to(root),'Outside extraction')
    data=q.read_bytes();need(len(data)==e['bytes']and sha(data)==e['sha256'],'Indexed snapshot/evidence bytes differ')
    return q,data
def ptr(j,p):
    need(isinstance(p,str)and p.startswith('/'),'Explicit JSON pointer')
    for k in p[1:].split('/'):
        k=k.replace('~1','/').replace('~0','~');j=j[int(k)]if isinstance(j,list)else j[k]
    return j

class _Reader:
    def __init__(self,b):self.b=memoryview(b)[:-8];self.i=0
    def take(self,n):
        if n<0 or self.i+n>len(self.b):raise ValueError('Truncated Native diagnostic snapshot')
        value=self.b[self.i:self.i+n];self.i+=n;return value
    def u8(self):return self.take(1)[0]
    def u32(self):return struct.unpack('<I',self.take(4))[0]
    def u64(self):return struct.unpack('<Q',self.take(8))[0]
    def count(self):
        n=self.u32()
        if n>1000000:raise ValueError('Native snapshot count bound')
        return n
    def text(self):
        n=self.u32()
        if n>16*1024*1024:raise ValueError('Native snapshot string bound')
        return self.take(n).tobytes().decode('utf-8')
    def skip_text(self):
        n=self.u32()
        if n>16*1024*1024:raise ValueError('Native snapshot string bound')
        self.take(n)

def _snapshot_fields(path,keep_raw=False):
    encoded=Path(path).read_bytes();payload=gzip.decompress(encoded);r=_Reader(payload)
    if r.take(8).tobytes()!=b'DEETSNP1'or r.u32()!=2:raise ValueError('Native v2 snapshot required')
    n=r.u32();tick=r.u64();paused=r.u8();next_id=r.u64();next_sequence=r.u64();phase=r.text();count=r.u64()
    if n!=67 or count!=n**3:raise ValueError('Exact complete N67 snapshot required')
    raw=r.take(count*8);clocks=r.take(count*8)
    raw_hash=sha(raw);clock_hash=sha(clocks);raw_copy=raw.tobytes()if keep_raw else None;clock_copy=clocks.tobytes()if keep_raw else None
    start=r.i;nc=r.count()
    for _ in range(nc):r.skip_text();r.take(31)
    channel_hash=sha(r.b[start:r.i]);start=r.i;npending=r.count()
    for _ in range(npending):
        r.take(8+8+1+8+8)
        for _ in range(r.count()):r.skip_text()
        r.take(20*r.count())
    pending_hash=sha(r.b[start:r.i]);start=r.i;nreceipts=r.count()
    for _ in range(nreceipts):
        r.take(8+1+1+8)
        if r.u8():r.take(8)
        for _ in range(r.count()):r.skip_text()
        r.skip_text()
    receipt_hash=sha(r.b[start:r.i]);backend=r.u8();threads=r.u64();causal=sha(r.b[:r.i]);metadata_start=r.i;nm=r.count()
    for _ in range(nm):r.skip_text();r.skip_text()
    if r.i!=len(r.b):raise ValueError('Unparsed Native diagnostic bytes')
    return {'snapshot':{'path':str(path),'bytes':len(encoded),'sha256':sha(encoded)},
        'N':n,'tick':tick,'RAW_sha256':raw_hash,'clocks_sha256':clock_hash,'paused':bool(paused),
        'next_event_id':next_id,'next_sequence':next_sequence,'phase':phase,'interfaces_count':nc,
        'interfaces_sha256':channel_hash,'pending_count':npending,'pending_sha256':pending_hash,
        'receipts_count':nreceipts,'receipts_sha256':receipt_hash,'backend':backend,'threads':threads,
        'Native_causal_prefix_sha256':causal,'metadata_key_count':nm,
        'metadata_serialized_sha256':sha(r.b[metadata_start:r.i]),
        'Native_complete_content_sha256':sha(r.b[:r.i]),
        'verification_scope':'Gzip CRC and full Native-v2 parse; internal Native FNV not separately recalculated.'},(raw_copy,clock_copy)

def calculate(root,index_name):
    root=Path(root).resolve(strict=True);rel=PurePosixPath(index_name)
    need(not rel.is_absolute()and '..'not in rel.parts and ':'not in index_name and '\\'not in index_name,'Relative index')
    ip=root.joinpath(*rel.parts);index=json.loads(ip.read_text('utf-8-sig'))
    need(index['schema']=='DEE.PI08.F1.portable_snapshot_triplet.R03','Exact F1 diagnostic index')
    need(index['fixed_site']==list(SITE)and index['raw_cut_value']==0 and index['clock_edit']is None,'Fixed postformation RAWonly cut')
    bp,bb=local(root,index['before']);cp,cb=local(root,index['cut'])
    before,(br,bc)=_snapshot_fields(bp,True);cut,(cr,cc)=_snapshot_fields(cp,True)
    need(before['N']==cut['N']==67 and before['tick']==cut['tick'],'Same declared N/tick cut')
    idx=((SITE[0]*67+SITE[1])*67+SITE[2])*8
    rb=struct.unpack_from('<Q',br,idx)[0];ra=struct.unpack_from('<Q',cr,idx)[0]
    direction=[((rb>>s)&15)-16 if((rb>>s)&15)&8 else((rb>>s)&15)for s in(48,52,56)]
    need(rb&0xffffffff>0 and rb>>60==1 and(rb>>32)&65535==0 and direction==[-1,0,1],'Actual fixed postformation signature absent; no alternative sought')
    expected=bytearray(br);expected[idx:idx+8]=bytes(8)
    need(ra==0 and bytes(expected)==cr,'Cut differs beyond the one exact declared RAW site')
    need(bc==cc,'Complete clocks differ')
    fields=('N','tick','paused','next_event_id','next_sequence','phase','interfaces_count','interfaces_sha256','pending_count','pending_sha256','receipts_count','receipts_sha256','backend','threads','metadata_key_count','metadata_serialized_sha256')
    equal={k:before[k]==cut[k]for k in fields};need(all(equal.values()),'Additional serialized Native field changed')
    clock=struct.unpack_from('<Q',bc,idx)[0]
    identity=None
    if index.get('identity'):
        q,data=local(root,index['identity']);value,_=_snapshot_fields(q,False)
        need(value['Native_complete_content_sha256']==before['Native_complete_content_sha256'],'Identity Native content differs')
        need(all(value[k]==before[k]for k in fields),'Identity Native metadata/phase/agenda differs')
        identity={'mode':'FULL_SNAPSHOT_REPARSED','path':index['identity']['file'],'Native_complete_content_equal':True,'Native_future_ticks':0,'snapshot':value}
    else:
        report=index['identity_report'];need(index.get('identity_omission_reason'),'Explicit omission reason required')
        q,data=local(root,report['evidence']);record=json.loads(data)
        need(ptr(record,report['full_content_sha256_pointer'])==before['Native_complete_content_sha256'],'Reported identity full hash differs')
        need(ptr(record,report['future_ticks_pointer'])==0,'Identity future must not be presented as executed')
        identity={'mode':'REPORTED_FULL_HASH_BOUND_TO_INCLUDED_PROOF_NOT_SNAPSHOT_REPARSED','Native_complete_content_hash_matches':True,'Native_future_ticks_reported':0,'evidence':report,'omission_reason':index['identity_omission_reason']}
    return{'schema':'DEE.PI08.F1.recalculated_snapshot_cut.R03','all_checks_passed':True,'new_Native_ticks':0,'DEE_imports':0,
       'index_sha256':sha(ip.read_bytes()),'parser_source_wrapper_sha256':PARSER_SOURCE_WRAPPER_SHA,
       'before':before,'cut':cut,'identity':identity,'exact_changed_RAW_sites':1,
       'site':list(SITE),'before_RAW':str(rb),'after_RAW':str(ra),'before_clock':str(clock),'after_clock':str(clock),
       'complete_RAW_expected_one_site_patch_exact':True,'complete_clocks_bytes_equal':True,'preserved_Native_fields':equal,
       'scope':'Documentary comparison of actual frozen Native snapshots only. This neither runs the engine nor establishes a functional effect or a new sham future; pre-existing intact Native continuation is separate evidence. No unique carrier lineage inferred.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--raiz',required=True);ap.add_argument('--indice',default='INDICE_F1_Q8_PI08_R03.json');ap.add_argument('--salida',required=True);a=ap.parse_args()
    out=Path(a.salida);need(not out.exists(),'Fresh output only');v=calculate(a.raiz,a.indice)
    with out.open('x',encoding='utf-8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'all_checks_passed':True,'new_Native_ticks':0,'identity_scope':v['identity']['mode'],'sha256':sha(out.read_bytes())},ensure_ascii=False))
if __name__=='__main__':main()
