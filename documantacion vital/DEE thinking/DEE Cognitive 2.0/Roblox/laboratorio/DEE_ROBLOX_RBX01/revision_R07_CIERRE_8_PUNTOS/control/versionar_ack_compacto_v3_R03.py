"""Do not return inherited command history through a bounded SDK text reply.

The complete World is still transferred byte-for-byte by compressed checkpoint
and compared before opening any Native owner. This changes only the ACK size.
"""
from pathlib import Path
import ast,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def save(p,text):
    ast.parse(text)
    with p.open('x',encoding='utf8')as f:f.write(text)
    return {'file':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
s=(ROOT/'control/world_comprimido_v3_R02.py').read_text('utf8')
s=s.replace("run_integrated_v3_R02.py','_r07_original_world_base_R02'", "run_integrated_v3_R03.py','_r07_original_world_base_R03'")
old="        result=self.mcp(COMP.import_apply_code(meta,expected,identity),'restore_apply_once_zstd')"
new='''        # initialize's full restored.controller includes the complete ancestral
        # command history and may exceed the SDK text envelope. Return only its
        # technical ACK; the following compressed capture still verifies ALL
        # World contents, not a summary of that state.
        apply_code=COMP.import_apply_code(meta,expected,identity)
        compact='local r07Ack=(function()\\n'+apply_code+'\\nend)();return {restored={checkpoint_id=r07Ack.restored.checkpoint_id},S=r07Ack.S,phase=r07Ack.phase,original_events=r07Ack.original_events,current_events=r07Ack.current_events,new_Native_ticks=r07Ack.new_Native_ticks}'
        result=self.mcp(compact,'restore_apply_once_zstd_compact_ack')'''
if old not in s:raise ValueError('Expected frozen R02 apply call missing')
s=s.replace(old,new)
rows=[save(ROOT/'control/world_comprimido_v3_R03.py',s)]
s=(ROOT/'control/run_integrated_v3_R02.py').read_text('utf8').replace('world_comprimido_v3_R02.py','world_comprimido_v3_R03.py')
rows.append(save(ROOT/'control/run_integrated_v3_R03.py',s))
with(ROOT/'control/CORRECCION_ACK_COMPACTO_V3_R03.json').open('x',encoding='utf8')as f:
    json.dump({'Native_calls':0,'MCP_calls':0,'old_R02_preserved':True,'changes':['Only initialize technical ACK shape shrinks; complete post-restore compressed capture and comparison remain mandatory before configured_owner'],
      'unknown_mutations_not_retried':True,'files':rows},f,ensure_ascii=False,indent=2)
print(json.dumps(rows))
