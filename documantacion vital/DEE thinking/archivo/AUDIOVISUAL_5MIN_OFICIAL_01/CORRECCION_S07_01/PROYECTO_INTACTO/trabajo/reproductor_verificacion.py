"""Loopback-only exact-file player. No external assets, uploads or operational DEE data."""
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import json,hashlib,datetime
H=Path(__file__).resolve().parent;R=H.parent
P=R/'DEE_Cognitive_5min_MASTER_1080p_ES_ENsub.mp4';SHA=hashlib.sha256(P.read_bytes()).hexdigest()
PAGE='''<!doctype html><html lang="es"><meta charset="utf-8"><title>DEE — comprobación del máster local</title>
<style>body{background:#07131d;color:white;font:18px system-ui;margin:18px}video{display:block;width:min(100%,1280px);background:#07131d}button{font:20px system-ui;padding:8px;margin:10px}pre{white-space:pre-wrap;font-size:14px}</style>
<h1>Máster local completo · 1080p · 5 minutos</h1><button id="play">Reproducir completo</button>
<video id="v" preload="metadata" playsinline controls src="/master.mp4"></video><pre id="stats">Cargando metadatos…</pre>
<script>
const v=document.querySelector('#v'),s=document.querySelector('#stats');let ev=[],rvfc=0,start=null;
function data(){let q=v.getVideoPlaybackQuality();return {currentTime:v.currentTime,duration:v.duration,width:v.videoWidth,height:v.videoHeight,paused:v.paused,ended:v.ended,muted:v.muted,volume:v.volume,playbackRate:v.playbackRate,readyState:v.readyState,totalVideoFrames:q.totalVideoFrames,droppedVideoFrames:q.droppedVideoFrames,corruptedVideoFrames:q.corruptedVideoFrames||0,frameCallbacks:rvfc,error:v.error?{code:v.error.code,message:v.error.message}:null,events:ev,wallSeconds:start?(performance.now()-start)/1000:null}}
function update(){s.textContent=JSON.stringify(data(),null,2)}
for(let n of ['loadedmetadata','playing','pause','waiting','stalled','error','ended','seeking','seeked'])v.addEventListener(n,()=>{ev.push({event:n,time:v.currentTime,wall:performance.now()});update();if(n==='ended')fetch('/receipt',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data())})});
function cb(){rvfc++;v.requestVideoFrameCallback(cb)}v.requestVideoFrameCallback(cb);
document.querySelector('#play').onclick=()=>{v.currentTime=0;v.muted=false;v.volume=.9;v.playbackRate=1;start=performance.now();v.play();};
setInterval(update,1000);</script></html>'''.encode('utf8')
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_GET(self):
  if self.path=='/':
   self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(PAGE)));self.end_headers();self.wfile.write(PAGE);return
  if self.path!='/master.mp4':self.send_error(404);return
  size=P.stat().st_size;start=0;end=size-1;partial='Range' in self.headers
  if partial:
   a,b=self.headers['Range'].removeprefix('bytes=').split('-');start=int(a or 0);end=min(int(b) if b else size-1,size-1)
  if not 0<=start<=end<size:self.send_error(416);return
  self.send_response(206 if partial else 200);self.send_header('Content-Type','video/mp4');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1))
  if partial:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  self.end_headers()
  try:
   with P.open('rb') as f:
    f.seek(start);remaining=end-start+1
    while remaining:
     b=f.read(min(262144,remaining));self.wfile.write(b);remaining-=len(b)
  except (BrokenPipeError,ConnectionResetError):pass
 def do_POST(self):
  if self.path!='/receipt':self.send_error(404);return
  rec=json.loads(self.rfile.read(min(200000,int(self.headers['Content-Length']))))
  out={'source':str(P),'sha256':SHA,'bytes':P.stat().st_size,'received_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'browser_report':rec,'scope':'Local browser playback, not a human hearing test and not a verification of the user-downloaded copy.'}
  (H/'QA_ROOT/REPRODUCCION_NAVEGADOR.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8')
  self.send_response(200);self.send_header('Content-Length','2');self.end_headers();self.wfile.write(b'OK')
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
url=f'http://127.0.0.1:{server.server_port}/';(H/'QA_ROOT/REPRODUCTOR_URL.txt').write_text(url,'utf8');print(url,flush=True)
try:server.serve_forever()
except KeyboardInterrupt:server.server_close()
