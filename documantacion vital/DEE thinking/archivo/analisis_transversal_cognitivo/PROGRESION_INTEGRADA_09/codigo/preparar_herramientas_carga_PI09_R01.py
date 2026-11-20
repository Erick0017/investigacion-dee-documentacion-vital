"""Versioned Root adoption/reopen tools consuming only exact admin supplement."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def once(t,a,b):
 if t.count(a)!=1:raise ValueError('Exact anchor changed '+a[:80])
 return t.replace(a,b)
def main():
 source=H/'incorporar_PI09_misma_identidad_R03.py';target=H/'incorporar_PI09_misma_identidad_R04.py';text=source.read_text('utf-8-sig')
 before=" for row in prepared['deployed_code']:\n  if sha(S/row['file'])!=row['sha256']:raise ValueError('Deployed source changed after preparation')"
 after=""" # Original preparation/decision stay immutable. Only the independently
 # reviewed two-file PREPARED-load administrative supplement may supersede
 # the corresponding source hash, with its original beforeimage proved.
 supplement_file=CONTROL/'CARGA_PREPARADA_PI09_APLICADA_R01.json';supplement=read(supplement_file)
 if supplement.get('schema')!='DEE.PI09.prepared_load.administrative_supplement.applied.R01'or supplement.get('applied')is not True or supplement.get('critical_state_before_after_equal')is not True or supplement.get('Native_executed')is not False or supplement['preparation']['sha256']!=sha(PREPARED)or supplement['decision']['sha256']!=sha(file):raise ValueError('Exact closed administrative source supplement required')
 proposed=read(H/'CARGA_PREPARADA_PI09_R01_PROPUESTA/PLAN.json')
 if supplement['files']!=proposed['files']:raise ValueError('Administrative supplement differs from reviewed plan')
 patches={r['file']:r for r in supplement['files']}
 if set(patches)!={'capacidades/pi09_permiso_operativo_R01.py','capacidades/pi09_carga_preparada_R01.py'}:raise ValueError('Only the exact two administrative sources may change')
 for row in prepared['deployed_code']:
  patch=patches.get(row['file'])
  if patch and patch['before_sha256']!=row['sha256']:raise ValueError('Administrative source beforeimage differs')
  if sha(S/row['file'])!=(patch['sha256']if patch else row['sha256']):raise ValueError('Deployed source changed outside the reviewed supplement')
 for row in supplement['files']:
  if sha(S/row['file'])!=row['sha256']or sha(Path(row['source']))!=row['sha256']:raise ValueError('Supplement source changed')
 if patches['capacidades/pi09_carga_preparada_R01.py']['before_sha256']is not None:raise ValueError('New administrative helper unexpectedly replaces a prior body')"""
 text=once(text,before,after)
 text=once(text,"'source_history_not_rewritten':True,'old_principal_preserved'","'source_history_not_rewritten':True,'administrative_source_supplement':info(supplement_file),'old_principal_preserved'")
 if target.exists():raise FileExistsError('Preserve current revision')
 ast.parse(text);target.write_text(text,'utf8');rows=[{'file':target.name,'source_sha256':sha(source),'sha256':sha(target)}]
 source=H/'ejecutar_administracion_con_tope_PI09_R03.py';target=H/'ejecutar_administracion_con_tope_PI09_R04.py';text=source.read_text('utf-8-sig').replace('incorporar_PI09_misma_identidad_R03.py','incorporar_PI09_misma_identidad_R04.py')
 if target.exists():raise FileExistsError('Preserve admin revision')
 ast.parse(text);target.write_text(text,'utf8');rows.append({'file':target.name,'source_sha256':sha(source),'sha256':sha(target)})
 source=H/'reabrir_producto_PI09_0_R02.py';target=H/'reabrir_producto_PI09_0_R03.py';text=source.read_text('utf-8-sig').replace('PI09_PRODUCT0_SELECTED_R02','PI09_PRODUCT0_SELECTED_R03').replace('PI09_PRODUCT0_UNSELECTED_R02','PI09_PRODUCT0_UNSELECTED_R03')
 if target.exists():raise FileExistsError('Preserve failed reopen source')
 ast.parse(text);target.write_text(text,'utf8');rows.append({'file':target.name,'source_sha256':sha(source),'sha256':sha(target)})
 proof={'schema':'DEE.PI09.prepared_load.Root_tools_prepared.R01','Native_executed':False,'original_failed_reopening_R02_preserved':True,'original_preparation_and_decision_preserved':True,'files':rows}
 (H/'HERRAMIENTAS_CARGA_PREPARADA_PI09_R01.json').write_text(json.dumps(proof,indent=2)+'\n','utf8');print(json.dumps(proof))
if __name__=='__main__':main()
