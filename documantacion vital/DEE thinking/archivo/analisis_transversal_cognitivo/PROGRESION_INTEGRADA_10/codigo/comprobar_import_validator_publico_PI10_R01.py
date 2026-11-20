from pathlib import Path
import importlib.util,json,sys,traceback,hashlib
C=Path(__file__).resolve().parents[4]/'DEE Cognitive 2.0';S=C/'sistema';app=S/'app'
sys.path.insert(0,str(app))
spec=importlib.util.spec_from_file_location('PI10_pure_queue_validator',app/'cola_local.py')
q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
literal={'operacion':'sesion','situaciones':[{'modo':'eci01-pi10-episodio'}],'actuador':'closed','retorno':'omit'}
result={'schema':'DEE.PI10.pure_public_client_import_diagnosis.R01','input':literal,'QueueDB_instantiations':0,'SQLite_opens':0,'Native_calls':0,'original_sys_path_local':[str(app)]}
try:
 q.validate_request(literal);result['before']={'unexpected_success':True}
except Exception as e:result['before']={'type':type(e).__name__,'detail':str(e),'traceback':traceback.format_exc()}
sys.path.insert(1,str(S))
try:q.validate_request(literal);result['after']={'validator_succeeded':True}
except Exception as e:result['after']={'type':type(e).__name__,'detail':str(e),'traceback':traceback.format_exc()}
result['Native_module_names']=[n for n in sys.modules if 'dee_thinking' in n.lower() or n.startswith('dee_universe')]
out=Path(__file__).resolve().parent.parent/'control/DIAGNOSTICO_IMPORT_PUBLICO_PI10_R01.json'
assert not out.exists(),'No overwrite'
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2));print('OUTPUT',str(out));print('SHA256',hashlib.sha256(out.read_bytes()).hexdigest())

