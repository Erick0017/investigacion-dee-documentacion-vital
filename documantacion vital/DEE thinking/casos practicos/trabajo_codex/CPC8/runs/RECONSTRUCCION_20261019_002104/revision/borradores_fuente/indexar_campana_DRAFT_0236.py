"""Read-only reconciliation of every campaign primary, including adverse cases.

Only the four named review outputs are written. No engine is imported, native
world is advanced, source modified, or scientific verdict assigned. Container
counts, explicit declared counts and independently located trajectory units
remain separate. Run --mode FINAL only after the campaign writer freeze.
"""
import argparse,collections,datetime,hashlib,json,re,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COUNT_KEYS=('preparations','fresh_preparations','independent_preparations','reference_reproductions','diagnostic_forks','continuations','controlled_continuations','technical_continuations','technical_restored_continuations','technical_reproductions','technical_preparations','technical_replays','audit_forks','audit_continuation_forks','unaltered_continuations','new_E1_histories')
BRANCH_KEYS=('results','conditions','conditional_forks','diagnostic_and_restore','diagnostic_forks')
INPUT_KEYS={'requests','inputs','receipts','native_receipts','quantity_receipts','initiative_receipts','source_requests','recipient_requests','new_requests','new_inputs_after_fork','new_inputs_after_restore','alternative_requests','all_parent_requests'}
OBS_KEYS={'frames','captures','social_captures','observations','trace','rows','local_windows','windows','quantity_observations','magnitude_observations','contact_social_observations','mode_captures','spatial_captures','social_captures_after_fork','captures_after_fork','receiving_readouts','readings','magnitude_readings','return_readouts','return_use_observations','renewal_observations','repeat_initiative_observations','initiative_captures'}
HEX=re.compile(r'^[0-9a-fA-F]{64}$');UINT=re.compile(r'^(?:[0-9]+|0[xX][0-9a-fA-F]+)$')

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb')as stream:
  for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def pointer(path,key):return path+'/'+str(key).replace('~','~0').replace('/','~1')
def rel(path):return path.relative_to(ROOT).as_posix()
def walk(value,path=''):
 yield path,value
 if isinstance(value,dict):
  for k,v in value.items():
   if isinstance(v,(dict,list)):yield from walk(v,pointer(path,k))
 elif isinstance(value,list):
  for i,v in enumerate(value):
   if isinstance(v,(dict,list)):yield from walk(v,pointer(path,i))
def scalar_label(value):
 if isinstance(value,(str,int,bool))or value is None:return value
 if isinstance(value,dict):return value.get('id',value.get('case_id'))
 return None
def identifier(value,fallback):return next((scalar_label(value[k])for k in('case','case_id','id','condition','mode')if k in value and scalar_label(value[k])is not None),fallback)
def int_counts(value):
 result={k:v for k in COUNT_KEYS if isinstance((v:=value.get(k)),int)and not isinstance(v,bool)}
 if isinstance(value.get('counting'),dict):
  result.update({'counting.'+k:v for k,v in value['counting'].items()if k in COUNT_KEYS and isinstance(v,int)and not isinstance(v,bool)})
 return result
def category(value):
 counts=int_counts(value);text=str(value.get('modality',value.get('mode',''))).upper()
 if text=='HISTORICAL_REFERENCE_REPRODUCTION':return'TECHNICAL_REFERENCE_REPRODUCTION'
 if any(counts.get(k,0)>0 for k in('technical_preparations','technical_reproductions','technical_replays')):return'TECHNICAL_REPRODUCTION'
 if any(counts.get(k,0)>0 for k in('preparations','fresh_preparations','independent_preparations','counting.independent_preparations'))or value.get('kind')=='EXPLORATORY_INDEPENDENT_PREPARATION_NOT_E1':return'PREPARATION'
 if counts.get('diagnostic_forks',0)>0 or text=='DIAGNOSTIC_FORK':return'DIAGNOSTIC_FORK'
 if 'TECHNICAL' in text or any(counts.get(k,0)>0 for k in('technical_continuations','technical_restored_continuations')):return'TECHNICAL_RESTORATION_OR_REPLAY'
 if counts.get('continuations',0)>0 or counts.get('controlled_continuations',0)>0:return'CONTINUATION'
 if value.get('status')=='TECHNICAL_ERROR'and counts.get('preparations')==0:return'PREPARATION_FAILED_BEFORE_RUNTIME'
 return'UNCLASSIFIED'

def branch_children(m):
 found=[]
 for key in BRANCH_KEYS:
  seq=m.get(key)
  if isinstance(seq,list):found.extend((pointer(pointer('',key),i),x)for i,x in enumerate(seq)if isinstance(x,dict))
  elif isinstance(seq,dict):found.extend((pointer(pointer('',key),i),x)for i,x in seq.items()if isinstance(x,dict))
 # "rows" in a physical measurement is normally a tick table. Only entries
 # with a condition/mode/modality or explicit per-trajectory count are units.
 for i,x in enumerate(m.get('rows',[])if isinstance(m.get('rows'),list)else[]):
  if isinstance(x,dict)and(any(k in x for k in('condition','mode','modality'))or int_counts(x)):found.append(('/rows/'+str(i),x))
 return found

def units(m,primary):
 children=branch_children(m);declared=int_counts(m);top=category(m)
 # A root scientific preparation can contain later diagnostic branches. Its
 # own primary is one unit, plus those explicit children, not a second copy
 # of its frame/observation arrays or a nested saved base338 run.
 rows=[]
 if top!='UNCLASSIFIED'and(declared.get('preparations',0)==1 or declared.get('fresh_preparations',0)==1 or declared.get('counting.independent_preparations',0)==1 or m.get('kind')=='EXPLORATORY_INDEPENDENT_PREPARATION_NOT_E1' or top=='TECHNICAL_REFERENCE_REPRODUCTION'):rows.append({'pointer':'','category':top,'count':1,'reason':'Explicit preparation/type declaration at container root; reference and technical categories remain separate'})
 elif not children and top!='UNCLASSIFIED':
  count=next((declared[k]for k in('diagnostic_forks','continuations','controlled_continuations','technical_continuations','technical_restored_continuations','technical_preparations','technical_replays','technical_reproductions')if declared.get(k,0)>0),1)
  rows.append({'pointer':'','category':top,'count':count,'reason':'Root explicit count; no child trajectories separately counted'})
 for p,x in children:
  c=category(x)
  if c=='UNCLASSIFIED':
   condition=str(x.get('condition',x.get('mode',''))).lower()
   if condition.startswith('restore')or condition in('unchanged_restore','technical_restore'):c='TECHNICAL_RESTORATION_OR_REPLAY'
   elif any(q in condition for q in('cut','sham','lesion','intercept','edit')):c='DIAGNOSTIC_FORK'
  if c=='UNCLASSIFIED'and(str(primary).startswith(('resultados/diagnostico_L15/','resultados/diagnostico_L15_r1/','resultados/diagnostico_L15_causal/'))):c='DIAGNOSTIC_CONTINUATION'
  if c=='UNCLASSIFIED'and str(primary).startswith('resultados/rescate_SOC21/')and x.get('condition')=='intact':c='TECHNICAL_RESTORATION_OR_REPLAY'
  rows.append({'pointer':p,'category':c,'count':1,'label':identifier(x,p),'declared_counts':int_counts(x),'reason':'Explicit branch object; condition-derived type is retained for review, not an independent preparation'})
 if not rows:rows=[{'pointer':'','category':'UNCLASSIFIED','count':1,'reason':'No unambiguous root or branch trajectory declaration'}]
 # Provenance reanalyses contain copied case summaries plus new diagnostic
 # branches. The /cases collection is intentionally never a new preparation.
 return rows

def exact_integer_check(m):
 n=0;errors=[]
 for p,v in walk(m):
  if not isinstance(v,dict):continue
  for k,x in v.items():
   if k.lower()not in('raw','clock','raw64','clock64','clocks'):continue
   for q,y in ((pointer(p,k)+'/'+str(i),z)for i,z in enumerate(x))if isinstance(x,list)else((pointer(p,k),x),):
    if isinstance(y,(dict,list))or y is None:continue
    n+=1
    if isinstance(y,bool)or isinstance(y,float):errors.append({'pointer':q,'type':type(y).__name__,'reason':'RAW/clock must be exact uint64, never floating point'})
    elif isinstance(y,int):
     if not 0<=y<2**64:errors.append({'pointer':q,'reason':'Integer outside uint64 range'})
    elif isinstance(y,str)and UINT.fullmatch(y):
     if not 0<=int(y,16 if y.lower().startswith('0x')else 10)<2**64:errors.append({'pointer':q,'reason':'String outside uint64 range'})
    else:errors.append({'pointer':q,'reason':'Unrecognized scalar RAW/clock encoding','type':type(y).__name__})
 return{'exact_scalar_fields_checked':n,'violations':errors}

def collections_index(m):
 rows=[]
 for k,v in m.items():
  if k in INPUT_KEYS and isinstance(v,list):
   statuses=collections.Counter();ids=[]
   for x in v:
    if isinstance(x,dict):
     r=x.get('receipt',x);r=r if isinstance(r,dict)else{};statuses[str(r.get('status','not_recorded'))]+=1
     if isinstance(x.get('id'),int):ids.append(x['id'])
   rows.append({'pointer':'/'+k,'kind':'INPUT_OR_RECEIPT_COLLECTION','count':len(v),'row_pointer_template':'/'+k+'/{index}','statuses':dict(statuses),'id_range':[min(ids),max(ids)]if ids else None,'not_independent_samples':True})
  elif k in OBS_KEYS and isinstance(v,list):
   ticks=[x.get('tick')for x in v if isinstance(x,dict)and isinstance(x.get('tick'),int)]
   rows.append({'pointer':'/'+k,'kind':'OBSERVATION_COLLECTION','count':len(v),'row_pointer_template':'/'+k+'/{index}','tick_range':[min(ticks),max(ticks)]if ticks else None,'not_independent_samples':True})
 # All embedded branch frames/inputs have exact relative locators too. Their
 # values are not duplicated in this compact index.
 for p,x in branch_children(m):
  for row in collections_index_shallow(x):rows.append({**row,'pointer':p+row['pointer'],'row_pointer_template':p+row['row_pointer_template']})
 return rows
def collections_index_shallow(m):
 rows=[]
 for k,v in m.items():
  if k in INPUT_KEYS|OBS_KEYS and isinstance(v,list):rows.append({'pointer':'/'+k,'kind':'INPUT_OR_RECEIPT_COLLECTION'if k in INPUT_KEYS else'OBSERVATION_COLLECTION','count':len(v),'row_pointer_template':'/'+k+'/{index}','not_independent_samples':True})
 return rows

def source_declarations(m):
 rows=[]
 for k in('source','source_sha256','code_sha256','frozen_source_hashes'):
  v=m.get(k)
  if isinstance(v,str)and HEX.fullmatch(v):rows.append({'pointer':'/'+k,'name':None,'sha256':v.lower()})
  elif isinstance(v,dict):
   for name,d in v.items():
    if isinstance(d,str)and HEX.fullmatch(d):rows.append({'pointer':pointer('/'+k,name),'name':name,'sha256':d.lower()})
 return rows

def main():
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=('DRAFT','FINAL'),default='DRAFT');p.add_argument('--out',type=Path,default=ROOT/'revision');a=p.parse_args();started=time.monotonic();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
 script_hash=sha(__file__)
 source_paths=list(ROOT.rglob('*.py'));source_paths+=list((ROOT/'configuraciones').rglob('*.json'));source_paths+=list((ROOT/'base_validada').rglob('*.json'));source_paths+=list((ROOT/'genealogia').rglob('*.json'));source_paths += [x for x in(ROOT/'resultados').rglob('*.json')if x.name.upper().startswith(('CONFIG','CANDIDATE','FIXTURE','CRITERIA'))];byhash=collections.defaultdict(list)
 for x in source_paths:
  try:byhash[sha(x)].append(rel(x))
  except OSError:pass
 primaries=sorted((ROOT/'resultados').rglob('MEASUREMENTS*.json'));containers=[];observations=[];controls=[];problems=[];unclassified=[];schema_counts=collections.Counter();unit_counts=collections.Counter();partition_counts=collections.defaultdict(collections.Counter)
 for path in primaries:
  relative=rel(path)
  try:
   st=path.stat();data=path.read_bytes();m=json.loads(data.decode('utf-8-sig'));same=st.st_size==path.stat().st_size and st.st_mtime_ns==path.stat().st_mtime_ns
  except(Exception,)as e:problems.append({'primary':relative,'status':'OPEN_OR_UNREADABLE','error':repr(e)});continue
  status=m.get('status','NOT_DECLARED');schema=m.get('schema','UNVERSIONED_EXPLICIT_FIELDS');schema_counts[schema]+=1;parts=Path(relative).parts;partition='REFERENCE_CPC7'if parts[1]=='cpc7_reproduccion'else'REFERENCE_K65'if'K65'in relative.upper()else'REFERENCE_FROZEN_CPC8'if m.get('modality')=='HISTORICAL_REFERENCE_REPRODUCTION'or'.heritage.'in schema or'HERITAGE'in str(m.get('case_id',''))else'CAMPAIGN_TECHNICAL'if parts[1]=='tecnicas'else'NEW_CAMPAIGN_PHYSICS'
  row={'primary':relative,'primary_sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'schema':schema,'case_id':identifier(m,path.parent.name),'status':status,'stable_during_read':same,'partition':partition,'declared_counts':int_counts(m),'count_basis':'Root and explicit branch trajectories only; embedded /base338 and copied /cases summaries are not new individuals. L15/SOC historical continuation classifications reconciled with campaign owner; no new MAIN preparation.','trajectory_units':units(m,relative),'collections':collections_index(m),'uint64':exact_integer_check(m),'source_checks':[]}
  if m.get('error')is not None:row['recorded_error']={'type':m.get('error_type'),'text':str(m['error'])[:1000],'pointer':'/error'}
  if status in('RUNNING','STARTED')or not same:problems.append({'primary':relative,'status':'OPEN_PRIMARY','last_complete_tick':m.get('last_complete_tick')})
  for d in source_declarations(m):
   matches=byhash.get(d['sha256'],[]);near=[x for x in matches if x.startswith(rel(path.parent)+'/')];archived=[x for x in matches if'/executed_source/'in x or'/source/'in x or'/fuentes/'in x]
   row['source_checks'].append({**d,'status':'MATCH_CASE_ARCHIVE'if near else'MATCH_OTHER_ARCHIVE'if archived else'MATCH_CURRENT_SOURCE_ONLY'if matches else'DECLARED_HASH_NOT_LOCATED','matches':near or archived[:8]or matches[:8]})
  row['configuration_checks']=[]
  for key in('configuration_sha256','config_sha256','historical_configuration_sha256','frozen_configuration_sha256'):
   if isinstance(m.get(key),str)and HEX.fullmatch(m[key]):
    matches=byhash.get(m[key].lower(),[]);row['configuration_checks'].append({'pointer':'/'+key,'sha256':m[key].lower(),'status':'MATCH_EXACT_FILE_BYTES'if matches else'DECLARED_HASH_NOT_LOCATED','matches':matches[:8]})
  for u in row['trajectory_units']:
   unit_counts[u['category']]+=u['count'];partition_counts[partition][u['category']]+=u['count']
   if u['category']=='UNCLASSIFIED':unclassified.append({'primary':relative,**u})
  for key in('parent','reference_primary','source_primary','interrupted_attempt'):
   if key in m:row[key]=m[key]if isinstance(m[key],(str,int,bool))else{q:m[key][q]for q in('path','sha256','primary','snapshot','tick')if q in m[key]}if isinstance(m[key],dict)else None
  errors=row['uint64']['violations']
  if errors:problems.append({'primary':relative,'status':'UINT64_FORMAT_VIOLATIONS','violations':errors})
  for pth,x in walk(m):
   if isinstance(x,dict)and any(k in x for k in('edited_sites','intervention','interventions','edits','diagnostic_edits','sham_full_physical_equal','parent_unchanged')):
    keys=[k for k in x if k in('edited_sites','intervention','interventions','edits','diagnostic_edits','sham_full_physical_equal','parent_unchanged','clock_preserved','current_sensor_perception_preserved')]
    controls.append({'primary':relative,'pointer':pth,'case_id':row['case_id'],'fields':keys,'field_locators':[relative+'#'+pointer(pth,k)for k in keys]})
  containers.append(row);observations.append({'case_id':row['case_id'],'primary':relative,'sha256':row['primary_sha256'],'status':status,'partition':partition,'trajectory_units':row['trajectory_units'],'collections':row['collections'],'uint64_exact_fields_checked':row['uint64']['exact_scalar_fields_checked'],'selection':'Every primary, including controls, failed attempts and adverse results; no success filter.'})
 # Public app logs are technical trajectory reproductions, not scientific
 # acquisitions or independent minds. They have no MEASUREMENTS primary.
 apps=[]
 for path in sorted((ROOT/'resultados/app').rglob('OBSERVACIONES.jsonl'))if(ROOT/'resultados/app').exists()else[]:
  try:
   records=[json.loads(x)for x in path.read_text(encoding='utf8').splitlines()if x.strip()];frames=[x['contenido']for x in records if x.get('origen')=='ENTE'];errs=[i+1 for i,x in enumerate(records)if x.get('contenido',{}).get('estado')in('ERROR_EXPLICITO','RECHAZO_EXPLICITO')];r={'primary':rel(path),'sha256':sha(path),'category':'TECHNICAL_PUBLIC_APP_REPRODUCTION','lines':len(records),'observed_frames':len(frames),'ticks':[x['tick']for x in frames],'explicit_error_lines':errs,'line_locator_template':rel(path)+'#line={one_based_line}'};apps.append(r);observations.append({**r,'selection':'All public app logs, not scientific independent preparations'})
  except Exception as e:problems.append({'primary':rel(path),'status':'OPEN_OR_UNREADABLE_APP_LOG','error':repr(e)})
 partial=[]
 for config in sorted((ROOT/'resultados').rglob('CONFIG.json')):
  if(config.parent/'MEASUREMENTS.json').exists():continue
  snaps=sorted(config.parent.glob('*.deetsnap*'))
  if not snaps:continue
  row={'configuration':rel(config),'configuration_sha256':sha(config),'category':'PERSISTED_ATTEMPT_WITHOUT_MEASUREMENTS','status':'PARTIAL_NO_TERMINAL_PRIMARY','snapshots':[{'path':rel(x),'sha256':sha(x),'bytes':x.stat().st_size}for x in snaps],'counting':'Not silently dropped or declared PASS. A fresh T0 checkpoint establishes a prepared native attempt; later recovery is a continuation, not another preparation.'}
  if any(x.name.startswith('T0.')for x in snaps):row['partial_prepared_attempts']=1
  partial.append(row);observations.append(row)
 family_counts=collections.defaultdict(collections.Counter)
 for row in containers:
  family=Path(row['primary']).parts[1];family_counts[family]['containers']+=1
  for unit in row['trajectory_units']:family_counts[family][unit['category']]+=unit['count']
 current_primaries={rel(x)for x in(ROOT/'resultados').rglob('MEASUREMENTS*.json')};initial_primaries={rel(x)for x in primaries};changed=[]
 if a.mode=='FINAL':
  for row in containers:
   if sha(ROOT/row['primary'])!=row['primary_sha256']:changed.append(row['primary'])
  for row in apps:
   if sha(ROOT/row['primary'])!=row['sha256']:changed.append(row['primary'])
 if current_primaries!=initial_primaries or changed:problems.append({'status':'PRIMARY_INVENTORY_OR_BYTES_CHANGED','added':sorted(current_primaries-initial_primaries),'removed':sorted(initial_primaries-current_primaries),'changed':changed})
 summary={'schema':'CPC8R.campaign.reconciled_counts.v1','mode':a.mode,'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'script_sha256':script_hash,'script_unchanged':script_hash==sha(__file__),'primary_files_found':len(primaries),'primary_containers_read':len(containers),'schemas':dict(schema_counts),'recorded_statuses':dict(collections.Counter(x['status']for x in containers)),'trajectory_units_provisionally_classified':dict(unit_counts),'partitions':{k:dict(v)for k,v in partition_counts.items()},'families':{k:dict(v)for k,v in family_counts.items()},'public_app_technical_reproductions':len(apps),'partial_attempt_containers':len(partial),'partial_prepared_attempts_not_in_MEASUREMENTS_totals':sum(x.get('partial_prepared_attempts',0)for x in partial),'unclassified':unclassified,'problems':problems,'exact_uint64_scalars_checked':sum(x['uint64']['exact_scalar_fields_checked']for x in containers),'semantics':'Counts are execution/accounting categories, never measures of NSM mastery, general intelligence, architecture superiority or independent replicas. A fork, query, frame and tick are not a new preparation.','source_check_counts':dict(collections.Counter(x['status']for r in containers for x in r['source_checks'])),'configuration_check_counts':dict(collections.Counter(x['status']for r in containers for x in r['configuration_checks'])),'elapsed_seconds':time.monotonic()-started}
 summary['classification_complete']=not unclassified;summary['primary_integrity_passed']=not problems;summary['status']='DRAFT_NOT_FROZEN'if a.mode=='DRAFT'else'FINAL_RECONCILED'if not problems and not unclassified and summary['script_unchanged']else'FINAL_INCOMPLETE'
 index={'schema':'CPC8R.campaign.evidence_index.v1','mode':a.mode,'summary':'RECUENTOS_RECONCILIADOS.json','primary_containers':containers,'app_reproductions':apps,'persisted_partial_attempts':partial,'open_or_unreadable':problems,'limits':'Compact locators preserve access to every source array entry via JSON Pointer/index. Values remain in their byte-hashed primary and are not copied into the review index. Source matches outside the case archive are explicitly distinguished; absence of a declared hash is not silently interpreted as validation.'}
 def write(name,v):
  target=out/name;tmp=target.with_name(target.name+'.writing');tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8');tmp.replace(target)
 write('INDICE_EVIDENCIA.json',index);write('RECUENTOS_RECONCILIADOS.json',summary);write('CONTROLES_Y_ABLACIONES.json',{'schema':'CPC8R.campaign.controls_index.v1','mode':a.mode,'records':controls,'limits':'Localizers of actually recorded intervention/control fields, not an automatic causal-validity verdict.'})
 target=out/'OBSERVACIONES.jsonl';tmp=target.with_name(target.name+'.writing');tmp.write_text(''.join(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n'for x in observations),encoding='utf8');tmp.replace(target)
 print(json.dumps({k:summary[k]for k in('mode','primary_containers_read','trajectory_units_provisionally_classified','public_app_technical_reproductions','source_check_counts','elapsed_seconds')}));print(json.dumps({'unclassified_count':len(unclassified),'problem_count':len(problems)}))
 if a.mode=='FINAL'and summary['status']!='FINAL_RECONCILED':raise SystemExit(1)
if __name__=='__main__':main()
