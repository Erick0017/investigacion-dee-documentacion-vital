"""Read-only source analysis and technical isolated excerpt; no DEE or TTS execution."""
from pathlib import Path
import subprocess,json,re,hashlib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1];WORK=ROOT/'trabajo'
T=next(p for p in HERE.parents if p.name=='tests')
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
FP=T/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
MASTER=ROOT/'DEE_Cognitive_5min_MASTER_1080p_ES_ENsub.mp4'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(cmd):
 r=subprocess.run([str(v) for v in cmd],capture_output=True);assert r.returncode==0,r.stderr.decode('utf8','replace');return r
def probe(p,opts):return json.loads(run([FP,'-v','error',*opts,'-of','json',p]).stdout)
def find_lists(obj):
 if isinstance(obj,dict):
  for k,v in obj.items():
   if isinstance(v,list):yield k,v
   elif isinstance(v,dict):yield from find_lists(v)
index=json.loads((WORK/'audio/CONTINUIDAD_AUDIO_300s_R01.json').read_text('utf8'))
blocks=json.loads((WORK/'audio/guion.json').read_text('utf8'))['blocks']
voice=blocks[6]
expected='En comunicación, información adquirida por un participante llegó a otro y afectó una respuesta posterior del receptor. Los controles con mensajes interrumpidos o con contenido distinto identifican su efecto. Se demuestra transmitir y utilizar información entre participantes definidos, sin afirmar conversación humana.'
assert voice['literal_ES']==expected
phrases=[]
for key,rows in find_lists(index):
 for row in rows:
  if isinstance(row,dict) and row.get('block_id')=='B07':
   if 'start_s_in_master' in row:
    item=dict(row);item['local_start_s']=round(row['start_s_in_master']-130,6);item['local_end_s']=round(row['end_s_in_master']-130,6);item['container_key']=key;phrases.append(item)
subs=json.loads((WORK/'audio/INDICE_SUBTITULOS_EN_R01.json').read_text('utf8'))['rows'];subs=[r for r in subs if r['block_id']=='B07']
for r in subs:r['local_start_s']=round(r['SRT_start_global_s']-130,6);r['local_end_s']=round(r['SRT_end_global_s']-130,6)
srt=ROOT/'DEE_Cognitive_5min_EN.srt'
def seconds(txt):
 h,m,s=txt.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
def stamp(t):
 n=round(t*1000);h,n=divmod(n,3600000);m,n=divmod(n,60000);s,ms=divmod(n,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
out=[]
for block in re.split(r'\n\s*\n',srt.read_text('utf8').strip()):
 lines=block.splitlines();a,b=[seconds(x) for x in lines[1].split(' --> ')]
 if a>=130 and a<150:
  out.append(f'{len(out)+1}\n{stamp(a-130)} --> {stamp(b-130)}\n'+ '\n'.join(lines[2:]))
local_srt=HERE/'S07_EN_ORIGINAL_LOCAL.srt';local_srt.write_text('\n\n'.join(out)+'\n','utf8')
assert len(out)==6
pack130=probe(MASTER,['-select_streams','v:0','-read_intervals','129.9%130.1','-show_packets','-show_entries','packet=pts_time,dts_time,flags,duration_time'])['packets']
exact=[x for x in pack130 if abs(float(x.get('pts_time','-1000'))-130)<1e-6]
assert exact and 'K' in exact[0]['flags'],exact
test=HERE/'PRUEBA_GOP600_COPY.mp4'
cmd=[FF,'-v','error','-n','-i',WORK/'clips/S07.mp4','-ss','130','-i',MASTER,'-t','20','-map','0:v:0','-map','1:a:0','-c','copy','-avoid_negative_ts','disabled','-movflags','+faststart',test]
if not test.exists():run(cmd)
testmeta=probe(test,['-show_format','-show_streams'])
packetopts=['-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=pts_time,dts_time,duration_time,data_hash,side_data_list']
testaudio=probe(test,packetopts)['packets'];masteraudio=probe(MASTER,packetopts)['packets']
relevant=[p for p in masteraudio if 129.9<=float(p.get('pts_time','-1'))<150.1]
indexbyhash={p['data_hash']:p for p in relevant}
matches=[]
for p in testaudio:
 source=indexbyhash.get(p['data_hash']);matches.append({'source':source,'cut':p,'same_encoded_packet':source is not None,'delta_pts_s':round(float(source['pts_time'])-float(p['pts_time']),9) if source else None})
assert all(p['same_encoded_packet'] for p in matches)
assert all(abs(p['delta_pts_s']-130)<1e-6 for p in matches)
testvideo=probe(test,['-select_streams','v:0','-count_frames','-show_streams'])['streams'][0]
assert testvideo['nb_read_frames']=='600' and testvideo['width']==1920 and testvideo['height']==1080
result={'scope':'Only existing S07 audio, subtitles and technical trim; no DEE evolution or voice synthesis.',
 'master':{'path':str(MASTER),'sha256':SHA(MASTER)},'literal_ES':expected,'voice_block':voice,
 'phrases_and_clauses':phrases,'subtitles':subs,'original_SRT_sha256':SHA(srt),'local_SRT':{'path':str(local_srt),'sha256':SHA(local_srt)},
 'video_boundary_130':exact,'copy_trim':{'path':str(test),'bytes':test.stat().st_size,'sha256':SHA(test),'command':[str(v) for v in cmd],
 'probe':testmeta,'decoded_video_frames':testvideo['nb_read_frames'],'audio_packet_count':len(testaudio),'all_AAC_packets_identical_to_source':True,
 'all_AAC_pts_shift_exactly_130':True,'first_AAC_packets':matches[:2],'last_AAC_packets':matches[-2:]},
 'recommendation':'Use this exact stream-copy20s segment as ANTES and as the common AAC source of DESPUES (-map correctedVideo:v -map ANTES:a -c:a copy), retaining the same edit-list timeline. Compare AACpacketpayload and PTS before delivery. Do not re-encode or resynthesize the audio.'}
(HERE/'RECIBO_AUDIO_S07.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'receipt':str(HERE/'RECIBO_AUDIO_S07.json'),'phrases':phrases,'cues':[{k:r[k] for k in ['EN_cue','local_start_s','local_end_s']} for r in subs],
 'cut_dimensions':[testvideo['width'],testvideo['height']],'frames':testvideo['nb_read_frames'],'duration':testmeta['format']['duration'],'audio_packets':len(testaudio),
 'audio_first':testaudio[0],'audio_last':testaudio[-1]},ensure_ascii=False,indent=2),flush=True)
