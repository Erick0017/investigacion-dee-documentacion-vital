"""Portable exact F1 strict-identity-stop autopsy, stdlib only.
No Native, no actor import, no new cut, no waived preregistration. The original
sealed F1R03 remains unchanged. Native internal FNV is not recomputed; indexed
encoded SHA/gzip CRC and full binary format/arrays are checked.
"""
from pathlib import Path,PurePosixPath
import argparse,gzip,hashlib,json,struct
def sha(b):return hashlib.sha256(b).hexdigest()

def need(b,t):
    if not b:raise ValueError(t)

def local(root,e):
    name=e['file'];need(isinstance(name,str)and name and '\\'not in name and ':'not in name,'Portable indexed relative path')
    rel=PurePosixPath(name);need(not rel.is_absolute()and not any(x in ('.','..')for x in rel.parts),'Escaping path')
    q=root.joinpath(*rel.parts)
    for node in(q,*q.parents):
        if node==root.parent:break
        need(not node.is_symlink()and not(getattr(node.lstat(),'st_file_attributes',0)&1024),'No link/reparse')
    q=q.resolve(strict=True);need(q.is_relative_to(root),'Outside extraction')
    data=q.read_bytes();need(len(data)==e['bytes']and sha(data)==e['sha256'],'Indexed snapshot/evidence bytes differ')
    return q,data

def ptr(j,p):
    need(isinstance(p,str)and p.startswith('/'),'Explicit JSON pointer')
    for k in p[1:].split('/'):
        k=k.replace('~1','/').replace('~0','~');j=j[int(k)]if isinstance(j,list)else j[k]
    return j

class _Reader:
    def __init__(self,b):self.b=memoryview(b)[:-8];self.i=0
    def take(self,n):
        if n<0 or self.i+n>len(self.b):raise ValueError('Truncated Native diagnostic snapshot')
        value=self.b[self.i:self.i+n];self.i+=n;return value
    def u8(self):return self.take(1)[0]
    def u32(self):return struct.unpack('<I',self.take(4))[0]
    def u64(self):return struct.unpack('<Q',self.take(8))[0]
    def count(self):
        n=self.u32()
        if n>1000000:raise ValueError('Native snapshot count bound')
        return n
    def text(self):
        n=self.u32()
        if n>16*1024*1024:raise ValueError('Native snapshot string bound')
        return self.take(n).tobytes().decode('utf-8')
    def skip_text(self):
        n=self.u32()
        if n>16*1024*1024:raise ValueError('Native snapshot string bound')
        self.take(n)

def _snapshot_fields(path,keep_raw=False):
    encoded=Path(path).read_bytes();payload=gzip.decompress(encoded);r=_Reader(payload)
    if r.take(8).tobytes()!=b'DEETSNP1'or r.u32()!=2:raise ValueError('Native v2 snapshot required')
    n=r.u32();tick=r.u64();paused=r.u8();next_id=r.u64();next_sequence=r.u64();phase=r.text();count=r.u64()
    if n!=67 or count!=n**3:raise ValueError('Exact complete N67 snapshot required')
    raw=r.take(count*8);clocks=r.take(count*8)
    raw_hash=sha(raw);clock_hash=sha(clocks);raw_copy=raw.tobytes()if keep_raw else None;clock_copy=clocks.tobytes()if keep_raw else None
    start=r.i;nc=r.count()
    for _ in range(nc):r.skip_text();r.take(31)
    channel_hash=sha(r.b[start:r.i]);start=r.i;npending=r.count()
    for _ in range(npending):
        r.take(8+8+1+8+8)
        for _ in range(r.count()):r.skip_text()
        r.take(20*r.count())
    pending_hash=sha(r.b[start:r.i]);start=r.i;nreceipts=r.count()
    for _ in range(nreceipts):
        r.take(8+1+1+8)
        if r.u8():r.take(8)
        for _ in range(r.count()):r.skip_text()
        r.skip_text()
    receipt_hash=sha(r.b[start:r.i]);backend=r.u8();threads=r.u64();causal=sha(r.b[:r.i]);metadata_start=r.i;nm=r.count()
    metadata={}
    for _ in range(nm):
        key=r.text();value=r.text();metadata[key]=value
    if r.i!=len(r.b):raise ValueError('Unparsed Native diagnostic bytes')
    return {'snapshot':{'path':str(path),'bytes':len(encoded),'sha256':sha(encoded)},
        'N':n,'tick':tick,'RAW_sha256':raw_hash,'clocks_sha256':clock_hash,'paused':bool(paused),
        'next_event_id':next_id,'next_sequence':next_sequence,'phase':phase,'interfaces_count':nc,
        'interfaces_sha256':channel_hash,'pending_count':npending,'pending_sha256':pending_hash,
        'receipts_count':nreceipts,'receipts_sha256':receipt_hash,'backend':backend,'threads':threads,
        'Native_causal_prefix_sha256':causal,'metadata_key_count':nm,
        'metadata_serialized_sha256':sha(r.b[metadata_start:r.i]),
        'Native_complete_content_sha256':sha(r.b[:r.i]),
        'verification_scope':'Gzip CRC and full Native-v2 parse; internal Native FNV not separately recalculated.'},(raw_copy,clock_copy,metadata)
class OrgReader:
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

def parse_org(meta):
 prefix='dee_thinking.organizational.v1.';n=int(meta[prefix+'chunks']);b=bytes.fromhex(''.join(meta[prefix+str(i)]for i in range(n)));r=OrgReader(b);sections={};counts={};ops=[]
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

def diagnostic_edit_records(meta,view):
    prefix='dee_thinking.organizational.v1.'
    data=bytes.fromhex(''.join(meta[prefix+str(i)]for i in range(int(meta[prefix+'chunks']))))
    sec=view['sections']['diagnostic_edits'];r=OrgReader(data[sec['start']:sec['end']]);rows=[]
    for _ in range(r.n()):
        site=list(struct.unpack('<qqq',r.take(24)));label=r.text();tick,rb,ra,cb,ca=struct.unpack('<QQQQQ',r.take(40));mod=r.u8()
        rows.append({'site':site,'label':label,'tick':tick,'RAW_before':str(rb),'RAW_after':str(ra),'clock_before':str(cb),'clock_after':str(ca),'modality_enum':mod})
    return rows

def calculate(root,index_name):
    root=Path(root).resolve(strict=True);rel=PurePosixPath(index_name)
    need(not rel.is_absolute()and '..'not in rel.parts and ':'not in index_name and '\\'not in index_name,'Relative indexonly')
    ip=root.joinpath(*rel.parts);index=json.loads(ip.read_text('utf-8-sig'))
    need(index['schema']=='DEE.PI08.F1.identity_failure.portable.v1','Exact strict-identity-failure index')
    beforep,_=local(root,index['before']);identityp,_=local(root,index['identity'])
    before,(br,bc,bm)=_snapshot_fields(beforep,True);identity,(ir,ic,im)=_snapshot_fields(identityp,True)
    need(br==ir and bc==ic,'Physical RAW/clocks differ: not the observed audit-only result')
    need(before['Native_causal_prefix_sha256']==identity['Native_causal_prefix_sha256'],'Native header/phase/interfaces/agenda/receipts differ')
    need(before['metadata_serialized_sha256']!=identity['metadata_serialized_sha256']and before['Native_complete_content_sha256']!=identity['Native_complete_content_sha256'],'Strict metadata identity did not actually fail')
    need(identity['metadata_key_count']==before['metadata_key_count']+2,'Unexpected metadata-key count')
    flags={'dee_thinking.diagnostic_fork':'true','dee_thinking.diagnostic_edit_count':'1'}
    for key,value in flags.items():need(key not in bm and im.get(key)==value,'Expected runtime audit flags differ')
    prefix='dee_thinking.organizational.v1.'
    restb={k:v for k,v in bm.items()if not k.startswith(prefix)and k not in flags}
    resti={k:v for k,v in im.items()if not k.startswith(prefix)and k not in flags}
    need(restb==resti,'Other Native metadata differs')
    ob,opsb=parse_org(bm);oi,opsi=parse_org(im)
    equal={k:ob['sections'][k]['sha256']==oi['sections'][k]['sha256']for k in ob['sections']}
    need(all(v for k,v in equal.items()if k!='diagnostic_edits')and not equal['diagnostic_edits'],'Organizational difference not confined to diagnostic-edit audit')
    need(opsb==opsi,'Externaloperation history differs')
    eb=diagnostic_edit_records(bm,ob);ei=diagnostic_edit_records(im,oi)
    need(not eb and len(ei)==1,'One structural diagnostic record only')
    record=ei[0]
    need(record['site']==[52,48,56]and record['tick']==before['tick']and record['modality_enum']==5,'Exact recorded diagnostic fork differs')
    need(record['RAW_before']==record['RAW_after']and record['clock_before']==record['clock_after'],'Identity diagnostic actually edited physical value')
    idx=((52*67+48)*67+56)*8
    need(str(struct.unpack_from('<Q',br,idx)[0])==record['RAW_before']and str(struct.unpack_from('<Q',bc,idx)[0])==record['clock_before'],'Recorded physical values do not match exact buffers')
    proofp,data=local(root,index['actual_failure_proof']);proof=json.loads(data)
    need(proof['status']=='STOPPED_PRESERVED'and proof['closed']is True and proof['new_Native_ticks']==378,'Actual preserved F1stop proof differs')
    need(proof['initial_tick']==849645 and proof['final_tick']==before['tick']==850023,'Actual observed partial Nativecut differs')
    need(not proof['rows'] and proof['identity_sham_Native_future_ticks']==0,'No successful material cut or new identityfuture may be claimed')
    parent_report=index['parent_after_identity_encoded_bytes_sha256_reported']
    need(parent_report==index['before']['sha256'],'Reported parent-after-identity did not remain bitwise equivalent')
    parent_evidence=index['parent_after_identity_proof'];_,parent_data=local(root,parent_evidence['evidence'])
    need(ptr(json.loads(parent_data),parent_evidence['pointer'])==parent_report,'Reported parent identity not bound to included passive source proof')
    return{'schema':'DEE.PI08.F1.recalculated_strict_identity_failure.R04','all_checks_passed':True,'new_Native_ticks':0,'DEE_imports':0,
      'actual_recorded_Native_ticks':378,'actual_imported_worlds':1,'actual_identity_forks':1,'actual_cut_forks':0,'budget_worldslots_used':2,
      'Native_RAW_complete_bytes_equal':True,'Native_clocks_complete_bytes_equal':True,'Native_causal_prefix_equal_before_metadata':True,
      'complete_metadata_equal':False,'runtime_audit_flags_added':flags,'organizational_sections_equal':equal,'external_operation_history_equal':True,
      'diagnostic_receipt':record,'parent_after_identity_scope':'Encoded SHA reported in included passiveproof; third binary omitted as exact duplicate of parentbefore.',
      'parent_after_identity_encoded_sha256_reported':parent_report,'snapshots':{'before':before,'identity':identity},
      'no_new_sham_future':True,'actual_cut_executed':False,'behavioral_effect_tested':False,'strict_preregistered_check_waived':False,
      'runner_zero_counts_scope':'Runner collected no completed operation and reports0inputs/forks; these are incomplete aggregates, not proof0Native activity. Exact partial receipts recorded separately.',
      'scope':'Frozen2-snapshot documentary recalc only. The diagnostic API records an audit even for a physical identity edit; strict identity correctly failed. This does not authorize ignoring the audit or establish any effect of a RAWcut or later FI.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--raiz',required=True);ap.add_argument('--indice',default='INDICE_F1_IDENTITY_FALLO_PI08_R04.json');ap.add_argument('--salida',required=True);a=ap.parse_args();out=Path(a.salida);need(not out.exists(),'Freshoutputonly');v=calculate(a.raiz,a.indice)
    with out.open('x',encoding='utf-8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'all_checks_passed':True,'actual_cut_executed':False,'new_Native_ticks':0,'sha256':sha(out.read_bytes())},ensure_ascii=False))
if __name__=='__main__':main()
