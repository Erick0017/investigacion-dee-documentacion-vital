"""ROOT ONLY, default code-only proposal; --aplicar is explicit CAS deployment.

Reads only code/config/manifests and Root's already-created closed-process
witness. No Native/DEE/Owner/SQLite/card/snapshot read, import or write. The
actual 0-tick FI8 admission is a separate Root material command after install.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ast,hashlib,json,os
P=Path(__file__).resolve().parents[1];H=P/'codigo';SYSTEM=P/'estados/DISCOVERY/sistema';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'
SOURCE=H/'pi09_lote_FI8_R01.py';MANIFEST='SISTEMA_CODIGO_PI09.json'
def require(ok,why):
    if not ok:raise ValueError(why)
def sha(data):return hashlib.sha256(data).hexdigest()
def digest(p):return sha(Path(p).read_bytes())
def encoded(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def plain(p):
    for q in(p,*p.parents):require(not q.exists()or not(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024),'No linked/reparse installation path')
def fresh_process(file):
    proof=read(file);require(proof.get('schema')=='DEE.PI09.scoped_code_patch_process_proof.R01'and proof.get('safe_to_patch')is True and proof.get('no_live_affected_writers')is True,'Actual Root narrow closed-process witness required')
    require(Path(proof['system']).resolve()==SYSTEM.resolve()and proof['life_id']==LIFE,'Process witness is only for this exact Discovery system')
    age=(datetime.now(timezone.utc)-datetime.fromisoformat(proof['recorded_utc'])).total_seconds();require(0<=age<=min(600,proof.get('reuse_limit_seconds',0)),'Refresh expired process evidence; no PID/cache inference by installer')
    return {'path':str(Path(file).resolve()),'sha256':digest(file),'age_seconds':age,'scope':proof['scope']}
def prepare(tag):
    require(tag.replace('_','').isalnum()and len(tag)<65,'Short fresh tag');plain(SYSTEM);require(not(SYSTEM/'estado/ACTIVO.json').exists(),'Unselected Discovery code only')
    root=SYSTEM.parent;mf=root/MANIFEST;context=root/'CONTEXTO_EJECUCION.json';preparation=root/'PREPARACION_PI09.json';registry=SYSTEM/'capacidades/PI09_PLUGINS_R02.json'
    m=read(mf);ctx=read(context);prep=read(preparation);r=read(registry);require(ctx['life']==LIFE and Path(ctx['system']).resolve()==SYSTEM.resolve()and prep['context_sha256']==digest(context),'Exact official imported Discovery context/preparation')
    require(r['schema']=='DEE.PI09.fixed_plugins_source_registry.R01'and 'pi09_lote_FI8_R01'not in r['plugins']and not(SYSTEM/'capacidades'/SOURCE.name).exists(),'Fresh FI8 code registration only; do not replace/retry prior preparation')
    # Full code closure checked without opening any estado file or loading code.
    rows={}
    for row in m['files']:
        name=row['file'];require(name not in rows and not name.startswith(('estado/','motor/'))and '..'not in Path(name).parts,'Only literal code closure members')
        file=SYSTEM/name;plain(file);require(file.is_file()and file.stat().st_size==row['bytes']and digest(file)==row['sha256'],'Current code differs from its official closure: '+name);rows[name]=dict(row)
    for name,v in r['files_sha256'].items():require(Path(name).name==name and digest(SYSTEM/'capacidades'/name)==v,'Registered source changed: '+name)
    source=SOURCE.read_bytes();ast.parse(source.decode('utf-8-sig'));r['plugins'].append('pi09_lote_FI8_R01');r['files_sha256'][SOURCE.name]=sha(source)
    changes=[(SYSTEM/'capacidades'/SOURCE.name,source),(registry,encoded(r))]
    for target,data in changes:rows[target.relative_to(SYSTEM).as_posix()]={'file':target.relative_to(SYSTEM).as_posix(),'bytes':len(data),'sha256':sha(data)}
    prior=digest(mf);m.update(schema='DEE.PI09.derived_code_closure.FI8.R01',files=[rows[k]for k in sorted(rows)],previous_literal_manifest_sha256=prior,code_only_FI8_preparation={'source_sha256':sha(source),'Native_executed':False,'admission_executed':False,'new_Native_inputs':0,'scientific_actor_R02_changed':False})
    mbytes=encoded(m);ctx.setdefault('code_only_preparations',[]).append({'kind':'PI09_FI8_CODE_ONLY','current_manifest_file':MANIFEST,'current_manifest_sha256':sha(mbytes),'previous_manifest_sha256':prior,'admission_not_executed':True});ctx['current_code_manifest']={'file':MANIFEST,'sha256':sha(mbytes)}
    ctxbytes=encoded(ctx);prep['context_sha256']=sha(ctxbytes);prep['current_code_manifest_sha256']=sha(mbytes);prep.setdefault('code_only_preparations',[]).append({'kind':'FI8_CODE_ONLY','admission_executed':False,'D_permissions_resolved':False})
    changes.extend([(mf,mbytes),(context,ctxbytes),(preparation,encoded(prep))]);out=H/('INSTALACION_FI8_'+tag);require(not out.exists(),'Fresh staged proposal only');out.mkdir()
    plan={'schema':'DEE.PI09.FI8.code_only_installation_plan.R01','system':str(SYSTEM),'life_id':LIFE,'tag':tag,'Native_executed':False,'SQLite_or_world_read':False,'material_admission_executed':False,'changes':[],'plan_builder_sha256':digest(__file__)}
    for i,(target,data)in enumerate(changes):
        proposal=out/('%02d_PROPUESTO'%i);proposal.write_bytes(data);before=target.read_bytes()if target.exists()else None
        if before is not None:(out/('%02d_ORIGINAL_LITERAL'%i)).write_bytes(before)
        plan['changes'].append({'target':str(target),'before_sha256':None if before is None else sha(before),'source':str(proposal),'after_sha256':sha(data),'bytes':len(data)})
    file=out/'PLAN.json';file.write_bytes(encoded(plan));return {'plan':str(file),'sha256':digest(file),'Native_executed':False,'installed':False,'targets':len(changes)}
def apply(planfile,processfile):
    plan=read(planfile);require(plan['schema']=='DEE.PI09.FI8.code_only_installation_plan.R01'and plan['system']==str(SYSTEM)and plan['life_id']==LIFE and plan['plan_builder_sha256']==digest(__file__),'Exact original code-only plan/builder')
    process=fresh_process(processfile);require(not(SYSTEM/'estado/ACTIVO.json').exists(),'Never selected product');allowed={SYSTEM/'capacidades/pi09_lote_FI8_R01.py',SYSTEM/'capacidades/PI09_PLUGINS_R02.json',SYSTEM.parent/MANIFEST,SYSTEM.parent/'CONTEXTO_EJECUCION.json',SYSTEM.parent/'PREPARACION_PI09.json'}
    proof=P/'control'/('INSTALACION_FI8_'+plan['tag']+'_APLICADA.json');require(not proof.exists(),'Existing application preserved')
    for row in plan['changes']:
        target=Path(row['target']);source=Path(row['source']);plain(target);require(target in allowed and source.resolve().is_relative_to(H.resolve())and digest(source)==row['after_sha256'],'Fixed explicit code/config target and staged source')
        require((digest(target)if target.exists()else None)==row['before_sha256'],'Code/config CAS changed: '+str(target));require(not target.with_name(target.name+'.PI09_FI8_TMP').exists(),'Partial write remains fenced')
    for row in plan['changes']:
        target=Path(row['target']);data=Path(row['source']).read_bytes();temp=target.with_name(target.name+'.PI09_FI8_TMP')
        with temp.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
        os.replace(temp,target)
    result={'schema':'DEE.PI09.FI8.code_only_installation.applied.R01','applied':True,'system':str(SYSTEM),'life_id':LIFE,'plan':{'path':str(Path(planfile).resolve()),'sha256':digest(planfile)},'closed_process_witness':process,'changes':plan['changes'],'all_expected_code_sha256_match':all(digest(r['target'])==r['after_sha256']for r in plan['changes']),'Native_executed':False,'SQLite_card_snapshot_or_world_opened':False,'admission_executed':False,'R02_scientific_actor_changed':False,'current_code_manifest':{'path':str(SYSTEM.parent/MANIFEST),'sha256':digest(SYSTEM.parent/MANIFEST)},'literal_backups':str(Path(planfile).parent),'source_context_historical_capsule_pointer_preserved':True}
    with proof.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    return {'proof':str(proof),'sha256':digest(proof),'applied':True,'Native_executed':False,'admission_executed':False}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--tag',default='R01');ap.add_argument('--plan',type=Path);ap.add_argument('--procesos',type=Path);ap.add_argument('--aplicar',action='store_true');a=ap.parse_args()
    if a.aplicar:require(a.plan is not None and a.procesos is not None,'Explicit plan plus fresh Root narrow process proof');result=apply(a.plan,a.procesos)
    else:result=prepare(a.tag)
    print(json.dumps(result,ensure_ascii=False))
