from pathlib import Path
import subprocess,json,hashlib,re
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
T=next(p for p in HERE.parents if p.name=='tests')
F=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
P=T/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
OUT=ROOT/'DEE_PILOTO_3D_COMPOSICION_10s_1080p.mp4'
ass='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: EN,Segoe UI,90,&H00FFFFFF,&H00FFFFFF,&H00201008,&H70000000,0,0,0,0,100,100,0,0,1,3.4,1.5,2,100,100,48,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.07,0:00:05.10,EN,,0,0,0,,In composition, two contributions\\Nformed a common product.
Dialogue: 0,0:00:05.15,0:00:08.65,EN,,0,0,0,,That product was used in another\\Ninteraction within the same world.
'''
(HERE/'subtitulos.ass').write_text(ass,'utf8')
def execute(name,args):
 r=subprocess.run(args,cwd=HERE,capture_output=True)
 (HERE/(name+'.stderr.txt')).write_bytes(r.stderr)
 if r.returncode:raise RuntimeError(name+' failed: '+r.stderr.decode('utf8','replace')[-4000:])
 return r
execute('encode_final',[str(F),'-hide_banner','-y','-i','piloto_mudo.mp4','-i','audio/mezcla_tiempo_visual_10s.wav',
 '-map','0:v:0','-map','1:a:0','-vf','ass=subtitulos.ass,setsar=1',
 '-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-r','30','-fps_mode','cfr',
 '-frames:v','300','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t','10',
 '-metadata:s:a:0','language=spa','-movflags','+faststart',str(OUT)])
r=execute('ffprobe',[str(P),'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(OUT)])
d=json.loads(r.stdout);(HERE/'FFPROBE_FINAL.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
v=next(x for x in d['streams'] if x['codec_type']=='video');a=next(x for x in d['streams'] if x['codec_type']=='audio')
assert (v['width'],v['height'],v['codec_name'],v['sample_aspect_ratio'])==(1920,1080,'h264','1:1')
assert v['r_frame_rate']==v['avg_frame_rate']=='30/1'
assert int(v['nb_read_frames'])==int(v['nb_frames'])==300
assert float(v['duration'])==float(d['format']['duration'])==10
assert a['codec_name']=='aac' and int(a['sample_rate'])==48000 and a['channels']==2
execute('decode_total',[str(F),'-hide_banner','-v','error','-xerror','-i',str(OUT),'-map','0:v:0','-map','0:a:0','-f','null','-'])
r=execute('packets',[str(P),'-v','error','-select_streams','v:0','-show_entries','packet=pts_time,duration_time','-of','json',str(OUT)])
packets=json.loads(r.stdout)['packets'];pts=sorted(float(x['pts_time']) for x in packets)
assert len(pts)==300 and all(abs(x-i/30)<1e-6 for i,x in enumerate(pts))
execute('audio_meter',[str(F),'-hide_banner','-i',str(OUT),'-vn','-af','loudnorm=I=-16:TP=-1:print_format=json','-f','null','-'])
frames=[0,60,90,120,150,180,210,240,297];thumbs=[]
for n in frames:
 p=HERE/'fotogramas'/f'final_{n:03}.png'
 execute('still_'+str(n),[str(F),'-hide_banner','-loglevel','error','-y','-i',str(OUT),'-vf',f'select=eq(n\\,{n})','-frames:v','1',str(p)])
 im=Image.open(p).convert('RGB');im.thumbnail((640,360));thumbs.append(im)
sheet=Image.new('RGB',(1920,1080))
for i,im in enumerate(thumbs):sheet.paste(im,((i%3)*640,(i//3)*360))
sheet.save(HERE/'CONTACTO_FINAL.png')
receipt={'file':str(OUT),'bytes':OUT.stat().st_size,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
 'container_duration_s':10,'native_resolution':[1920,1080],'video_frames':300,'CFR_fps':30,'SAR':'1:1',
 'codecs':['H.264','AAC stereo 48000Hz'],'burned_English_subtitles':True,
 'full_video_and_audio_decode_errors':0,'all_300_pts_match_n_over_30':True,
 'not_a_user_approval':True}
(HERE/'VERIFICACION_FINAL.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(receipt,ensure_ascii=False))
