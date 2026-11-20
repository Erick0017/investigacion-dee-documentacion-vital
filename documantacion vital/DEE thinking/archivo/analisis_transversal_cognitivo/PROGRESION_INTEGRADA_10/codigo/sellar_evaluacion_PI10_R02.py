"""Root-controlled R02 seal after actual closed five-case sensor metrology.

This reads fixed archived RAW/receipts/files, never executes DEE. Native q1
NULL remains a failure even under forced Query; no reader is broadened.
Only an explicit Root decision authorizes the later separate evaluation.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json
H=Path(__file__).resolve().parent;P=H.parent
CALSHA='60f92c8078179acfa9ac4e3a4862ac2a0d2b182c30cf7e721a1793cb25de0e67'
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(b):return hashlib.sha256(b).hexdigest()

def metrology(index):
    spec=importlib.util.spec_from_file_location('audit',H/'recalcular_primarios_PI10_R03.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    v=m.bundle(index);need(v['protocol_sha256']==CALSHA,'Exact R02 calibration protocol')
    rows=sorted(v['rows'],key=lambda r:r['ordinal']);need(len(rows)==5 and [r['ordinal']for r in rows]==list(range(5)),'All five actual metrology cases; no selected successful subset')
    need(len({r['life_id']for r in rows})==1 and all(r['calibration']and r['arm']=='real'and r['q1_actual_motor']==1 for r in rows),'One explicitly forced-all-Query diagnostic life, never candidate learning')
    indexvalue=json.loads(index.read_bytes());protocol=json.loads(m.safe_file(index.parent,indexvalue['protocol']['file']).read_bytes())
    need([r['cue']for r in protocol['calibration_schedule']]==['threat','falsecue','threat','none','falsecue'],'Same five-case diagnostic exposes original fifth-X failure')
    observed=[]
    for entry in indexvalue['episodes']:
        witness=json.loads(m.safe_file(index.parent,entry['witness']['file']).read_bytes());o=witness['first_stage']['sample_register']['actual_preview_observation'];observed.append((witness['ordinal'],m.raw_observation(o)))
    observed=dict(observed)
    # Actual source axes, not the scheduled cue label or a desired response.
    for ordinal,direction in((1,[1,0,0]),(2,[0,0,1]),(4,[1,0,0])):
        d=observed[ordinal];need(d['state']>0 and d['semantic']==1 and d['direction']==direction,'Source-axis metrology did not form its recorded X/Z/fifth-X condition')
    need(all(r['query_applied']and r['query_released']and r['FI_choice_old_q6']==1 and r['Q2_stable']and r['q2_before']==-1 and r['q2_after']==-1 and r['physical_delivered']for r in rows),'The physical question, fixed q2/FI work and actual resource transfer must operate in every metrology case')
    need(all(r['Native_rejected']==0 for r in rows),'Preserve a rejected metrology, do not silently approve it')
    # Absence of an offered cue is not forcibly relabeled as empty RAW.
    return {'life_id':rows[0]['life_id'],'complete_cases':5,'actual_preview_axes':{str(k):{'RAW':str(o['raw']),'state':o['state'],'semantic':o['semantic'],'direction':o['direction']}for k,o in observed.items()},
      'q1_Native_choices':[r['q1_Native_choice']for r in rows],'Native_q1_NULL_count':sum(r['q1_Native_choice']is None for r in rows),
      'physical_resources':sum(r['physical_delivered']for r in rows),'attributed_resources':sum(r['attributed_useful']for r in rows),
      'all_FI_plus':True,'q2_delta_minus1_unchanged':True,'fifth_X_axis_really_observed':True,
      'scope':'Actual forced calibration only. SourceNone may retain activity; it is reported, not overwritten. Native NULLs are neither chosen NoQuery nor learned success.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--decision-root',type=Path,required=True);parser.add_argument('--calibracion-indice',type=Path,required=True);args=parser.parse_args()
    db=args.decision_root.read_bytes();d=json.loads(db)
    need(d.get('schema')=='DEE.PI10.Root_calibration_decision.R02'and d.get('calibration_accepted')is True and d.get('evaluation_authorized')is True,'Explicit Root causal calibration decision and evaluation authorization')
    need(d.get('protocol_calibration_sha256')==CALSHA and d.get('scientific_schedule_and_criteria_unchanged')is True,'No silently changed calibration, reserve or adoption criteria')
    need(d.get('calibration_primary_index_sha256')==sha(args.calibracion_indice.read_bytes()),'Root decision must bind the exact closed actual metrology index')
    out=H/'PROTOCOLO_PI10_R02.json';b=out.read_bytes();need(sha(b)==CALSHA,'Unexpected current protocol, do not overwrite a newer cut');p=json.loads(b)
    need(p['status']=='SEALED_FOR_CALIBRATION','Keep the actual calibration cut')
    for name,digest in p['sources_sha256'].items():need(sha((H/name).read_bytes())==digest,'Pinned physical actor/helper/codec changed')
    actual=metrology(args.calibracion_indice)
    saved=P/'fuentes'/'PROTOCOLO_PI10_R02_SELLADO_CALIBRACION.json';need(not saved.exists(),'Never replace a calibration original');saved.write_bytes(b)
    p['status']='SEALED_FOR_EVALUATION';p['evaluation_sealed_utc']=datetime.now(timezone.utc).isoformat()
    p['evaluation_root_decision']={'file':str(args.decision_root.absolute()),'sha256':sha(db),'calibration_protocol_sha256':CALSHA}
    p['evaluation_actual_metrology']={'closed_primary_index_sha256':sha(args.calibracion_indice.read_bytes()),'actual':actual}
    p['not_a_seal']='Separate12-case evaluation authorized after recorded forced metrology. No reserve result, adaptive capacity, general autonomy or adoption has been inferred from calibration.'
    out.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps({'protocol':str(out),'sha256':sha(out.read_bytes()),'status':p['status'],'calibration_preserved':str(saved),'Native_executed':False}))
if __name__=='__main__':main()
