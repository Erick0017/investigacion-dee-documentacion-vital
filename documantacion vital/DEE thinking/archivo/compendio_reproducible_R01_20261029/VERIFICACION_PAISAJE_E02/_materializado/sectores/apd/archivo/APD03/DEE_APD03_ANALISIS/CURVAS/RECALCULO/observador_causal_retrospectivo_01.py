"""Read-only snapshot-v2 and sparse-field observer. No engine or tick API.

Format follows the frozen runtime serializer. Parsing never constructs a world,
executes metadata, imports a participant or edits a saved snapshot.
"""
from pathlib import Path
from array import array
from collections import Counter
import struct,gzip,json,hashlib,sys

MASK=(1<<64)-1
LIFE_KEY='DEE.Cognitive.System.1.1.life.v1'
def sha(b):return hashlib.sha256(b).hexdigest()
def fnv(b):
    h=1469598103934665603
    for v in b:h=((h^v)*1099511628211)&MASK
    return h
class Reader:
    def __init__(self,b):self.b=b;self.i=0
    def take(self,n):
        if n<0 or n>len(self.b)-self.i:raise ValueError('Truncated or oversized snapshot')
        v=self.b[self.i:self.i+n];self.i+=n;return v
    def u8(self):return self.take(1)[0]
    def u32(self):return struct.unpack('<I',self.take(4))[0]
    def u64(self):return struct.unpack('<Q',self.take(8))[0]
    def i32(self):return struct.unpack('<i',self.take(4))[0]
    def text(self):
        n=self.u32()
        if n>16*1024**2:raise ValueError('Oversized snapshot text')
        return self.take(n).decode('utf8')
    def coord(self):return[self.i32(),self.i32(),self.i32()]
    def count(self,maximum=1000000):
        n=self.u32()
        if n>maximum:raise ValueError('Oversized item count')
        return n
def qarray(b):
    v=array('Q');v.frombytes(b)
    if sys.byteorder!='little':v.byteswap()
    return v
def pbytes(a):
    v=array('Q',a)
    if sys.byteorder!='little':v.byteswap()
    return v.tobytes()
def coord(i,n):return[i//(n*n),(i//n)%n,i%n]
def index(p,n):return(p[0]*n+p[1])*n+p[2]
def fields(v):
    def signed(k):x=(v>>k)&15;return x-16 if x&8 else x
    return{'raw':str(v),'state':v&0xffffffff,'s_reg':(v>>32)&65535,'direction':[signed(k)for k in(48,52,56)],'semantic':(v>>60)&15}
def load_json(p):
    p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
class Snapshot:
    def __init__(self,path,verify_checksum=True,data=None):
        self.path=Path(path);encoded=self.path.read_bytes()if data is None else data;self.encoded_bytes=len(encoded);b=gzip.decompress(encoded)if encoded[:2]==b'\x1f\x8b'else encoded
        if len(b)>2*1024**3:raise ValueError('Bounded snapshots only')
        self.b=b;self.encoded_sha256=sha(encoded);self.decoded_sha256=sha(b);self.checksum=struct.unpack('<Q',b[-8:])[0]
        self.checksum_valid=fnv(b[:-8])==self.checksum if verify_checksum else None
        if self.checksum_valid is False:raise ValueError('Snapshot checksum mismatch')
        r=Reader(b[:-8])
        if r.take(8)!=b'DEETSNP1'or r.u32()!=2:raise ValueError('Only known v2 snapshot format')
        self.N=r.u32();self.tick=r.u64();self.paused=r.u8();self.next_event_id=r.u64();self.next_sequence=r.u64();self.phase=r.text();self.total=r.u64()
        if self.total!=self.N**3 or self.total>128**3*4:raise ValueError('Invalid field dimensions')
        self.raw_offset=r.i;self.raw=qarray(r.take(8*self.total));self.clock_offset=r.i;self.clocks=qarray(r.take(8*self.total));self.channels={}
        for _ in range(r.count(65536)):
            name=r.text();self.channels[name]={'site':r.coord(),'state':r.u32(),'direction':[r.i32(),r.i32(),r.i32()],'semantic':r.u8(),'allow_experience':r.u8(),'allow_probe':r.u8()}
        self.pending=[]
        for _ in range(r.count()):
            event={'boundary':r.u64(),'id':r.u64(),'kind':r.u8(),'requested_tick':r.u64(),'sequence':r.u64()};event['channels']=[r.text()for _ in range(r.count(65536))];event['writes']=[{'site':r.coord(),'raw':str(r.u64())}for _ in range(r.count(65536))];self.pending.append(event)
        self.receipts=[]
        for _ in range(r.count()):
            event={'id':r.u64(),'kind':r.u8(),'status':r.u8(),'requested_tick':r.u64()};event['effective_tick']=r.u64()if r.u8()else None;event['channels']=[r.text()for _ in range(r.count(65536))];event['reason']=r.text();self.receipts.append(event)
        self.backend=r.u8();self.threads=r.u64();self.metadata_offset=r.i;count=r.count(65536);self.metadata={};self.metadata_packets={}
        for _ in range(count):
            start=r.i;key=r.text();value=r.text()
            if key in self.metadata:raise ValueError('Duplicate metadata')
            self.metadata[key]=value;self.metadata_packets[key]=b[start:r.i]
        if r.i!=len(b)-8:raise ValueError('Trailing or unparsed snapshot bytes')
    def normalized_bytes(self,exclude=()):
        keys=[key for key in self.metadata if key not in exclude];b=self.b[:self.metadata_offset]+struct.pack('<I',len(keys))+b''.join(self.metadata_packets[key]for key in keys);return b+struct.pack('<Q',fnv(b))
    def observation(self,site):
        i=index(site,self.N);return{'tick':self.tick,'site':site,'clock':str(self.clocks[i]),**fields(self.raw[i])}
    def summary(self):
        return{'path':str(self.path),'encoded_bytes':self.encoded_bytes,'encoded_sha256':self.encoded_sha256,'native_bytes':len(self.b),'native_sha256':self.decoded_sha256,'checksum_valid':self.checksum_valid,'N':self.N,'tick':self.tick,'RAW_sha256':sha(pbytes(self.raw)),'clocks_sha256':sha(pbytes(self.clocks)),'raw_nonzero':sum(v!=0 for v in self.raw),'occupied':sum(bool(v&0xffffffff)for v in self.raw),'state_zero_raw_nonzero':sum(bool(v)and not(v&0xffffffff)for v in self.raw),'channels':len(self.channels),'pending_count':len(self.pending),'receipts':len(self.receipts),'metadata_keys':list(self.metadata),'backend':self.backend,'threads':self.threads,'no_native_ticks_executed':True}
def frame_arrays(q):
    n=q['N'];raw=array('Q',[0])*(n**3);clocks=array('Q',[int(q['clock_default'])])*(n**3)
    for i,v,c in q['rows']:raw[i]=int(v)
    if q['clock_exceptions']is None:raise ValueError('Incomplete clocks cannot establish whole-state equality')
    for i,c in q['clock_exceptions']:clocks[i]=int(c)
    for i,v,c in q['rows']:
        if clocks[i]!=int(c):raise ValueError('Sparse row clock disagrees with full clocks')
    if sha(pbytes(raw))!=q['RAW_sha256']or sha(pbytes(clocks))!=q['clocks_sha256']:raise ValueError('Sparse frame reconstruction mismatch')
    return raw,clocks
def walk(v,loc='$'):
    if isinstance(v,dict):
        yield loc,v
        if v.get('schema')=='DCS1.1.life.v1':return
        for k,x in v.items():
            if k not in('parent_current','parent','initial_record','final_record','reached_record'):yield from walk(x,loc+'.'+k)
    elif isinstance(v,list):
        for j,x in enumerate(v):yield from walk(x,loc+'['+str(j)+']')

class OrgReader(Reader):
    def text(self):return self.take(self.u64()).decode('utf8')
    def count(self,maximum=1048576):
        n=self.u64()
        if n>maximum:raise ValueError('Organizational collection too large')
        return n
    def i64(self):return struct.unpack('<q',self.take(8))[0]
    def coord(self):return[self.i64(),self.i64(),self.i64()]
    def optional(self):return self.coord()if self.u8()else None
    def obs(self):return{'tick':self.u64(),'site':self.coord(),'raw':str(self.u64()),'clock':str(self.u64())}
    def symbols(self):return[(self.text(),self.u64())for _ in range(self.count())]
    def codec(self):return{'version':self.text(),'type':self.u8(),'minimum':self.i64(),'maximum':self.i64(),'symbols':self.symbols()}

def organization(s):
    """Decode all saved owner fields, without restoring or advancing an owner."""
    prefix='dee_thinking.organizational.v1.'
    if prefix+'chunks'not in s.metadata:return None
    n=int(s.metadata[prefix+'chunks']);b=bytes.fromhex(''.join(s.metadata[prefix+str(i)]for i in range(n)));r=OrgReader(b)
    if r.u64()!=1:raise ValueError('Unknown organizational schema')
    recipe={'id':r.text(),'version':r.text(),'N':r.i64(),'origin':r.coord(),'t0':r.u64(),'domain':r.text(),'backend':r.u8(),'threads':r.u64()}
    recipe['parameters']=[(r.text(),r.i64())for _ in range(r.count())];recipe['options']=[(r.text(),r.text())for _ in range(r.count())]
    recipe['placements']=[{'site':r.coord(),'raw':str(r.u64()),'clock':str(r.u64()),'role':r.text()}for _ in range(r.count())]
    recipe['organizations']=[]
    for _ in range(r.count()):
        q={'id':r.text(),'recipe_id':r.text(),'t0':r.u64(),'a':r.optional(),'b':r.optional(),'comparator':r.optional()};q['ports']=[(r.text(),r.coord())for _ in range(r.count())];q['supports']=[r.coord()for _ in range(r.count())];recipe['organizations'].append(q)
    recipe['interfaces']=[]
    for _ in range(r.count()):recipe['interfaces'].append({'name':r.text(),'channel':r.text(),'site':r.coord(),'state':r.u64(),'direction':r.coord(),'semantic':r.u8(),'allow_experience':r.u8(),'allow_probe':r.u8(),'codec':r.codec(),'admission':r.text(),'meaning_location':r.text()})
    recipe['actions']=[{'id':r.text(),'scope':r.text(),'sites':[r.coord()for _ in range(r.count())],'roles':[r.text()for _ in range(r.count())],'ticks':[r.u64()for _ in range(r.count())]}for _ in range(r.count())]
    q={'recipe':recipe,'protocols':[]}
    for _ in range(r.count()):
        p={'id':r.text(),'kind':r.text(),'modality':r.u8(),'next_capture':r.u64(),'steps':[]}
        for _ in range(r.count()):p['steps'].append({'input_tick':r.u64(),'read_tick':r.u64(),'input':r.i64(),'receipt_ids':[r.u64()for _ in range(r.count())],'targets':[r.coord()for _ in range(r.count())],'captured':[r.obs()for _ in range(r.count())]})
        q['protocols'].append(p)
    q['edits']=[{'site':r.coord(),'label':r.text(),'tick':r.u64(),'raw_before':str(r.u64()),'raw_after':str(r.u64()),'clock_before':str(r.u64()),'clock_after':str(r.u64()),'modality':r.u8()}for _ in range(r.count())]
    q['operations']=[r.text()for _ in range(r.count())]
    q['decoders']=[{'id':r.text(),'version':r.text(),'type':r.u8(),'symbols':r.symbols()}for _ in range(r.count())]
    q['has_trace']=r.u8()
    if q['has_trace']:
        t={'budget':r.u64(),'stopped':r.u8(),'sites':[(r.text(),r.coord())for _ in range(r.count())],'segments':[]}
        for _ in range(r.count()):
            v={'id':r.text(),'birth':r.coord(),'direction':r.coord(),'birth_tick':r.u64(),'last_tick':r.u64()};v['expected_load']=r.u64()if r.u8()else None;v['expected_semantic']=r.u8()if r.u8()else None;v['stopped']=r.u8();t['segments'].append(v)
        t['samples']=[{'id':r.text(),'tick':r.u64(),'observation':r.obs(),'relative':r.coord(),'unwrapped':r.coord(),'coverage':r.text()}for _ in range(r.count())];q['trace']=t
    if r.i!=len(b):raise ValueError('Unparsed organizational bytes')
    return q

def compare(a,b,sample_limit=24):
    if a.N!=b.N:return{'same_dimension':False,'warning':'Different architectures; no cellwise identity claim'}
    raw_indices=[i for i,(x,y)in enumerate(zip(a.raw,b.raw))if x!=y];clock_indices=[i for i,(x,y)in enumerate(zip(a.clocks,b.clocks))if x!=y]
    oa=organization(a);ob=organization(b)
    return{'same_dimension':True,'ticks':[a.tick,b.tick],'identical_file_bytes':a.b==b.b,'RAW_different_sites':len(raw_indices),'clock_different_sites':len(clock_indices),'differences_sample':[{'site':coord(i,a.N),'a':fields(a.raw[i]),'b':fields(b.raw[i]),'clock_a':str(a.clocks[i]),'clock_b':str(b.clocks[i])}for i in raw_indices[:sample_limit]],'prefix_through_execution_before_metadata_equal':a.b[:a.metadata_offset]==b.b[:b.metadata_offset],'pending_equal':a.pending==b.pending,'channels_equal':a.channels==b.channels,'receipts_equal':a.receipts==b.receipts,'different_metadata_keys':[k for k in sorted(set(a.metadata)|set(b.metadata))if a.metadata.get(k)!=b.metadata.get(k)],'different_owner_sections':[k for k in sorted(set(oa or{})|set(ob or{}))if(oa or{}).get(k)!=(ob or{}).get(k)],'no_native_ticks_executed':True,'scope':'Physical equality is not full-file equality. No metadata is silently excluded and no functional recovery is inferred from a difference.'}

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('snapshot');ap.add_argument('--owner',action='store_true');ap.add_argument('--comparar',type=Path);a=ap.parse_args();s=Snapshot(a.snapshot);result=s.summary()
    if a.owner:result['owner']=organization(s)
    if a.comparar:result['comparison']=compare(s,Snapshot(a.comparar))
    print(json.dumps(result,ensure_ascii=False,indent=2))
