from pathlib import Path,PurePosixPath
import zipfile,json,gzip,hashlib,importlib.util,base64,shutil
ROOT=Path(r'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests\documantacion vital\DEE thinking')
WORK=Path(__file__).resolve().parent
ARCHIVE=ROOT/'casos practicos/trabajo_codex/CPC9/runs/RUN_20261019_165651/core/final/DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip'
ORIGINAL=WORK/'original_core'
STAGE=WORK/'stage'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ORIGINAL.mkdir(exist_ok=True);STAGE.mkdir(exist_ok=True)
with zipfile.ZipFile(ARCHIVE) as z:
    assert z.testzip() is None
    for n in z.namelist():
        q=PurePosixPath(n)
        assert q.parts[0]=='DEE_COGNITIVE_CORE' and '..' not in q.parts and ':' not in n
        if n.endswith('/'):continue
        dst=ORIGINAL/Path(*q.parts[1:]);dst.parent.mkdir(parents=True,exist_ok=True)
        value=z.read(n)
        if not dst.exists():dst.write_bytes(value)
        assert dst.read_bytes()==value
spec=importlib.util.spec_from_file_location('recovery_constants',ORIGINAL/'reproduccion/desde_cero.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
index=json.loads((ORIGINAL/'documentacion/INDICE_MIEMBROS.json').read_text(encoding='utf8'))
chosen={n:r for n,r in index['paths'].items() if any(n.startswith(p) for p in mod.PREFIXES)}
needed={r['sha256'] for r in chosen.values()}
store=STAGE/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz';store.parent.mkdir(parents=True,exist_ok=True)
with gzip.open(ORIGINAL/'mecanismos/RECUPERACION_POR_HASH.jsonl.gz','rt',encoding='ascii') as src,store.open('wb') as raw:
    with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,compresslevel=9) as dst:
        for line in src:
            row=json.loads(line)
            if row['sha256'] in needed:dst.write(line.encode('ascii'))
index.update(paths=chosen,content_store_sha256=sha(store),consolidation='Exact selected blobs; unused historical paths excluded. Files materialize only under new output, never mutate archive.')
dest=STAGE/'documentacion/INDICE_MIEMBROS.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(index,ensure_ascii=False,separators=(',',':')),encoding='utf8')
keep=['scripts/materializar.py','reproduccion/worker_core.py','reproduccion/worker_extension.py','reproduccion/worker_initial_cpc8.py','reproduccion/worker_legacy_core.py','reproduccion/worker_retention.py','reproduccion/worker_social.py','reproduccion/recalcular_observadores.py','configuraciones/OBSERVADORES_PRIMARIOS_CONGELADOS.json','configuraciones/RECUPERACION_EXTENSION_CONGELADA.json','verificaciones/CORE06_PRIMARY_TRANSITIONS.json','verificaciones/CORE07_PRIMARY_TRANSITIONS.json']
for rel in keep:
    dst=STAGE/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ORIGINAL/rel,dst)
print(json.dumps({'original_paths':len(json.loads((ORIGINAL/'documentacion/INDICE_MIEMBROS.json').read_text(encoding='utf8'))['paths']),'chosen_paths':len(chosen),'unique_blobs':len(needed),'store_bytes':store.stat().st_size,'archive_sha256':sha(ARCHIVE),'families':list(mod.FAMILIES)+list(mod.LEGACY_ARRAY_FAMILIES)},ensure_ascii=False))
