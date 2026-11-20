"""PI11 standard-RP identity binding, before official import; stdlib only.

Five administrative JSON files change in a new unselected code destination.
No snapshot, Native content, history, clock, scientific source or protocol is
edited. Preserved PI10/PI11 provenance remains literal. No current ACTIVO cut
is used to recover a past prefix; stable pair/capsule hashes are the contract.
"""
from pathlib import Path,PurePosixPath
import copy,hashlib,json,re,os
VERSION='DEE.PI11.diagnostic_family.identity_binding.R01'
RID='pi11_habitat16_familia_desde_REAL2_R01';CAP='PI11_HABITAT16_FAMILIA_R01'
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_RP_'
FILES=('capacidades/PI10_TRANSPORTE_ANCESTRAL_R01.json','capacidades/PI10_EXPERIMENTO_R02.json',
       'capacidades/PI10_PLUGINS_R01.json','capacidades/PI11_EXPERIMENTO_R01.json','capacidades/PI11_PLUGINS_R01.json')

def need(ok,msg):
    if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def encoded(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def regular(p):
    for n in(p,*p.parents):need(not n.is_symlink()and(not n.exists()or not(getattr(n.lstat(),'st_file_attributes',0)&1024)),'No symlink/reparse family path')
def inside(root,name):
    need(isinstance(name,str),'Relative resource string required');rel=PurePosixPath(name)
    need('\\'not in name and ':'not in name and not rel.is_absolute()and rel.parts and all(x not in('.','..')for x in rel.parts),'Exact safe relative resource')
    p=root.joinpath(*rel.parts);regular(p);need(p.resolve().is_relative_to(root.resolve()),'Escaping resource');return p

def rebound_documents(documents,life,template_life):
    """Pure transformation with no paths, current selection or scientific data."""
    need(re.fullmatch(re.escape(PREFIX)+r'[A-Z0-9]{1,10}',life),'Fresh explicit PI11 RP identity only')
    need(life!=template_life,'Cannot bind over source/template life')
    a,e,r,x,z=[copy.deepcopy(documents[n])for n in FILES]
    need(a.get('schema')=='DEE.PI10.exact_inherited_transport_scope.R01'and a.get('life_id')==template_life and a.get('role')in('real','reproduction'),'Actual PI11 descendant transport template')
    need(a.get('PI11_source_main_life_id')=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'and a.get('PI11_source_main_tick')==947395,'Preserved complete REAL2 prefix provenance')
    need(e.get('schema')=='DEE.PI10.fixed_experiment_scope.R02'and e.get('life_id')==template_life and e.get('role')=='evaluation'and e.get('arm')=='real'and e.get('trace_control')=='none'and e.get('force_query')is None,'Unforced inherited PI10 real scope')
    need(r.get('schema')=='DEE.PI10.fixed_plugins.v1'and z.get('schema')=='DEE.PI11.fixed_plugins.R01','Exact original plugin registries')
    need(x.get('schema')=='DEE.PI11.fixed_experiment_scope.R01'and x.get('life_id')==template_life and x.get('role')=='evaluation'and x.get('return_arm')=='real'and x.get('continuation')=='native','PI11 real/native evaluation only; controls remain separate')
    a['life_id']=life;a['role']='reproduction';e['life_id']=life;x['life_id']=life
    r['files_sha256']['PI10_TRANSPORTE_ANCESTRAL_R01.json']=hashlib.sha256(encoded(a)).hexdigest()
    r['files_sha256']['PI10_EXPERIMENTO_R02.json']=hashlib.sha256(encoded(e)).hexdigest()
    z['files_sha256']['PI11_EXPERIMENTO_R01.json']=hashlib.sha256(encoded(x)).hexdigest()
    return dict(zip(FILES,(a,e,r,x,z)))

def bind_context(context_file):
    context_file=Path(context_file).resolve(strict=True);dest=context_file.parent;system=dest/'sistema';context=read(context_file)
    recipe=context['fixed_recipe'];binding=recipe['diagnostic_identity_binding'];life=context['life'];regular(dest)
    need(context['recipe']==RID and recipe['id']==RID and context['variant']=='real16'and recipe['code_capsule_key']==CAP and binding.get('schema')==VERSION,'Exact registered PI11 real16 family only')
    need(re.fullmatch(re.escape(PREFIX)+r'[A-Z0-9]{1,10}',life)and not(system/'estado/ACTIVO.json').exists(),'Fresh unselected diagnostic family only')
    need(context['prefix_manifest_sha256']==binding['source_prefix_manifest_sha256']and context['system']==str(system)and context['source_code_capsule_key']==CAP,'Actual complete source pair and exact capsule required')
    for folder in('vidas','servicios_locales','servicios_persistentes'):need(not(system/'estado'/folder/life).exists(),'Binding must precede any Native import/owner')
    here=Path(__file__).resolve().parent;product=here.parent;resources=read(here/'RECURSOS.json');entry=resources['code_capsules'][CAP]
    capsule=inside(product,entry['product_relative']);mf=capsule/entry.get('manifest','SISTEMA_CODIGO.json')
    need(sha(mf)==entry['manifest_sha256']==context['source_code_manifest_sha256'],'Stable code capsule differs')
    rows={row['file']:row for row in read(mf)['files']};need(set(FILES)<=set(rows),'All five administrative templates must be preserved')
    for name,row in rows.items():need(sha(inside(capsule,name))==row['sha256']==sha(inside(system,name)),'Source/copied code differs: '+name)
    docs={name:read(system/name)for name in FILES}
    for registry,names in((FILES[2],FILES[:2]),(FILES[4],(FILES[3],))):
        for name in names:need(docs[registry]['files_sha256'][Path(name).name]==sha(system/name),'Original copied registry pin mismatch')
    after=rebound_documents(docs,life,binding['template_life_id']);before={name:sha(system/name)for name in FILES}
    output=dest/'VINCULO_FAMILIA_PI11_R01.json';intent=dest/'VINCULO_FAMILIA_PI11_R01.INTENT.json'
    need(not output.exists()and not intent.exists(),'Used/partial binding preserved; no retry')
    record={'schema':VERSION,'recipe':RID,'variant':'real16','exact_life_id':life,'template_life_id':binding['template_life_id'],
            'source_prefix_manifest_sha256':context['prefix_manifest_sha256'],'capsule_manifest_sha256':sha(mf),'files_before':before,
            'changed_paths':{FILES[0]:['/life_id','/role'],FILES[1]:['/life_id'],FILES[2]:['/files_sha256/PI10_TRANSPORTE_ANCESTRAL_R01.json','/files_sha256/PI10_EXPERIMENTO_R02.json'],FILES[3]:['/life_id'],FILES[4]:['/files_sha256/PI11_EXPERIMENTO_R01.json']},
            'Native_state_created_yet':False,'new_native_ticks':0,'new_native_inputs':0,'scientific_sources_or_protocol_changed':False,'not_learning_or_principal_adoption':True}
    with intent.open('xb')as f:f.write(encoded(record));f.flush();os.fsync(f.fileno())
    for name in FILES:
        target=system/name;need(sha(target)==before[name],'Concurrent administrative mutation');tmp=target.with_name(target.name+'.PI11_BINDING_WRITING');need(not tmp.exists(),'Unresolved prior JSON write')
        with tmp.open('xb')as f:f.write(encoded(after[name]));f.flush();os.fsync(f.fileno())
        os.replace(tmp,target)
    for name,row in rows.items():
        if name in FILES:need(read(system/name)==after[name],'Administrative binding failed')
        else:need(sha(system/name)==row['sha256'],'Other capsule file changed during binding')
    record['files_after']={name:sha(system/name)for name in FILES};record['all_other_capsule_files_literal']=True
    with output.open('xb')as f:f.write(encoded(record));f.flush();os.fsync(f.fileno())
    return record
