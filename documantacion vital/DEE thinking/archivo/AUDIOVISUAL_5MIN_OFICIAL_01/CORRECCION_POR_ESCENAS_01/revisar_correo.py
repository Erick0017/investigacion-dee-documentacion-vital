"""Extract paired encoded-file samples for visual inspection, including phone scale."""
from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;T=next(x for x in H.parents if x.name=='tests')
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
master=H/'DEE_Cognitive_5min_MASTER_CORREGIDO_1080p_ES_ENsub.mp4'
email=H/'DEE_Cognitive_5min_CORREO_CORREGIDO_1080p_ES_ENsub.mp4'
if not email.exists():email=H/'DEE_Cognitive_5min_CORREO_CORREGIDO_720p_ES_ENsub.mp4'
out=H/'correo/revision';out.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',32)
times=[12,35,61,79,101,119,142,161,180,204,218,241,264,292]
index=[]
for n,t in enumerate(times,1):
 images=[]
 for tag,p in [('MASTER',master),('CORREO',email)]:
  dst=out/f'S{n:02}_{tag}.png'
  r=subprocess.run([str(FF),'-v','error','-y','-ss',str(t),'-i',str(p),'-frames:v','1',str(dst)],capture_output=True)
  assert r.returncode==0,r.stderr
  images.append(Image.open(dst).convert('RGB'))
 pair=Image.new('RGB',(1920,1200),(7,19,29));d=ImageDraw.Draw(pair)
 for j,im in enumerate(images):
  pair.paste(im.resize((960,540),Image.Resampling.LANCZOS),(960*j,90));d.text((960*j+30,30),['MASTER','CORREO'][j],font=font,fill=(232,244,243))
  pair.paste(im.resize((426,240),Image.Resampling.LANCZOS),(960*j+267,700))
 pair.save(out/f'PAR_S{n:02}.png')
 index.append({'scene':n,'time_master_seconds':t,'comparison':f'PAR_S{n:02}.png','native_samples':[f'S{n:02}_MASTER.png',f'S{n:02}_CORREO.png'],'phone_size':[426,240]})
(out/'INDICE.json').write_text(json.dumps({'source_master':str(master),'source_mail':str(email),'samples':index,'review':'PENDING_MODEL_INSPECTION','scope':'Samples for image/legibility; not an automatic comprehension verdict.'},ensure_ascii=False,indent=2),'utf8')
print('Fourteen encoded delivery comparisons extracted.',flush=True)
