"""Private loopback playback QA. Exposes exactly one video, no directory list."""
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import json,threading,hashlib,time
HERE=Path(__file__).resolve().parent
VIDEO=HERE.parent/'DEE_PILOTO_3D_COMPOSICION_10s_1080p.mp4'
HTML='''<!doctype html><meta charset="utf-8"><title>Revisión del piloto DEE · 10 s</title>
<style>body{background:#07131d;color:#e8f4f3;font:18px Segoe UI,Arial;margin:24px}video{width:min(100%,1200px);height:auto;display:block}button{font:20px Segoe UI;padding:12px;margin:12px 0}p{max-width:1200px}</style>
<video id="v" src="/video.mp4" preload="auto" playsinline controls></video>
<button id="play">Reproducir los diez segundos</button><p id="estado">Preparado para revisión.</p>
<script>let v=document.getElementById('v'),s=document.getElementById('estado');
document.getElementById('play').onclick=()=>{if(v.ended)v.currentTime=0;v.play();s.textContent='Reproduciendo desde el inicio, sin acelerar.'};
v.onended=()=>{let q=v.getVideoPlaybackQuality();let r={ended:v.ended,duration:v.duration,currentTime:v.currentTime,videoWidth:v.videoWidth,videoHeight:v.videoHeight,totalVideoFrames:q.totalVideoFrames,droppedVideoFrames:q.droppedVideoFrames,muted:v.muted,volume:v.volume,playbackRate:v.playbackRate,error:v.error?.message||null};s.textContent='Reproducción completa: '+JSON.stringify(r);fetch('/receipt',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(r)})};
v.onerror=()=>{s.textContent='Error de reproducción: '+v.error?.message};</script>'''.encode()
class H(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_GET(self):
  if self.path=='/':
   self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(HTML)));self.end_headers();self.wfile.write(HTML)
  elif self.path=='/video.mp4':
   size=VIDEO.stat().st_size;start=0;end=size-1;r=self.headers.get('Range')
   if r:
    a,b=r.removeprefix('bytes=').split('-',1);start=int(a or 0);end=min(int(b) if b else end,end)
   self.send_response(206 if r else 200);self.send_header('Content-Type','video/mp4');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1))
   if r:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
   self.end_headers()
   with VIDEO.open('rb') as f:
    f.seek(start);remain=end-start+1
    while remain:
     block=f.read(min(65536,remain))
     if not block:break
     self.wfile.write(block);remain-=len(block)
  else:self.send_error(404)
 def do_POST(self):
  if self.path!='/receipt':self.send_error(404);return
  n=int(self.headers.get('Content-Length','0'))
  if not 0<n<8192:self.send_error(400);return
  d=json.loads(self.rfile.read(n));d['video_sha256']=hashlib.sha256(VIDEO.read_bytes()).hexdigest();d['host_time']=time.time()
  (HERE/'REPRODUCCION_COMPLETA_BROWSER.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
  self.send_response(204);self.end_headers()
server=ThreadingHTTPServer(('127.0.0.1',0),H)
(HERE/'REPRODUCTOR_LOCAL.json').write_text(json.dumps({'url':f'http://127.0.0.1:{server.server_port}/','scope':'loopback one video only; no publication'}),'utf8')
print(f'http://127.0.0.1:{server.server_port}/',flush=True)
threading.Timer(300,server.shutdown).start();server.serve_forever();server.server_close()
