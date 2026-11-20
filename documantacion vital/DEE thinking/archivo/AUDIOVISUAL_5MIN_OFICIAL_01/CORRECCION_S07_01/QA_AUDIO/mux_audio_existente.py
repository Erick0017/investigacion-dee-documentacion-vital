"""Mux only an existing600-frame native video with the preserved original AAC.

This helper is specific to the isolated S07 correction. It does not synthesize,
resample or encode audio. It refuses to silently accept AAC/PCM differences.
"""
from pathlib import Path
import subprocess,json,hashlib,argparse
from fijar_presentacion_mp4 import limit_presentation
H=Path(__file__).resolve().parent;DELIVERY=H.parent
T=next(p for p in H.parents if p.name=='tests')
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
FP=T/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
BEFORE=DELIVERY/'DEE_S07_ANTES.mp4'
def run(cmd):
 r=subprocess.run([str(x) for x in cmd],capture_output=True)
 assert r.returncode==0,r.stderr.decode('utf8','replace');return r
def packets(p):
 return json.loads(run([FP,'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries',
 'packet=pts_time,dts_time,duration_time,data_hash,side_data_list','-of','json',p]).stdout)['packets']
def pcm(p):
 return run([FF,'-v','error','-i',p,'-map','0:a:0','-af','atrim=start_sample=0:end_sample=960000',
 '-f','f32le','-acodec','pcm_f32le','-']).stdout
def mux_video_con_audio_existente(video600,out):
 video600=Path(video600).resolve();out=Path(out).resolve();assert BEFORE.is_file() and video600.is_file() and not out.exists()
 if out==BEFORE:raise ValueError('The baseline cannot be overwritten.')
 temporary=H/(out.stem+'_SIN_LIMITE_EDITLIST.mp4');assert not temporary.exists()
 command=[FF,'-hide_banner','-n','-i',video600,'-i',BEFORE,'-map','0:v:0','-map','1:a:0','-c','copy','-t','20',
 '-use_editlist','1','-avoid_negative_ts','disabled','-movflags','+faststart',temporary]
 r=run(command);temporary.with_suffix('.MUX.log').write_bytes(r.stderr)
 patch=limit_presentation(temporary,out,20)
 a=packets(BEFORE);b=packets(out)
 # Exact native packet content, PTS/DTS and skip-sample metadata are required.
 packet_equality=a==b
 pa=pcm(BEFORE);pb=pcm(out);assert len(pa)==len(pb)==960000*2*4
 probe=json.loads(run([FP,'-v','error','-count_frames','-show_streams','-show_format','-of','json',out]).stdout)
 v=next(s for s in probe['streams'] if s['codec_type']=='video')
 checks={'AAC_packets_payload_PTS_DTS_duration_and_side_data_equal':packet_equality,'PCM_20s_identical_ANTES_DESPUES':pa==pb,
 '600_decoded_video_frames':v['nb_read_frames']=='600','native1080':v['width']==1920 and v['height']==1080,
 'duration20_exact':probe['format']['duration']=='20.000000','CFR30':v['r_frame_rate']=='30/1' and v['avg_frame_rate']=='30/1','SAR1':v['sample_aspect_ratio']=='1:1'}
 dec=run([FF,'-v','error','-xerror','-i',out,'-f','null','-']);checks['full_AV_decode']=not dec.stderr.strip()
 receipt={'source_video':str(video600),'source_original_audio':str(BEFORE),'command':[str(x) for x in command],
 'patch':patch,'probe':probe,'checks':checks,'all_checks':all(checks.values()),'AAC_packets':len(a),
 'PCM_before_sha256':hashlib.sha256(pa).hexdigest(),'PCM_after_sha256':hashlib.sha256(pb).hexdigest(),
 'file':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
 'audio_offset_s':0,'note':'No audio encode/filter/resample. Before and after share identical encoded AAC and decode to identical20s PCM. The cut is packet-identical to the master but decoder start state can cause tiny differences from decoding the complete300s master.'}
 receipt_path=H/(out.stem+'_VERIFICACION_AUDIO_Y_FORMATO.json');receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),'utf8')
 print(json.dumps({k:receipt[k] for k in ['file','bytes','sha256','checks','all_checks']},ensure_ascii=False,indent=2),flush=True)
 assert receipt['all_checks'],checks
 return receipt
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('video600');p.add_argument('out');a=p.parse_args();mux_video_con_audio_existente(a.video600,a.out)
