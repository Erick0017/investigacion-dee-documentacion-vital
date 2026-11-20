"""Host-only prospective guard for the explicitly delegated CTRL1 six cases."""
from pathlib import Path
import argparse, ctypes, datetime, hashlib, json
ROOT=Path(__file__).resolve().parents[1]

def need(value,message):
    if not value:raise ValueError(message)

def read(path):return json.loads(path.read_text('utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

class Memory(ctypes.Structure):
    _fields_=[('dwLength',ctypes.c_uint32),('dwMemoryLoad',ctypes.c_uint32)]+[(n,ctypes.c_uint64)for n in
       ('ullTotalPhys','ullAvailPhys','ullTotalPageFile','ullAvailPageFile','ullTotalVirtual','ullAvailVirtual','ullAvailExtendedVirtual')]

def run(output):
    output=output.resolve();need(not output.exists() and output.parent==ROOT/'control/HANDOFF_CTRL6_R06','FRESH_BOUNDED_GUARD_OUTPUT')
    mem=Memory();mem.dwLength=ctypes.sizeof(mem);need(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem)),'ACTUAL_WIN32_MEMORY')
    freeze=read(ROOT/'control/CONGELADO_NATIVE_R07_LEASE_R06.json')
    checked=[]
    for item in freeze['files']:
        need(sha(ROOT/item['file'])==item['sha256'],'FROZEN_R06_SOURCE_CHANGED:'+item['file']);checked.append(item['file'])
    native=ROOT/'native/CTRL1';context=read(native/'CONTEXTO_EJECUCION.json');life=context['life']
    scope=read(native/'sistema/capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json')
    need(scope['role']=='control' and scope['max_cycles']==6 and scope['q2_sensor_arm']=='constant_tag2' and
         scope['native_cutoff_utc_epoch']==1794906420 and scope['last_new_cycle_utc_epoch']==1794902400,'EXACT_DECLARED_CONTROL_SCOPE')
    for filename,digest in freeze['native_sources_sha256'].items():
        need(sha(native/'sistema/capacidades'/filename)==digest,'EXACT_INSTALLED_NATIVE_SOURCE')
    cache=native/'sistema/app/cache_fuentes_C02.py'
    need(sha(cache)=='e4621d4875376a910511cadd55503daccadbd0a9787be8d99516417bf2e02adf','ONLY_ORIGINAL_CACHE')
    card=read(native/'sistema/estado/vidas'/life/'VIDA.json');world=native/'WORLD_PADRE_PAR28.json';state=read(world)
    need(card['physical']['N']==67 and card['physical']['tick']==991187 and state['native_tick']==991187 and
         state['boundary']['completed_opportunities']==28 and state['boundary']['next_opportunity']==29,'EXACT_FRESH_PAR28_CONTROL')
    need(sha(world)==context['source_world_sha256'],'EXACT_PRESERVED_PARENT_WORLD')
    ledger_path=ROOT/'control/LEDGER_V3.json';ledger=read(ledger_path)
    need(ledger['consumed']==23460 and not ledger['intents'],'EXCLUSIVE_CLOSED_GLOBAL_BOUNDARY')
    budget=ledger['worlds'].get(life)
    need(budget is None or budget['consumed']==0 and budget['cycles']==0 and budget['reserved']==0,'NO_PREVIOUS_CONTROL_NATIVE')
    need(not(ROOT/'evidencia/CTRL1_SEIS_R06').exists(),'ONE_FRESH_OUTPUT_NO_REPLAY')
    result=dict(schema='DEE.R07.CTRL6.prospective_host_guard.R06',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      memory={name:int(getattr(mem,name))for name,_ in Memory._fields_},required_available_bytes=3758096384,
      memory_passed=mem.ullAvailPhys>=3758096384,source_files_verified=checked,
      scope=scope,life=life,physical=card['physical'],cache_sha256=sha(cache),parent_world_sha256=sha(world),
      ledger_sha256=sha(ledger_path),global_consumed=ledger['consumed'],intents=ledger['intents'],
      Native_Studio_model_calls=0)
    with output.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    need(result['memory_passed'],'DECLARED_3_5_GIB_RAM_GUARD_NOT_MET')
    return dict(output=str(output),sha256=sha(output),available=mem.ullAvailPhys,status='PASSED_NO_NATIVE')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(run(a.output),ensure_ascii=False))
