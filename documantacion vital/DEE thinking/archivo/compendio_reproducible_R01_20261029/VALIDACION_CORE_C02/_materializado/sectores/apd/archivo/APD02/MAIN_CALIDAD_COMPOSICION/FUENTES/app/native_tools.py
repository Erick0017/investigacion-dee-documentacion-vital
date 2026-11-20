"""Exact passive observations, official identity and bounded persistence."""
from pathlib import Path
from array import array
import hashlib,json,platform,struct,sys,time
import dee_thinking as d
from dee_thinking.persistence import load_world_snapshot,save_world_snapshot,decode_metadata,encode_metadata
from dee_thinking.consolidated import exact_observation,exact_receipt

WHEEL_SHA='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
PYD_SHA='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
KERNEL_SHA='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
SYSTEM_KEY='DEE.Cognitive.System.1.1.life.v1'

def digest_file(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def identity(system_root=None):
    info=d.build_info();pyd=d._native.__file__;actual=digest_file(pyd)
    if sys.version_info[:2]!=(3,13)or struct.calcsize('P')!=8:raise RuntimeError('Requires CPython3.13x64, not another ABI')
    if d.__version__!='4.5.0'or actual!=PYD_SHA or info['kernel_source_sha256']!=KERNEL_SHA:raise RuntimeError('Official4.5/v27 identity mismatch')
    if system_root is not None:
        whl=Path(system_root)/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
        if digest_file(whl)!=WHEEL_SHA:raise RuntimeError('System wheel identity mismatch')
    return {'python':sys.version,'executable':sys.executable,'imported':d.__file__,'native':pyd,'native_sha256':actual,'wheel_sha256':WHEEL_SHA,'build_info':info,'bits':64}

def physical(world,*,occupation=False):
    rt=world.runtime;raw=rt.raw_copy();clock=rt.clock_copy();result={'N':int(rt.dimension),'tick':int(rt.current_tick),'RAW_sha256':hashlib.sha256(array('Q',raw).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',clock).tobytes()).hexdigest()}
    if occupation:
        result['sites']=len(raw);result['occupied']=sum((v&0xffffffff)>0 for v in raw);result['max_s_reg']=max((v>>32)&0xffff for v in raw);result['basic_buffers_bytes']=32*len(raw)
    return result

def observe(world,site):return exact_observation(world.runtime.observe(d.Coordinate(*map(int,site))))
def moore27(world,site):
    n=int(world.runtime.dimension)
    return [observe(world,[(site[i]+v[i])%n for i in range(3)])for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)for v in[(x,y,z)]]

def atomic_json(path,value):
    import os,uuid
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);pending=path.with_name(path.name+'.pending.'+uuid.uuid4().hex)
    with pending.open('x',encoding='utf8')as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(pending,path)

def metadata(world):
    return {k:decode_metadata(v)for k,v in dict(world.runtime.snapshot_metadata_entries).items() if k.startswith(('CPC','DEE.Cognitive.System'))}
