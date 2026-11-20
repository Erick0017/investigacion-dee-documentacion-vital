"""Pure recount of fixed PI06 phase primaries; no engine/actor imports."""
from pathlib import Path
import argparse,hashlib,json

P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def checked(path):
    path=Path(path).resolve(strict=True)
    if not path.is_relative_to(P.resolve()):raise ValueError('Only PI06 fixed primary paths')
    for node in(path,*path.parents):
        if node.exists()and(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&0x400):raise ValueError('No reparse source')
    return path
def recount(proof_path):
    path=checked(proof_path);summary=read(path)
    if summary['schema']!='DEE.PI06.fixed_phase_execution.v1'or not summary['closed']:raise ValueError('A closed actual phase is required')
    planpath=checked(summary['plan']);plan=read(planpath)
    if sha(planpath)!=summary['plan_sha256']:raise ValueError('Plan bytes changed')
    rows=[];all_ids={};new_ticks=0
    for i,outcome in enumerate(summary['outcomes']):
        step=plan['steps'][i]
        if outcome['label']!=step['label']:raise ValueError('Literal order changed')
        primary_path=checked(outcome['primary'])
        if sha(primary_path)!=outcome['primary_sha256']:raise ValueError('Primary bytes changed')
        transport=read(primary_path)
        if isinstance(transport.get('result'),str):
            if transport.get('status')!='completed' or transport.get('error')is not None:
                raise ValueError('Only a completed unambiguous current transport result')
            payload=json.loads(transport['payload'])
            if payload.get('situaciones')!=[step['literal']]:raise ValueError('Actual literal differs from sealed plan')
            primary=json.loads(transport['result'])
        else:primary=transport
        actual_rows=primary.get('result',{}).get('rows',[])
        if len(actual_rows)!=1:raise ValueError('One actual phase row required')
        row=actual_rows[0];before=row['before_tick'];after=row['after_tick']
        if before!=primary['before_tick']or after!=primary['after_tick']:raise ValueError('Primary row age differs from transport')
        delta=after-before;new_ticks+=delta
        if not 0<=delta<=step['max_native_ticks']:raise ValueError('Predeclared age cap exceeded')
        literal=step['literal'];entry={'label':step['label'],'literal':literal,'before_tick':before,'after_tick':after,
            'new_ticks':delta,'primary':str(primary_path),'primary_sha256':sha(primary_path)}
        if literal['modo']=='eci01-pi06-fiplus':
            unique={}
            for request in row['requests']:
                rid=request['id']
                if rid in unique and unique[rid]!=request:raise ValueError('Contradictory within-row receipt alias')
                unique[rid]=request
                if rid in all_ids and all_ids[rid]!=request:raise ValueError('Conflicting Native request ID within this life')
                all_ids[rid]=request
            applied=sum(r['receipt']['status']=='applied'for r in unique.values())
            expected=176+int(literal['condicion']!='intacto')
            if len(unique)!=expected or row['Native_inputs']['unique_requested']!=len(unique)or row['Native_inputs']['applied']!=applied:
                raise ValueError('Declared count differs from actual unique receipts')
            q=row['calendar']['query_tick'];observed=row['early_physical_choice'];late=row['old_q6_choice']
            reference=(literal['izquierda']>literal['derecha'])-(literal['izquierda']<literal['derecha'])
            if observed is not None and (type(observed)is not int or observed not in(-1,0,1)):raise ValueError('No valid fixed decoder class')
            if row['calendar']['early_reader_tick']!=q+4 or row['calendar']['old_reader_tick']!=q+6:raise ValueError('Reader offset changed')
            transient=row.get('transient')
            if literal['condicion']!='intacto':
                request=transient['request']
                if request['tick']!=row['calendar']['input_tick']+4 or request['tick']!=q-50:raise ValueError('Transient timing changed')
                if request['declared_state']!=1 or request['declared_semantic']!=1 or request['direction']!=[0,0,1]:raise ValueError('No replacement/support anatomy is allowed')
            elif transient is not None:raise ValueError('Intact condition scheduled an extra transient')
            entry.update({'condition':literal['condicion'],'query_tick':q,'early_reader_tick':q+4,'old_reader_tick':q+6,
                'observed_q4':observed,'observed_q6':late,'reader_has_signature':observed is not None,
                'reference_only_for_posthoc_evaluation':reference,'correct':observed is not None and observed==reference,
                'Native_inputs_unique':len(unique),'Native_inputs_applied':applied,'Native_inputs_rejected_or_other':len(unique)-applied,
                'transient':transient,'capture':row.get('external_global_capture'),
                'NULL_is_not_zero':True})
        else:
            if row.get('new_inputs_scheduled')!=0 or row.get('requests')!=[]:raise ValueError('Evolution must not schedule material repair/input')
            if delta!=literal['ticks']:raise ValueError('Evolution age changed')
            entry['new_inputs_scheduled']=0
        rows.append(entry)
    fi=[r for r in rows if'condition'in r]
    gaps=[fi[i]['query_tick']-fi[i-1]['query_tick']for i in range(1,len(fi))]
    result={'execution_proof':str(path),'execution_proof_sha256':sha(path),'plan':str(planpath),
        'plan_sha256':sha(planpath),'life_id':summary['life_id'],'status':summary['status'],
        'closed':summary['closed'],'initial_tick':summary['initial_tick'],'final_tick':summary['final_tick'],
        'new_ticks_recalculated':new_ticks,'new_ticks_reported':summary['new_ticks'],
        'FI_queries_observed':len(fi),'formed_q4_signatures':sum(r['reader_has_signature']for r in fi),
        'correct_FI_queries':sum(r['correct']for r in fi),'FI_sequence_q4':[r['observed_q4']for r in fi],
        'FI_sequence_q6':[r['observed_q6']for r in fi],'actual_query_tick_gaps':gaps,
        'third_minus_first_query':fi[2]['query_tick']-fi[0]['query_tick']if len(fi)>=3 else None,
        'Native_inputs_unique_in_this_life':len(all_ids),
        'Native_inputs_applied':sum(x['receipt']['status']=='applied'for x in all_ids.values()),
        'rows':rows,'preserved_original_error':summary['error'],
        'common_prefix_is_not_independent_replication':True}
    if new_ticks!=summary['new_ticks']:raise ValueError('Actual operation horizons differ from saved cut')
    return result
def main(a):
    cases=[recount(p)for p in a.casos]
    comparisons=[]
    for i,left in enumerate(cases):
        for right in cases[i+1:]:
            lf=[r for r in left['rows']if'condition'in r];rf=[r for r in right['rows']if'condition'in r]
            comparisons.append({'left':left['life_id'],'right':right['life_id'],
                'same_initial_age':left['initial_tick']==right['initial_tick'],
                'same_final_age':left['final_tick']==right['final_tick'],
                'same_actual_query_ticks':[r['query_tick']for r in lf]==[r['query_tick']for r in rf],
                'same_public_operands':[r['literal'].get('izquierda')for r in lf]==[r['literal'].get('izquierda')for r in rf]and[r['literal'].get('derecha')for r in lf]==[r['literal'].get('derecha')for r in rf],
                'same_material_input_count':left['Native_inputs_unique_in_this_life']==right['Native_inputs_unique_in_this_life'],
                'q4_sequences_equal':left['FI_sequence_q4']==right['FI_sequence_q4'],
                'same_age_not_complete_global_causal_identity':True})
    value={'schema':'DEE.PI06.fixed_phases.documentary_recount.R01','cases':cases,'pairwise_comparisons':comparisons,
        'Native_executed':False,'new_Native_ticks':0,'experiment_reproduced':False,
        'interpretation_limits':['This script verifies existing records and receipt counts; it does not run the engine or prove a unique carrier lineage.',
            'Recovery of a fixed function can reflect age, phase, decay, encounters or previous material queries. It is not automatically learned regulation.',
            'Intact176 and perturb/sham177 differ in dose; only matched material controls isolate position at equal dose.',
            'A numerical zero is a formed direction class. NULL is no fixed decoder signature and is retained separately.']}
    output=Path(a.salida).absolute()
    if not output.parent.resolve().is_relative_to((P/'control').resolve()):raise ValueError('New campaign control output only')
    with output.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':str(output),'sha256':sha(output),'cases':[{k:c[k]for k in('life_id','FI_sequence_q4','correct_FI_queries','Native_inputs_unique_in_this_life')}for c in cases],'Native_executed':False}))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--casos',nargs='+',required=True);ap.add_argument('--salida',required=True)
    main(ap.parse_args())
