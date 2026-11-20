"""Open one allowlisted R06 local scene with a hidden window; no Native backend."""
from pathlib import Path
import argparse,json,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
STUDIO=Path('C:/Users/Erik/AppData/Local/Roblox/Versions/version-63eb6055af4e4688/RobloxStudioBeta.exe')
ALLOWED={'native':ROOT/'mundo/DEE_RBX01_INTEGRAL_V2_NATIVE.rbxlx',
 'programmed':ROOT/'mundo/DEE_RBX01_INTEGRAL_V2_PROGRAMMED.rbxlx',
 'ai':ROOT/'mundo/DEE_RBX01_INTEGRAL_V2_AI.rbxlx',
 'prototype':ROOT/'prototipo/exportado/DEEConnector_ESCENA_MINIMA_R06.rbxlx',
 'prototype_native':ROOT/'prototipo/NATIVE_LIMPIO_R01/DEEConnector_NATIVE_LIMPIO_R01.rbxlx'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--scene',required=True,choices=ALLOWED);a=p.parse_args()
 target=ALLOWED[a.scene].resolve(strict=True);assert target.is_relative_to(ROOT) and not target.is_symlink()
 startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
 child=subprocess.Popen([str(STUDIO),str(target)],startupinfo=startup,creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
 with(ROOT/'control/GUI_APERTURAS_R06.jsonl').open('a',encoding='utf8')as f:
  f.write(json.dumps({'time':time.time(),'scene':a.scene,'path':str(target),'pid':child.pid,'Native_started':False})+'\n')
 print(json.dumps({'pid':child.pid,'scene':str(target),'Native_started':False}))
