"""Pure external-device/official-JSON quota test, zero Native execution.

Copies only tiny device files. Uses actual closed snapshot metadata and the
two recorded E3 actions, then explicit synthetic fixed+1 external actions.
Synthetic action/test ticks are never attributed to an E1 life or learning.
"""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,runpy,shutil
P=Path(__file__).resolve().parents[2];C=P.parents[2]/'DEE Cognitive 2.0';HERE=Path(__file__).resolve().parent
ROOT=P/'control/SUMINISTRO_METADATA_R02_PURO';ROOT.mkdir(exist_ok=False)
def sha(data):return hashlib.sha256(data).hexdigest()
def imp(name,file):
    spec=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
new=imp('PURE_R03_R02',HERE/'pi03_suministro_explicito_R03.py')
old=imp('PURE_R03_ORIGINAL',HERE/'pi03_suministro_explicito_R03_ORIGINAL.py')
device_module=imp('PURE_EXTERNAL_FILE_DEVICE',C/'sistema/capacidades/pi03_dispositivo_diferido_R02_PROPUESTA.py')
parse=runpy.run_path(str(C/'reproducibilidad/observador_pasivo.py'),run_name='PASSIVE_ONLY')['snapshot_view']
official=C/'motor/python313/site-packages/dee_thinking/persistence.py';tree=ast.parse(official.read_text(encoding='utf-8'));ns={'json':json,'DEFAULT_MAX_METADATA_BYTES':8*1024**2}
for name in('_positive_integer','_walk_json','encode_metadata'):
    exec(compile(ast.Module(body=[next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name)],type_ignores=[]),str(official),'exec'),ns)
new._encode_native_metadata=lambda m:ns['encode_metadata'](m,max_bytes=1048576)
KEY='DEE.Cognitive.PI03.useful_delayed_task.R02'
primary=json.loads((P/'ensayos/PI04_E3_REAL_R01_OP_1.json').read_text(encoding='utf-8'));last=json.loads(primary['result'])['committed_snapshot']
snap=P/'estados/candidato/sistema'/last['snapshot'];assert sha(snap.read_bytes())==last['snapshot_sha256']
metadata=parse(snap)['metadata'][KEY];base=json.loads(metadata)
assert base['opportunity']==26 and len(base['schedule'])==26 and len(base['resource_supply_history'])==6
source_device=C/'sistema/estado/servicios_locales/ECI02_PI03_MAIN/PI03_TAREA_DIFERIDA_R02/dispositivo'
recorded=[]
for i in(0,1):
    outer=json.loads((P/f'ensayos/PI04_E3_REAL_R01_OP_{i}.json').read_text(encoding='utf-8'));recorded.append(json.loads(outer['result'])['result']['rows'][0])
def tick_device(device,motor,action,ready,receipt_id):
    device.begin(motor,action,ready);effect=device.complete_due(ready)
    device.mark_feedback_scheduled(receipt_id,ready+1)
    device.reconcile_feedback({'id':receipt_id,'status':'applied','requested_tick':ready+1,'effective_tick':ready+1,'scope':'SYNTHETIC_MOCK_RECEIPT_NOT_NATIVE'})
    return effect
def prepare(label):
    dest=ROOT/label/'dispositivo'
    nodes=[source_device,*source_device.rglob('*')]
    assert not any(n.is_symlink()or bool(getattr(n.lstat(),'st_file_attributes',0)&0x400)for n in nodes)
    shutil.copytree(source_device,dest)
    d=device_module.DelayedFeeder(dest)
    for i,r in enumerate(recorded):
        effect=tick_device(d,r['applied_motor'],r['reader']['tick'],r['actual_effect']['consequence_tick'],900000+i)
        assert effect['failed']==r['actual_effect']['failed']and effect['actual_product_sha256']==r['actual_effect']['actual_product_sha256']
    assert d.m['opportunity']==26 and len(d.m['capsules'])==26
    assert d.m['products']==base['products']and d.m['rejections']==base['rejections']
    return copy.deepcopy(base),d
def commit_factory(m,folder,tick):
    journal=folder/'TASK_MOCK_EVENTS.jsonl';sizes=[]
    def commit(event):
        preview=new._preflight_task_record(m,event,tick[0])
        line=({'index':m['log_count'],'tick':tick[0],**event})
        encoded=(json.dumps(line,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8')
        with journal.open('ab')as f:f.write(encoded)
        m['log_count']+=1;m['log_chain_sha256']=sha(bytes.fromhex(m['log_chain_sha256'])+encoded)
        actual=ns['encode_metadata'](m,max_bytes=1048576)
        assert actual==preview;sizes.append(len(actual.encode('utf-8')))
    return commit,sizes
original,d0=prepare('NEGATIVO_ORIGINAL');tick0=[776919];commit0,sizes0=commit_factory(original,d0.home.parent,tick0)
negative=None
try:old.append_supply(original,d0,{'modo':old.MODE,'cantidad':4,'conexion':-1,'demora_periodos':2},commit0)
except ValueError as e:
    candidate=ns['encode_metadata'](original)
    negative={'error':str(e),'prospective_metadata_bytes_at_failure':len(candidate.encode('utf-8')),'native_limit':1048576,'native_ticks':0,'task_journal_lines_before_rejection':len(sizes0),'scope':'Official JSON + simulated Native1MiB guard, not a Native reproduction'}
else:raise AssertionError('Original full-source metadata should exceed frozen Native limit')
m,d=prepare('POSITIVO_COMPACTO');tick=[776919];commit,sizes=commit_factory(m,d.home.parent,tick)
history0=copy.deepcopy(m['resource_supply_history']);current0=copy.deepcopy(m['current_resource_source']);prefix_rows=copy.deepcopy(m['rows']);stages=[]
for stage,(connection,delay)in enumerate(((-1,2),(1,4),(-1,2),(1,4))):
    r=new.append_supply(m,d,{'modo':new.MODE,'cantidad':4,'conexion':connection,'demora_periodos':delay},commit)
    assert r['old_opportunity_unchanged']==26+4*stage and r['historical_prefix_preserved']and'source_ref'in r['supply']and'source'not in r['supply']
    for j in range(4):
        i=m['opportunity'];spec=m['schedule'][i];effect=tick_device(d,1,tick[0]+1,tick[0]+2,910000+i)
        tick[0]+=782
        m['rows'].append({'opportunity':i,'spec':spec,'reader_choice':1,'useful_product':not effect['failed'],'effect_sha256':effect['actual_product_sha256'],'after_tick':tick[0]})
        m['opportunity']+=1;m['products']=copy.deepcopy(d.m['products']);m['rejections']=copy.deepcopy(d.m['rejections'])
        # One compact task result row per simulated opportunity; no Native
        # field, clock, charge or acquired snapshot is modified in this test.
        commit({'kind':'SYNTHETIC_FIXED_PLUS_EXTERNAL_TEST_NOT_NATIVE','opportunity':i})
    stages.append({'stage':stage+1,'task_opportunity':m['opportunity'],'history_items':len(m['resource_supply_history']),'metadata_bytes':len(ns['encode_metadata'](m,max_bytes=1048576).encode('utf-8'))})
assert m['opportunity']==42 and len(m['schedule'])==42 and len(m['rows'])==42
assert m['resource_supply_history'][:6]==history0 and m['current_resource_source']==current0 and m['rows'][:26]==prefix_rows
new._validate_preserved_source_references(m,d)
archives=list((d.home/'FUENTES').glob('*.json'));assert len(archives)==1
assert sha(archives[0].read_bytes())==m['resource_supply_history'][-1]['source_ref']['source_sha256']
assert max(sizes)<=1048576
tamper=m['resource_supply_history'][-1]['source_ref']['source_sha256'];data=archives[0].read_bytes();archives[0].write_bytes(b'{}')
try:new._validate_preserved_source_references(m,d)
except ValueError:tamper_refused=True
else:raise AssertionError('Changed provenance source must refuse')
archives[0].write_bytes(data)
proof={'schema':'PI04.explicit_supply.compact_metadata.pure_test.R02','actual_DEE_imports':0,'new_native_ticks':0,'official_limit_bytes':1048576,
       'actual_last_closed_task_metadata_bytes':len(metadata.encode('utf-8')),'negative_original':negative,
       'positive_compact':{'four_supplies':4,'two_recorded_plus_sixteen_synthetic_external_uses':18,'end_task_consumed':42,'end_task_prepared':42,'max_preview_bytes':max(sizes),'headroom_at_max':1048576-max(sizes),'stages':stages,'old_six_history_items_literal':True,'old_rows_prefix_literal':True,'current_full_source_literal':True,'archive_files':len(archives),'archived_full_source_bytes':len(data),'tampered_archive_refused':tamper_refused},
       'mock_receipts_not_Native':True,'synthetic_fixed_plus_actions_not_E1_learning':True,
       'code':{f.name:{'bytes':f.stat().st_size,'sha256':sha(f.read_bytes())}for f in(HERE/'pi03_suministro_explicito_R03.py',HERE/'pi03_suministro_explicito_R03_ORIGINAL.py')},
       'scope':'Storage/codec/progress compatibility only, not a Native operational checkpoint or scientific replication. Original runtime/Python limits unchanged.'}
out=P/'control/E3_SUPPLY_COMPACTO_PRUEBA_PURA_R02.json'
if out.exists():raise FileExistsError('Previous proof protected')
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(proof,ensure_ascii=False,indent=2))
