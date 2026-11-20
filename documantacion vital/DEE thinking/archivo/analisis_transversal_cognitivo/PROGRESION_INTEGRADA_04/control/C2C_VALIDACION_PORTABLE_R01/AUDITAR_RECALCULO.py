from pathlib import Path
import json,runpy,sys
root=Path('D:\\GENESIS AI\\GENESIS 5.0\\simulador de universo ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion vital\\DEE thinking\\archivo\\analisis_transversal_cognitivo\\PROGRESION_INTEGRADA_04\\control\\C2C_VALIDACION_PORTABLE_R01\\EXTRACCION_LIMPIA').resolve(); output=Path('D:\\GENESIS AI\\GENESIS 5.0\\simulador de universo ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion vital\\DEE thinking\\archivo\\analisis_transversal_cognitivo\\PROGRESION_INTEGRADA_04\\control\\C2C_VALIDACION_PORTABLE_R01\\RECALCULO');audit=Path('D:\\GENESIS AI\\GENESIS 5.0\\simulador de universo ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion vital\\DEE thinking\\archivo\\analisis_transversal_cognitivo\\PROGRESION_INTEGRADA_04\\control\\C2C_VALIDACION_PORTABLE_R01\\AUDIT_RECALCULO.json');base=Path(sys.base_prefix).resolve(); evidence_root=Path('D:\\GENESIS AI\\GENESIS 5.0\\simulador de universo ab-initio\\dee_libreria\\VERSION_27\\tests\\documantacion vital\\DEE thinking\\archivo\\analisis_transversal_cognitivo\\PROGRESION_INTEGRADA_04').resolve()
opened=[];blocked=[];forbidden_imports=[]
def hook(event,args):
 if event=='import'and str(args[0]).split('.')[0]in('dee','dee_thinking','app','capacidades'):
  forbidden_imports.append(str(args[0]));raise PermissionError('DEE/app import forbidden in documentary recalculation')
 if event=='open'and args and isinstance(args[0],str):
  path=Path(args[0]).resolve()
  if path.is_relative_to(evidence_root)and not path.is_relative_to(root)and not path.is_relative_to(audit.parent):
   blocked.append(str(path));raise PermissionError('Original campaign source access forbidden')
  if path.is_relative_to(root):opened.append(str(path.relative_to(root)))
sys.addaudithook(hook)
try:
 sys.argv=[str(root/'RECALCULAR_C2C_R01.py'),'recalculate','--evidence',str(root),'--out',str(output)]
 runpy.run_path(str(root/'RECALCULAR_C2C_R01.py'),run_name='__main__')
finally:
 audit.write_text(json.dumps({'original_project_file_attempts':blocked,'DEE_app_imports':forbidden_imports,'extracted_member_opens':opened,'Native_ticks':0},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
