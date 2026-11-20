"""Seal existing lexical AUX successes/adverses, stdlib only, zero Native."""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as stream:
        for block in iter(lambda:stream.read(1048576),b''):h.update(block)
    return h.hexdigest()


def emit(path,body):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8')as stream:
        json.dump(body,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab',required=True,type=Path)
    parser.add_argument('--evidence-root',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path);args=parser.parse_args()
    if args.out.exists():raise FileExistsError('New closed stage required; no replacing previous bytes')
    args.out.mkdir(parents=True)
    metric_path=args.lab/'recalcular_curvas_lexico_apd03_r01.py'
    spec=importlib.util.spec_from_file_location('curve_metric_closed',metric_path)
    metric=importlib.util.module_from_spec(spec);spec.loader.exec_module(metric)
    regenerated=[]
    for path in sorted((args.evidence_root/'CURVAS_LEXICO_AUX_R03').glob('ARM_*/RECALCULO.json')):
        primary=json.loads(gzip.decompress(path.with_name('PRIMARIO.json.gz').read_bytes()))
        data=(json.dumps(metric.recalculate(primary),ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
        if path.read_bytes()!=data:raise ValueError('An excluded metric report is not byte-regenerable')
        regenerated.append({'source':str(path),'sha256':sha(path),'bytes':len(data),'byte_regenerated_before_exclusion':True})
    selected=[];omitted=[];before={}
    for case in('CURVAS_LEXICO_AUX_R01','CURVAS_LEXICO_AUX_R02','CURVAS_LEXICO_AUX_R03'):
        source=args.evidence_root/case
        for path in sorted(source.rglob('*')):
            if not path.is_file():continue
            if path.is_symlink():raise ValueError('No linked originals')
            relative=path.relative_to(source)
            row={'source':str(path),'relative_path':relative.as_posix(),'bytes':path.stat().st_size,'sha256':sha(path)}
            before[str(path)]=row['sha256']
            if path.name.endswith('.deetsnap.gz')or path.name=='RECALCULO.json'or path.suffix=='.pyc'or'__pycache__'in path.parts:
                row['reason']='Complete physical/owner snapshot remains local; essential export is not a continuation backup'if path.name.endswith('.deetsnap.gz')else'Exact output regenerated before exclusion; no unique Native event removed'
                omitted.append(row);continue
            target=args.out/'EVIDENCIA'/case/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
            selected.append({**row,'file':target.relative_to(args.out).as_posix()})
    for name in('recalcular_curvas_completas_apd03_n0.py','recalcular_curvas_lexico_apd03_r01.py','observador_causal_retrospectivo_01.py'):
        target=args.out/'RECALCULO'/name;target.parent.mkdir(exist_ok=True)
        shutil.copyfile(args.lab/'recalculo'/name,target)
    extra_sources=('diagnosticar_prefijo_lexico_r02_n0.py','diagnosticar_origen_lexico_r03_n0.py',
        'lexico_generico_apd03_r01.py','lexico_generico_apd03_r02.py',
        'protocolo_curvas_lexico_apd03_r01.py','protocolo_curvas_lexico_apd03_r02.py',
        'ejecutar_curvas_lexico_apd03_r01.py','ejecutar_curvas_lexico_apd03_r02.py','ejecutar_curvas_lexico_apd03_r03.py')
    for name in extra_sources:
        target=args.out/'CODIGO_CIERRE'/name;target.parent.mkdir(exist_ok=True);shutil.copyfile(args.lab/name,target)
    shutil.copyfile(__file__,args.out/'CODIGO_CIERRE'/Path(__file__).name)
    doc=args.out/'INFORMES'/'HALLAZGO_CURVAS_LEXICO_APD03_R03.md';doc.parent.mkdir(exist_ok=True)
    shutil.copyfile(args.lab/doc.name,doc)
    reference=args.out/'REFERENCIAS'/'CURVAS_LEXICO.json';reference.parent.mkdir(exist_ok=True)
    command=[sys.executable,'-I','-B',str(args.out/'RECALCULO/recalcular_curvas_completas_apd03_n0.py'),
        '--evidence',str(args.out/'EVIDENCIA'),'--out',str(reference)]
    result=subprocess.run(command,cwd=tempfile.gettempdir(),capture_output=True,text=True,encoding='utf8',timeout=120)
    if result.returncode:
        emit(args.out/'FALLO_RECALCULO.json',{'command':command,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
        raise ValueError('Primary recalculation failed')
    calculated=json.loads(reference.read_bytes())
    if calculated['issues']:raise ValueError('Scientific discrepancies in primary recalculation')
    job={'name':'CURVAS_LEXICO_R01_R03','base':'.','script':'RECALCULO/recalcular_curvas_completas_apd03_n0.py',
        'args':['--evidence','EVIDENCIA','--out','{output}'],'reference':'REFERENCIAS/CURVAS_LEXICO.json'}
    emit(args.out/'PLAN_RECALCULO.json',{'jobs':[job]})
    emit(args.out/'INDICE_FUENTES_Y_OMISIONES.json',{'schema':'APD03.lexical_essential_index.v1',
        'selected_originals':selected,'omitted_originals':omitted,
        'selected_original_bytes':sum(row['bytes']for row in selected),
        'omitted_original_bytes':sum(row['bytes']for row in omitted),
        'regenerated_excluded_reports':regenerated,
        'scope':'All unique recorded events, successes, negatives, complete-source preflights and source revisions included. Complete Native snapshots remain local; K/metadata extraction has original hashes and code but is not a whole-state backup.'})
    for path,digest in before.items():
        if sha(path)!=digest:raise ValueError('Read-only closure changed an original')
    portable_root=Path(tempfile.mkdtemp(prefix='dee_apd03_curvas_'));portable=portable_root/'paquete'
    shutil.copytree(args.out,portable)
    actual=portable_root/'RECALCULADO.json'
    portable_command=[sys.executable,'-I','-B',str(portable/job['script']),'--evidence',str(portable/'EVIDENCIA'),'--out',str(actual)]
    run=subprocess.run(portable_command,cwd=portable_root,capture_output=True,text=True,encoding='utf8',timeout=120)
    identical=run.returncode==0 and actual.is_file()and actual.read_bytes()==reference.read_bytes()
    emit(args.out/'PRUEBA_PORTABLE.json',{'schema':'APD03.lexical_portable_stdlib.v1','location':str(portable_root),
        'jobs':[{'name':job['name'],'command':portable_command,'exit_code':run.returncode,
            'stdout':run.stdout,'stderr':run.stderr,'byte_identical':identical,
            'expected_sha256':sha(reference),'actual_sha256':sha(actual)if actual.is_file()else None}],
        'all_byte_identical':identical,'checks':calculated['checks'],'issues':len(calculated['issues']),
        'RAW':calculated['RAW_fields_checked'],'readers':calculated['common_reader_queries_redecoded'],
        'new_native_ticks':0,'scope':'Archived primary recalculation elsewhere, not Native reproduction, new learning or another computer.'})
    if not identical:raise ValueError('Portable exact-byte comparison failed')
    members=[{'file':path.relative_to(args.out).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path)}for path in sorted(args.out.rglob('*'))if path.is_file()]
    emit(args.out/'MANIFIESTO.json',{'schema':'APD03.closed_lexical_stage.v1','status':'CLOSED_RECALCULATED_PORTABLY_N0',
        'files':members,'files_count':len(members),'files_bytes':sum(row['bytes']for row in members),
        'self_reference_excluded':'MANIFIESTO.json','portable_jobs':1,'new_native_ticks_in_closure':0})
    print(json.dumps({'stage':str(args.out),'files':len(members)+1,'bytes_without_self':sum(row['bytes']for row in members),
        'manifest_sha256':sha(args.out/'MANIFIESTO.json'),'reference_sha256':sha(reference),
        'plan_sha256':sha(args.out/'PLAN_RECALCULO.json'),'all_byte_identical':True}))


if __name__=='__main__':main()
