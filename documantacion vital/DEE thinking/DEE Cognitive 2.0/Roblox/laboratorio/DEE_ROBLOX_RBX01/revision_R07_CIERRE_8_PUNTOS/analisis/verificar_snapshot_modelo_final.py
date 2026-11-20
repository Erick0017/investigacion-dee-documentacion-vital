"""Audit immutable model snapshots against two closed result/event parts; no live history/model."""
import argparse,csv,hashlib,importlib.util,json
from pathlib import Path
s=importlib.util.spec_from_file_location('passive_source',Path(__file__).with_name('RECALCULO_CIERRE8_R07_R02.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def run(a):
 if a.output.exists()or not a.output.parent.is_dir():raise ValueError('Fresh output required')
 spec=json.loads(a.inputs.read_text('utf-8-sig'));src=m.Sources(a.source_root,a.package_root);manifest=src.json(spec['manifest']);state=src.json(spec['state']);quota=src.json(spec['quota']);history=[v for n,v in src.jsonl(spec['history'])];policy=[v for n,v in src.jsonl(spec['policy_events'])];issues=[]
 def check(ok,reason):
  if not ok:issues.append(reason)
 for f in manifest['files']:
  key=spec['by_name'][f['file']];raw=src.raw(key);check(len(raw)==f['bytes']and m.digest(raw)==f['sha256'],'SNAPSHOT_PIN_'+f['file'])
 check(state['pending']is None and len(state['cache'])==6,'CLOSED_CACHE_PENDING');check(state['model_journal_sha256']==m.digest(src.raw(spec['history'])),'JOURNAL_PIN')
 responses={v['call']:v for v in history if v['kind']=='RESPONSE'};requests={v['call']:v for v in history if v['kind']=='REQUEST'};check(set(responses)==set(requests)=={1,2,3,4},'FOUR_CALLS')
 expected={};phase_ops={}
 for block in spec['parts']:
  r=src.json(block['result']);check(r['owner_closed']and r['new_Native_ticks']==0,'PART_CLOSED_NON_NATIVE')
  for row in r['rows']:
   for key in('Native_Q1','Native_Q2'):
    out=row[key];expected[out['evidence']['model_call']]=out
  for n,event in src.jsonl(block['events']):
   if event.get('kind')=='BACKEND_COMPLETED':phase_ops[event['operation_id']]=event['result']
 check(len(expected)==4 and len(phase_ops)==6,'DENOMINATORS')
 for op,result in phase_ops.items():check(state['cache'][op]['result']==result,'CACHE_RESULT_'+op)
 messages=state['model']['messages'];rows=[]
 for call,response in sorted(responses.items()):
  result=expected[call];check(response['choice']['action']==result['action'],'MODEL_CHOICE_'+str(call));check(response['semantic_correction']is False and response['rejection']is None,'NO_SEMANTIC_CORRECTION')
  locations=[i for i,v in enumerate(messages)if v.get('role')=='assistant'and v.get('content')==response['response_content']]
  prefix_match=any(m.digest(m.canonical(messages[:i]).encode())==requests[call]['messages_sha256']for i in locations);check(prefix_match,'MESSAGE_PREFIX_'+str(call))
  rows.append({'call':call,'action':result['action'],'operation_id':result['operation_id'],'raw_response':response['response_content'],'wall_seconds':response['wall_seconds'],'prompt_eval_count':response['metrics'].get('prompt_eval_count'),'eval_count':response['metrics'].get('eval_count'),'message_prefix_hash_verified':prefix_match})
 check(quota['used']==5 and len(quota['reservations'])==5,'GLOBAL_QUOTA5');check(sum(x['run_id']==state['session_id']for x in quota['reservations'])==4,'OWN_QUOTA4')
 feedback=[v for v in history if v['kind']=='OWN_FEEDBACK'];check(len(feedback)==2 and all(v['no_inference']for v in feedback),'TWO_FEEDBACK_NO_INFERENCE');src.verify_unchanged()
 report={'schema':'DEE.R07.immutable_model_snapshot_audit.final.v1','issues':issues,'received_choices':4,'completed_opportunities':2,'target18':18,'backend_operations':6,'own_feedback_no_inference':2,'quota_used':5,'old_failed_call_separate':1,'pending':state['pending'],'cache_entries':len(state['cache']),'message_prefixes_verified':all(r['message_prefix_hash_verified']for r in rows),'policy_no_reset':manifest['no_history_reset'],'weights_manifest':quota['model_manifest_sha256'],'weight_updates':history[0]['weight_updates'],'own_API_messages_only':history[0]['external_memory'],'shared_Codex_context':history[0]['shared_Codex_context'],'options':state['model']['options'],'calls':rows,'API_eval_tokens_sum':sum(r['eval_count']for r in rows),'API_prompt_eval_counts_sum_repeated_context_not_unique_tokens':sum(r['prompt_eval_count']for r in rows),'scope':'Frozen copies only. API counters/wall latency are not kernel CPU,energy,Native ticks or learning. No actual q8 load/next31/capture inferred.','sources':list(src.records.values()),'Native_MCP_Studio_model_SQLite_calls':0}
 a.output.mkdir();(a.output/'AUDITORIA_SNAPSHOT_MODELO_FINAL.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 with(a.output/'RESPUESTAS_MODELO_CUATRO.csv').open('w',encoding='utf-8',newline='')as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print(json.dumps({'issues':issues,'choices':4,'episodes':2,'quota5':quota['used'],'no_live_history':True}));return 0 if not issues else 1
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--source-root',type=Path,required=True);p.add_argument('--package-root',type=Path);p.add_argument('--output',type=Path,required=True);raise SystemExit(run(p.parse_args()))
