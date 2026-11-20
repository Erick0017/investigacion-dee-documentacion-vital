"""Portable R04 wall-mode accounting, separate from the original R11 trial."""
import argparse,hashlib,json
from datetime import datetime
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def calculate(root):
    result=json.loads((root/'RESULTADO.json').read_bytes());protocol=json.loads((root/'PROTOCOLO.json').read_bytes());events=[json.loads(x)for x in(root/'ADMISIONES_Y_EVENTOS.jsonl').read_text(encoding='utf8').splitlines()if x.strip()];controls={e['id']:json.loads(e['record']['result'])for e in events if e['kind']=='technical_control_result'}
    prefix=protocol['request_prefix'];intervals=[];issues=[]
    for i in range(3):
        a=controls[prefix+'pause_'+str(i)];b=controls[prefix+'resume_'+str(i)];start=datetime.fromisoformat(a['started_utc']);end=datetime.fromisoformat(b['finished_execution_utc']);duration=(end-start).total_seconds()
        intervals.append({'pause':a['id'],'resume':b['id'],'discount_start_utc':start.isoformat(),'discount_end_utc':end.isoformat(),'discount_seconds':duration,'pause_tick':a['after_tick'],'resume_tick':b['before_tick']})
        if duration<0 or a['after_tick']!=b['before_tick']:issues.append('invalid_pause_interval_'+str(i))
    elapsed=result['host_seconds_from_owner_ready_to_horizon'];discount=sum(x['discount_seconds']for x in intervals);active=elapsed-discount
    checks={'frozen_3720_second_horizon':protocol['seconds']==3720 and elapsed>=3720,'exclusive_R3_prefix':prefix=='fi60r3_','at_least_sixty_unpaused_operational_minutes':active>=3600,'same_life_world_and_parent':all(result['before'][k]==result['final'][k]for k in('life_id','world_id','parent')),'no_unresolved_queue_or_uncertainty':not result.get('error')and not result['remaining_before_close']and not result['final_owner']['uncertain_external_result'],'world_advanced':result['final']['physical']['tick']>result['before']['physical']['tick']}
    issues +=[k for k,v in checks.items()if not v]
    return {'schema':'DEE.unified.R3.real_time_accounting.v1','sources':[{'file':f,'sha256':sha(root/f)}for f in('PROTOCOLO.json','RESULTADO.json','ADMISIONES_Y_EVENTOS.jsonl')],'issues':issues,'checks':checks,'fixed_horizon_seconds':elapsed,'conservative_pause_reload_discount_seconds':discount,'unpaused_operational_seconds_lower_estimate':active,'pause_intervals':intervals,'initial_tick':result['before']['physical']['tick'],'final_tick':result['final']['physical']['tick'],'scope':'Host mode duration, not simulated time or nonstop CPU execution. Three entire pause-through-resume intervals (including process reload) are discounted. This R04 is the declared R3P0 fork with altered calendar preparation and new reserved raw layouts, not a replay/independent replicate of R11, whose results remain separately archived.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();r=calculate(a.evidencia);a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(r,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'issues':r['issues'],'unpaused_seconds':r['unpaused_operational_seconds_lower_estimate']}));return bool(r['issues'])
if __name__=='__main__':raise SystemExit(main())
