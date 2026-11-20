"""Root-only pure-code correction on closed NONE/YOKE PI11 diagnostics.

PLAN writes nothing. APPLY preserves old code/closure, changes no role or
Native state and never grants public retention. Root must first reconcile
any global writer fence and closed SQLite auxiliary files, with real PID
evidence; this helper does not delete locks or repair queues.
"""
from pathlib import Path
import argparse,ast,hashlib,importlib.util,json,os,shutil
H=Path(__file__).resolve().parent;P=H.parent
def need(ok,msg):
    if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,p):
    sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def write_new(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def replace(p,v):
    tmp=p.with_name(p.name+'.PI11_CONTROL_WRITING');write_new(tmp,v);os.replace(tmp,p)
def patch_owner(text):
    old='from capacidades import pi11_identidad_heredada_R01 as pi11_identity';new='from capacidades import pi11_identidad_diagnostica_R02 as pi11_identity'
    need(text.count(old)==1,'Exact R01 diagnostic identity import');text=text.replace(old,new)
    for method in('validate','execute'):
        anchor='    def '+method+'(self,payload):\n        row=self._eci01_row(payload)\n';need(text.count(anchor)==1,'Exact owner operation anchor')
        text=text.replace(anchor,anchor+'        from capacidades import pi11_identidad_diagnostica_R02 as pi11_identity\n        pi11_identity.validate_external(self.a,row,payload=payload)\n')
    ast.parse(text);return text
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--system',type=Path,required=True);ap.add_argument('--life',required=True);ap.add_argument('--root-reconciliation',type=Path);ap.add_argument('--root-reconciliation-sha256');ap.add_argument('--preparado-no-importado',action='store_true');ap.add_argument('--source-code-sha256');ap.add_argument('--aplicar',action='store_true');a=ap.parse_args();system=a.system.resolve(strict=True)
    need(system.name=='sistema'and system.parent.parent==(P/'estados').resolve()and not(system/'estado/ACTIVO.json').exists(),'Only unselected PI11 diagnostic code')
    scopefile=system/'capacidades/PI10_TRANSPORTE_ANCESTRAL_R01.json';scope=read(scopefile);need(scope['life_id']==a.life and scope.get('role')in('none','yoked','reproduction'),'Only current non-REAL control/replay; no role change')
    need(system.parent.name in('NONE01','YOKE01','REPLAY01','REPLAY02'),'Only specifically identified control/replay destinations')
    for p in(system,*system.parents):need(not p.is_symlink()and not(getattr(p.lstat(),'st_file_attributes',0)&1024),'No linked control path')
    if a.preparado_no_importado:
        need(a.source_code_sha256 and sha(system.parent/'SISTEMA_CODIGO_PI11.json')==a.source_code_sha256,'Exact explicit prepared code manifest hash')
        need(not(system.parent/'IMPORTACION_DIAGNOSTICA.json').exists()and not(system.parent/'IMPORTACION_PI11.json').exists(),'Only truly unimported code preparation')
        for name in('vidas','servicios_persistentes','servicios_locales'):need(not(system/'estado'/name/a.life).exists(),'No partial/imported state may be treated as code-only')
        proof_file=None;guard={'no_live_affected_writer':True,'scope':'No world/service/worker/import exists; code-only preparation'}
        scientific=[scopefile,system/'capacidades/pi11_actor_R01.py',system/'capacidades/PROTOCOLO_PI11_R01.json',system/'capacidades/PI11_EXPERIMENTO_R01.json'];critical={str(p):sha(p)for p in scientific}
    else:
        need(a.root_reconciliation is not None,'Explicit Root reconciliation required for an imported control')
        proof_file=a.root_reconciliation.resolve(strict=True);need(proof_file.is_relative_to(P.resolve())and sha(proof_file)==a.root_reconciliation_sha256,'Exact Root closure/fence reconciliation proof');proof=read(proof_file)
        need(proof.get('schema')=='DEE.PI11.root_control_bootstrap_reconciliation.R01'and proof.get('life_id')==a.life and proof.get('no_live_affected_writer')is True and proof.get('global_writer_fence_reconciled')is True and proof.get('Native_tick_unchanged')is True and proof.get('SQLite_integrity')=='ok'and proof.get('unresolved_requests')==0,'Actual Root closure/reconciliation required, no guessed lock removal')
        guard=load('PI11_control_patch_closed_guard',H/'comprobar_proceso_PI11_R01.py').inspect('PI11_control_identity_R02_patch',system,a.life);need(guard.get('no_live_affected_writer')is True,'Strict current process/queue/import guard')
        cardfile=system/'estado/vidas'/a.life/'VIDA.json';card=read(cardfile);snapshot=system/card['snapshot'];db=system/'estado/servicios_persistentes'/a.life/'cola.sqlite3';critical={str(p):sha(p)for p in(cardfile,snapshot,db,scopefile)}
    ownerfile=system/'app/mundo_genesis_apd05.py';before_owner=sha(ownerfile);patched=patch_owner(ownerfile.read_text('utf-8-sig'));source=H/'pi11_identidad_diagnostica_R02.py';ast.parse(source.read_bytes());target=system/'capacidades'/source.name;need(not target.exists(),'Prior control identity attempt preserved')
    mf_file=system.parent/'SISTEMA_CODIGO_PI11.json';contextfile=system.parent/'CONTEXTO_EJECUCION.json';prepfile=system.parent/'PREPARACION_PI11.json';mf=read(mf_file);ctx=read(contextfile)
    need(ctx['source_code_manifest_sha256']==sha(mf_file),'Exact current code closure')
    for row in mf['files']:need(sha(system/row['file'])==row['sha256'],'Current source changed: '+row['file'])
    result={'schema':'DEE.PI11.control_readonly_identity_patch.R02','life_id':a.life,'role_preserved':scope['role'],'Native_ticks':0,'Native_inputs':0,'public_retention_enabled':False,'critical_before':critical,'old_owner_sha256':before_owner,'new_owner_sha256':hashlib.sha256(patched.encode('utf8')).hexdigest(),'new_identity_sha256':sha(source),'root_reconciliation':None if proof_file is None else{'path':str(proof_file),'sha256':sha(proof_file)},'closed_guard':guard,'code_only_before_any_import':a.preparado_no_importado}
    if not a.aplicar:print(json.dumps({**result,'mode':'PLAN_ONLY','writes':0},ensure_ascii=False,indent=2));return
    need(not(P/'PI11_ROOT_NATIVE_WRITER.lock').exists(),'Root global fence must already be reconciled, never removed here')
    backup=system.parent/'IDENTIDAD_CONTROL_R02_ANTES';need(not backup.exists(),'Prior patch preserved');backup.mkdir()
    registryfile=system/'capacidades/PI11_PLUGINS_R01.json'
    for f in(ownerfile,registryfile,mf_file,contextfile,prepfile):out=backup/(f.relative_to(system)if f.is_relative_to(system)else Path(f.name));out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,out)
    ownerfile.write_text(patched,'utf8');shutil.copyfile(source,target)
    registry=read(registryfile);registry['files_sha256'][source.name]=sha(target);replace(registryfile,registry)
    files={r['file']:r for r in mf['files']}
    for f in(ownerfile,target,registryfile):files[f.relative_to(system).as_posix()]={'file':f.relative_to(system).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}
    mf['files']=[files[n]for n in sorted(files)];mf['control_readonly_identity_revision']='R02';replace(mf_file,mf);ctx['source_code_manifest_sha256']=sha(mf_file);replace(contextfile,ctx);prep=read(prepfile);prep.update(context_sha256=sha(contextfile),final_code_manifest_sha256=sha(mf_file));replace(prepfile,prep)
    need(critical=={p:sha(Path(p))for p in critical},'Control patch altered Native/card/SQLite/role')
    result.update(applied=True,backup=str(backup),critical_unchanged=True,new_code_manifest_sha256=sha(mf_file));out=P/'control'/('IDENTIDAD_CONTROL_'+system.parent.name+'_R02.json');write_new(out,result);print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
