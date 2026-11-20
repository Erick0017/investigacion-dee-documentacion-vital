"""Prospective administrative storage revision before ANY PI09 Native query."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=H/'SELLO_PI09_CONSULTA_R02.json'
 if out.exists():raise FileExistsError('R02 seal already exists')
 old=H/'SELLO_PI09_CONSULTA_R01.json';v=json.loads(old.read_text('utf8'));body=H/'pi09_consulta_selectiva_R02.py';proto=H/'PROTOCOLO_PI09_CONSULTA_R01.json';legacy=H/'pi08_consulta_condicional_C_R03.py'
 if sha(body)!='3b81573f4dc0d9401db2210f3b23694e1f1f4a4d820d7654bcbd1e1b42b2dfbf' or sha(proto)!='cb6973e6f1bd747de8da73ecda37497579370330f828ea43d559a61c86e45ad5':raise ValueError('Final R02/protocol pins changed; inspect before sealing')
 if any((P/'ensayos').glob('PI09_NATIVE_R01_*.json')):raise ValueError('A R01 query has run; cannot relabel its science')
 v.update(schema='DEE.PI09.selective_consultation.source_seal.R02',sealed_utc=datetime.now(timezone.utc).isoformat(),files_sha256={p.name:sha(p)for p in(body,proto,legacy)},prior_prospective_seal={'file':old.name,'sha256':sha(old),'PI09_queries_executed_under_R01':0},experimental_continuation_ids=['ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'],technical_revision={'reason':'Historical full first_stage_rows scale beyond the unchanged65536byte metadata limit at18opportunities','change':'Retain compact immutable witness references in metadata; full stage remains in journal, primary and immediate witness','Native_inputs_timing_readers_policy_and_returns_changed':False,'physical_bank_or_old_C_history_edited':False})
 v.update(no_Native_before_this_seal=False,no_PI09_consultation_queries_before_this_seal=True,other_Native_scope='The independent arithmetic diagnostics have already run under their frozen R01 sources; they are not consultation episodes or relabelled as R02.')
 out.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'seal':str(out),'sha256':sha(out),'Native_ticks_added_by_sealing':0}))
if __name__=='__main__':main()
