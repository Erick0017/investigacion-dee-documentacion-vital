"""Explain preserved failed metadata gate; do not revise it or rerun Native."""
from pathlib import Path
import hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 originalproof=P/'control/FISICA_RP_R02_EP04_EP08_R01.json';proof=read(originalproof);recipefile=RP/'recetas/pi07_r02_8_ep04.json';recipe=read(recipefile);key='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1.queue.0'
 parser=load('PI07_queue_explanation_passive',RP/'observador_pasivo.py');compare=load('PI07_queue_explanation_diff',P/'codigo/comparar_RP_R02_EP04_pasivo_R01.py');actual=Path(proof['cuts']['EP04']['replay']);right=parser.snapshot_view(actual);rows=[]
 before={str(originalproof):sha(originalproof),str(recipefile):sha(recipefile),str(actual):sha(actual)}
 for item in recipe['expected_EP04_Native']['all_same_cut_candidates']:
  file=Path(item['path'])
  if sha(file)!=item['sha256']:raise ValueError('Predetermined original candidate changed')
  before[str(file)]=sha(file);left=parser.snapshot_view(file);qleft=json.loads(left['metadata'].get(key,'null'));qright=json.loads(right['metadata'].get(key,'null'))
  rows.append({'source':str(file),'source_sha256':sha(file),'full_Native_fields_equal':all(left[k]==right[k]for k in('physical','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase')),'original_queue0':qleft,'replay_queue0':qright,'queue0_changed_JSON_leaves':compare.diff(qleft,qright)})
 servicefile=P/'estados/candidato/sistema/app/servicio_persistente.py'
 result={'schema':'DEE.PI07.RP.EP04.transport_metadata_gate_explanation.v1','original_failed_gate_proof':{'path':str(originalproof),'sha256':sha(originalproof),'bounded_comparison_criteria_met':proof['bounded_comparison_criteria_met']},'criterion_unchanged':True,'before_execution_recipe_unchanged_sha256':sha(recipefile),'all_three_predetermined_candidates':rows,
  'source_contract':{'path':str(servicefile),'sha256':sha(servicefile),'lines':[167,172,239,241,293,298],'mechanism':'PersistentService.checkpoint serializes external outstanding transport requests into metadata SERVICE.queue.slot. The current active request is excluded when checkpoint() runs; cached metadata may describe a different outstanding request at the same Native cut. This is separate from Native scheduled input agenda/receipts, which the full causal-prefix comparison covers exactly.'},
  'interpretation':'EP04 fixed original candidate contains next external EP05; cold diagnostic snapshot contains the RP-only EP04 wrapper envelope. Its requested mode, ID, arrival time and payload hash differ. This is declared transport/instrumentation provenance, but the original strict comparison did not exempt this key, so overall false remains preserved. Do not select another source candidate for a pass or equate this diagnostic snapshot with a complete coherent service export.',
  'Native_executed':False,'new_ticks':0,'sources_unchanged_during_read':all(sha(Path(path))==h for path,h in before.items()),'inspected_sha256':before}
 out=P/'control/EXPLICACION_TRANSPORTE_EP04_RP_PI07_R01.json'
 with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(out),'sha256':sha(out),'all_three_full_Native_equal':all(v['full_Native_fields_equal']for v in rows),'original_gate_remains':result['original_failed_gate_proof']['bounded_comparison_criteria_met'],'Native_executed':False}))
if __name__=='__main__':main()
