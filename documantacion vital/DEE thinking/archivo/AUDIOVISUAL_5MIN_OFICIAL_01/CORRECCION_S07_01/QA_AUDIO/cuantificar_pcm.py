from pathlib import Path
import subprocess,numpy as np,json,hashlib,math
H=Path(__file__).resolve().parent;R=H.parents[1];T=next(p for p in H.parents if p.name=='tests')
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
def pcm(p,af):
 r=subprocess.run([str(FF),'-v','error','-i',str(p),'-map','0:a:0','-af',af,'-f','f32le','-acodec','pcm_f32le','-'],capture_output=True,check=True);return np.frombuffer(r.stdout,dtype='<f4').reshape(-1,2)
a=pcm(R/'DEE_Cognitive_5min_MASTER_1080p_ES_ENsub.mp4','atrim=start_sample=6240000:end_sample=7200000,asetpts=PTS-STARTPTS')
b=pcm(H/'ANTES_BITSTREAM_EDITLIST20.mp4','atrim=start_sample=0:end_sample=960000,asetpts=PTS-STARTPTS')
d=a.astype('float64')-b.astype('float64');rms=lambda x:float(np.sqrt(np.mean(x*x)));db=lambda x:20*math.log10(max(x,1e-20))
persec=[{'second':i,'changed':int(np.count_nonzero(d[i*48000:(i+1)*48000])),
 'max_abs_delta':float(np.abs(d[i*48000:(i+1)*48000]).max()),'difference_RMS_dBFS':db(rms(d[i*48000:(i+1)*48000]))} for i in range(20)]
rec={'scope':'Decoder floating-PCM difference, not an edit to audio. Identical AAC payload can decode differently from a different decoder starting state; the specific cause is not established by this calculation.',
 'samples_per_channel':len(a),'max_abs_delta':float(np.abs(d).max()),'difference_RMS_dBFS':db(rms(d)),'source_RMS_dBFS':db(rms(a.astype('float64'))),
 'SNR_dB':db(rms(a.astype('float64'))/rms(d)),'per_second':persec}
(H/'DIFERENCIA_PCM.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),'utf8');print(json.dumps(rec,ensure_ascii=False,indent=2))
