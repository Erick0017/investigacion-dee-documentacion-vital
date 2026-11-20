"""Extract native encoded frames for the opening, model and conclusion."""
from pathlib import Path
import subprocess,json,hashlib,math
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;T=next(x for x in H.parents if x.name=='tests')
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
out=H/'QA_ROOT';out.mkdir(exist_ok=True)
pre=json.loads((H/'PREVISUALIZACION.json').read_text('utf8'))
blocks=json.loads((H/'audio/guion.json').read_text('utf8'))['blocks'];records=[]
for scene in [1,2,14]:
 b=blocks[scene-1];src=H/f'clips/S{scene:02}.mp4';rows=[]
 for row in pre:
  if row['shot'].startswith(f'S{scene:02}_'):
   p=out/(row['shot']+'.png');t=row['time']-b['start_s']
   cmd=[str(FF),'-v','error','-y','-ss',str(t),'-i',str(src),'-frames:v','1',str(p)]
   subprocess.run(cmd,check=True,capture_output=True)
   im=Image.open(p);assert im.size==(1920,1080)
   r={'shot':row['shot'],'source_clip':str(src),'film_time':row['time'],'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()};rows.append(r);records.append(r)
 sheet=Image.new('RGB',(1920,360*math.ceil(len(rows)/3)),(7,19,29))
 for i,r in enumerate(rows):
  im=Image.open(r['file']).resize((640,360),Image.Resampling.LANCZOS);sheet.paste(im,(i%3*640,i//3*360))
 sheet.save(out/f'CONTACTO_S{scene:02}.png')
(out/'INDICE.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),'utf8')
print('Extracted',len(records),'encoded native frames.',flush=True)
