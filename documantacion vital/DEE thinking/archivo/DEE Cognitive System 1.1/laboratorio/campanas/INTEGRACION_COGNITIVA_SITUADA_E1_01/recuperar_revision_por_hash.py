"""Read-only bounded source recovery; emit only exact recorded SHA matches."""
from pathlib import Path
import hashlib,json
expected='641f3f628bc23351e3f24b3e2ca549723f62c4bdb38d05aa6c60c42077672e7c'
original=Path(__file__).with_name('ic_body_R1_guard_key_error.py').read_bytes()
corrected=original.replace(b"plan['guards']",b"plan.get('guards',[])")
candidates=[corrected]+[corrected.rstrip(bytes([10]))+bytes([10])*n for n in range(4)]
matched=next((b for b in candidates if hashlib.sha256(b).hexdigest()==expected),None)
print(json.dumps({'matched':matched is not None,'sha256':expected,'basis':'Archived pre-shunt body plus the single recorded guard-key fix; byteSHA confirmation required, no behavioral equivalence substituted.','text':matched.decode('utf8')if matched else None}))
