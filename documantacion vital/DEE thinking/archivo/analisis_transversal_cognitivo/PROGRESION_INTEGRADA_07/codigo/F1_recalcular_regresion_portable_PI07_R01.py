"""Audit included panel/primary/RAW features only; never follow original paths."""
from pathlib import Path
import argparse,hashlib,json


def require(value,message):
    if not value:raise ValueError(message)


def decode(row):
    value=int(row.get('RAW',row.get('raw')));ds=[(value>>s)&15 for s in(48,52,56)]
    fields={'state':value&0xffffffff,'s_reg':(value>>32)&65535,'semantic':value>>60,
            'direction':[v-16 if v&8 else v for v in ds]}
    require(all(row[k]==v for k,v in fields.items()),'RAW field mismatch')
    return fields


def recalculate(evidence_bytes,primary_bytes,panel_bytes):
    e=json.loads(evidence_bytes);d=json.loads(primary_bytes);panel=json.loads(panel_bytes)
    require(e['schema']=='DEE.PI07.F1.closed_panel_FIplus_regression.passive_recalculation.v1','Wrong evidence family')
    # Original absolute paths are provenance strings. Only their final names and
    # digests are compared; they are never opened, resolved or executed.
    recorded={r['file'].replace('\\','/').rsplit('/',1)[-1]:r['sha256']for r in e['sources']}
    require(hashlib.sha256(primary_bytes).hexdigest()==recorded['PI07_PANEL_INTERCALADO_R01_FIplus.json'],'Included primary differs')
    require(hashlib.sha256(panel_bytes).hexdigest()==recorded['PI07_PANEL_INTERCALADO_R01.json'],'Included panel differs')
    outer=json.loads(d['result'])if isinstance(d['result'],str)else d['result'];row=outer['result']['rows'][0]
    t=row['original_result']['native_trial'];receipts=row['all_material_receipts']
    ids=[r['id']for r in receipts]
    require(len(ids)==len(set(ids))==176 and ids==e['FI']['Native_receipt_ids'],'Actual direct receipt IDs differ')
    require(all(r['receipt']['status']=='applied'for r in receipts),'A direct request was not applied')
    require(outer['before_tick']==856200 and outer['after_tick']==856398,'Actual trial cut differs')
    require(row['query_tick']==856256 and row['early_tick']==856260,'Fixed query/read calendar differs')
    require(row['early_physical_choice']==row['old_q6_choice']==-1,'Actual Native result differs')
    require(row['early_observation']==e['FI']['early_observation'],'Early RAW evidence differs')
    require(decode(row['early_observation'])['direction'][0]==-1,'Negative choice not formed in RAW')
    for obs in t['reader']['observations']:decode(obs)
    require(t['reader']['choice']==-1,'Frozen six-site reader differs')
    c=t['frames'][0]['fields']['C'];s=t['frames'][2]['fields']['S'];decode(c);decode(s)
    require(c['s_reg']==s['s_reg']==17 and c==e['FI']['observed_C']and s==e['FI']['observed_S'],'Recorded local tree values differ')
    for phase in('references_pre','references_after'):
        refs=t[phase]
        for r in refs:decode(r)
        require(refs[0]['s_reg']-refs[1]['s_reg']==-20,'Reference difference changed')
    require(panel['closed']is True and panel['status']=='STOPPED_PRESERVED','Panel status differs')
    require(panel['correct']==5 and panel['tested']==6 and panel['new_Native_ticks']==497,'Panel coverage differs')
    require(panel['Native_inputs']=={'unique_requested':211,'applied':211,'rejected_or_other':0},'Panel dose differs')
    features=e['closed_snapshots'];positions={}
    for name,view in features.items():
        rows=view['all_RAW_nonzero_in_fixed_row_x52_y48']
        for r in rows:
            fields=decode(r);require(fields=={'state':1,'s_reg':0,'semantic':1,'direction':[0,0,1]},'Snapshot row signature differs')
            require(r['site'][:2]==[52,48],'Fixed feature row differs')
        positions[name]=sorted(r['site'][2]for r in rows)
    shifts=[]
    for a,b in(('source_R03','before_FI'),('before_FI','after_FI')):
        dt=features[b]['physical']['tick']-features[a]['physical']['tick']
        require(sorted((z+dt)%67 for z in positions[a])==positions[b],'Endpoint translation differs')
        shifts.append({'from':a,'to':b,'ticks':dt,'endpoint_set_match':True,'path_between_endpoints_observed':False})
    trace=e['last_existing_R03_capture']['frames'];require(len(trace)==31,'31 included feature frames required')
    for frame in trace:
        for r in frame['fixed_row_RAW_nonzero']:decode(r)
    require(features['before_FI']['physical']['tick']==856200,'Projection source differs')
    parent_tick=row['query_tick']-48;dt=parent_tick-856200
    require(dt==8 and [z for z in positions['before_FI']if(z+dt)%67==58]==[50],'Conditional phase projection differs')
    return{'schema':'DEE.PI07.F1.panel_regression.included_features_recalculation.v1',
      'Native_executed':False,'DEE_imports':False,'new_Native_ticks':0,
      'recorded_absolute_source_locators_opened':0,'only_explicit_CLI_input_files_opened':True,
      'evidence_sha256':hashlib.sha256(evidence_bytes).hexdigest(),'primary_sha256':hashlib.sha256(primary_bytes).hexdigest(),
      'panel_sha256':hashlib.sha256(panel_bytes).hexdigest(),'actual_panel_correct_tested':[5,6],
      'actual_trial_receipts_unique_applied':176,'FI_material_choice_q4_q6':[-1,-1],
      'material_minus_one_is_not_NULL':True,'MU_reference_difference_preserved':-20,
      'recorded_C_S':[17,17],'fixed_snapshot_row_positions':positions,'endpoint_translation':shifts,
      'recorded_trace_feature_frames':31,'conditional_parent_projection':{'site':[52,48,58],'tick':parent_tick,'from_z':50,'advance':dt,'measured_intermediate_frame':False},
      'full_global_buffers_reconstructed_by_this_small_verifier':False,
      'scope':'Actual included primary/receipts/RAW fields and frozen extracted features are recalculated. Snapshot/full-buffer hashes are provenance, not regenerated from these sparse features. This is not a Native replay, measured intermediate encounter, unique lineage, global causal equality, memory-erasure diagnosis or learned repair.'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence',type=Path,required=True)
    ap.add_argument('--primary',type=Path,required=True);ap.add_argument('--panel',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    require(not a.out.exists(),'Output exists')
    result=recalculate(a.evidence.read_bytes(),a.primary.read_bytes(),a.panel.read_bytes())
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'out':str(a.out),'actual_regression_recalculated':True,'Native_ticks':0},ensure_ascii=False))


if __name__=='__main__':main()
