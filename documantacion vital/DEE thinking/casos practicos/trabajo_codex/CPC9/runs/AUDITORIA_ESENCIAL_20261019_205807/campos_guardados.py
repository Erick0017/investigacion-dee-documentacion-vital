"""Independently extract physical uint64 fields; never loads a Runtime.

Only decodes the documented DEETSNP1/version2 data envelope. It is not a DEE
transition implementation. Metadata/channels/queues are deliberately not copied.
"""
from pathlib import Path
from collections import Counter
import argparse,struct,gzip,hashlib,json,itertools,sys,zipfile,base64,zlib
sys.stdout.reconfigure(encoding='utf8')
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'),sort_keys=True).encode('utf8')
def decode(b):
    if b[:8]!=b'DEETSNP1':raise ValueError('Unknown native envelope')
    ver,n=struct.unpack_from('<II',b,8);tick=struct.unpack_from('<Q',b,16)[0]
    if ver!=2 or not 1<=n<=512:raise ValueError('Undocumented snapshot version/domain')
    length=struct.unpack_from('<I',b,41)[0];count_offset=45+length;count=struct.unpack_from('<Q',b,count_offset)[0];start=count_offset+8
    if count!=n**3 or start+16*count>len(b)-8:raise ValueError('Truncated physical arrays')
    raw=b[start:start+count*8];clocks=b[start+count*8:start+count*16]
    # Native envelope uses this documented project seed, not the standard FNV
    # offset basis. It is a container check, not a physical transition rule.
    h=1469598103934665603
    for v in b[:-8]:h=((h^v)*1099511628211)&((1<<64)-1)
    if h!=struct.unpack_from('<Q',b,len(b)-8)[0]:raise ValueError('Native envelope checksum mismatch')
    return n,tick,raw,clocks,start
def values(b):return(v[0]for v in struct.iter_unpack('<Q',b))
def rle(b):return[[sum(1 for _ in g),str(v)]for v,g in itertools.groupby(values(b))]
def stats(b):
    c=Counter();s=Counter();occupied=alive=directional=cap=0;maxload=0
    for v in values(b):
        state=v&0xffffffff;sem=v>>60;load=(v>>32)&65535
        c[str(sem)]+=1;s[str(state)]+=1;occupied+=state>0;alive+=state>0 and sem!=5;directional+=bool((v>>48)&4095);cap+=load>=19664;maxload=max(maxload,load)
    return{'sites':len(b)//8,'occupied_state_gt0':occupied,'alive_except_sem5':alive,'directional_fields_nonzero':directional,'semantic_counts':dict(c),'state_counts':dict(s),'max_s_reg':maxload,'at_or_above_reducer_cap':cap}
def inflate(runs,count):
    out=bytearray()
    for length,v in runs:
        if type(length)is not int or not 1<=length<=count or not isinstance(v,str)or not v.isdecimal()or not 0<=int(v)<2**64:raise ValueError('Invalid uint64 RLE')
        out.extend(struct.pack('<Q',int(v))*length)
        if len(out)>count*8:raise ValueError('Oversized RLE')
    if len(out)!=count*8:raise ValueError('Incomplete RLE')
    return bytes(out)
def array_bytes(d,key,base_dir=None,_stack=None):
    count=d['N']**3
    if not 0<count<=1_000_000:raise ValueError('Audit array size outside declared domain')
    if key+'_RLE'in d:return inflate(d[key+'_RLE'],count)
    delta=d.get(key+'_DELTA');encoded=delta['residual_ZLIB_BASE64']if delta else d[key+'_ZLIB_BASE64']
    packed=base64.b64decode(encoded,validate=True);dec=zlib.decompressobj();b=dec.decompress(packed,count*8+1)
    if len(b)!=count*8 or not dec.eof or dec.unused_data or dec.unconsumed_tail:raise ValueError('Invalid bounded compressed physical array')
    if delta:
        if base_dir is None:raise ValueError('A declared same-folder base is required')
        name=delta['base_file']
        if Path(name).name!=name or any(c in name for c in('/','\\',':')):raise ValueError('Unsafe physical field base')
        stack=set()if _stack is None else set(_stack);tag=(name,key)
        if tag in stack:raise ValueError('Cyclic field delta')
        stack.add(tag);base=json.loads((Path(base_dir)/name).read_bytes())
        if base['N']!=d['N']:raise ValueError('Physical field dimension mismatch')
        old=array_bytes(base,key,base_dir,stack);out=bytearray(count*8)
        for i,(previous,residual)in enumerate(zip(values(old),values(b))):
            value=previous^residual if delta['operation']=='XOR'else(previous+delta['offset']+residual)&((1<<64)-1)if delta['operation']=='ADD_OFFSET_MOD2_64'else None
            if value is None:raise ValueError('Unknown lossless field delta')
            struct.pack_into('<Q',out,i*8,value)
        b=bytes(out)
    expected=d['physical']['RAW_sha256'if key=='RAW'else'clocks_sha256']
    if sha(b)!=expected:raise ValueError('Decoded physical-array SHA mismatch')
    return b
def main():
    p=argparse.ArgumentParser();p.add_argument('--zip',type=Path);p.add_argument('--out',required=True,type=Path);p.add_argument('--verify-only',action='store_true');p.add_argument('--compact',action='store_true');a=p.parse_args()
    if a.verify_only:
        rows=[]
        for f in sorted(a.out.glob('S*.json')):
            d=json.loads(f.read_bytes());raw=array_bytes(d,'RAW',f.parent);clock=array_bytes(d,'CLOCKS',f.parent)
            if sha(raw)!=d['physical']['RAW_sha256']or sha(clock)!=d['physical']['clocks_sha256']or stats(raw)!=d['independently_recounted']:raise ValueError('Saved-field verification failed')
            rows.append({'file':f.name,'tick':d['physical']['tick'],'occupied':stats(raw)['occupied_state_gt0'],'source':d['source_snapshot']})
        print(json.dumps({'status':'PASS','count':len(rows),'rows':rows,'engine_imported':False},ensure_ascii=False));return
    if a.out.exists()and any(a.out.iterdir()):raise FileExistsError('Use a new extraction destination')
    a.out.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.zip)as z:
        obs=json.loads(z.read('CPC9/resultados/auditoria/OCUPACION_Y_RESTAURACION/MEDICIONES.json'));report=[]
        for i,row in enumerate(obs['rows']):
            name='CPC9/'+row['member'];b=z.read(name)
            if sha(b)!=row['sha256']:raise ValueError('Snapshot original hash mismatch')
            decoded=gzip.decompress(b);n,tick,raw,clocks,offset=decode(decoded);physical={'tick':tick,'RAW_sha256':sha(raw),'clocks_sha256':sha(clocks)}
            actual=stats(raw);expected={k:v for k,v in row['statistics'].items()if k!='note'}
            if physical!=row['physical']or actual!=expected:raise ValueError('Independent field recount differs: '+name)
            data={'schema':'CPC9.audit.exact.physical_fields.v1','source_snapshot':{'archive':a.zip.name,'archive_sha256':'917a559b917388fc63a6948762d73c3e87a00c30199c5b65c635a8d39bf96bad','member':name,'sha256':sha(b),'decoded_sha256':sha(decoded),'decoded_bytes':len(decoded),'array_offset_bytes':offset},
              'N':n,'cell_order':'Exact native vector order; array identity verified against recorded full-array SHA. No field is a float.',
              'physical':physical,'independently_recounted':actual,
              'excluded':'Native channels/queues/session metadata and unselected checkpoints. This physical extraction is NOT a restorable operational snapshot.'}
            if a.compact:
                data.update(array_encoding='base64(zlib(uint64 little-endian bytes)); lossless; parser capped by declared N',RAW_ZLIB_BASE64=base64.b64encode(zlib.compress(raw,9)).decode('ascii'),CLOCKS_ZLIB_BASE64=base64.b64encode(zlib.compress(clocks,9)).decode('ascii'))
            else:data.update(RAW_RLE=rle(raw),CLOCKS_RLE=rle(clocks))
            if array_bytes(data,'RAW')!=raw or array_bytes(data,'CLOCKS')!=clocks:raise ValueError('Physical arrays did not reconstruct exactly')
            f=a.out/('S'+str(i).zfill(2)+'_T'+str(tick)+'.json');f.write_bytes(canon(data)+b'\n')
            report.append({'file':f.name,'sha256':sha(f.read_bytes()),'physical':physical,'source':data['source_snapshot'],'all_statistics_equal':True,'source_statistics_member':'CPC9/resultados/auditoria/OCUPACION_Y_RESTAURACION/MEDICIONES.json'})
    (a.out/'EXTRACCION_CAMPOS.json').write_text(json.dumps({'status':'PASS','engine_imported':False,'records':report},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'PASS','field_states':len(report),'bytes':sum(f.stat().st_size for f in a.out.iterdir()),'engine_imported':False}))
if __name__=='__main__':main()
