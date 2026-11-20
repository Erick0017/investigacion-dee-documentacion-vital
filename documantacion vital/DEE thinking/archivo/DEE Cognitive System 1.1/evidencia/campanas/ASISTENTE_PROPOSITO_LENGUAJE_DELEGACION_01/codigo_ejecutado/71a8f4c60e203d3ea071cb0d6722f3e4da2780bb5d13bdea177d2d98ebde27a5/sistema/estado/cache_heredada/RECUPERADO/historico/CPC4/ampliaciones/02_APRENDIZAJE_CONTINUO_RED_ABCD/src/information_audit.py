"""Static host-operation inventory, not an attribution oracle or sandbox."""
from pathlib import Path
import ast,json
from campaign import ROOT,PARENT,put,sha

PHYSICAL={'set_raw','set_clock','import_research_state','apply_research_edits','diagnostic_fork','submit','submit_symbol','probe','probe_symbol','experience','create','load_snapshot','fork','save_snapshot'}
DATA_READS={'read_text','read_bytes','open','load','loads','read','loadtxt','load_snapshot'}

def scan(path):
    tree=ast.parse(path.read_text(encoding='utf-8-sig'),filename=str(path));rows=[]
    parents={c:p for p in ast.walk(tree) for c in ast.iter_child_nodes(p)}
    for node in ast.walk(tree):
        if not isinstance(node,ast.Call):continue
        fn=node.func.attr if isinstance(node.func,ast.Attribute) else node.func.id if isinstance(node.func,ast.Name) else ''
        if fn not in PHYSICAL|DATA_READS:continue
        p=node;scope=[]
        while p in parents:
            p=parents[p]
            if isinstance(p,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):scope.append(p.name)
        rows.append({'line':node.lineno,'scope':'.'.join(reversed(scope)),'call':fn,
                     'source':ast.get_source_segment(path.read_text(encoding='utf-8-sig'),node)[:350],
                     'role':'potential physical/operational operation' if fn in PHYSICAL else 'possible data read, review context'})
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'calls':sorted(rows,key=lambda x:x['line'])}

def run():
    paths=[p for p in (ROOT/'src').rglob('*.py') if '__pycache__' not in p.parts]
    paths += [p for p in (ROOT/'ejecutar.py',ROOT/'demostracion.py') if p.exists()]
    report={'schema':'CPC4.A02.HOST_OPERATION_INVENTORY.v1','scope':'AST audit of exact new source; not a guarantee against arbitrary native I/O',
            'separation':'Expected results and post-hoc metrics belong to auditor/tests; participant paths must not read measured result tables.',
            'modules':[scan(p) for p in sorted(paths)]}
    put(ROOT/'resultados'/'HOST_OPERATION_INVENTORY.json',report)
    return report

if __name__=='__main__':
    r=run();print(json.dumps({'modules':len(r['modules']),'calls':sum(len(x['calls']) for x in r['modules'])}))
