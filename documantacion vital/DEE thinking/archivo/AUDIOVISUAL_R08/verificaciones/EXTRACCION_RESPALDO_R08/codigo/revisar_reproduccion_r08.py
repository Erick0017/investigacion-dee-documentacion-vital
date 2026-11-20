"""Loopback-only review player for one completed R08 MP4.

No directory listing, no Cognitive access, no external listener. The only
served media is the selected final film. This is audiovisual instrumentation.
"""
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import hashlib,json,re,threading,time

ROOT=Path(__file__).resolve().parents[1]
VIDEO=ROOT/'DEE_Cognitive_2_0_R08_Experiencia_y_Procesamiento_1080p_ES.mp4'
OUT=ROOT/'verificaciones/REPRODUCCION_LOCAL_R08.json'
HTML='''<!doctype html><html lang="es"><meta charset="utf-8"><title>Revisión local R08</title>
<style>body{margin:0;background:#0B1220;color:#F5F7FA;font:20px sans-serif}main{max-width:1280px;margin:auto}video{width:100%;display:block}button{font:22px sans-serif;padding:12px;margin:12px}p{margin:12px}</style>
<main><video id="v" controls preload="auto" playsinline src="/video"></video>
<button id="play">Reproducir desde el inicio</button><p id="status">Verificación local a velocidad normal. La escucha humana no está certificada.</p></main>
<script>const v=document.getElementById('v');document.getElementById('play').onclick=()=>{v.currentTime=0;v.playbackRate=1;v.play();};
v.addEventListener('ended',()=>{const q=v.getVideoPlaybackQuality?v.getVideoPlaybackQuality():null;const r={ended:v.ended,currentTime:v.currentTime,duration:v.duration,playbackRate:v.playbackRate,muted:v.muted,volume:v.volume,videoWidth:v.videoWidth,videoHeight:v.videoHeight,error:v.error?{code:v.error.code,message:v.error.message}:null,quality:q?{totalVideoFrames:q.totalVideoFrames,droppedVideoFrames:q.droppedVideoFrames,corruptedVideoFrames:q.corruptedVideoFrames}:null};document.getElementById('status').textContent='Reproducción completa '+JSON.stringify(r);fetch('/resultado',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(r)});});</script></html>'''

class Review(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        if self.path=='/':
            b=HTML.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b);return
        if self.path!='/video':self.send_error(404);return
        size=VIDEO.stat().st_size;start,end=0,size-1;status=200
        value=self.headers.get('Range')
        if value:
            m=re.fullmatch(r'bytes=(\d+)-(\d*)',value)
            if not m:self.send_error(416);return
            start=int(m[1]);end=min(size-1,int(m[2])) if m[2] else size-1;status=206
            if start>end:self.send_error(416);return
        self.send_response(status);self.send_header('Content-Type','video/mp4');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1));self.send_header('Cache-Control','no-store')
        if status==206:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.end_headers()
        try:
            with VIDEO.open('rb') as f:
                f.seek(start);left=end-start+1
                while left:
                    b=f.read(min(left,1024*1024))
                    if not b:break
                    self.wfile.write(b);left-=len(b)
        except (BrokenPipeError,ConnectionResetError):pass
    def do_POST(self):
        if self.path!='/resultado':self.send_error(404);return
        n=int(self.headers.get('Content-Length','0'))
        if not 0<n<=8192:self.send_error(400);return
        result=json.loads(self.rfile.read(n))
        result.update({'scope':'Real browser playback end event. Not human listening, independent audience evaluation, or a Native run.',
            'video':str(VIDEO),'video_sha256':hashlib.sha256(VIDEO.read_bytes()).hexdigest(),'new_Native_ticks':0,'loopback_only':True})
        with OUT.open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
        self.send_response(200);self.end_headers();self.wfile.write(b'OK')
        threading.Thread(target=self.server.shutdown,daemon=True).start()

def main():
    if not VIDEO.is_file():raise FileNotFoundError('Final MP4 not ready')
    if OUT.exists():raise FileExistsError('Preserve prior playback receipt')
    server=ThreadingHTTPServer(('127.0.0.1',0),Review)
    timer=threading.Timer(900,server.shutdown);timer.daemon=True;timer.start()
    print(json.dumps({'url':f'http://127.0.0.1:{server.server_port}/','served_only':str(VIDEO),'timeout_seconds':900}),flush=True)
    try:server.serve_forever(poll_interval=.25)
    finally:timer.cancel();server.server_close()
    print('Playback receipt saved' if OUT.exists() else 'Review expired without a completion receipt',flush=True)
if __name__=='__main__':main()
