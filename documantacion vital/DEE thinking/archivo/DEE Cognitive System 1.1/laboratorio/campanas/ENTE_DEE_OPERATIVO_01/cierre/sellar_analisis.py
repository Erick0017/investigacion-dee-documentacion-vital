"""Sella un análisis esencial; el hash del contenedor queda sólo fuera de él."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,tempfile,zipfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];STAGE=HERE/'PAQUETE_ANALISIS'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--verificacion-completa',required=True,type=Path);p.add_argument('--python',required=True,type=Path);p.add_argument('--colaborador',required=True,type=Path);a=p.parse_args()
    fullproof=a.verificacion_completa.resolve(strict=True)
    target=ROOT/'entregas/DEE_ENTE_OPERATIVO_01_ANALISIS.zip';candidate=target.with_suffix('.candidato.zip')
    if target.exists()or candidate.exists():raise FileExistsError('Sealed candidate preserved; choose a new explicit revision')
    assert target.resolve().is_relative_to((ROOT/'entregas').resolve())
    target.parent.mkdir(parents=True,exist_ok=True)
    sources={p.relative_to(STAGE).as_posix():p for p in STAGE.rglob('*')if p.is_file()}
    sources['VERIFICACION_PAQUETE_COMPLETO_EXTERNA.json']=fullproof
    sources['RECALCULO/verificar_analisis_final.py']=HERE/'verificar_analisis_final.py'
    # Compatibility location required by the preserved earlier export checker.
    sources['RECALCULO/resultados/RECALCULO_RESULTADOS.json']=STAGE/'RECALCULO/REFERENCIA_RESULTADOS.json'
    manifest={'schema':'EO01.analysis.members.v1','members':[],'self_hash_intentionally_absent':True,'analysis_is_not_full_native_backup':True}
    with zipfile.ZipFile(candidate,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for name,source in sorted(sources.items()):
            if name.startswith('/')or'..'in Path(name).parts:raise ValueError('Unsafe member')
            z.write(source,name)
            info=z.getinfo(name)
            manifest['members'].append({'path':name,'bytes':source.stat().st_size,'compressed_bytes':info.compress_size,'sha256':sha(source)})
        z.writestr('MANIFIESTO_HASHES.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    if candidate.stat().st_size>=16000000:raise ValueError('Strict16,000,000byte analysis limit exceeded; candidate retained')
    extract=Path(tempfile.mkdtemp(prefix='EO01-analisis-final-')).resolve()
    with zipfile.ZipFile(candidate)as z:
        if z.testzip()is not None:raise ValueError('CRC failure')
        if len(z.namelist())!=len(set(z.namelist())):raise ValueError('Duplicate members')
        for row in manifest['members']:
            b=z.read(row['path']);assert len(b)==row['bytes']and hashlib.sha256(b).hexdigest()==row['sha256']
            if row['path'].endswith('.json.gz'):json.loads(gzip.decompress(b))
            elif row['path'].endswith('.json'):json.loads(b)
            elif row['path'].endswith(('.md','.py','.txt')):b.decode('utf8')
        z.extractall(extract)
    command=[str(a.python),'-I','-B','-X','utf8',str(extract/'RECALCULO/verificar_analisis_final.py'),'--prohibir-raiz',str(ROOT),'--prohibir-raiz',str(a.colaborador.resolve())]
    r=subprocess.run(command,cwd=extract,capture_output=True,text=True,encoding='utf8',timeout=240)
    worker=extract/'RECALCULADO_DESDE_ZIP/VERIFICACION_RECALCULO_DESDE_ZIP.json'
    if r.returncode or not worker.exists():raise RuntimeError('Exact ZIP recalculation failed: '+r.stdout+'\n'+r.stderr)
    proof=json.loads(worker.read_bytes());assert proof['byte_identical_to_closed_reference']and not proof['mismatches']
    before=sha(candidate);os.rename(candidate,target);assert sha(target)==before
    report={'schema':'EO01.analysis.final.external.v1','closed_utc':datetime.now(timezone.utc).isoformat(),'zip':str(target),'bytes':target.stat().st_size,'sha256':sha(target),'files':len(manifest['members'])+1,'strict_limit_bytes':16000000,'member_hashes_verified':True,'crc_verified':True,'text_json_gzip_readability_verified':True,'extracted_to':str(extract),'recalculation_command':command,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'archived_recalculation':proof,'full_distribution_verification_source':str(fullproof),'full_distribution_verification_sha256':sha(fullproof),'same_machine_not_second_computer':True,'no_engine_or_all_snapshots_in_analysis':True,'private_no_remote_upload':True}
    destination=ROOT/'entregas/VERIFICACION_ENTE_OPERATIVO_01_ANALISIS_EXTERNA.json'
    if destination.exists():raise FileExistsError('Prior external verification retained')
    destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
