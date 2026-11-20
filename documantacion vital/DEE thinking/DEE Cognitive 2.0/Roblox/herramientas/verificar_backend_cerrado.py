"""Resolución del backend instalado y estado cerrado; ninguna instancia Native."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,sys,time
p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,required=True);p.add_argument('--denegar',action='append',default=[]);a=p.parse_args();root=a.runtime.resolve(strict=True)
forbidden=[os.path.normcase(str(Path(x).absolute()))for x in a.denegar]
def hook(event,args):
 if event in('subprocess.Popen','socket.connect','socket.bind','os.system'):raise PermissionError('No processes/network in closed backend inspection')
 if event=='import'and args and str(args[0]).startswith(('dee_thinking','dee_universe')):raise PermissionError('No Native import')
 if event in('open','os.scandir','os.listdir')and args and isinstance(args[0],(str,bytes,os.PathLike)):
  name=os.path.normcase(os.path.abspath(os.fsdecode(args[0])))
  if any(name==x or name.startswith(x+os.sep)for x in forbidden):raise PermissionError('Original installation denied')
sys.addaudithook(hook)
spec=importlib.util.spec_from_file_location('isolated_common_r06',root/'backend/r06/sdk_common.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
assert module.RUNTIME==root,'Runtime resolver escaped installed location'
marker=json.loads((root/'INSTALACION_ROBLOX_R06.json').read_text('utf-8'));desc=marker['closedNative'];id=desc['lifeId'].removeprefix(module.LIFE_PREFIX)
home,cfg=module.instance_home(id);proof=module.closed_native(home,cfg)
assert proof==desc,'Closed installed state differs from packaged cut'
window=module.budget(now=0)
assert time.time()>window['hardFinishUtcEpoch'],'Do not call this an authorized open window'
try:module.validate_pair(home,cfg,proof)
except(ValueError,KeyError)as error:pair={'status':'KNOWN_PRE_CAP_NOT_CURRENT','exception':type(error).__name__,'reason':str(error)}
else:raise AssertionError('Unexpected current pair; inspect without starting')
required=['backend/r06/sdk_owner.py','backend/r06/native_factory.py','backend/extension_r06_R04/servicio_capabilities_http_R06.py','dependencias/producto/reproducibilidad/propietario_diagnostico.py','estado_demo/prefijos/PAR28_COMPLETO/EXPORTACION_SERVICIO.json']
assert all((root/n).is_file()for n in required)
print(json.dumps({'backendRoot':str(module.RUNTIME),'closedNative':proof,'pair':pair,'windowExpired':True,'authenticationProvided':(root/'configuracion/CONEXION_PRIVADA.json').exists(),'ordinarySessionReady':False,'closedInspectionPassed':True,'requiredComponentsPresent':required,'ownersOpened':0,'newTicks':0,'NativeImported':False},ensure_ascii=False))
