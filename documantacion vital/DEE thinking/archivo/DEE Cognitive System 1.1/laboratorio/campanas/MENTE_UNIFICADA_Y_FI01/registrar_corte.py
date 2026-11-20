"""Registra una única autorización A+B desde MA02 real, sin ticks ni reinstalar."""
from pathlib import Path
from datetime import datetime,timezone
import ctypes,hashlib,json,shutil,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
START='2026-10-25T09:49:35+00:00';A_LIMIT='2026-10-25T17:49:35+00:00';LIMIT='2026-10-26T01:49:35+00:00'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    target=HERE/'PRESUPUESTO.json'
    if target.exists():raise FileExistsError('Budget exists: never reset it')
    now=datetime.now(timezone.utc);mono=time.monotonic()
    lives={}
    for name in ['MA02_MAIN_5','MA02_MAIN','MA02_MEMORIA_SEPARADA','MA02_SELECTOR_P1_H1','MA02_SELECTOR_P1_H0','MA02_COMPOSICION_PLUS_LISTA','MA_MAIN_R9','E1_SOCIAL_11']:
        p=ROOT/'sistema/estado/vidas'/name/'VIDA.json';r=json.loads(p.read_bytes());s=ROOT/'sistema'/r['snapshot']
        h=sha(s)
        if h!=r['snapshot_sha256']:raise ValueError('Protected full state differs: '+name)
        lives[name]={'record':str(p),'record_sha256':sha(p),'snapshot':str(s),'snapshot_sha256':h,'physical':r['physical']}
    if lives['MA02_MAIN_5']['physical']['tick']!=11196:raise ValueError('Unexpected parent: preserve and investigate actual later history')
    class Status(ctypes.Structure):
        _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),*[(k,ctypes.c_ulonglong)for k in ['total_phys','avail_phys','total_page','avail_page','total_virtual','avail_virtual','avail_extended']]]
    m=Status();m.length=ctypes.sizeof(m)
    memory={'available_bytes':None,'source':'Windows GlobalMemoryStatusEx public resource status'}
    try:
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):memory|={'available_bytes':int(m.avail_phys),'total_bytes':int(m.total_phys)}
    except (AttributeError,OSError):memory['source']='Resource status unavailable; no permission changes requested'
    manual=ROOT/json.loads((ROOT/'PROYECTO.json').read_bytes())['manual_current']
    data={'campaign':'MENTE_UNIFICADA_Y_FI01','start_utc':START,'block_A_limit_utc':A_LIMIT,'total_limit_utc':LIMIT,
      'registered_utc':now.isoformat(),'registered_monotonic':mono,
      'block_A_deadline_monotonic':mono+(datetime.fromisoformat(A_LIMIT)-now).total_seconds(),
      'total_deadline_monotonic':mono+(datetime.fromisoformat(LIMIT)-now).total_seconds(),
      'maximum_seconds':57600,'maximum_A_seconds':28800,'maximum_B_seconds':28800,
      'previous_MA02_closed_and_not_resumed':True,'supersedes_unexecuted_FI01_prompt':True,
      'native_workers_max':2,'OMP_NUM_THREADS':1,'one_writer_per_world':True,'memory_status':memory,
      'disk_free_bytes':shutil.disk_usage(ROOT).free,'protected':lives,
      'active_record_sha256':sha(ROOT/'sistema/estado/ACTIVO.json'),
      'manual':{'path':str(manual),'sha256':sha(manual)},
      'block_A_checkpoint_required_before_B_native_execution':True,
      'final_continuous_wall_seconds_target':3600,'last_quarter_reserved_for_checks_and_delivery':True}
    target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'registered':str(target),'parent':lives['MA02_MAIN_5']['physical'],'memory':memory,'limits':[A_LIMIT,LIMIT]},ensure_ascii=False))
if __name__=='__main__':main()
