"""Limit an isolated MP4 presentation using edit-list durations only.

No bytes of encoded audio/video or media duration tables are changed. This is
an explicit packaging operation on a copy, not a change to the master movie.
"""
from pathlib import Path
import struct,json,subprocess,hashlib
import numpy as np
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
T=next(p for p in H.parents if p.name=='tests')
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
FP=T/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
source=H/'PRUEBA_GOP600_COPY.mp4';target=H/'ANTES_BITSTREAM_EDITLIST20.mp4'
assert source.exists() and not target.exists()
data=bytearray(source.read_bytes());patches=[]
def boxes(start,end):
 pos=start
 while pos<end:
  n,typ=struct.unpack_from('>I4s',data,pos);head=8
  if n==1:n=struct.unpack_from('>Q',data,pos+8)[0];head=16
  if n==0:n=end-pos
  assert n>=head and pos+n<=end,(pos,typ,n)
  yield pos,n,head,typ.decode('ascii');pos+=n
 assert pos==end
top=list(boxes(0,len(data)));moov=next(x for x in top if x[3]=='moov')
children=list(boxes(moov[0]+moov[2],moov[0]+moov[1]));mvhd=next(x for x in children if x[3]=='mvhd')
v=data[mvhd[0]+mvhd[2]];assert v==0
ts=struct.unpack_from('>I',data,mvhd[0]+20)[0];duration=20*ts
def put(offset,width,value,label):
 fmt='>I' if width==4 else '>Q';old=struct.unpack_from(fmt,data,offset)[0]
 struct.pack_into(fmt,data,offset,value);patches.append({'field':label,'offset':offset,'old':old,'new':value,'width':width})
put(mvhd[0]+24,4,duration,'mvhd.duration')
for track in [x for x in children if x[3]=='trak']:
 trackchild=list(boxes(track[0]+track[2],track[0]+track[1]));tkhd=next(x for x in trackchild if x[3]=='tkhd')
 assert data[tkhd[0]+8]==0
 trackid=struct.unpack_from('>I',data,tkhd[0]+20)[0]
 put(tkhd[0]+28,4,duration,f'trak{trackid}.tkhd.duration')
 edts=next(x for x in trackchild if x[3]=='edts');elst=next(x for x in boxes(edts[0]+edts[2],edts[0]+edts[1]) if x[3]=='elst')
 version=data[elst[0]+8];count=struct.unpack_from('>I',data,elst[0]+12)[0];assert count==1
 put(elst[0]+16,8 if version else 4,duration,f'trak{trackid}.elst.segment_duration')
target.write_bytes(data)
def run(cmd):
 r=subprocess.run([str(x) for x in cmd],capture_output=True);assert r.returncode==0,r.stderr.decode('utf8','replace');return r
def probe(p):return json.loads(run([FP,'-v','error','-count_frames','-show_streams','-show_format','-of','json',p]).stdout)
info=probe(target)
def sample(p,af):return run([FF,'-v','error','-i',p,'-map','0:a:0','-af',af,'-f','f32le','-acodec','pcm_f32le','-']).stdout
master=ROOT/'DEE_Cognitive_5min_MASTER_1080p_ES_ENsub.mp4'
a=sample(master,'atrim=start_sample=6240000:end_sample=7200000,asetpts=PTS-STARTPTS')
b=sample(target,'atrim=start_sample=0:end_sample=960000,asetpts=PTS-STARTPTS')
aa=np.frombuffer(a,dtype='<f4');bb=np.frombuffer(b,dtype='<f4')
assert len(aa)==len(bb)==1920000,(len(aa),len(bb))
diff=np.abs(aa-bb)
def packets(p,typ):
 return json.loads(run([FP,'-v','error','-select_streams',typ,'-show_packets','-show_data_hash','sha256','-show_entries','packet=pts_time,dts_time,duration_time,data_hash,side_data_list','-of','json',p]).stdout)['packets']
old=packets(source,'a:0');new=packets(target,'a:0')
payloadold=[x['data_hash'] for x in old];payloadnew=[x['data_hash'] for x in new]
vo=packets(source,'v:0');vn=packets(target,'v:0');assert [x['data_hash'] for x in vo]==[x['data_hash'] for x in vn]
assert payloadold==payloadnew
assert info['format']['duration']=='20.000000',info['format']['duration']
assert next(x for x in info['streams'] if x['codec_type']=='video')['nb_read_frames']=='600'
dec=run([FF,'-v','error','-xerror','-i',target,'-f','null','-'])
result={'operation':'Only mvhd/tkhd/elst presentation-duration integers patched in a new isolated copy; encoded packets/mdat and media timing tables unchanged.',
 'source':str(source),'target':str(target),'target_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'target_bytes':target.stat().st_size,
 'patches':patches,'probe':info,'AAC_packet_payloads_unchanged':payloadold==payloadnew,'video_packet_payloads_unchanged':True,
 'audio_PCM_20s_sha_master':hashlib.sha256(a).hexdigest(),'audio_PCM_20s_sha_excerpt':hashlib.sha256(b).hexdigest(),
 'audio_sample_frames':len(aa)//2,'PCM_identical_to_master_130_150':a==b,'PCM_max_abs_delta':float(diff.max()),'PCM_changed_float_values':int(np.count_nonzero(diff)),
 'AAC_first_packet_after':new[0],'AAC_last_packet_after':new[-1],'AV_decode_return_code':dec.returncode,'AV_decode_stderr':dec.stderr.decode()}
(H/'RECIBO_EDITLIST20.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({k:result[k] for k in ['target','target_sha256','target_bytes','AAC_packet_payloads_unchanged','video_packet_payloads_unchanged','PCM_identical_to_master_130_150','PCM_max_abs_delta','PCM_changed_float_values']},ensure_ascii=False,indent=2),flush=True)
