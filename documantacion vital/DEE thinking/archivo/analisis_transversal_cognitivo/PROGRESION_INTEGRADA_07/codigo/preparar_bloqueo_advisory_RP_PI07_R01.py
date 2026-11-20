"""Root-only CAS transport fix: additive known-schema dependency blocks.
No Native imports/actions; historical recipe/capsule/recalculation unchanged.
"""
from pathlib import Path
import argparse,ast,datetime,hashlib,importlib.util,json,os,shutil,sys,tempfile
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';ORIGINAL=RP/'reproducir.py'
STAGE=H/'RP_ADVISORY_PI07_R01';PLAN=P/'control/DELTA_ADVISORY_RP_PI07_R01.json';OUT=P/'control/ADVISORY_RP_PI07_APLICADO_R01.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def put(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def prepare():
 if PLAN.exists()or STAGE.exists():raise FileExistsError('Existing staged revision preserved')
 s=ORIGINAL.read_text('utf-8-sig');source_sha=sha(ORIGINAL)
 needle='def checked_files(root, rows, exact=False, omit=()):'
 addition='''def dependency_advisories(name):
    """Only explicit static dependency-block records; no actor input or policy."""
    blocked = []
    for record in recorded_verifications(name):
        if record.get('schema') != 'DEE.reproduction.static_dependency_advisory.v1':
            continue
        replacement = record.get('use_replacement_recipe')
        if (record.get('recipe') != name or
                record.get('status') != 'DOCUMENTED_DEPENDENCY_BLOCK_SUPERSEDED' or
                record.get('actual_native_execution_completed') is not False or
                record.get('new_native_ticks') != 0 or
                not isinstance(replacement, str) or
                not re.fullmatch(r'[A-Za-z0-9_]{1,120}', replacement) or
                replacement == name):
            raise ValueError('Invalid explicit static-dependency advisory; fail closed')
        blocked.append(record)
    return blocked


'''
 if s.count(needle)!=1:raise ValueError('Exact current RP source anchor required')
 s=s.replace(needle,addition+needle)
 needle="    result['requirements_available'] = all(v['available_and_identity_checked'] for v in result['checks'])"
 replacement="""    advisory_blocks = dependency_advisories(name)
    result['material_execution_blocked_by_advisory'] = bool(advisory_blocks)
    if advisory_blocks:
        result['checks'].append({'kind': 'explicit_static_dependency_advisory',
                                'available_and_identity_checked': False,
                                'error': 'Historical recipe preserved but material execution blocked by a known dependency advisory.',
                                'advisories': advisory_blocks})
"""+needle
 if s.count(needle)!=1:raise ValueError('Exact requirements gate required')
 s=s.replace(needle,replacement)
 needle="    r = recipe(args.receta); c = config()\n"
 replacement=needle+"    if dependency_advisories(args.receta):\n        emit(verification(args.receta)); return 2  # Before destination creation/import/owner.\n"
 if s.count(needle)!=1:raise ValueError('Exact material gate required')
 s=s.replace(needle,replacement)
 needle="'actual_registered_verifications': recorded_verifications(value['id'])}"
 replacement="'actual_registered_verifications': recorded_verifications(value['id']), 'material_execution_blocked_by_advisory': bool(dependency_advisories(value['id']))}"
 if s.count(needle)!=1:raise ValueError('Exact catalogue display anchor required')
 s=s.replace(needle,replacement);ast.parse(s)
 STAGE.mkdir();shutil.copyfile(ORIGINAL,STAGE/'reproducir_ANTES.py');(STAGE/'reproducir.py').write_text(s,encoding='utf8')
 put(PLAN,{'schema':'DEE.PI07.RP.static_advisory.CAS_delta.v1','source':str(ORIGINAL),'before_sha256':source_sha,'after_sha256':sha(STAGE/'reproducir.py'),'prepared_source':str(STAGE/'reproducir.py'),'before_literal':str(STAGE/'reproducir_ANTES.py'),'Native_executed':False,'scope':'Known-schema dependency advisory blocks only material replay. listar/verificar show the block. Historical recipe/capsules and recalcular body remain literal. Old R02 cold8 has no advisory and is unaffected.'})
 return read(PLAN)
def pure_tests():
 plan=read(PLAN);spec=importlib.util.spec_from_file_location('RP_static_advisory_no_Native',STAGE/'reproducir.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);checks={}
 value={'schema':'DEE.reproduction.static_dependency_advisory.v1','recipe':'old','status':'DOCUMENTED_DEPENDENCY_BLOCK_SUPERSEDED','actual_native_execution_completed':False,'new_native_ticks':0,'use_replacement_recipe':'new'}
 m.recorded_verifications=lambda name:[value];checks['known_schema_blocks']=m.dependency_advisories('old')==[value]
 m.recorded_verifications=lambda name:[{'schema':'historical.material.proof','actual_native_execution_completed':True}];checks['material_proof_not_a_block']=m.dependency_advisories('old')==[]
 m.recorded_verifications=lambda name:[value]
 try:m.dependency_advisories('wrong');checks['wrong_recipe_fail_closed']=False
 except ValueError:checks['wrong_recipe_fail_closed']=True
 m.recipe=lambda name:{};m.config=lambda:{};m.verification=lambda name:{'recipe':name,'requirements_available':False};m.emit=lambda value:None
 m.fresh_destination=lambda value:(_ for _ in ()).throw(RuntimeError('Destination helper must not be reached'))
 class Args:vida='ECI02_PI03_REPRO_FAKE_PURE';receta='old'
 checks['material_refused_before_destination_or_world']=m.run_material(Args())==2
 oldtree=ast.parse((STAGE/'reproducir_ANTES.py').read_text('utf-8-sig'));newtree=ast.parse((STAGE/'reproducir.py').read_text('utf8'))
 get=lambda tree,name:ast.dump(next(node for node in tree.body if isinstance(node,ast.FunctionDef)and node.name==name),include_attributes=False)
 checks['historical_recalculate_AST_literal']=get(oldtree,'recalculate')==get(newtree,'recalculate')
 checks['no_DEE_or_app_imported']=not any(name=='dee_thinking'or name.startswith(('dee_thinking.','app.'))for name in sys.modules)
 if not all(checks.values()):raise AssertionError(checks)
 return checks
def actual_read_only_checks():
 spec=importlib.util.spec_from_file_location('RP_static_advisory_actual_RO',STAGE/'reproducir.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.HERE=RP;m.PRODUCT=C
 results={}
 for name in('pi07_r03_uso_adquirido_post4_R02','pi07_r03_uso_adquirido_post4_R03','pi07_r02_8_ep04'):
  if not(RP/'recetas'/(name+'.json')).is_file():raise ValueError('Root registration must finish before actual read-only check')
  result=m.verification(name);results[name]={'requirements_available':result['requirements_available'],'material_execution_blocked_by_advisory':result['material_execution_blocked_by_advisory'],'new_native_ticks':result['new_native_ticks'],'checks':[{'kind':r['kind'],'available_and_identity_checked':r['available_and_identity_checked']}for r in result['checks']]}
 if results['pi07_r03_uso_adquirido_post4_R02']['requirements_available']or not results['pi07_r03_uso_adquirido_post4_R02']['material_execution_blocked_by_advisory']:raise ValueError('Incomplete old R02 must be mechanically blocked')
 for name in('pi07_r03_uso_adquirido_post4_R03','pi07_r02_8_ep04'):
  if not results[name]['requirements_available']or results[name]['material_execution_blocked_by_advisory']:raise ValueError('Complete replacement and historical R02cold must remain available')
 return results
def main(a):
 plan=read(PLAN)if PLAN.exists()else prepare();tests=pure_tests()
 if a.verificar_actual:
  checks=actual_read_only_checks();out=P/'control/PRUEBAS_ADVISORY_RP_PI07_R01.json';put(out,{'schema':'DEE.PI07.RP.static_advisory.pure_actual_RO.v1','pure_checks':tests,'actual_read_only_checks':checks,'Native_executed':False,'DEE_imported':False,'original_RP_source_unchanged':sha(ORIGINAL)==plan['before_sha256']});print(json.dumps({'proof':str(out),'sha256':sha(out),'checks':checks}));return
 if not a.aplicar:print(json.dumps({'mode':'READ_ONLY_PLAN','plan':str(PLAN),'sha256':sha(PLAN),'pure_checks':tests,'Native_executed':False}));return
 proof=P/'control/PRUEBAS_ADVISORY_RP_PI07_R01.json'
 if not proof.is_file()or not read(proof)['original_RP_source_unchanged']:raise ValueError('Actual static tests must precede Root application')
 if sha(ORIGINAL)!=plan['before_sha256']or sha(STAGE/'reproducir.py')!=plan['after_sha256']:raise ValueError('RP source CAS changed')
 capsule=RP/'codigo_preservado/PI07_RP_STATIC_ADVISORY_R01'
 if capsule.exists()or OUT.exists():raise FileExistsError('Existing correction/version preserved')
 capsule.mkdir();shutil.copyfile(STAGE/'reproducir_ANTES.py',capsule/'reproducir_ANTES.py');shutil.copyfile(STAGE/'reproducir.py',capsule/'reproducir.py');shutil.copyfile(PLAN,capsule/'DELTA.json')
 put(capsule/'MANIFIESTO.json',{'schema':'DEE.RP.instrument_delta.v1','files':[{'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(capsule.iterdir())if p.is_file()],'no_Native_or_frozen_capsule_change':True})
 temporary=ORIGINAL.with_name('reproducir.PI07_ADVISORY_WRITING.py')
 with temporary.open('xb')as f:f.write((STAGE/'reproducir.py').read_bytes());f.flush();os.fsync(f.fileno())
 if sha(ORIGINAL)!=plan['before_sha256']:raise ValueError('Concurrent RP mutation; preserve staged bytes')
 os.replace(temporary,ORIGINAL)
 put(OUT,{'schema':'DEE.PI07.RP.static_advisory.applied.v1','applied':True,'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'file':str(ORIGINAL),'before_sha256':plan['before_sha256'],'after_sha256':sha(ORIGINAL),'preserved_delta':str(capsule),'preserved_manifest_sha256':sha(capsule/'MANIFIESTO.json'),'tests':{'path':str(proof),'sha256':sha(proof)},'Native_executed':False,'new_ticks':0,'old_recipes_capsules_and_recalculation_unchanged':True})
 print(json.dumps({'proof':str(OUT),'sha256':sha(OUT),'Native_executed':False}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');ap.add_argument('--verificar-actual',action='store_true');main(ap.parse_args())
