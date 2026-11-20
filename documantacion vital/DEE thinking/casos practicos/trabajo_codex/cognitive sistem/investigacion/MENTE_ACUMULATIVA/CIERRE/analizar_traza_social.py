"""Archived-only passive-recorder and private-observation checks."""
from pathlib import Path
import argparse,gzip,hashlib,json
def read(p):return json.loads(gzip.decompress(p.read_bytes()))
def subset_equal(a,b):
    if isinstance(a,dict):return all(k in b and subset_equal(v,b[k])for k,v in a.items())
    if isinstance(a,list):return len(a)==len(b)and all(subset_equal(x,y)for x,y in zip(a,b))
    return a==b
def calculate(ev):
    originals=read(ev/'16_RESERVA_FINAL_MAIN.json.gz')['result']
    trace=read(ev/'20_TRAZA_SOCIAL.json.gz')['result']
    no_B=read(ev/'16U_RESERVA_FINAL_NO_B.json.gz')['result']
    checks=[];social=[]
    for i,(a,b)in enumerate(zip(originals['result']['rows'],trace['result']['rows'])):
        detailed={f['tick']:f for f in b['frames']}
        checks.append(dict(ordinal=i,common_sample_frames=len(a['frames']),
            all_common_observations_identical=all(subset_equal(f,detailed[f['tick']])for f in a['frames']),
            receipts_identical=a['requests']==b['requests'],
            extra_receipts_identical=a['sensory_extra']['request_receipts']==b['sensory_extra']['request_receipts'],
            action_identical=a['formed_native_command']==b['formed_native_command'],
            useful_identical=a['job_completed']==b['job_completed']))
        if 'privada_B'in b['situation']:
            waypoints=[]
            for f in b['frames']:
                if f['tick']<b['row']['critical_tick']+13:continue
                buses=[]
                for name,lane in f['message_waypoints'].items():
                    q=lane[6]
                    if q['state']>0:buses.append(dict(lane=name,site=q['site'],raw=q['raw'],direction=q['direction'],s_reg=q['s_reg']))
                if buses:waypoints.append(dict(tick=f['tick'],active_bus_observations=buses))
            social.append(dict(ordinal=i,raw_private=b['situation']['privada_B'],
                input_receipts=[q for q in b['requests']if 'private.B_incoming'in q['port']],
                current_action_precedes_private_observation=b['observed_result']['tick']<b['row']['private_input_fixed_tick'],
                bus_coverage='Both declared buses after the private entry through critical+80; not a whole-world lineage proof.',
                bus_events=waypoints,
                context_before=[x['s_reg']for x in b['before']['context_A']],
                context_after=[x['s_reg']for x in b['after']['context_A']]))
    fields=('N','tick','RAW_sha256','clocks_sha256')
    physical_match=lambda a,b:all(a['physical'][k]==b['physical'][k]for k in fields)
    flags=[all(x[k]for k in('all_common_observations_identical','receipts_identical','extra_receipts_identical','action_identical','useful_identical'))for x in checks]
    return dict(schema='MA.passive_trace_social.v1',recorder_checks=checks,
        recorder_final_physical_equal=physical_match(originals,trace),
        private_vs_no_B_final_physical_equal=physical_match(originals,no_B),
        private_vs_no_B_actions_equal=[r['formed_native_command']for r in originals['result']['rows']]==[r['formed_native_command']for r in no_B['result']['rows']],
        private_observations=social,
        discrepancies=[]if all(flags)and physical_match(originals,trace)else['passive_recorder_changed_observation_or_state'],
        scope='RAW/clocks equality is not identity of documentary metadata, receipts or complete files. Two private entries were not needed for the measured actions; no new useful social update is established.')
def main():
    p=argparse.ArgumentParser();p.add_argument('--evidencia',required=True,type=Path);p.add_argument('--salida',required=True,type=Path);a=p.parse_args()
    d=calculate(a.evidencia);a.salida.mkdir(parents=True,exist_ok=True)
    (a.salida/'TRAZA_SOCIAL.json').write_text(json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf8')
    print(json.dumps({'recorder_final_equal':d['recorder_final_physical_equal'],'private_vs_no_B_final_equal':d['private_vs_no_B_final_physical_equal'],'private_vs_no_B_actions_equal':d['private_vs_no_B_actions_equal'],'bus_event_counts':[len(x['bus_events'])for x in d['private_observations']],'discrepancies':d['discrepancies']}))
    return int(bool(d['discrepancies']))
if __name__=='__main__':raise SystemExit(main())
