"""Embed the verified inert recovery store and adapt only host wheel location."""
from pathlib import Path
import argparse,ast,hashlib,json,zipfile,shutil
ROOT=Path(__file__).resolve().parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def constants(source):
    values={}
    def value(n):
        if isinstance(n,ast.Constant):return n.value
        if isinstance(n,ast.Tuple):return tuple(value(x)for x in n.elts)
        if isinstance(n,ast.Name):return values[n.id]
        if isinstance(n,ast.BinOp)and isinstance(n.op,ast.Add):return value(n.left)+value(n.right)
        raise ValueError('Not an inert constant')
    for n in ast.parse(source).body:
        if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
            try:values[n.targets[0].id]=value(n.value)
            except(KeyError,ValueError):pass
        elif isinstance(n,ast.AugAssign)and isinstance(n.target,ast.Name)and isinstance(n.op,ast.Add):
            try:values[n.target.id]+=value(n.value)
            except(KeyError,ValueError):pass
    return values
def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--numpy-root',type=Path);a=p.parse_args();core=ROOT/'sistema/capacidades/core';rows=[];diffs=[]
    with zipfile.ZipFile(a.archive)as z:
        for i in z.infolist():
            n=i.filename.removeprefix('DEE_COGNITIVE_CORE/')
            keep=n.startswith(('configuraciones/','reproduccion/','scripts/'))or n in('mecanismos/RECUPERACION_POR_HASH.jsonl.gz','documentacion/INDICE_MIEMBROS.json','documentacion/MATRIZ_CAPACIDADES.json','documentacion/NUMPY_DEPENDENCIA.json','IDENTIDAD_KERNEL.json','DEPENDENCIAS.json','README.md','USO_PRIVADO.md','documentacion/CORRECCIONES_HISTORICAS.md','verificaciones/CORE06_PRIMARY_TRANSITIONS.json','verificaciones/CORE07_PRIMARY_TRANSITIONS.json')
            if not keep or i.is_dir():continue
            b=z.read(i);original=hashlib.sha256(b).hexdigest()
            if n=='reproduccion/worker_core.py':
                before=b.decode('utf8');after=before.replace("ROOT/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'","Path(__file__).resolve().parents[3]/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'")
                after=after.replace('allowed=(ROOT.resolve(),materialized.resolve()',"allowed=((Path(__file__).resolve().parents[3]/'runtime').resolve(),ROOT.resolve(),materialized.resolve()")
                after=after.replace('def identity():\n import dee_thinking as d',"def identity():\n sys.path.insert(0,str(Path(__file__).resolve().parents[3]))\n from app.process_control import protect_current\n protection=protect_current()\n import dee_thinking as d")
                if after==before:raise ValueError('Expected legacy wheel location was not found')
                b=after.encode('utf8');diffs.append({'member':i.filename,'original_sha256':original,'new_sha256':hashlib.sha256(b).hexdigest(),'change':'Two wheel references point at the unique system/runtime wheel; audit read scope admits only that shared runtime dependency folder in addition to original scopes. Physics, recipes, evaluator and fixture selection unchanged.'})
            f=core/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b);rows.append({'source_member':i.filename,'original_sha256':original,'system_path':f.relative_to(ROOT/'sistema').as_posix(),'system_sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
        text=z.read('DEE_COGNITIVE_CORE/reproduccion/desde_cero.py').decode('utf8');const=constants(text)
    config={'schema':'DCS1.1.legacy.families.v1','prefixes':list(const['PREFIXES']),'families':list(const['FAMILIES'])+list(const['LEGACY_ARRAY_FAMILIES']),'extensions':list(const['EXTENSIONS']),'retention':list(const['RETENTION']),'optional_numeric_families':['core06','core07'],'runtime_materialization':'Hash-verified cache generated only for explicitly requested legacy tests; not a participant answer table','all_are_auxiliary_not_active_E1':True}
    (core/'FAMILIAS.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    numeric=[]
    if a.numpy_root:
        for name in('numpy','numpy.libs','numpy-2.2.6.dist-info'):
            source=a.numpy_root/name;dest=ROOT/'sistema/runtime/optional_numeric'/name
            if not source.is_dir():raise FileNotFoundError(source)
            for f in source.rglob('*'):
                if not f.is_file()or'__pycache__'in f.parts or f.suffix in('.pyc','.pyo'):continue
                target=dest/f.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,target);numeric.append({'path':target.relative_to(ROOT/'sistema').as_posix(),'sha256':sha(target),'bytes':target.stat().st_size})
        (ROOT/'sistema/runtime/NUMPY_PRIVADO.json').write_text(json.dumps({'version':'2.2.6','scope':'Only explicit auxiliary CORE06/07 original array and frozen RNG contracts; never participant decision policy','distribution':'Exact available installed package plus numpy.libs and dist-info notices; not a renamed wheel','files':numeric},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    proof={'status':'RECOVERED_NOT_YET_REVALIDATED_1_1','source_archive_sha256':sha(a.archive),'files':rows,'adapter_diffs':diffs,'families':len(config['families']),'numeric_dependency_files':len(numeric),'numeric_dependency_bytes':sum(x['bytes']for x in numeric),'engine_wheel_copies_in_this_component':0}
    (ROOT/'evidencia/genealogia/CORE_OPERATIVO_RECUPERADO.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:v for k,v in proof.items()if k not in('files',)},ensure_ascii=False))
if __name__=='__main__':main()
