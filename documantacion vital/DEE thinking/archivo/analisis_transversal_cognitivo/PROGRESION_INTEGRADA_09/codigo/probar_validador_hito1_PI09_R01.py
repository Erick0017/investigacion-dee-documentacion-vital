"""Pure synthetic decoder/type tests, not repeated material panel evidence."""
from pathlib import Path
import hashlib,importlib.util,json
H=Path(__file__).resolve().parent;OUT=H/'PRUEBA_VALIDADOR_HITO1_PI09_R01'
def main():
 if OUT.exists():raise FileExistsError('Prueba anterior preservada')
 OUT.mkdir();sp=importlib.util.spec_from_file_location('PI09_panel_pure_validation',H/'validar_paneles_hito1_PI09_R01.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);reader,source=m.frozen_numeric();tests=[]
 def check(n,v):
  if v is not True:raise AssertionError(n)
  tests.append({'name':n,'pass':True})
 def observation(state,payload,direction=(1,-1,-1),semantic=1):
  raw=state|(payload<<32)|(semantic<<60)
  for d,shift in zip(direction,(48,52,56)):raw|=(d&15)<<shift
  return {'raw':str(raw),'clock':'123','tick':123,'state':state,'s_reg':payload,'semantic':semantic,'direction':list(direction),'site':[12,17,18]}
 def decode(o,op):return reader({'kind':'native_joint_raw_perception','level':128,'datum_tick':125,'frames':[{'tick':123,'fields':{'C':o}}]},op)
 x=observation(1,0);m.RAW(x);check('formed_SUM_zero_is_int0',decode(x,'suma')['numeric_result']==0 and type(decode(x,'suma')['numeric_result'])is int)
 x=observation(1,32);m.RAW(x);check('formed_DIF_zero_is_int0',decode(x,'diferencia')['numeric_result']==0 and type(decode(x,'diferencia')['numeric_result'])is int)
 x=observation(0,0,semantic=4);m.RAW(x);check('SEM4_state0_is_not_numeric0',decode(x,'suma')['numeric_result']is None)
 x=observation(1,7);check('RAW_actual7_is_not_expected13',decode(x,'suma')['numeric_result']==7)
 x=observation(1,34);check('bias32_preserved_DIF2',decode(x,'diferencia')['numeric_result']==2)
 x=observation(1,7);x['state']=True
 try:m.RAW(x)
 except ValueError:check('bool_is_not_physical_integer',True)
 else:raise AssertionError('bool accepted')
 result={'schema':'DEE.PI09.hito1.pure_validator_decoder_tests.R01','passed':len(tests),'tests':tests,'fixture_MOCK_ONLY_NOT_NATIVE':True,'Native_executed':False,'DEE_imports':0,'actual_frozen_numeric_reader_extracted_AST':source,'no_material_panel_repeated':True}
 file=OUT/'RESULTADO.json';file.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'passed':len(tests),'proof':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'Native_executed':False}))
if __name__=='__main__':main()
