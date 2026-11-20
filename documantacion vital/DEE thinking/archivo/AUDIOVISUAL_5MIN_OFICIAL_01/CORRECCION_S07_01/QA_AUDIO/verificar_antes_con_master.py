"""Prove the delivered baseline's600 encoded picture packets are the master's S07."""
from pathlib import Path
import json,subprocess,hashlib
H=Path(__file__).resolve().parent;R=H.parents[1];T=next(p for p in H.parents if p.name=='tests')
FP=T/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
master=R/'DEE_Cognitive_5min_MASTER_1080p_ES_ENsub.mp4';before=H.parent/'DEE_S07_ANTES.mp4'
def packets(p):
 r=subprocess.run([str(FP),'-v','error','-select_streams','v:0','-show_packets','-show_data_hash','sha256',
 '-show_entries','packet=pts_time,dts_time,duration_time,data_hash,flags','-of','json',str(p)],capture_output=True,check=True)
 return json.loads(r.stdout)['packets']
a=[x for x in packets(master) if 130<=float(x['pts_time'])<150];b=packets(before)
assert len(a)==len(b)==600
checks=[{'same_payload':x['data_hash']==y['data_hash'],'PTS_offset130':abs(float(x['pts_time'])-float(y['pts_time'])-130)<1e-6,
 'DTS_offset130':abs(float(x['dts_time'])-float(y['dts_time'])-130)<1e-6,'same_duration':x['duration_time']==y['duration_time']} for x,y in zip(a,b)]
counts={k:sum(not x[k] for x in checks) for k in checks[0]}
assert counts['PTS_offset130']==counts['DTS_offset130']==counts['same_duration']==0
assert counts['same_payload']==10 and all('K' in a[i]['flags'] for i,x in enumerate(checks) if not x['same_payload'])
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
def decoded_video_hash(p,seek=None):
 cmd=[str(FF),'-v','error']
 if seek is not None:cmd+=['-ss',str(seek)]
 cmd+=['-i',str(p),'-map','0:v:0','-an','-frames:v','600','-c:v','rawvideo','-pix_fmt','yuv420p','-f','hash','-hash','sha256','-']
 r=subprocess.run(cmd,capture_output=True,check=True);return r.stdout.decode().strip()
ha=decoded_video_hash(master,130);hb=decoded_video_hash(before);assert ha==hb,(ha,hb)
rec={'master':str(master),'master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'baseline':str(before),
 'baseline_sha256':hashlib.sha256(before.read_bytes()).hexdigest(),'encoded_video_packets':600,
 'packet_mismatch_counts':counts,'decoded_600frame_yuv420p_hash_master':ha,'decoded_600frame_yuv420p_hash_before':hb,
 'all_decoded_video_picture_bytes_identical_to_master_S07':True,'all_video_PTS_DTS_offset_exactly130':True,'first_master_packet':a[0],'first_baseline_packet':b[0],
 'last_master_packet':a[-1],'last_baseline_packet':b[-1],'scope':'No video re-encoding. All600 decoded pictures are byte-identical. The concat master has different in-band headers in10keyframe packets, not changed picture pixels; other590packets identical.'}
(H/'ANTES_VIDEO_MASTER_IGUALDAD.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(rec,ensure_ascii=False,indent=2),flush=True)
