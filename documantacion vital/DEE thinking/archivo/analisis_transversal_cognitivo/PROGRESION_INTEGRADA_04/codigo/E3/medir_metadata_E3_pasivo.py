"""Read frozen snapshot metadata and exact official JSON functions as text.

No DEE import, Native loading, SQLite, or world mutation. Outputs are new P4
diagnostic evidence only. Native1MiB per-value bound is kept unchanged.
"""
from pathlib import Path
import ast,copy,hashlib,json,runpy
P=Path(__file__).resolve().parents[2];C=P.parents[2]/'DEE Cognitive 2.0'
OUT=P/'control/E3_CUOTA_METADATA_MEDIDA_PASIVA.json'
if OUT.exists():raise FileExistsError('Preserve prior measurement')
def sha(data):return hashlib.sha256(data).hexdigest()
pure=runpy.run_path(str(C/'reproducibilidad/observador_pasivo.py'),run_name='explicit_passive_snapshot_parser')
official=C/'motor/python313/site-packages/dee_thinking/persistence.py';text=official.read_text(encoding='utf-8')
tree=ast.parse(text);functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
ns={'json':json,'DEFAULT_MAX_METADATA_BYTES':8*1024**2}
for name in('_positive_integer','_walk_json','encode_metadata'):
    exec(compile(ast.Module(body=[functions[name]],type_ignores=[]),str(official),'exec'),ns)
encode=ns['encode_metadata']
active=json.loads((C/'sistema/estado/ACTIVO.json').read_text(encoding='utf-8'))
snap=C/'sistema'/active['snapshot'];view=pure['snapshot_view'](snap)
if view['physical']['tick']!=775355 or sha(snap.read_bytes())!=active['snapshot_sha256']:raise ValueError('Exact protected source changed')
key='DEE.Cognitive.PI03.useful_delayed_task.R02';base_text=view['metadata'][key];base=json.loads(base_text)
if encode(base)!=base_text:raise ValueError('Official exact encoder differs from source metadata')
outer=json.loads((P/'ensayos/PI04_E3_REAL_R01_OP_1.json').read_text(encoding='utf-8'))
last=json.loads(outer['result'])['committed_snapshot'];snapshot=P/'estados/candidato/sistema'/last['snapshot']
if sha(snapshot.read_bytes())!=last['snapshot_sha256']:raise ValueError('Exact last completed checkpoint changed')
lastview=pure['snapshot_view'](snapshot);last_text=lastview['metadata'][key];m=json.loads(last_text)
if encode(m)!=last_text:raise ValueError('Exact encoder differs at closedOP1')
source=m.get('current_resource_source',m.get('resource_source'));source_bytes=encode(source).encode('utf-8')
item_sources=[{'index':i,'id':h['id'],'full_source_bytes':len(encode(h['source']).encode('utf-8'))if'source'in h else 0}for i,h in enumerate(m.get('resource_supply_history',[]))]
runtime=C.parent/'4.5/DEE_thinking_4_5_0/source/src/runtime.cpp'
rt=runtime.read_text(encoding='utf-8')
if 'constexpr std::size_t kMaxSnapshotStringBytes = 1U << 20;'not in rt or'if (value.size() > kMaxSnapshotStringBytes)'not in rt:raise ValueError('Official quota source differs')
result={'schema':'PI04.E3.actual_metadata_quota.passive.v1','new_native_ticks':0,'actual_DEE_imports':0,'official_runtime_limit_bytes':1048576,
        'official_Python_encoder_default_bytes':8*1024**2,'scope':'Per-Native-metadata-value1MiB, distinct from Python JSON8MiB guard; neither limit changed',
        'source775355':{'snapshot':str(snap),'sha256':active['snapshot_sha256'],'task_metadata_bytes':len(base_text.encode('utf-8')),'supplies':len(base.get('resource_supply_history',[])),'headroom_bytes':1048576-len(base_text.encode('utf-8'))},
        'last_completed776919':{'snapshot':str(snapshot),'sha256':last['snapshot_sha256'],'task_metadata_bytes':len(last_text.encode('utf-8')),'supplies':len(m.get('resource_supply_history',[])),'headroom_bytes':1048576-len(last_text.encode('utf-8'))},
        'current_full_source':{'bytes':len(source_bytes),'sha256':sha(source_bytes),'actual_first':source['first']['numeric_result'],'actual_second':source['second']['numeric_result']},
        'historical_full_sources':item_sources,'source_locations':{'runtime.cpp':str(runtime),'runtime.cpp_sha256':sha(runtime.read_bytes()),'persistence.py':str(official),'persistence.py_sha256':sha(official.read_bytes())}}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
