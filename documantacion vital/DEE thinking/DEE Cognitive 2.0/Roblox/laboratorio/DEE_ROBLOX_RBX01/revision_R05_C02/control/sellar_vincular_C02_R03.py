"""R03 performance wrapper around preserved exact closed-sealing algorithms.

No original source is edited. Only this process's path-check functions use a
scoped directory cache; all file SHA256/content checks remain mandatory. Fresh
ancestor identity checks run before binding, pair-manifest commit and final
seal. Root alone may execute; no Native/MCP process is opened.
"""
from pathlib import Path
import importlib.util,json,sys,time,types
ROOT=Path(__file__).resolve().parents[1]
def load(relative,name):
    s=importlib.util.spec_from_file_location(name,ROOT/relative);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
base=load('control/sellar_vincular_C02.py','_C02_R03_preserved_sealer')
paths=load('control/path_guard_C02_R03.py','_C02_R03_scoped_path_guard')
def verify(output,persistence=None):
    persistence=persistence or load('control/persistencia_C02.py','_C02_R03_preserved_verify_codec')
    guard=paths.PathGuard(ROOT);start=time.monotonic();original_safe=(base.safe,persistence.safe)
    def scoped(path,root=persistence.ROOT,*,exists=True):
        if Path(root)!=persistence.ROOT:return original_safe[1](path,root=root,exists=exists)
        return guard.safe(path,exists=exists)
    try:
        base.safe=lambda path,exists=True:guard.safe(path,exists=exists);persistence.safe=scoped
        result=base.verify(output,persistence)
        guard.recheck()
        return {**result,'verification_R03':{'elapsed_seconds':time.monotonic()-start,'path_checks':guard.stats(),
                'writes':False,'Native_imports':0,'Native_ticks':0,'all_member_SHA256_checked':True}}
    finally:base.safe,persistence.safe=original_safe
def seal(args,persistence=None,bridge=None):
    persistence=persistence or load('control/persistencia_C02.py','_C02_R03_preserved_codec')
    bridge=bridge or load('puente/rbx02_bridge_C02.py','_C02_R03_preserved_binder')
    guard=paths.PathGuard(ROOT);start=time.monotonic()
    originals=(base.safe,base.native_manifest,base.write,persistence.safe,persistence.write_json)
    def scoped_p_safe(path,root=persistence.ROOT,*,exists=True):
        if Path(root)!=persistence.ROOT:return originals[3](path,root=root,exists=exists)
        return guard.safe(path,exists=exists)
    def before_pair_write(path,value):
        if Path(path).name=='PAREJA_C02.json':guard.recheck()
        return originals[4](path,value)
    def before_final_write(path,value):
        if Path(path).name=='SELLADO_VINCULO_C02.json':guard.recheck()
        return originals[2](path,value)
    def guarded_bind(*a,**kw):guard.recheck();return bridge.bind_checkpoint(*a,**kw)
    proxy=types.SimpleNamespace(bind_checkpoint=guarded_bind)
    try:
        base.safe=lambda path,exists=True:guard.safe(path,exists=exists)
        base.native_manifest=lambda root,p:paths.scan_files(root,guard,base.sha,p.MAX_MEMBERS,p.MAX_BYTES)
        base.write=before_final_write;persistence.safe=scoped_p_safe;persistence.write_json=before_pair_write
        result=base.seal(args,persistence=persistence,bridge=proxy)
        guard.recheck()
        report={'schema':'DEE.RBX01.C02.closed_seal_path_checks.R03','elapsed_seconds':time.monotonic()-start,
                'path_guard':guard.stats(),'all_file_SHA256_required':True,'Native_imports':0,'Native_ticks':0,'MCP_calls':0,
                'source_files_sha256':{name:base.sha(ROOT/name)for name in('control/sellar_vincular_C02.py',
                     'control/persistencia_C02.py','control/path_guard_C02_R03.py','control/sellar_vincular_C02_R03.py')},
                'scope':'Only path ancestor checks cached within this invocation; fresh nonreparse identity rechecks before every commit. Scientific tables and complete file sets use preserved algorithms.'}
        originals[2](Path(args.output)/'OPTIMIZACION_R03.json',report)
        return {**result,'path_optimization':report}
    finally:
        base.safe,base.native_manifest,base.write,persistence.safe,persistence.write_json=originals
def main():
    args=base.parser().parse_args()
    if args.verify_only:result=verify(args.verify_only)
    else:result=seal(args)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
