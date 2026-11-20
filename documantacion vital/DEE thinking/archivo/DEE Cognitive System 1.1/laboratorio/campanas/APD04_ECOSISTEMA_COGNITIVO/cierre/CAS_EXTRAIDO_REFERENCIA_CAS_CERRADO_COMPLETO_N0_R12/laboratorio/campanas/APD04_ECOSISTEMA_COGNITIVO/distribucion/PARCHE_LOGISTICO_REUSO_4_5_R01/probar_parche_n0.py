"""Pure archive-copy tests. No Runtime/owner/tick. Original files unchanged."""
import argparse
import ast
import base64
import hashlib
import importlib.util
import io
import json
from pathlib import Path,PurePosixPath
import shutil
import tempfile
import types

p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args()
s=a.root.resolve();collab=s.parent/'casos practicos/trabajo_codex/cognitive sistem'
here=Path(__file__).resolve().parent;source=collab/'actualizaciones/actualizar.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('logistic_updater_n0_test',source)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
tree=ast.parse(source.read_text(encoding='utf8'))
klass=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Build')
doc=next(n for n in klass.body if isinstance(n,ast.FunctionDef) and n.name=='documentation')
start=next(i for i,n in enumerate(doc.body) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='core' for x in n.targets))
# Execute the exact changed tail from the current function, not a second
# approximation. Manuals/official ZIP processing before it is unaffected.
tail=ast.FunctionDef(name='changed_documentation_tail',args=doc.args,body=doc.body[start:],decorator_list=[])
unit=ast.fix_missing_locations(ast.Module(body=[tail],type_ignores=[]));exec(compile(unit,'CURRENT_CHANGED_DOCUMENTATION_TAIL','exec'),m.__dict__)
index=m.read(s/'sistema/capacidades/core/documentacion/INDICE_MIEMBROS.json')
rows={n:r for n,r in index['paths'].items() if n.startswith('cpc8/genealogia/product45/') and PurePosixPath(n).suffix in ('.cpp','.hpp','.h','.json','.md','.txt')}
assert len(rows)==9
originals={n:(collab/('fuentes/thinking_4_5/'+PurePosixPath(n).name)).read_bytes() for n in rows}
before={n:hashlib.sha256(b).hexdigest() for n,b in originals.items()}
cases=[]
for mode in ('all9_reuse','one_missing_recover','one_modified_conflict'):
    temp=Path(tempfile.mkdtemp(prefix='logistic_'+mode+'_',dir=here))
    for n,b in originals.items():
        dest=temp/'fuentes/thinking_4_5'/PurePosixPath(n).name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
    selected=next(iter(rows));target=temp/'fuentes/thinking_4_5'/PurePosixPath(selected).name
    if mode=='one_missing_recover':target.unlink()
    if mode=='one_modified_conflict':target.write_bytes(target.read_bytes()+b'\nLOCAL_MODIFICATION_TEST_ONLY\n')
    reads=[]
    def fake_open(*args,**kwargs):
        reads.append('capsule_open')
        if mode=='all9_reuse':raise AssertionError('Capsule must not open for all nine exact files')
        wanted=rows[selected]['sha256']
        # Only missing/modified source is needed; sentinel must not be parsed.
        line=json.dumps({'sha256':wanted,'base64':base64.b64encode(originals[selected]).decode('ascii')})+'\n'
        return io.StringIO(line+'THIS_MUST_NEVER_BE_PARSED_AFTER_WANTED_EMPTY\n')
    m.ROOT=temp;m.gzip=types.SimpleNamespace(open=fake_open)
    build=m.Build(s);build.release='N0_TEST_ONLY';dirty=target.read_bytes() if mode=='one_modified_conflict' else None
    failure=None
    try:m.changed_documentation_tail(build)
    except RuntimeError as error:failure=str(error)
    if mode=='all9_reuse':
        assert len(build.members)==9 and not build.staged and not reads and failure is None
    elif mode=='one_missing_recover':
        assert len(build.members)==9 and len(build.staged)==1 and len(reads)==1 and failure is None
    else:
        assert failure and 'modificación local protegida' in failure and target.read_bytes()==dirty and len(reads)==1
        assert list((temp/'actualizaciones/conflictos').rglob('CONFLICTO.json'))
    cases.append({'case':mode,'members':len(build.members),'staged':len(build.staged),'capsule_opens':len(reads),'expected_conflict':bool(failure),'test_tree':str(temp)})
assert all(sha(collab/('fuentes/thinking_4_5/'+PurePosixPath(n).name))==d for n,d in before.items())
after=here/'actualizar_DESPUES.py';shutil.copyfile(source,after)
report={'schema':'APD04.updater_logistic.source_reuse.N0.R01','Native_ticks':0,'original_source_and_lives_unchanged':True,
        'exact_changed_AST_tail_executed':True,'nine_source_current_bytes':sum(map(len,originals.values())),
        'capsule_source_not_decompressed_by_these_tests':True,'cases':cases,
        'code_before_sha256':sha(here/'actualizar_ANTES.py'),'code_after_sha256':sha(after),'current_updater_sha256':sha(source)}
dest=here/'PRUEBAS_N0.json'
with dest.open('x',encoding='utf8',newline='\n') as f:json.dump(report,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
manifest={'members':[{'file':x.name,'bytes':x.stat().st_size,'sha256':sha(x)} for x in (here/'actualizar_ANTES.py',after,Path(__file__).resolve(),dest)],'no_self_hash':True}
mf=here/'MANIFIESTO.json'
with mf.open('x',encoding='utf8',newline='\n') as f:json.dump(manifest,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'manifest_sha256':sha(mf),'updater_after_sha256':sha(source),'cases':cases},ensure_ascii=False))
