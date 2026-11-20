"""Read-only encoded-video QA extraction. No renderer, engine or scene imports."""
from pathlib import Path
import sys,json,hashlib,subprocess,datetime
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
TESTS=next(x for x in R.parents if x.name=='tests')
FF=TESTS/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
PROBE=TESTS/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
DUR={'S03':32,'S05':22,'S06':28,'S07':22,'S08':22,'S10':20}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 for scene in sys.argv[1:]:
  src=R/'escenas'/(scene+'.mp4')
  if not src.is_file():print(json.dumps({'scene':scene,'status':'not_closed_yet'}),flush=True);continue
  out=R/'previas/QA_CODIFICADO'/scene;out.mkdir(parents=True,exist_ok=True)
  idx=out/'extraccion.json'
  if idx.exists():
   v=json.loads(idx.read_text(encoding='utf8'));assert v['source_sha256']==sha(src);print(json.dumps({'scene':scene,'already_extracted':True}),flush=True);continue
  probe=json.loads(subprocess.check_output([str(PROBE),'-v','error','-show_streams','-show_format','-of','json',str(src)]))
  v=next(x for x in probe['streams'] if x['codec_type']=='video')
  assert int(v['width'])==1920 and int(v['height'])==1080 and int(v['nb_frames'])==DUR[scene]*30
  assert abs(float(v['duration'])-DUR[scene])<.001
  cmd=[str(FF),'-hide_banner','-v','error','-n','-threads','1','-i',str(src),'-map','0:v:0','-an','-sn','-vf','select=not(mod(n\\,30))','-fps_mode','vfr','-start_number','0',str(out/'t_%03d.png')]
  run=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  if run.returncode:raise RuntimeError(run.stderr)
  files=sorted(out.glob('t_*.png'));assert len(files)==DUR[scene]
  font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
  sheets=[]
  for start in range(0,len(files),12):
   rows=(len(files[start:start+12])+3)//4;sheet=Image.new('RGB',(1920,rows*300),'#07131D');d=ImageDraw.Draw(sheet)
   for j,p in enumerate(files[start:start+12]):
    im=Image.open(p);assert im.size==(1920,1080);sheet.paste(im.resize((480,270)),((j%4)*480,(j//4)*300))
    d.text(((j%4)*480+12,(j//4)*300+273),f'{scene} t={start+j}s',font=font,fill='white')
   p=out/f'progresion_{start:03d}_{min(start+11,len(files)-1):03d}.png';sheet.save(p);sheets.append({'path':p.relative_to(R).as_posix(),'sha256':sha(p)})
  record={'schema':'DEE.R05.encoded_QA_frames.R01','scene':scene,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':src.relative_to(R).as_posix(),'source_sha256':sha(src),'source_bytes':src.stat().st_size,'video_probe':v,'method':'Exact decoded original frame n=30*t, t integer seconds. Contact sheets only editorial overview; individual causal points reviewed separately. No continuous human playback or listening certified.','frames':[{'time_seconds':i,'frame_number':30*i,'path':p.relative_to(R).as_posix(),'sha256':sha(p)}for i,p in enumerate(files)],'sheets':sheets,'native_ticks':0,'render_GPU':False}
  idx.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
  print(json.dumps({'scene':scene,'frames':len(files),'index':str(idx),'source_sha256':record['source_sha256']}),flush=True)
if __name__=='__main__':main()
