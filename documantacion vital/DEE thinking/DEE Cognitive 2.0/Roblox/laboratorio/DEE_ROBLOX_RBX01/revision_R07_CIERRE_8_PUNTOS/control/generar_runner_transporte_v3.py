"""FS-only mechanical versioning of the tested R06 transport/loop; no execution."""
from pathlib import Path
import ast,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT.parent/'revision_R06_INTEGRAL_V2'
def put(name,text):
    ast.parse(text);p=ROOT/name
    if p.exists():raise FileExistsError(p)
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf8')
    return {'file':name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
rows=[]
for old,new in [('mcp_persistente_R06.py','mcp_persistente_v3.py'),('transporte_comprimido_R06.py','transporte_comprimido_v3.py')]:
    text=(OLD/'control'/old).read_text('utf8').replace('WorldAPI_R06','WorldAPI_R07')
    if old.startswith('transporte'):text=text.replace("SCHEMA='DEE.R06.ZstdFrozenBytes.R01'","SCHEMA='DEE.R07.ZstdFrozenBytes.R01'").replace("'R06Zstd_'","'R07Zstd_'")
    rows.append(put('control/'+new,text))
text=(OLD/'control/run_integrated_R06.py').read_text('utf8')
text=text.replace('FINISH=1794802380','FINISH=1794863220').replace('2026-11-16T04:13:00Z','2026-11-16T21:07:00Z')
text=text.replace('WorldAPI_R06','WorldAPI_R07').replace('INTEGRAL_V2_MAIN','INTEGRAL_V3_MAIN')
text=text.replace("protocol=read(ROOT/'protocolo/PROTOCOLO_INTEGRAL_V2_R01.json')", "protocol={'native_hard_finish_utc':'2026-11-16T21:07:00Z','deadline_new_episodes_utc':'2026-11-16T20:00:00Z'}")
text=text.replace("need(life=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_MAIN','Only declared R06 candidate')", "need(life.startswith('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_') and life.rsplit('_',1)[-1] in ('MAIN','CTRL1','CTRL','PILOT'),'Only explicitly scoped R07 candidate/control/pilot')")
text=text.replace('5<=a.stop_cycle<=28','29<=a.stop_cycle<=52').replace("need(time.time()<new_cut-1500,'No new block without finite margin')","need(time.time()<new_cut-600,'No new block without finite margin')")
text=text.replace("session=a.session or 'R06_MAIN_'", "session=a.session or 'R07_MAIN_'")
text=text.replace("world=World(a.studio_id,output,record)","world=World(a.studio_id,output,record,expected_place=a.expected_place)")
text=text.replace("owner_support_integral_v2.py','_r06_support'", "owner_support_v3.py','_r07_support'").replace("adapter_integral_v2.py','_r06_adapter'", "adapter_v3.py','_r07_adapter'")
text=text.replace("record('PROTOCOL_STARTED',protocol_sha256=sha(ROOT/'protocolo/PROTOCOLO_INTEGRAL_V2_R01.json'),", "record('PROTOCOL_STARTED',prospective_protocol=protocol,")
text=text.replace("tag='R06_INTEGRAL'", "tag='R07_INTEGRAL'").replace("operation='R06_'", "operation='R07_'")
text=text.replace("'new_opportunity':cycle-4", "'new_opportunity':cycle-28").replace("'host_order_prepared':cycle<=22", "'host_order_prepared':False")
text=text.replace("'R06_PAIR_'", "'R07_PAIR_'").replace("DEE.RBX01.R06.integrated.result.R01", "DEE.RBX01.R07.integrated.result.R01")
text=text.replace(" world=World(a.studio_id", " world=World(a.studio_id")
# Public import is pure. The actual SDK is instantiated only by execute().
text=text.replace("class World:\n", "class LegacyWorld:\n",1)
marker='\ndef execute(a):'
insert="\ndef _world_class():\n return load(ROOT/'control/world_comprimido_v3.py','_r07_world_transport').CompressedWorld\n\nclass World:\n def __new__(cls,*args,**kwargs):return _world_class()(*args,**kwargs)\n"
text=text.replace(marker,insert+marker)
text=text.replace("p.add_argument('--session')", "p.add_argument('--session');p.add_argument('--expected-place',default='DEE_RBX01_R07_NATIVE.rbxlx')")
# Close the SDK even after a material failure; do not replay an operation.
text=text.replace(" print(json.dumps({k:v for k,v in result.items()if k!='rows'},ensure_ascii=False))", " world.close()\n print(json.dumps({k:v for k,v in result.items()if k!='rows'},ensure_ascii=False))")
rows.append(put('control/run_integrated_v3.py',text))
text=(OLD/'control/world_comprimido_R06.py').read_text('utf8')
text=text.replace("run_integrated_R06.py','_r06_original_world_base'", "run_integrated_v3.py','_r07_original_world_base'")
text=text.replace("mcp_persistente_R06.py", "mcp_persistente_v3.py").replace("transporte_comprimido_R06.py", "transporte_comprimido_v3.py")
text=text.replace('DEE_RBX01_INTEGRAL_V2_NATIVE.rbxlx','DEE_RBX01_R07_NATIVE.rbxlx').replace('WorldAPI_R06','WorldAPI_R07')
text=text.replace('class CompressedWorld(BASE.World):','class CompressedWorld(BASE.LegacyWorld):').replace('R06_TECHNICAL_IDENTITY','R07_TECHNICAL_IDENTITY').replace('R06_VERIFY_RESTORE_','R07_VERIFY_RESTORE_')
# R07 first restores the complete R06 state then adds the declared path-motor
# anatomy. Do not misrepresent that new anatomy as byte-identical geometry.
begin=text.index('        initial_environment_clone=')
end=text.index('        comparison=compare_values(before,after)',begin)
text=text[:begin]+'''        initial_environment_clone=(state['native_life_id']!=identity['life'] or state['world_id']!=restored['world_id'])
        if initial_environment_clone:
            # Every inherited S field is preserved except transport/UI fields.
            # New motor anatomy and additional motor bookkeeping are explicit
            # preparation, not Native learning; original raw source is retained.
            old_s=before['S'];new_s=after['S']
            inherited={key:new_s.get(key)for key in old_s}
            for key in ('lifeId','sessionId'):inherited[key]=old_s.get(key)
            before={'S':old_s};after={'S':inherited}
''' +text[end:]
text=text.replace("comparison_mode='INITIAL_ENVIRONMENT_CLONE_WITH_NEW_TRANSPORT_IDENTITIES'", "prepared_motor_anatomy_change=initial_environment_clone, comparison_mode='PARENT_CONTENTS_AND_COUNTERS_WITH_DECLARED_NEW_MOTOR_ANATOMY'")
rows.append(put('control/world_comprimido_v3.py',text))
report={'schema':'DEE.R07.runner_transport.versioning.R01','Native_calls':0,'MCP_calls':0,'sources':rows,'source_revision':str(OLD),'first_parent_expected':'derived from literal source checkpoint, never substituted with R07 identity','route_override':False}
(ROOT/'control/RUNNER_TRANSPORTE_V3_GENERADO.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
