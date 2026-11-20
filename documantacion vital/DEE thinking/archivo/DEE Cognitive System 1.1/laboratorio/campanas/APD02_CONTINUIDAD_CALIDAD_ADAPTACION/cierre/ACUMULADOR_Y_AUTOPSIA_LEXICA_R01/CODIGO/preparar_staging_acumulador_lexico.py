"""Lossless compact scientific export of closed owned fronts; zero ticks."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2]
EV=ROOT/'evidencia/campanas/APD02_CONTINUIDAD_CALIDAD_ADAPTACION'
OUT=LAB/'cierre/ACUMULADOR_Y_AUTOPSIA_LEXICA_R01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8')as f:json.dump(x,f,ensure_ascii=False,indent=2)
def copy(src,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():raise FileExistsError(dest)
    shutil.copyfile(src,dest)
def main():
    if OUT.exists():raise FileExistsError('Preserve prior export')
    OUT.mkdir(parents=True);omitted=[]
    for run in('R01','R02'):
        source=EV/'acumulador'/run
        for p in sorted(source.iterdir()):
            if p.suffixes[-2:]==['.deetsnap','.gz']:
                omitted.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'reason':'Complete diagnostic snapshot retained locally; compact analysis is not an operational backup'})
            elif p.is_file():copy(p,OUT/'EVIDENCIA/ACUMULADOR'/run/p.name)
    for p in sorted((EV/'LENGUAJE_R02').rglob('*')):
        if not p.is_file():continue
        if p.name.endswith('.deetsnap.gz'):
            omitted.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'reason':'Complete native diagnostic state retained locally'})
        else:copy(p,OUT/'EVIDENCIA/LEXICO'/p.relative_to(EV/'LENGUAJE_R02'))
    extras=[(HERE/'recalcular_acumulador_r01_r02.py','CODIGO/recalcular_acumulador_r01_r02.py'),
        (LAB/'lenguaje/recalcular_consulta_r02.py','CODIGO/recalcular_consulta_r02.py'),
        (LAB/'lenguaje/recalcular_consulta_r02_R00_INSTRUMENTAL.py','CODIGO/recalcular_consulta_r02_R00_INSTRUMENTAL.py'),
        (Path(__file__),'CODIGO/preparar_staging_acumulador_lexico.py'),
        (HERE/'supervisar_acumulador_r01.py','CODIGO/supervisar_acumulador_r01.py'),
        (HERE/'supervisar_acumulador_r02.py','CODIGO/supervisar_acumulador_r02.py'),
        (LAB/'lenguaje/supervisar_consulta_r02.py','CODIGO/supervisar_consulta_r02.py'),
        (HERE/'RESULTADOS_ACUMULADOR_R01_R02.md','RESULTADOS_ACUMULADOR_R01_R02.md'),
        (LAB/'lenguaje/RESULTADOS_CONSULTA_R02.md','RESULTADOS_CONSULTA_R02.md'),
        (EV/'acumulador/RECALCULO_R01_R02_R2.json','REFERENCIAS/ACUMULADOR_R2.json'),
        (EV/'LENGUAJE_R02_RECALCULO.json','REFERENCIAS/LEXICO_R02.json')]
    for src,dest in extras:copy(src,OUT/dest)
    for p in sorted((EV/'acumulador').glob('R0[12]_*.txt')):copy(p,OUT/'SUPERVISION/ACUMULADOR'/p.name)
    for p in sorted((EV/'acumulador').glob('R0[12]_SUPERVISION.json')):copy(p,OUT/'SUPERVISION/ACUMULADOR'/p.name)
    for name in('LENGUAJE_R02_STDOUT.txt','LENGUAJE_R02_STDERR.txt','LENGUAJE_R02_SUPERVISION.json'):copy(EV/name,OUT/'SUPERVISION/LEXICO'/name)
    cases=[{'script':'CODIGO/recalcular_acumulador_r01_r02.py','args':['--evidence','EVIDENCIA/ACUMULADOR'],'reference':'REFERENCIAS/ACUMULADOR_R2.json'},
        {'script':'CODIGO/recalcular_consulta_r02.py','args':['--evidence','EVIDENCIA/LEXICO'],'reference':'REFERENCIAS/LEXICO_R02.json'}]
    write(OUT/'PLAN_RECALCULO.json',{'cases':cases,'all_recalculations_zero_ticks':True,'no_engine_or_snapshots_required':True})
    proof=[]
    with tempfile.TemporaryDirectory(prefix='apd02_compact_n0_')as temp:
        for i,c in enumerate(cases):
            generated=Path(temp)/f'case{i}.json'
            command=[sys.executable,'-I','-B','-X','utf8',c['script'],*c['args'],'--output',str(generated)]
            p=subprocess.run(command,cwd=OUT,capture_output=True,text=True,encoding='utf8',timeout=50)
            reference=OUT/c['reference'];equal=p.returncode==0 and generated.read_bytes()==reference.read_bytes()
            proof.append({'case':i,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'reference_sha256':sha(reference),
                'generated_sha256':sha(generated)if generated.exists()else None,'byte_identical':equal})
            if not equal:raise AssertionError(proof[-1])
    write(OUT/'PRUEBA_PORTABLE.json',{'new_native_ticks':0,'engine_imported':False,'cases':proof})
    write(OUT/'INDICE_OMISIONES.json',{'omitted':omitted,'omitted_snapshot_bytes':sum(x['bytes']for x in omitted),
        'scope':'Only our closed accumulator R01/R02 and lexical query autopsy R02. Root lexical acquisition R01 and quality peer review remain separate.',
        'instrumental_error':'The initial lexical archive decoder accepted int only and rejected exact decimal RAW strings. Preserved R00 source; corrected parser; no native rerun.'})
    files=[{'path':str(p.relative_to(OUT)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(OUT.rglob('*'))if p.is_file()]
    write(OUT/'MANIFIESTO.json',{'members':files,'bytes':sum(x['bytes']for x in files),'self_excluded':True})
    print(json.dumps({'stage':str(OUT),'members_excluding_manifest':len(files),'bytes':sum(x['bytes']for x in files),'omitted':len(omitted),'proof':proof},ensure_ascii=False))
if __name__=='__main__':main()
