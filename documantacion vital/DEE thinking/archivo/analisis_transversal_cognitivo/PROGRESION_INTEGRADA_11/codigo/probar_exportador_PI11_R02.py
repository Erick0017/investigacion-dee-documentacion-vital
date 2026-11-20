"""Pure regression of the exact no-ACTIVO reference and unchanged guards."""
from pathlib import Path
import ast,hashlib,importlib.util,json,types,sys
H=Path(__file__).resolve().parent
def main():
    p=H/'pi11_exportar_R02.py';sp=importlib.util.spec_from_file_location('PI11_export_R02_pure',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);before=set(sys.modules);text=m.adapted_source();tree=ast.parse(text)
    adapt=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='adapt')
    statement=next(n.value.value for n in ast.walk(adapt)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='new'for t in n.targets)and isinstance(n.value,ast.Constant)and isinstance(n.value.value,str)and 'activefile='in n.value.value)
    code=ast.parse(statement);assignment=next(n for n in code.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='active'for t in n.targets))
    class Absent:
        def exists(self):return False
    supplied='3eecc1284248b558e6a479a205a9fc9f3ef521e7e7b040e364a22b59579db99e';a=types.SimpleNamespace(tick=972419,snapshot_sha256=supplied)
    value=eval(compile(ast.Expression(assignment.value),'actual_R02_fallback_expression','eval'),{'a':a,'LIFE':'CURRENT_CLONE','activefile':Absent(),'read':lambda _:None})
    assert value=={'life_id':'CURRENT_CLONE','tick':972419,'snapshot_sha256':supplied}
    original=H/'pi11_exportar_R01.py';original_bytes=original.read_bytes();b=m.base();source=b.OLD.read_text('utf-8-sig')
    exact_guard="card['snapshot_sha256']==active['snapshot_sha256']==sha(snapshot)==a.snapshot_sha256"
    assert exact_guard in source and "json.loads(history.read_text('utf8').splitlines()[-1])['snapshot_sha256']==a.snapshot_sha256"in source
    assert source.index(exact_guard)<source.index('dest.mkdir(parents=True)')
    assert hashlib.sha256(original.read_bytes()).hexdigest()==m.SOURCE_SHA and original.read_bytes()==original_bytes
    assert not any(n.startswith(('dee_thinking','dee_universe'))for n in set(sys.modules)-before)
    print(json.dumps({'schema':'DEE.PI11.pure_export_R02_reference_regression.R01','passed':True,'Native_imported':False,'Native_ticks':0,'exports_performed':0,'file_writes':0,'R01_preserved':True,'fallback_has_exact_supplied_hash':True,'actual_card_snapshot_history_guards_unchanged_before_mkdir':True,'R02_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
