"""Closed DG findings and bounded ROI-observer comparison; no Native."""
from pathlib import Path
import datetime,hashlib,json,runpy
P4=Path(__file__).resolve().parents[1];S2=P4/'estados/candidato_R02/sistema'
def sha(b):return hashlib.sha256(b).hexdigest()
def info(p):
 b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':sha(b)}
def primary(p):
 d=json.loads(p.read_text(encoding='utf-8'))
 return json.loads(d['result'])if isinstance(d.get('result'),str)else d
def frame_values(journal):
 events=[json.loads(line)for line in Path(journal).read_bytes().splitlines()]
 if events[-1]['kind']!='DG_COMPLETED':raise ValueError('Only completed DG journals')
 return {e['frame']['relative_to_query']:e['frame']for e in events if e['kind']=='DG_PASSIVE_FRAME'}
def cell(f,site):
 hit=next(o for o in f['observations']if o['site']==site)
 return {k:hit[k]for k in('site','raw','clock','state','s_reg','semantic','direction')}
def main():
 out=P4/'control/DG_ANALISIS_Y_PASIVIDAD_R01.json'
 if out.exists():raise FileExistsError('Prior closed proof protected')
 parser=runpy.run_path(str(P4/'codigo/contrastar_finales_E3_pasivo.py'),run_name='pure_frozen_DG_parser')['parse']
 names={'single_full':'SINGLE_FULL01','single_compact':'SINGLE_COMPACT01','symmetric_full':'SYM_FULL01'};sources={};results={};analyses={}
 analysis_names={'single_full':'DG_SINGLE_FULL_CAMPO_PASIVO_R01.json','single_compact':'DG_SINGLE_COMPACT_CAMPO_PASIVO_R01.json','symmetric_full':'DG_SYM_FULL_CAMPO_PASIVO_R01.json'}
 for key,name in names.items():
  path=P4/f'ensayos/PI04_DG_{name}.json';d=primary(path);r=d['result']['rows'][0]
  if r['after_tick']!=798815 or r['before_tick']!=798033 or not r['all_inputs_applied']:raise ValueError('Closed matched-age DG expected')
  sources[key]={'primary':info(path),'committed_snapshot':d['committed_snapshot'],'result_summary':{k:r[k]for k in('life_id','condition','recording','before_tick','after_tick','new_native_ticks','requested','applied','all_inputs_applied','old_C2_metadata_unchanged','efference_count','generic_return_count','arithmetic_calls','actuator_calls')}}
  results[key]=r;analyses[key]=json.loads((P4/'control'/analysis_names[key]).read_text(encoding='utf-8'))
 parsed={}
 for key in('single_full','single_compact'):
  cut=sources[key]['committed_snapshot'];parsed[key]=parser(S2/cut['snapshot'],cut['snapshot_sha256'])
 a=parsed['single_full'];b=parsed['single_compact'];metakeys=[k for k in sorted(set(a[6])|set(b[6]))if a[6].get(k)!=b[6].get(k)]
 allowed=lambda k:k=='DEE.Cognitive.PI04.DG.field_equality.R01'or k=='DEE.Cognitive.System.1.1.life.v1'or k.startswith('DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1')
 framehashes=[]
 for x,y in zip(results['single_full']['frames'],results['single_compact']['frames']):
  framehashes.append({'relative_to_query':x['relative_to_query'],'physical_exact':x['physical']==y['physical'],'full_ROI':x['ROI_observations'],'compact_ROI':y['ROI_observations']})
 passivity={'same_four_material_requests':[(x['channel'],x['payload'],x['requested_tick'],x['receipt'])for x in results['single_full']['requests']]==[(x['channel'],x['payload'],x['requested_tick'],x['receipt'])for x in results['single_compact']['requests']],
  'all10_frame_global_hashes_equal':len(framehashes)==10 and all(x['physical_exact']for x in framehashes),'frame_comparisons':framehashes,
  'whole_RAW_buffers_exact':a[7]==b[7],'whole_clocks_buffers_exact':a[8]==b[8],
  'interfaces_exact':a[3]==b[3],'interfaces_count':[a[0]['interfaces_count'],b[0]['interfaces_count']],
  'pending_agenda_exact':a[4]==b[4],'pending_counts':[len(a[4]),len(b[4])],
  'all_Native_receipts_exact':a[5]==b[5],'receipt_counts':[len(a[5]),len(b[5])],
  'causal_prefix_exact':a[0]['causal_prefix_sha256']==b[0]['causal_prefix_sha256'],
  'metadata_differences':metakeys,'metadata_differences_only_declared_logging_identity_service':all(allowed(k)for k in metakeys),
  'same_original_six_site_reader':results['single_full']['reader']==results['single_compact']['reader'],
  'scope':'Only the additional4480ROI reads in this protocol. Same material queries and necessary six-site sensor retained. This is not universal neutrality of probes or all observers.'}
 fullframes=frame_values(results['single_full']['frames'][0]['journal']['file']);symframes=frame_values(results['symmetric_full']['frames'][0]['journal']['file'])
 evidence={'single':{'q':results['single_full']['calendar']['query_tick'],'q3_Q':cell(fullframes[3],[19,54,5]),'q4_Q':cell(fullframes[4],[19,54,5]),'q5_Q':cell(fullframes[5],[19,54,5]),'q4_intercept':cell(fullframes[4],[19,55,4]),'q5_intercept':cell(fullframes[5],[19,55,4]),'q6_equality_reader':cell(fullframes[6],[19,56,3]),'reader':results['single_full']['reader']},
  'symmetric':{'q':results['symmetric_full']['calendar']['query_tick'],'q4_Q':cell(symframes[4],[19,54,5]),'q5_plus_diagonal':cell(symframes[5],[20,55,5]),'q6_plus_reader':cell(symframes[6],[21,56,5]),'reader':results['symmetric_full']['reader']}}
 gradients={key:[{'relative':f['relative_to_query'],'Q':f['selected'].get('Q')}for f in analyses[key]['frames']if f['relative_to_query']in(3,4)]for key in('single_full','symmetric_full')}
 paragraph=('En un diagnóstico nuevo desde el corte completo detenido T798033, y no en una reproducción del episodio histórico, el dato4 y la referencia A−B=−4 sí formaron una igualdad física: en q+4 Q=(19,54,5) presentó SEM1 activa, s_reg0 y dirección(0,+1,−1). En q+5 Q quedó RAW0 y el soporte intermedio(19,55,4) conservó SEM4 activa; el lector previsto(19,56,3) permaneció vacío en q+6. La regla congelada de SEM4 conserva ese soporte antes de considerar fuentes entrantes, por lo que los registros y el código explican un bloqueo del tránsito de la igualdad, no ausencia de adquisición ni un cero leído como NULL. La condición de dos datos4 simétricos canceló la contribución Z, pero también duplicó la aportación X: formó dirección(+1,+1,0), observada después en(20,55,5) y en el lector(21,56,5), con elección+1. Esta condición tiene cinco entradas frente a cuatro y no es una reparación equivalente de la igualdad ni un control de dosis. Full y compact single llegaron T798815 con los mismos RAW/clocks globales, agenda, interfaces, recibos Native y lector, pese a4480lecturas ROI adicionales; sus diferencias declaradas de identidad/servicio/diario no se atribuyen a memoria cognitiva. La pasividad queda acotada a esta instrumentación y protocolo.')
 proof={'schema':'PI04.DG.field_and_observer.closed_analysis.v1','inspection_local':datetime.datetime.now().astimezone().isoformat(),'sources':sources,'field_evidence':evidence,'gradient_details':gradients,'passivity_single_full_vs_compact':passivity,
  'scientific_paragraph':paragraph,'interpretation':{'equality_signal_formed_then_blocked':True,'historical_original_episode_replayed':False,'new_diagnostic_only':True,'symmetric_changes_both_Z_balance_and_X_gain':True,'symmetric_not_dose_matched':True,'no_new_learning_or_repair_attributed':True,'no_trajectory_particle_identity_claim':True},
  'Native_execution_recorded_by_Root':{'three_closed_clones':True,'ticks_each':782,'ticks_total':2346,'source_tick':798033,'final_tick':798815},'new_Native_ticks_by_this_analysis':0,'DEE_imports':0,'sources_modified':False}
 out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'output':info(out),'reader_choices':{k:v['reader']['choice']for k,v in results.items()},'passivity':{k:v for k,v in passivity.items()if not isinstance(v,list)},'metadata_differences':metakeys,'new_Native_ticks_by_analysis':0},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
