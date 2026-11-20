"""Directory-schema helper with synthetic files/SQLite only, no DEE worlds."""
from pathlib import Path
import hashlib,importlib.util,json,sqlite3,sys
P=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('pi06_schema_pure',P/'codigo/materializar_vacios_PI06.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);root=P/'control/FAKE_VACIOS_PI06_R01'
root.mkdir(exist_ok=False);m.P=root;m.C=root/'fake_product';m.S=root/'fake_system';checks=[]
def test(name,value):
 if not value:raise AssertionError(name)
 checks.append({'name':name,'passed':True})
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v),encoding='utf8')
life=m.PREFIX+'FAKE_ONLY';service=m.S/'estado/servicios_persistentes'/life;worker=m.S/'estado/servicios_locales'/life
service.mkdir(parents=True);worker.mkdir(parents=True);(root/'control').mkdir();pair=root/'pares/FAKE_ONLY';pair.mkdir(parents=True)
snapshot=m.S/'estado/checkpoints/fake.dat';snapshot.parent.mkdir(parents=True);snapshot.write_bytes(b'FAKE_NOT_A_NATIVE_SNAPSHOT')
manifest={'life_id':'FAKE_SOURCE_ONLY','snapshot_sha256':m.sha(snapshot),'empty_directories_preserved':[
 'resultados','resultados/folder','artefactos_trabajador','artefactos_trabajador/device','artefactos_trabajador/device/inflight']}
write(pair/'EXPORTACION_SERVICIO.json',manifest)
write(service/'IMPORTACION.json',{'new_life_id':life,'source_life_id':manifest['life_id'],'source_snapshot_sha256':manifest['snapshot_sha256'],
 'verification':{'manifest_sha256':m.sha(pair/'EXPORTACION_SERVICIO.json')}})
write(m.S/'estado/vidas'/life/'VIDA.json',{'life_id':life,'world_id':life,'snapshot':'estado/checkpoints/fake.dat','snapshot_sha256':m.sha(snapshot),'physical':{'N':67,'tick':1}})
db=service/'cola.sqlite3';q=sqlite3.connect(db);q.execute('create table meta(key text,value text)');q.execute('create table requests(id text,status text)');q.execute('insert into meta values(?,?)',('owner',json.dumps({'running':False,'imported_not_yet_started':True,'tick':1})));q.commit();q.close()
existing=worker/'existing.bin';existing.write_bytes(b'PRESERVE_EXISTING_CONTENT')
before=m.sha(existing);dry=m.materialize(life,pair)
test('dry_read_does_not_create_missing_directory',dry['planned_missing']==4 and not(worker/'device').exists())
applied=m.materialize(life,pair,apply=True,output=root/'control/apply.json')
test('only_declared_missing_directories_created',len(applied['created'])==4 and applied['all_declared_directories_present'])
test('snapshot_card_SQLite_unchanged',applied['critical_before_sha256']==applied['critical_after_sha256'])
test('existing_file_content_unchanged',m.sha(existing)==before)
again=m.materialize(life,pair,apply=True,output=root/'control/idempotent.json')
test('repeat_schema_does_not_touch_existing_paths',again['created']==[] and again['planned_missing']==0)
for bad in('../escape','/absolute','C:/drive','resultados/../escape','other_root/x','resultados/./x','resultados\\x','resultados//x'):
 try:m.directory_map([bad],service,worker)
 except ValueError:test('reject_'+bad,True)
 else:raise AssertionError('Unsafe directory accepted: '+bad)
locks=m.S/'estado/locks';locks.mkdir();(locks/'FAKE_WRITER.lock').write_text('fake')
try:m.materialize(life,pair)
except ValueError:test('refuses_any_active_or_uncertain_writer_lock',True)
else:raise AssertionError('Writer was ignored')
test('no_DEE_or_app_imports',not any(x=='app'or x.startswith(('app.','dee_thinking'))for x in sys.modules))
proof={'schema':'DEE.PI06.directory_schema_pure_tests.R01','checks':checks,'passed':len(checks),'Native_executed':False,
 'fake_root':str(root),'actual_C_or_S6_read_or_written':False,'helper_sha256':m.sha(P/'codigo/materializar_vacios_PI06.py'),
 'scope':'Synthetic files and SQLite, explicit fake marker snapshot. No Native load or actual-world passivity claim.'}
out=P/'control/VACIOS_PI06_PRUEBAS_PURAS_R01.json'
with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'proof':str(out),'sha256':m.sha(out),'passed':len(checks),'Native_executed':False}))
