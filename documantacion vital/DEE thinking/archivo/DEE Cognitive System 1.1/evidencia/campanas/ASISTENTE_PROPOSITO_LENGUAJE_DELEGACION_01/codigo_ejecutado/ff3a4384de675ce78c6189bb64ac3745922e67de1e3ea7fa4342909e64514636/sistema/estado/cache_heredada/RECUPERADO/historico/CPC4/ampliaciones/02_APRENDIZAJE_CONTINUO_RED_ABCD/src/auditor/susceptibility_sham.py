"""One eligible off-path sham after the frozen four-trajectory pilot."""
from datetime import datetime,timezone
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from src.auditor.passive import digest,operation_state,receipt
from src.auditor.susceptibility_pilot import sample
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')

def main():
    import dee_thinking as d
    out=ROOT/'resultados/auditor/SUSCEPTIBILITY_PILOT';pilot=json.loads((out/'RUN_SUMMARY.json').read_text(encoding='utf-8'))
    assert pilot['sham_followup_eligible']
    source=ROOT/'resultados/regulacion/DUAL_CONFIRMATION/BA_AB/T520.deetsnap'
    meta=json.loads((source.parent/'MEASUREMENTS.json').read_text(encoding='utf-8'));spec=meta['spec']
    config={'id':'CPC4_A02.HISTORY_COMMON_E_B522.offpath_followup.v1','freeze_utc':datetime.now(timezone.utc).isoformat(),
       'followup_type':'EXPLORATORY_CONDITIONAL_CONTROL_AFTER_FROZEN_FOUR_ARMS',
       'eligibility':'BA_AB real admitted common event changed expression at524/525 without relational rewrite.',
       'parent_pilot_config_sha256':pilot['config_sha256'],'source_sha256':sha(source),
       'channel':'m2.B','load':3,'requested_tick':522,'horizon':525,
       'reason':'Same initial state, scalar payload, direction+Y,state5001,semantic1 and clock522 at input site, but another already declared physical inlet. Its toroidal distance19 from comparator1 exceeds the three-tick conservative radius9 when overflow is absent.',
       'do_not_claim':'Not outside influence forever, not a negative-memory result, not an autonomous action or MAIN intervention.'}
    cp=out/'FOLLOWUP_SHAM_CONFIG.json';assert not cp.exists();put(cp,config)
    parent=d.OrganizationalWorld.load_snapshot(str(source));original=operation_state(parent);w=parent.fork()
    channel=next(i.channel for i in w.interfaces if i.name=='m2.B')
    assert [channel.direction.dx,channel.direction.dy,channel.direction.dz]==[0,1,0] and channel.state==5001 and channel.semantic==1
    initial=digest(w);event=w.submit('m2.B',3,522);assert digest(w)==initial
    folder=out/'BA_AB__SHAM_M2_B522';folder.mkdir();trace=[];max_loads=[]
    for tick in range(520,526):
        trace.append(sample(w,spec))
        values=[d.decode_record(v).s_reg for v in w.runtime.raw_copy() if v]
        max_loads.append({'tick':tick,'max_s_reg':max(values,default=0)})
        if tick in (522,523,525):w.save_snapshot(str(folder/f'T{tick}.deetsnap'))
        if tick<525:w.advance()
    actual_receipt=receipt(w.runtime.receipt(event.id));assert operation_state(parent)==original
    omitted=json.loads((out/'BA_AB__OMITTED_E/MEASUREMENTS.json').read_text(encoding='utf-8'))
    common=json.loads((out/'BA_AB__COMMON_E_B522/MEASUREMENTS.json').read_text(encoding='utf-8'))
    def m1(r):return [x['memories']['1'] for x in r]
    result={'id':'BA_AB__SHAM_M2_B522','mode':'EXPERIENCE_PROTOCOL_ON_FULL_OPERATIVE_FORK',
       'source':str(source.relative_to(ROOT)),'source_sha256':sha(source),'config_sha256':sha(cp),
       'receipt':actual_receipt,'trace':trace,'final':trace[-1],'max_loads':max_loads,
       'same_memory1_trace_as_omitted':m1(trace)==m1(omitted['trace']),
       'same_memory1_trace_as_real_event':m1(trace)==m1(common['trace']),
       'parent_unchanged':operation_state(parent)==original,'manual_RAW_clock_edits':0,
       'scope':config['do_not_claim'],'source_code_sha256':sha(__file__)}
    put(folder/'MEASUREMENTS.json',result)
    put(out/'SHAM_FOLLOWUP_RESULT.json',{'receipt':actual_receipt,
       'same_memory1_trace_as_omitted':result['same_memory1_trace_as_omitted'],
       'same_memory1_trace_as_real_event':result['same_memory1_trace_as_real_event'],
       'max_s_reg':max(x['max_s_reg'] for x in max_loads),'horizon':[520,525],
       'additional_fresh_preparations':0,'additional_continuation_forks':1,
       'evidence':str((folder/'MEASUREMENTS.json').relative_to(ROOT)),
       'scope':'An actually admitted off-path comparable event is a finite selective-expression control; no extra parameter search.'})
    print(json.dumps({'status':actual_receipt['status'],'same_M1_as_omitted':result['same_memory1_trace_as_omitted'],
       'same_M1_as_real':result['same_memory1_trace_as_real_event']}))

if __name__=='__main__':main()
