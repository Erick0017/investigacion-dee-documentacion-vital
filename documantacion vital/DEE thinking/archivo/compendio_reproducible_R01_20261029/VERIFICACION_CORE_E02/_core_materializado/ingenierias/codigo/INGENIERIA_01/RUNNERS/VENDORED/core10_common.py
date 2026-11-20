"""Portable minimal v27 runtime used only in the packaged reproduction copy."""
from __future__ import annotations
import hashlib,importlib,os,platform,sys
from pathlib import Path
import numpy as np

EXPECTED={"wheel":"69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939","package":"7e2991b1fc8a053ee44ead6e177b129855ae9265dea68505a8e545f0c3fdf8b4","kernel":"0b17ba32037935a255b0f2182a52137bceab424f7e09126b761076b63e42c6ff"}
STATE_MASK=np.uint64((1<<32)-1);SREG_MASK=np.uint64(0xFFFF);SEM_MASK=np.uint64(0xF)

def sha256_file(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def _candidate_roots():
    env=os.environ.get("DEE_V27_TESTS_ROOT")
    if env:yield Path(env)
    for p in Path(__file__).resolve().parents:yield p

def verify_and_load_kernel(threads=1):
    if sys.version_info[:2]!=(3,13):raise RuntimeError(f"DEE v27 requires CPython 3.13; observed {sys.version}")
    canonical=None
    for root in _candidate_roots():
        pkg=root/"DEE_CODEX_NATIVE_DISCOVERY_AND_CLOSURE_V1_WORK"/"ANALYSIS"/"binary_api"/"wheel_extracted"
        if (pkg/"dee_universe_v27"/"dee_kernel_v27.cp313-win_amd64.pyd").exists():canonical=(root,pkg);break
    if canonical:
        root,extracted=canonical;sys.path.insert(0,str(extracted));importlib.invalidate_caches()
    import dee_universe_v27 as package
    from dee_universe_v27 import dee_kernel_v27 as kernel
    package_path=Path(package.__file__).resolve();kernel_path=Path(kernel.__file__).resolve()
    observed={"package":sha256_file(package_path),"kernel":sha256_file(kernel_path),"wheel":None}
    for root in _candidate_roots():
        wheel=root/"dee_universe_v27-27.0.0-cp313-cp313-win_amd64.whl"
        if wheel.exists():observed["wheel"]=sha256_file(wheel);break
    if observed["package"]!=EXPECTED["package"] or observed["kernel"]!=EXPECTED["kernel"]:raise RuntimeError(f"sealed identity mismatch: {observed}")
    if observed["wheel"] is not None and observed["wheel"]!=EXPECTED["wheel"]:raise RuntimeError(f"wheel identity mismatch: {observed['wheel']}")
    return kernel,{"observed_hashes":observed,"python":sys.version,"numpy":np.__version__,"platform":platform.platform(),"threads":int(threads),"package_path":str(package_path),"kernel_path":str(kernel_path)}

def pack(state,sreg,direction,semantic=1):return np.uint64((int(state)&0xFFFFFFFF)|((int(sreg)&0xFFFF)<<32)|((int(direction[0])&0xF)<<48)|((int(direction[1])&0xF)<<52)|((int(direction[2])&0xF)<<56)|((int(semantic)&0xF)<<60))
def signed_nibble(raw,shift):
    v=(np.asarray(raw,dtype=np.uint64)>>np.uint64(shift))&np.uint64(0xF);v=v.astype(np.int16);return np.where(v>=8,v-16,v)
def fields(raw):return {"state":(raw&STATE_MASK).astype(np.uint32),"sreg":((raw>>np.uint64(32))&SREG_MASK).astype(np.uint16),"dx":signed_nibble(raw,48),"dy":signed_nibble(raw,52),"dz":signed_nibble(raw,56),"semantic":((raw>>np.uint64(60))&SEM_MASK).astype(np.uint8)}
def unpack_scalar(raw):
    v=np.uint64(raw);return {"raw":int(v),"state":int(v&STATE_MASK),"sreg":int((v>>np.uint64(32))&SREG_MASK),"direction":[int(signed_nibble(v,s)) for s in (48,52,56)],"semantic":int((v>>np.uint64(60))&SEM_MASK)}

class NativeWorld:
    def __init__(self,kernel,raw,clock=None,threads=1):
        self.kernel=kernel;self.n=int(raw.shape[0]);self.threads=int(threads);self.raw_a=np.ascontiguousarray(raw,dtype=np.uint64).copy();self.raw_b=self.raw_a.copy();base=np.zeros_like(raw,dtype=np.uint64) if clock is None else clock;self.clock_a=np.ascontiguousarray(base,dtype=np.uint64).copy();self.clock_b=self.clock_a.copy()
    @property
    def raw(self):return self.raw_a
    def tick(self):return {str(k):v for k,v in dict(self.kernel.tick_universo_lazy(self.raw_a,self.raw_b,self.clock_a,self.clock_b,self.n,self.threads)).items()}
    def inject(self,q,value,clock=0):
        q=tuple(int(x)%self.n for x in q);self.raw_a[q]=np.uint64(value);self.raw_b[q]=np.uint64(value);self.clock_a[q]=np.uint64(clock);self.clock_b[q]=np.uint64(clock)
