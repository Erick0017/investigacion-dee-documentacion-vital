"""Decode and play only the two20s S07 deliverables on localhost."""
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import subprocess,json,hashlib,datetime,math
from PIL import Image
H=Path(__file__).resolve().parent;T=next(x for x in H.parents if x.name=='tests')
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
FILES={'/antes.mp4':H/'DEE_S07_ANTES.mp4','/despues.mp4':H/'DEE_S07_DESPUES_1080p.mp4'}
QA=H/'QA_VISUAL';QA.mkdir(exist_ok=True)
for key,p in FILES.items():assert p.exists()
times=[.2,1.6,2.6,3.7,4.7,6.2,7.6,8.5,9.8,11.4,12.8,14.8,17.9,19.7];rows=[]
for i,t in enumerate(times):
 p=QA/f'DESPUES_{i:02}_{t:05.2f}.png'
 subprocess.run([str(FF),'-v','error','-y','-ss',str(t),'-i',str(FILES['/despues.mp4']),'-frames:v','1',str(p)],capture_output=True,check=True)
 assert Image.open(p).size==(1920,1080);rows.append({'time':t,'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
sheet=Image.new('RGB',(1920,360*math.ceil(len(rows)/3)),(7,19,29))
for i,r in enumerate(rows):sheet.paste(Image.open(r['file']).resize((640,360),Image.Resampling.LANCZOS),((i%3)*640,(i//3)*360))
sheet.save(QA/'CONTACTO_CODIFICADO.png');(QA/'FOTOGRAMAS.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf8')
PAGE='''<!doctype html><html lang="es"><meta charset="utf-8"><title>DEE — S07 antes y después</title>
<style>body{background:#07131d;color:white;margin:16px;font:18px system-ui}button{font-size:20px;padding:10px}.pair{display:flex;gap:12px}section{width:50%}video{width:100%;display:block}pre{font-size:13px;white-space:pre-wrap}h2{font-size:20px}</style>
<h1>Escena07 · comparación local completa · 20segundos</h1><button id="go">Reproducir ambos desde el inicio</button>
<p>Audio: DESPUÉS. ANTES permanece silenciado para evitar duplicación.</p>
<div class="pair"><section><h2>ANTES · montaje original</h2><video id="a" src="/antes.mp4" controls preload="auto" muted playsinline></video></section>
<section><h2>DESPUÉS · corrección aislada</h2><video id="b" src="/despues.mp4" controls preload="auto" playsinline></video></section></div><pre id="stats">Cargando…</pre>
<script>const a=document.querySelector('#a'),b=document.querySelector('#b'),s=document.querySelector('#stats');let started=null,events=[];
function one(v){let q=v.getVideoPlaybackQuality();return {time:v.currentTime,duration:v.duration,width:v.videoWidth,height:v.videoHeight,ended:v.ended,paused:v.paused,muted:v.muted,rate:v.playbackRate,total:q.totalVideoFrames,dropped:q.droppedVideoFrames,corrupt:q.corruptedVideoFrames||0,error:v.error?{code:v.error.code,message:v.error.message}:null}}
function data(){return {antes:one(a),despues:one(b),events,wallSeconds:started?(performance.now()-started)/1000:null}}
function update(){s.textContent=JSON.stringify(data(),null,2)}
for(let v of [a,b])for(let n of ['loadedmetadata','playing','waiting','stalled','seeking','seeked','pause','ended','error'])v.addEventListener(n,()=>{events.push({video:v.id,event:n,time:v.currentTime,wall:performance.now()});update();if(a.ended&&b.ended)fetch('/receipt',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data())})});
document.querySelector('#go').onclick=()=>{a.currentTime=0;b.currentTime=0;a.muted=true;b.muted=false;b.volume=.9;a.playbackRate=b.playbackRate=1;started=performance.now();a.play();b.play()};setInterval(update,500);</script></html>'''.encode('utf8')
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_GET(self):
  if self.path=='/':self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(PAGE)));self.end_headers();self.wfile.write(PAGE);return
  if self.path not in FILES:self.send_error(404);return
  p=FILES[self.path];size=p.stat().st_size;start=0;end=size-1;partial='Range' in self.headers
  if partial:
   a,b=self.headers['Range'].removeprefix('bytes=').split('-');start=int(a or 0);end=min(int(b) if b else size-1,size-1)
  self.send_response(206 if partial else 200);self.send_header('Content-Type','video/mp4');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1))
  if partial:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  self.end_headers()
  try:
   with p.open('rb') as f:
    f.seek(start);remaining=end-start+1
    while remaining:
     b=f.read(min(262144,remaining));self.wfile.write(b);remaining-=len(b)
  except (BrokenPipeError,ConnectionResetError):pass
 def do_POST(self):
  if self.path!='/receipt':self.send_error(404);return
  obj=json.loads(self.rfile.read(int(self.headers['Content-Length'])));obj['files']=[{'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in FILES.values()]
  obj['received_UTC']=datetime.datetime.now(datetime.timezone.utc).isoformat();obj['scope']='Local browser playback only, no claim of human hearing, audience approval or remote transfer.'
  (QA/'REPRODUCCION_COMPLETA.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2),'utf8')
  self.send_response(200);self.send_header('Content-Length','2');self.end_headers();self.wfile.write(b'OK')
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);url=f'http://127.0.0.1:{server.server_port}/';print(url,flush=True)
(QA/'URL.txt').write_text(url,'utf8')
try:server.serve_forever()
except KeyboardInterrupt:server.server_close()
