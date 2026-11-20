"""Passive frozen original error-snapshot autopsy; no Native or database."""
from pathlib import Path
import gzip,hashlib,importlib.util,json,struct
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=P/'estados/REAL/sistema'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL_01';OUT=P/'control/AUTOPSIA_FALLO_PREVIEW_REAL_PI10_R01.json'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def main():
 need(not OUT.exists(),'Preserve previous autopsy')
 witness=P/'ensayos/PI10_REAL_F0_OWNER_R01_05.json';wbytes=witness.read_bytes();w=json.loads(wbytes);need(w['status']=='failed_preserved','Exact preserved failure receipt')
 error=json.loads(w['error']);f=error['failed_native_future_preserved'];snap=S/f['snapshot'];encoded=snap.read_bytes();need(sha(encoded)==f['snapshot_sha256'],'Exact immutable failure snapshot')
 pp=C/'reproducibilidad/observador_pasivo.py';spec=importlib.util.spec_from_file_location('P10_failure_std_parser',pp);passive=importlib.util.module_from_spec(spec);spec.loader.exec_module(passive)
 view=passive.snapshot_view(snap);data=gzip.decompress(encoded);r=passive.Reader(data[:-8]);need(r.take(8)==b'DEETSNP1'and r.u32()==2,'Known full snapshot version')
 n=r.u32();tick=r.u64();r.u8();r.u64();r.u64();phase=r.text();total=r.u64();need(n==67 and tick==928974 and total==n**3,'Exact failed cut')
 raw=r.take(8*total);clocks=r.take(8*total)
 def observe(site):
  x,y,z=site;index=(x*n+y)*n+z;v=struct.unpack_from('<Q',raw,index*8)[0];ds=[(v>>k)&15 for k in(48,52,56)]
  return {'site':list(site),'tick':tick,'raw':v,'clock':struct.unpack_from('<Q',clocks,index*8)[0],'state':v&0xffffffff,'s_reg':(v>>32)&65535,'semantic':v>>60,'direction':[d-16 if d&8 else d for d in ds]}
 channels=[]
 for _ in range(r.count()):
  name=r.text();site=[r.u32()for _ in range(3)];state=r.u32();direction=list(struct.unpack('<iii',r.take(12)));semantic=r.u8();experience=r.u8();probe=r.u8()
  if name.startswith('PI10.'):channels.append(dict(name=name,site=site,state=state,direction=direction,semantic=semantic,experience=experience,probe=probe))
 pending=r.count()
 for _ in range(pending):
  r.take(33)
  for _ in range(r.count()):r.text()
  r.take(20*r.count())
 receipts=[];receipt_count=r.count()
 for _ in range(receipt_count):
  ident=r.u64();kind=r.u8();status=r.u8();requested=r.u64();effective=r.u64()if r.u8()else None;names=[r.text()for _ in range(r.count())];reason=r.text()
  if any(name.startswith('PI10.')for name in names)and requested>=928600:receipts.append({'id':ident,'kind_enum':kind,'status_enum':status,'requested_tick':requested,'effective_tick':effective,'channels':names,'reason':reason})
 home=S/'estado/servicios_locales'/LIFE/'PI10_CONSULTA_ADAPTATIVA_R01';journal=home/'eventos.jsonl';lines=[json.loads(x)for x in journal.read_text('utf8').splitlines()];intent=next(v for v in reversed(lines)if v.get('kind')=='TWO_NATIVE_SELECTORS_OPPORTUNITY_INTENT')
 known=read(home/'episodio_0003.json');known_status={v['id']:v['receipt']['status']for v in known['requests']};enum_map={str(row['status_enum']):known_status[row['id']]for row in receipts if row['id']in known_status}
 for row in receipts:row['status_from_matching_prior_closed_receipt']=enum_map.get(str(row['status_enum']))
 preview=(30,40,30);sites={((preview[0]+x)%67,(preview[1]+y)%67,(preview[2]+z)%67)for x in range(-2,3)for y in(-1,0,1)for z in range(-2,3)}
 region=[observe(site)for site in sorted(sites)];center=observe(preview);clock_phase={'mod67':tick%67,'mod391':tick%391,'mod782':tick%782}
 out={'schema':'DEE.PI10.frozen_preview_failure_autopsy.R01','Native_imported':False,'new_ticks_in_this_recalculation':0,'receipt_source':{'file':str(witness),'sha256':sha(wbytes)},'error':{k:v for k,v in error.items()if k!='failed_native_future_preserved'},
  'snapshot':{'file':str(snap),'sha256':sha(encoded),'physical':view['physical'],'phase':phase,'pending_Native':pending,'receipt_count':receipt_count},'preview':center,'source_Z':observe((30,40,29)),'source_X':observe((29,40,30)),'device_region':region,'device_nonzero_RAW':[x for x in region if x['raw']!=0],
  'q1_center':observe((24,12,12)),'q1_A':observe((23,11,12)),'q1_B':observe((25,11,12)),'q2_A':observe((7,39,50)),'q2_B':observe((9,39,50)),
  'last_intent':intent,'actual_global_clock_phase':clock_phase,'recent_actual_Native_receipts':receipts,'status_enum_matching_prior_witness':enum_map,
  'PI10_progress':json.loads(view['metadata']['DEE.Cognitive.PI10.adaptive_query.two_native_traces.R01']),'journal':{'file':str(journal),'sha256':sha(journal.read_bytes())},
  'source_channels':[c for c in channels if c['name'].startswith('PI10.device.')],
  'interpretation_scope':'One full preserved failed state plus actual receipt and earlier complete episode. No continuous trajectory reconstructed; compound directions or payload do not by themselves identify ancestors. No retry, changed codec or new experiment.'}
 need(snap.read_bytes()==encoded and witness.read_bytes()==wbytes,'Frozen sources changed during read')
 with OUT.open('x',encoding='utf8')as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'file':str(OUT),'sha256':sha(OUT.read_bytes()),'preview':center,'device_nonzero_RAW':out['device_nonzero_RAW'],'recent_receipts':receipts[-4:],'pending_Native':pending,'last_intent_calendar':intent['calendar'],'actual_ordinal':out['PI10_progress']['ordinal']},ensure_ascii=False))
if __name__=='__main__':main()
