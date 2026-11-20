"""Sólo configura una copia instalada con una credencial aportada por su propietario."""
from pathlib import Path
import argparse,json,os
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime',type=Path,required=True);p.add_argument('--token-file',type=Path,required=True);p.add_argument('--autorizar-configuracion',action='store_true');a=p.parse_args()
if not a.autorizar_configuracion:raise SystemExit('Se exige autorización explícita de configuración. No se genera ninguna credencial.')
root=a.runtime.resolve(strict=True)
if not(root/'INSTALACION_ROBLOX_R06.json').is_file():raise ValueError('Only a new R06 installation; never the source runtime')
for q in(root,*root.parents):
 if q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024:raise ValueError('No reparse')
target=root/'configuracion/CONEXION_PRIVADA.json'
if target.exists():raise FileExistsError('No overwrite/rotation of existing credentials')
token=a.token_file.read_text('utf-8-sig').strip()
if len(token)<32 or any(x.isspace()for x in token)or token.startswith('PROPORCIONAR_'):raise ValueError('Owner-supplied credential required')
with target.open('x',encoding='utf-8')as f:json.dump({'schema':'DEE.Roblox.SDK.private.0.1.0','bind':'127.0.0.1','port':8896,'token':token},f)
print(json.dumps({'configured':True,'tokenPrinted':False,'credentialGenerated':False,'NativeOpened':False,'sessionAdmitted':False,'scope':'Configuration only. Requires a separately authorized prospective Native protocol and matched pair.'}))
