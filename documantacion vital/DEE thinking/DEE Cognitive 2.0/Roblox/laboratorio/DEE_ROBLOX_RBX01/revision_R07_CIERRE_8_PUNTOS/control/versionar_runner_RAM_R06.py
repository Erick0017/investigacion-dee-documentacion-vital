"""Version-only host-safety change; no Studio/model/Native execution."""
from pathlib import Path
import hashlib

ROOT=Path(__file__).resolve().parent
old=ROOT/'runner_comparador_v3_R05.py'
new=ROOT/'runner_comparador_v3_R06_RAM.py'
original=old.read_bytes()
assert hashlib.sha256(original).hexdigest()=='76bdd69a2768c42a3f2758b414408362672568d54f1f5f40da341962e75aa72d'
text=original.decode('utf-8-sig')
def change(before,after):
    global text
    assert text.count(before)==1,before
    text=text.replace(before,after)
change("HARD_CLOSE=1794884820", """HARD_CLOSE=1794884820
STOP_FREE_BYTES=1024**3

def host_memory():
    # Pure read-only Win32 host measurement. Failure is not guessed as free RAM.
    import ctypes
    from ctypes import wintypes
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_=[('dwLength',wintypes.DWORD),('dwMemoryLoad',wintypes.DWORD),
            ('ullTotalPhys',ctypes.c_ulonglong),('ullAvailPhys',ctypes.c_ulonglong),
            ('ullTotalPageFile',ctypes.c_ulonglong),('ullAvailPageFile',ctypes.c_ulonglong),
            ('ullTotalVirtual',ctypes.c_ulonglong),('ullAvailVirtual',ctypes.c_ulonglong),
            ('ullAvailExtendedVirtual',ctypes.c_ulonglong)]
    data=MEMORYSTATUSEX();data.dwLength=ctypes.sizeof(data)
    api=ctypes.WinDLL('kernel32',use_last_error=True).GlobalMemoryStatusEx
    api.argtypes=[ctypes.POINTER(MEMORYSTATUSEX)];api.restype=wintypes.BOOL
    if not api(ctypes.byref(data)):raise ctypes.WinError(ctypes.get_last_error())
    return {'source':'Win32.GlobalMemoryStatusEx','available_physical_bytes':int(data.ullAvailPhys),
        'total_physical_bytes':int(data.ullTotalPhys),'memory_load_percent':int(data.dwMemoryLoad),
        'available_page_file_bytes':int(data.ullAvailPageFile),'total_page_file_bytes':int(data.ullTotalPageFile),
        'scope':'Host OS memory, not DEE cognitive memory, process RSS or measured energy'}""")
change("    need(time.time()<CUTOFF,'Prospective new-episode cutoff reached before opening reference')", """    need(time.time()<CUTOFF,'Prospective new-episode cutoff reached before opening reference')
    need(type(a.min_start_free_bytes)is int and STOP_FREE_BYTES<=a.min_start_free_bytes<=2**50,
         'Explicit finite start RAM threshold >=1GiB required for both references')""")
change("    session=a.session or 'R07_'+a.participant+'_'+uuid.uuid4().hex[:12]", """    samples=output/'HOST_MEMORY_SAMPLES.jsonl'
    def memory_sample(stage,cycle=None):
        value={'utc':utc(),'stage':stage,'next_cycle':cycle,**host_memory()}
        with samples.open('a',encoding='utf-8')as f:
            f.write(json.dumps(value,ensure_ascii=False,allow_nan=False)+'\\n');f.flush();os.fsync(f.fileno())
        record('HOST_MEMORY_SAMPLE',**{k:v for k,v in value.items()if k!='utc'})
        return value
    initial_memory=memory_sample('INITIAL_PRECHECK',state['boundary']['next_opportunity'])
    if initial_memory['available_physical_bytes']<a.min_start_free_bytes:
        rejected={'status':'PRESTART_RESOURCE_REJECTED_NO_WORLD_OR_POLICY_OPENED',
            'minimum_start_free_bytes':a.min_start_free_bytes,'measurement':initial_memory,
            'Native_calls':0,'model_calls':0,'MCP_calls':0}
        (output/'PREFLIGHT_RAM_REJECTED.json').write_text(json.dumps(rejected,indent=2,ensure_ascii=False),encoding='utf-8')
        raise MemoryError('Explicit initial free-RAM threshold not met; no World/policy opened')
    session=a.session or 'R07_'+a.participant+'_'+uuid.uuid4().hex[:12]""")
change("    backend=None;rows=[];failure=None", "    backend=None;rows=[];failure=None;stop_reason=None")
change("               prospective_cutoff_epoch=CUTOFF,source_code_sha256=sha(__file__))", """               prospective_cutoff_epoch=CUTOFF,source_code_sha256=sha(__file__),
               host_RAM_guard={'revision':'R06_RAM','initial_min_free_bytes':a.min_start_free_bytes,
                   'boundary_stop_below_bytes':STOP_FREE_BYTES,'policy_changed':False,
                   'daemon_stop_written':False})""")
change("            need(time.time()<CUTOFF,'Prospective new-episode cutoff; preserve completed prefix')\n            base=", """            need(time.time()<CUTOFF,'Prospective new-episode cutoff; preserve completed prefix')
            memory=memory_sample('BEFORE_BEGIN',cycle)
            if memory['available_physical_bytes']<STOP_FREE_BYTES:
                stop_reason='HOST_FREE_RAM_BELOW_1GiB'
                record('HOST_BOUNDARY_STOP',stop_reason=stop_reason,completed_new=len(rows),
                    next_cycle_not_started=cycle,available_physical_bytes=memory['available_physical_bytes'],
                    backend_pending=None,no_policy_request=True,no_World_BEGIN=True)
                break
            base=""")
change("        final=world.checkpoint('R07_PAIR_'+session+'_C'+str(a.stop_cycle),output/'WORLD_CHECKPOINT.json')", """        actual_completed=rows[-1]['state_after']['completedCycles']if rows else state['S']['completedCycles']
        final=world.checkpoint('R07_PAIR_'+session+'_C'+str(actual_completed),output/'WORLD_CHECKPOINT.json')
        need(final['S']['completedCycles']==actual_completed,'Actual cursor, never planned horizon, is saved')""")
change("                'new_scenario_sha256':final['scenario_sha256'],'source_world_sha256':sha(source)}", """                'new_scenario_sha256':final['scenario_sha256'],'source_world_sha256':sha(source),
                'stop_reason':stop_reason or 'REQUESTED_HORIZON_COMPLETED',
                'planned_stop_cycle':a.stop_cycle,'minimum_start_free_bytes':a.min_start_free_bytes,
                'boundary_stop_below_bytes':STOP_FREE_BYTES,'host_memory_samples':str(samples),
                'host_safety_is_not_cognitive_regulation':True,'daemon_stop_written':False}""")
change("    p.add_argument('--stop-cycle',type=int,required=True);p.add_argument('--session');p.add_argument('--resume',action='store_true')", """    p.add_argument('--stop-cycle',type=int,required=True);p.add_argument('--session');p.add_argument('--resume',action='store_true')
    p.add_argument('--min-start-free-bytes',type=int,required=True,
        help='Explicit measured host margin for either reference, >=1073741824; not a model-memory guarantee')""")
assert not new.exists(),str(new)
new.write_text(text,encoding='utf-8',newline='\n')
assert old.read_bytes()==original
print(new.name,hashlib.sha256(new.read_bytes()).hexdigest())
