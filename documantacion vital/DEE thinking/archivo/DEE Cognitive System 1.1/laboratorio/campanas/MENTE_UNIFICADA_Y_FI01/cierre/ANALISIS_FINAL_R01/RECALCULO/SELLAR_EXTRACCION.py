"""Sellado de extracción científica A+B; no importa DEE ni avanza mundos."""
from __future__ import annotations
import argparse, hashlib, json, shutil, zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
LAB=HERE.parent
ROOT=LAB.parents[2]
EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01'

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--stage',type=Path,required=True);ap.add_argument('--zip',type=Path,required=True);a=ap.parse_args()
    plan=json.loads(a.plan.read_text(encoding='utf-8'))
    assert plan['status']=='CLOSED_APPROVED_FOR_PACKAGING'
    if a.stage.exists() or a.zip.exists():raise FileExistsError('Choose a fresh sealed revision; never overwrite')
    a.stage.mkdir(parents=True);index=[];omitted=[]
    def add(src,rel,kind='original_bytes'):
        src=Path(src);rel=Path(rel)
        assert src.is_file() and not rel.is_absolute() and '..'not in rel.parts
        if src.name.endswith('.deetsnap.gz') or src.suffix.lower() in ('.whl','.pyd','.dll','.exe','.lib','.obj','.zip'):
            raise ValueError('Analysis plan accidentally includes an operational world/engine/archive; preserve it locally and index its exact omission instead: '+str(src))
        dst=a.stage/rel
        if dst.exists():
            assert sha(src)==sha(dst),'Destination collision with differing bytes'
            return
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
        assert sha(src)==sha(dst)
        index.append({'included':rel.as_posix(),'source':str(src.resolve()),'sha256':sha(src),'bytes':src.stat().st_size,'kind':kind})
    for item in plan['files']:add(item['source'],item['to'],item.get('kind','original_bytes'))
    for item in plan['trees']:
        source=Path(item['source']);assert source.is_dir()
        for src in sorted(source.rglob('*')):
            if src.is_file() and '__pycache__'not in src.parts:
                add(src,Path(item['to'])/src.relative_to(source))
    # All primary root operations, including failed instrument variants.
    for src in sorted(EV.glob('*.json.gz')):add(src,Path('TRAYECTORIA_MAIN')/src.name)
    for src in sorted(EV.glob('RECALCULO*.json')):add(src,Path('TRAYECTORIA_MAIN')/src.name)
    for src in sorted(LAB.glob('*')):
        if src.is_file() and src.suffix in('.py','.json') and src.name!='PLAN_PAQUETE.json':add(src,Path('CODIGO_MAIN')/src.name)
    # Preserve every exact executed source revision without nine redundant libraries.
    revisions={};objects={}
    for revision in sorted((EV/'codigo_ejecutado').iterdir()):
        if not revision.is_dir():continue
        mapping={}
        for src in sorted(revision.rglob('*')):
            if not src.is_file():continue
            digest=sha(src);mapping[src.relative_to(revision).as_posix()]={'sha256':digest,'bytes':src.stat().st_size}
            objects.setdefault(digest,src)
        revisions[revision.name]=mapping
    for digest,src in objects.items():add(src,Path('CODIGO_EJECUTADO/objetos')/digest)
    (a.stage/'CODIGO_EJECUTADO/REVISIONES.json').write_text(json.dumps(revisions,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Deep worlds remain locally; never call this analysis an operational backup.
    for directory in plan.get('omitted_trees',[]):
        source=Path(directory['source']);assert source.is_dir()
        for src in sorted(source.rglob('*')):
            if src.is_file() and '__pycache__'not in src.parts:
                omitted.append({'source':str(src.resolve()),'bytes':src.stat().st_size,'sha256':sha(src),'reason':directory['reason']})
    for item in plan.get('omitted_files',[]):
        src=Path(item['source']);assert src.is_file()
        omitted.append({'source':str(src.resolve()),'bytes':src.stat().st_size,'sha256':sha(src),'reason':item['reason']})
    (a.stage/'INDICE_FUENTES_Y_OMISIONES.json').write_text(json.dumps({'scope':'Scientific analysis, NOT full life continuation backup','included_original_sources':index,'omitted':omitted,'declared_limits':plan['declared_limits']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    manifest=[]
    for src in sorted(a.stage.rglob('*')):
        if src.is_file():manifest.append({'path':src.relative_to(a.stage).as_posix(),'bytes':src.stat().st_size,'sha256':sha(src)})
    (a.stage/'MANIFIESTO_HASHES.json').write_text(json.dumps({'members':manifest,'self_hash_excluded':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    a.zip.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.zip,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for src in sorted(a.stage.rglob('*')):
            if src.is_file():z.write(src,src.relative_to(a.stage).as_posix())
    assert a.zip.stat().st_size<16000000,'Keep this candidate unpublished; revise representation without dropping counterexamples'
    with zipfile.ZipFile(a.zip)as z:
        assert z.testzip()is None
        for m in manifest:assert hashlib.sha256(z.read(m['path'])).hexdigest()==m['sha256']
    report={'zip':str(a.zip.resolve()),'bytes':a.zip.stat().st_size,'sha256':sha(a.zip),'files':len(manifest)+1,'expanded_bytes':sum(x['bytes']for x in manifest)+(a.stage/'MANIFIESTO_HASHES.json').stat().st_size,'native_ticks':0,'crc_and_members_verified':True,'source_files_exact':len(index),'source_revision_count':len(revisions),'deduplicated_source_objects':len(objects)}
    reportpath=a.zip.with_suffix('.SELLADO_EXTERNO.json');reportpath.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=True))
if __name__=='__main__':main()
