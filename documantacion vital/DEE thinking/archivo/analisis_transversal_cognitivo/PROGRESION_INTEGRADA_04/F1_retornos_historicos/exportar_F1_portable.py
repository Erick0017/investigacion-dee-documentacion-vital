"""Export lossless sparse physical features from already frozen PI03 files."""
from pathlib import Path
import array,collections,gzip,hashlib,json,runpy,struct,sys
HERE=Path(__file__).resolve().parent;P4=HERE.parent;OUT=P4/'fuentes/observador_F1_portable'
def sha(b):return hashlib.sha256(b).hexdigest()
def info(p):
 b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':sha(b)}
def sparse(a,default):return {'default':str(default),'exceptions':[[i,str(v)]for i,v in enumerate(a)if v!=default]}
def buffers(item):
 p=Path(item['snapshot']['path']);e=p.read_bytes()
 if sha(e)!=item['snapshot']['sha256']:raise ValueError('Original snapshot changed')
 b=gzip.decompress(e);i=41;length=struct.unpack_from('<I',b,i)[0];i+=4+length;total=struct.unpack_from('<Q',b,i)[0];i+=8
 raw=array.array('Q');raw.frombytes(b[i:i+8*total]);clocks=array.array('Q');clocks.frombytes(b[i+8*total:i+16*total])
 if sha(b[i:i+8*total])!=item['physical']['RAW_sha256']or sha(b[i+8*total:i+16*total])!=item['physical']['clocks_sha256']:raise ValueError('Physical source witness changed')
 if sys.byteorder!='little':raw.byteswap();clocks.byteswap()
 default=collections.Counter(clocks).most_common(1)[0][0]
 return sparse(raw,0),sparse(clocks,default)
def trial(item,arm,phase,key):
 raw,clocks=buffers(item)
 return {'key':key,'phase':phase,'arm':arm,'tick':item['physical']['tick'],'opportunity':item['event']['opportunity'],
  'query_tick':item['event']['query_tick'],'query_read_tick':item['event']['query_read_tick'],'reported_original_choice':item['event']['choice'],
  'delay_laps':item['delay_laps'],'query_reader_RAW':[{'site':o['site'],'RAW':str(o['raw']),'clock':int(o['clock'])}for o in item['original_query_reader']['observations']],
  'RAW_sparse':raw,'clocks_sparse':clocks,'physical_witness':item['physical'],'snapshot_original':item['snapshot'],'primary_original':item['primary'],'original_F1_row_Y':item['actual_zero_Y']}
def main():
 source=HERE/'F1_RESULTADO.json';before={str(p):info(p)for p in(HERE/'F1_NOTAS.md',HERE/'F1_recalcular.py',source)}
 d=json.loads(source.read_text(encoding='utf-8'));cuts=[]
 for arm,items in d['R02'].items():
  for i,item in enumerate(items):cuts.append(trial(item,arm,'R02',f'R02/{arm}/{i}'))
 for i,item in enumerate(d['R04_existing_extension']):cuts.append(trial(item,'real','R04',f'R04/real/{i}'))
 witnesses=[]
 for c in d['R02_pair_comparisons']:
  for name,arm in(('real_vs_nonfailure','return_nonfailure'),('real_vs_actuator_null','actuator_null')):
   v=c[name];witnesses.append({'opportunity':c['opportunity'],'comparison':name,'a_key':f"R02/real/{c['opportunity']}",'b_key':f"R02/{arm}/{c['opportunity']}",**v})
 old=d['R05_frozen'];initial=old[0];failed=next(x for x in old if x['label']=='failed_query_T771955');current=d['adopted_PI03_T775355']
 dataset={'schema':'PI04.F1.portable_exact_physical_features.v1','N':67,'source_F1_result':info(source),'source_script':info(HERE/'F1_recalcular.py'),
  'cuts':cuts,'global_comparison_witnesses':witnesses,
  'R05':{'source_tick':initial['physical']['tick'],'source_Y':[o['site'][1]for o in initial['row_zero_Y_carriers']],
    'noquery_frames':[{'label':f['label'],'tick':f['tick'],'recorded_Y':f['recorded_Y']}for f in d['R05_noquery_translation']],
    'failed_query_reader_RAW':[{'site':o['site'],'RAW':o['RAW'],'clock':o['clock']}for o in failed['fixed_reader_at_cut']]},
  'current_protected_MAIN':{'snapshot_original':current['snapshot'],'physical_witness':current['physical'],'row_RAW':current['row_RAW'],'row_clocks':current['row_clocks'],'row_nonzero':current['row_nonzero'],'zero_Y_carriers':len(current['row_zero_Y_carriers']),'recent_choices':[x['reader_choice']for x in current['actual_recent_output_history_from_record_NOT_used_by_physical_reader']],'scope':'Selected row only here; full-global reconstruction covers the47 R02/R04 cuts. Protected anatomy prevents applying the unprotected observer.'},
  'limits':{'instrument_only':True,'Native_positive_use_of_history_not_demonstrated':True,'exploratory_R02':True,'R04_endpoint_previously_known':True,'R04_intermediate_cuts_not_used_to_derive_rule':True,'R02_original_reserves_not_reserves_for_this_new_reader':True,'calendar_scope':'Prepared settled query calendar,782 between opportunity cuts; not arbitrary timing transfer','no_trajectory_identity_claim':True,'current_MAIN_not_assigned_new_memory_capacity':True,'compressed_buffers_not_complete_operational_states':True}}
 (OUT/'DATOS_F1.json').write_text(json.dumps(dataset,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
 readme='''OBSERVADOR F1 PORTABLE — herramienta externa del investigador

Ejecutar dentro de esta carpeta extraída, con Python3.10+ estándar:
  python RECALCULAR_F1.py --output RESULTADO_NUEVO.json
El destino debe ser nuevo y estar dentro de esta misma carpeta. Sin --output se
imprime el resultado. No instala dependencias, importa DEE ni abre un mundo.

Recalcula47/47 cortes (42R02+5R04), reconstruye exactamente los300763 RAW y
clocks de cada corte a partir de representación dispersa SIN PÉRDIDA, verifica
sus hashes globales y recalcula28 diferencias globales (300763 sitios por par).
Los clocks uniformes se representan por valor predeterminado y excepciones;
no se supone que sean uniformes sin haber comparado los buffers originales.
También contrasta lectura material0 frente aNULL y nueve pasos toroidales.
Los hashes y localizadores de los snapshots/primarios originales se conservan
como procedencia; los archivos originales NO se necesitan ni se abren aquí.

Hallazgo: huella física de las últimas tres salidas0/+1 en una anatomía y un
calendario preparados. Es observación retrospectiva, no memoria semántica ni
recuperación nativa. Las reservas originales R02 no eran reservas de este
lector. El extremo R04 ya era conocido: no se afirma validación ciega nueva.
R05 probó interferencia, no un uso positivo de esa huella. La MAIN protegida
ya no mantiene ese soporte y no recibe esta capacidad por publicar el lector.

El manifiesto cubre datos, código, este texto y resultado contrastado, sin hash
autorreferencial. Resultado contrastado se calculó con los buffers exportados
y se comparó con los testigos previamente registrados en F1. No hay snapshots
Native restaurables: faltan interfaces, agenda, recibos, colas, transporte,
metadata y entorno completos. No puede usarse para reconstruir una vida.

INCORPORACIÓN PROPUESTA (Root al cierre, no ejecutada por este paquete):
Copiar esta carpeta sin alterar contenido a Cognitive/reproducibilidad/
herramientas/observador_F1_portable. Registrar ID
PI04_F1_OBSERVADOR_COLA_AUDITOR, clase instrumento_externo, modalidadA:
recálculo de registros; estado probado desde extracción. Asociar la entrada
del Manual y catálogo de herramientas al comando real de este archivo.
No crear otra vida, cambiar ACTIVO, añadir la huella como conocimiento del
principal ni hacer que listar/verificar ejecute consultas. Es una herramienta
externa propuesta para integración estable, sin aprendizaje atribuido aMAIN.
'''
 (OUT/'LEER_PRIMERO.txt').write_text(readme,encoding='utf-8')
 tool=runpy.run_path(str(OUT/'RECALCULAR_F1.py'),run_name='F1_portable_export_calculator')
 result=tool['calculate'](dataset)
 expected=d['summary']
 if result['checks']['R02_history_cuts_exact']!=expected['R02_observer_exact']or result['checks']['R04_existing_extension_cuts_exact']!=expected['R04_observer_exact']:raise ValueError('Portable observation counts differ from original F1')
 (OUT/'RESULTADO_CONTRASTADO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 names=('DATOS_F1.json','RECALCULAR_F1.py','LEER_PRIMERO.txt','RESULTADO_CONTRASTADO.json')
 manifest={'schema':'PI04.F1.portable_content_manifest.v1','members':{n:{'bytes':(OUT/n).stat().st_size,'sha256':sha((OUT/n).read_bytes())}for n in names},'original_F1_artifacts_preserved':before,'scope':'Exact physical features, no DEE or Native complete snapshots; original paths are provenance only.'}
 (OUT/'MANIFIESTO_SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 after={str(p):info(p)for p in(HERE/'F1_NOTAS.md',HERE/'F1_recalcular.py',source)}
 if before!=after:raise ValueError('Original F1 artifacts changed during export')
 size=sum(p.stat().st_size for p in OUT.iterdir()if p.is_file())
 if size>2000000:raise ValueError('Portable package exceeds2MB')
 print(json.dumps({'folder':str(OUT),'bytes':size,'files':len(list(OUT.iterdir())),'checks':result['checks'],'original_F1_unchanged':True,'new_Native_ticks':0},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
