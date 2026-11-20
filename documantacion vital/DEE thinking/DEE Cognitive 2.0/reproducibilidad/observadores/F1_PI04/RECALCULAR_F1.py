"""Portable exact physical-feature recalculation. Stdlib only; never DEE."""
from pathlib import Path
import argparse,array,hashlib,json,sys
HERE=Path(__file__).resolve().parent
ZERO=1157425104234217473
def sha(b):return hashlib.sha256(b).hexdigest()
def encoded(a):
 if sys.byteorder=='little':return a.tobytes()
 b=array.array('Q',a);b.byteswap();return b.tobytes()
def unpack_sparse(spec,total):
 default=int(spec['default']);a=array.array('Q',[default])*total;seen=set()
 for index,value in spec['exceptions']:
  if type(index)is not int or not 0<=index<total or index in seen:raise ValueError('Invalid sparse index')
  v=int(value)
  if not 0<=v<2**64 or v==default:raise ValueError('Invalid sparse value')
  a[index]=v;seen.add(index)
 return a
def fields(raw):
 digits=[(raw>>k)&15 for k in(48,52,56)]
 return {'state':raw&0xffffffff,'semantic':raw>>60,'s_reg':(raw>>32)&65535,'direction':[d-16 if d&8 else d for d in digits]}
def reader(obs):
 candidates=[]
 for sign in(-1,0,1):
  expected=[19+2*sign,56,5];hits=[o for o in obs if o['site']==expected]
  if len(hits)!=1:raise ValueError('Missing/duplicate fixed reader cell')
  f=fields(int(hits[0]['RAW']))
  if f['state']>0 and f['semantic']==1 and f['direction']==[sign,1,0]:candidates.append(sign)
 return candidates[0]if len(candidates)==1 else None
def difference(a,b,n):
 return [{'site':[i//(n*n),(i//n)%n,i%n],'a':str(x),'b':str(y)}for i,(x,y)in enumerate(zip(a,b))if x!=y]
def calculate(d):
 n=d['N'];total=n**3
 if n!=67:raise ValueError('Only declared N67 domain')
 arrays={};physics=[];histories={a:[]for a in('real','return_nonfailure','actuator_null')};trialchecks=[]
 for cut in d['cuts']:
  raw=unpack_sparse(cut['RAW_sparse'],total);clocks=unpack_sparse(cut['clocks_sparse'],total)
  rh=sha(encoded(raw));ch=sha(encoded(clocks));w=cut['physical_witness']
  if rh!=w['RAW_sha256']or ch!=w['clocks_sha256']:raise ValueError('Global physical-buffer hash mismatch '+cut['key'])
  arrays[cut['key']]=raw
  physics.append({'key':cut['key'],'N':n,'tick':cut['tick'],'RAW_sha256':rh,'clocks_sha256':ch,'exact':True})
  choice=reader(cut['query_reader_RAW'])
  if choice!=cut['reported_original_choice']:raise ValueError('Fixed q+6 decoding differs from original report')
  history=histories[cut['arm']]
  history.append({'choice':choice,'read_tick':cut['query_read_tick']})
  predicted=sorted((56+cut['tick']-old['read_tick'])%n for old in history[-3:]if old['choice']==0)
  row=[raw[(19*n+y)*n+5]for y in range(n)]
  actual=sorted(y for y,v in enumerate(row)if v==ZERO)
  exact=actual==predicted and all(v in(0,ZERO)for v in row)
  if actual!=cut['original_F1_row_Y']or not exact:raise ValueError('History observer mismatch '+cut['key'])
  trialchecks.append({'key':cut['key'],'phase':cut['phase'],'tick':cut['tick'],'choice':choice,'predicted_Y':predicted,'actual_Y':actual,'exact':exact})
 pairs=[]
 for witness in d['global_comparison_witnesses']:
  a=arrays[witness['a_key']];b=arrays[witness['b_key']];actual=difference(a,b,n)
  if actual!=witness['positions']or len(actual)!=witness['RAW_sites_different']:raise ValueError('Full-global difference mismatch')
  pairs.append({'opportunity':witness['opportunity'],'comparison':witness['comparison'],'RAW_sites_different':len(actual),'positions':actual,'matches_original_full_array_comparison':True})
 clock_equal=[]
 for k in range(14):
  values=[x['clocks_sha256']for x in physics if x['key']in[f'R02/{a}/{k}'for a in histories]]
  if len(values)!=3 or len(set(values))!=1:raise ValueError('Matched-age clock mismatch')
  clock_equal.append(k)
 r05=d['R05'];translation=[]
 for f in r05['noquery_frames']:
  expected=sorted((y+f['tick']-r05['source_tick'])%n for y in r05['source_Y'])
  if expected!=f['recorded_Y']:raise ValueError('Toroidal noquery translation differs')
  translation.append({'label':f['label'],'tick':f['tick'],'expected_Y':expected,'actual_Y':f['recorded_Y'],'exact':True})
 failed_choice=reader(r05['failed_query_reader_RAW'])
 if failed_choice is not None:raise ValueError('Failed query must stay NULL, never numeric zero')
 r02=[x for x in trialchecks if x['phase']=='R02'];r04=[x for x in trialchecks if x['phase']=='R04']
 patterns=sorted({tuple(x['actual_Y'])for x in r02},key=lambda x:(len(x),x))
 return {'schema':'PI04.F1.portable_recalculation.v1','mode':'EXACT_FROZEN_PHYSICAL_FEATURES_NOT_NATIVE_REPLAY','N':n,
  'source_F1_result_sha256':d['source_F1_result']['sha256'],
  'checks':{'full_RAW_and_clocks_reconstructed_and_SHA_verified':len(physics),'R02_history_cuts_exact':len(r02),'R04_existing_extension_cuts_exact':len(r04),'global_RAW_pairs_reconstructed_and_compared':len(pairs),'matched_age_global_clock_equalities':len(clock_equal),'all_eight_row_patterns_observed':len(patterns)==8,'noquery_toroidal_frames_exact':len(translation),'failed_query_decodes_NULL':failed_choice is None,'zero_query_responses':sum(x['choice']==0 for x in trialchecks),'NULL_in_47_original_query_readers':sum(x['choice']is None for x in trialchecks)},
  'physical_hashes':physics,'history_checks':trialchecks,'global_differences':pairs,'row_patterns':[list(x)for x in patterns],'noquery_translation':translation,
  'current_protected_MAIN':d['current_protected_MAIN'],
  'limits':d['limits'],'new_Native_ticks':0,'DEE_imports':0,'external_original_files_opened':0,
  'not_full_operational_backup':'Only exact physical RAW/clocks and selected observations are exported; interfaces, agendas, receipts, queues, environment and transport are absent. Never restore this as a Native world.'}
def verify_manifest():
 manifest=json.loads((HERE/'MANIFIESTO_SHA256.json').read_text(encoding='utf-8'))
 allowed={'DATOS_F1.json','RECALCULAR_F1.py','LEER_PRIMERO.txt','RESULTADO_CONTRASTADO.json'}
 if set(manifest['members'])!=allowed:raise ValueError('Unexpected manifest members')
 for name,entry in manifest['members'].items():
  data=(HERE/name).read_bytes()
  if len(data)!=entry['bytes']or sha(data)!=entry['sha256']:raise ValueError('Manifest mismatch '+name)
 return manifest
def main(args):
 verify_manifest();data=json.loads((HERE/'DATOS_F1.json').read_text(encoding='utf-8'));actual=calculate(data)
 expected=json.loads((HERE/'RESULTADO_CONTRASTADO.json').read_text(encoding='utf-8'))
 if actual!=expected:raise ValueError('Recalculation differs from sealed contrasted result')
 text=json.dumps(actual,ensure_ascii=False,indent=2)+'\n'
 if args.output:
  out=Path(args.output).resolve()
  if not out.is_relative_to(HERE)or out.name in('DATOS_F1.json','RECALCULAR_F1.py','LEER_PRIMERO.txt','RESULTADO_CONTRASTADO.json','MANIFIESTO_SHA256.json'):raise ValueError('Output must be a new JSON inside this extracted directory')
  with out.open('x',encoding='utf-8')as f:f.write(text)
  print(json.dumps({'output':str(out),'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),'checks':actual['checks'],'new_Native_ticks':0},ensure_ascii=False))
 else:print(text,end='')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output');main(ap.parse_args())
