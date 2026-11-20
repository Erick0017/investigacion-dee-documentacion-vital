"""Recalculate finite relational measurements; never imported by participants."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
SCHEMAS={
 'CPC8R.mode_reference.measurements.v1':'MODE','CPC8R.mode_reference.control.v1':'MODE_CONTROL',
 'CPC8R.mode_communication.measurements.v1':'MODE_SOCIAL','CPC8R.mode_communication.diagnostic.v1':'MODE_SOCIAL_CONTROL','CPC8R.mode_communication.restore.v1':'TECHNICAL_RESTORE',
 'CPC8R.spatial_arrival.measurements.v1':'SPATIAL_ARRIVAL_DISCOVERY','CPC8R.spatial_gradient.calibration.v1':'SPATIAL_SENSOR_CALIBRATION',
 'CPC8R.spatial_reference.measurements.v1':'SPATIAL_REFERENCE','CPC8R.spatial_reference.diagnostic.v1':'SPATIAL_REFERENCE_CONTROL',
 'CPC8R.spatial_communication.measurements.v1':'SPATIAL_SOCIAL','CPC8R.spatial_communication.diagnostic.v1':'SPATIAL_SOCIAL_CONTROL','CPC8R.spatial_communication.restore.v1':'TECHNICAL_RESTORE',
 'CPC8R.spatial_context.measurements.v1':'SPATIAL_NATIVE_CONTEXT','CPC8R.spatial_context.diagnostic.v1':'SPATIAL_NATIVE_CONTEXT_CONTROL','CPC8R.spatial_context.restore.v1':'TECHNICAL_RESTORE',
 'CPC8R.full_spatialE1.measurements.v1':'FRESH_FULL_E1_SPATIAL',
 'CPC8R.full_spatialE1.access_diagnostic.v1':'FRESH_FULL_E1_ACCESS_CONTROL',
 'CPC8R.contact_socialE1.measurements.v1':'CONTACT_SOCIAL_E1_DISCOVERY',
 'CPC8R.contact_socialE1.regulated.v1':'CONTACT_SOCIAL_E1_REGULATED',
 'CPC8R.contact_socialE1.diagnostic.v1':'CONTACT_SOCIAL_E1_CONTROL',
 'CPC8R.contact_socialE1.restore.v1':'TECHNICAL_RESTORE'
}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def flatten(captures):
 if isinstance(captures,list):return captures
 return[{**x,'candidate_reference':key}for key,rows in captures.items()for x in rows]
def analyze(root):
 out=[];totals=Counter();semantic=[]
 for p in sorted((root/'resultados/semantica').glob('*/MEASUREMENTS.json')):
  m=json.loads(p.read_text(encoding='utf-8'));schema=m.get('schema');family=SCHEMAS.get(schema)
  if family is None:raise ValueError('Unregistered primary semantic schema: '+str(schema)+' '+str(p))
  technical=family=='TECHNICAL_RESTORE';failed=m.get('status')=='TECHNICAL_ERROR';prepared=0 if failed and not m.get('snapshots')else m.get('preparations',0)
  req=m.get('requests',[]);ids=[r['id']for r in req];assert len(ids)==len(set(ids)),p
  admission=Counter(x.get('receipt',{}).get('status','MISSING_RECEIPT')for x in req)
  counts={'preparations':prepared,'diagnostic_forks':m.get('diagnostic_forks',0),'scientific_continuations':0 if technical else m.get('continuations',0),'technical_continuations':m.get('continuations',0)if technical else 0,'technical_failed_preparation_attempts':int(failed)}
  totals.update(counts);totals['primary_records']+=1;totals['new_requests']+=len(req)if prepared else 0
  row={'case_id':m.get('case',{}).get('id',p.parent.name),'schema':schema,'family':family,'path':p.relative_to(root).as_posix(),'sha256':sha(p),'status':m.get('status'),'case':m.get('case',{}),'parent':m.get('parent'),**counts,'requests_all_including_inherited':len(req),'requests_new':len(req)if prepared else 0,'admission_all_including_inherited':dict(admission),'physics_comparison':m.get('checks'),'parent_unchanged':m.get('parent_unchanged'),'source_sha256':m.get('source_sha256'),'configuration_sha256':m.get('configuration_sha256',m.get('config_sha256')),'snapshot_count':len(m.get('snapshots',[]))}
  caps=flatten(m.get('spatial_captures',m.get('captures',m.get('captures_after_fork',[]))));window=[]
  for stage in sorted({x['stage']for x in caps}):
   cs=[x for x in caps if x['stage']==stage];valid=[x for x in cs if x['covered']]
   window.append({'stage':stage,'ticks':sorted({x['tick']for x in cs}),'candidate_reading_sites':len(cs),'valid_native_readings':len(valid),'classes':[x['relation']for x in valid],'raw_evidence':[{'tick':x['tick'],'raw':x['physical']['raw'],'clock':x['physical']['clock'],'direction':x['physical']['direction'],'s_reg':x['physical']['s_reg']}for x in valid]})
  row['native_comparison_windows']=window
  social=m.get('spatial_social_captures',m.get('social_captures',m.get('social_captures_after_fork',m.get('social_captures_after_restore',[]))))
  queries=[x for x in social if x['phase']=='FORM_QUERY'];valid=[x for x in queries if x['covered']]
  row['receiver_query_window']={'candidate_reading_sites':len(queries),'query_receipts_applied':sum(x.get('request_applied',False)for x in queries),'valid_native_readings':len(valid),'classes':[x['relation']for x in valid],'readouts':[{'tick':x['tick'],'receiver':x['receiver'],'raw':x['physical']['raw'],'clock':x['physical']['clock'],'direction':x['physical']['direction'],'s_reg':x['physical']['s_reg'],'request_applied':x.get('request_applied')}for x in valid]}if queries else None
  row['consequence_records']=[{'tick':x['tick'],'receiver':x['receiver'],'context_candidate':x.get('context_candidate'),'raw':x['physical']['raw'],'clock':x['physical']['clock'],'site':x['physical']['site'],'direction':x['physical']['direction'],'s_reg':x['physical']['s_reg']}for x in social if x['phase']=='DELIVERY'and x['physical']['active']]
  contact=m.get('contact_social_observations',m.get('contact_social_observations_after_fork',m.get('contact_social_observations_after_restore',[])))
  cq=[x for x in contact if x['phase']=='QUERY']
  row['contact_receiver_query554']={'candidate_sites':len(cq),'valid_native_readings':sum(x['covered']for x in cq),'contents':[x['content']for x in cq if x['covered']],'readouts':[{'receiver':x['receiver'],'request_applied':x['request_applied'],'covered':x['covered'],'content':x['content'],'physical':x['physical']}for x in cq]}if cq else None
  row['contact_native_consequences']=[{'tick':x['tick'],'receiver':x['receiver'],'phase':x['phase'],'physical':x['physical']}for x in contact if x['phase']in('USE','DELIVERY')]
  out.append(row)
 return {'schema':'CPC8R.relational_analysis.v1','scope':'Independent calculation layer only; not a participant policy or a universal semantic verdict.','totals':dict(totals),'denominators':'Worlds/controlled branches are units. Candidate reading ports, sensor copies and ticks are not independent samples. Technical restorations are not scientific replicas.','formulas':{'valid_native_readings':'sum(capture.covered) over the frozen window, with first and later windows reported separately','requests_new':'All explicit requests of a fresh preparation;0 in inherited diagnostic/technical branches with no new inputs','class_zero_vs_absence':'Empty class list is0valid decoded responses, never a numeric answer0','scientific_counts':'Prepared Runtime worlds are counted once; failed beforecreate attempt does not add a preparation.'},'cases':out}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,default=ROOT/'resultados/semantica/ANALYSIS.json');a=p.parse_args();r=analyze(a.root);a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(r['totals']))
