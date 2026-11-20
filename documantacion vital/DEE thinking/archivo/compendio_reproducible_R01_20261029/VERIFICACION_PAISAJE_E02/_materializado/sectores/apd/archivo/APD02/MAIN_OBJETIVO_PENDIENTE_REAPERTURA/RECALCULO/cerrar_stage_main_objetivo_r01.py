"""Seal the CLOSED archived goal audit; no native imports, actors, or live SQL."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    with p.open('x',encoding='utf8')as f:json.dump(x,f,ensure_ascii=False,sort_keys=True,indent=2)
def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',type=Path,required=True);a=p.parse_args();stage=a.stage.resolve()
    if (stage/'MANIFIESTO.json').exists():raise FileExistsError('Never reseal an existing stage')
    reference=stage/'REFERENCIA_MAIN_OBJETIVO_R02.json';result=json.loads(reference.read_text(encoding='utf8'))
    if result['issues']or result['new_native_ticks']or result['engine_imported']:raise ValueError('Cannot seal a failed or nonzero-tick audit')
    plan={'cases':[{'script':'RECALCULO/recalcular_main_objetivo_r01.py','args':['--evidence','EVIDENCIA'],'reference':reference.name}],
          'scope':'Archived recalculate only; extraction script requires named local complete sources and is not the portable replay entrypoint.'}
    write(stage/'PLAN_RECALCULO.json',plan)
    with tempfile.TemporaryDirectory(prefix='apd02_goal_portable_')as temp:
        dest=Path(temp)/'copied';shutil.copytree(stage,dest)
        cp=subprocess.run([sys.executable,'-I','-B','-X','utf8','RECALCULO/recalcular_main_objetivo_r01.py','--evidence','EVIDENCIA','--output','PORTABLE_RESULT.json'],cwd=dest,capture_output=True,text=True,encoding='utf8',timeout=45)
        calculated=dest/'PORTABLE_RESULT.json'
        proof={'schema':'APD02.archived_main_goal.portable.R01','copied_to_different_short_location':True,'returncode':cp.returncode,
               'reference_sha256':sha(reference),'calculated_sha256':sha(calculated)if calculated.exists()else None,
               'byte_identical':calculated.exists()and calculated.read_bytes()==reference.read_bytes(),'stdout':cp.stdout,'stderr':cp.stderr,
               'new_native_ticks':0,'engine_imported':False,'no_live_SQLite':True}
        write(stage/'PRUEBA_PORTABLE.json',proof)
        if cp.returncode or not proof['byte_identical']:raise ValueError('Portable calculation differs; preserve this failed stage')
    context=json.loads((stage/'EVIDENCIA/CONTEXTO_ARCHIVADO.json').read_text(encoding='utf8'))
    write(stage/'INDICE_OMISIONES.json',{'complete_native_snapshots_retained_locally':context['omitted_full_native'],
        'deep_local_material':'Complete paired exports, SQLite journals, outbox, historical native receipt ledgers and all previous campaign evidence remain in their local source locations.',
        'scope':'This analysis stage is not an operational backup; witnesses preserve full physical arrays and current protocol, not omitted historical ledgers.'})
    files=[]
    for f in sorted(stage.rglob('*')):
        if f.is_file():files.append({'file':f.relative_to(stage).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
    manifest={'schema':'APD02.closed_analysis_stage.R01','namespace':'MAIN_OBJETIVO_PENDIENTE_Y_REAPERTURA_R01','status':'CLOSED',
        'cases':plan['cases'],'member_count':len(files),'total_bytes':sum(f['bytes']for f in files),'members':files,
        'native_ticks_new':0,'authoritative_reference':reference.name,'older_references':'R01 and PRE_OLD_PANEL retained as instrumental genealogy, not additional samples.'}
    write(stage/'MANIFIESTO.json',manifest)
    print(json.dumps({'stage':str(stage),'members':len(files),'bytes':manifest['total_bytes'],'manifest_sha256':sha(stage/'MANIFIESTO.json'),'reference_sha256':sha(reference),'portable':proof},ensure_ascii=False))
if __name__=='__main__':main()
