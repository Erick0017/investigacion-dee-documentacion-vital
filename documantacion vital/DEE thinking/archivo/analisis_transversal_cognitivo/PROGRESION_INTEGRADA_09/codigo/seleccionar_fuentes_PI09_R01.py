"""Explicit analysis-source declaration. No ZIP, Native, owners or cleanup.

--candidatos lists only top-level campaign code/control/sources and the exact
active-code paths supplied by Root. --config expands only selected files and
the explicitly enabled bounded portable evidence directories into a new draft.
Root must close real gates and approve the final declaration before packaging.
"""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,os
P=Path(__file__).resolve().parents[1];R=P.parents[2];C=R/'DEE Cognitive 2.0'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def require(ok,message):
 if not ok:raise ValueError(message)
def safe(name):
 q=PurePosixPath(name)
 require(isinstance(name,str)and str(q)==name and not q.is_absolute()and ':'not in name and '\\'not in name and all(x not in ('..','.')for x in q.parts),'Safe canonical member path required')
 return q
def unlinked(path):
 path=Path(path).absolute();require(path.is_relative_to(R),'Source outside declared DEE tree')
 for x in(path,*path.parents):
  if x.exists():require(not x.is_symlink()and not(getattr(x.lstat(),'st_file_attributes',0)&1024),'No reparse/symlink source')
  if x==R:break
 return path.resolve(strict=True)
def entry(path,target,role):
 path=unlinked(path);require(path.is_file(),'File source only');safe(target)
 return {'source':str(path),'file':target,'bytes':path.stat().st_size,'sha256':sha(path),'role':role}
def save(path,obj):
 with Path(path).open('x',encoding='utf8')as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
def candidates(a):
 rows=[]
 for folder in ('codigo','control','fuentes'):
  for p in sorted((P/folder).iterdir()):
   if p.is_file()and p.suffix.lower()in ('.py','.json','.jsonl','.csv','.md','.txt','.ps1'):
    rows.append(entry(p,('03_CODIGO/'if folder=='codigo'else'05_CONTROL/'if folder=='control'else'02_FUENTES/')+p.name,'CANDIDATE_ONLY_NOT_SELECTED'))
 approved=read(a.codigo_aprobado)if a.codigo_aprobado else []
 for row in approved:
  current=entry(Path(row['source']),row['file'],'Root explicit active-code candidate')
  if row.get('sha256'):require(row['sha256']==current['sha256'],'Approved-code source changed')
  rows.append(current)
 value={'schema':'DEE.PI09.package_source_candidates.R01','status':'CANDIDATES_NOT_PACKAGE_APPROVAL','candidates':rows,'scope':'Top-level campaign files only; no Native worlds, disk inventory or automatic inclusion. Root must explicitly select current/decisive evidence, including negatives.','Native':0}
 save(a.salida,value);print(json.dumps({'output':str(a.salida),'candidates':len(rows),'Native':0}))
def expand(a):
 config=read(a.config);require(config['schema']=='DEE.PI09.explicit_package_selection.R01','Exact source-selection schema')
 members=[];seen=set();bundles=[]
 def add(row):
  name=row['file'];require(name.casefold()not in seen,'Duplicate/case-colliding package member: '+name);seen.add(name.casefold());members.append(row)
 for row in config.get('files',[]):
  add(entry(Path(row['source']),row['file'],row.get('role','Root explicit analysis evidence')))
 for row in config.get('active_approved_code',[]):
  item=entry(Path(row['source']),row['file'],'Actual approved Cognitive code delta')
  require(row.get('sha256')==item['sha256'],'Active code must have actual approved SHA, not a filename assertion');add(item)
 for bundle in config.get('portable_bundles',[]):
  if not bundle['enabled']:continue
  root=unlinked(Path(bundle['source_root']));require(root.is_dir()and root.is_relative_to(P/'control'),'Only explicit bounded portable evidence under campaign control')
  index=unlinked(root/bundle['index']);require(index.is_relative_to(root)and sha(index)==bundle['index_sha256'],'Frozen portable index required')
  count=total=0
  for base,dirs,files in os.walk(root,followlinks=False):
   for name in dirs:unlinked(Path(base)/name)
   for name in sorted(files):
    path=unlinked(Path(base)/name);rel=path.relative_to(root).as_posix();item=entry(path,bundle['target_root']+'/'+rel,'Closed '+bundle['id']+' portable documentary evidence');add(item);count+=1;total+=item['bytes']
  require(count<=bundle.get('maximum_files',2000)and total<=bundle.get('maximum_bytes',300000000),'Portable bundle scope exceeds explicit bound')
  bundles.append({'id':bundle['id'],'files':count,'bytes':total,'index_sha256':bundle['index_sha256']})
 docs={key:entry(Path(row['source']),row['file'],'Literal complete current '+key)for key,row in config['complete_documents'].items()}
 plan={'schema':'DEE.PI09.final_package_plan.v1','status':'DRAFT_EXPANDED_ACTUAL_BYTES_NOT_CLOSED','edition':config.get('edition'),'new_Native_ticks_by_packager':0,'members':members,'complete_documents':docs,'gates':config.get('gates',[]),'protected_files':config.get('protected_files',[]),'visual_QA_status':config.get('visual_QA_status','PENDING_ROOT_ACTUAL_RENDER_OR_LIMITATION'),'privacy_review':'PENDING_ROOT_EXPLICIT_REVIEW','D_executed':config.get('D_executed',False),'portable_verifications':config['portable_verifications'],'portable_bundle_expansion':bundles,'max_uncompressed_bytes':config.get('max_uncompressed_bytes',500000000),'source_selection_provenance':{'file':str(a.config.resolve()),'sha256':sha(a.config)},'analysis_is_not_a_full_executable_backup':True,'omitted_large_state_locators_must_be_included':True}
 save(a.salida,plan);print(json.dumps({'output':str(a.salida),'members':len(members),'bundles':bundles,'status':plan['status'],'Native':0},ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser();mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--candidatos',action='store_true');mode.add_argument('--config',type=Path);p.add_argument('--codigo-aprobado',type=Path);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();candidates(a)if a.candidatos else expand(a)
