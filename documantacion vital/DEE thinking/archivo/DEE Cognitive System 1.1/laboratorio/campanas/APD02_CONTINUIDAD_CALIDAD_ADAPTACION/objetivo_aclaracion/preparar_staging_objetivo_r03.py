"""Compact closed-goal export and clean-location archive recalculation."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2]
EV=ROOT/'evidencia/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION'
OUT=LAB/'cierre/OBJETIVO_ACLARACION_AUX_R03'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    with p.open('x',encoding='utf8')as f:json.dump(x,f,ensure_ascii=False,indent=2)
def copy(p,d):d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
def main():
    if OUT.exists():raise FileExistsError('Preserve any previous export')
    OUT.mkdir(parents=True);omissions=[]
    for p in sorted((EV/'OBJETIVO_NATIVO_R03').rglob('*')):
        if not p.is_file():continue
        if p.name.endswith('.deetsnap.gz'):
            omissions.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'reason':'Complete native diagnostic snapshot retained locally; not needed to recalculate exported observations/receipts/file effects'})
        else:copy(p,OUT/'EVIDENCIA'/p.relative_to(EV/'OBJETIVO_NATIVO_R03'))
    for name in('OBJETIVO_PURO_R01','OBJETIVO_RESTAURACION_PURA_R02'):
        for p in sorted((EV/name).rglob('*')):
            if p.is_file():copy(p,OUT/'PRUEBAS_PURAS'/name/p.relative_to(EV/name))
    for name in('entorno_objetivo_aclaracion_r01.py','aparato_objetivo_aclaracion_r01.py','CONTRATO_OBJETIVO_ACLARACION_R01.json',
        'entorno_objetivo_aclaracion_r02.py','aparato_objetivo_aclaracion_r02.py','CONTRATO_OBJETIVO_ACLARACION_R02.json',
        'probar_aparato_puro_r01.py','probar_restauracion_pura_r02.py','recalcular_objetivo_r03.py',Path(__file__).name):copy(HERE/name,OUT/'CODIGO'/name)
    copy(HERE/'RESULTADOS_OBJETIVO_NATIVO_R03.md',OUT/'RESULTADOS_OBJETIVO_NATIVO_R03.md')
    copy(EV/'OBJETIVO_NATIVO_R03_RECALCULO.json',OUT/'REFERENCIA_OBJETIVO_R03.json')
    plan={'cases':[{'script':'CODIGO/recalcular_objetivo_r03.py','args':['--evidence','EVIDENCIA'],'reference':'REFERENCIA_OBJETIVO_R03.json'}],
        'all_recalculations_zero_ticks':True,'no_engine_or_local_snapshots_required':True}
    write(OUT/'PLAN_RECALCULO.json',plan)
    with tempfile.TemporaryDirectory(prefix='apd02_goal_archive_')as tmp:
        portable=Path(tmp)/'export';shutil.copytree(OUT,portable);result=Path(tmp)/'audit.json'
        argv=[sys.executable,'-I','-B','-X','utf8','CODIGO/recalcular_objetivo_r03.py','--evidence','EVIDENCIA','--output',str(result)]
        p=subprocess.run(argv,cwd=portable,capture_output=True,text=True,encoding='utf8',timeout=50)
        identical=p.returncode==0 and result.read_bytes()==(OUT/'REFERENCIA_OBJETIVO_R03.json').read_bytes()
        proof={'new_native_ticks':0,'engine_imported':False,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,
            'reference_sha256':sha(OUT/'REFERENCIA_OBJETIVO_R03.json'),'generated_sha256':sha(result)if result.exists()else None,'byte_identical':identical}
        write(OUT/'PRUEBA_PORTABLE.json',proof)
        if not identical:raise AssertionError(proof)
    write(OUT/'INDICE_OMISIONES.json',{'omitted':omissions,'omitted_bytes':sum(x['bytes']for x in omissions),
        'scope':'Four deterministic AUX physical branches with goal-world state. No MAIN experience transfer or full SQLite/service backup; complete snapshots remain local.'})
    members=[{'path':str(p.relative_to(OUT)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(OUT.rglob('*'))if p.is_file()]
    write(OUT/'MANIFIESTO.json',{'members':members,'bytes':sum(x['bytes']for x in members),'self_excluded':True})
    print(json.dumps({'stage':str(OUT),'members_excluding_manifest':len(members),'bytes':sum(x['bytes']for x in members),'omitted_snapshots':len(omissions),'portable':identical},ensure_ascii=False))
if __name__=='__main__':main()
