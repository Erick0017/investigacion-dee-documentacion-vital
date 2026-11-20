"""Lossless compact evidence staging; no native imports, ticks or life edits."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parents[2]
EV=ROOT/'evidencia/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def new_json(p,z):
    with p.open('xb')as f:f.write((json.dumps(z,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8'))
def main():
    stage=HERE/'ANALISIS_LEXICO_R01_R02_R2'
    # Windows CreateProcess rejects the original long cwd (WinError267).
    # This short independent test location remains inside the authorized workspace.
    test=ROOT.parents[4]/'_APD01_LEX_PORTABLE_R02_20261025'
    if stage.exists()or test.exists():raise FileExistsError('Preserve previous staging and test')
    stage.mkdir();rows=[]
    def copy(source,relative):
        target=stage/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        rows.append({'included':relative.replace('\\','/'),'source':str(source),'bytes':source.stat().st_size,'source_sha256':sha(source),'included_sha256':sha(target)})
    for revision in('R01','R02'):
        source=EV/'lenguaje'/('APD01_LEX_'+revision)
        for p in sorted(source.iterdir()):
            if p.is_file()and p.name!='RECALCULO.json':copy(p,'EVIDENCIA/'+revision+'/'+p.name)
        copy(source/'RECALCULO.json','REFERENCIAS/'+revision+'.json')
        copy(HERE/('recalcular_lexico_'+revision.lower()+'.py'),'RECALCULO/recalcular_lexico_'+revision.lower()+'.py')
        copy(HERE/('RESULTADOS_LEXICO_'+revision+'.md'),'RESULTADOS_LEXICO_'+revision+'.md')
    for name in('PROTOCOLO_LENGUAJE_R01.md','PREFLIGHT_GEOMETRIA_R01.json','PREFLIGHT_SEGUNDO_HUB_R02.json','preflight_geometria_r01.py','preflight_segundo_hub_r02.py'):
        copy(HERE/name,'PREPARACION/'+name)
    for name in('LEX_R01_CUATRO_HISTORIAS.json.gz','LEX_R02_SEGUNDO_HUB.json.gz'):copy(EV/name,'SUPERVISION/'+name)
    cases=[{'case':rev,'script':'RECALCULO/recalcular_lexico_'+rev.lower()+'.py',
            'script_sha256':sha(stage/'RECALCULO'/('recalcular_lexico_'+rev.lower()+'.py')),
            'args':['--primarios','EVIDENCIA/'+rev,'--salida','RECALCULADO_'+rev+'.json'],
            'reference':'REFERENCIAS/'+rev+'.json','reference_sha256':sha(stage/'REFERENCIAS'/(rev+'.json'))}for rev in('R01','R02')]
    new_json(stage/'PLAN_RECALCULO.json',{'cases':cases,'new_native_ticks':0,'stdlib_only':True})
    lives=[]
    for rev in('R01','R02'):
        for case in('paired','omitted','reversed','unpaired'):
            path=ROOT/'sistema/estado/vidas'/('APD01_LEX_'+rev+'_'+case)/'VIDA.json'
            rec=json.loads(path.read_bytes());snapshot=ROOT/'sistema'/rec['snapshot']
            lives.append({'life_id':rec['life_id'],'tick':rec['physical']['tick'],'snapshot_local':str(snapshot),'snapshot_sha256':sha(snapshot),
                          'VIDA_local':str(path),'VIDA_sha256':sha(path),'omission':'Whole operational state retained locally, not required for archived recalculation; exported arrays do not replace it.'})
    new_json(stage/'INDICE_FUENTES_Y_OMISIONES.json',{'included':rows,'operational_snapshots_omitted':lives,
        'scope':'Eight full native histories are not independent biographies; R02 shares the successful R01 prefix. No snapshots or motor distributed in this analysis component.',
        'deep_primary_coverage':'All four R01 and all four R02 positive/negative compact primaries included without field filtering; exact sources and receipts are preserved.'})
    shutil.copytree(stage,test)
    validations=[]
    for case in cases:
        argv=[sys.executable,'-I','-B',case['script'],*case['args']]
        result=subprocess.run(argv,cwd=test,capture_output=True,text=True,encoding='utf8',timeout=60)
        generated=test/('RECALCULADO_'+case['case']+'.json');reference=test/case['reference']
        same=result.returncode==0 and generated.exists()and generated.read_bytes()==reference.read_bytes()
        validations.append({'case':case['case'],'argv':argv,'returncode':result.returncode,
            'byte_identical_to_reference':same,'generated_sha256':sha(generated)if generated.exists()else None,
            'reference_sha256':sha(reference),'stderr':result.stderr})
        if not same:raise AssertionError('Portable recalculation failed: '+case['case'])
    new_json(stage/'PRUEBA_PORTABLE.json',{'cases':validations,'native_ticks_executed':0,'temporary_independent_location':str(test),'no_S_or_historical_source_imports':True,
        'prior_instrumental_error':'First staging CreateProcess cwd exceeded Windows practical path; WinError267 before any recalculation process. Source and incomplete staging preserved, no physics repeated.'})
    manifest=[{'path':p.relative_to(stage).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(stage.rglob('*'))if p.is_file()]
    new_json(stage/'MANIFIESTO.json',{'members':manifest,'self_hash_omitted':True})
    print(json.dumps({'stage':str(stage),'files':len(manifest)+1,'expanded_bytes':sum(p.stat().st_size for p in stage.rglob('*')if p.is_file()),'portable_cases':validations},ensure_ascii=False))
if __name__=='__main__':main()
