"""Create one portable APD audit cut and include the lexical component once.

No native import, evolution, life mutation, installation or historical scan.
Only completed supervisor primaries and their named closed-source revisions.
"""
import argparse,gzip,hashlib,json,re,shutil,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema'
EV=ROOT/'evidencia/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def new_json(p,z):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write((json.dumps(z,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8'))
def walk(v):
    if isinstance(v,dict):
        yield v
        for k,x in v.items():
            if k not in('parent','operations','historical_parent'):yield from walk(x)
    elif isinstance(v,list):
        for x in v:yield from walk(x)
def main():
    p=argparse.ArgumentParser();p.add_argument('--corte',required=True);p.add_argument('--hasta',type=int,required=True)
    args=p.parse_args()
    if not re.fullmatch('[A-Za-z0-9_-]{1,40}',args.corte) or not 1<=args.hasta<=99:raise ValueError('Finite explicit cut required')
    stage=HERE/('ANALISIS_APD_'+args.corte);test=ROOT.parents[4]/('_APD01_PORTABLE_'+args.corte)
    if stage.exists()or test.exists():raise FileExistsError('Never overwrite an earlier audit cut')
    stage.mkdir();index=[];snapshot_index=[];code_index=[];artifacts_needed=set()
    def copy(source,relative):
        target=stage/relative;target.parent.mkdir(parents=True,exist_ok=True)
        before=sha(source);shutil.copyfile(source,target)
        if sha(source)!=before or sha(target)!=before:raise ValueError('Source changed during copy: '+str(source))
        index.append({'included':relative,'source':str(source),'bytes':target.stat().st_size,'sha256':before})
    sources=[p for p in sorted(EV.glob('P[0-9][0-9]_*.json.gz'))if int(p.name[1:3])<=args.hasta]
    critical=['sistema/capacidades/aritmetica_apd_01.py','sistema/capacidades/asistente_proposito_01.py',
        'sistema/capacidades/acumulador_adquirido_apd_01.py','sistema/capacidades/lexico_apd_01.py',
        'sistema/capacidades/lexico_apd_extendido_02.py','sistema/capacidades/mente_unificada_01.py',
        'sistema/capacidades/mente_acumulativa_r02.py','sistema/capacidades/percepcion_cruda_fi01.py',
        'sistema/capacidades/selector_acrecion_nativo.py','sistema/app/lives.py',
        'laboratorio/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/aritmetica/aritmetica_fi01_candidata.py',
        'laboratorio/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/lenguaje/lexico_extensible_r01.py',
        'laboratorio/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/lenguaje/lexico_extensible_r02.py']
    copied_code=set()
    for source in sources:
        copy(source,'PRIMARIOS/'+source.name);primary=read(source);result=primary.get('result',{})
        for node in walk(result):
            artifact=node.get('artifact')
            if isinstance(artifact,dict)and'sha256'in artifact and'name'in artifact:artifacts_needed.add((artifact['sha256'],artifact['name']))
        if isinstance(result,dict)and isinstance(result.get('INSTRUMENTO'),dict):
            ins=result['INSTRUMENTO'];life=ins.get('life_id');tick=ins.get('tick');digest=ins.get('snapshot_sha256')
            if life and tick is not None and digest:
                matching=[q for q in(SYSTEM/'estado/checkpoints').glob(life+'.T'+str(tick)+'.*.deetsnap.gz')if sha(q)==digest]
                snapshot_index.append({'primary':source.name,'life_id':life,'tick':tick,'snapshot_sha256':digest,
                    'matching_complete_local_snapshots':[str(q)for q in matching],
                    'omitted':'Whole operational state retained locally; compact analysis is not a continuation backup.'})
        revision=primary.get('code_revision_sha256');archive=EV/'codigo_ejecutado'/str(revision)
        wanted=list(critical)
        argv=primary.get('argv',[])
        for argument in argv:
            candidate=Path(argument)
            if candidate.suffix=='.py'and candidate.is_absolute():
                try:wanted.append(candidate.relative_to(ROOT).as_posix())
                except ValueError:pass
        signature=read(archive/'INDICE.json')if(archive/'INDICE.json').exists()else{}
        for relative in sorted(set(wanted)):
            archived=archive/relative
            if not archived.is_file():continue
            digest=sha(archived)
            if signature.get(relative)!=digest:raise ValueError('Exact archived source signature mismatch: '+relative)
            dest='FUENTES/'+digest+'/'+archived.name
            if dest not in copied_code:copy(archived,dest);copied_code.add(dest)
            code_index.append({'primary':source.name,'code_revision_sha256':revision,'original_relative':relative,'included':dest,'sha256':digest})
    artifact_root=SYSTEM/'estado/artefactos_apd'
    if artifact_root.exists():
        for source in sorted(artifact_root.rglob('*.bin')):
            digest=sha(source)
            if(digest,source.name)in artifacts_needed:copy(source,'ARTEFACTOS/'+source.relative_to(artifact_root).as_posix())
    copy(HERE/'recalcular_primarios_apd.py','RECALCULO/recalcular_primarios_apd.py')
    copy(HERE/'INFORME_PARCIAL_RECALCULO_P01_P15.md','INFORME_PARCIAL_RECALCULO_P01_P15.md')
    copy(HERE/'REFERENCIAS_MAIN_CORTE_R01.json','REFERENCIAS_PASIVAS_MAIN.json')
    lex_stage=LAB/'lenguaje/ANALISIS_LEXICO_R01_R02_R2'
    for source in sorted(lex_stage.rglob('*')):
        if source.is_file():copy(source,'LENGUAJE/'+source.relative_to(lex_stage).as_posix())
    (stage/'REFERENCIAS').mkdir()
    argv=[sys.executable,'-I','-B',str(stage/'RECALCULO/recalcular_primarios_apd.py'),
          '--primarios',str(stage/'PRIMARIOS'),'--artefactos',str(stage/'ARTEFACTOS'),
          '--salida',str(stage/'REFERENCIAS/ROOT.json')]
    result=subprocess.run(argv,capture_output=True,text=True,encoding='utf8',timeout=120)
    if result.returncode:raise RuntimeError('Archived root recalc failed, no physics repeated: '+result.stdout+result.stderr)
    root_result=read(stage/'REFERENCIAS/ROOT.json')
    coverage={'cut':args.corte,'last_requested_P_number':args.hasta,'included_primaries':[p.name for p in sources],
        'root_RAW_observations':root_result['RAW_observations_decoded'],'root_discrepancies':root_result['discrepancies'],
        'files':[{'primary':q['primary'],'life_id':q['life_id'],'tick':q['committed_tick'],
                  'native_numeric':q['native_numeric_counts'],'prepared_count':q['prepared_count_counts'],
                  'accumulator':q['bounded_accumulation_counts'],'integrated':q['integrated_counts'],
                  'requests':q['request_denominators']}for q in root_result['files']],
        'lexical_component_once':'LENGUAJE, its8positive/negative histories and2portable recalculations',
        'not_a_campaign_closure':True,'new_native_ticks':0,'scope':'No new ticks or independent samples. This fixed audit cut cannot certify later Pxx or final package integrity.'}
    new_json(stage/'COBERTURA_RECALCULO.json',coverage)
    cases=[{'case':'ROOT','script':'RECALCULO/recalcular_primarios_apd.py','args':['--primarios','PRIMARIOS','--artefactos','ARTEFACTOS','--salida','RECALCULADO_ROOT.json'],
            'reference':'REFERENCIAS/ROOT.json','reference_sha256':sha(stage/'REFERENCIAS/ROOT.json')}]
    for rev in('R01','R02'):
        cases.append({'case':'LEX_'+rev,'script':'LENGUAJE/RECALCULO/recalcular_lexico_'+rev.lower()+'.py',
            'args':['--primarios','LENGUAJE/EVIDENCIA/'+rev,'--salida','RECALCULADO_LEX_'+rev+'.json'],
            'reference':'LENGUAJE/REFERENCIAS/'+rev+'.json','reference_sha256':sha(stage/'LENGUAJE/REFERENCIAS'/(rev+'.json'))})
    new_json(stage/'PLAN_RECALCULO.json',{'cases':cases,'native_ticks_executed':0,'stdlib_only':True})
    new_json(stage/'INDICE_FUENTES_Y_OMISIONES.json',{'files':index,'exact_code_revisions':code_index,'complete_states_local_only':snapshot_index,
        'omitted':'Motor, interpreter, WHL, full paired service queues and snapshots, deep historical telemetry; not required for archived calculation and not claimed redistributable continuation here.'})
    shutil.copytree(stage,test);validations=[]
    for case in cases:
        argv=[sys.executable,'-I','-B',case['script'],*case['args']]
        p=subprocess.run(argv,cwd=test,capture_output=True,text=True,encoding='utf8',timeout=120)
        generated=test/case['args'][-1];reference=test/case['reference']
        same=p.returncode==0 and generated.exists()and generated.read_bytes()==reference.read_bytes()
        validations.append({'case':case['case'],'argv':argv,'returncode':p.returncode,'byte_identical':same,
            'generated_sha256':sha(generated)if generated.exists()else None,'reference_sha256':sha(reference),'stderr':p.stderr})
        if not same:raise AssertionError('Portable calculation differs: '+case['case'])
    new_json(stage/'PRUEBA_PORTABLE.json',{'cases':validations,'short_independent_test_directory':str(test),'native_ticks_executed':0,'no_runtime_or_historical_imports':True})
    members=[{'path':p.relative_to(stage).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(stage.rglob('*'))if p.is_file()]
    new_json(stage/'MANIFIESTO.json',{'members':members,'self_hash_omitted':True})
    print(json.dumps({'stage':str(stage),'files':len(members)+1,'expanded_bytes':sum(p.stat().st_size for p in stage.rglob('*')if p.is_file()),
        'primary_count':len(sources),'root_RAW_observations':root_result['RAW_observations_decoded'],'portable_cases':validations},ensure_ascii=False))
if __name__=='__main__':main()
