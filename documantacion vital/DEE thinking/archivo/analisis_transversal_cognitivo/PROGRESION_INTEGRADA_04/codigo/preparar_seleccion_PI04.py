"""Prepare a small PI04 analysis selection, never writes ZIP or original files.
Re-run with a new --out after literal1.31 publication and final evidence closure.
Pending entries are explicit and must not be silently replaced by old artifacts.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,io,zipfile
P=Path(__file__).resolve().parents[1];R=P.parents[2];C=R/'DEE Cognitive 2.0'
def main(a):
 entries=[];pending=[];targets=set()
 def add(p,t,reason):
  p=Path(p)
  if not p.exists():pending.append({'source':str(p.resolve()),'target':t,'reason':reason});return
  if t in targets:raise ValueError('Duplicate target '+t)
  b=p.read_bytes();targets.add(t);entries.append({'source':str(p.resolve()),'file':t,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'reason':reason})
 def tree(p,t,reason):
  for f in sorted(Path(p).rglob('*')):
   if f.is_file()and'__pycache__'not in f.parts:add(f,t+'/'+f.relative_to(p).as_posix(),reason)
 add(P/'entrega/00_LEER_PRIMERO.txt','00_LEER_PRIMERO.txt','Actual Root closure, not a new generic summary')
 add(P/'INFORME_CIENTIFICO_PI04.md','01_INFORME_CIENTIFICO.md','One scientific report with positives and negatives')
 man=C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
 with zipfile.ZipFile(man)as z:edition=z.read('docProps/core.xml').decode('utf8')
 if '>1.31<'in edition:add(man,'02_MANUAL/'+man.name,'Full literal current Manual, not a derived summary')
 else:pending.append({'source':str(man.resolve()),'target':'02_MANUAL/'+man.name,'reason':'Current1.30must not be passed off as updated1.31; wait for publication'})
 add(R/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx','02_MANUAL/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx','Complete current compact compendium')
 tree(P/'mapas','03_MAPAS','Directed coverage/capabilities/genealogy, no old massive inventory')
 for src,dst in [(P/'fuentes/observador_F1_portable','F1'),(P/'ensayos/EVIDENCIA_E3_PORTABLE','E3'),(P/'ensayos/EVIDENCIA_C2C_TRES_HISTORIAS20_PORTABLE_R01','C2C')]:tree(src,'04_EVIDENCIAS/'+dst,'Self-contained decisive pure recalculation and actual Native primaries')
 closure=['DECISION_NO_ADOPCION_PI04.json','CONSERVACION_REGRESION_PI04_VERIFICADA.json','C2C_COLD20_NATIVE_VERIFICADA_R01.json','CIERRE_CIENTIFICO_PI04.json']
 for n in closure:add(P/'control'/n,'04_EVIDENCIAS/CIERRE/'+n,'Actual no-adoption/closed science gate required by unified verifier')
 explicit=['REGRESION_FIPLUS_REPLICA_CERRADA_R01.json','TICKS_NATIVE_CERRADOS_FINAL_PI04.json','PI04_REGRESION_RET2_R01.json','CONSERVACION_MAIN_PARCIAL_FIPLUS_R01.json','PI04_C2C_POSTPANEL_DIAG_CRUCE22_R01.json','C2C_RET2_CTX2_RECALCULADOS_PASIVO_R01.json','PI04_C2C_REAL_RET2_R01.json','PI04_C2C_CTX_CUT4_OP2_R02.json','PI04_C2C_LINK_CUT1_OP3_R01.json','C2C_CTX1_FALLO_INFRAESTRUCTURA_R01.json','C2_DESARROLLO_ADVERSO_R02.json','C2_DENOMINADORES_PRIMARIOS_RECALCULADOS_PASIVO.json','C2B_DEV_STOP_AUTOPSIA_PASIVA_R01.json','C2B_DENOMINADORES_PRIMARIOS_R01.json','C2C_TRAZA_NUMERICA_FISICA_Y_CODEC_R01.json','DGC_ANALISIS_Y_PASIVIDAD_R01.json','E3_FUTURO_ADVERSO_R01_PRESERVADO.json','E3_FALLO_SUPPLY_R01.json','E3_CONTRASTE_FISICO_FINAL_PASIVO.json','C2C_TRES_HISTORIAS20_CONTRASTE_DOCUMENTAL_R01.json','INCORPORACION_MECANISMOS_PRODUCTO_PI04_JSON_R02.json','INCORPORACION_MECANISMOS_PI04_VERIFICACION_ESTATICA_Y_GUIA.json','AJUSTE_ESTIMACION_ALMACENAMIENTO_LOCAL.json','EXPORTACION_ESTABLE_PI03_PI04_C2C_CONSERVACION_FALLIDA_T818074.json','REGRESION_FIPLUS_PROTOCOLO_PRE_REPLICA_R01.json']
 for n in explicit:add(P/'control'/n,'04_EVIDENCIAS/CONTROL/'+n,'Decisive result/control/adverse or continuity/incorporation proof')
 for pat in ['PI04_REGRESION_PANEL6_R01_*.json','PI04_REGRESION_RET2_R01_OP_*.json','PI04_MAIN_PANEL12_OP2_*.json','PI04_C2_REAL_DEV_R02_OP_*.json','PI04_C2B_REAL_DEV_R01_OP_*.json','PI04_C2C_CTX_CUT4_R01_OP_12.json','PI04_C2C_REAL_RET2_R01_OP_*.json','PI04_C2C_CTX_CUT4_OP2_R02_OP_*.json','PI04_C2C_LINK_CUT1_OP3_R01_OP_*.json','PI04_C2C_POSTPANEL_DIAG_CRUCE22_R01_OP_*.json']:
  for f in sorted((P/'ensayos').glob(pat)):add(f,'04_EVIDENCIAS/PRIMARIOS/'+f.name,'Material Native primary; panel/adverse/retention or dependence beyond the main portable20')
 add(P/'codigo/RECALCULAR_EXPEDIENTE_PI04.py','05_RECALCULO/RECALCULAR_EXPEDIENTE_PI04.py','Unified stdlib clean extraction verifier; Native0')
 # Relevant scientific module directories; preserve exact historical bytes.
 for d in ['E3','E3_R02','PI04_C2C_SCAFFOLD_OP2']:
  if(P/'codigo'/d).is_dir():tree(P/'codigo'/d,'06_CODIGO/'+d,'Exact experiment/protocol or localized technical revision')
 for f in sorted((P/'codigo').glob('*.py')):
  if f.name.startswith(('pi04_','ejecutar_C2','RECALCULAR_C2','verificar_regresion','finalizar_hechos_PI04_sin_adopcion','publicar_documentos_PI04_literal','actualizar_manual_PI04')):add(f,'06_CODIGO/'+f.name,'Scientific execution, passive recalc or documentary delta; not executed on extraction')
 add(C/'sistema/contratos/PI04_OBSERVACION_Y_REPRODUCCION_01.json','06_CODIGO/PI04_OBSERVACION_Y_REPRODUCCION_01.json','Actual product incorporation contract')
 omissions=[{'source':str((P/'estados').resolve()),'reason':'Complete coherent physical/operational states stay local; never call this small analysis package a restorable backup','minimal_next':'Stable full pair named in actual continuity and preservation proofs'},{'source':str((C/'reproducibilidad/materiales').resolve()),'reason':'Shared large preserved prefix/final full pairs; local locators/manifests in closure','minimal_next':'Exact named full pair, no RAW/clocks-only reconstruction'},{'source':str((R/'4.5').resolve()),'reason':'Two official Thinking manuals and official engine stay local, frozen; not copied wholesale','minimal_next':'Directed technical sections when needed'},{'source':str((P/'ensayos/EVIDENCIA_C2C_REAL20_PORTABLE_R01').resolve()),'reason':'Older export superseded in this package by complete three-history20 export; originals untouched'},{'source':str((P/'ensayos/EVIDENCIA_C2C_REAL_NONE20_PORTABLE_R01').resolve()),'reason':'Redundant older two-history export; three histories included'},{'source':str((P/'control/C2C_CTX1_DESGLOSE_POR_PREFIJO_SUPERADO.json').resolve()),'reason':'Superseded prefix denominator; canonical actualCtx1failure included with184inputs724ticks'}]
 result={'schema':'DEE.PI04.analysis_selection.preliminary.v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'NOT_A_SEALED_PACKAGE':True,'content':entries,'pending_required':pending,'omissions':omissions,'content_bytes':sum(x['bytes']for x in entries),'Native_ticks':0,'originals_modified':False}
 # Exact Deflate size estimate of the chosen currently available bytes, no disk ZIP.
 stream=io.BytesIO()
 with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for x in entries:z.writestr(x['file'],Path(x['source']).read_bytes())
 result['current_Deflate_estimate_bytes']=len(stream.getvalue());need=Path(a.out);need.parent.mkdir(exist_ok=True,parents=True)
 if need.exists():raise ValueError('Selection output exists, use a new filename')
 need.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'output':str(need),'files':len(entries),'bytes':result['content_bytes'],'Deflate_estimate':result['current_Deflate_estimate_bytes'],'pending':[x['target']for x in pending]},ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=P/'entrega/SELECCION_PRELIMINAR_PI04.json');main(p.parse_args())
