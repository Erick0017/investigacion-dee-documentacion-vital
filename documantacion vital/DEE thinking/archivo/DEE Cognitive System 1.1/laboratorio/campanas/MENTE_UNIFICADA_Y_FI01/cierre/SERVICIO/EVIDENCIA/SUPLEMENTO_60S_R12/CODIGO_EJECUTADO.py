"""Declared sixty-second no-teaching continuation AFTER the fixed R03 trial.

No reserve is extended/rewritten. Same saved life and transport, explicit resume,
sixty real seconds, then pause/save/export/stop; no material questions or repair.
"""
import argparse,gzip,hashlib,json,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cola_local import QueueDB


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def run(system,trial,protocol,out):
    p=json.loads(protocol.read_bytes());previous=json.loads((trial/'RESULTADO.json').read_bytes());out.mkdir(parents=True,exist_ok=False)
    if previous.get('error')or previous.get('remaining_before_close')or previous.get('final_owner',{}).get('uncertain_external_result'):raise ValueError('R03 did not leave an unambiguous complete closed owner; no automatic action or favorable fallback')
    life=p['life_id'];record=json.loads((system/'estado/vidas'/life/'VIDA.json').read_bytes())
    if record['snapshot_sha256']!=previous['final']['snapshot_sha256']:raise ValueError('Same actual R03 final cut required; no rewind or intervening future')
    folder=system/'estado/servicios_persistentes'/record['world_id'];db=QueueDB(folder/'cola.sqlite3')
    if db.outstanding():raise ValueError('Preserve pending/outcome; this supplemental interval cannot silently consume an old task')
    sources=previous['sources']
    for item in sources:
        if sha(system/item['file'])!=item['sha256']:raise ValueError('Frozen actor source changed before supplement')
    if(system/'estado/locks'/(record['world_id']+'.lock')).exists():raise ValueError('Another writer owns this world')
    code=out/'CODIGO_EJECUTADO.py';code.write_bytes(Path(__file__).read_bytes());(out/'PROTOCOLO.json').write_bytes(protocol.read_bytes())
    before={k:record.get(k)for k in('life_id','world_id','parent','snapshot','snapshot_sha256','physical')};result={'schema':'DEE.unified.operational_sixty_second_supplement.v1','protocol_sha256':sha(protocol),'before':before,'source_trial':'SERVICIO_60MIN_FINAL_R11','sources':sources,'started_utc':now(),'material_requests':0,'explicit_teaching':0};owner=None
    def control(identifier,op):
        reply=db.put(identifier,{'operacion':op});limit=time.monotonic()+40
        while time.monotonic()<limit:
            row=db.get(identifier)
            if row and row['status']in('completed','uncertain','failed_preserved','rejected_invalid'):
                if row['status']!='completed':raise ValueError('Supplemental technical control failed: '+str(row))
                return {'admission':reply,'record':row,'result':json.loads(row['result'])}
            time.sleep(.05)
        raise TimeoutError(identifier)
    try:
        launch_wall=time.time();argv=[sys.executable,'-I','-B','-X','utf8',str(system/'gestionar.py'),'mente-unificada-iniciar','--vida',life,'--backend','mente_unificada','--pausado','--intervalo','.1','--guardar-cada','60','--max-segundos','150']
        owner=subprocess.Popen(argv,stdout=(out/'OWNER_STDOUT.txt').open('x',encoding='utf8'),stderr=(out/'OWNER_STDERR.txt').open('x',encoding='utf8'));limit=time.monotonic()+45
        while time.monotonic()<limit:
            if owner.poll()is not None:raise RuntimeError('Supplemental owner failed before readiness')
            status=db.get_meta('owner')
            if status and status.get('running')and datetime.fromisoformat(status['wall_utc']).timestamp()>=launch_wall:break
            time.sleep(.1)
        else:raise TimeoutError('Supplemental owner readiness')
        result['initial_owner']=status;result['resume']=control('fi60s_resume','reanudar');started=time.monotonic();result['unpaused_window_started_utc']=now();samples=[]
        while time.monotonic()-started<p['unpaused_seconds_after_resume_acknowledgement']:
            if owner.poll()is not None:raise RuntimeError('Supplemental owner ended before the fixed sixty-second window')
            samples.append({'utc':now(),'host_elapsed_seconds':time.monotonic()-started,'cached_owner':db.get_meta('owner')});time.sleep(.5)
        result['measured_real_seconds_after_resume_acknowledgement']=time.monotonic()-started;result['pause']=control('fi60s_pause','pausar');result['save']=control('fi60s_save','guardar');result['export']=control('fi60s_export','exportar');result['stop']=control('fi60s_stop','detener');owner.wait(timeout=45);result['owner_returncode']=owner.returncode;owner=None
        after=json.loads((system/'estado/vidas'/life/'VIDA.json').read_bytes());result['after']={k:after.get(k)for k in before};result['final_owner']=db.get_meta('owner');result['samples']=samples
        checks={'same_life_and_world':before['life_id']==result['after']['life_id']and before['world_id']==result['after']['world_id']and before['parent']==result['after']['parent'],
            'at_least_sixty_real_unpaused_seconds':result['measured_real_seconds_after_resume_acknowledgement']>=60,
            'world_advanced_without_material_request':result['after']['physical']['tick']>before['physical']['tick']and result['final_owner']['material_calls']==result['initial_owner']['material_calls'],
            'no_uncertainty_or_pending':not db.outstanding()and not result['final_owner']['uncertain_external_result'],
            'all_actor_sources_unchanged':all(sha(system/i['file'])==i['sha256']for i in sources)}
        result['checks']=checks;result['issues']=[k for k,v in checks.items()if not v]
    except Exception as error:
        result['error']={'type':type(error).__name__,'detail':str(error)}
        if owner and owner.poll()is None:
            try:result['emergency_stop']=control('fi60s_emergency_stop','detener');owner.wait(timeout=45)
            except Exception as stop_error:result['stop_error']=str(stop_error)
    result['finished_utc']=now();result['scope']='Fixed supplemental operational window, not a new reserve, teaching episode, cognitive survival score or retroactive extension of R03. Same life; passive cached observations only.'
    target=out/'SUPLEMENTO.json.gz'
    with gzip.GzipFile(filename=str(target),mode='wb',mtime=0)as f:f.write((json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
    print(json.dumps({'primary':str(target),'sha256':sha(target),'error':result.get('error'),'issues':result.get('issues'),'after':result.get('after')}));return bool(result.get('error')or result.get('issues'))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--ensayo',type=Path,required=True);p.add_argument('--protocolo',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();return run(a.sistema,a.ensayo,a.protocolo,a.salida)
if __name__=='__main__':raise SystemExit(main())
