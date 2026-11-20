"""Preflight R06 puro: SDK y dependencia empaquetada; no importa Native."""
from pathlib import Path
import argparse,hashlib,json,runpy,sys,io,contextlib
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sdk-only',action='store_true');p.add_argument('--runtime-root',type=Path);p.add_argument('--verificar-fuentes',action='store_true');a=p.parse_args()
 sdk=ROOT/'sdk/0.1.1';script=sdk/'herramientas/ensamblar_publico_R06.py';saved=sys.argv;sys.argv=[str(script),'verify','--root',str(sdk)];out=io.StringIO()
 try:
  with contextlib.redirect_stdout(out):
   try:runpy.run_path(str(script),run_name='__main__')
   except SystemExit as e:
    if e.code not in(None,0):raise RuntimeError('SDK verification failed')
 finally:sys.argv=saved
 result={'sdk':json.loads(out.getvalue()),'NativeImported':False,'newTicks':0,'fallbackUsed':False}
 if not a.sdk_only:
  m=json.loads((ROOT/'dependencias/MANIFIESTO_RUNTIME_R06.json').read_text('utf-8'));f=ROOT/'dependencias'/m['payload']['file'];h=hashlib.sha256()
  with f.open('rb')as stream:
   for b in iter(lambda:stream.read(1048576),b''):h.update(b)
  assert f.stat().st_size==m['payload']['bytes']and h.hexdigest()==m['payload']['sha256']
  result.update(payloadIntegrity=True,manifestFiles=len(m['files']),authentication='NOT_PROVISIONED',Native='PENDING_SESSION_OR_TEST')
  if a.runtime_root:result['runtimeMarkerPresent']=(a.runtime_root/'INSTALACION_ROBLOX_R06.json').is_file()
 print(json.dumps(result,ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
