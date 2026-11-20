"""Portable passive MAIN/control view of existing R02 measurements.

This does not run Native, Studio, a model or a database. Both arms must point to
closed real result/checkpoint files. Optional later MAIN blocks are explicit;
missing or merely planned episodes are never inserted or scored as zero.
"""
from pathlib import Path
import argparse
import csv
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from RECALCULO_CIERRE8_R07_R02 import Sources,run,save_outputs,ensure,canonical

def selected_summary(arm,cycles,scope,pair):
    rows=[r for r in arm['rows']if r['cycle']in cycles]
    return {'pair':pair,'arm':arm['name'],'sensor_arm':arm['sensor_arm'],'scope':scope,
        'completed_opportunities':len(rows),'global_cycles':[r['cycle']for r in rows],
        'queries':sum(r['query_cost']or 0 for r in rows),
        'tolls':sum(r['toll_cost']or 0 for r in rows),
        'new_resources':sum(r['new_resources']or 0 for r in rows),
        'new_deliveries':sum(r['new_deliveries']or 0 for r in rows),
        'numeric_invocations':sum('numeric_formed'in r for r in rows),
        'formed_integers':sum(r.get('numeric_formed')is True for r in rows),
        'correct_chosen_opcode':sum(r.get('numeric_correct')is True for r in rows),
        'no_integer':sum(r.get('numeric_formed')is False for r in rows),
        'loops_2_3':sum(r['loop_2_3_transition']for r in rows),
        'effective_overrides':sum(r['effective_override']for r in rows)}

def paired_view(facts):
    main=[a for a in facts['arms']if a['participant']=='LIVE_NATIVE'and a['sensor_arm']=='local_tag']
    ctrl=[a for a in facts['arms']if a['participant']=='LIVE_NATIVE'and a['sensor_arm']=='constant_tag2']
    ensure(main and ctrl,'At least one closed MAIN and constant-tag control required')
    table=[];pairs=[]
    for m in main:
        for c in ctrl:
            pair=m['name']+'__'+c['name']
            common=set(m['completed_cycles'])&set(c['completed_cycles'])
            ordered=sorted(common)
            pair_rows=[]
            for arm in(m,c):
                pair_rows.append(selected_summary(arm,set(arm['completed_cycles']),'FULL_OBSERVED',pair))
                pair_rows.append(selected_summary(arm,common,'MATCHED_COMMON_OBSERVED',pair))
            table.extend(pair_rows)
            pairs.append({'pair':pair,'main_completed':m['completed_new'],'control_completed':c['completed_new'],
                'matched_completed':len(ordered),'matched_global_cycles':ordered,
                'matched_is_contiguous_prefix':not ordered or ordered==list(range(29,max(ordered)+1)),
                'main_first6_P02':m['first6_P02'],'control_first6_P02':c['first6_P02'],
                'shared_parent_is_not_independent_replicates':True,
                'no_score_for_unoffered_or_planned_episodes':True})
    return {'schema':'DEE.R07.MAIN_CTRL.PassivePairedView.R01','pairs':pairs,'table':table,
        'interpretation':['FULL denominators can differ, e.g. MAIN8 versus control6; comparison of the matched prefix then uses6 in each arm.',
            'No admission/dose equality is inferred after distinct choices. Phase, exposure and consequences require the recorded primaries.',
            'R02 common_observed_cycles/comparison are for the main/reference configuration group; the paired-control table here is authoritative for MAIN versus CTRL.',
            'Source fragments preserve their original operation IDs and source/line locations. Recovered Q1 is not executed or counted again.',
            'The verified kind/utc decoration difference in the MAIN29–33 combined result is documentary; scientific/source-field discrepancies remain visible.',
            'No causal learning result, material reopen or pending episode is certified by this passive view.']}

def execute(inputs,source_root,package_root,output):
    spec=json.loads(Path(inputs).read_text('utf-8-sig'))
    facts=run(spec,Sources(source_root or Path(inputs).parent,package_root))
    paired=paired_view(facts)
    save_outputs(output,facts)
    output=Path(output)
    (output/'CONTROLES_PAREADOS_R07.json').write_text(json.dumps(paired,ensure_ascii=False,indent=2)+'\n','utf-8')
    table=paired['table']
    with(output/'COMPARACION_PAREADA_MAIN_CTRL_R07.csv').open('w',encoding='utf-8',newline='')as f:
        writer=csv.DictWriter(f,fieldnames=list(table[0]));writer.writeheader()
        for row in table:writer.writerow({k:canonical(v)if isinstance(v,(dict,list))else v for k,v in row.items()})
    return facts,paired

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inputs',type=Path,required=True)
    p.add_argument('--source-root',type=Path);p.add_argument('--package-root',type=Path)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();facts,paired=execute(a.inputs,a.source_root,a.package_root,a.output)
    print(json.dumps({'output':str(a.output),'issues':facts['issues_total'],'pairs':paired['pairs'],
        'Native_calls':0,'MCP_calls':0,'model_calls':0},ensure_ascii=False))
