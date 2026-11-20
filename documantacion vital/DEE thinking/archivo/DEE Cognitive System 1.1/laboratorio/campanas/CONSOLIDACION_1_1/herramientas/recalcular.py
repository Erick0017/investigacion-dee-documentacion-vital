"""Engine-free recalculation from primary observations, not cached verdicts.

Run after a trajectory. Nothing in sistema imports this auditor or its outputs.
"""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[4]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def qualified(o,load=None,direction=None):return bool(o['active']and o['semantic']==1 and(load is None or o['s_reg']==load)and(direction is None or o['direction']==direction))
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
def recalcular(root):
    out={'schema':'DCS1.1.primary_recalculation.v1','role':'AUDITOR_AFTER_TRAJECTORY','formulas':{'K65':'sum(active && semantic==1 && observed_direction==frozen_expected_direction) / number_of_unique_forms_in_complete_staggered_window','social':'For every original actualevents, compare the corresponding native branch against the predeclared stage load anddirection; report both load+direction and direction-only counts. No inactive branch becomes a numerical answer.','mobile':'same-history sign; expected_load=65+7*read_index; expected_direction=[0,sign,1]for even read_index else[1,sign,1]','old_two':'sum(active && semantic1 && direction[1,0,0]) / supplied_old_two_queries','memory':'basic_buffers=32*N**3 bytes, not processRAM and not energy'},'sources':[],'K65':[],'late_access':[],'functional':[],'social_causal':[],'mobile':[],'technical_incidents':[]}
    groups=['INTERFERENCIA_R1','FACTORIAL_R2','LECTURA_TARDIA_R1','CONTINUIDAD_FUNCIONAL_R1','CONTINUIDAD_FUNCIONAL_R2','CONTINUIDAD_FUNCIONAL_R3_RESERVAS','MOVIL_SOCIAL_R1']
    files=[p for group in groups for p in(root/'evidencia/telemetria'/group).glob('*/MEDICIONES.json')]
    files+=list((root/'evidencia/controles').glob('*/MEDICIONES.json'))
    for p in sorted(files):
        d=read(p);source={'file':p.relative_to(root).as_posix(),'sha256':sha(p),'schema':d['schema'],'status':d.get('status')};out['sources'].append(source)
        if d.get('status')!='MEASURED':continue
        if d['schema'].startswith('DCS1.1.K65'):
            queries=[q for f in d['frames']for q in f['queries']];computed=[qualified(q['physical'],direction=q['expected_auditor_direction'])for q in queries];windows=[]
            for w in d['staggered_sweeps']:
                rows=[q for q in queries if w['begin_tick']<=q['tick']<=w['end_tick']];n=sum(qualified(q['physical'],direction=q['expected_auditor_direction'])for q in rows);windows.append({**w,'recalculated':n,'unique_forms':len({q['form']for q in rows}),'cached_count_equal':n==w['qualified']})
            out['K65'].append({'case':d['case_id'],'source':source,'start':d['start_physical'],'final':d['final_physical'],'query_count':len(queries),'qualified_recalculated':sum(computed),'all_cached_flags_equal':all(a==b['qualified']for a,b in zip(computed,queries)),'staggered_sweeps':windows,'old_two_queries':len(d.get('old_operand_queries',[])),'old_two_positive_X':sum(qualified(x['physical'],direction=[1,0,0])for x in d.get('old_operand_queries',[])),'receipt_statuses':d['receipt_statuses']})
        elif d['schema'].startswith('DCS1.1.late_access'):
            queries=[q for f in d['frames']for q in f['queries']];rounds=[]
            for i in range(d['case']['rounds']):
                rows=[q for q in queries if q['qindex']==i];rounds.append({'index':i,'n':len(rows),'qualified':sum(qualified(q['physical'],direction=q['expected_auditor_direction'])for q in rows),'ticks':sorted({q['tick']for q in rows})})
            out['late_access'].append({'case':d['case']['id'],'source':source,'rounds':rounds,'initial':d['initial'],'final':d['final'],'old_two_n':sum('old_two_memory'in f for f in d['frames']),'old_two_positive_X':sum(qualified(f['old_two_memory'],direction=[1,0,0])for f in d['frames']if'old_two_memory'in f),'receipt_statuses':d['receipt_statuses'],'limits':'Offpath sham can return through a torus; a nonzero later score is not silently discarded. Zeroquery control has no direct knowledge score.'})
        elif d['schema'].startswith('DCS1.1.functional_continuation'):
            plan_candidates=list((root/'laboratorio/campanas/CONSOLIDACION_1_1').glob('CONTINUIDAD_FUNCIONAL_PLAN*.json'));matches=[x for x in plan_candidates if sha(x)==d['plan_sha256']]
            if len(matches)!=1:raise ValueError('Missing/ambiguous exact frozen plan for '+str(p))
            plan=read(matches[0]);events=d['case'].get('actual_new_form_events',plan['actual_new_form_events']);base=d['case'].get('cue',plan.get('new_cue_load',5))+d['case'].get('teacher',plan.get('new_teacher_load',11));timing=d['bridge_geometry']['roundtrip'];stages=[]
            for stage,tick,load,key in [('A',timing['A_read'],base+7,'A'),('B',timing['B_read'],base+19,'B_hub'),('C',timing['C_read'],base+31,'C_hub'),('use',timing['use'],base+42,'use_site')]:
                frame=next(f for f in d['frames']if f['tick']==tick);rows=[]
                for index,form in enumerate(frame['social']):
                    sign=events[index];ob=form['A']if key=='A'else next(b[key]for b in form['branches']if b['id']==('plus'if sign==1 else'minus'));direction=[1 if stage=='use'else 0,sign,1];rows.append({'form':form['id'],'expected_sign':sign,'observation':ob,'qualified':qualified(ob,load,direction),'direction_only':qualified(ob,direction=direction)})
                stages.append({'stage':stage,'tick':tick,'expected_load':load,'n':len(rows),'qualified':sum(x['qualified']for x in rows),'direction_only':sum(x['direction_only']for x in rows),'rows':rows})
            late=[]
            for index,tick in enumerate(plan.get('late_source_reads',[])):
                f=next(f for f in d['frames']if f['tick']==tick);rows=[qualified(x['A'],base+7*(index+2),[0,events[i],1])for i,x in enumerate(f['social'])];late.append({'tick':tick,'n':len(rows),'qualified':sum(rows)})
            quantities=[{'tick':f['tick'],'center':f['quantity']['center'],'reference_hub':f['quantity']['reference_hub'],'reference_site':f['quantity']['reference_site'],'object_site':f['quantity']['object_site']}for f in d['frames']if'quantity'in f]
            old_count=[{'tick':f['tick'],'rows':len(f['old_count']),'unique_sites':len({tuple(x['physical']['site'])for x in f['old_count']}),'informative_plusX_rows':sum(qualified(x['physical'])and x['physical']['direction'][0]==1 for x in f['old_count'])}for f in d['frames']if'old_count'in f]
            out['functional'].append({'case':d['case']['id'],'life_id':d['life_id'],'source':source,'plan':matches[0].relative_to(root).as_posix(),'plan_sha256':d['plan_sha256'],'new_stages':stages,'late_A':late,'quantity':quantities,'old_two_n':sum('old_two_memory'in f for f in d['frames']),'old_two_positive_X':sum(qualified(f['old_two_memory'],direction=[1,0,0])for f in d['frames']if'old_two_memory'in f),'old_count_observable_rows_not_independent_concepts':old_count,'old_joint_primary':[{'tick':f['tick'],'values':f['old_joint']}for f in d['frames']if'old_joint'in f],'receipt_statuses':d['receipt_statuses'],'final':d['final'],'scope':'Branch from the same1948parent; learned histories are not added across branches.'})
        elif d['schema'].startswith('DCS1.1.mobile_social_access'):
            rounds=[]
            for f in d['frames']:
                if 'forms'not in f:continue
                i=f['read_index'];rows=[]
                for j,form in enumerate(f['forms']):
                    sign=1 if j%2==0 else-1;b=next(x for x in form['branches']if x['id']==('plus'if sign==1 else'minus'));o=b['physical'];rows.append({'form':form['id'],'physical':o,'qualified':qualified(o,65+7*i,[0 if i%2==0 else 1,sign,1]),'has_acquired_Y':qualified(o)and o['direction'][1]==sign})
                rounds.append({'tick':f['tick'],'read_index':i,'qualified':sum(x['qualified']for x in rows)if d['case']['query']else None,'native_informative_Y':sum(x['has_acquired_Y']for x in rows),'n':len(rows),'rows':rows,'modality':'MATERIAL_QUERY'if d['case']['query']else'PASSIVE_CONTROL_NO_QUERY_NO_FUNCTIONAL_SCORE'})
            out['mobile'].append({'case':d['case']['id'],'life_id':d['life_id'],'source':source,'query_was_supplied':d['case']['query'],'rounds':rounds,'old_two_n':sum('old_two_memory'in f for f in d['frames']),'old_two_positive_X':sum(qualified(f['old_two_memory'],direction=[1,0,0])for f in d['frames']if'old_two_memory'in f),'final':d['final'],'receipt_statuses':d['receipt_statuses']})
    cp=root/'evidencia/controles/PUENTE_CAUSAL_R1B/CONTROLES.json'
    if cp.exists():
        data=read(cp);out['sources'].append({'file':cp.relative_to(root).as_posix(),'sha256':sha(cp)})
        for d in data['cases']:
            frame=next(f for f in d['frames']if f['tick']==2189);rows=[]
            for i,f in enumerate(frame['forms']):
                sign=1 if i%2==0 else-1;b=next(b for b in f['branches']if b['id']==('plus'if sign==1 else'minus'));rows.append({'form':f['id'],'qualified':qualified(b['use_site'],58,[1,sign,1]),'physical':b['use_site']})
            out['social_causal'].append({'case':d['case']['id'],'source':cp.relative_to(root).as_posix(),'source_sha256':sha(cp),'parent_unchanged':d['parent_unchanged'],'qualified':sum(x['qualified']for x in rows),'n':len(rows),'rows':rows})
    inherited=root/'evidencia/verificaciones/HERENCIA_01/REGRESION_HEREDADA.json'
    if inherited.exists():
        h=read(inherited);out['heritage']={'source':inherited.relative_to(root).as_posix(),'sha256':sha(inherited),'families':{k:v['status']for k,v in h['family_results'].items()},'counts':dict(Counter(x['status']for x in h['family_results'].values())),'not_E1_knowledge':True}
    for p in(root/'evidencia/verificaciones').glob('PERFILES*/**/RESULTADOS.json'):
        d=read(p);out['technical_incidents'].append({'source':p.relative_to(root).as_posix(),'sha256':sha(p),'status':d['status'],'checks':{k:v['passed']for k,v in d.get('checks',{}).items()},'error':d.get('error'),'scope':d.get('coverage','Declared system profile checks')})
    # Common-interface receipts remain primary observations. The audit export
    # carries byte-exact copies, so it can recalculate without an installed motor.
    out['lived_profiles']=[]
    for life in ('R65_45_VIVIDO','R65_REVISION_11','R65_SHAM_11_R2','R65_N67_RESERVA','U0_14_VIVIDO'):
        p=root/'evidencia/telemetria/REGISTROS_OPERATIVOS'/life/'VIDA.json'
        if not p.exists():p=root/'sistema/estado/vidas'/life/'VIDA.json'
        d=read(p);rows=[]
        for i,op in enumerate(d.get('operations',[])):
            if op['kind']!='MATERIAL_QUERY':continue
            result=op['result'];responses=result['responses'];observations=[]
            for x in responses:
                ob=x['physical'];expected=(-1 if (int(x['form'][1:])-1)%3==1 else 1)if x['form'].startswith('L')else(1 if int(x['form'][1:])%2==0 else -1)
                if life=='R65_REVISION_11'and x['form']=='L01':expected=-1
                if life=='U0_14_VIVIDO':expected=None
                # Official value decoder is independently checked from active
                # SEM1 and the learned Y direction, never from a cached flag.
                value=ob['direction'][1]if qualified(ob)and ob['direction'][1]in(-1,1)else None
                observations.append({'form':x['form'],'physical':ob,'decoded_Y':value,'expected_from_declared_experience':expected,'matches_experience':value==expected if expected is not None else None,'cached_decoder_equal':x.get('value',value)==value})
            rows.append({'operation_index':i,'read_tick':result['read_tick'],'n':len(observations),'covered':sum(x['decoded_Y']is not None for x in observations),'matches_experience':sum(x['matches_experience']is True for x in observations),'missing':[x['form']for x in observations if x['decoded_Y']is None],'rows':observations})
        out['lived_profiles'].append({'life':life,'source':p.relative_to(root).as_posix(),'sha256':sha(p),'snapshot_sha256':d['snapshot_sha256'],'queries':rows,'scope':'Actual operational query records, not replayed answers. Independent profiles are not added to E1 knowledge.'})
    out['ontogeny']=[]
    for p in sorted((root/'evidencia/controles/ONTOGENIA_N67_R1').glob('*/MEDICIONES.json')):
        d=read(p);frames=[]
        for f in d['frames']:
            if f['tick']not in(0,31,214,281,348,415,482,549,616,683,750,817,884):continue
            frames.append({'tick':f['tick'],'physical':f['physical'],'body_emission':f['view']['body']['emission'],'contact':f['view']['contact'],'joint':f['view']['joint'],'initiative':f['view']['initiative']})
        out['ontogeny'].append({'case':d['case'],'source':p.relative_to(root).as_posix(),'sha256':sha(p),'initial':d['initial'],'final':d['final'],'frames':frames,'full884reference_equal':d.get('full_884_reference_equal'),'interpretation_limit':'Different history is not automatically a stable successful learner. Dense expansion in opposite/unpaired histories is retained as an adverse result; only measured signatures are reported.'})
    out['microscopic']=[]
    p=root/'evidencia/diagnosticos/EXPANSION_MICRO_R1/MICRO_EXPANSION.json'
    if p.exists():
        d=read(p);out['microscopic'].append({'source':p.relative_to(root).as_posix(),'sha256':sha(p),'exact_reference_frames':len(d['reference_matches']),'all_reference_frames_equal':all(x['full_RAW_clocks_tick_equal']for x in d['reference_matches']),'survival_reception_witnesses':len(d['survival_reception_witnesses']),'first_survival_reception_pre_tick':min(x['pre_tick']for x in d['survival_reception_witnesses']),'XNOR_witnesses':len(d['XNOR_witnesses']),'all_XNOR_local_branches_match':all(x['branch_match']for x in d['XNOR_witnesses']),'first_XNOR_pre_tick':min(x['pre_tick']for x in d['XNOR_witnesses']),'first_above600':next(x['post_tick']for x in d['steps']if x['occupied_post']>600),'scope':d['coverage_limits']})
    p=root/'evidencia/diagnosticos/REVISION_MICRO_R1/MICRO_REVISION.json'
    if p.exists():
        d=read(p);out['microscopic'].append({'source':p.relative_to(root).as_posix(),'sha256':sha(p),'cases':[{'life':x['life'],'full920_replay_equal':x['full920_replay_equal'],'L01_920':next(f['L01']for f in x['frames']if f['tick']==920),'L06_920':next(f['L06']for f in x['frames']if f['tick']==920)}for x in d['cases']],'scope':'Local actual equal-dose offpath control changes L06 too. It is not a globally inert sham.'})
    return out
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path);a=p.parse_args();out=a.out or a.root/'evidencia/informes/CALCULOS_DESDE_PRIMARIOS.json';data=recalcular(a.root.resolve());put(out,data);print(json.dumps({'file':str(out),'primary_sources':len(data['sources']),'K65_cases':len(data['K65']),'functional_cases':len(data['functional']),'mobile_cases':len(data['mobile'])}))
if __name__=='__main__':main()
