from pathlib import Path
import subprocess,json,math
from PIL import Image
H=Path(__file__).resolve().parent;OLD=H.parent/'trabajo';T=next(x for x in H.parents if x.name=='tests')
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
blocks=json.loads((H/'herramientas/guion.json').read_text('utf8'))['blocks']
for n in [1,2,14]:
 b=blocks[n-1];d=H/f'escenas/S{n:02}/inspeccion_original';d.mkdir(exist_ok=True);rows=[]
 times=sorted(set([b['duration_s']*q for q in [.15,.4,.65,.9]]+[x*.5 for x in range(math.ceil(b['duration_s']*2))]))
 for i,t in enumerate(times):
  p=d/f'F{i:03}.png';subprocess.run([str(FF),'-v','error','-y','-ss',str(t),'-i',str(OLD/f'clips/S{n:02}.mp4'),'-frames:v','1',str(p)],capture_output=True,check=True)
  rows.append({'time':t,'file':str(p)})
 for base in range(0,len(rows),12):
  group=rows[base:base+12];sheet=Image.new('RGB',(1920,360*math.ceil(len(group)/3)),(7,19,29))
  for i,r in enumerate(group):sheet.paste(Image.open(r['file']).resize((640,360),Image.Resampling.LANCZOS),((i%3)*640,(i//3)*360))
  sheet.save(d/f'SECUENCIA_{base//12:02}.png')
 (d/'INDICE.json').write_text(json.dumps({'scene':n,'voice':b['literal_ES'],'start_in_master':b['start_s'],'samples':rows},ensure_ascii=False,indent=2),'utf8')
 print('Conserved candidate inspected sequence generated',n,flush=True)
