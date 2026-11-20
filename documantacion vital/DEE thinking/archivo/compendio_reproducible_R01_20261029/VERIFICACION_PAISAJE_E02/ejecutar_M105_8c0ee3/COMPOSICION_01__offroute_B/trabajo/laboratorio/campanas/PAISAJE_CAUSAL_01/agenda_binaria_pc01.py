"""Passive bounded reader of the official runtime snapshot-v2queue section.

Only parses fresh output of the already validated official serializer. No
deserialization of arbitrary Python/code and no writes to a world.
"""
from pathlib import Path
import hashlib,struct,tempfile
class Reader:
    def __init__(self,b):self.b=b;self.i=0
    def take(self,n):
        if n<0 or self.i+n>len(self.b):raise ValueError('Truncatednativequeueextraction')
        v=self.b[self.i:self.i+n];self.i+=n;return v
    def u8(self):return self.take(1)[0]
    def u32(self):return struct.unpack('<I',self.take(4))[0]
    def u64(self):return struct.unpack('<Q',self.take(8))[0]
    def i32(self):return struct.unpack('<i',self.take(4))[0]
    def text(self):
        n=self.u32()
        if n>1048576:raise ValueError('Oversizedsnapshotstring')
        return self.take(n).decode('utf8')
    def coord(self):return[self.i32(),self.i32(),self.i32()]
def queue_state(rt):
    with tempfile.TemporaryDirectory(prefix='pc01-queue-')as folder:
        p=Path(folder)/'world.deetsnap';rt.save_snapshot(str(p));b=p.read_bytes()
    r=Reader(b)
    if r.take(8)!=b'DEETSNP1'or r.u32()!=2:raise ValueError('Onlydocumentedofficialsnapshot-v2isparsed')
    n=r.u32();tick=r.u64();paused=r.u8();eventid=r.u64();sequence=r.u64();phase=r.text();count=r.u64()
    if count!=n**3 or len(b)>2*1024**3:raise ValueError('Invalidnativebuffersize')
    header_bytes=b[:r.i]
    r.take(16*count);channels={};nc=r.u32()
    if nc>65536:raise ValueError('Nativechannellimit')
    for j in range(nc):
        name=r.text();channels[name]={'site':r.coord(),'state':r.u32(),'direction':[r.i32(),r.i32(),r.i32()],'semantic':r.u8(),'allow_experience':bool(r.u8()),'allow_probe':bool(r.u8())}
    pending=[];np=r.u32()
    if np>1000000:raise ValueError('Pendingeventbound')
    for j in range(np):
        boundary=r.u64();eid=r.u64();kind=r.u8();requested=r.u64();seq=r.u64();nc=r.u32()
        if nc>65536:raise ValueError('Eventchannellimit')
        names=[r.text()for _ in range(nc)];nw=r.u32()
        if nw>65536:raise ValueError('Eventwritelimit')
        writes=[{'site':r.coord(),'raw':str(r.u64())}for _ in range(nw)];pending.append({'boundary':boundary,'id':eid,'kind':kind,'requested_tick':requested,'sequence':seq,'channels':names,'writes':writes})
    return{'schema':'PC01.nativequeue.snapshotv2.extraction','native_snapshot_sha256':hashlib.sha256(b).hexdigest(),'native_snapshot_bytes':len(b),'header_bytes_hex':header_bytes.hex(),'N':n,'tick':tick,'paused':bool(paused),'next_event_id':eventid,'next_sequence':sequence,'protocol_phase':phase,'channels':channels,'pending':pending,'boundary_semantics':'Frameattisaidbeforeinputsadmittedatt;applyadmittedwriteswithoutalteringclock,thenF_v27. Notfromanassumedemptyqueue.'}
