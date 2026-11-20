"""Decode organizational binary sections by frozen4.5 serializer; no DEE import."""
from pathlib import Path
import hashlib,importlib.util,json,struct
P=Path(__file__).resolve().parents[1]
def sha(x):return hashlib.sha256(x).hexdigest()
class R:
 def __init__(self,b):self.b=b;self.i=0
 def take(self,n):
  if n<0 or self.i+n>len(self.b):raise ValueError('Truncated organizational metadata')
  a=self.b[self.i:self.i+n];self.i+=n;return a
 def u8(self):return self.take(1)[0]
 def u64(self):return struct.unpack('<Q',self.take(8))[0]
 def text(self):
  n=self.u64()
  if n>1048576:raise ValueError('Oversized organizational string')
  return self.take(n).decode('utf8')
 def n(self,cap=1048576):
  n=self.u64()
  if n>cap:raise ValueError('Organizational count cap')
  return n
 def coord(self):self.take(24)
 def many(self,n,callback):
  for _ in range(n):callback()
 def symbols(self):
  for _ in range(self.n(65536)):self.text();self.u64()

def parse(meta):
 prefix='dee_thinking.organizational.v1.';n=int(meta[prefix+'chunks']);b=bytes.fromhex(''.join(meta[prefix+str(i)]for i in range(n)));r=R(b);sections={};counts={};ops=[]
 if r.u64()!=1:raise ValueError('Organizational schema')
 start=0;recipe_id=r.text();version=r.text();dim=r.u64();r.coord();t0=r.u64();domain=r.text();backend=r.u8();threads=r.u64()
 for _ in range(r.n(4096)):r.text();r.u64()
 for _ in range(r.n(4096)):r.text();r.text()
 counts['placements']=r.n()
 for _ in range(counts['placements']):r.coord();r.take(16);r.text()
 counts['organizations']=r.n(4096)
 for _ in range(counts['organizations']):
  r.text();r.text();r.u64()
  for _ in range(3):
   if r.u8():r.coord()
  for _ in range(r.n(4096)):r.text();r.coord()
  for _ in range(r.n(65536)):r.coord()
 counts['interfaces']=r.n(65536)
 for _ in range(counts['interfaces']):
  r.text();r.text();r.coord();r.u64();r.coord();r.take(3);r.text();r.u8();r.take(16);r.symbols();r.text();r.text()
 counts['actions']=r.n(4096)
 for _ in range(counts['actions']):
  r.text();r.text()
  for _ in range(r.n(65536)):r.coord()
  for _ in range(r.n(65536)):r.text()
  r.take(r.n(65536)*8)
 sections['recipe']={'start':start,'end':r.i,'sha256':sha(b[start:r.i])};start=r.i
 counts['protocols']=r.n(4096)
 for _ in range(counts['protocols']):
  r.text();r.text();r.u8();r.u64()
  for _ in range(r.n(4096)):
   r.take(24);r.take(r.n(4096)*8);r.take(r.n(4096)*24);r.take(r.n(4096)*48)
 sections['protocols']={'start':start,'end':r.i,'sha256':sha(b[start:r.i])};start=r.i
 counts['diagnostic_edits']=r.n()
 for _ in range(counts['diagnostic_edits']):r.coord();r.text();r.take(40);r.u8()
 sections['diagnostic_edits']={'start':start,'end':r.i,'sha256':sha(b[start:r.i])};start=r.i
 counts['external_operations']=r.n()
 for _ in range(counts['external_operations']):ops.append(r.text())
 sections['external_operations']={'start':start,'end':r.i,'sha256':sha(b[start:r.i])};start=r.i
 counts['decoders']=r.n(4096)
 for _ in range(counts['decoders']):r.text();r.text();r.u8();r.symbols()
 sections['decoders']={'start':start,'end':r.i,'sha256':sha(b[start:r.i])};start=r.i
 trace_saved=bool(r.u8())
 if trace_saved:
  budget=r.n(65536);r.u8();counts['trace_sites']=r.n(128)
  for _ in range(counts['trace_sites']):r.text();r.coord()
  counts['trace_segments']=r.n(256)
  for _ in range(counts['trace_segments']):
   r.text();r.coord();r.coord();r.take(16)
   if r.u8():r.u64()
   if r.u8():r.u8()
   r.u8()
  counts['trace_samples']=r.n(budget)
  for _ in range(counts['trace_samples']):r.text();r.take(104);r.text()
 sections['trace']={'start':start,'end':r.i,'sha256':sha(b[start:r.i])}
 if r.i!=len(b):raise ValueError('Unparsed organizational suffix '+str(len(b)-r.i))
 return {'serialized_bytes':len(b),'sha256':sha(b),'chunks':n,'recipe_id':recipe_id,'version':version,'dimension':dim,'t0':t0,'domain':domain,'backend':backend,'threads':threads,'counts':counts,'sections':sections,'trace_saved':trace_saved},ops

def main():
 q=P/'fuentes/CONTRASTE_PREFIJOS_C2C_816019_PI05.json';before=q.read_bytes();j=json.loads(before)
 if'organizational_section_contrast'in j:raise ValueError('Already supplemented')
 sp=importlib.util.spec_from_file_location('pure_snapshot_parser',P/'codigo/contrastar_prefijos_C2C_PI05_pasivo.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);parsed={};ops={}
 for arm,v in j['views'].items():
  source=v['snapshot'];value=m.parse(Path(source['path']),source['sha256']);parsed[arm],ops[arm]=parse(value[6])
 result={}
 for a,b in [('real','none'),('real','yoked'),('none','yoked')]:
  x=parsed[a];y=parsed[b];diff=[]
  for i,(u,v)in enumerate(zip(ops[a],ops[b])):
   if u!=v:diff.append({'index':i,a:u,b:v})
  result[a+'_vs_'+b]={'sections':{k:x['sections'][k]['sha256']==y['sections'][k]['sha256']for k in x['sections']},'counts_exact':x['counts']==y['counts'],'external_operation_differences':diff,'only_external_operations_differ':all(x['sections'][k]['sha256']==y['sections'][k]['sha256']for k in x['sections']if k!='external_operations')}
 j['organizational_section_contrast']={'source_contract':'4.5/DEE_thinking_4_5_0/source/src/organizational.cpp:write_recipe/read_recipe,serialize/deserialize,lines76–130; save/load233–240','all_binary_bytes_parsed':True,'views':parsed,'comparisons':result,'scope':'Organizational protocol and operation records are inspected, not assumed equal from global RAW/clocks. No records are fed to the participant.'};j['prior_analysis_revision_sha256']=sha(before)
 if q.read_bytes()!=before:raise ValueError('Analysis map changed concurrently')
 q.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'map':str(q),'bytes':q.stat().st_size,'sha256':sha(q.read_bytes()),'counts':{k:v['counts']for k,v in parsed.items()},'comparisons':{k:{'sections':v['sections'],'operation_differences':len(v['external_operation_differences'])}for k,v in result.items()}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
