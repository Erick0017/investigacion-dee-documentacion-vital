"""PI11 fresh NONE/YOKE clones with read-only C2C identity R02.

The preserved R01 clone/import engine is reused. Only explicit control code
gets the bootstrap alias; role, scientific actor and Native state stay
unchanged. Main and decisive acquisition replay use their original R01.
"""
from pathlib import Path
import argparse,ast,hashlib,importlib.util,json,shutil
H=Path(__file__).resolve().parent
SOURCE=H/'pi11_clonar_R01.py';SOURCE_SHA='92740973ce39360bf2f8edc26bfcef2766a02bfa6dcd5da240ba0e2cc27853c9'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,p):
    sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def base():
    need(sha(SOURCE)==SOURCE_SHA,'Preserved R01 cloner changed');b=load('PI11_control_cloner_R01_literal',SOURCE);patch=load('PI11_control_patch_pure',H/'aplicar_identidad_control_PI11_R02.py');old_install=b.install_actor
    def install_actor(a,dest,system):
        need(a.rol in('none','yoked','reproduction'),'This R02 adapter is exclusively a non-REAL control/replay; never modify MAIN R01')
        mf=old_install(a,dest,system);owner=system/'app/mundo_genesis_apd05.py';text=owner.read_text('utf-8-sig')
        if 'from capacidades import pi11_identidad_diagnostica_R02 as pi11_identity'not in text:owner.write_text(patch.patch_owner(text),'utf8')
        source=H/'pi11_identidad_diagnostica_R02.py';target=system/'capacidades'/source.name;ast.parse(source.read_bytes());shutil.copyfile(source,target)
        registryfile=system/'capacidades/PI11_PLUGINS_R01.json';registry=b.read(registryfile);registry['files_sha256'][source.name]=sha(target);registryfile.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n','utf8')
        manifest=b.read(mf);files={r['file']:r for r in manifest['files']}
        for f in(owner,target,registryfile):files[f.relative_to(system).as_posix()]={'file':f.relative_to(system).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}
        manifest['files']=[files[n]for n in sorted(files)];manifest['control_readonly_identity_revision']='R02';mf.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
        contextfile=dest/'CONTEXTO_EJECUCION.json';ctx=b.read(contextfile);ctx['source_code_manifest_sha256']=sha(mf);contextfile.write_text(json.dumps(ctx,ensure_ascii=False,indent=2)+'\n','utf8')
        prepfile=dest/'PREPARACION_PI11.json';prep=b.read(prepfile);prep.update(context_sha256=sha(contextfile),final_code_manifest_sha256=sha(mf),control_readonly_identity_revision='R02',role_preserved=a.rol,public_retention_enabled=False);prepfile.write_text(json.dumps(prep,ensure_ascii=False,indent=2)+'\n','utf8')
        return mf
    b.install_actor=install_actor;return b
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--slug',required=True);ap.add_argument('--vida',required=True);ap.add_argument('--rol',choices=('none','yoked','reproduction'),required=True);ap.add_argument('--prefijo',type=Path,required=True);ap.add_argument('--manifest-sha256',required=True);ap.add_argument('--sistema-padre',type=Path);ap.add_argument('--codigo-padre',type=Path);ap.add_argument('--actor',type=Path);ap.add_argument('--dependencia',type=Path,action='append');ap.add_argument('--codigo-cerrado-sha256');g=ap.add_mutually_exclusive_group();g.add_argument('--preparar',action='store_true');g.add_argument('--instalar-actor',action='store_true');g.add_argument('--importar',action='store_true');base().main(ap.parse_args())
if __name__=='__main__':main()
