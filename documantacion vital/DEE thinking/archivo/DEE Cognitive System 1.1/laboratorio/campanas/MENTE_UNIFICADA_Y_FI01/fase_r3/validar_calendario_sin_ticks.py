"""AST-isolated calendar checks; no DEE imports, world loads or native ticks."""
import ast,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2];MODULE=ROOT/'sistema/capacidades/mente_unificada_01.py'
def main():
    source=MODULE.read_text(encoding='utf8');tree=ast.parse(source);nodes=[]
    for n in tree.body:
        if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in('VERSION','PHASE_PROTECTION_VERSION')for t in n.targets):nodes.append(n)
        if isinstance(n,ast.FunctionDef)and n.name=='calendar_query_timing':nodes.append(n)
    subset=ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[]));scope={};exec(compile(subset,'CALENDAR_ONLY','exec'),scope);f=scope['calendar_query_timing']
    count=0;maximum=0;shifted=0
    for q in range(2,200001):
        old=f(q,False);new=f(q,True)
        assert old['effective_query_tick']==q and old['wait_ticks']==0
        e=new['effective_query_tick'];w=new['wait_ticks'];assert 0<=w<=10 and e==q+w
        assert not any(t%391==0 for t in range(e-1,e+9))
        assert all(any(t%391==0 for t in range(x-1,x+9))for x in range(q,e))
        count+=1;maximum=max(maximum,w);shifted+=w>0
    fn=next(n for n in nodes if isinstance(n,ast.FunctionDef));names={n.id for n in ast.walk(fn)if isinstance(n,ast.Name)}
    assert not names.intersection({'a','observation','physical','raw','target','value','reader','get','runtime'})
    result={'schema':'MUFI01.R3P0.calendar_static_check.v1','DEE_imports':0,'native_ticks':0,'worlds_loaded':0,'module_sha256':hashlib.sha256(MODULE.read_bytes()).hexdigest(),
      'calendar_function_arguments':[a.arg for a in fn.args.args],'domain_queries_checked':count,'legacy_exact_calendar_unchanged':True,'protected_window_contains_no_multiple391':True,
      'minimal_wait_checked':True,'maximum_wait_ticks':maximum,'shifted_queries':shifted,'R15_requested62556':f(62556,True),'R15_unprotected62556':f(62556,False),
      'scope':'Pure integer scheduling only. Does not establish physical benefit or preservation, which requires separately declared matched copies and native observations.'}
    p=HERE/'VALIDACION_CALENDARIO.json'
    if p.exists():raise FileExistsError('Preserve the original static validation')
    p.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8');print(json.dumps(result))
if __name__=='__main__':main()
