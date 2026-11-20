"""Archived wall-time accounting; no Runtime, DEE import or new tick.

Conservatively discounts each complete pause-to-resume interval, including
the planned stopped-owner/reload gap, and adds the separately timed supplement.
"""
import argparse,gzip,hashlib,json
from datetime import datetime,timedelta
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stamp(s):return datetime.fromisoformat(s)
def calculate(ev):
    trial=ev/'SERVICIO_60MIN_FINAL_R11';extra=ev/'SUPLEMENTO_60S_R12'
    result=json.loads((trial/'RESULTADO.json').read_bytes())
    supplement=json.loads(gzip.decompress((extra/'SUPLEMENTO.json.gz').read_bytes()))
    events=[json.loads(s)for s in(trial/'ADMISIONES_Y_EVENTOS.jsonl').read_text(encoding='utf8').splitlines()if s.strip()]
    controls={e['id']:json.loads(e['record']['result'])for e in events if e['kind']=='technical_control_result'}
    ready=[e for e in events if e['kind']=='owner_ready'];intervals=[];issues=[]
    def check(name,ok):
        if not ok:issues.append(name)
    check('one_original_ready_event',len(ready)==1)
    for i in range(3):
        pause=controls['fi60_pause_'+str(i)];resume=controls['fi60_resume_'+str(i)]
        start=stamp(pause['started_utc']);end=stamp(resume['finished_execution_utc'])
        check('pause_'+str(i)+'_nonnegative',end>=start)
        intervals.append({'pause_id':pause['id'],'resume_id':resume['id'],'discount_start_utc':start.isoformat(),'discount_end_utc':end.isoformat(),'discount_seconds':(end-start).total_seconds(),'pause_tick':pause['after_tick'],'resumed_tick':resume['before_tick']})
    horizon=result['host_seconds_from_owner_ready_to_horizon'];discount=sum(x['discount_seconds']for x in intervals)
    main_active=max(0,horizon-discount)
    supplement_active=supplement['measured_real_seconds_after_resume_acknowledgement']
    # The supplemental interval starts AFTER the resume result acknowledgement;
    # its native owner must remain alive for the fixed measured interval.
    check('same_exact_R03_cut_loaded_by_supplement',supplement['before']['snapshot_sha256']==result['final']['snapshot_sha256'])
    check('same_life_world_parent',all(supplement['before'][k]==supplement['after'][k]==result['final'][k]for k in('life_id','world_id','parent')))
    check('supplement_has_no_material_input_or_teaching',supplement['material_requests']==supplement['explicit_teaching']==0 and supplement['initial_owner']['material_calls']==supplement['final_owner']['material_calls'])
    check('supplement_advanced_world',supplement['after']['physical']['tick']>supplement['before']['physical']['tick'])
    check('supplement_at_least_sixty_real_seconds',supplement_active>=60)
    check('all_supplement_local_checks',not supplement.get('error')and not supplement.get('issues')and all(supplement['checks'].values()))
    check('original_horizon_unchanged',horizon>=3605 and json.loads((trial/'PROTOCOLO.json').read_bytes())['seconds']==3605)
    check('at_least_sixty_minutes_in_unpaused_operational_mode',main_active+supplement_active>=3600)
    check('no_remaining_original_material_or_uncertainty',not result.get('error')and not result['remaining_before_close']and not result['final_owner']['uncertain_external_result'])
    return {'schema':'DEE.unified.real_time_accounting.v1','issues':issues,'sources':[{'file':str(p.relative_to(ev)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p)}for p in(trial/'RESULTADO.json',trial/'ADMISIONES_Y_EVENTOS.jsonl',trial/'PROTOCOLO.json',extra/'SUPLEMENTO.json.gz')],
      'original_fixed_horizon_seconds':horizon,'conservative_discounted_pause_and_reload_seconds':discount,'discounted_intervals':intervals,'original_unpaused_operational_seconds_lower_estimate':main_active,
      'separate_supplement_unpaused_seconds_after_resume_acknowledgement':supplement_active,'combined_unpaused_operational_seconds_lower_estimate':main_active+supplement_active,'original_initial_tick':result['before']['physical']['tick'],'original_final_tick':result['final']['physical']['tick'],'supplement_final_tick':supplement['after']['physical']['tick'],
      'scope':'Measured host operational duration, not simulated physical time or a claim of CPU execution every instant. R03 retains its frozen 3605-second horizon and reserved outcomes. The three complete technical pause-to-resume intervals (including process reload) are conservatively discounted with archived UTC execution boundaries; the supplement is a separate monotonic sixty-second no-teaching continuation of the same life. No claim of one uninterrupted process, autonomous learning, survival or stability beyond the measured conditions.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();r=calculate(a.evidencia);a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(r,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'issues':r['issues'],'combined_active_seconds':r['combined_unpaused_operational_seconds_lower_estimate']}));return bool(r['issues'])
if __name__=='__main__':raise SystemExit(main())
