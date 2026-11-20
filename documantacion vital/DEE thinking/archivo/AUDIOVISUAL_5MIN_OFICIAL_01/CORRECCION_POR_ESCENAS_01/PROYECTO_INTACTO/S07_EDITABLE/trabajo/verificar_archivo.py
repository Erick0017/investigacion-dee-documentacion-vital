"""Read and decode an exported film. This tool never imports the DEE runtime."""
from pathlib import Path
import argparse,subprocess,json,hashlib,time
H=Path(__file__).resolve().parent
T=next(x for x in H.parents if x.name=='tests')
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
FP=T/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
def run(cmd):
 r=subprocess.run([str(x) for x in cmd],capture_output=True)
 return r.returncode,r.stdout,r.stderr
def verify(p,out):
 p=p.resolve();out.mkdir(parents=True,exist_ok=True)
 t=time.monotonic()
 c,b,e=run([FP,'-v','error','-show_format','-show_streams','-of','json',p]);assert c==0,e
 probe=json.loads(b);v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
 c,b,e=run([FP,'-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time,pkt_duration_time,width,height,sample_aspect_ratio','-of','json',p]);assert c==0,e
 frames=json.loads(b)['frames'];ts=[float(x['best_effort_timestamp_time']) for x in frames]
 gap=max(abs(y-x-1/30) for x,y in zip(ts,ts[1:]))
 dc,do,de=run([FF,'-v','error','-xerror','-i',p,'-map','0:v:0','-map','0:a:0','-f','null','-'])
 (out/(p.stem+'_DECODE.log')).write_bytes(de)
 checks={'MP4':probe['format']['format_name'].find('mp4')>=0,'H264':v['codec_name']=='h264','yuv420p':v['pix_fmt']=='yuv420p',
 'duration_exact_300':abs(float(probe['format']['duration'])-300)<1e-6,'9000_decoded_frames':len(frames)==9000,
 '30_CFR':v['r_frame_rate']=='30/1' and v['avg_frame_rate']=='30/1' and gap<2e-6,
 'square_pixels':v['sample_aspect_ratio']=='1:1','first_PTS_zero':abs(ts[0])<1e-6,'last_PTS_8999_over_30':abs(ts[-1]-8999/30)<2e-6,
 'AAC':a['codec_name']=='aac','48k_stereo':a['sample_rate']=='48000' and a['channels']==2,
 'full_AV_decode':dc==0 and not de.strip()}
 sha=hashlib.sha256(p.read_bytes()).hexdigest()
 result={'file':str(p),'bytes':p.stat().st_size,'sha256':sha,'checks':checks,'all_required_checks':all(checks.values()),
 'resolution':[v['width'],v['height']],'decoded_video_frames':len(frames),'max_frame_interval_error_s':gap,'ffprobe':probe,
 'decoder_return_code':dc,'decoder_stderr':de.decode('utf8','replace'),'host_seconds':time.monotonic()-t,
 'scope':'Exact local file; automated temporal/codec and full decode verification. No claim of human listening or remote delivery.'}
 target=out/(p.stem+'_VERIFICACION.json');target.write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
 print(json.dumps({k:result[k] for k in ['file','bytes','sha256','resolution','decoded_video_frames','all_required_checks','host_seconds']},ensure_ascii=False),flush=True)
 assert result['all_required_checks'],checks
 return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('file',type=Path);ap.add_argument('--out',type=Path,default=H/'verificacion');args=ap.parse_args();verify(args.file,args.out)
