"""Copy exact closed Full proof bytes and recalculate without Native."""
import argparse,gzip,hashlib,importlib.util,json,shutil,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def write(path,value):
    with Path(path).open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
def load(path):
    s=importlib.util.spec_from_file_location('portable_full_N0',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def export(root,proof,outer,destination,bat_help=None):
    root=Path(root).resolve(strict=True);proof=Path(proof).resolve(strict=True);outer=Path(outer).resolve(strict=True);destination=Path(destination).resolve();report=read(outer)
    if destination.exists():raise FileExistsError('A previous scientific cut is preserved')
    if report.get('execution',{}).get('resources',{}).get('job_active_processes')!=0:raise ValueError('Wait for the actual owned proof job to close; do not copy a live proof')
    result=read(proof/'RESULTADOS_FULL_APD03.json');destination.mkdir(parents=True,exist_ok=False);provenance=[]
    def copy(source,relative,compress=False):
        source=Path(source);before=sha(source);target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True)
        if compress:
            with target.open('xb')as f:f.write(gzip.compress(source.read_bytes(),mtime=0))
            if hashlib.sha256(gzip.decompress(target.read_bytes())).hexdigest()!=before:raise ValueError('Lossless proof compression mismatch')
        else:shutil.copyfile(source,target)
        if sha(source)!=before:raise ValueError('Closed proof source changed while copying')
        provenance.append({'source':str(source),'source_bytes':source.stat().st_size,'source_sha256':before,'file':relative,'lossless_gzip':compress})
    copy(outer,'VERIFICACION_FULL_APD03_R01.json')
    for stream in ('PROOF_STDOUT.txt','PROOF_STDERR.txt'):
        copy(root.parent/stream,'EVIDENCIA/OUTER_'+stream+'.gz',True)
    if bat_help is not None:
        bat_report=read(bat_help)
        if bat_report.get('new_native_ticks')!=0 or bat_report.get('new_lives')!=0:raise ValueError('Help report is not the explicit N0 check')
        copy(bat_help,'EVIDENCIA/VERIFICACION_BAT_HELP_APD03_R01.json')
        copy(HERE/'verificar_bat_help_apd03_n0.py','RECALCULO/verificar_bat_help_apd03_n0.py')
    argv=report['execution']['argv'];protocol=Path(argv[argv.index('--protocolo')+1]).resolve(strict=True)
    if not protocol.is_relative_to(root)or sha(protocol)!=report['protocol_sha256']:raise ValueError('Actual originally passed protocol bytes differ')
    copy(protocol,'EVIDENCIA/PROTOCOLO_ORIGINAL_BYTES.json')
    for path in sorted(proof.rglob('*')):
        if not path.is_file():continue
        relative=path.relative_to(proof).as_posix();compress=path.suffix in('.json','.jsonl','.txt')and relative!='PROTOCOLO_CONGELADO.json'and not relative.startswith('ARTEFACTOS/')
        copy(path,'EVIDENCIA/'+relative+('.gz'if compress else''),compress)
    for row in result['sources']:
        source=root/row['file']
        if source.stat().st_size!=row['bytes']or sha(source)!=row['sha256']:raise ValueError('Executed source no longer matches the frozen proof')
        copy(source,'CODIGO_EJECUTADO/'+row['file'])
    helper=root/'actualizaciones/probar_full_apd03_entrada.py'
    if sha(helper)!=report['execution']['included_helper_sha256']:raise ValueError('Included proof helper changed')
    copy(helper,'CODIGO_EJECUTADO/probar_full_apd03_entrada.py')
    for name in('recalcular_full_apd03_n0.py','exportar_prueba_full_apd03_n0.py'):copy(HERE/name,'RECALCULO/'+name)
    omitted=[]
    life=result['one_life_not_MAIN']
    for folder in(root/'trabajo_personal/estado/checkpoints',root/'trabajo_personal/estado/vidas'/life,root/'trabajo_personal/entrada_sencilla/vidas'/life):
        for path in sorted(folder.rglob('*')):
            if path.is_file():omitted.append({'source':str(path),'bytes':path.stat().st_size,'sha256':sha(path),'reason':'Complete local operational state retained; analysis is not a restorable backup. Exact session evidence is separately included.'})
    write(destination/'ORIGENES_Y_OMISIONES.json',{'included':provenance,'omitted_operational':omitted,'engine_and_WHL_not_included':True,'no_native_ticks':0,'exact_archive_sha256':report['zip_sha256']})
    audit=load(destination/'RECALCULO/recalcular_full_apd03_n0.py');r=audit.recalculate(destination);write(destination/'RECALCULO_FULL.json',r)
    with tempfile.TemporaryDirectory(prefix='apd03-full-recalc-')as t:
        other=Path(t)/'otras_fuentes';shutil.copytree(destination,other);second=load(other/'RECALCULO/recalcular_full_apd03_n0.py').recalculate(other)
        if r!=second:raise ValueError('Different-directory archived recalculation differs')
    write(destination/'PRUEBA_PORTABLE.json',{'new_native_ticks':0,'new_provider_calls':0,'checks':r['checks'],'issues':r['issues'],'identical_recalculated_JSON_after_copy_to_other_root':True,'not_a_new_Native_reproduction':True})
    write(destination/'PLAN_RECALCULO.json',{'jobs':[{'name':'Exact Full archived proof; no Native','script':'RECALCULO/recalcular_full_apd03_n0.py','args':['--evidencia','.','--salida','{output}'],'base':'.','reference':'RECALCULO_FULL.json'}]})
    members=[{'file':p.relative_to(destination).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(destination.rglob('*'))if p.is_file()]
    write(destination/'MANIFIESTO.json',{'members':members,'own_hash_excluded':True,'scope':'Analysis of an exact Full Native proof on the same computer. No engine or operational backup; preserves positive and negative proof records.'})
    return {'files':len(members)+1,'bytes_without_own_manifest':sum(r['bytes']for r in members),'manifest_sha256':sha(destination/'MANIFIESTO.json'),'recalculated_checks':r['checks'],'issues':r['issues'],'new_native_ticks_in_export':0}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--raiz-extraida',required=True,type=Path);p.add_argument('--prueba',required=True,type=Path);p.add_argument('--verificacion',required=True,type=Path);p.add_argument('--salida',required=True,type=Path);p.add_argument('--ayuda-bat',type=Path);a=p.parse_args();print(json.dumps(export(a.raiz_extraida,a.prueba,a.verificacion,a.salida,a.ayuda_bat),ensure_ascii=False))
if __name__=='__main__':main()
