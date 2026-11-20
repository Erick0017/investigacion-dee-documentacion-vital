"""Limit presentation to20s on a NEW MP4 copy; keep media payloads untouched."""
from pathlib import Path
import struct,hashlib,json,argparse
def limit_presentation(source,target,seconds=20):
 source=Path(source).resolve();target=Path(target).resolve()
 assert source!=target and source.is_file() and not target.exists()
 data=bytearray(source.read_bytes());patches=[]
 def boxes(start,end):
  pos=start
  while pos<end:
   n,typ=struct.unpack_from('>I4s',data,pos);head=8
   if n==1:n=struct.unpack_from('>Q',data,pos+8)[0];head=16
   if n==0:n=end-pos
   assert head<=n<=end-pos
   yield pos,n,head,typ.decode('ascii');pos+=n
  assert pos==end
 top=list(boxes(0,len(data)));moov=next(x for x in top if x[3]=='moov')
 children=list(boxes(moov[0]+moov[2],moov[0]+moov[1]));mvhd=next(x for x in children if x[3]=='mvhd')
 assert data[mvhd[0]+8]==0,'This exact source uses version0 headers.'
 ts=struct.unpack_from('>I',data,mvhd[0]+20)[0];duration=round(seconds*ts)
 def put(offset,width,label):
  fmt='>I' if width==4 else '>Q';old=struct.unpack_from(fmt,data,offset)[0]
  assert abs(old/ts-seconds)<.1,(label,old/ts,'Unexpectedly different presentation')
  struct.pack_into(fmt,data,offset,duration);patches.append({'field':label,'offset':offset,'old':old,'new':duration,'width':width})
 put(mvhd[0]+24,4,'mvhd.duration')
 for track in [x for x in children if x[3]=='trak']:
  c=list(boxes(track[0]+track[2],track[0]+track[1]));tkhd=next(x for x in c if x[3]=='tkhd');assert data[tkhd[0]+8]==0
  trackid=struct.unpack_from('>I',data,tkhd[0]+20)[0];put(tkhd[0]+28,4,f'trak{trackid}.tkhd.duration')
  edts=next(x for x in c if x[3]=='edts');elst=next(x for x in boxes(edts[0]+edts[2],edts[0]+edts[1]) if x[3]=='elst')
  version=data[elst[0]+8];count=struct.unpack_from('>I',data,elst[0]+12)[0];assert count==1
  put(elst[0]+16,8 if version else 4,f'trak{trackid}.elst.segment_duration')
 target.write_bytes(data)
 return {'source':str(source),'target':str(target),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'target_sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'duration_seconds':seconds,
 'operation':'Only existing mvhd/tkhd/elst duration integer fields in a new MP4 copy. No packet/media/timing-table payload changes. Final ffprobe/decode still required.',
 'patches':patches}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('target');a=p.parse_args()
 receipt=limit_presentation(a.source,a.target);Path(a.target).with_suffix('.DURACION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),'utf8');print(json.dumps(receipt,ensure_ascii=False,indent=2))
