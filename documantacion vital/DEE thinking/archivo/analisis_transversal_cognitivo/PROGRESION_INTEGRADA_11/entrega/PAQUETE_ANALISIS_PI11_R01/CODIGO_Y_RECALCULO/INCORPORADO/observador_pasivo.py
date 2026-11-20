"""Passive DEETSNP1/v2 parser, exact AST segments from preserved PROMOVER_PI01.py.
Gzip CRC is checked; internal FNV is not recalculated here. No DEE imports.
"""
from pathlib import Path
import gzip, hashlib, struct
SYSTEM_KEY="DEE.Cognitive.System.1.1.life.v1"
SERVICE_KEY="DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1"

class Reader:
 def __init__(self,b):self.b=b;self.i=0
 def take(self,n):
  if n<0 or self.i+n>len(self.b):raise ValueError('Snapshot truncado')
  a=self.b[self.i:self.i+n];self.i+=n;return a
 def u8(self):return self.take(1)[0]
 def u32(self):return struct.unpack('<I',self.take(4))[0]
 def u64(self):return struct.unpack('<Q',self.take(8))[0]
 def text(self):
  n=self.u32()
  if n>16*1024**2:raise ValueError('Texto de snapshot fuera de límite')
  return self.take(n).decode('utf8')
 def count(self):
  n=self.u32()
  if n>1000000:raise ValueError('Colección fuera de límite')
  return n

def snapshot_view(path):
 encoded=Path(path).read_bytes();b=gzip.decompress(encoded)if encoded[:2]==b'\x1f\x8b'else encoded
 r=Reader(b[:-8])
 if r.take(8)!=b'DEETSNP1'or r.u32()!=2:raise ValueError('Snapshot no es v2 conocido')
 n=r.u32();tick=r.u64();r.u8();r.u64();r.u64();phase=r.text();total=r.u64()
 if total!=n**3 or total>128**3*4:raise ValueError('Dimensiones inválidas')
 raw=r.take(8*total);clocks=r.take(8*total);channels=r.count()
 for _ in range(channels):r.text();r.take(12+4+12+3)
 pending=r.count()
 for _ in range(pending):
  r.take(8+8+1+8+8)
  for _ in range(r.count()):r.text()
  for _ in range(r.count()):r.take(12+8)
 receipts=r.count()
 for _ in range(receipts):
  r.take(8+1+1+8)
  if r.u8():r.take(8)
  for _ in range(r.count()):r.text()
  r.text()
 r.u8();r.u64();prefix=r.i;metadata={}
 for _ in range(r.count()):
  k=r.text();v=r.text()
  if k in metadata:raise ValueError('Clave duplicada')
  metadata[k]=v
 if r.i!=len(b)-8:raise ValueError('Bytes no interpretados en snapshot')
 return {'physical':{'N':n,'tick':tick,'RAW_sha256':hashlib.sha256(raw).hexdigest(),'clocks_sha256':hashlib.sha256(clocks).hexdigest()},
         'encoded_sha256':hashlib.sha256(encoded).hexdigest(),'causal_prefix_sha256':hashlib.sha256(b[:prefix]).hexdigest(),
         'interfaces':channels,'pending_native':pending,'native_receipts':receipts,'phase':phase,'metadata':metadata,
         'scope':'Lectura binaria pasiva. GzipCRC y hashes comprobados; no se recalcula aquí FNV interno ni se restaura mundo.'}

def compare_native(a,b,allow_service=False):
 if a['physical']!=b['physical']or a['causal_prefix_sha256']!=b['causal_prefix_sha256']:raise ValueError('Cambió estado físico/agenda/interfaces/recibos durante migración0ticks')
 excluded={SYSTEM_KEY}
 if allow_service:excluded|={k for k in set(a['metadata'])|set(b['metadata'])if k==SERVICE_KEY or k.startswith(SERVICE_KEY+'.queue.')}
 changed=[k for k in set(a['metadata'])|set(b['metadata'])if k not in excluded and a['metadata'].get(k)!=b['metadata'].get(k)]
 if changed:raise ValueError('Cambió metadata no administrativa: '+repr(changed))
 return {'physical_equal':True,'causal_prefix_equal':True,'metadata_equal_except':sorted(excluded),'new_ticks':0}
