"""F1: frozen PI03 RAW/clocks/history only. No DEE imports or world execution.

The three-history observation is exploratory. R04 is an existing temporal
extension, not a prospectively blinded reserve for this newly designed reader.
"""
from pathlib import Path
import argparse,array,datetime,gzip,hashlib,json,struct,sys

HERE=Path(__file__).resolve().parent
DEFAULT_PI03=HERE.parents[1]/'PROGRESION_INTEGRADA_03'
N=67;Q=(19,54,5);ZERO_RAW=1157425104234217473
ARMS=('real','return_nonfailure','actuator_null')
def sha(b):return hashlib.sha256(b).hexdigest()
def stable(p):
 a=p.stat();b=p.read_bytes();c=p.stat()
 if(a.st_size,a.st_mtime_ns)!=(c.st_size,c.st_mtime_ns):raise ValueError('Concurrent source '+str(p))
 return b
def load(p):return json.loads(stable(p))
def inf(p):
 b=stable(p);return {'path':str(p.resolve()),'bytes':len(b),'sha256':sha(b)}
def primary(p):
 d=load(p)
 return json.loads(d['result'])if isinstance(d.get('result'),str)else d
def idx(site):return (site[0]*N+site[1])*N+site[2]
def xyz(i):return [i//(N*N),(i//N)%N,i%N]
def obs(raw,clocks,site):
 i=idx(site);v=raw[i];digits=[(v>>k)&15 for k in(48,52,56)]
 return {'site':list(site),'RAW':str(v),'clock':int(clocks[i]),'state':v&0xffffffff,'s_reg':(v>>32)&65535,'semantic':v>>60,'direction':[x-16 if x&8 else x for x in digits]}
def snapshot(path,expected_sha=None,expected_physical=None):
 encoded=stable(path)
 if expected_sha and sha(encoded)!=expected_sha:raise ValueError('Snapshot encoded hash '+str(path))
 b=gzip.decompress(encoded) # verifies the gzip CRC, not the DEE internal FNV
 if b[:8]!=b'DEETSNP1'or struct.unpack_from('<I',b,8)[0]!=2:raise ValueError('Unsupported frozen format')
 n=struct.unpack_from('<I',b,12)[0];tick=struct.unpack_from('<Q',b,16)[0];i=41
 size=struct.unpack_from('<I',b,i)[0];i+=4+size
 total=struct.unpack_from('<Q',b,i)[0];i+=8
 if n!=N or total!=N**3:raise ValueError('Unexpected dimensions')
 raw_bytes=b[i:i+8*total];clock_bytes=b[i+8*total:i+16*total]
 if len(raw_bytes)!=8*total or len(clock_bytes)!=8*total:raise ValueError('Truncated arrays')
 raw=array.array('Q');raw.frombytes(raw_bytes);clocks=array.array('Q');clocks.frombytes(clock_bytes)
 if sys.byteorder!='little':raw.byteswap();clocks.byteswap()
 physical={'N':n,'tick':tick,'RAW_sha256':sha(raw_bytes),'clocks_sha256':sha(clock_bytes)}
 if expected_physical and any(physical[k]!=expected_physical[k]for k in physical):raise ValueError('Physical witness mismatch')
 row=[obs(raw,clocks,(19,y,5))for y in range(N)]
 item={'snapshot':{'path':str(path.resolve()),'bytes':len(encoded),'sha256':sha(encoded)},'physical':physical,
       'row_region':'x=19,z=5,all Y=0..66; index=((x*N)+y)*N+z',
       'row_RAW':[o['RAW']for o in row],'row_clocks':[o['clock']for o in row],
       'row_nonzero':[o for o in row if int(o['RAW'])!=0],
       'row_zero_Y_carriers':[o for o in row if int(o['RAW'])==ZERO_RAW],
       'fixed_reader_at_cut':[obs(raw,clocks,(x,56,5))for x in(17,19,21)],
       'banks':[obs(raw,clocks,(x,53,5))for x in(18,20)],
       'limits':'Header/RAW/clocks read only; no interfaces, queues or metadata used as a reader. Full state remains local. No internal FNV recalc or Native restoration.'}
 return item,raw
def take_trial(p3,relative,history):
 path=p3/relative;d=primary(path);event=d['result']['rows'][0];committed=d['committed_snapshot']
 snap,raw=snapshot(p3/'estados/candidato/sistema'/committed['snapshot'],committed['snapshot_sha256'],committed['physical'])
 record={'opportunity':int(event['opportunity']),'choice':event['reader']['choice'],'query_read_tick':int(event['calendar']['query_read_tick']),'query_tick':int(event['calendar']['query_tick']),'after_tick':int(d['after_tick'])}
 history.append(record)
 predicted=[]
 for old in history[-3:]:
  if old['choice']==0:
   # Geometric translation of a zero read at Y56. This is a proposed observer,
   # not a simulation of collisions or a claim that one particle has identity.
   y=(56+record['after_tick']-old['query_read_tick'])%N
   predicted.append(y)
 actual=[o['site'][1]for o in snap['row_zero_Y_carriers']]
 snap.update({'primary':inf(path),'life':committed['life_id'],'event':record,'original_query_reader':event['reader'],
              'delay_laps':event['calendar']['delay_laps'],'after_minus_read':record['after_tick']-record['query_read_tick'],
              'all_row_nonzero_are_zero_Y':all(int(o['RAW'])==ZERO_RAW for o in snap['row_nonzero']),
              'prediction_last3_zero_events_Y':sorted(predicted),'actual_zero_Y':sorted(actual),
              'three_event_observer_exact':sorted(predicted)==sorted(actual)and all(int(o['RAW'])==ZERO_RAW for o in snap['row_nonzero'])})
 return snap,raw
def diff(a,b):
 changed=[i for i in range(len(a))if a[i]!=b[i]]
 return {'RAW_sites_different':len(changed),'positions':[{'site':xyz(i),'a':str(a[i]),'b':str(b[i])}for i in changed]}
def main(args):
 p3=args.pi03.resolve();out=(args.output or HERE/'F1_RESULTADO.json').resolve()
 if not out.is_relative_to(HERE.resolve())or out.suffix.lower()!='.json':raise ValueError('Output must be a JSON inside this F1 analysis directory; originals are read-only')
 if out.exists()and not args.replace_result:raise FileExistsError('Explicit --replace-result required; sources never change')
 histories={a:[]for a in ARMS};series={a:[]for a in ARMS};comparisons=[];last_arrays={}
 for k in range(14):
  arrays={}
  for arm in ARMS:
   item,arrays[arm]=take_trial(p3,f'ensayos/PI03_R02_{arm}_OP_{k}.json',histories[arm]);series[arm].append(item)
  current=[series[a][-1]for a in ARMS]
  comparisons.append({'opportunity':k,'same_tick':len({x['physical']['tick']for x in current})==1,
   'global_clocks_equal':len({x['physical']['clocks_sha256']for x in current})==1,
   'real_vs_nonfailure':diff(arrays['real'],arrays['return_nonfailure']),
   'real_vs_actuator_null':diff(arrays['real'],arrays['actuator_null'])})
  if k==13:last_arrays=arrays
 # Freeze the R02-derived observer before checking all five existing R04 cuts.
 r04=load(p3/'control/CONTINUACION_CADENA_R04.json');extension=[];arithmetic_intervals=[]
 for case in r04['cases']:
  arithmetic_intervals.append({'case':case['label'],'before_tick':case['source']['before_tick'],'after_tick':case['source']['after_tick'],'new_ticks':case['source']['after_tick']-case['source']['before_tick']})
  for opportunity in case['opportunities']:
   item,raw=take_trial(p3,opportunity['primary'],histories['real']);item['case']=case['label'];extension.append(item)
 # R05: translate the two recorded final R04 carriers through actual frozen cuts.
 old=load(p3/'control/FILA_CERO_TOROIDAL_PI03_PASIVA.json');r05=[];origin=old['views']['source_good_T768317']
 initial_y=[o['site'][1]for o in origin['nonzero_cells']if o['state']>0 and o['s_reg']==0 and o['direction']==[0,1,0]]
 for label,v in old['views'].items():
  item,_=snapshot(Path(v['snapshot']),v['sha256']);dt=item['physical']['tick']-origin['tick']
  item['label']=label;item['straight_prediction_from_source_Y']=sorted((y+dt)%N for y in initial_y)
  item['matches_translation']=item['straight_prediction_from_source_Y']==sorted(o['site'][1]for o in item['row_zero_Y_carriers'])
  item['interpretation']='Matching endpoints are compatible with recirculation; not unique lineage across unobserved interactions.'
  r05.append(item)
 frames=load(p3/'control/LECTURA_NOQUERY_R05_PASIVA.json')['frames'];noquery=[]
 for f in frames:
  expected=sorted((y+f['tick']-origin['tick'])%N for y in initial_y)
  actual=sorted(x['site'][1]for x in f['activeY']if x['state']>0 and x['s_reg']==0 and x['direction']==[0,1,0])
  noquery.append({'label':f['label'],'tick':f['tick'],'expected_Y':expected,'recorded_Y':actual,'exact':expected==actual})
 # Current adopted PI03 snapshot is an explicit immutable cut, not latest by tick.
 adopted=load(p3/'control/ADOPCION_PRODUCTO_PI03.json');product=p3.parents[2]/'DEE Cognitive 2.0'
 current,_=snapshot(product/'sistema'/adopted['active']['snapshot'],adopted['active']['snapshot_sha256'])
 retained=load(p3/'control/MAIN_INTEGRADA_OP3_RETENCION.json')
 current['actual_recent_output_history_from_record_NOT_used_by_physical_reader']=retained['final_task_state']['progress']['rows'][-3:]
 current['observer_domain_changed']='OP3 added state=0/SEM4 at (19,57,5); the unprotected three-event observer does NOT apply to the protected adopted anatomy. Absence of a tail no longer decodes +1.'
 outside=[]
 for comparison in comparisons:
  for key in('real_vs_nonfailure','real_vs_actuator_null'):
   for o in comparison[key]['positions']:
    site=o['site']
    if site not in([18,53,5],[20,53,5])and not(site[0]==19 and site[2]==5):outside.append({'opportunity':comparison['opportunity'],'comparison':key,'site':site})
 summary={'R02_cuts':42,'R02_observer_exact':sum(x['three_event_observer_exact']for a in ARMS for x in series[a]),
  'R02_clock_equal_comparisons':sum(x['global_clocks_equal']for x in comparisons),'R04_existing_extension_cuts':len(extension),
  'R04_observer_exact':sum(x['three_event_observer_exact']for x in extension),
  'R02_final_row_Y':{a:series[a][-1]['actual_zero_Y']for a in ARMS},
  'R02_final_global_RAW_diff_vs_real':{'return_nonfailure':comparisons[-1]['real_vs_nonfailure']['RAW_sites_different'],'actuator_null':comparisons[-1]['real_vs_actuator_null']['RAW_sites_different']},
  'all_28_R02_global_RAW_comparisons_confined_to_banks_and_Y_row':not outside,
  'noquery_translation_frames_exact':sum(x['exact']for x in noquery),'noquery_frames':len(noquery),
  'adopted_PI03_zero_Y_carriers':len(current['row_zero_Y_carriers']),
  'no_positive_native_use_demonstrated_for_new_history_reader':True,
  'interpretation':'Externally distinguishable short history of material outputs outside the banks; existing R05 proves causal interference, not useful recovery or learned access.'}
 result={'schema':'PI04.F1.frozen_history_observer.exploratory.v1','inspection_local':datetime.datetime.now().astimezone().isoformat(),
  'mode':'STATIC_FROZEN_RECORD_RECALCULATION_NO_NATIVE','summary':summary,
  'observer':{'region':[19,'allY',5],'zero_carrier_RAW':str(ZERO_RAW),'fingerprint':{'state':1,'semantic':1,'s_reg':0,'direction':[0,1,0]},
   'fitted_history_window':3,'coordinate_formula':'y=(56+Tcut-query_read_tick_of_old_zero)%67','scope':'Only reported settled cuts with the prepared query calendar; no learned decoder, new sensor or general memory capacity.',
   'blinding_limit':'Observer chosen after seeing all R02 outcomes and final R04 row in PI03 autopsy. Original eight R02 reserved cases are not reserves for this new observer. R04 intermediate row cuts not used to derive it, but endpoint was known. No prospective blind generalization claim.'},
  'R02':series,'R02_pair_comparisons':comparisons,'RAW_differences_outside_declared_region':outside,'R04_existing_extension':extension,'R04_interleaved_arithmetic_intervals':arithmetic_intervals,'R05_frozen':r05,'R05_noquery_translation':noquery,
  'adopted_PI03_T775355':current,'sources':{n:inf(p3/'control'/n)for n in('FILA_CERO_TOROIDAL_PI03_PASIVA.json','LECTURA_NOQUERY_R05_PASIVA.json','DIAGNOSTICO_COLA_R05B_GUARD.json','DIAGNOSTICO_COLA_R05B_SHAM.json','CONTINUACION_CADENA_R04.json','ADOPCION_PRODUCTO_PI03.json','MAIN_INTEGRADA_OP3_RETENCION.json')},
  'new_Native_ticks':0,'DEE_imports':0,'originals_modified':False,'all_full_snapshots_stay_at_listed_local_paths':True}
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'output':inf(out),'summary':summary},ensure_ascii=False,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--pi03',type=Path,default=DEFAULT_PI03);ap.add_argument('--output',type=Path);ap.add_argument('--replace-result',action='store_true');main(ap.parse_args())
