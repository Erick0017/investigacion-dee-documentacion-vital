"""Static source extraction only: no Native or edits to PI03/product originals."""
from pathlib import Path
import ast,hashlib,json
P=Path(__file__).resolve().parents[2]
C=P.parents[2]/'DEE Cognitive 2.0'
source=C/'sistema/capacidades/pi03_tarea_diferida_R02.py'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='b136e79abb6e07efcd8b69da0a37cc8d667d7140788e18c490975f8e2a88e40b'
text=source.read_text(encoding='utf-8');node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name=='opportunity')
body=ast.get_source_segment(text,node)
changes={
 'def opportunity(a, directory):':'def _op_body(a, directory):',
 '    ready_tick = calendar["outcome_injection_tick"] - 1':'    _e3_prequery(a, calendar, before_banks, start)\n    ready_tick = calendar["outcome_injection_tick"] - 1',
 'returned_failed = False if m["control"] == "return_nonfailure" else effect["failed"]':'returned_failed = _e3_feedback(a, effect["failed"], calendar, before_banks, start)',
 '"control": m["control"], "before_tick": start':'"control": "PI04_E3_" + _e3_get(a)["arm"], "before_tick": start',
}
for a,b in changes.items():
    if body.count(a)!=1:raise ValueError('Exact source anchor differs '+a)
    body=body.replace(a,b)
dest=Path(__file__).with_name('pi04_e3_contingencia.py');current=dest.read_text(encoding='utf-8')
start='# BEGIN_EXACT_PI03_OPPORTUNITY_BODY';end='# END_EXACT_PI03_OPPORTUNITY_BODY'
a=current.index(start)+len(start);b=current.index(end,a)
if 'def _op_body' in current[a:b]:raise ValueError('Body already preserved; no automatic overwrite')
new=current[:a]+'\n'+body+'\n'+current[b:];ast.parse(new)
dest.write_text(new,encoding='utf-8')
print(json.dumps({'source_hash':hashlib.sha256(source.read_bytes()).hexdigest(),'module_hash':hashlib.sha256(dest.read_bytes()).hexdigest(),'new_native_ticks':0,'exact_source_transformations':list(changes)},ensure_ascii=False))
