"""Pure infrastructure tests. Read originals; fake path writes stay in RAM."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,types
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema'
def load(name,p):
    sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def need(ok,msg):
    if not ok:raise AssertionError(msg)
def main():
    before=set(sys.modules);clone=load('PI11_pure_clone_test',H/'pi11_clonar_R01.py');supervisor=load('PI11_pure_plan_test',H/'pi11_ejecutar_plan_R01.py');export=load('PI11_pure_export_test',H/'pi11_exportar_R01.py')
    need(not any(n.startswith(('dee_thinking','dee_universe'))for n in set(sys.modules)-before),'No DEE import')
    original={n:(S/n).read_text('utf-8-sig')for n in('app/mundo_genesis_apd05.py','app/cola_local.py')};memory=dict(original)
    class FakePath:
        def __init__(self,p=''):self.p=p
        def __truediv__(self,k):return FakePath(self.p+'/'+k if self.p else k)
        def read_text(self,*args):return memory[self.p]
        def read_bytes(self):return memory[self.p].encode('utf8')
        def write_text(self,value,*args):memory[self.p]=value
    actual_sha=clone.sha;clone.sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    clone.patch_hooks(FakePath());clone.sha=actual_sha
    for text in memory.values():ast.parse(text)
    owner=memory['app/mundo_genesis_apd05.py'];queue=memory['app/cola_local.py']
    need(owner.count('pi11_identity.install(self.a)')==1,'One diagnostic identity hook')
    need(owner.count("startswith('eci01-pi11-')")==2,'Validate and execute PI11 before ancestors')
    need(queue.count('from capacidades.pi11_dispatcher_R01 import validate_literal')==1,'One queue hook')
    need(all((S/n).read_text('utf-8-sig')==text for n,text in original.items()),'Original source unchanged')
    sys.path[:0]=[str(S),str(S/'app')]
    owner_namespace={'__file__':str(S/'app/mundo_genesis_apd05.py'),'__name__':'PI11_pure_patched_owner'}
    exec(compile(owner,str(S/'app/mundo_genesis_apd05.py')+':in_memory_PI11_hooks','exec'),owner_namespace)
    need('GenesisNativeWorld'in owner_namespace,'Owner class imports without opening Native')
    actor=load('PI11_pure_actor_validate',H/'pi11_actor_R01.py')
    for mode in actor.MODES:actor.validate_literal({'modo':mode})
    rejected=0
    for row in ({'modo':'eci01-pi11-episodio','answer':1},{'modo':'eci01-pi11-forzar'},{'modo':'eci01-pi11-episodio','wait':67}):
        try:actor.validate_literal(row)
        except ValueError:rejected+=1
    need(rejected==3,'No answer, force or wait overrides accepted')
    adapted=export.adapt(export.OLD.read_text('utf-8-sig'),system=S.resolve(),life=export.PARENT,slug='PURE_TEST')
    need(adapted.P==P and adapted.S==S.resolve()and adapted.LIFE==export.PARENT,'Exact export scope')
    need(adapted.EXPORT_SLUG=='PURE_TEST'and adapted.PROC.name=='comprobar_proceso_PI11_R01.py','Scoped destination and process guard')
    for file in H.glob('*.py'):ast.parse(file.read_text('utf-8-sig'))
    need(not any(n.startswith(('dee_thinking','dee_universe'))for n in set(sys.modules)-before),'No DEE execution/import')
    print(json.dumps({'schema':'DEE.PI11.pure.infrastructure_tests.R01','passed':True,'Native_imported':False,'Native_ticks':0,'writes':'Only in-memory fake paths','original_operational_sources_unchanged':True,'checked':['clone hooks exact anchors','no duplicated hooks','queue PI11 scope','patched owner class import under isolated Python without open','actor literal modes and three rejected overrides','export adaptation','all PI11 syntax','module import passivity']}))
if __name__=='__main__':main()
