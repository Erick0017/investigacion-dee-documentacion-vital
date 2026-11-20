"""Filesystem-only, exact mechanical correction of the P06 fingerprint guard."""
from pathlib import Path
import datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise ValueError(m)
def new(path,value):
    with path.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def run():
    old=ROOT/'native/benchmark_dependencias_P06_R05.py'
    need(sha(old)=='1fc48e710389017ea6ae20faa8deb89e8ba8642da8029ae1456843b216c0fa16','EXACT_R05_SOURCE')
    result_path=ROOT/'evidencia/P06_BENCHMARK_FULL_R01/RESULTADO_P06.json';result=json.loads(result_path.read_text('utf8'))
    card=result['basis']['recorded_physical'];actual=result['final_physical'];keys={'N','tick','RAW_sha256','clocks_sha256'}
    need(set(actual)==keys and all(card[k]==actual[k] for k in keys),'ONLY_SCHEMA_MISMATCH_ALLOWED')
    need(result['Native_ticks']==0 and result['critical_files_identical']and result['operational_files_identical']and result['no_operational_add_delete'],'SOURCE_RESULT_HAS_NO_PHYSICAL_OR_FILE_MUTATION')
    projection="""PHYSICAL_CORE=('N','tick','RAW_sha256','clocks_sha256')
PHYSICAL_CARD_EXTRA=('sites','occupied','max_s_reg','basic_buffers_bytes')
def physical_projection(value,*,recorded):
    required=set(PHYSICAL_CORE)|set(PHYSICAL_CARD_EXTRA)if recorded else set(PHYSICAL_CORE)
    ensure(type(value)is dict and set(value)==required,'Declared physical fingerprint schema')
    ensure(type(value['N'])is int and value['N']==67 and type(value['tick'])is int and value['tick']>=0,'Typed fixed N67 and tick')
    for key in('RAW_sha256','clocks_sha256'):
        ensure(type(value[key])is str and len(value[key])==64 and all(c in '0123456789abcdef'for c in value[key]),'Exact SHA256 fingerprint type')
    if recorded:
        ensure(all(type(value[k])is int and value[k]>=0 for k in PHYSICAL_CARD_EXTRA),'Typed derived card fields')
    return{k:value[k]for k in PHYSICAL_CORE}

"""
    text=old.read_text('utf8')
    replacements=[("PROTOCOL=ROOT/'protocolo/PROTOCOLO_P06_DEPENDENCIAS_R05.json'","PROTOCOL=ROOT/'protocolo/PROTOCOLO_P06_DEPENDENCIAS_R06.json'"),
      ('def preflight(dest):',projection+'def preflight(dest):'),
      ("'recorded_physical':card['physical'],'critical':", "'recorded_physical':card['physical'],'recorded_physical_projection':physical_projection(card['physical'],recorded=True),'critical':"),
      ("ensure(before==basis['recorded_physical'],'Opened RAW/clocks differ from stored closed record')", "ensure(physical_projection(before,recorded=False)==basis['recorded_physical_projection'],'Opened RAW/clocks differ from stored closed record')"),
      ("'DEE.R07.P06.FullDependenciesBenchmark.R05'","'DEE.R07.P06.FullDependenciesBenchmark.R06'")]
    for source,target in replacements:
        need(text.count(source)==1,'ONE_DECLARED_MECHANICAL_ANCHOR: '+source)
        text=text.replace(source,target)
    target=ROOT/'native/benchmark_dependencias_P06_R06.py'
    with target.open('x',encoding='utf8',newline='\n')as f:f.write(text)
    source_protocol=ROOT/'protocolo/PROTOCOLO_P06_DEPENDENCIAS_R05.json';protocol=json.loads(source_protocol.read_text('utf-8-sig'))
    protocol['technical_revision']='R06: compare official four-field fingerprint against exact typed projection of eight-field VIDA physical record. No change to passes, criteria, instrumentation or policy.'
    protocol['previous_protocol_sha256']=sha(source_protocol)
    new(ROOT/'protocolo/PROTOCOLO_P06_DEPENDENCIAS_R06.json',protocol)
    proof={'schema':'DEE.R07.P06.PhysicalSchemaCorrection.R06','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'source_result':str(result_path),'source_result_sha256':sha(result_path),'recorded_exact_eight_fields':card,'observed_exact_four_fields':actual,
      'mandatory_keys_equal':all(card[k]==actual[k]for k in keys),'SHA_utf8_bytes_equal':all(card[k].encode()==actual[k].encode()for k in('RAW_sha256','clocks_sha256')),
      'record_only_derived_keys':sorted(set(card)-keys),'Native_ticks':0,'critical_files_identical':True,'operational_files_identical':True,
      'original_source_preserved_sha256':sha(old),'corrected_source':str(target),'corrected_source_sha256':sha(target),
      'same_three_passes_and_twenty_percent_criterion':True,'Native_or_MCP_calls_by_preparation':0}
    new(ROOT/'control/PRUEBA_ESQUEMA_P06_R06.json',proof)
    print(json.dumps({k:proof[k]for k in('corrected_source','corrected_source_sha256','mandatory_keys_equal','Native_ticks')},indent=2))
if __name__=='__main__':run()
