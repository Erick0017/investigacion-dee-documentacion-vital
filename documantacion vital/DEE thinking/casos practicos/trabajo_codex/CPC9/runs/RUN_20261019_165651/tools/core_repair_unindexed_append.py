"""Restore the last verified store prefix after a pre-engine missing-member exit."""
from pathlib import Path
import hashlib,json,os
RUN=Path(__file__).resolve().parents[1];CORE=RUN/'core/DEE_COGNITIVE_CORE';store=CORE/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz';index=CORE/'documentacion/INDICE_MIEMBROS.json';expected=json.loads(index.read_text(encoding='utf8'))['content_store_sha256'];b=store.read_bytes();candidates=[];start=0
while True:
 k=b.find(b'RECUPERACION_POR_HASH.jsonl\x00',start)
 if k<0:break
 header=k-10
 if header>=0 and b[header:header+3]==b'\x1f\x8b\x08':candidates.append(header)
 start=k+1
found=next((n for n in reversed(candidates)if hashlib.sha256(memoryview(b)[:n]).hexdigest()==expected),None)
assert found is not None,'No cryptographically verified prior store prefix found; do not alter anything'
tail=RUN/'notes/core_audit/STORE_UNINDEXED_APPEND.bin';assert not tail.exists();tail.write_bytes(b[found:]);candidate=store.with_name('RECUPERACION_POR_HASH.repair.gz');candidate.write_bytes(memoryview(b)[:found]);assert hashlib.sha256(candidate.read_bytes()).hexdigest()==expected;os.replace(candidate,store)
report={'stage':'binary builder, no engine launched','reason':'CPC6 archive stores selected states as .deetsnap.gz; preflight requested .deetsnap and exited before index commit','restored_prefix_bytes':found,'restored_sha256':expected,'excluded_unindexed_tail_bytes':len(b)-found,'tail_preserved':str(tail),'original_scientific_artifacts_modified':False}
(RUN/'notes/core_audit/STORE_APPEND_REPAIR.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(report))
