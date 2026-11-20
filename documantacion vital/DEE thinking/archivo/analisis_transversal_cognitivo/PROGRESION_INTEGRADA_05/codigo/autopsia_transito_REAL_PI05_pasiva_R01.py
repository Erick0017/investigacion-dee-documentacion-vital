"""Closed PI05 REAL capture autopsy; exact records, no Native or lineage labels."""
from pathlib import Path
import gzip,hashlib,json,math,runpy

HERE=Path(__file__).resolve().parent;P5=HERE.parent;R=P5.parents[2]
OUT=P5/'control'/'AUTOPSIA_TRANSITO_REAL_GLOBAL_R01.json'
TARGET=[19,53,25];T=817884
KERNEL=R/'4.5'/'DEE_thinking_4_5_0'/'source'/'src'/'kernel_v27.cpp'
KERNEL_SHA='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'

def info(p):
    b=Path(p).read_bytes();return {'path':str(Path(p).resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def main():
    if OUT.exists():raise FileExistsError('No overwrite of scientific proof')
    proof=P5/'control'/'PI05_REAL_FI_GLOBAL_R01.json';closed=json.loads(proof.read_text(encoding='utf-8'))
    assert closed['owner_closed_coherently'] is True
    capture=Path(closed['capture_budget_after']['directories'][0]['path'])
    assert closed['capture_budget_after']['directories'][0]['closed_index'] is True
    source=KERNEL.read_bytes();assert hashlib.sha256(source).hexdigest()==KERNEL_SHA
    m=runpy.run_path(str(HERE/'analizar_influencia_global_PI05_R01.py'),run_name='pure_PI05_closed_autopsy')
    summary=P5/'control'/'INVENTARIO_REAL_FI_GLOBAL_R01'/'RESUMEN_GLOBAL.json'
    inv=json.loads(summary.read_text(encoding='utf-8'));events=inv['actual_requests']['events']
    wanted={817876,817878,817879,817880,817881,817882,817883,817884,817885,817886,817897,817933,817935,817936,817938}
    frames={f['tick']:f for f in m['frame_iterator'](capture)if f['tick']in wanted}
    def at(t,p):
        f=frames[t];i=m['index'](p);return {'tick':t,'site':p,'clock':str(f['clocks'][i]),**m['record'](f['raw'][i])}
    before=frames[T];offsets=[(x,y,z)for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)if(x,y,z)!=(0,0,0)]
    neighbours=[at(T,[(TARGET[i]+d[i])%67 for i in range(3)])for d in offsets]
    alive=[v for v in neighbours if v['state']>0 and v['semantic']!=5]
    patterns=[[(1,0,0),(0,1,0),(0,0,1),(1,1,1)],[(-1,0,0),(0,1,0),(0,0,1),(-1,1,1)],[(1,0,0),(0,-1,0),(0,0,1),(1,-1,1)],[(1,0,0),(0,1,0),(0,0,-1),(1,1,-1)],[(-1,0,0),(0,-1,0),(0,0,1),(-1,-1,1)],[(-1,0,0),(0,1,0),(0,0,-1),(-1,1,-1)],[(1,0,0),(0,-1,0),(0,0,-1),(1,-1,-1)],[(-1,0,0),(0,-1,0),(0,0,-1),(-1,-1,-1)]]
    alive_sites={tuple(v['site'])for v in alive}
    tetra=[i for i,pattern in enumerate(patterns)if all(tuple((TARGET[j]+v[j])%67 for j in range(3))in alive_sites for v in pattern)]
    tension=16.0 if tetra and len(alive)<7 else 2.5
    predicted_rule=math.floor(len(alive)*tension/26.0+0.5)
    incoming=[v for v in neighbours if any(v['direction'])and all((v['site'][i]+v['direction'][i])%67==TARGET[i]for i in range(3))]
    assert at(T,TARGET)['state']>0 and not tetra and len(alive)==4 and predicted_rule==0
    assert at(T+1,TARGET)['raw']=='0'
    observed=[];z_candidates=[];charge17=[]
    with gzip.open(summary.parent/'RAW_NO_NULO_GLOBAL.jsonl.gz','rt',encoding='utf-8')as f:
        for line in f:
            row=json.loads(line);tick=row['tick'];records=row['nonzero_RAW_records']
            matching=[r for r in records if r['s_reg']==17]
            charge17.append({'tick':tick,'records':matching})
            z=(17+tick-817876)%67
            candidates=[r for r in records if r['site']==[19,53,z]and r['state']==1 and r['s_reg']==0 and r['semantic']==1 and r['direction']==[0,0,1]]
            z_candidates.append({'tick':tick,'predicted_site_from_first_frozen_record_not_identity':[19,53,z],'exact_field_match':len(candidates)==1,'records':candidates})
    for tick,p in [(817878,[14,46,20]),(817879,[15,47,21]),(817880,[15,48,21]),(817881,[15,49,21]),(817882,[16,50,22]),(817883,[17,51,23]),(817884,[18,52,24]),(817885,TARGET),(817897,[29,65,35]),(817897,[62,36,1]),(817933,[12,17,18]),(817935,[14,15,16]),(817936,[15,15,15]),(817938,[13,17,13])]:observed.append(at(tick,p))
    old_source=P5.parent/'PROGRESION_INTEGRADA_03'/'ensayos'/'PI03_MAIN_OP3_PANEL_FIplus.json'
    result={'schema':'DEE.PI05.closed_REAL.global_transit_autopsy.R01','modality':'PASSIVE_RECALCULATION_OF_CLOSED_NATIVE_RECORDS','new_Native_ticks':0,'source_proof':info(proof),'inventory':info(summary),'capture_index':info(capture/'INDEX.json'),'analyzer':info(HERE/'analizar_influencia_global_PI05_R01.py'),'autopsy_code':info(Path(__file__)),'frozen_kernel_source':info(KERNEL),'historical_positive_primary':info(old_source),
      'Native_admissions':{'unique':inv['actual_requests']['unique_requests'],'status_counts':inv['actual_requests']['statuses'],'events_at_critical_update_start':list(e for e in events if e['tick']==T),'exact_public_operands':[14,3],'fixed_codec_right_payload':17,'charge_is_not_identity':True},
      'observations':observed,'critical_boundary':{'before_target':at(T,TARGET),'after_target':at(T+1,TARGET),'full_Moore26_before':neighbours,'alive_neighbour_count':len(alive),'pointing_neighbours_before':incoming,'pointing_neighbour_count':len(incoming),'tetrahedron_pattern_hits':tetra,'source_branch':'kernel_v27.cpp:244-251 SEM_OBSERVER bypass;301-339 empty-only demux;346-352 matter rule','external_local_rule_recalculation':{'self_state':at(T,TARGET)['state'],'selected_branch':'MATTER because state>0, SEM1','TENSION_ELECTROWEAK':2.5,'n_active':len(alive),'DMOORE':26,'formula':'floor(n_active*T_local/26+0.5)','predicted_rule_value':predicted_rule,'predicted_RAW':'0','observed_RAW':'0','match':True,'not_a_new_Runtime_execution':True}},
      'global_charge17_field_matches':charge17,'zero_Z_exact_field_translation_candidates':z_candidates,'zero_Z_translation_all_observed_frames_match':all(v['exact_field_match']for v in z_candidates),
      'bounds':{'last_observed_nominal_incoming_charge17':817884,'first_nominal_parent_disagreement':817885,'first_simple_right_node_correct':817879,'right_parent_at817885':'RAW0, not material zero','right_root_at817897':'state1, s_reg0, SEM1, direction(0,+1,0)','C_at817933':14,'S_at817935':14,'early_q4_and_fixed_q6':'material -1, not NULL, not a charge0 response','global_max_sreg_observed':max(f['max_s_reg']for f in inv['frames']),'fusion_threshold_branch_excluded_on_each_next_single_step_by_observed_max':all(f['max_s_reg']<=19663 for f in inv['frames'])},
      'scientific_interpretation':{'established':'Legal admissions formed the first right aggregate. Before the next nominal merge, a pre-existing active zero-charge +Z configuration occupies its destination. The exact local frozen-kernel matter rule predicts the observed empty destination despite four incoming directed records. Global records bound the first nominal loss before C, rather than only recording C=14.','causal_inference_limit':'One history only: no intervention has yet isolated that zero-charge configuration. A matching charge, field pattern or toroidal translation is not a Native lineage label. No destruction/global memory loss or unique origin is certified. b2/b3/b4 and controlled blocker/sham evidence are still pending.','historical_positive_limit':'Old positive primary records C/S=31 under a different whole physical history; no old continuous global capture is available in this proof, so earlier-route equality with the positive past is not claimed.','downstream_reader':'The early and fixed readers coherently expose the wrong comparison after C/S=14; no decoder was changed.','actor_receives_this_analysis':False}}
    with OUT.open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':str(OUT),'bytes':OUT.stat().st_size,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'critical_tick':T,'neighbours':len(alive),'rule':predicted_rule,'zeroZ_all_observed':result['zero_Z_translation_all_observed_frames_match']}))

if __name__=='__main__':main()
