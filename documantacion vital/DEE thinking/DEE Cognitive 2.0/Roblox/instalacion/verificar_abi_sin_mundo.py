"""Carga ABI/metadatos únicamente: no construye Runtime, World ni propietarios."""
from pathlib import Path
import argparse,hashlib,importlib,json,os,struct,sys
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime',type=Path,required=True);p.add_argument('--denegar',action='append',default=[]);a=p.parse_args();root=a.runtime.resolve(strict=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def machine(p):
 with p.open('rb')as f:
  if f.read(2)!=b'MZ':raise ValueError('Not PE')
  f.seek(60);offset=struct.unpack('<I',f.read(4))[0];f.seek(offset)
  if f.read(4)!=b'PE\0\0':raise ValueError('No PE signature')
  return struct.unpack('<H',f.read(2))[0]
assert sys.version_info[:2]==(3,13)and struct.calcsize('P')==8
site=root/'dependencias/producto/motor/python313/site-packages';pyds=list((site/'dee_thinking').glob('_native*.pyd'));assert len(pyds)==1
assert machine(Path(sys.executable))==0x8664 and machine(pyds[0])==0x8664
marker=json.loads((root/'INSTALACION_ROBLOX_R06.json').read_text('utf-8'));desc=marker['closedNative'];home=root/'estado_demo/instancias'/desc['lifeId'].removeprefix('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_')
card=home/'sistema/estado/vidas'/desc['lifeId']/'VIDA.json';data=json.loads(card.read_text('utf-8'));snapshot=home/'sistema'/data['snapshot'];db=home/'sistema/estado/servicios_persistentes'/desc['lifeId']/'cola.sqlite3'
anchors={str(q):sha(q)for q in(card,snapshot,db,root/'estado_demo/LEDGER_SDK_R06.json')}
assert anchors[str(card)]==desc['cardSha256']and anchors[str(snapshot)]==desc['snapshotSha256']and anchors[str(db)]==desc['databaseSha256']
forbidden=[os.path.normcase(str(Path(x).absolute()))for x in a.denegar];reads=[]
def hook(event,args):
 if event in('open','os.scandir','ctypes.dlopen','os.add_dll_directory')and args and isinstance(args[0],(str,bytes,os.PathLike)):
  name=os.path.normcase(os.path.abspath(os.fsdecode(args[0])))
  if any(name==x or name.startswith(x+os.sep)for x in forbidden):reads.append(name);raise PermissionError('Original installation denied')
 if event=='open'and len(args)>1 and isinstance(args[0],(str,bytes,os.PathLike)):
  name=Path(os.path.abspath(os.fsdecode(args[0])));mode=args[1]
  writing=isinstance(mode,str)and any(x in mode for x in('w','a','x','+'))
  if writing and name.is_relative_to(root/'estado_demo'):raise PermissionError('No state writes in ABI probe')
sys.addaudithook(hook)
sys.path.insert(0,str(site));module=importlib.import_module('dee_thinking')
assert Path(module.__file__).resolve().is_relative_to(root)
assert module.__version__=='4.5.0';identity=module.kernel_identity();assert identity['kernel_version']==27
assert not reads
for name,value in anchors.items():assert sha(Path(name))==value,'State anchor changed during import'
result={'abi_import':'VALIDATED','thinking':module.__version__,'kernel_version':identity['kernel_version'],'python':sys.version.split()[0],'architecture':'AMD64/PE8664/cp313','native_module':str(pyds[0]),'native_module_sha256':sha(pyds[0]),'original_reads_attempted':len(reads),'worldFactoriesInvokedByProbe':[],'ownersOpened':0,'ticksAdvanced':0,'stateAnchorsUnchanged':True,'functionalNativeContinuity':'PENDING_NEW_SESSION_OR_TEST','credentialRead':False}
print(json.dumps(result,ensure_ascii=False))
