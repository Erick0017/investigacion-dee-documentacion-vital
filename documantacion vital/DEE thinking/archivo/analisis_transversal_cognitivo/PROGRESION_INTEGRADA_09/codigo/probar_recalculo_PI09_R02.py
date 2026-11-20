"""Synthetic PI09-format fixture derived from closed PI08 bytes, NOT PI09 Native.
Exercises the portable verifier's RAW/receipt/product path without a runtime.
"""
from pathlib import Path
import copy,importlib.util,json,shutil,subprocess,sys
H=Path(__file__).resolve().parent;P=H.parent;OLD=P.parent/'PROGRESION_INTEGRADA_08/control/C_PORTABLE_FINAL_R01';D=P/'control/PRUEBA_RECALCULO_MOCK_PI09_R02';D.mkdir(exist_ok=False)
spec=importlib.util.spec_from_file_location('recalc_pi09_fixture',H/'RECALCULAR_CONSULTA_PI09_R01.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);FIXTURE_VERSION='DEE.PI09.selective_registered_consultation.R02'
def write(name,obj,**extra):
    file=D/name;file.parent.mkdir(parents=True,exist_ok=True);data=(json.dumps(obj,ensure_ascii=False,sort_keys=True)+'\n').encode();file.write_bytes(data);return {'file':name,'bytes':len(data),'sha256':r.sha(data),**extra}
def member(source,name,**extra):
    file=D/name;file.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,file);return {'file':name,'bytes':file.stat().st_size,'sha256':r.sha(file.read_bytes()),**extra}
oldindex=json.loads((OLD/'INDICE_C_PI08_R03.json').read_bytes());protocol=json.loads((H/'PROTOCOLO_PI09_CONSULTA_R01.json').read_bytes());oldp=json.loads((OLD/'PROTOCOLO_PI08_C_R02.json').read_bytes())
for i in range(6):protocol['schedule'][i]={**oldp['schedule'][i],'stage':'development','wait_ticks':0}
index={'schema':'DEE.PI09.consultation.portable_primary_index.R01','fixture_MOCK_ONLY_NOT_NATIVE':True,'protocol':write('PROTOCOL_MOCK.json',protocol),'primaries':[],'witnesses':[],'products':[]}
witnesses={json.loads((OLD/v['file']).read_bytes())['ordinal']:json.loads((OLD/v['file']).read_bytes())for v in oldindex['immediate_witnesses']}
for item in oldindex['episode_primaries']:
    primary=json.loads((OLD/item['file']).read_bytes());row=r.rows(primary)[0];i=row['ordinal'];first=row['first_stage'];reg=first['sample_register'];second=row['second_stage'];row['version']=second['version']=FIXTURE_VERSION;second['environment_spec']=protocol['schedule'][i]
    first['actual_query_motor']=first['native_motor'];first['query_control']='native';first['operator_reference_not_candidate_policy']=False
    reg['release_source']={'kind':'current_actual_registered_RAW','observation':reg['actual_preview_observation'],'observation_sha256':r.sha(r.canon(reg['actual_preview_observation']))}if reg['question_applied_and_signature']else None
    row['query_control']='native';row['information_control']='real';row['extra_bit_source']=reg['release_source'];row['prepared_wait_ticks']=0;row['before_prepared_wait']=row['before_tick'];row['whole_new_native_ticks']=row['new_native_ticks']
    w=witnesses[i];w['actual_query_motor']=w['native_motor'];w['query_control']='native';wi=write('TESTIGOS/'+str(i)+'.json',w,arm='native_real');index['witnesses'].append(wi)
    row['external_immediate_first_stage_witness']={**row['external_immediate_first_stage_witness'],'bytes':wi['bytes'],'sha256':wi['sha256']}
    pp={'status':'completed','result':json.dumps({'result':{'rows':[row]}}),'fixture_MOCK_ONLY_NOT_NATIVE':True};index['primaries'].append(write('PRIMARIOS/'+str(i)+'.json',pp,arm='native_real'))
for v in oldindex['products']:index['products'].append(member(OLD/v['file'],v['file']))
write('INDICE_PI09_CONSULTA_R01.json',index)
for name in('RECALCULAR_CONSULTA_PI09_R01.py','RECALCULAR_C_PI08_LITERAL.py','RECALCULAR_PRIMARIOS_PI07_LITERAL.py'):member(H/name,name)
out=D/'RESULTADO_MOCK.json';proc=subprocess.run([sys.executable,'-I','-B',str(D/'RECALCULAR_CONSULTA_PI09_R01.py'),'--raiz',str(D),'--salida',str(out)],capture_output=True,text=True)
(D/'stdout.txt').write_text(proc.stdout,encoding='utf8');(D/'stderr.txt').write_text(proc.stderr,encoding='utf8')
if proc.returncode:raise RuntimeError(proc.stderr)
value=json.loads(out.read_bytes());assert value['integrity_passed']and value['fixture_MOCK_ONLY_NOT_NATIVE']and value['completed_opportunities']==6 and value['groups'][0]['useful']==5 and value['groups'][0]['version']==FIXTURE_VERSION
proof={'schema':'DEE.PI09.consultation.portable_recalculation.synthetic_test.R01','passed':True,'Native_executed':False,'DEE_imported':False,'fixture_MOCK_ONLY_NOT_NATIVE':True,'not_PI09_material_evidence':True,'recalculation_sha256':r.sha(out.read_bytes()),'checks':'6 synthetic-format rows preserve PI08 RAW, direct receipts, 64B actual products;5useful only from the earlier PI08 fixture','CLI_exit':proc.returncode}
file=P/'control/PRUEBAS_RECALCULO_MOCK_PI09_R02.json';file.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf8');print(json.dumps(proof))
