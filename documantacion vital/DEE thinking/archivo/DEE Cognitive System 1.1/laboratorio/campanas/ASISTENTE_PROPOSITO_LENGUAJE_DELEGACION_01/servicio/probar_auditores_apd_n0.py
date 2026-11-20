"""Instrument-only regression fixtures plus existing archived pilot; zero ticks."""
import argparse,gzip,hashlib,importlib.util,json
from pathlib import Path
def module(path):
    s=importlib.util.spec_from_file_location(path.stem,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
    p=argparse.ArgumentParser();p.add_argument('--piloto',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();here=Path(__file__).parent;c=module(here/'recalcular_servicio_apd.py');audit=c.apd;checks={}
    original=json.loads(gzip.decompress(a.piloto.read_bytes()));top=json.loads(original['records']['apdpilot_apd']['result'])['result'];ap=audit.audit(top['rows'][0]);checks['existing_pilot_APD_no_decoder_disagreement']=not ap['issues'];checks['existing_pilot_native_number20']=ap['numeric_result']==20 and ap['correct_when_responded']is True
    count=json.loads(original['records']['apdpilot_count']['result'])['result']['rows'][0];co=audit.audit(count);checks['existing_pilot_native_count2']=co['numeric']['value']==2 and co['correct_when_responded']is True
    prior=json.loads(gzip.decompress(a.baseline.read_bytes()));history={}
    for _,node in c.walk(prior['result']):
        if node.get('kind')=='lexical_query':
            d=audit.lexical(node['reader']);history[node['form']]=d['command'];checks['baseline_'+node['form']]=d['agrees_with_archived_command']and d['gate_count']==24
    checks['baseline_old10_no_new_forms']=set(history)=={'alfa','beta','gamma','delta','epsilon','zeta','suma','diferencia','agrega','resta'}
    r={'requested_tick':1,'effective_tick':None,'channels':['fixture'],'kind':'experience','status':'scheduled','reason':''};s={**r,'effective_tick':2,'status':'applied'};checks['receipt_progress_not_false_conflict']=audit.admissions([{'id':1,'receipt':r},{'id':1,'receipt':s}])['conflicting_receipt_ids']==[];checks['receipt_progress_counts_final_applied']=audit.admissions([{'id':1,'receipt':s},{'id':1,'receipt':r}])['by_status']=={'applied':1}
    bad={**s,'requested_tick':3};checks['actual_receipt_identity_conflict_detected']=audit.admissions([{'id':1,'receipt':s},{'id':1,'receipt':bad}])['conflicting_receipt_ids']==[1]
    old=json.loads(original['records']['apdpilot_old6']['result'])['result']['rows'][0]['result']['rows'][0]['reader'];checks['old_memory_existing_decode']=c.memory(old)==old['formed_native_command']
    wrong=json.loads(json.dumps(old));q=next(o for o in wrong['panel']if int(o['raw'])!=0);u=int(q['raw']);sg=q['site'][2]-33;opposite=-sg;u=(u&~(15<<56))|((opposite&15)<<56);q['raw']=str(u);q['direction']=[0,0,opposite];checks['wrong_height_sign_not_read']=c.memory(wrong)is None
    result={'schema':'DEE.APD01.auditor_instrument_regressions.N0.v1','checks':checks,'all_true':all(checks.values()),'new_ticks':0,'synthetic_receipt_and_wrong_gate_cases':'Instrument fixtures, not an actual DEE world or newly observed cognitive behavior.','source_files':[{'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in(a.piloto,a.baseline)]}
    with a.salida.open('x',encoding='utf8')as f:json.dump(result,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(result));return not result['all_true']
if __name__=='__main__':raise SystemExit(main())
