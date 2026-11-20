"""Pure descriptor/guard tests only; never invokes the publisher main/apply."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';script=H/'publicar_documentos_PI05_literal.py'
spec=importlib.util.spec_from_file_location('PI05_publication_pure_under_test',script)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
paths=[m.C/'PROYECTO.json',m.C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json',m.S/'capacidades/CATALOGO_CAPACIDADES.json']
critical=paths+[m.C/m.NAME,m.R/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx',m.S/'estado/ACTIVO.json']
before={str(p):m.info(p)['sha256']for p in critical}
original={str(p):m.read(p)for p in paths};unchanged=copy.deepcopy(original);tests=[]
def test(name,value):
 if not value:raise AssertionError(name)
 tests.append({'name':name,'passed':True})
manual={'published':{'path':str(m.C/m.NAME),'bytes':123,'sha256':'a'*64},'literal_backup':{'path':'fixture_only','sha256':'b'*64}}
visual=m.visual_evidence(None,'a'*64)
updated=m.metadata_updates(original,paths,manual,visual,m.D/'fixture_publication.json',m.D/'fixture_structure.json','fixture_time')
test('input_copies_not_mutated',original==unchanged)
allowed=[{'manual_before_PI05_publication_historical','manual_internal_edition','manual_current_sha256','manual_current_bytes','manual_publication_witness'},
 {'manual_before_PI05_publication_historical','manual','manual_current','last_documentary_update_PI05'},
 {'manual_before_PI05_publication_historical','manual_current'}]
for p,keys in zip(paths,allowed):
 test('only_document_descriptor_keys_'+p.name,{k:v for k,v in original[str(p)].items()if k not in keys}=={k:v for k,v in updated[str(p)].items()if k not in keys})
test('edition_updates_only_descriptors',updated[str(paths[0])]['manual_internal_edition']=='1.32')
test('compatible_filename_preserved',updated[str(paths[0])]['manual_current']==m.NAME)
test('visual_absence_is_not_approval',visual['status']=='NOT_VALIDATED'and visual['reviewed_images']==[])
try:m.metadata_updates(updated,paths,manual,visual,m.D/'fixture_publication.json',m.D/'fixture_structure.json','fixture_time')
except ValueError:test('reject_duplicate_publication_history',True)
else:raise AssertionError('Duplicate publication allowed')
bad=copy.deepcopy(original);bad[str(paths[0])]['manual_current']='different_manual.docx'
try:m.metadata_updates(bad,paths,manual,visual,m.D/'fixture_publication.json',m.D/'fixture_structure.json','fixture_time')
except ValueError:test('reject_changed_compatible_filename',True)
else:raise AssertionError('Renaming allowed')
try:m.validate_docx(m.C/m.NAME,m.OLD['Manual'])
except ValueError as e:test('old_manual_is_not_new_edition',str(e)=='Staged core edition is not1.32')
else:raise AssertionError('Old edition accepted')
history=m.history43_47(m.C/m.NAME);test('historical_chapters_range_reads_nonempty',bool(history))
tree=ast.parse(script.read_bytes());imports=[n for n in ast.walk(tree)if isinstance(n,(ast.Import,ast.ImportFrom))]
test('no_DEE_or_app_imports',not any(any(alias.name.startswith(('dee_','app'))for alias in n.names)if isinstance(n,ast.Import)else(n.module or'').startswith(('dee_','app'))for n in imports))
after={str(p):m.info(p)['sha256']for p in critical};test('critical_original_hashes_unchanged',before==after)
result={'schema':'DEE.PI05.publication_pure_checks.v1','tests':tests,'passed':len(tests),'Native_executed':False,'publisher_main_called':False,
 'publisher_sha256':m.info(script)['sha256'],'original_critical_before':before,'original_critical_after':after,
 'scope':'Pure in-memory descriptor guards and frozen DOCX structural reads. No publication, rendering, visual approval, DEE import or operational execution.'}
out=P/'control/PUBLICADOR_PI05_PRUEBAS_PURAS_R01.json'
with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'output':str(out),'sha256':m.info(out)['sha256'],'passed':len(tests),'Native_executed':False},ensure_ascii=False))
