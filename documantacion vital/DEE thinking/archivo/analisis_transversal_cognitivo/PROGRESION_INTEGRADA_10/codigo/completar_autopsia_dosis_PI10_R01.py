"""Supplement a stopped bundle with a hashed frozen-snapshot autopsy, no DEE."""
from pathlib import Path
import argparse,hashlib,importlib.util,json
H=Path(__file__).resolve().parent
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--indice',type=Path,required=True);p.add_argument('--autopsia',type=Path,required=True);a=p.parse_args()
    b=a.autopsia.read_bytes();v=json.loads(b);need(v['schema']=='DEE.PI10.frozen_preview_failure_autopsy.R01','Exact frozen-state diagnostic')
    spec=importlib.util.spec_from_file_location('audit',H/'recalcular_primarios_PI10_R02.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    rec=m.bundle(a.indice);rows=rec['rows'];ids={int(k):s for r in rows for k,s in r['receipt_id_status'].items()}
    preview=m.raw_observation(v['preview']);need(preview['raw']!=0 and m.extra_bit(v['preview'])is None,'Existing active RAW outside original fixed bit codec, not absent material')
    need(v['snapshot']['pending_Native']==0,'No unaccounted Native future input in the parsed frozen snapshot')
    previous=max(ids);latest=v['snapshot']['receipt_count'];new=[r for r in v['recent_actual_Native_receipts']if r['id']>previous]
    need(latest==previous+1 and len(new)==1 and new[0]['id']==latest,'Exactly one new Native receipt after the whole completed prefix')
    request=new[0];need(request['status_from_matching_prior_closed_receipt']=='applied'and v['status_enum_matching_prior_witness'][str(request['status_enum'])]=='applied','Status enum anchored by an existing matching own terminal receipt')
    need(request['channels']==['PI10.device.actual_plusX.R01']and request['requested_tick']==request['effective_tick']==preview['tick']-1,'Only actual cueX birth before aborted q1')
    progress=v['PI10_progress'];need(progress['ordinal']==len(rows)and progress['uncertain']is True and progress['pending']['ordinal']==len(rows),'Keep the actor interrupted phase, not a silently cleared ordinal')
    outdir=a.indice.parent/'FALLO';need(outdir.is_dir(),'Preserve the exact failed primary first')
    target=outdir/'AUTOPSIA_SNAPSHOT_ORIGINAL.json';need(not target.exists(),'No replacement of an earlier autopsy')
    with target.open('xb')as f:f.write(b)
    need(target.read_bytes()==b and a.autopsia.read_bytes()==b,'Exact original autopsy copy and unchanged source')
    result={'schema':'DEE.PI10.stopped_exact_dose_supplement.R01','Native_executed':False,'DEE_imported':False,
      'autopsy_source':{'file':str(a.autopsia.absolute()),'bytes':len(b),'sha256':sha(b),'exported_member':'FALLO/AUTOPSIA_SNAPSHOT_ORIGINAL.json'},
      'failure_preview':preview,'failure_class':'Nonempty active SEM1 diagonal(+X,+Z) outside original axis-only codec. No q1 reader, resource offer or FI work was reached in this attempted opportunity.',
      'Native_dose_completed':len(ids),'Native_dose_failed_attempt':1,'Native_dose_total':len(ids)+1,'Native_applied_total':sum(s=='applied'for s in ids.values())+1,
      'Native_rejected_total':sum(s!='applied'for s in ids.values()),'exact_new_request':request,
      'Native_pending':0,'actor_PI10_pending_preserved':progress['pending'],'actor_PI10_uncertain_preserved':progress['uncertain'],
      'snapshot_sha256':v['snapshot']['sha256'],'q1_A_minus_B':m.raw_observation(v['q1_A'])['s_reg']-m.raw_observation(v['q1_B'])['s_reg'],
      'q2_A_minus_B':m.raw_observation(v['q2_A'])['s_reg']-m.raw_observation(v['q2_B'])['s_reg'],
      'qualification':'Enum interpretation is explicitly anchored by the source autopsy to a matching earlier closed receipt. One final snapshot cannot establish a unique ancestry of the diagonal or the additional+Z carrier. Pipeline pending is distinct from outstanding Native entries or unknown external execution.'}
    out=outdir/'AUTOPSIA_Y_DOSIS_COMPLETADAS.json';need(not out.exists(),'No overwriting earlier supplement')
    with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'file':str(out),'sha256':sha(out.read_bytes()),'Native_total':result['Native_dose_total'],'Native_executed':False}))
if __name__=='__main__':main()
