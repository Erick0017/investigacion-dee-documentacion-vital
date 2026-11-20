"""Closed Real18/RPF18 passive comparison, deliberately strict.

No engine imports or execution. All nonmatching scientific paths remain
errors. Only exact current-life/worker paths, checked journal/witness hashes,
known environment wall-clock provenance and PI02 pause segmentation receive
explicit narrowly named transport treatment. Native physical/causal prefix
must be exactly equal; no tolerance is fitted from the replay.
"""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,re,sqlite3
KEY='DEE.Cognitive.PI10.adaptive_query.two_native_traces.R01';FOLDER='PI10_CONSULTA_ADAPTATIVA_R01';SYSTEM='DEE.Cognitive.System.1.1.life.v1';SERVICE='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1';PI02='DEE.Cognitive.PI02.continuous_workbench.R04';PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RPF_'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def diff(a,b,path=''):
 if type(a)is not type(b):return[path]
 if isinstance(a,dict):return[p for k in sorted(set(a)|set(b))for p in([path+'/'+k]if k not in a or k not in b else diff(a[k],b[k],path+'/'+k))]
 if isinstance(a,list):return[path+'/length']if len(a)!=len(b)else[p for i,(x,y)in enumerate(zip(a,b))for p in diff(x,y,path+'/'+str(i))]
 return[]if a==b else[path]
def normalized(value,life):
 if isinstance(value,list):return[normalized(x,life)for x in value]
 if isinstance(value,dict):
  out={k:normalized(v,life)for k,v in value.items()}
  schema=value.get('schema','')
  if schema=='DEE.PI10.fixed_two_bin_environment.R01.offer':out.pop('prepared_utc',None);out.pop('manifest_sha256',None)
  if schema=='DEE.PI10.fixed_two_bin_environment.R01.result':out.pop('offer_manifest_sha256',None)
  return out
 if isinstance(value,str):
  if value==life:return'__CURRENT_TRANSPORT_LIFE__'
  text=value.replace('\\','/');marker='/estado/servicios_locales/'+life+'/'
  if marker in text and(re.match('^[A-Za-z]:/',text)or text.startswith('/')):return'__CURRENT_WORKER_HOME__/'+text.split(marker,1)[1]
 return value
def checked_journal(home,meta):
 file=home/'eventos.jsonl';chain='00'*32;rows=[]
 for line in file.read_bytes().splitlines(keepends=True):rows.append(json.loads(line));chain=hashlib.sha256(bytes.fromhex(chain)+line).hexdigest()
 need(len(rows)==meta['log_count']and chain==meta['log_chain_sha256'],'Journal does not match its complete checkpoint')
 return rows,{'sha256':sha(file),'rows':len(rows),'chain':chain}
def compare(source_pair,source_sha,replay,parser_path):
 source_pair=Path(source_pair).resolve(strict=True);replay=Path(replay).resolve(strict=True);mf=source_pair/'EXPORTACION_SERVICIO.json';need(sha(mf)==source_sha,'Actual immutable Real18 full export/hash required');m=read(mf);life=read(replay/'CONTEXTO_EJECUCION.json')['life'];need(re.fullmatch(re.escape(PREFIX)+r'[A-Z0-9]{1,10}',life),'Fresh RPF family only');system=replay/'sistema';need(not(system/'estado/ACTIVO.json').exists(),'Never compare by opening a selected original')
 card=read(system/'estado/vidas'/life/'VIDA.json');snapshot=system/card['snapshot'];need(sha(snapshot)==card['snapshot_sha256'],'Replay snapshot/card differs')
 need(sha(parser_path)=='dbb2a5e15d70c64112d36505197f4aebf6ff7d4092972923e17cd60c10a1c873','Exact passive parser only');sp=importlib.util.spec_from_file_location('PI10_frozen_complete_state_reader',parser_path);p=importlib.util.module_from_spec(sp);sp.loader.exec_module(p);x=p.snapshot_view(source_pair/'VIDA.deetsnap.gz');y=p.snapshot_view(snapshot)
 source_life=m['life_id'];sx=json.loads(x['metadata'][KEY]);sy=json.loads(y['metadata'][KEY]);need(sx['ordinal']==sy['ordinal']==18 and len(sx['rows'])==len(sy['rows'])==18 and all(not q.get('pending')and not q.get('uncertain')and q.get('ready')and q.get('admitted')for q in(sx,sy)),'Both complete continuous closed Real18 states required')
 need(all(q['admission_control']=={'role':'evaluation','arm':'real','trace_control':'none','force_query':None}for q in(sx,sy)),'Calibration/control never compared as real acquisition')
 sh=source_pair/'artefactos_trabajador'/FOLDER;th=system/'estado/servicios_locales'/life/FOLDER;sj,sjp=checked_journal(sh,sx);tj,tjp=checked_journal(th,sy);witnesses=[];unexpected=[];canonical_hashes={}
 for i,(a,b)in enumerate(zip(sx['rows'],sy['rows'])):
  aa=a['witness'];bb=b['witness'];af=sh/aa['file'];bf=th/bb['file'];need(aa['file']==bb['file']=='episodio_%04d.json'%i and af.stat().st_size==aa['bytes']and bf.stat().st_size==bb['bytes']and sha(af)==aa['sha256']and sha(bf)==bb['sha256'],'Actual episode witness integrity differs')
  av=normalized(read(af),source_life);bv=normalized(read(bf),life);paths=diff(av,bv);witnesses.append({'ordinal':i,'normalized_equal':not paths,'other_different_paths':paths,'source_sha256':aa['sha256'],'replay_sha256':bb['sha256']})
  canonical_hashes[aa['file']]=hashlib.sha256(json.dumps(av,sort_keys=True,separators=(',',':')).encode()).hexdigest()
  if paths:unexpected.append(KEY+'.witness.'+str(i))
 def norm_meta(v,identity):
  v=normalized(copy.deepcopy(v),identity);v.pop('log_chain_sha256',None)
  for row in v['rows']:row['witness']={'file':row['witness']['file'],'normalized_verified_content_sha256':canonical_hashes[row['witness']['file']]}
  return v
 metadata_changes=[]
 for key in sorted(set(x['metadata'])|set(y['metadata'])):
  a=x['metadata'].get(key);b=y['metadata'].get(key)
  if a==b:continue
  entry={'key':key,'source_sha256':None if a is None else hashlib.sha256(a.encode()).hexdigest(),'replay_sha256':None if b is None else hashlib.sha256(b.encode()).hexdigest()}
  if key==SYSTEM or key==SERVICE or key.startswith(SERVICE+'.queue.'):entry['permitted_scope']='Explicit current transport/service/queue identity; Native prefix compared separately'
  elif key==KEY and a is not None and b is not None:
   paths=diff(norm_meta(json.loads(a),source_life),norm_meta(json.loads(b),life));entry.update(changed_scientific_paths=paths,permitted_scope='Checked own journal chain/current identity/witness provenance only')
   if paths:unexpected.append(key)
  elif key==PI02 and a is not None and b is not None:
   av,bv=json.loads(a),json.loads(b);paths=diff(av,bv);entry['changed_paths']=paths;aa=copy.deepcopy(av);bb=copy.deepcopy(bv);aa.pop('paused_intervals',None);bb.pop('paused_intervals',None)
   if aa!=bb:unexpected.append(key)
   else:entry['permitted_scope']='PI02 host pause-interval segmentation only; all other fields literal'
  else:unexpected.append(key)
  metadata_changes.append(entry)
 def normalized_journal(rows,identity):
  value=normalized(rows,identity)
  for event in value:
   for k in('witness',):
    if k in event and event[k].get('file')in canonical_hashes:event[k]={'file':event[k]['file'],'normalized_verified_content_sha256':canonical_hashes[event[k]['file']]}
  return value
 jpaths=diff(normalized_journal(sj,source_life),normalized_journal(tj,life))
 if jpaths:unexpected.append(KEY+'.journal')
 result={'schema':'DEE.PI10.actual_real18_RPF18.full_passive_comparison.R01','physical_equal':x['physical']==y['physical'],'causal_prefix_equal':x['causal_prefix_sha256']==y['causal_prefix_sha256'],'source_physical':x['physical'],'replay_physical':y['physical'],'source_causal_prefix_sha256':x['causal_prefix_sha256'],'replay_causal_prefix_sha256':y['causal_prefix_sha256'],'unexpected_metadata_changes':unexpected,'metadata_changes_all_listed':metadata_changes,'episode_witnesses':witnesses,'journals':{'source':sjp,'replay':tjp,'normalized_equal':not jpaths,'other_different_paths':jpaths},'source_pair_manifest_sha256':source_sha,'Native_executed':False,'new_ticks':0,'comparison_criteria_not_fitted_to_replay':True,'preserve_failure_without_relaxing_criterion':True};result['overall']=result['physical_equal']and result['causal_prefix_equal']and not unexpected;return result
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--fuente-par',type=Path,required=True);ap.add_argument('--fuente-manifest-sha256',required=True);ap.add_argument('--destino-replay',type=Path,required=True);ap.add_argument('--parser',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args();need(not a.salida.exists(),'Never overwrite a failed comparison');v=compare(a.fuente_par,a.fuente_manifest_sha256,a.destino_replay,a.parser);a.salida.parent.mkdir(parents=True,exist_ok=True)
 with a.salida.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(a.salida),'sha256':sha(a.salida),'overall':v['overall'],'unexpected_metadata_changes':v['unexpected_metadata_changes'],'Native':0}));return 0 if v['overall']else 2
if __name__=='__main__':raise SystemExit(main())
