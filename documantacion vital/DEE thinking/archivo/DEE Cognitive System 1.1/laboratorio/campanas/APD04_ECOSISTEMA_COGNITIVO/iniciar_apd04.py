"""Arranque acotado: importa el par completo original y registra presupuesto una vez."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, importlib.util, json, os, subprocess, sys, time

ROOT=Path(__file__).resolve().parents[3]
SYSTEM=ROOT/'sistema'
EV=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
START=datetime.fromisoformat('2026-10-26T19:30:51+00:00')
PAIR=SYSTEM/'estado/fuentes_emparejadas/APD03_MAIN_T604825_R01'

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')

def main():
    if (SYSTEM/'estado/vidas/APD04_MAIN').exists() or (EV/'ARRANQUE_R01').exists():
        raise FileExistsError('Existe inicio APD04: inspeccionar y continuar, nunca repetirlo')
    if sha(PAIR/'EXPORTACION_SERVICIO.json')!='9610905c1c3879fd4de3062894c2978c8cb5187e068185cfe889b7b2ee80a085':raise ValueError('Otro par padre')
    parent=read(SYSTEM/'estado/vidas/APD03_MAIN/VIDA.json')
    if parent['physical']['tick']!=604825 or parent['snapshot_sha256']!='c7cf2e78837ed5f99c950016314bfe5f8fbfa868f72a67af36a94a78261a24ba':raise ValueError('Padre distinto: no volver a pasado favorable')
    paths=[SYSTEM/'estado/ACTIVO.json',SYSTEM/'estado/vidas/APD03_MAIN/VIDA.json',SYSTEM/parent['snapshot'],PAIR/'EXPORTACION_SERVICIO.json']
    protected={str(p):sha(p) for p in paths}
    now=datetime.now(timezone.utc);mono=time.monotonic()
    budget={'start_utc_first_command':START.isoformat(),'maximum_seconds':28800,
      'deadline_utc':(START+timedelta(hours=8)).isoformat(),
      'last_third_starts_utc':(START+timedelta(seconds=19200)).isoformat(),
      'monotonic_origin_estimated_from_first_command':mono-(now-START).total_seconds(),
      'monotonic_anchor':mono,'anchor_utc':now.isoformat(),
      'native_job_memory_limit_bytes':536870912,'outer_job_memory_limit_bytes':1073741824,
      'cpu_threads':1,'campaign_storage_target_max_bytes':17179869184,'stop_if_free_disk_bytes_below':10737418240,
      'reserve_real_continuous_seconds':3600,'no_automatic_extension':True}
    write(EV/'PRESUPUESTO.json',budget)
    out=EV/'ARRANQUE_R01';out.mkdir()
    write(out/'PROTEGIDOS_ANTES.json',protected)
    spec=importlib.util.spec_from_file_location('apd04_processes',SYSTEM/'app/process_control.py');pc=importlib.util.module_from_spec(spec);spec.loader.exec_module(pc)
    os.environ['OMP_NUM_THREADS']='1'
    runs=[]
    for name,args in [('IDENTIDAD',['version']),('IMPORTACION_COMPLETA',['mente-unificada-importar','--paquete',str(PAIR),'--vida','APD04_MAIN'])]:
        command=[sys.executable,'-I','-B','-X','utf8',str(SYSTEM/'gestionar.py'),*args]
        t=time.monotonic()
        with (out/(name+'.stdout.json')).open('xb') as stdout,(out/(name+'.stderr.txt')).open('xb') as stderr:
            p,job,jobname=pc.spawn_owned(command,cwd=Path(sys.executable).parent,stdout=stdout,stderr=stderr,memory_limit=536870912)
            try:
                p.wait(timeout=180);resources=pc.job_resources(job)
                if resources.get('job_active_processes'):
                    for _ in range(50):
                        time.sleep(.05);resources=pc.job_resources(job)
                        if not resources.get('job_active_processes'):break
            finally:pc.close_job(job)
        runs.append({'command':command,'pid':p.pid,'job':jobname,'exit_code':p.returncode,'wall_seconds':time.monotonic()-t,'resources':resources})
        write(out/(name+'.EJECUCION.json'),runs[-1])
        if p.returncode:raise RuntimeError('Comando fallido conservado: '+name)
    child=read(SYSTEM/'estado/vidas/APD04_MAIN/VIDA.json')
    for key in ('N','tick','RAW_sha256','clocks_sha256'):
        if child['physical'][key]!=parent['physical'][key]:raise ValueError('Importacion cambió estado '+key)
    if any(sha(p)!=s for p,s in protected.items()):raise ValueError('Fuente protegida cambió')
    write(out/'ARRANQUE_COMPLETO.json',{'parent':'APD03_MAIN','life':'APD04_MAIN','new_ticks':0,'physical':child['physical'],'protected_unchanged':True,'runs':runs,'native_owner_started':False,'full_pair_not_snapshot_only':True})
    print(json.dumps({'life':'APD04_MAIN','tick':child['physical']['tick'],'new_ticks':0,'protected_unchanged':True}))

if __name__=='__main__':main()
