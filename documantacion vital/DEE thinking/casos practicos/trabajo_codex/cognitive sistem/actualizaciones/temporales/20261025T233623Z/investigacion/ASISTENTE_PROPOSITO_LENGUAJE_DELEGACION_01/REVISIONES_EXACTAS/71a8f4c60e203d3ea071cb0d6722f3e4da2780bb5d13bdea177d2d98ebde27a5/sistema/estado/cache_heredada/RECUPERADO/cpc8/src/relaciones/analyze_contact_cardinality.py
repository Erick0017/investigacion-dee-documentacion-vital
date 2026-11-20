"""Recalculate only instrumental contact-unit observables from exact primaries."""
import argparse,hashlib,json,os
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def put(path,obj):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+'.pending');temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,path)

def main():
 rows=[];snapshots=[]
 for folder in('contact_cardinality','contact_cardinality_f2','contact_cardinality_f3'):
  for path in sorted((ROOT/'resultados/semantica'/folder).glob('*/MEASUREMENTS.json')):
   m=json.loads(path.read_text(encoding='utf8'));case=m['case'];delay=case.get('delay',0)
   row={'case_id':case['id'],'primary':path.relative_to(ROOT).as_posix(),'primary_sha256':sha(path),'preparations':m['preparations'],'status':m['status'],'case':case,'source_sha256':m['source_sha256'],'observed_contact_branches5':[], 'queries':[]}
   if m['status']!='MEASURED':
    row.update(error=m.get('error'),error_type=m.get('error_type'));rows.append(row);continue
   bytick={x['tick']:x for x in m['frames']}
   for name,b in bytick[5+delay]['branches'].items():
    o=b['base'];sign=m['geometry']['branches'][name]['sign']
    row['observed_contact_branches5'].append({'branch':name,'reading':o,'contact_consequence_observed':o['active'] and o['semantic']==1 and o['direction']==[sign,1,0]})
   observed_contacts=sum(x['contact_consequence_observed']for x in row['observed_contact_branches5'])
   row['observed_contact_count5']=observed_contacts
   row['dose_calibration_satisfied']=case.get('unit_load',1)==1 and case.get('actor_load',0)==0
   for index,(tick,fixed_dose)in enumerate(((10+delay,5),(77+delay,12),(144+delay,19))):
    o=bytick[tick]['collector'];value=o['s_reg']-fixed_dose if o['active'] and o['semantic']==1 else None
    row['queries'].append({'tick':tick,'exact':o,'fixed_observer_material_dose':fixed_dose,'affine_unit_estimate':value,
      'within_frozen_0_1_2_reading':value in(0,1,2),'equals_measured_contact_units':value==observed_contacts,
      'interpretation':'INSTRUMENTAL_COUNT_OF_NORMALIZED_UNITS_NOT_SEMANTIC_EMISSION'})
   row['other_experience_response170']=bytick[170+delay]['extra']
   row['receipt_statuses']=dict(Counter(x['receipt']['status']for x in m['requests']))
   row['material_resources']=m['geometry']['resources']
   row['snapshots_byte_hashes_verified']=True
   for s in m['snapshots']:
    p=path.parent/s['path'];ok=sha(p)==s['sha256'];snapshots.append({'case_id':case['id'],'path':p.relative_to(ROOT).as_posix(),'verified':ok})
    row['snapshots_byte_hashes_verified']&=ok
   rows.append(row)
 f3={r['case_id']:r for r in rows if r['case_id'].startswith('CARD_F4')or r['case_id'].startswith('CARD_F5')}
 contrasts={}
 for a,b in [('CARD_F44_NONE','CARD_F45_OFFPATH_NONE'),('CARD_F43_AB','CARD_F46_OFFPATH_AB')]:
  contrasts[a+'_vs_'+b]={'left':a,'right':b,'same_material_doses':True,'same_input_count':True,'difference':'Only prepared zero-load normalization routes are translated12Y; this is a fixed regulation intervention, not an acquired policy.',
    'reads_left':[x['exact']for x in f3[a]['queries']],'reads_right':[x['exact']for x in f3[b]['queries']]}
 out={'schema':'CPC8R.contact_cardinality.analysis.v1','layers':{'data':'Exact fields copied from frozen primaries','calculation':'Estimate=s_reg-(5,12,19) only where active semantic1; fixed offset follows declared physical cue/probe doses, never writes into a world. Ground-truth contact is the measured branch consequence5, not a hidden class sent to Runtime.','reading':'Human provisional interpretation below, not an automated semantic verdict.'},
      'counts':{'primary_records':len(rows),'physical_preparations':sum(r['preparations']for r in rows),'preCreate_rejections':sum(r['status']!='MEASURED'for r in rows),'snapshots':len(snapshots),'snapshot_hash_failures':sum(not s['verified']for s in snapshots)},
      'cases':rows,'causal_contrasts':contrasts,'snapshot_checks':snapshots,
      'technical_reobservations':{'invalid_index_v1':'resultados/tecnicas/CARD_T01_NONE_TRACE.json contains empty active lists due a mistaken flattening index. Preserved, not a physical silence result.','corrected_index_v2':'resultados/tecnicas/CARD_T02_NONE_TRACE_FIXED_INDEX.json validates raw_copy index against each exact native observe; same parent10, not another preparation.','reproducibility_not_replication':True},
      'provisional_reading':{
       'capacity':'A/B individual contacts and their joint occurrence natively contribute1/1/2 unit matter to a common carrier; two later fixed queries preserve the1/2 distinction after a separate paired exposure100. Candidate count depends on normalization of physical doses.',
       'zero_limit':'With two branch normalizers, none gives an explicit active zero-direction record of load12 at77; that zero-direction record does not persist to144. The latter probe-only7 is NOT reinterpreted as a retained calibrated zero; its affine estimate is invalid.',
       'history_limit':'This apparatus acquires physical contact outcomes, but no arbitrary form is taught to denote ONE or TWO, no new referent-counting rule is learned, and no semantic category query is implemented. ONE/TWO remain unestablished semantic entries, with executed supporting mechanism.',
       'dose_counterexample':'A single actor with load3 contributes extra material: one contact reads4 normalized units. Therefore accumulated s_reg is not cardinality independent of object/actor dose.',
       'causal_revision':'Original and one lower normalizer worlds permit unactivated media to recur and contaminate none. Two pre-fusion branch rays prevent that bypass. This fixed prepared regulation is not attention learned by consequences.',
       'budget_stop':'One architecture family, two justified causal revisions; no further geometry or decoder fitting. One-tick timing reserve rejected before Runtime because initial opportunity sites coincide, so it is not a negative DEE capability result.'}}
 out['supervised_costs']=[]
 for name in('card_unit_first_01','card_unit_f2_01','card_unit_f3_01','card_unit_trace_01','card_unit_trace_v2_01','card_unit_restore_01'):
  p=ROOT/'jobs'/name/'COMMAND.json'
  if p.exists():
   j=json.loads(p.read_text(encoding='utf8'));out['supervised_costs'].append({'job':name,'source':p.relative_to(ROOT).as_posix(),'source_sha256':sha(p),**{k:j.get(k)for k in('started_utc','finished_utc','status','exit_code','elapsed_seconds','peak_job_memory_bytes','peak_process_memory_bytes','owned_worker_waited','owned_job_closed')}})
 restore=ROOT/'resultados/tecnicas/CARD_T03_RESTORE.json'
 if restore.exists():
  out['technical_restore']={'primary':restore.relative_to(ROOT).as_posix(),'sha256':sha(restore),**json.loads(restore.read_text(encoding='utf8'))}
 out['unexecuted_plan_entries']=[]
 present={r['case_id']for r in rows}
 for name in('CONTACT_CARDINALITY_FROZEN.json','CONTACT_CARDINALITY_F2_FROZEN.json','CONTACT_CARDINALITY_F3_FROZEN.json'):
  cfg=json.loads((ROOT/'configuraciones/semantica'/name).read_text(encoding='utf8'))
  for case in cfg['cases']:
   if case['id']not in present:
    out['unexecuted_plan_entries'].append({'case_id':case['id'],'configuration':name,'state':'NO_EJECUTADO_TRAS_RECHAZO_PREPARACION_EN_BATCH','explanation':'The original sequential batch stopped at its one-tick initial collision; the actor-dose challenge was subsequently executed in F2/F3, not relabelled as the original V1 case.'})
 put(ROOT/'resultados/semantica/CONTACT_CARDINALITY_ANALYSIS.json',out)
 print(json.dumps(out['counts']))

if __name__=='__main__':main()
