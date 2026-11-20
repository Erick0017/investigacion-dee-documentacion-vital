"""Pure/Fake validation of conditional relocation; never Store/move/adopt."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parents[1];H=P/'codigo';OUT=P/'control/TRASLADO_PI07_FAKE';OUT.mkdir(exist_ok=False)
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('PI07_relocation_pure',H/'incorporar_PI07_misma_identidad.py');identity=load('PI07_moved_identity_pure',H/'pi07_identidad_c2c_R02.py');tests=[]
def test(name,ok):
 if not ok:raise AssertionError(name)
 tests.append({'name':name,'passed':True})
# One-leaf identity is a pure proposal. Histories with old IDs stay literal.
old={'life_id':m.PARENT,'ordinal':30,'rows':[{'life_id':m.PARENT}],'protocol_sha256':'KEEP','pending':None,'uncertain':False};before=copy.deepcopy(old);new,leaf=identity.propose_identity(old,m.LIFE)
test('pure_one_current_identity_leaf',old==before and new['life_id']==m.LIFE and new['rows']==old['rows']and new['protocol_sha256']==old['protocol_sha256'])
left={'physical':{'N':67,'tick':9,'RAW_sha256':'A','clocks_sha256':'B'},'causal_prefix_sha256':'C','metadata':{'DEE.Cognitive.PI04.C2C.coordination.R01':json.dumps(old),'UNCHANGED':'LITERAL'}};right=copy.deepcopy(left);right['metadata']['DEE.Cognitive.PI04.C2C.coordination.R01']=json.dumps(new)
test('narrow_native_comparison_accepts_only_current_leaf',m.native_equal(left,right)['new_ticks']==0)
for i,bad in enumerate((copy.deepcopy(right),copy.deepcopy(right),copy.deepcopy(right))):
 if i==0:bad['physical']['RAW_sha256']='CHANGED'
 elif i==1:bad['metadata']['UNCHANGED']='ALTERED'
 else:
  b=json.loads(bad['metadata']['DEE.Cognitive.PI04.C2C.coordination.R01']);b['rows']=[];bad['metadata']['DEE.Cognitive.PI04.C2C.coordination.R01']=json.dumps(b)
 try:m.native_equal(left,bad)
 except ValueError:test('reject_nonadministrative_change_'+str(i),True)
 else:raise AssertionError('Changed cognitive/native state accepted')
# Inventory exact three trees, empty directories, all named checkpoints and
# closure of HISTORIA hashes, with arbitrary Fake bytes (not a Native state).
m.CS=OUT/'source/sistema';m.S=OUT/'product/sistema';state=m.CS/'estado'
for name in('vidas','servicios_persistentes','servicios_locales'):
 root=state/name/m.LIFE;root.mkdir(parents=True);(root/'EMPTY_FAKE_DIRECTORY').mkdir()
cp=state/'checkpoints';cp.mkdir();a=cp/(m.LIFE+'.T9.fake.deetsnap.gz');a.write_bytes(b'FAKE_NOT_NATIVE');initial=cp/('import.'+m.LIFE+'.fake.deetsnap.gz');initial.write_bytes(b'FAKE_IMPORT_NOT_NATIVE')
card={'life_id':m.LIFE,'world_id':m.LIFE,'physical':{'N':67,'tick':9},'snapshot_sha256':m.sha(a),'snapshot':'estado/checkpoints/'+a.name,'parent':{'source_tick':3,'source_name':'P0_LITERAL'}}
folder=state/'vidas'/m.LIFE;(folder/'VIDA.json').write_text(json.dumps(card),encoding='utf8');(folder/'HISTORIA.jsonl').write_text(json.dumps({'snapshot_sha256':m.sha(a),'previous_snapshot_sha256':m.sha(initial)})+'\n',encoding='utf8')
_,roots,snaps,items=m.inventory({'source_tick':9,'source_snapshot_sha256':m.sha(a)})
test('three_trees_and_two_checkpoints_including_import',len(roots)==3 and len(snaps)==2)
test('empty_directories_manifested',sum(v['kind']=='directory'and v['relative'].endswith('EMPTY_FAKE_DIRECTORY')for v in items)==3)
test('source_fake_inventory_not_moved',all(p.exists()for p in(*roots,*snaps)))
(folder/'HISTORIA.jsonl').write_text(json.dumps({'snapshot_sha256':m.sha(a),'previous_snapshot_sha256':'MISSING'})+'\n',encoding='utf8')
try:m.inventory({'source_tick':9,'source_snapshot_sha256':m.sha(a)})
except ValueError:test('missing_historical_checkpoint_blocks_move',True)
else:raise AssertionError('Incomplete history accepted')
for p in('/absolute','../bad','app/../bad','C:/bad','app\\bad'):
 try:m.relative(p)
 except ValueError:test('unsafe_relative_rejected_'+p,True)
 else:raise AssertionError('Unsafe path accepted')
# Extract only OriginalBackend.import_new as a pure function: true flag must
# refuse before any root/manager/import side effect can be touched.
file=H/'PI07_LAUNCHER_EXISTENTE_PREPARADO/app/usar_dee.py';tree=ast.parse(file.read_bytes());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='OriginalBackend');fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name=='import_new');ns={};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'FAKE_ONLY_LAUNCHER_GUARD','exec'),ns)
class Fake:
 config={'existing_continuation_only':True}
try:ns['import_new'](Fake(),'NO_NEW_WORLD')
except ValueError:test('existing_only_launcher_refuses_before_import',True)
else:raise AssertionError('New import was allowed')
test('no_DEE_or_app_import',not any(n=='app'or n.startswith(('app.','dee_thinking'))for n in sys.modules))
out=P/'control/PI07_TRASLADO_PRUEBAS_PURAS_R01.json'
with out.open('x',encoding='utf8')as f:json.dump({'schema':'DEE.PI07.same_identity_relocation.pure_tests.v1','tests':tests,'passed':len(tests),'helper_sha256':hashlib.sha256((H/'incorporar_PI07_misma_identidad.py').read_bytes()).hexdigest(),'identity_adapter_sha256':hashlib.sha256((H/'pi07_identidad_c2c_R02.py').read_bytes()).hexdigest(),'launcher_guard_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'Native_executed':False,'actual_move_or_promotion':False,'product_or_S7_modified':False,'scope':'Fake path inventory/history closure, one-leaf proposal, strict nonadministrative comparison and pure launcher early refusal only. Actual Store/reopening/selected operation remain Root gates.'},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'proof':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'passed':len(tests),'Native_executed':False}))
