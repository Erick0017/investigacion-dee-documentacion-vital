"""Carry and test the exact master bytes, without scientific or operational state files."""
from pathlib import Path
import zipfile,hashlib,json,shutil,datetime
from verificar_archivo import verify
H=Path(__file__).resolve().parent;R=H.parent
master=R/'DEE_Cognitive_5min_MASTER_1080p_ES_ENsub.mp4'
digest=hashlib.sha256(master.read_bytes()).hexdigest();size=master.stat().st_size
check=json.loads((H/'verificacion'/(master.stem+'_VERIFICACION.json')).read_text('utf8'))
assert check['sha256']==digest and check['all_required_checks']
receipt=f'''DEE Cognitive — máster original de cinco minutos

Archivo: {master.name}
Tamaño exacto: {size} bytes
SHA-256: {digest}
Duración de presentación: 300.000000 s
Imagen: 1920 x 1080 nativos; 30 fps constantes; 9000 fotogramas; SAR 1:1.
Video: H.264, yuv420p. Audio: AAC, 48 kHz, estéreo, español.
Subtítulos ingleses integrados en la imagen.

Este ZIP transporta los mismos bytes del MP4 local verificado. No es una nueva
codificación ni un respaldo del ente. No contiene snapshots, código científico,
credenciales ni los datos privados usados para la representación audiovisual.

Después de descargar y extraer, compare tamaño y SHA-256 con estos valores.
La copia descargada por el destinatario no ha sido inspeccionada: transferencia
no verificada. La resolución de una miniatura o previsualización no sustituye
la verificación del archivo extraído.
'''
zp=R/'DEE_Cognitive_5min_MASTER_1080p_DESCARGA_ORIGINAL.zip'
assert not zp.exists(),'Preserve an existing sealed candidate first.'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 z.write(master,master.name);z.writestr('INTEGRIDAD_MASTER.txt',receipt.encode('utf8'))
ext=H/'verificacion_extraccion';ext.mkdir(exist_ok=False)
with zipfile.ZipFile(zp) as z:
 assert z.namelist()==[master.name,'INTEGRIDAD_MASTER.txt'];assert z.testzip() is None
 for name in z.namelist():
  with z.open(name) as src,(ext/name).open('wb') as dst:shutil.copyfileobj(src,dst)
assert hashlib.sha256((ext/master.name).read_bytes()).hexdigest()==digest
result=verify(ext/master.name,ext/'resultados')
assert result['sha256']==digest and result['all_required_checks']
rec={'created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'zip':str(zp),'bytes':zp.stat().st_size,
 'sha256':hashlib.sha256(zp.read_bytes()).hexdigest(),'members':[master.name,'INTEGRIDAD_MASTER.txt'],
 'CRC_all_members_ok':True,'extracted_master_sha256':digest,'extracted_master_verification':result,
 'user_received_copy':'TRANSFERENCIA_NO_VERIFICADA'}
(H/'verificacion/VERIFICACION_ZIP_EXACTO.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({k:rec[k] for k in ['zip','bytes','sha256','CRC_all_members_ok']}),flush=True)
