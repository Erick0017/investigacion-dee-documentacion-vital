"""Prepare/add one bounded A code capsule, current full-prefix alias and recipe.

Root --aplicar only. No Native, state copy, product-selection/source-code edit,
old capsule overwrite or B installation. Default prepares reviewable P8 data.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ast, copy, hashlib, json, os, shutil

P = Path(__file__).resolve().parents[1]; H = P / 'codigo'; R = P.parents[2]
C = R / 'DEE Cognitive 2.0'; S = C / 'sistema'; RP = C / 'reproducibilidad'
KEY = 'PI08_A_CONSOLIDADA_TRANSPORTE_R02'
RID = 'pi08_a_consolidada_uso_T861426_R02'
ALIAS = 'PI08_A_CONSOLIDADA_T861426'
PAIR = RP / 'materiales' / ALIAS
STAGE = H / 'RP_A_CONSOLIDADA_R02_PROPUESTA'
PLAN = P / 'control/PLAN_RP_A_CONSOLIDADA_PI08_R02.json'
PROOF = P / 'control/RP_A_CONSOLIDADA_INCORPORADA_PI08_R02.json'
PREFIX = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_ARP_'

def require(ok, text):
    if not ok: raise ValueError(text)
def read(path): return json.loads(path.read_text('utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8') as stream: json.dump(value, stream, ensure_ascii=False, indent=2); stream.write('\n')
def regular(path):
    for node in (path, *path.parents):
        require(not node.exists() or not(node.is_symlink() or getattr(node.lstat(), 'st_file_attributes', 0)&1024), 'No linked preserved source/target')
def copy_new(source, target):
    regular(source); regular(target); target.parent.mkdir(parents=True, exist_ok=True)
    before = sha(source)
    with source.open('rb') as src, target.open('xb') as dst: shutil.copyfileobj(src, dst)
    require(before == sha(source) == sha(target), 'Source changed or copy corrupted')

def recipe(manifest, capsule_sha, analysis_sha):
    state = [
      {'label': 'R03_STATE', 'literal': {'modo': 'eci01-pi07-r03-estado'}, 'require_zero_ticks': True,
       'read_path': ['result','rows',0,'progress','ordinal'], 'expected': 12},
      {'label': 'C2C_STATE', 'literal': {'modo': 'eci01-pi04-c2c-estado'}, 'require_zero_ticks': True,
       'read_path': ['result','rows',0,'progress','ordinal'], 'expected': 31},
      {'label': 'FI_STATE', 'literal': {'modo': 'eci01-pi07-fi-acceso-estado'}, 'require_zero_ticks': True,
       'read_path': ['result','rows',0,'progress','ordinal'], 'expected': 4}]
    checks = [{'label': 'physical_'+key, 'operation': 'value',
               'values': [{'step':'R03_STATE','path':['result','rows',0,'physical',key]}], 'expected': value}
              for key,value in manifest['physical'].items() if key in ('N','tick','RAW_sha256','clocks_sha256')]
    next_use = {'label': 'R03_OP12', 'literal': {'modo':'eci01-pi07-r03-episodio'},
                'feedback':'real', 'actuator':'closed', 'read_path':['result','rows',0,'actual_failed'],
                'expected':False, 'receipt_paths':[['result','rows',0,'requests']],
                'stop_on_unapplied_receipt':True}
    return {'schema':'DEE.reproduction.recipe.v1','id':RID,
       'title':'PI08 A: complete current acquired state and a prospective next R03 use',
       'revision':'R01_CURRENT_A_311_SOURCES_PLUS_EXPLICIT_DIRECTORY_TRANSPORT',
       'prefix':ALIAS,'code_capsule_key':KEY,'required_life_prefix':PREFIX,
       'requires_explicit_material':True,'reproduction_enabled':True,
       'modalities':['B_complete_acquired_state_use','A_selected_public_records_recalculation','E_prepared_future_use'],
       'variants':{
          'estado_operativo':{'batches':[state],'final_checks':checks,
              'native_receipt_expectations':{'unique_requested':0,'applied':0,'rejected':0,'pending_or_other':0},
              'expected_final_physical':{k:manifest['physical'][k]for k in ('N','tick','RAW_sha256','clocks_sha256')}},
          'siguiente_regulacion':{'batches':[[copy.deepcopy(state[0]),next_use]],
              'interpretation':'Prospective resource12 in a new descendant. expected=false is an evaluator criterion, not an observed result at this current cut. No frozen expected physical final state or exact dose is invented.'}},
       'analysis':{'product_relative':'reproducibilidad/materiales/PI08_A_ANALISIS_PUBLICO_R02',
                   'manifest':'MANIFIESTO_ESTABLE.json','manifest_sha256':analysis_sha,
                   'recalculation_script':'RECALCULAR_A_PUBLICA_RP_PI08_R01.py','interface':'DEE.recalculation.root_outdir.v1'},
       'assistance':['Fixed operator schedule and inherited codecs/readers; only literal modes reach the owner.',
                     'The code capsule preserves 308current product source files plus3 historical beforeimages; the isolated importer has an explicit empty-directory transport adaptation before opening Native.',
                     'The current selected public FI alias belongs exactly to A; this descendant recipe does not claim that alias is selected on the clone.'],
       'limitations':['Shared complete acquired prefix, not T0 acquisition or independent history.',
                      'New recipe has not had an end-to-end material CLI replay. Historical normal_op4 replay ended850427 and was registered separately.',
                      'Documentary analysis recalculates only the actual selected public FI18/7 and alfa records; it does not verify future OP12.',
                      'State has R03ordinal12/18, C2Cordinal31/32 and regulatedFIordinal4/8. Diagnostic uses consume resources only in their clone.'],
       'verification':{'state':'PREPARADA_REPLAY_NATIVE_PENDIENTE','Native_replay_verified':False,
                       'requirements_only_until_actual_completed_record':True},
       'sources':{'current_full_manifest_sha256':sha(PAIR/'EXPORTACION_SERVICIO.json'),
                  'code_capsule_manifest_sha256':capsule_sha,
                  'actual_selected_use_proof':{'path':str(P/'control/PI08_USO_PUBLICO_PRINCIPAL_R01.json'),
                      'sha256':sha(P/'control/PI08_USO_PUBLICO_PRINCIPAL_R01.json')}}}

def prepare():
    require(not PROOF.exists(), 'Existing incorporation protected')
    manifest = read(PAIR/'EXPORTACION_SERVICIO.json')
    require(manifest['physical']['tick']==861426 and manifest['life_id']=='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01', 'Exact complete A prefix required')
    if PLAN.exists(): return read(PLAN)
    require(not STAGE.exists(), 'Partial previous stage preserved')
    base=read(RP/'codigo_preservado/PI07_R03_LOCAL_FI_PRE34_R03/SISTEMA_CODIGO.json')
    delta=read(P/'control/DELTA_OPERATIVO_PRODUCTO_PROPUESTO_PI08_R02.json')
    names={row['file']for row in base['files']}|{row['file']for row in delta['proposed_code_files']}|{'gestionar.py'}
    require(len(names)==311 and not any('revision_flexible_B' in name for name in names), 'Bounded exact308 current files plus3 historical beforeimages, no B')
    cap=STAGE/'capsule'; provenance=[]
    for name in sorted(names):
        require(not name.startswith(('estado/','runtime/')) and not name.endswith('.sqlite3'), 'No state/engine in capsule')
        source=S/name; origin='current_product'
        if not source.exists() and name.startswith('procedencia/ANTES_ACCESO_FI/'):
            source=RP/'codigo_preservado/PI07_R03_LOCAL_FI_PRE34_R03'/name; origin='preserved_historical_beforeimage'
        copy_new(source,cap/name); provenance.append({'file':name,'sha256':sha(source),'bytes':source.stat().st_size,'origin':origin})
    original=cap/'app/importacion_emparejada.py'; copy_new(original,cap/'procedencia/importacion_emparejada_ANTES_PI08.py')
    text=original.read_text('utf8')
    anchor='def import_pair(store,directory,life):\n';require(text.count(anchor)==1,'Exact importer function required')
    text=text.replace(anchor,anchor+"    if not life.startswith('"+PREFIX+"'):raise ValueError('PI08 A capsule requires an explicit fresh ARP diagnostic identity; never principal.')\n")
    anchor="        mapping['external_directory_scaffold']=restore_known_device_directories(store.state/'servicios_locales'/life)\n"
    require(text.count(anchor)==1,'Exact pre-Native import hook required')
    text=text.replace(anchor,anchor+"        from .estructuras_exportadas_PI08_R01 import restore_exported_directories\n        mapping['exported_directory_transport']=restore_exported_directories(source,m,folder,store.state/'servicios_locales'/life)\n")
    ast.parse(text); original.write_text(text,encoding='utf8')
    copy_new(H/'estructuras_exportadas_PI08_R01.py',cap/'app/estructuras_exportadas_PI08_R01.py')
    caprows=[]
    for file in sorted(cap.rglob('*')):
        if file.is_file():
            if file.suffix=='.py':ast.parse(file.read_text('utf-8-sig'))
            caprows.append({'file':file.relative_to(cap).as_posix(),'bytes':file.stat().st_size,'sha256':sha(file)})
    require(len(caprows)==313,'311sources preserved plus helper and importer beforeimage')
    put(cap/'SISTEMA_CODIGO.json',{'schema':'DEE.PI08.A.current_code_capsule.transport_R01','files':caprows,
        'bounded_source_files311':provenance,'current_product_files':sum(row['origin']=='current_product'for row in provenance),'historical_beforeimages':sum(row['origin']=='preserved_historical_beforeimage'for row in provenance),'scientific_sources_literal':True,'only_runtime_transport_adapted':'app/importacion_emparejada.py',
        'original_importer_beforeimage':'procedencia/importacion_emparejada_ANTES_PI08.py','new_empty_directory_helper':'app/estructuras_exportadas_PI08_R01.py',
        'Native_or_B_code_or_engine_added':False,'Native_executed':False})
    analysis=STAGE/'analysis'; index={'schema':'DEE.PI08.portable_primary_index.v1','primaries':[],'products':[],
                                   'scope':'Actual selected public uses only; not a new material reproduction.'}
    for name in ('PI08_USO_PUBLICO_PRINCIPAL_R01_FI18_7.json','PI08_USO_PUBLICO_PRINCIPAL_R01_alfa.json'):
        source=P/'ensayos'/name; target=analysis/'04_EVIDENCIAS/PRIMARIOS'/name;copy_new(source,target)
        index['primaries'].append({'file':target.relative_to(analysis).as_posix(),'bytes':target.stat().st_size,'sha256':sha(target),'modality':'PI08_ACTUAL_SELECTED_PUBLIC_USE','source_reference_for_packager_only':str(source)})
    put(analysis/'04_EVIDENCIAS/PRIMARIOS/INDICE_PRIMARIOS_PI08.json',index)
    for name in ('RECALCULAR_A_PUBLICA_RP_PI08_R01.py','RECALCULAR_PRIMARIOS_PI08.py','auditoria_documental_PI08.py'):
        copy_new(H/name,analysis/name)
    copy_new(H/'heredado/RECALCULAR_PRIMARIOS_PI07_LITERAL.py',analysis/'heredado/RECALCULAR_PRIMARIOS_PI07_LITERAL.py')
    copy_new(P/'control/PI08_USO_PUBLICO_PRINCIPAL_R01.json',analysis/'USO_PUBLICO_ORIGINAL.json')
    analysisrows=[{'file':f.relative_to(analysis).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(analysis.rglob('*'))if f.is_file()]
    put(analysis/'MANIFIESTO_ESTABLE.json',{'schema':'DEE.PI08.A.public_analysis.files.R01','files':analysisrows,'Native_executed':False})
    spec=recipe(manifest,sha(cap/'SISTEMA_CODIGO.json'),sha(analysis/'MANIFIESTO_ESTABLE.json'));put(STAGE/'receta.json',spec)
    resources=read(RP/'RECURSOS.json')
    require(KEY not in resources.get('code_capsules',{}) and ALIAS not in resources['pairs'] and not(RP/'recetas'/(RID+'.json')).exists(), 'Additive unique RP aliases/recipe only')
    resources['code_capsules'][KEY]={'product_relative':'reproducibilidad/codigo_preservado/'+KEY,'manifest':'SISTEMA_CODIGO.json','manifest_sha256':sha(cap/'SISTEMA_CODIGO.json')}
    resources['pairs'][ALIAS]={'product_relative':'reproducibilidad/materiales/'+ALIAS,'manifest_sha256':sha(PAIR/'EXPORTACION_SERVICIO.json'),'life_id':manifest['life_id'],'tick':861426}
    resources.setdefault('analysis_deltas',{})['PI08_A_PUBLICO_R01']=spec['analysis']
    put(STAGE/'RECURSOS_PROPUESTOS.json',resources)
    plan={'schema':'DEE.PI08.A.RP.additive_integration.CAS_plan.R01','resource_before_sha256':sha(RP/'RECURSOS.json'),
          'capsule_key':KEY,'capsule_manifest_sha256':sha(cap/'SISTEMA_CODIGO.json'),'capsule_files':313,
          'bounded_sources_preserved':311,'current_product_sources_preserved':308,'historical_beforeimages_preserved':3,'analysis_manifest_sha256':sha(analysis/'MANIFIESTO_ESTABLE.json'),
          'recipe_id':RID,'recipe_sha256':sha(STAGE/'receta.json'),'source_pair_manifest_sha256':sha(PAIR/'EXPORTACION_SERVICIO.json'),
          'new_resource_sha256':sha(STAGE/'RECURSOS_PROPUESTOS.json'),'Native_executed':False,'new_full_state_or_engine_copy':False,
          'material_replay_executed':False,'recipe_state':'PREPARADA_REPLAY_NATIVE_PENDIENTE'}
    put(PLAN,plan);return plan

def main(args):
    plan=prepare()
    require(sha(RP/'RECURSOS.json')==plan['resource_before_sha256'],'CAS resources changed; preserve plan and review')
    require(sha(PAIR/'EXPORTACION_SERVICIO.json')==plan['source_pair_manifest_sha256'],'Source full prefix changed')
    require(sha(STAGE/'capsule/SISTEMA_CODIGO.json')==plan['capsule_manifest_sha256']and sha(STAGE/'receta.json')==plan['recipe_sha256'],'Preserved stage changed')
    if args.aplicar:
        capdest=RP/'codigo_preservado'/KEY; anadest=RP/'materiales/PI08_A_ANALISIS_PUBLICO_R02'; recdest=RP/'recetas'/(RID+'.json')
        require(not capdest.exists()and not anadest.exists()and not recdest.exists(),'Existing RP material protected')
        backup=P/'control/RECURSOS_ANTES_A_RP_PI08_R02.json';copy_new(RP/'RECURSOS.json',backup)
        for source,dest in ((STAGE/'capsule',capdest),(STAGE/'analysis',anadest)):
            for file in sorted(source.rglob('*')):
                if file.is_file():copy_new(file,dest/file.relative_to(source))
        copy_new(STAGE/'receta.json',recdest)
        require(sha(RP/'RECURSOS.json')==plan['resource_before_sha256'],'Concurrent registry write')
        temp=RP/'RECURSOS.json.PI08_A_WRITING'
        with temp.open('xb')as stream:stream.write((STAGE/'RECURSOS_PROPUESTOS.json').read_bytes());stream.flush();os.fsync(stream.fileno())
        os.replace(temp,RP/'RECURSOS.json')
        put(PROOF,{'schema':'DEE.PI08.A.RP.additive_integration.applied.R01','applied':True,'recorded_utc':datetime.now(timezone.utc).isoformat(),
           **plan,'recipe_path':str(recdest),'code_capsule':str(capdest),'analysis':str(anadest),
           'resources_after_sha256':sha(RP/'RECURSOS.json'),'Native_executed':False,'principal_or_source_code_modified':False})
    file=PROOF if args.aplicar else PLAN
    print(json.dumps({'mode':'APPLIED_ROOT_ONLY'if args.aplicar else'P8_PLAN_READY_NO_RP_WRITE','proof':str(file),'sha256':sha(file),
                      'recipe':RID,'capsule_files':313,'Native_executed':False,'material_replay_verified':False}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--aplicar',action='store_true');main(parser.parse_args())
