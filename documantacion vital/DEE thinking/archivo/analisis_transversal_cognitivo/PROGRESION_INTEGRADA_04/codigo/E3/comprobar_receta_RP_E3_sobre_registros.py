"""Map prepared generic recipe to original closed Native records, no replay.

Verifies JSON paths, literal/supply order, receipt denominators and every
post-run criterion using the already exported original records. This is not
an execution of the material RP CLI and never imports the engine.
"""
from pathlib import Path
import gzip,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[2];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
root=RP/'evidencia/PI04_E3_R02/datos';recipe_file=RP/'recetas/pi04_e3_contingencia_R02.json';r=json.loads(recipe_file.read_text(encoding='utf-8'))
def sha(b):return hashlib.sha256(b).hexdigest()
def read(name):
    b=(root/name).read_bytes();return json.loads(gzip.decompress(b)if b[:2]==b'\x1f\x8b'else b)
def value(o):
    assert o['status']=='completed';return json.loads(o['result'])if type(o['result'])is str else o['result']
def path(v,parts):
    for p in parts:v=v[p]
    return v
mapped=[]
for arm,variant in r['variants'].items():
    records={'admit':value(read(arm+'/admit.json.gz')),'final_state':value(read(arm+'/final.json.gz'))}
    for i in range(18):records['opportunity_%02d'%i]=value(read(arm+'/primaries/%02d.json.gz'%i))
    for i in(2,6,10,14):records['supply_%02d'%i]=value(read(arm+'/supplies/%02d.json.gz'%i))
    assert len(variant['batches'])==1 and len(variant['batches'][0])==24
    expected_labels=['admit']
    for i in range(18):
        if i in(2,6,10,14):expected_labels.append('supply_%02d'%i)
        expected_labels.append('opportunity_%02d'%i)
    expected_labels.append('final_state');assert [s['label']for s in variant['batches'][0]]==expected_labels
    receipts={};decoded=[]
    for step in variant['batches'][0]:
        assert step['feedback']=='omit'and'expected'not in step['literal']
        v=records[step['label']]
        if step.get('require_zero_ticks'):assert v['before_tick']==v['after_tick']
        if 'read_path'in step:
            got=path(v,step['read_path']);assert got is not None and type(got)is int and step['stop_on_NULL'];decoded.append(got)
        for parts in step.get('receipt_paths',[]):
            for item in path(v,parts):
                rr=item['receipt'];assert rr['id']==item['id']and rr['status']=='applied'
                assert rr['id']not in receipts;receipts[rr['id']]=rr
    criteria=[]
    for check in variant['final_checks']:
        vals=[path(records[x['step']],x['path'])for x in check['values']]
        observed=sum(v is True for v in vals)if check['operation']=='sum_true'else vals[0]
        assert observed==check['expected']and type(observed)is type(check['expected']),check['label']
        criteria.append({'label':check['label'],'observed_from_original_batch':observed,'expected_recipe':check['expected'],'coincides':True})
    assert len(receipts)==variant['native_receipt_expectations']['unique_requested']==90
    mapped.append({'variant':arm,'steps':24,'decoded_responses':len(decoded),'unique_applied_Native_inputs_in_original_records':len(receipts),'criteria_on_original_recorded_batch':criteria})
proof={'schema':'PI04.E3.prepared_RP_recipe.mapped_to_closed_records.v1','modality':'DOCUMENTARY_VALIDATION_OF_RECIPE_PATHS_NOT_NATIVE_CLI_REPLAY','recipe':'pi04_e3_contingencia_R02','recipe_sha256':sha(recipe_file.read_bytes()),'variants':mapped,
       'new_native_ticks':0,'actual_DEE_imports':0,'Native_RP_CLI_executed':False,'original_Root_Native_batches_executed':True,
       'scope':'Correct paths/criteria and source protocol mapping do not certify the newly prepared generic RP recipe has itself run Native. Requirements verification and material execution are separate.'}
out=P/'control/E3_RECETA_RP_MAPEADA_A_PRIMARIOS_R02.json'
if out.exists():raise FileExistsError('Prior proof preserved')
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
dest=RP/'verificaciones/pi04_e3_contingencia_R02/E3_MAPEO_DOCUMENTAL_R02.json';dest.parent.mkdir(parents=True,exist_ok=True)
if dest.exists():raise FileExistsError('Prior RP documentary verification preserved')
dest.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'variants_mapped':len(mapped),'steps_each':24,'unique_original_inputs_each':90,'new_native_ticks':0,'RP_material_CLI_executed':False,'verification':str(dest)},ensure_ascii=False))
