"""Read existing complete snapshots only: no experiment, probe or advance.

Recover admission denominators omitted by some early hand-recorded trials.
Outputs are auditor data and are never read by the operational participant.
"""
from pathlib import Path
import argparse,json,sys,hashlib,collections,gc
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.lives import load_adapter
from app.native_tools import physical
from app.process_control import protect_current
from dee_thinking.consolidated import exact_receipt
protect_current(output=a.out.with_suffix('.recursos.json'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
snapshots={sha(p):p for p in(a.system/'estado/checkpoints').glob('*.gz')};parents={};rows=[]
def receipts(runtime):
 r=runtime.receipts
 return[exact_receipt(v)for v in(r()if callable(r)else r)]
def parent_receipts(h,profile):
 if h in parents:return parents[h]
 x=load_adapter(profile,snapshots[h]);before=physical(x.world);r=receipts(x.world.runtime)
 if physical(x.world)!=before:raise AssertionError('Receipt read changed native parent')
 parents[h]={str(v['id']):v for v in r};del x;return parents[h]
files=sorted(a.data.rglob('PRIMARIOS.json'))
for i,p in enumerate(files):
 d=read(p);rel=p.relative_to(a.data).as_posix();commit=d.get('commit',{}).get('INSTRUMENTO',{});h=commit.get('snapshot_sha256');profile=commit.get('profile',d.get('parent',{}).get('profile'))
 if not h or h not in snapshots or not profile:
  rows.append({'primary':rel,'coverage':'NO_EXACT_COMMITTED_CHILD_SNAPSHOT_POINTER','not_assumed_zero':True});continue
 parent=d.get('parent',{});ph=parent.get('snapshot_sha256');old=parent_receipts(ph,profile)if ph in snapshots else{}
 x=load_adapter(profile,snapshots[h]);before=physical(x.world);allr=receipts(x.world.runtime);after=physical(x.world)
 if before!=after:raise AssertionError('Receipt read changed native child')
 expected=d.get('post',d.get('commit',{}).get('physical',{}))
 for key in('tick','RAW_sha256','clocks_sha256'):
  if key in expected and expected[key]!=before[key]:raise ValueError('Wrong historical child snapshot '+rel)
 new=[v for v in allr if str(v['id'])not in old];pending=[{'before':old[str(v['id'])],'after':v}for v in allr if str(v['id'])in old and old[str(v['id'])]['status']!=v['status']]
 rows.append({'primary':rel,'coverage':'COMPLETE_NATIVE_RECEIPT_SET_DIFFERENCE'if ph in snapshots else'COMPLETE_CHILD_RECEIPTS_PARENT_NOT_AVAILABLE','life':d.get('life'),'parent_snapshot_sha256':ph,'child_snapshot':str(snapshots[h]),'child_snapshot_sha256':h,'child_snapshot_bytes':snapshots[h].stat().st_size,'physical_before':before,'physical_after':after,'new_request_count':len(new),'new_request_statuses':dict(collections.Counter(v['status']for v in new)),'new_receipts':new,'inherited_receipt_transitions':pending,'all_child_receipts_count':len(allr),'all_parent_receipts_count':len(old)})
 del x;gc.collect()
 if i%25==0:print(json.dumps({'read_snapshots':i+1,'of':len(files)}),flush=True)
result={'schema':'DCS1.1.EF01.complete_receipt_extraction.v1','role':'AUDITOR','no_runtime_advance_or_probe':True,'method':'Exact committed child snapshot versus exact parent receipt-ID set, not current latest state. Inherited pending status changes separate. Existing primary fields preserve payloads; native receipts supply status/timing/admission denominators.','cases':rows,'coverage':dict(collections.Counter(r['coverage']for r in rows)),'receipt_sum_warning':'Different futures share past and are not independent samples. Do not pool these into a cognitive score.'}
a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result['coverage']))
