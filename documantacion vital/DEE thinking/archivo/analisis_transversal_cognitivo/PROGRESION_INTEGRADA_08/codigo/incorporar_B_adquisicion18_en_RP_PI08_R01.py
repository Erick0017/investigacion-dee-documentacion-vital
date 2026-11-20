"""Root-only additive RP preservation of exact B code and actual REAL18 evidence.

Default prepares P8 review data only. --aplicar adds a capsule/analysis/recipe and
CAS-updates RECURSOS. No Native, world/full-state copy, selector or actor rewrite.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse, ast, hashlib, json, os, shutil

P=Path(__file__).resolve().parents[1];H=P/'codigo';R=P.parents[2]
C=R/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
SOURCE=P/'estados/B_REAL_R01/sistema'
SOURCE_MANIFEST=H/'FUENTES_B_PI08_R02_PREPARADAS/SISTEMA_CODIGO.json'
KEY='PI08_B_REAL18_IDENTIDAD_TRANSPORTE_R01'
RID='pi08_b_adquisicion18_desde_A_T861426_R01'
ALIAS='PI08_A_CONSOLIDADA_T861426';PAIR=RP/'materiales'/ALIAS
ANALIAS='PI08_B_REAL18_ANALISIS_R01'
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_BRP_'
STAGE=H/'RP_B_ADQUISICION18_R01_PROPUESTA'
PLAN=P/'control/PLAN_RP_B_ADQUISICION18_PI08_R01.json'
PROOF=P/'control/RP_B_ADQUISICION18_INCORPORADA_PI08_R01.json'
BUNDLE=P/'control/B_PORTABLE_REAL18_R01'
ACTUAL=P/'control/PI08_B_REAL_R02.json'
A_MANIFEST='dfadc5037b804f3c6112263eb0af84f6215d53fd3cb138ae143676a56dfcc00c'
SCIENCE={'pi08_revision_flexible_B_R01.py':'aebe20a4566046957b274b07b942a3843ab4b612a9214791ff38edeb6bc53480',
 'pi08_revision_flexible_B_episodio_R01.py':'a110b1de0953d86b1488f62a623f9623fad686885bd30d446c5f5a3deb44ab6f',
 'PROTOCOLO_PI08_B_R01.json':'8c7b1fc983b7279e9ec78cd0136d5bc8d80d072340668783446f8ec19dd34640',
 'SELLO_PI08_B_R01.json':'98a54759d0d4bae2e53a6f432962b08e92f2b3836ee98b98b3b44dad7ae8779e'}

def require(ok,message):
    if not ok:raise ValueError(message)
def read(path):return json.loads(path.read_text('utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def put(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8')as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
def regular(path):
    for node in(path,*path.parents):
        require(not node.exists()or not(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&1024),'No links/reparse points')
def local(root,name):
    part=PurePosixPath(name)
    require(not part.is_absolute()and '\\'not in name and all(x not in('..','')for x in part.parts),'Bounded relative preserved filename required')
    target=root.joinpath(*part.parts);regular(target);return target
def copy_new(source,target):
    regular(source);regular(target);require(source.is_file(),'Regular source file required')
    before=sha(source);target.parent.mkdir(parents=True,exist_ok=True)
    with source.open('rb')as src,target.open('xb')as dst:shutil.copyfileobj(src,dst)
    require(before==sha(source)==sha(target),'Source changed or copied bytes differ')
def decoded_primary(file):
    data=read(file);result=data['result'];result=json.loads(result)if isinstance(result,str)else result
    return result['result']['rows'][0]

def recipe(capsule_sha,analysis_sha,actual,primaries):
    start={'label':'B_START_REAL','literal':{'modo':'eci01-pi08-b-iniciar','brazo':'real','prefijo_sha256':A_MANIFEST,'registro_global':False},
           'require_zero_ticks':True,'feedback':'real','actuator':'closed','read_path':['result','rows',0,'admitted'],'expected':True}
    steps=[start];checks=[]
    for index,row in enumerate(primaries):
        label='B_EP%02d'%index;base=['result','rows',0]
        steps.append({'label':label,'literal':{'modo':'eci01-pi08-b-episodio'},'feedback':'real','actuator':'closed',
          'read_path':base+['actual_failed'],'expected':row['actual_failed'],'receipt_paths':[base+['requests']],
          'stop_on_unapplied_receipt':False})
        values=[('Native_choice',['reader','choice'],row['reader']['choice']),('native_motor',['native_motor'],row['native_motor']),
                ('FI_q4',['FI','early_physical_choice'],row['FI']['early_physical_choice']),
                ('message_delivered',['message','delivered_exact'],row['message']['delivered_exact'])]
        values += [('physical_'+k,['physical_after',k],v)for k,v in row['physical_after'].items()]
        for name,path,expected in values:
            checks.append({'label':label+'_'+name,'operation':'value','values':[{'step':label,'path':base+path}],'expected':expected})
    steps.append({'label':'B_FINAL_STATE','literal':{'modo':'eci01-pi08-b-estado'},'require_zero_ticks':True,
                  'read_path':['result','rows',0,'progress','ordinal'],'expected':30})
    return {'schema':'DEE.reproduction.recipe.v1','id':RID,'title':'PI08 B: actual REAL18 trajectory from complete adopted A prefix',
      'revision':'R01_LITERAL_B_WITH_SEPARATE_DIAGNOSTIC_IDENTITY_AND_DIRECTORY_TRANSPORT',
      'prefix':ALIAS,'code_capsule_key':KEY,'required_life_prefix':PREFIX,
      'requires_explicit_material':True,'reproduction_enabled':True,
      'variants':{'real18_sin_global':{'batches':[steps],'final_checks':checks,
          'native_receipt_expectations':{'unique_requested':3306,'applied':3302,'rejected':4,'pending_or_other':0},
          'expected_final_physical':primaries[-1]['physical_after'],
          'known_material_adverse_events_preserved':'Four actual failures, including four terminal rejected_conflict inputs; no successful-only filtering.'}},
      'analysis':{'product_relative':'reproducibilidad/materiales/'+ANALIAS,'manifest':'MANIFIESTO_ESTABLE.json',
                  'manifest_sha256':analysis_sha,'recalculation_script':'RECALCULAR_B_REAL18_RP_PI08_R01.py','interface':'DEE.recalculation.root_outdir.v1'},
      'verification':{'state':'PREPARADA_REPLAY_NATIVE_PENDIENTE','Native_replay_verified':False,'B_new_CLI_replay_verified':False},
      'assistance':['External fixed finite schedule and fixed physical input/reader codecs are inherited literal. Expected responses are used only by the evaluator after Native outputs.',
        'RP-only private validation projects the sealed real role during validation; actual SYSTEM/new descendant identity remains in journals/effects.',
        'All complete-prefix declared empty directories are transported before the first Native opening. No file, memory or clock is recreated.',
        'Global recording is disabled in this prospective replay; original REAL18 recording was enabled. Passivity of this instrumentation difference is not claimed as newly verified.'],
      'limitations':['Not T0 acquisition: shares the complete learned A prefix T861426.',
        'Actual original REAL18 is14/18, NONE13/18, YOKE9/18, reference14/18; no universal advantage over external WSLS is claimed.',
        'New B material frontdoor replay remains unexecuted. Preserved original18 execution is not relabelled a replica.',
        'Documentary recalculation contains only the actual REAL18 bundle; its PARTIAL four-arm status is preserved.',
        'No selected principal, control/reference role, forced action, old-calendar reuse or alternative feedback is admitted.'],
      'sources':{'source_full_pair_manifest_sha256':A_MANIFEST,'code_capsule_manifest_sha256':capsule_sha,
        'actual_B18_proof':{'path':str(ACTUAL),'sha256':sha(ACTUAL)},'actual_B18_source_final_tick':actual['final_tick'],
        'original_Native_counts':actual['Native_inputs'],'new_material_replay_executed':False}}

def prepare():
    require(not PROOF.exists(),'Existing Root incorporation protected')
    if PLAN.exists():return read(PLAN)
    require(not STAGE.exists(),'Previous partial stage preserved; choose a new revision')
    require(sha(PAIR/'EXPORTACION_SERVICIO.json')==A_MANIFEST,'Exact stable A complete prefix required')
    manifest=read(PAIR/'EXPORTACION_SERVICIO.json');require(manifest['physical']['tick']==861426,'Exact A tick')
    actual=read(ACTUAL);require(actual['closed']and actual['opportunities_completed']==18 and actual['final_tick']==875451,'Actual closed REAL18 required')
    require(actual['role']=='real'and actual['joint_useful']==14,'Truthful original REAL18 denominator')
    require(sha(BUNDLE/'INDICE_B_PI08_R01.json')=='b19208f812ea9a59c79ce29f05341a95a40dcd527597404d433cc08204400375','Preserved literal REAL18 index required')
    sources=read(SOURCE_MANIFEST)['files'];require(len(sources)==311,'Exact bounded311 source closure required')
    cap=STAGE/'capsule';provenance=[]
    for row in sources:
        name=row['file'];require(not name.startswith(('estado/','runtime/'))and not name.endswith('.sqlite3'),'No state/engine in code capsule')
        source=local(SOURCE,name);require(sha(source)==row['sha256'],'Used B source changed: '+name)
        copy_new(source,local(cap,name));provenance.append({'file':name,'bytes':row['bytes'],'sha256':row['sha256'],'source':str(source)})
    importer=cap/'app/importacion_emparejada.py';copy_new(importer,cap/'procedencia/ANTES_RP_B/importacion_emparejada.py')
    text=importer.read_text('utf8');anchor='def import_pair(store,directory,life):\n';require(text.count(anchor)==1,'Exact importer entry')
    text=text.replace(anchor,anchor+"    if not life.startswith('"+PREFIX+"'):raise ValueError('Explicit fresh BRP descendant required; never principal.')\n")
    anchor="        mapping['external_directory_scaffold']=restore_known_device_directories(store.state/'servicios_locales'/life)\n"
    require(text.count(anchor)==1,'Exact pre-Native directory hook')
    text=text.replace(anchor,anchor+"        from .estructuras_exportadas_PI08_R01 import restore_exported_directories\n        mapping['exported_directory_transport']=restore_exported_directories(source,m,folder,store.state/'servicios_locales'/life)\n")
    ast.parse(text);importer.write_text(text,encoding='utf8')
    owner=cap/'app/mundo_genesis_apd05.py';copy_new(owner,cap/'procedencia/ANTES_RP_B/mundo_genesis_apd05.py')
    text=owner.read_text('utf8');anchor='from capacidades import pi08_revision_flexible_B_R01 as pi08b\n'
    require(text.count(anchor)==5,'Exactly five isolated B owner paths')
    lines=text.splitlines(True);patched=[]
    for line in lines:
        patched.append(line)
        if anchor.strip()==line.strip():
            indent=line[:len(line)-len(line.lstrip())]
            patched.extend([indent+'from capacidades import pi08_permiso_B_reproduccion_R02 as rp_identity\n',indent+'pi08b=rp_identity.component(self.a,pi08b)\n'])
    text=''.join(patched);ast.parse(text);owner.write_text(text,encoding='utf8')
    copy_new(H/'estructuras_exportadas_PI08_R01.py',cap/'app/estructuras_exportadas_PI08_R01.py')
    copy_new(H/'pi08_permiso_B_reproduccion_R02.py',cap/'capacidades/pi08_permiso_B_reproduccion_R02.py')
    for name,digest in SCIENCE.items():require(sha(cap/'capacidades'/name)==digest,'Frozen B scientific file changed')
    files=[]
    for f in sorted(cap.rglob('*')):
        if f.is_file():
            if f.suffix=='.py':ast.parse(f.read_text('utf-8-sig'))
            files.append({'file':f.relative_to(cap).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
    require(len(files)==315,'311literal sources plus2helpers/2beforeimages')
    put(cap/'SISTEMA_CODIGO.json',{'schema':'DEE.PI08.B.RP.literal_code_with_transport.R01','files':files,
       'source_closure_manifest_sha256':sha(SOURCE_MANIFEST),'bounded_used_sources':provenance,'scientific_sources_literal':SCIENCE,
       'only_adapted_runtime_files':['app/importacion_emparejada.py','app/mundo_genesis_apd05.py'],
       'source_system_or_product_modified':False,'Native_executed':False})
    analysis=STAGE/'analysis'
    for source in sorted(BUNDLE.rglob('*')):
        if source.is_file():copy_new(source,analysis/source.relative_to(BUNDLE))
    copy_new(H/'RECALCULAR_B_REAL18_RP_PI08_R01.py',analysis/'RECALCULAR_B_REAL18_RP_PI08_R01.py')
    arows=[{'file':f.relative_to(analysis).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(analysis.rglob('*'))if f.is_file()]
    put(analysis/'MANIFIESTO_ESTABLE.json',{'schema':'DEE.PI08.B.RP.actual_REAL18_files.R01','files':arows,'Native_executed':False})
    index=read(BUNDLE/'INDICE_B_PI08_R01.json');primaries=[decoded_primary(local(BUNDLE,x['file']))for x in index['arms']['real']['primaries']]
    require(len(primaries)==18,'All18 actual adverse/favorable episodes required')
    spec=recipe(sha(cap/'SISTEMA_CODIGO.json'),sha(analysis/'MANIFIESTO_ESTABLE.json'),actual,primaries);put(STAGE/'receta.json',spec)
    resources=read(RP/'RECURSOS.json');require(ALIAS in resources['pairs']and resources['pairs'][ALIAS]['manifest_sha256']==A_MANIFEST,'Reuse registered A full prefix')
    require(KEY not in resources['code_capsules']and not(RP/'recetas'/(RID+'.json')).exists(),'New capsule/recipe only')
    resources['code_capsules'][KEY]={'product_relative':'reproducibilidad/codigo_preservado/'+KEY,'manifest':'SISTEMA_CODIGO.json','manifest_sha256':sha(cap/'SISTEMA_CODIGO.json')}
    resources.setdefault('analysis_deltas',{})['PI08_B_REAL18_R01']=spec['analysis'];put(STAGE/'RECURSOS_PROPUESTOS.json',resources)
    plan={'schema':'DEE.PI08.B.RP.acquisition18_preservation.CAS_plan.R01','resource_before_sha256':sha(RP/'RECURSOS.json'),
      'capsule_key':KEY,'capsule_files':315,'capsule_manifest_sha256':sha(cap/'SISTEMA_CODIGO.json'),
      'recipe_id':RID,'recipe_sha256':sha(STAGE/'receta.json'),'analysis_manifest_sha256':sha(analysis/'MANIFIESTO_ESTABLE.json'),
      'source_prefix':{'path':str(PAIR),'manifest_sha256':A_MANIFEST},'actual_B18_proof':{'path':str(ACTUAL),'sha256':sha(ACTUAL)},
      'new_resource_sha256':sha(STAGE/'RECURSOS_PROPUESTOS.json'),'Native_executed':False,'B_new_CLI_replay_verified':False,
      'new_full_state_or_engine_copy':False,'recipe_state':'PREPARADA_REPLAY_NATIVE_PENDIENTE',
      'new_bytes':sum(x.stat().st_size for x in STAGE.rglob('*')if x.is_file())}
    put(PLAN,plan);return plan

def main(args):
    plan=prepare();require(sha(RP/'RECURSOS.json')==plan['resource_before_sha256'],'CAS registry changed; preserve plan and review')
    require(sha(PAIR/'EXPORTACION_SERVICIO.json')==A_MANIFEST,'Stable source prefix manifest changed')
    for folder,manifest in[(STAGE/'capsule','SISTEMA_CODIGO.json'),(STAGE/'analysis','MANIFIESTO_ESTABLE.json')]:
        for row in read(folder/manifest)['files']:
            f=local(folder,row['file']);require(f.stat().st_size==row['bytes']and sha(f)==row['sha256'],'Staged member changed')
    require(sha(STAGE/'receta.json')==plan['recipe_sha256'],'Staged recipe changed')
    if args.aplicar:
        capdest=RP/'codigo_preservado'/KEY;anadest=RP/'materiales'/ANALIAS;recdest=RP/'recetas'/(RID+'.json')
        require(not capdest.exists()and not anadest.exists()and not recdest.exists(),'Existing RP resources protected')
        copy_new(RP/'RECURSOS.json',P/'control/RECURSOS_ANTES_B_RP_PI08_R01.json')
        for source,dest in[(STAGE/'capsule',capdest),(STAGE/'analysis',anadest)]:
            for file in sorted(source.rglob('*')):
                if file.is_file():copy_new(file,dest/file.relative_to(source))
        copy_new(STAGE/'receta.json',recdest)
        require(sha(RP/'RECURSOS.json')==plan['resource_before_sha256'],'Concurrent RP registry write')
        temp=RP/'RECURSOS.json.PI08_B_WRITING'
        with temp.open('xb')as stream:stream.write((STAGE/'RECURSOS_PROPUESTOS.json').read_bytes());stream.flush();os.fsync(stream.fileno())
        os.replace(temp,RP/'RECURSOS.json')
        put(PROOF,{**plan,'schema':'DEE.PI08.B.RP.acquisition18_preservation.applied.R01','applied':True,
          'recorded_utc':datetime.now(timezone.utc).isoformat(),'recipe_path':str(recdest),'code_capsule':str(capdest),
          'capsule_manifest':str(capdest/'SISTEMA_CODIGO.json'),'analysis':str(anadest),'resources_after_sha256':sha(RP/'RECURSOS.json'),
          'historical_R03_frontdoor_replay':{'path':str(P/'control/RP_FRONTDOOR_HISTORICO_A_PI08_REGISTRADO_R01.json'),
             'sha256':sha(P/'control/RP_FRONTDOOR_HISTORICO_A_PI08_REGISTRADO_R01.json')},
          'principal_or_source_code_modified':False})
    result=PROOF if args.aplicar else PLAN
    print(json.dumps({'mode':'APPLIED_ROOT_ONLY'if args.aplicar else'P8_PLAN_ONLY_NO_RP_WRITES','proof':str(result),'sha256':sha(result),'recipe':RID,'capsule_files':315,'Native_executed':False,'B_new_CLI_replay_verified':False}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--aplicar',action='store_true');main(parser.parse_args())
