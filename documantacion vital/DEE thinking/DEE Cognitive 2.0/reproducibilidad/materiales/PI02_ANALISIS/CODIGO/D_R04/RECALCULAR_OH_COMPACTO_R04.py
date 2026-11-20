"""Lossless compact O/H Native-snapshot comparison; stdlib, no DEE or ticks.

--export-on/--export-off create a DERIVED byte archive: one exact common
causal prefix and two exact suffixes. Concatenating each pair reproduces every
uncompressed byte of each original Native snapshot, without duplicating the
shared RAW/clocks/interfaces/agenda/receipts/progress. It is not a complete
Cognitive operating backup (no SQLite or external owner state is included).
"""
from pathlib import Path
import argparse,gzip,hashlib,json,struct
SYSTEM_KEY='DEE.Cognitive.System.1.1.life.v1'
SERVICE_KEY='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'

def sha(b):return hashlib.sha256(b).hexdigest()

class Reader:
    def __init__(self,b):self.b=b;self.i=0
    def take(self,n):
        if n<0 or self.i+n>len(self.b):raise ValueError('Truncated Native byte record')
        out=self.b[self.i:self.i+n];self.i+=n;return out
    def u8(self):return self.take(1)[0]
    def u32(self):return struct.unpack('<I',self.take(4))[0]
    def u64(self):return struct.unpack('<Q',self.take(8))[0]
    def text(self):
        n=self.u32()
        if n>16*1024**2:raise ValueError('Native text outside parser bound')
        return self.take(n).decode('utf-8')
    def count(self):
        n=self.u32()
        if n>1000000:raise ValueError('Native collection outside parser bound')
        return n

def view(b):
    r=Reader(b[:-8])
    if r.take(8)!=b'DEETSNP1'or r.u32()!=2:raise ValueError('Declared Native snapshot v2 required')
    n=r.u32();tick=r.u64();paused=r.u8();next_event=r.u64();next_sequence=r.u64();phase=r.text();total=r.u64()
    if total!=n**3 or total>128**3*4:raise ValueError('Native dimensions outside parser bound')
    raw=r.take(8*total);clocks=r.take(8*total);channels=r.count()
    for _ in range(channels):r.text();r.take(12+4+12+3)
    pending=r.count()
    for _ in range(pending):
        r.take(8+8+1+8+8)
        for _ in range(r.count()):r.text()
        for _ in range(r.count()):r.take(12+8)
    receipts=r.count()
    for _ in range(receipts):
        r.take(8+1+1+8)
        if r.u8():r.take(8)
        for _ in range(r.count()):r.text()
        r.text()
    r.u8();r.u64();prefix=r.i;metadata={}
    for _ in range(r.count()):
        k=r.text();v=r.text()
        if k in metadata:raise ValueError('Duplicate metadata key')
        metadata[k]=v
    if r.i!=len(b)-8:raise ValueError('Unparsed Native bytes')
    return {'N':n,'tick':tick,'paused':paused,'next_event':next_event,'next_sequence':next_sequence,'phase':phase,
            'RAW_sha256':sha(raw),'clocks_sha256':sha(clocks),'interfaces':channels,'pending_native':pending,
            'native_receipts':receipts,'causal_prefix_bytes':prefix,'causal_prefix_sha256':sha(b[:prefix]),'metadata':metadata}

def export(on,off,home):
    sources=[];decoded=[];views=[]
    for label,path in [('ON',on),('OFF',off)]:
        encoded=path.read_bytes();b=gzip.decompress(encoded);v=view(b)
        sources.append({'arm':label,'original_path':str(path.resolve()),'original_encoded_bytes':len(encoded),
                        'original_encoded_sha256':sha(encoded),'decoded_bytes':len(b),'decoded_sha256':sha(b)})
        decoded.append(b);views.append(v)
    prefix=views[0]['causal_prefix_bytes']
    if views[1]['causal_prefix_bytes']!=prefix or decoded[0][:prefix]!=decoded[1][:prefix]:raise ValueError('The declared common causal prefix is not equal')
    parts={'COMMON_CAUSAL_PREFIX.bin.gz':decoded[0][:prefix],'ON_SUFFIX.bin.gz':decoded[0][prefix:],'OFF_SUFFIX.bin.gz':decoded[1][prefix:]}
    rows=[];home.mkdir(parents=True,exist_ok=True)
    for name,b in parts.items():
        encoded=gzip.compress(b,compresslevel=9,mtime=0);dest=home/name
        if dest.exists()and dest.read_bytes()!=encoded:raise ValueError('Existing derived archive differs')
        dest.write_bytes(encoded);rows.append({'file':name,'bytes':len(encoded),'sha256':sha(encoded),'decoded_bytes':len(b),'decoded_sha256':sha(b)})
    index={'schema':'PI02.OH.lossless_native_byte_archive.v1','derived':True,'new_ticks':0,'DEE_imports':0,'sources':sources,'parts':rows,
           'reconstruction':'gzip.decompress(COMMON_CAUSAL_PREFIX)+gzip.decompress(ARM_SUFFIX) exactly equals the original decompressed Native snapshot bytes',
           'limits':['Original gzip container bytes are identified by hash but not reproduced; every uncompressed Native byte is retained',
                     'Trailing Native checksum bytes are retained unchanged; this tool verifies SHA-256/Gzip CRC, not the separate Native FNV checksum',
                     'Native-only evidence, not a full Cognitive operational backup; no SQLite is read or copied']}
    (home/'INDICE_OH_BYTES_DERIVADOS.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def verify(home):
    index=json.loads((home/'INDICE_OH_BYTES_DERIVADOS.json').read_text(encoding='utf-8'));parts={}
    for item in index['parts']:
        name=item['file']
        if Path(name).name!=name or ':'in name:raise ValueError('Unsafe archive member')
        encoded=(home/name).read_bytes();b=gzip.decompress(encoded)
        if len(encoded)!=item['bytes']or sha(encoded)!=item['sha256']or len(b)!=item['decoded_bytes']or sha(b)!=item['decoded_sha256']:raise ValueError('Derived part identity mismatch')
        parts[name]=b
    views=[];sources=[]
    for source in index['sources']:
        b=parts['COMMON_CAUSAL_PREFIX.bin.gz']+parts[source['arm']+'_SUFFIX.bin.gz']
        if len(b)!=source['decoded_bytes']or sha(b)!=source['decoded_sha256']:raise ValueError('Full decompressed Native reconstruction identity mismatch')
        views.append(view(b));sources.append({'arm':source['arm'],'decoded_bytes':len(b),'decoded_sha256':sha(b)})
    a,b=views;excluded={SYSTEM_KEY}|{k for k in set(a['metadata'])|set(b['metadata'])if k==SERVICE_KEY or k.startswith(SERVICE_KEY+'.queue.')}
    differences=[]
    for k in sorted(set(a['metadata'])|set(b['metadata'])):
        if k not in excluded and a['metadata'].get(k)!=b['metadata'].get(k):differences.append(k)
    causal=a['causal_prefix_sha256']==b['causal_prefix_sha256'];errors=[]
    if not causal:errors.append('Different causal prefix')
    if differences:errors.append('Different nonadministrative metadata')
    return {'schema':'PI02.OH.compact_portable_recalculation.v1','new_ticks':0,'DEE_imports':0,'sources':sources,
            'physical_and_causal_views':[{k:v for k,v in x.items()if k!='metadata'}for x in views],
            'all_native_decompressed_bytes_reconstructed_and_sha_verified':True,'causal_prefix_exact_equal':causal,
            'metadata_entry_counts':[len(a['metadata']),len(b['metadata'])],
            'excluded_administrative_metadata_keys':sorted(excluded),'nonadministrative_metadata_differing_keys':differences,
            'complete_serialized_native_state_equal_except_declared_administrative_metadata':causal and not differences,
            'inconsistencies':errors,'limits':index['limits'],
            'scope':'Same134tick segmentation on a shared prefix, O/H getter observation versus no observation, no admitted habitat. No claim of universal passivity or equality of external Cognitive/SQLite state.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--evidence',type=Path,required=True);ap.add_argument('--export-on',type=Path);ap.add_argument('--export-off',type=Path);ap.add_argument('--result',type=Path,required=True);args=ap.parse_args()
    if bool(args.export_on)!=bool(args.export_off):raise ValueError('Both explicit immutable Native sources required')
    if args.export_on:export(args.export_on,args.export_off,args.evidence)
    result=verify(args.evidence);args.result.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2));return 2 if result['inconsistencies']else 0

if __name__=='__main__':raise SystemExit(main())
