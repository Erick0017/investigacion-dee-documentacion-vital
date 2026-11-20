"""Compare the exact closed E3 cuts, never current VIDA or a Native owner."""
from pathlib import Path
import array,collections,datetime,gzip,hashlib,json,struct,sys,sqlite3
P4=Path(__file__).resolve().parents[1];S2=P4/'estados/candidato_R02/sistema'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
class Reader:
 def __init__(self,b):self.b=b;self.i=0
 def take(self,n):
  if n<0 or self.i+n>len(self.b):raise ValueError('Truncated snapshot')
  v=self.b[self.i:self.i+n];self.i+=n;return v
 def u8(self):return self.take(1)[0]
 def u32(self):return struct.unpack('<I',self.take(4))[0]
 def u64(self):return struct.unpack('<Q',self.take(8))[0]
 def text(self):
  n=self.u32()
  if n>16*1024*1024:raise ValueError('String limit')
  return self.take(n).decode('utf-8')
 def count(self):
  n=self.u32()
  if n>1000000:raise ValueError('Count limit')
  return n
def decode(value):
 digits=[(value>>k)&15 for k in(48,52,56)]
 return {'RAW':str(value),'state':value&0xffffffff,'s_reg':(value>>32)&65535,'semantic':value>>60,'direction':[v-16 if v&8 else v for v in digits]}
def parse(path,expected):
 encoded=path.read_bytes()
 if sha(encoded)!=expected:raise ValueError('Closed snapshot hash differs')
 payload=gzip.decompress(encoded);r=Reader(payload[:-8])
 if r.take(8)!=b'DEETSNP1'or r.u32()!=2:raise ValueError('Unexpected snapshot format')
 n=r.u32();tick=r.u64();paused=r.u8();next_event_id=r.u64();next_sequence=r.u64();phase=r.text();count=r.u64()
 if n!=67 or count!=n**3:raise ValueError('Expected N67')
 raw_bytes=r.take(count*8);clock_bytes=r.take(count*8)
 raw=array.array('Q');raw.frombytes(raw_bytes);clocks=array.array('Q');clocks.frombytes(clock_bytes)
 if sys.byteorder!='little':raw.byteswap();clocks.byteswap()
 start=r.i;channels=[]
 for _ in range(r.count()):channels.append((r.text(),r.take(31).hex()))
 channel_bytes=payload[start:r.i];start=r.i;pending=[]
 for _ in range(r.count()):
  item={'boundary':r.u64(),'id':r.u64(),'kind':r.u8(),'requested_tick':r.u64(),'sequence':r.u64()}
  item['channels']=[r.text()for _ in range(r.count())];item['writes']=[r.take(20).hex()for _ in range(r.count())];pending.append(item)
 pending_bytes=payload[start:r.i];start=r.i;receipts=[]
 for _ in range(r.count()):
  item={'id':r.u64(),'kind':r.u8(),'status':r.u8(),'requested_tick':r.u64()}
  item['effective_tick']=r.u64()if r.u8()else None;item['channels']=[r.text()for _ in range(r.count())];item['reason']=r.text();receipts.append(item)
 receipt_bytes=payload[start:r.i];backend=r.u8();threads=r.u64();prefix=r.i;metadata={r.text():r.text()for _ in range(r.count())}
 if r.i!=len(payload)-8:raise ValueError('Unparsed trailing data')
 banks=[]
 for label,site in(('A',[18,53,5]),('B',[20,53,5])):
  i=(site[0]*n+site[1])*n+site[2];banks.append({'label':label,'site':site,'clock':int(clocks[i]),**decode(raw[i])})
 public={'snapshot':{'path':str(path),'bytes':len(encoded),'sha256':sha(encoded)},'physical':{'N':n,'tick':tick,'RAW_sha256':sha(raw_bytes),'clocks_sha256':sha(clock_bytes)},
  'phase':phase,'paused':bool(paused),'next_event_id':next_event_id,'next_sequence':next_sequence,'backend_enum':backend,'threads':threads,'interfaces_count':len(channels),'interface_specs_sha256':sha(channel_bytes),'pending_count':len(pending),'pending_sha256':sha(pending_bytes),'pending':pending,
  'receipts_count':len(receipts),'receipts_block_sha256':sha(receipt_bytes),'causal_prefix_sha256':sha(payload[:prefix]),'metadata_keys':len(metadata),'metadata_serialized_sha256':sha(json.dumps(metadata,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')),
  'banks':banks,'RAW_nonzero':sum(v!=0 for v in raw),'state_active':sum((v&0xffffffff)>0 for v in raw),'s_reg_sum_all_sites':sum((v>>32)&65535 for v in raw),'s_reg_sum_active_sites':sum((v>>32)&65535 for v in raw if v&0xffffffff)}
 return public,raw,clocks,channels,pending,receipts,metadata,raw_bytes,clock_bytes

P5=Path(__file__).resolve().parents[1];P4=P5.parent/'PROGRESION_INTEGRADA_04';R=P5.parents[2];C=R/'DEE Cognitive 2.0';S2=P4/'estados/candidato_R02/sistema'
def fileinfo(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':sha(b)}
def jsondiff(a,b,path='',items=None):
 if items is None:items=[]
 if type(a)!=type(b):items.append({'pointer':path,'a':small(a),'b':small(b)});return items
 if isinstance(a,dict):
  for k in sorted(set(a)|set(b)):
   if k not in a or k not in b:items.append({'pointer':path+'/'+str(k),'a':small(a.get(k)),'b':small(b.get(k))})
   else:jsondiff(a[k],b[k],path+'/'+str(k),items)
 elif isinstance(a,list):
  if len(a)!=len(b):items.append({'pointer':path+'/length','a':len(a),'b':len(b)})
  for i,(x,y)in enumerate(zip(a,b)):jsondiff(x,y,path+'/'+str(i),items)
 elif a!=b:items.append({'pointer':path,'a':small(a),'b':small(b)})
 return items
def small(v):
 text=json.dumps(v,ensure_ascii=False,separators=(',',':'))
 return v if len(text)<=220 else {'serialized_bytes':len(text.encode()),'sha256':sha(text.encode()),'first80':text[:80]}
def metamap(a,b):
 result=[]
 for key in sorted(set(a)|set(b)):
  if a.get(key)==b.get(key):continue
  x=a.get(key);y=b.get(key);diff=None
  try:diff=jsondiff(json.loads(x),json.loads(y))
  except(TypeError,ValueError):pass
  result.append({'key':key,'a_bytes':len(x.encode())if x is not None else None,'b_bytes':len(y.encode())if y is not None else None,'a_sha256':sha(x.encode())if x is not None else None,'b_sha256':sha(y.encode())if y is not None else None,'different_scalar_fields':len(diff)if diff is not None else None,'field_differences':diff})
 return result

def environment(home):
 device=home/'PI04_C2C_COORDINACION_R01/dispositivo';state=device/'ESTADO_DISPOSITIVO.json';before=fileinfo(state);m=read(state)
 if m['ordinal']!=20 or m['pending']is not None or m['feedback_pending']is not None or m['uncertain']:raise ValueError('Exact closed20 environment required')
 files={p.relative_to(device).as_posix():fileinfo(p)for p in sorted(device.rglob('*'))if p.is_file()}
 verified=[]
 for p in m['products']:
  rel=p['path'];f=files[rel]
  if f['bytes']!=p['bytes']or f['sha256']!=p['sha256']:raise ValueError('Product bytes mismatch')
  actual=int.from_bytes((device/rel).read_bytes()[:2],'little',signed=False)
  if actual!=p['actual_native_integer']:raise ValueError('Actual integer in product differs')
  verified.append({'file':rel,'actual_native_integer':actual,'bytes':f['bytes'],'sha256':f['sha256']})
 if fileinfo(state)!=before:raise ValueError('Environment changed concurrently')
 return {'home':str(home.resolve()),'state':before,'version':m['version'],'law':m['environment'],'ordinal':m['ordinal'],'resources_total':len(m['resources']),'products':len(m['products']),'rejections':len(m['rejections']),'products_verified':verified,'device_files':files,'pending':m['pending'],'feedback_pending':m['feedback_pending'],'uncertain':m['uncertain'],'source_is_private_environment_not_cognitive_memory':True}

def backend(db):
 before=fileinfo(db);aux={p.name:fileinfo(p)for p in db.parent.glob(db.name+'-*')if p.is_file()}
 if any(n.endswith('-wal')and v['bytes']for n,v in aux.items()):return {'database':before,'auxiliaries':aux,'read_sqlite':False,'reason':'Nonempty WAL requires coherent closed export; no immutable reader ignores it'}
 con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  tables=[]
  for name,sql in con.execute("SELECT name,sql FROM sqlite_master WHERE type='table'ORDER BY name"):
   q='"'+name.replace('"','""')+'"';columns=[x[1]for x in con.execute('PRAGMA table_info('+q+')')];row={'name':name,'schema':sql,'rows':con.execute('SELECT COUNT(*) FROM '+q).fetchone()[0],'columns':columns}
   if'status'in columns:row['status_counts']={str(k):v for k,v in con.execute('SELECT status,COUNT(*) FROM '+q+' GROUP BY status')}
   tables.append(row)
  quick=[r[0]for r in con.execute('PRAGMA quick_check')]
 finally:con.close()
 after=fileinfo(db);auxafter={p.name:fileinfo(p)for p in db.parent.glob(db.name+'-*')if p.is_file()}
 if before!=after or aux!=auxafter:raise ValueError('Concurrent backend change; do not certify coherent read')
 return {'database':before,'auxiliaries':aux,'read_sqlite':True,'mode':'read-only immutable after no-WAL gate; before/after file hashes equal','quick_check':quick,'tables':tables,'not_equal_to_Native_cognitive_memory':True}

def main():
 out=P5/'fuentes/CONTRASTE_PREFIJOS_C2C_816019_PI05.json'
 if out.exists():raise FileExistsError('Preserve prior comparison; no overwrite')
 sources={};values={};views={}
 for arm,name,life in [('real','PI04_C2C_REAL_RES_R01.json','ECI02_PI03_REPRO_PI04_MAIN_02'),('none','PI04_C2C_NONE20_R01.json','ECI02_PI03_REPRO_PI04_C2C_NONE_01'),('yoked','PI04_C2C_YOKE20_R01.json','ECI02_PI03_REPRO_PI04_C2C_YOKE_01')]:
  p=P4/'control'/name;j=read(p);cut=j['final']['committed_snapshot'];v=parse(S2/cut['snapshot'],cut['snapshot_sha256'])
  if not j['owner_closed']or v[0]['physical']['tick']!=816019 or j['life']!=life:raise ValueError('Exact prior closed summary required')
  values[arm]=v;sources[arm]=fileinfo(p);view=v[0];view['life_id']=life;view['C2C_native_metadata']=json.loads(v[6]['DEE.Cognitive.PI04.C2C.coordination.R01']);view['known_C2C_products']=sum(r['useful_product']for r in view['C2C_native_metadata']['rows'])
  if arm=='real':pair=C/'reproducibilidad/materiales/PI03_PI04_C2C_POST_RES_T816019';home=pair/'artefactos_trabajador';db=pair/'cola.sqlite3';view['operational_source_scope']='Stable exactT816019 full pair; NOT current main02 home after ret2/panel'
  else:home=S2/'estado/servicios_locales'/life;db=S2/'estado/servicios_persistentes'/life/'cola.sqlite3';view['operational_source_scope']='Closed control currentT816019; environment/SQLite sampled with before/after equality. Root must export complete pair before new Native.'
  view['environment']=environment(home);view['backend_SQLite']=backend(db);views[arm]=view
 comparisons={}
 for aa,bb in [('real','none'),('real','yoked'),('none','yoked')]:
  a=values[aa];b=values[bb];rd=[];cd=[]
  for i,(x,y)in enumerate(zip(a[1],b[1])):
   if x!=y:rd.append({'site':[i//4489,(i//67)%67,i%67],aa:decode(x),bb:decode(y)})
   if a[2][i]!=b[2][i]:cd.append([i//4489,(i//67)%67,i%67])
  ra={r['id']:r for r in a[5]};rb={r['id']:r for r in b[5]};rc=[{'id':k,aa:ra.get(k),bb:rb.get(k)}for k in sorted(set(ra)|set(rb))if ra.get(k)!=rb.get(k)]
  controlfields=['paused','next_event_id','next_sequence','backend_enum','threads','phase']
  comparisons[aa+'_vs_'+bb]={'RAW_exact':a[7]==b[7],'clocks_exact':a[8]==b[8],'RAW_different_sites':rd,'clock_difference_positions':cd,'execution_header':{k:{aa:a[0][k],bb:b[0][k],'equal':a[0][k]==b[0][k]}for k in controlfields},'interfaces_exact':a[3]==b[3],'Native_agenda_exact':a[4]==b[4],'receipt_history_exact':a[5]==b[5],'receipt_difference_count':len(rc),'receipt_differences':rc,'metadata_exact':a[6]==b[6],'metadata_differences':metamap(a[6],b[6]),'full_operational_identity_NOT_claimed':True}
 result={'schema':'DEE.PI05.C2C.complete_available_prefices.passive.v1','inspection_local':datetime.datetime.now().astimezone().isoformat(),'mode':'FROZEN_NATIVE_SNAPSHOTS_PLUS_CLOSED_ENVIRONMENT_AND_READONLY_SQLITE','Native_ticks':0,'DEE_imports':0,'source_files_modified':False,'source_contract':'Thinking4.5 source/src/runtime.cpp save_snapshot/read_snapshot,lines612–814; original parser PI04 contrastar_finales_E3_pasivo.py extended with explicit header/backend and correct pending-field names','sources':sources,'views':views,'comparisons':comparisons,'limits':['Gzip CRC, encoded SHA and complete parsing checked; Native internal FNV not recalculated by this reader.','REAL backend/environment is a coherent exported pair; NONE/YOKE closed home/SQLite are not mislabeled as already-exported pairs.','Transport SQLite and environment differ by actual history and identity; none are cognitive answer tables for the participant.','No interpretation assumes persistent17particle, physical content erasure, learned-plan or true-contingency advantage.','Both control Native plans contain20completed rows; oldYOKEcontract is exhausted and must receive an explicit future-control extension, never a reset.']}
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'output':fileinfo(out),'comparisons':{k:{n:v[n]for n in['RAW_exact','clocks_exact','interfaces_exact','Native_agenda_exact','receipt_difference_count','metadata_exact']}|{'RAWdiff':len(v['RAW_different_sites']),'metadiff':len(v['metadata_differences'])}for k,v in comparisons.items()},'products':{k:v['environment']['products']for k,v in views.items()}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
