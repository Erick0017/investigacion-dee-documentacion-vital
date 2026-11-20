"""Normalización no destructiva de SAR del maestro limpio. No recodifica imágenes."""
from pathlib import Path
import json, subprocess, hashlib, os
from datetime import datetime,timezone
W=Path(__file__).resolve().parent
TEST=next(p for p in W.parents if (p/'_dee20_trabajo').is_dir())
FF=TEST/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def cmd(label,args):
 p=subprocess.run([str(FF),'-v','error','-nostdin']+list(map(str,args)),capture_output=True,text=True,check=True)
 (W/'qc'/('sar_'+label+'.log')).write_text(p.stdout+p.stderr,encoding='utf8')
 return p.stdout.strip()
path=W/'REGISTRO_R03.json';rec=json.loads(path.read_text(encoding='utf8'))
old=W/'montaje_limpio_R03.mp4';new=W/'montaje_limpio_R03_sar1_candidato.mp4'
assert not new.exists()
cmd('remux',['-n','-i',old,'-map','0','-c','copy','-bsf:v','h264_metadata=sample_aspect_ratio=1/1','-movflags','+faststart',new])
hashes={}
for label,p in [('before',old),('after',new)]:
 hashes[label]={
 'VCL':cmd('vcl_'+label,['-i',p,'-map','0:v:0','-c:v','copy','-bsf:v','filter_units=pass_types=1-5','-f','hash','-hash','sha256','-']),
 'AAC':cmd('aac_'+label,['-i',p,'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'])}
assert hashes['before']==hashes['after'],hashes
backup=W/'revisiones/maestro_limpio_antes_SAR1.mp4'
assert not backup.exists()
before=dict(path=str(old),bytes=old.stat().st_size,sha256=sha(old))
os.replace(old,backup);os.replace(new,old)
rec['quality'].setdefault('validation_history',[]).append(rec['quality']['final_validation'])
rec['quality']['clean_master_SAR_correction']={
 'utc':datetime.now(timezone.utc).isoformat(),
 'reason':'El final tenía SAR1:1 yDAR16:9 correctos. El maestro auxiliar había omitido el metadatoSAR y su comprobación estricta falló.',
 'method':'H264_metadata sample_aspect_ratio1/1 y remux copy; sin recodificación ni cambio de imágenes/audio.',
 'before':before,'preserved_before_at':str(backup),'after':dict(path=str(old),bytes=old.stat().st_size,sha256=sha(old)),
 'full_VCL_and_AAC_hashes_equal':hashes,
 'scope':'Se repite probe_clean y comparaciónAAC. El video final no cambia. DecodificaciónVCL yAAC del maestro son idénticos salvo SPS descriptivoSAR; revisión visual/SSIM previa permanece aplicable.'
}
path.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('CLEAN_SAR_NORMALIZED',hashes,flush=True)
