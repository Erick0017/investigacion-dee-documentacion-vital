"""Read-only current identity and full-life metadata; no new universe or ticks."""
from pathlib import Path
import sys,json,time,ctypes
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store
from app.native_tools import identity,physical,atomic_json
from dee_thinking.persistence import decode_metadata
from capacidades.observador_causal_retrospectivo_01 import Snapshot
class Memory(ctypes.Structure):
    _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(x,ctypes.c_ulonglong)for x in('total_phys','avail_phys','total_page','avail_page','total_virtual','avail_virtual','avail_extended')]
def main():
    out=ROOT/'evidencia/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01';out.mkdir(parents=True,exist_ok=True)
    store=Store();record,a=store.load('E1_SOCIAL_11')
    memory=Memory();memory.length=ctypes.sizeof(memory);ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory))
    fields={k:decode_metadata(v)for k,v in dict(a.world.runtime.snapshot_metadata_entries).items()if k.startswith(('DEE.Cognitive.System','CPC'))}
    saved=Snapshot(store.snapshot(record))
    value={'identity':identity(store.root),'parent_record':record,'physical':physical(a.world,occupation=True),'pending_inputs':saved.pending,'memory':{k:int(getattr(memory,k))for k,_ in memory._fields_},'monotonic_now':time.monotonic(),'geometry':a.geometry,'state':a.state,'metadata':fields,'interfaces':[str(x)for x in a.world.interfaces]}
    # PendingInputs is normally empty here; native objects must not be silently stringified.
    atomic_json(out/'INICIO_EXISTENTE.json',value)
    print(json.dumps({'tick':a.tick,'pending':len(value['pending_inputs']),'physical':value['physical'],'memory':value['memory'],'file':str(out/'INICIO_EXISTENTE.json')},ensure_ascii=False))
if __name__=='__main__':main()
