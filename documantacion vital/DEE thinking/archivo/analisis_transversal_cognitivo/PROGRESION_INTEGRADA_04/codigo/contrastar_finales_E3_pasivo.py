"""Compare the exact closed E3 cuts, never current VIDA or a Native owner."""
from pathlib import Path
import array,collections,datetime,gzip,hashlib,json,struct,sys
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
 n=r.u32();tick=r.u64();r.u8();r.u64();r.u64();phase=r.text();count=r.u64()
 if n!=67 or count!=n**3:raise ValueError('Expected N67')
 raw_bytes=r.take(count*8);clock_bytes=r.take(count*8)
 raw=array.array('Q');raw.frombytes(raw_bytes);clocks=array.array('Q');clocks.frombytes(clock_bytes)
 if sys.byteorder!='little':raw.byteswap();clocks.byteswap()
 start=r.i;channels=[]
 for _ in range(r.count()):channels.append((r.text(),r.take(31).hex()))
 channel_bytes=payload[start:r.i];start=r.i;pending=[]
 for _ in range(r.count()):
  item={'id':r.u64(),'seq':r.u64(),'kind':r.u8(),'tick':r.u64(),'payload':r.u64()}
  item['channels']=[r.text()for _ in range(r.count())];item['writes']=[r.take(20).hex()for _ in range(r.count())];pending.append(item)
 pending_bytes=payload[start:r.i];start=r.i;receipts=[]
 for _ in range(r.count()):
  item={'id':r.u64(),'kind':r.u8(),'status':r.u8(),'requested_tick':r.u64()}
  item['effective_tick']=r.u64()if r.u8()else None;item['channels']=[r.text()for _ in range(r.count())];item['reason']=r.text();receipts.append(item)
 receipt_bytes=payload[start:r.i];r.u8();r.u64();prefix=r.i;metadata={r.text():r.text()for _ in range(r.count())}
 if r.i!=len(payload)-8:raise ValueError('Unparsed trailing data')
 banks=[]
 for label,site in(('A',[18,53,5]),('B',[20,53,5])):
  i=(site[0]*n+site[1])*n+site[2];banks.append({'label':label,'site':site,'clock':int(clocks[i]),**decode(raw[i])})
 public={'snapshot':{'path':str(path),'bytes':len(encoded),'sha256':sha(encoded)},'physical':{'N':n,'tick':tick,'RAW_sha256':sha(raw_bytes),'clocks_sha256':sha(clock_bytes)},
  'phase':phase,'interfaces_count':len(channels),'interface_specs_sha256':sha(channel_bytes),'pending_count':len(pending),'pending_sha256':sha(pending_bytes),'pending':pending,
  'receipts_count':len(receipts),'receipts_block_sha256':sha(receipt_bytes),'causal_prefix_sha256':sha(payload[:prefix]),'metadata_keys':len(metadata),'metadata_serialized_sha256':sha(json.dumps(metadata,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')),
  'banks':banks,'RAW_nonzero':sum(v!=0 for v in raw),'state_active':sum((v&0xffffffff)>0 for v in raw),'s_reg_sum_all_sites':sum((v>>32)&65535 for v in raw),'s_reg_sum_active_sites':sum((v>>32)&65535 for v in raw if v&0xffffffff)}
 return public,raw,clocks,channels,pending,receipts,metadata,raw_bytes,clock_bytes
def main():
 out=P4/'control/E3_CONTRASTE_FISICO_FINAL_PASIVO.json'
 if out.exists():raise FileExistsError('Preserve prior comparison')
 inputs={};views={};parsed={}
 for arm in('real','desacoplado'):
  path=P4/f'control/E3_{arm}_R02.json';source_bytes=path.read_bytes();d=json.loads(source_bytes);cut=d['final']['committed_snapshot']
  if not d['owner_closed']or cut['physical']['tick']!=789431:raise ValueError('Exact closed E3 cut required')
  value=parse(S2/cut['snapshot'],cut['snapshot_sha256'])
  if value[0]['physical']!={k:cut['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')}:raise ValueError('Physical primary witness differs')
  public=value[0];public['life']=d['life'];public['E3_new_products']=d['products'];public['E3_included']=d['included'];public['E3_completed']=d['completed'];public['Native_ticks_recorded']=d['new_native_ticks']
  public['actual_failures']=sum(bool(x['actual_failed'])for x in d['rows']);public['returned_failures']=sum(bool(x['returned_failed'])for x in d['rows']);public['false_failures']=sum(x['returned_failed']and not x['actual_failed']for x in d['rows'])
  inputs[arm]={'path':str(path),'bytes':len(source_bytes),'sha256':sha(source_bytes)};views[arm]=public;parsed[arm]=value
 a=parsed['real'];b=parsed['desacoplado'];rawdiff=[];clockdiff=[];chargediff=[]
 for i,(x,y)in enumerate(zip(a[1],b[1])):
  site=[i//4489,(i//67)%67,i%67]
  if x!=y:rawdiff.append({'site':site,'real':decode(x),'desacoplado':decode(y)})
  if((x>>32)&65535)!=((y>>32)&65535):chargediff.append(site)
  if a[2][i]!=b[2][i]:clockdiff.append(site)
 receipt_a={x['id']:x for x in a[5]};receipt_b={x['id']:x for x in b[5]}
 receipt_differences=[{'id':k,'real':receipt_a.get(k),'desacoplado':receipt_b.get(k)}for k in sorted(set(receipt_a)|set(receipt_b))if receipt_a.get(k)!=receipt_b.get(k)]
 meta=[]
 for k in sorted(set(a[6])|set(b[6])):
  x=a[6].get(k);y=b[6].get(k)
  if x!=y:meta.append({'key':k,'real_bytes':len(x.encode('utf-8'))if x is not None else None,'desacoplado_bytes':len(y.encode('utf-8'))if y is not None else None,'real_sha256':sha(x.encode('utf-8'))if x is not None else None,'desacoplado_sha256':sha(y.encode('utf-8'))if y is not None else None})
 proof={'schema':'PI04.E3.closed_final_physical_comparison.passive.v1','inspection_local':datetime.datetime.now().astimezone().isoformat(),'mode':'FROZEN_EXACT_SNAPSHOTS_PRIOR_TO_C2; no current VIDA, SQLite or owner opened','inputs':inputs,'views':views,
  'comparison':{'GLOBAL_RAW_bytes_exact':a[7]==b[7],'GLOBAL_clocks_bytes_exact':a[8]==b[8],'RAW_different_sites':len(rawdiff),'RAW_differences':rawdiff,'clocks_different_sites':len(clockdiff),'clock_difference_positions':clockdiff,'s_reg_different_sites':len(chargediff),'s_reg_difference_positions':chargediff,'interface_specs_exact':a[3]==b[3],'pending_exact':a[4]==b[4],'receipt_history_exact':a[5]==b[5],'receipt_difference_count':len(receipt_differences),'receipt_differences':receipt_differences,'metadata_exact':a[6]==b[6],'metadata_different_keys':meta,'causal_prefix_exact':a[0]['causal_prefix_sha256']==b[0]['causal_prefix_sha256'],'encoded_snapshots_equal':a[0]['snapshot']['sha256']==b[0]['snapshot']['sha256']},
  'interpretation':{'physical_RAW_clocks_convergence_only':True,'not_full_causal_or_operational_identity':True,'external_environment_total_products':{'real':33,'desacoplado':37},'environment_count_scope':'19 inherited PI03 products plus the14 or18 recorded E3 products; these are separate actual device histories, not a merged score or cognitive state.',
   'future_scope':'Equal RAW/clocks do not establish equal complete future behavior: receipt histories, metadata, external resources/products and transport differ. The comparison neither tests future common inputs nor proves historical information lost from the whole declared organization.',
   'no_autonomy_or_promotion_inferred':True},'new_Native_ticks':0,'DEE_imports':0,'operational_files_modified':False,'gzip_CRC_checked':True,'internal_FNV_recalculation':False}
 out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'output':str(out),'bytes':out.stat().st_size,'sha256':sha(out.read_bytes()),'comparison':{k:v for k,v in proof['comparison'].items()if not isinstance(v,list)},'banks':{k:v['banks']for k,v in views.items()},'receipt_diffs':len(receipt_differences),'metadata_diffs':len(meta),'new_Native_ticks':0},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
