"""Fixed global RAW/clocks capture through the existing legal adapter only.

No DEE import or execution at import. Arrays remain in external files, never
snapshot metadata or an actor decision. A captured frame is NOT a full life.
"""
from pathlib import Path
from array import array
import hashlib
import json
import os
import sys
import zlib

VERSION = 'DEE.PI05.passive_global_uint64_frames.R01'


def digest(b): return hashlib.sha256(b).hexdigest()
def canon(v): return (json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode('utf8')
def uint64_bytes(values):
    a=array('Q',values)
    if a.itemsize!=8: raise ValueError('Exact uint64 arrays required')
    if sys.byteorder!='little':a.byteswap()
    return a.tobytes()
def xor_bytes(left,right):
    if len(left)!=len(right)or len(left)%8:raise ValueError('Equal uint64 byte buffers required')
    a=array('Q');b=array('Q');a.frombytes(left);b.frombytes(right)
    return array('Q',(x^y for x,y in zip(a,b))).tobytes()
def regular_parent(path):
    for node in(path,*path.parents):
        if node.exists()and(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&0x400):
            raise ValueError('No linked/reparse telemetry path')


class GlobalRecorder:
    """One external bounded recording; no input/sensor/decoder/state mutation."""
    def __init__(self,directory,*,N,ticks,anchor_ticks,provenance,max_frames=1440,max_compressed_bytes=402653184):
        self.directory=Path(directory).absolute();regular_parent(self.directory)
        if self.directory.exists():raise ValueError('A new unused telemetry directory is required')
        if type(N)is not int or N<1:raise ValueError('Exact dimension required')
        if not all(type(x)is int and x>=0 for x in ticks):raise ValueError('Predeclared absolute Native ticks only')
        self.N=N;self.ticks=tuple(sorted(set(ticks)));self.anchors=set(anchor_ticks)
        if not self.anchors<=set(self.ticks)or len(self.ticks)>max_frames:raise ValueError('Frozen finite capture bounds exceeded')
        if not self.ticks or self.ticks[0]not in self.anchors:raise ValueError('The first prospective frame must be an explicit anchor')
        if len(self.anchors)>40 or max_frames>1440:raise ValueError('PI05 global frame/anchor ceiling')
        self.max_bytes=max_compressed_bytes;self.bytes=0;self.previous=None;self.rows=[];self.captured=set();self.closed=False
        self.directory.mkdir(parents=True,exist_ok=False)
        self.config={'schema':VERSION,'N':N,'byte_order':'little','index':'(x*N+y)*N+z',
            'ticks':list(self.ticks),'anchor_ticks':sorted(self.anchors),'provenance':provenance,
            'buffers':'Complete N^3 RAW and clocks, including state0/nonzeroRAW and stationary configurations',
            'not_a_full_operational_snapshot':True,'no_native_lineage_tags':True,'actor_receives_recording':False}
        with(self.directory/'CAPTURA.json').open('xb')as f:f.write(canon(self.config))

    def capture(self,adapter):
        if self.closed:raise ValueError('Recording already closed')
        rt=adapter.world.runtime;tick=int(rt.current_tick)
        if tick in self.captured:return
        if tick not in self.ticks:raise ValueError('No retrospective/favourable unplanned frame')
        if int(rt.dimension)!=self.N:raise ValueError('Dimension changed')
        # Same owner thread, between legal scheduler calls. No submit/probe/run.
        raw=uint64_bytes(rt.raw_copy());clocks=uint64_bytes(rt.clock_copy())
        if int(rt.current_tick)!=tick or int(adapter.tick)!=tick:raise RuntimeError('RAW/clocks were not read at one coherent tick boundary')
        size=8*self.N**3
        if len(raw)!=size or len(clocks)!=size:raise ValueError('Incomplete global buffers')
        complete=raw+clocks;anchor=self.previous is None or tick in self.anchors
        payload=complete if anchor else xor_bytes(complete,self.previous)
        compressed=zlib.compress(payload,6)
        if self.bytes+len(compressed)>self.max_bytes:raise ValueError('External telemetry storage allowance reached; preserve partial capture')
        seq=len(self.rows);name='%04d_T%d_%s.zlib'%(seq,tick,'anchor'if anchor else'xor')
        row={'sequence':seq,'tick':tick,'kind':'anchor'if anchor else'xor_uint64',
            'previous_sequence':None if anchor else seq-1,'file':name,'compressed_bytes':len(compressed),
            'uncompressed_bytes':len(payload),'payload_sha256':digest(payload),'compressed_sha256':digest(compressed),
            'RAW_sha256':digest(raw),'clocks_sha256':digest(clocks),'complete_buffers_sha256':digest(complete),
            'boundary':'After legal WorldAdapter/OrganizationalWorld.run_until, before the next advance',
            'no_material_query':True}
        with(self.directory/name).open('xb')as f:f.write(compressed)
        with(self.directory/'FRAMES.jsonl').open('ab')as f:f.write(canon(row));f.flush();os.fsync(f.fileno())
        self.rows.append(row);self.previous=complete;self.captured.add(tick);self.bytes+=len(compressed)

    def close(self):
        if self.closed:raise ValueError('Do not close/rewrite a capture twice')
        result={'schema':VERSION,'frames':self.rows,'planned_frames':len(self.ticks),'captured_frames':len(self.rows),
            'anchors':sum(r['kind']=='anchor'for r in self.rows),'xor_frames':sum(r['kind']!='anchor'for r in self.rows),
            'compressed_payload_bytes':self.bytes,'missing_planned_ticks':sorted(set(self.ticks)-self.captured),
            'scope':'External observation only. Native passivity must be tested on complete matched copies; no automatic passivity claim.'}
        with(self.directory/'INDEX.json').open('xb')as f:f.write(canon(result))
        self.closed=True;self.previous=None
        return {'directory':str(self.directory),'index_sha256':digest((self.directory/'INDEX.json').read_bytes()),
            'captured_frames':len(self.rows),'compressed_payload_bytes':self.bytes,'missing_planned_ticks':result['missing_planned_ticks']}


class CapturingAdapter:
    """Duck-typed existing FI adapter; only calls base.run_until, never Runtime.run.

    The approved FI128 caller ignores TickInfo return values. The last legal
    segment result is returned; this is not a universal wrapper for callers
    that aggregate TickInfo event counters.
    """
    def __init__(self,base,*,ticks,recorder=None):
        self.base=base;self.ticks=tuple(sorted(set(ticks)));self.recorder=recorder;self.boundaries=[]
    @property
    def world(self):return self.base.world
    @property
    def tick(self):return int(self.base.tick)
    def __getattr__(self,name):return getattr(self.base,name)
    def run_until(self,target):
        if type(target)is not int or target<self.tick:raise ValueError('No rewind or clock edit')
        result=None
        for t in self.ticks:
            if self.tick<=t<=target:
                if t>self.tick:result=self.base.run_until(t)
                if self.recorder is not None:self.recorder.capture(self.base)
                self.boundaries.append(t)
        if self.tick<target:result=self.base.run_until(target)
        return result


def iter_frames(directory):
    """Yield complete verified LE uint64 buffers; no DEE/source-path access.

    Each item has tick, raw_bytes, clocks_bytes, hashes, row and config. The
    generator retains only the previous complete frame; callers control memory.
    A consumer must exhaust it to validate the entire record.
    """
    root=Path(directory).resolve(strict=True);cfg=json.loads((root/'CAPTURA.json').read_text(encoding='utf8'))
    rows=[json.loads(x)for x in(root/'FRAMES.jsonl').read_text(encoding='utf8').splitlines()if x]
    index=json.loads((root/'INDEX.json').read_text(encoding='utf8'))
    if rows!=index['frames']:raise ValueError('Journal/index differ')
    previous=None;size=8*cfg['N']**3
    for i,row in enumerate(rows):
        if row['sequence']!=i or Path(row['file']).name!=row['file']:raise ValueError('Invalid frame sequence/member')
        compressed=(root/row['file']).read_bytes()
        if len(compressed)!=row['compressed_bytes']or digest(compressed)!=row['compressed_sha256']:raise ValueError('Compressed frame differs')
        payload=zlib.decompress(compressed)
        if len(payload)!=2*size or digest(payload)!=row['payload_sha256']:raise ValueError('Frame payload differs')
        if row['kind']not in('anchor','xor_uint64')or(row['kind']=='xor_uint64'and previous is None):raise ValueError('Invalid anchor/delta chain')
        if row['kind']=='xor_uint64'and row['previous_sequence']!=i-1:raise ValueError('Broken delta predecessor')
        complete=payload if row['kind']=='anchor'else xor_bytes(payload,previous)
        if digest(complete)!=row['complete_buffers_sha256']or digest(complete[:size])!=row['RAW_sha256']or digest(complete[size:])!=row['clocks_sha256']:
            raise ValueError('Lossless reconstruction hash mismatch')
        previous=complete
        yield {'tick':row['tick'],'raw_bytes':complete[:size],'clocks_bytes':complete[size:],
            'hashes':{k:row[k]for k in('RAW_sha256','clocks_sha256','complete_buffers_sha256')},'row':row,'config':cfg}


def verify_recording(directory):
    """Lossless stdlib reconstruction; no DEE or absolute source locators."""
    root=Path(directory).resolve(strict=True);index=json.loads((root/'INDEX.json').read_text(encoding='utf8'))
    cfg=json.loads((root/'CAPTURA.json').read_text(encoding='utf8'));ticks=[]
    for item in iter_frames(root):ticks.append(item['tick'])
    return {'schema':'DEE.PI05.global_frames.lossless_verification.v1','frames_reconstructed':len(ticks),
        'all_RAW_clocks_hashes_match':True,'N':cfg['N'],'Native_ticks_executed':0,
        'coverage_ticks':ticks,'missing_ticks':index['missing_planned_ticks']}
