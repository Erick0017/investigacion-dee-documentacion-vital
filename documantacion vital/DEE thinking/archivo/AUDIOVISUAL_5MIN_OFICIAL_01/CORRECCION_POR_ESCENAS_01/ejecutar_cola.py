"""Run only requested local scene preview/render/comparison operations.
This fixed entry point cannot execute arbitrary commands or operate DEE.
"""
from pathlib import Path
import sys,json,subprocess,datetime,hashlib
H=Path(__file__).resolve().parent
items=json.loads((H/'EJECUCION_SOLICITADA.json').read_text('utf-8-sig'))
assert isinstance(items,list) and 0<len(items)<=14
log=H/'ejecuciones';log.mkdir(exist_ok=True)
for item in items:
 n=item['scene'];op=item['operation'];assert isinstance(n,int) and 1<=n<=14 and n!=7
 assert op in ['preview','render','compare','audio']
 module=H/f'escenas/S{n:02}/escena.py';assert module.is_file()
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f')
 if op=='audio':cmd=[sys.executable,'-B','-X','utf8',str(H/'herramientas/contexto_audio.py'),str(n)]
 else:cmd=[sys.executable,'-B','-X','utf8',str(H/'herramientas/escena_base.py'),str(module),'--'+op]
 source=module.read_bytes();(log/f'{stamp}_S{n:02}_{op}_escena.py').write_bytes(source)
 print('START',n,op,flush=True)
 r=subprocess.run(cmd,capture_output=True)
 (log/f'{stamp}_S{n:02}_{op}.log').write_bytes(r.stdout+b'\n'+r.stderr)
 print(r.stdout.decode('utf8','replace'),flush=True)
 print('END',n,op,'code',r.returncode,flush=True)
 if r.returncode:
  print(r.stderr.decode('utf8','replace')[-2500:],flush=True);raise SystemExit(r.returncode)
