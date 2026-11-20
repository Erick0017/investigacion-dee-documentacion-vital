"""Stable-RP PI10 family binding, before official import; stdlib only.

Exactly three administrative JSON files change. Native states, scientific
bodies, bank contents, old scopes, preparation history and inputs do not.
No dependence on a campaign directory or on which life is selected now.
"""
from pathlib import Path,PurePosixPath
import copy,hashlib,json,re,os
VERSION='DEE.PI10.diagnostic_family.identity_binding.R01'
RID='pi10_consulta18_familia_desde_P0_T922374_R01'
CAP='PI10_CONSULTA18_FAMILIA_R01'
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RPF_'
P0='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_P0_01'
P0_SHA='214062c2d706e1354e5bb22fa5c66b72f32c0e61a249913b71a5f4fa7d4cf7da'
FILES=('capacidades/PI10_TRANSPORTE_ANCESTRAL_R01.json','capacidades/PI10_EXPERIMENTO_R01.json','capacidades/PI10_PLUGINS_R01.json')
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def encoded(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def regular(p):
 for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No symlink/reparse family path')
def inside(root,name):
 rel=PurePosixPath(name);need(isinstance(name,str)and '\\'not in name and ':'not in name and not rel.is_absolute()and rel.parts and all(x not in('.','..')for x in rel.parts),'Exact safe relative resource');p=root.joinpath(*rel.parts);regular(p);need(p.resolve().is_relative_to(root.resolve()),'Escaping resource');return p
def rebound_documents(documents,life,template_life):
 need(re.fullmatch(re.escape(PREFIX)+r'[A-Z0-9]{1,10}',life),'Fresh explicit PI10 RPF identity only')
 a,e,r=[copy.deepcopy(documents[n])for n in FILES]
 need(a.get('schema')=='DEE.PI10.exact_inherited_transport_scope.R01'and a.get('life_id')==template_life and a.get('role')in('real','reproduction')and a.get('source_main_life_id')=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01','Actual PI10 descendant administrative template only')
 need(e.get('schema')=='DEE.PI10.fixed_experiment_scope.R01'and e.get('life_id')==template_life and e.get('role')=='evaluation'and e.get('arm')=='real'and e.get('trace_control')=='none'and e.get('force_query')is None,'Only unforced real evaluation recipe; no control/reconstruction')
 need(r.get('schema')=='DEE.PI10.fixed_plugins.v1','Fixed PI10 plugin registry')
 olda,olde=hashlib.sha256(encoded(a)).hexdigest(),hashlib.sha256(encoded(e)).hexdigest()
 # Original JSON formatting may differ, so callers verify original bytes and
 # the original registry pins before supplying these parsed documents.
 a['life_id']=life;a['role']='reproduction';e['life_id']=life
 r['files_sha256']['PI10_TRANSPORTE_ANCESTRAL_R01.json']=hashlib.sha256(encoded(a)).hexdigest();r['files_sha256']['PI10_EXPERIMENTO_R01.json']=hashlib.sha256(encoded(e)).hexdigest()
 return {FILES[0]:a,FILES[1]:e,FILES[2]:r}
def bind_context(context_file):
 context_file=Path(context_file).resolve(strict=True);dest=context_file.parent;system=dest/'sistema';context=read(context_file);recipe=context['fixed_recipe'];binding=recipe['diagnostic_identity_binding'];life=context['life'];regular(dest)
 need(context['recipe']==RID and recipe['id']==RID and context['variant']=='real18'and recipe['code_capsule_key']==CAP and binding.get('schema')==VERSION,'Exact registered PI10 real18 family only')
 need(re.fullmatch(re.escape(PREFIX)+r'[A-Z0-9]{1,10}',life)and not(system/'estado/ACTIVO.json').exists(),'Only a fresh unselected diagnostic family')
 need(context['prefix_manifest_sha256']==P0_SHA and context['system']==str(system)and context['source_code_capsule_key']==CAP,'Actual neutral complete P0 and exact capsule required')
 need(not(system/'estado/vidas'/life).exists()and not(system/'estado/servicios_persistentes'/life).exists(),'Binding occurs before any Native import/owner')
 here=Path(__file__).resolve().parent;product=here.parent;resources=read(here/'RECURSOS.json');entry=resources['code_capsules'][CAP];capsule=inside(product,entry['product_relative']);mf=capsule/entry.get('manifest','SISTEMA_CODIGO.json')
 need(sha(mf)==entry['manifest_sha256']==context['source_code_manifest_sha256'],'Stable code capsule differs')
 manifest=read(mf);rows={row['file']:row for row in manifest['files']};need(set(FILES)<=set(rows),'All three declared administrative templates must be preserved')
 for name,row in rows.items():need(sha(inside(capsule,name))==row['sha256']==sha(inside(system,name)),'Source capsule or copied code differs: '+name)
 docs={n:read(system/n)for n in FILES};pins=docs[FILES[2]]['files_sha256'];need(pins['PI10_TRANSPORTE_ANCESTRAL_R01.json']==sha(system/FILES[0])and pins['PI10_EXPERIMENTO_R01.json']==sha(system/FILES[1]),'Original scope pins do not match copied bytes')
 template=binding['template_life_id'];after=rebound_documents(docs,life,template);before={n:sha(system/n)for n in FILES};resultfile=dest/'VINCULO_FAMILIA_PI10_R01.json';intent=dest/'VINCULO_FAMILIA_PI10_R01.INTENT.json';need(not resultfile.exists()and not intent.exists(),'Used/partial binding is preserved; no retry')
 record={'schema':VERSION,'recipe':RID,'variant':'real18','exact_life_id':life,'template_life_id':template,'full_P0_manifest_sha256':P0_SHA,'capsule_manifest_sha256':sha(mf),'files_before':before,'changed_paths':{FILES[0]:['/life_id','/role'],FILES[1]:['/life_id'],FILES[2]:['/files_sha256/PI10_TRANSPORTE_ANCESTRAL_R01.json','/files_sha256/PI10_EXPERIMENTO_R01.json']},'Native_state_created_yet':False,'new_native_ticks':0,'new_native_inputs':0,'scientific_sources_or_calendars_changed':False,'not_learning_or_new_principal':True}
 with intent.open('xb')as f:f.write(encoded(record));f.flush();os.fsync(f.fileno())
 for name in FILES:
  target=system/name;need(sha(target)==before[name],'Concurrent administrative mutation');tmp=target.with_name(target.name+'.PI10_BINDING_WRITING');need(not tmp.exists(),'Unresolved prior JSON write');tmp.write_bytes(encoded(after[name]));os.replace(tmp,target)
 for name,row in rows.items():
  if name in FILES:need(read(system/name)==after[name],'Administrative binding failed')
  else:need(sha(system/name)==row['sha256'],'Other code changed during binding')
 record['files_after']={n:sha(system/n)for n in FILES};record['all_other_capsule_files_literal']=True
 with resultfile.open('xb')as f:f.write(encoded(record));f.flush();os.fsync(f.fileno())
 return record
