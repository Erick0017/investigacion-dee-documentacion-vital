"""Localiza/verifica archivos del despliegue privado. No inicia servicios ni Native."""
from pathlib import Path
import argparse,datetime,json,sys
def inspect(root):
 root=Path(root).absolute()
 if not root.is_dir():raise ValueError('RUNTIME_NOT_FOUND_NO_FALLBACK')
 for p in (root,*root.parents):
  if p.is_symlink() or getattr(p.lstat(),'st_file_attributes',0)&1024:raise ValueError('RUNTIME_REPARSE_REFUSED')
 required=['backend/servicio_sdk.py','backend/sdk_cli.py','backend/native_factory.py',
  'dependencias/producto/motor/python313/python.exe','dependencias/SDK_SOURCES.json',
  'estado_demo/instancias','configuracion/CONEXION_PRIVADA.json']
 rows=[{'relative':p,'exists':(root/p).exists()} for p in required]
 pyds=list((root/'dependencias/producto/motor/python313/site-packages/dee_thinking').glob('_native*.pyd'))
 return {'schema':'DEE.Roblox.RuntimeLocator.R02','runtime':str(root),'required':rows,
  'oneNativePYDPresent':len(pyds)==1,'filesPresent':all(p['exists'] for p in rows) and len(pyds)==1,
  'NativeImported':False,'worldOpened':False,'databaseOpened':False,'httpRequested':False,
  'tokenRead':False,'materialReadinessVerified':False,'startOrContinueAllowedByThisTool':False}
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--runtime-root',type=Path,help='Ruta corta explícita en otra computadora; no se escribe ni se instala nada.')
 args=parser.parse_args()
 locator=Path(__file__).resolve().parents[1]/'LOCALIZADORES.json'
 cfg=json.loads(locator.read_text('utf-8-sig'))
 if cfg.get('fallbackToProvisionBundle') is not False:raise ValueError('NO_PROVISION_FALLBACK')
 result=inspect(args.runtime_root or cfg['operationalRuntime'])
 deadline=datetime.datetime.fromisoformat(cfg['closed_validation_window_utc'].replace('Z','+00:00'))
 result['historicalValidationWindowExpired']=datetime.datetime.now(datetime.timezone.utc)>deadline
 print(json.dumps(result,ensure_ascii=False,indent=2))
 return 0 if result['filesPresent'] else 2
if __name__=='__main__':
 try:raise SystemExit(main())
 except (OSError,ValueError,KeyError) as e:
  print(json.dumps({'verified':False,'errorClass':type(e).__name__,'NativeImported':False,'fallbackUsed':False}),file=sys.stderr)
  raise SystemExit(2)
