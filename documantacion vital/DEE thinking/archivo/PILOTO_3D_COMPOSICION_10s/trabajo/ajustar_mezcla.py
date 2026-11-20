from pathlib import Path
import subprocess,json,re,hashlib
HERE=Path(__file__).resolve().parent
A=HERE/'audio';ROOT=HERE.parent
T=next(p for p in HERE.parents if p.name=='tests')
F=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
inputs=[str(A/n) for n in ['locucion_10s_48k.wav','ambiente_bajo_voz_21LU.wav','efectos_editoriales_3_0_y_8_3.wav']]
base=[str(F),'-hide_banner','-y']
for p in inputs:base+=['-i',p]
mix='[0:a]adelay=920:all=1,atrim=0:10[v];[v][1:a][2:a]amix=inputs=3:duration=first:normalize=0'
measure=base+['-filter_complex',mix+',loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json[a]','-map','[a]','-f','null','-']
p=subprocess.run(measure,capture_output=True)
if p.returncode:raise RuntimeError(p.stderr.decode('utf8','replace'))
text=p.stderr.decode('utf8','replace');m=json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}',text)[-1])
(A/'R02_medicion_primera.log').write_text(text,'utf8')
norm=f"loudnorm=I=-16:TP=-1.5:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true:print_format=json"
out=A/'mezcla_tiempo_visual_10s.wav'
p=subprocess.run(base+['-filter_complex',mix+','+norm+'[a]','-map','[a]','-ar','48000','-ac','2','-c:a','pcm_s24le','-t','10',str(out)],capture_output=True)
(A/'R02_normalizacion.log').write_bytes(p.stderr)
if p.returncode:raise RuntimeError(p.stderr.decode('utf8','replace'))
srt='1\n00:00:01,070 --> 00:00:05,100\nIn composition, two contributions\nformed a common product.\n\n2\n00:00:05,150 --> 00:00:09,800\nThat product was used in another\ninteraction within the same world.\n'
(ROOT/'DEE_PILOTO_3D_COMPOSICION_10s_EN.srt').write_text(srt,'utf8')
d={'change':'Whole uninterrupted narration shifted +0.920s; no internal splice, no time-stretch, no new TTS',
 'voice_phonemes_s':[[1.07,5.10],[5.15,8.55]],'continuous_music':True,'duration_s':10,
 'normalization':m,'output':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
(A/'AJUSTE_VISUAL_AUDIO_R02.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
print(json.dumps(d,ensure_ascii=False))
