"""Host-only guard for the same MAIN at34, before its explicit35..46 block."""
from pathlib import Path
import argparse,ctypes,datetime,hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[1]
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Memory(ctypes.Structure):
    _fields_=[('dwLength',ctypes.c_uint32),('dwMemoryLoad',ctypes.c_uint32)]+[(n,ctypes.c_uint64)for n in
       ('ullTotalPhys','ullAvailPhys','ullTotalPageFile','ullAvailPageFile','ullTotalVirtual','ullAvailVirtual','ullAvailExtendedVirtual')]
def run(out):
    out=out.resolve();need(not out.exists()and out.parent==ROOT/'control/HANDOFF_MAIN35_46_R06','FRESH_GUARD_ONLY')
    mem=Memory();mem.dwLength=ctypes.sizeof(mem);need(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem)),'WIN32_MEMORY')
    freeze=read(ROOT/'control/CONGELADO_NATIVE_R07_LEASE_R06.json')
    for row in freeze['files']:need(sha(ROOT/row['file'])==row['sha256'],'FROZEN_SOURCE_CHANGED:'+row['file'])
    native=ROOT/'native/MAIN';ctx=read(native/'CONTEXTO_EJECUCION.json');life=ctx['life']
    need(life=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_MAIN','EXACT_SAME_MAIN')
    scope=read(native/'sistema/capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json')
    need(scope['role']=='main'and scope['max_cycles']==24 and scope['q2_sensor_arm']=='local_tag'and
      scope['native_cutoff_utc_epoch']==1794906420 and scope['last_new_cycle_utc_epoch']==1794902400,'R06_SCOPE_NO_RESET')
    for file,digest in freeze['native_sources_sha256'].items():need(sha(native/'sistema/capacidades'/file)==digest,'INSTALLED_NATIVE_SOURCE')
    cache=native/'sistema/app/cache_fuentes_C02.py';need(sha(cache)=='e4621d4875376a910511cadd55503daccadbd0a9787be8d99516417bf2e02adf','ORIGINAL_CACHE')
    card=read(native/'sistema/estado/vidas'/life/'VIDA.json');physical=card['physical']
    need(physical['N']==67 and physical['tick']==1000571 and physical['RAW_sha256']=='511eaf4ee2617e9cddff5d9aaba3fea70d5ec03e2d03c514d43adbee574d5869'and
      physical['clocks_sha256']=='c135029c6ad34a61ad33f6ddc07ca9343073c56a6c55424b20f9d6652b7ee528','MAIN34_PHYSICAL')
    need(card['snapshot_sha256']=='658eb107e65d448e39cb7726a1c5e4dbd61cb5d1a94424127f2956ec138fb1fa'and sha(native/'sistema'/card['snapshot'])==card['snapshot_sha256'],'R06_ADMIN_SNAPSHOT')
    worldfile=ROOT/'evidencia/MAIN_BLOQUE_01_CONTINUACION34_R01/WORLD_CHECKPOINT.json';world=read(worldfile)
    need(sha(worldfile)=='3c8420a1fcbebce4514030fb937d76d87e1686f8349a3dcf04922850a8a1a2a7'and world['native_life_id']==life and world['native_tick']==1000571,'MAIN_COMPLETE_WORLD34')
    need(world['boundary']['completed_opportunities']==34 and world['boundary']['next_opportunity']==35 and world['S']['seq']==68 and
      world['S']['sessionId']=='R07_MAIN_adc933c82cc74fb0bb19','PRESERVED_SESSION_AND_CURSOR')
    ledgerfile=ROOT/'control/LEDGER_V3.json';ledger=read(ledgerfile);budget=ledger['worlds'][life]
    need(ledger['consumed']==32844 and not ledger['intents']and budget['consumed']==9384 and budget['cycles']==6 and budget['reserved']==0,'CLOSED_GLOBAL_BOUNDARY')
    need(not(ROOT/'evidencia/MAIN_REAPERTURA_35_46_R06').exists(),'NO_PRIOR_REOPEN_OR_REPLAY')
    value=dict(schema='DEE.R07.MAIN35_46.host_guard.R06',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      life=life,physical=physical,snapshot_sha256=card['snapshot_sha256'],world_sha256=sha(worldfile),scope=scope,
      ledger_sha256=sha(ledgerfile),global_consumed=ledger['consumed'],ledger_world=budget,
      memory={n:int(getattr(mem,n))for n,_ in Memory._fields_},required_available_bytes=3758096384,
      passed=mem.ullAvailPhys>=3758096384,Native_Studio_model_calls=0)
    with out.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    need(value['passed'],'RAM_GUARD_NOT_MET');return dict(path=str(out),sha256=sha(out),available=mem.ullAvailPhys,passed=True)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(run(a.output),ensure_ascii=False))
