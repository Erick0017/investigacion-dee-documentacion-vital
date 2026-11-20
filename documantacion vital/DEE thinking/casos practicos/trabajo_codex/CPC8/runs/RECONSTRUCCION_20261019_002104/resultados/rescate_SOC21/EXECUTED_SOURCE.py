"""Selective old-CPC8 interval replay, explicitly NOT the new E1.

After T138 all used events are already in the official snapshot queue. The
generic official world, not a historical Python decision policy, evolves it.
Observation geometry is an auditor dependency and never feeds new inputs.
"""
import argparse,gc,hashlib,json,shutil,sys
from array import array
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking.persistence import load_world_snapshot,save_world_snapshot
def put(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def physical(w):return{'tick':int(w.runtime.current_tick),'RAW_sha256':hashlib.sha256(array('Q',w.runtime.raw_copy()).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',w.runtime.clock_copy()).tobytes()).hexdigest()}
def observe(w,q):return exact_observation(w.runtime.observe(d.Coordinate(*q)))
def move(q,v,k):return[(q[i]+v[i]*k)%131 for i in range(3)]
def run(out,prepare_source=None):
 bases=ROOT/'genealogia/primer_cpc8/SOC_I21';bases.mkdir(parents=True,exist_ok=True)
 if prepare_source:
  records=[]
  for n in('T138.deetsnap.gz','T166.deetsnap.gz','MEASUREMENTS.json','CONFIG.json'):
   p=prepare_source/n;t=bases/n
   if t.exists():
    if sha(t)!=sha(p):raise ValueError('Protected historical selection changed')
   else:shutil.copyfile(p,t)
   records.append({'original_member':'CPC8/resultados/semantica/SOC_I21_SOCIAL_THEN_L01_REVISION/'+n,'selected_file':t.relative_to(ROOT).as_posix(),'sha256':sha(t),'bytes':t.stat().st_size})
  put(bases/'SELECCION.json',{'historical_zip_sha256':'65164c939621464c7d4faa800240bb1c2e25538ba9d878a65863016f57387c00','files':records,'not_new_MAIN':True})
 out.mkdir(parents=True,exist_ok=False);shutil.copyfile(Path(__file__),out/'EXECUTED_SOURCE.py');m=json.loads((bases/'MEASUREMENTS.json').read_text(encoding='utf-8'));g=m['geometry']['social'];parts=g['parts']
 cfg={'schema':'CPC8R.heritage.SOC21.replay.v1','parent':'genealogia/primer_cpc8/SOC_I21/T138.deetsnap.gz','parent_sha256':sha(bases/'T138.deetsnap.gz'),'frozen_before_load':True,
 'scope':'Replay138→166 covers native transmitted product, pedagogical encounter140, receiver157 and contextualdelivery166. It does not independently reproduce prior acquisition/query0→138 or later33acquisitions/L01revision.',
 'intervention':'Fixed four declared message-route sites at138, cutRAWonly or byteidenticalsham. Clocks/queues/channels and all recipient supplies preserved. No fork data returned to historical parent or newE1.',
 'future_external_inputs':[]}
 put(out/'CONFIG.json',cfg);parent,_=load_world_snapshot(bases/'T138.deetsnap.gz',max_bytes=1024**3);before=physical(parent);rows=[]
 for condition in('intact','message_sham','message_cut'):
  edits=[];interventions=[]
  if condition!='intact':
   for key,part in parts.items():
    q=move(part['source_action'],part['source_direction'],2);o=observe(parent,q);e=d.ResearchStateEdit();e.coordinate=d.Coordinate(*q);e.raw=int(o['raw'])if condition=='message_sham'else 0;e.label='InheritedSOC21 fixed message window '+condition;edits.append(e);interventions.append({'candidate':key,'pre':o,'new_raw':str(e.raw),'clock_edit':None})
  w=parent.diagnostic_fork(edits,True);frames=[]
  for t in(138,139,140,156,157,160,161,165,166):
   w.run_until(t);sites={}
   for key,part in parts.items():
    for role in('hub','query_site','effect_site'):sites[key+'.'+role]=observe(w,part[role])
    for context,q in part['delivery_sites'].items():sites[key+'.delivery'+context]=observe(w,q)
   centers=[part['hub']for part in parts.values()]if t in(139,140)else[part['query_site']for part in parts.values()]if t in(156,157)else[]
   windows=[{'center':q,'Moore27':[observe(w,move(q,v,1))for v in((x,y,z)for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1))]}for q in centers]
   frames.append({'tick':t,'sites':sites,'windows':windows})
  save_world_snapshot(w,out/(condition+'_T166.deetsnap.gz'),compress=True)
  receipts=[{'id':x['id'],'receipt':exact_receipt(w.runtime.receipt(x['id']))}for x in m['requests']if x['receipt']['requested_tick']<=165]
  rows.append({'condition':condition,'interventions':interventions,'frames':frames,'final':physical(w),'receipts':receipts});del w;gc.collect()
 reference,_=load_world_snapshot(bases/'T166.deetsnap.gz',max_bytes=1024**3);ref=physical(reference)
 result={'case_id':'HERITAGE_SOC_I21_NATIVE_REPLAY','config':cfg,'preparations':0,'continuations':1,'diagnostic_forks':2,'technical_reproductions':1,'parent_before':before,'parent_after':physical(parent),'conditions':rows,'reference166':ref,
 'intact_exact_full_physical_equal':rows[0]['final']==ref,'sham_exact_full_physical_equal':rows[1]['final']==ref,'parent_unchanged':before==physical(parent),
 'observed_receiver157':[{'condition':x['condition'],'physical':next(f for f in x['frames']if f['tick']==157)['sites']['left.plus.query_site']}for x in rows],
 'lineage_gaps':'No unique genealogical assignment merely from matchingloads. This interval replays exact fullstate and local windows; causal cut isolates the declared transport window. Prior sources and latercapabilities remainhistorical references.'}
 put(out/'MEASUREMENTS.json',result);print(json.dumps({k:result[k]for k in('intact_exact_full_physical_equal','sham_exact_full_physical_equal','parent_unchanged','observed_receiver157')}))
if __name__=='__main__':
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--prepare-source',type=Path);a=p.parse_args();run(a.out,a.prepare_source)
