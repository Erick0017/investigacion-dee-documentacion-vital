"""Objective and selected visual comparisons; neither is a human quality certification."""
from pathlib import Path
import subprocess,json,re,hashlib,math
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parent;T=next(x for x in H.parents if x.name=='tests')
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
master=R/'DEE_Cognitive_5min_MASTER_1080p_ES_ENsub.mp4';mail=R/'DEE_Cognitive_5min_CORREO_1080p_ES_ENsub.mp4'
out=H/'QA_CORREO';out.mkdir(exist_ok=True);times=[4,57,114.8,139,154,183,198,237,267,295]
items=[]
for i,t in enumerate(times):
 for label,p in [('MASTER',master),('CORREO',mail)]:
  target=out/f'{label}_{i:02}.png';subprocess.run([str(FF),'-v','error','-y','-ss',str(t),'-i',str(p),'-frames:v','1',str(target)],capture_output=True,check=True)
  items.append({'source':label,'time':t,'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
sheet=Image.new('RGB',(1920,360*math.ceil(len(times)/3)),(7,19,29))
for i,t in enumerate(times):
 im=Image.open(out/f'CORREO_{i:02}.png').resize((640,360),Image.Resampling.LANCZOS);sheet.paste(im,((i%3)*640,(i//3)*360))
sheet.save(out/'CONTACTO_CORREO.png')
cmd=[str(FF),'-hide_banner','-i',str(master),'-i',str(mail),'-filter_complex','[0:v:0][1:v:0]ssim=stats_file=correo_ssim_frames.log',
 '-an','-f','null','-']
r=subprocess.run(cmd,cwd=out,capture_output=True);(out/'SSIM.log').write_bytes(r.stderr);assert r.returncode==0
lines=(out/'correo_ssim_frames.log').read_text('utf8').splitlines();assert len(lines)==9000
scores=[float(re.search(r'All:([0-9.]+)',x).group(1)) for x in lines]
rec={'master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'email_sha256':hashlib.sha256(mail.read_bytes()).hexdigest(),
 'sampled_frames':items,'SSIM_frames':len(scores),'SSIM_min':min(scores),'SSIM_mean':sum(scores)/len(scores),'command':cmd,
 'scope':'SSIM quantifies encoding differences only; it does not establish scientific or perceptual approval.'}
(out/'COMPARACION.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({k:rec[k] for k in ['SSIM_frames','SSIM_min','SSIM_mean']}),flush=True)
