"""Root-approved pre-Native revision: GUARD/SHAM ×legal wait0/3 first."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;P=H.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def once(t,a,b):
    if t.count(a)!=1:raise ValueError('RecoveryR02 source anchor absent: '+a[:80])
    return t.replace(a,b,1)
def main():
    src=H/'ejecutar_RECUPERACION_PI05_R01.py';t=src.read_text('utf8');out=H/'ejecutar_RECUPERACION_PI05_R02.py'
    if out.exists():raise ValueError('Protect existing R02')
    t=t.replace("PROTOCOL=P/'control/PROTOCOLO_RECUPERACION_PI05_R01.json'","PROTOCOL=P/'control/PROTOCOLO_RECUPERACION_PI05_R02.json'")
    t=once(t,"calendar=planned_calendar(818074,bool(phase));need(calendar['expected_delta_ticks']<=600,'Bounded old recovery comparison horizon')",
       "start_FI=818074+a.espera;calendar=planned_calendar(start_FI,bool(phase));need(calendar['horizon_tick']-818074<=600,'Bounded entire wait plus original comparison horizon')")
    t=t.replace("floor+calendar['expected_delta_ticks']<=","floor+calendar['horizon_tick']-818074<=")
    t=once(t,"if 818074<=calendar['query_tick']+x<=calendar['horizon_tick']","if start_FI<=calendar['query_tick']+x<=calendar['horizon_tick']")
    t=once(t,"'calendar':calendar,'Native_ticks':0,'no_owner':True","'calendar':calendar,'legal_wait_first':a.espera,'total_planned_Native_ticks':calendar['horizon_tick']-818074,'Native_ticks':0,'no_owner':True")
    t=once(t,'prep=None;actual=None;summary=None;owner=None;closed=False;error=None;guard_final=None;support_field=None;allcounts=None',
        'wait_packet=None;prep=None;actual=None;summary=None;owner=None;closed=False;error=None;guard_final=None;support_field=None;allcounts=None')
    a="        with Owner(a.vida,a.tag)as owner:\n            prep=owner.material"
    b="""        with Owner(a.vida,a.tag)as owner:
            if a.espera:
                wait_packet=owner.material(a.tag+'_ESPERA',{'modo':'eci01-pi05-esperar','ticks':a.espera},feedback='omit',allow_failure=True)
                need(wait_packet['before_tick']==818074 and wait_packet['after_tick']==start_FI,'Legal wait did not preserve declared age')
            prep=owner.material"""
    t=once(t,a,b)
    t=once(t,"need(prep['before_tick']==818074 and prep['after_tick']==818074,'Support preparation advanced Native age')",
        "need(prep['before_tick']==start_FI and prep['after_tick']==start_FI,'Support preparation advanced Native age')")
    t=once(t,"summary['before_tick']==818074 and summary['after_tick']==calendar['horizon_tick']",
        "summary['before_tick']==start_FI and summary['after_tick']==calendar['horizon_tick']")
    t=once(t,"guard_final['requested_tick']==818076","guard_final['requested_tick']==start_FI+2")
    t=once(t,"'schema':'DEE.PI05.P0_recovery_matched_diagnosis.R01'","'schema':'DEE.PI05.P0_recovery_matched_diagnosis.R02'")
    t=once(t,"'calendar_preregistered_from_old_contract':calendar,'prepare_literal':prepare,'FI_literal':fi,",
        "'calendar_preregistered_from_old_contract':calendar,'legal_wait_first_ticks':a.espera,'wait_packet':wait_packet,'prepare_literal':prepare,'FI_literal':fi,")
    t=once(t,"'new_Native_ticks':None if actual is None else actual['after_tick']-actual['before_tick'],",
        "'new_Native_ticks':(read(cardpath)['physical']['tick']-818074)if closed else(None if actual is None else actual['after_tick']-818074),\n        'FI_only_Native_ticks':None if actual is None else actual['after_tick']-actual['before_tick'],")
    t=once(t,"ap.add_argument('--dry-run',action='store_true');raise SystemExit", "ap.add_argument('--espera',type=int,choices=(0,3),required=True);ap.add_argument('--dry-run',action='store_true');raise SystemExit")
    ast.parse(t);out.write_text(t,encoding='utf8')
    p=json.loads((P/'control/PROTOCOLO_RECUPERACION_PI05_R01.json').read_text('utf8'))
    p.update(schema='DEE.PI05.P0_recovery_runner.protocol.R02',runner_sha256=sha(out),wait_ticks=[0,3],
        previous_prepared_unexecuted_R01={'runner_sha256':sha(src),'protocol_sha256':sha(P/'control/PROTOCOLO_RECUPERACION_PI05_R01.json')},
        phase_control_cases=[{'condition':c,'wait_first_ticks':w,'source_tick':818074,'FI_start':818074+w,
            'support_scheduled_tick':818076+w,'expected_input_count':177}for w in(0,3)for c in('guardia','sham')],
        ordering='LegalWAIT0or3 FIRST (no Native inputs), then exactly one support prepared0ticks at current+2, then originalFI14/3normal/global without reinjection.',
        no_support_arm='Not included: historical176 baseline exists; matched guard/sham177 holds dose within each phase.')
    # Normal is selected for this phase contrast to conserve capture allowance;
    # R01 remains the separately prepared global-transit recovery diagnosis.
    t=out.read_text('utf8').replace("'captura':'global'","'captura':'normal'")
    old="""            cap=summary['external_global_capture'];need(cap and not cap['missing_planned_ticks'],'Missing frozen global frames')
            target=Path(cap['directory']).resolve();need(target.is_relative_to((S/'estado/observacion_pasiva'/a.vida).resolve()),'Unexpected telemetry directory')
            need(sha(target/'INDEX.json')==cap['index_sha256'],'Global index changed')
            rows=read(target/'INDEX.json')['frames'];need([r['tick']for r in rows]==[calendar['query_tick']+x for x in offsets],'Frozen capture times differ')"""
    t=once(t,old,"            need(summary['external_global_capture']is None,'Normal phase control must not silently record global arrays')")
    # Read existing usage for provenance only; no new global frames inR02.
    t=once(t,"need(usage['anchors']+len(anchors)<=budget['budget']['full_global_anchors_max'],'Anchor allowance exceeded')",
        "need(usage['anchors']<=budget['budget']['full_global_anchors_max'],'Existing anchor allowance exceeded')")
    t=once(t,"need(usage['delta_frames']+len(offsets)-len(anchors)<=budget['budget']['one_tick_lossless_delta_frames_max'],'Delta allowance exceeded')",
        "need(usage['delta_frames']<=budget['budget']['one_tick_lossless_delta_frames_max'],'Existing delta allowance exceeded')")
    ast.parse(t);out.write_text(t,encoding='utf8');p['runner_sha256']=sha(out);p['capture']='normal';p['predicted_calendar_by_wait']={str(w):{
        'FI_start':818074+w,'query_tick':818130+w,'horizon_tick':818272+w,'total_ticks':198+w}for w in(0,3)}
    pp=P/'control/PROTOCOLO_RECUPERACION_PI05_R02.json';assert not pp.exists();pp.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'runner':str(out),'runner_sha256':sha(out),'protocol':str(pp),'protocol_sha256':sha(pp),'Native_executed':False}))
if __name__=='__main__':main()
