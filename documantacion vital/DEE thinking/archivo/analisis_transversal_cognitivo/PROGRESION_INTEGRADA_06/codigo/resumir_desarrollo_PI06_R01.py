"""Small primary-only table; no global decoding, Native or scientific rerun."""
from pathlib import Path
import csv,datetime,hashlib,json
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    recountpath=P/'control/RECALCULO_DESARROLLO_TRES_BRAZOS_PI06_R01.json';recount=read(recountpath)
    baselinepath=P/'control/BASELINE_global_PI06_R01.json';baseline=read(baselinepath)
    rows=[]
    for c in recount['cases']:
        execution=read(Path(c['execution_proof']));fi=[r for r in c['rows']if'condition'in r]
        if len(fi)!=3 or not execution['closed']or c['new_ticks_recalculated']!=600:raise ValueError('Complete three-query finite arms only')
        rows.append({'condition':fi[0]['condition'],'life_id':c['life_id'],
            'source_tick':825849,'source_snapshot_sha256':baseline['closed_card']['snapshot_sha256'],
            'final_tick':c['final_tick'],'final_snapshot_sha256':execution['final_snapshot_sha256'],
            'actual_Native_ticks':c['new_ticks_recalculated'],'query_ticks':[r['query_tick']for r in fi],
            'q4_sequence':c['FI_sequence_q4'],'q6_sequence':c['FI_sequence_q6'],
            'correct':c['correct_FI_queries'],'opportunities':3,'NULL_observations':sum(r['observed_q4']is None for r in fi),
            'formed_zero_observations':sum(r['observed_q4']==0 and r['observed_q4']is not None for r in fi),
            'Native_unique_per_query':[r['Native_inputs_unique']for r in fi],
            'Native_unique_total':c['Native_inputs_unique_in_this_life'],'Native_applied_total':c['Native_inputs_applied'],
            'all_queries_same_fixed_q4_q6_readers':True,'execution_proof':c['execution_proof'],
            'execution_proof_sha256':c['execution_proof_sha256'],'plan_sha256':c['plan_sha256']})
    value={'schema':'DEE.PI06.development.three_arm_scientific_summary.R01',
        'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source_main':{'life_id':'ECI02_PI03_REPRO_PI04_PI05_MAIN_01','N':67,'tick':824911,
            'snapshot_sha256':'af74c8f47e43ed3b2395a338a23a6cbd42f105ec2cff4daac15b7a4d45e90832'},
        'common_post_baseline':{'tick':825849,'snapshot':baseline['closed_card']['snapshot'],
            'snapshot_sha256':baseline['closed_card']['snapshot_sha256'],'proof_sha256':sha(baselinepath)},
        'recount':{'file':recountpath.name,'sha256':sha(recountpath)},'table':rows,
        'interpretation':'The left zero-load legal packet changes the first and phase-aligned third FI outcomes, while the immediate second FI succeeds. Intact and equal-dose off-path sham succeed in all three at the exact same query ticks. This supports a local timing/position-dependent interference, not acquired regulation or durable recovery.',
        'causal_limits':['Branches share the complete825849prefix; they are paired controls, not independent organisms.',
            'The sham and left arms have equal529inputs; intact has528. Phase and question sequence are matched.',
            'A temporary correct answer is not retention of an unrestricted function, memory restoration or a learned repair.',
            'The unique terminal RAW difference at52,48,47 was inspected only for IZQ versus INTACTO; no SHAM full-array equality is invented.',
            'Only the IZQ207frame contact analysis is complete here. Other frame collections are available but this summary reads small primaries only.'],
        'actual_new_Native_ticks_executed_by_this_tool':0,'Native_executed_by_this_tool':False,
        'no_adoption_claim':True}
    out=P/'control/SINTESIS_DESARROLLO_TRES_BRAZOS_PI06_R01.json'
    with out.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    table=P/'control/TABLA_DESARROLLO_TRES_BRAZOS_PI06_R01.csv'
    with table.open('x',encoding='utf-8-sig',newline='')as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader()
        for row in rows:writer.writerow({k:json.dumps(v,ensure_ascii=False)if isinstance(v,(list,dict))else v for k,v in row.items()})
    print(json.dumps({'proof':out.name,'sha256':sha(out),'csv_sha256':sha(table),'table':rows,'Native_executed':False},ensure_ascii=False))
if __name__=='__main__':main()
