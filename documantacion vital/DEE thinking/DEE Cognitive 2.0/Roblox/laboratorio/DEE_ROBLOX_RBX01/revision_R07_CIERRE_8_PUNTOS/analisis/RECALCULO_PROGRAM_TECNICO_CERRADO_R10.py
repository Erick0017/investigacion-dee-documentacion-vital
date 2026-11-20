"""Passive new technical PROGRAMMED18 accounting; original facts reused, no Native."""
from __future__ import annotations
import argparse, csv, importlib.util, json
from pathlib import Path
s=importlib.util.spec_from_file_location('passive_R02',Path(__file__).with_name('RECALCULO_CIERRE8_R07_R02.py'))
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def run(a):
    if a.output.exists()or not a.output.parent.is_dir():raise ValueError('Fresh output required')
    spec=json.loads(a.inputs.read_text('utf-8-sig'));source=m.Sources(a.source_root,a.package_root)
    facts=m.run(spec['new_technical'],source)
    original=source.json(spec['original_facts']);arms=[x for x in original['arms']if x['participant']=='PROGRAMMED']
    if len(arms)!=1:raise ValueError('Exactly one original PROGRAMMED facts arm')
    old=arms[0];new=facts['arms'][0]
    old_result=source.json(spec['original_result']);new_result=source.json(spec['new_result'])
    old_rows={r['cycle']:r for r in old['rows']};new_rows={r['cycle']:r for r in new['rows']}
    old_raw={r['cycle']:r for r in old_result['rows']};new_raw={r['cycle']:r for r in new_result['rows']}
    fields=('origin','destination','q1','q1_null','selected_route','executed_route','route_null','outcome','motor_status','actual_A','actual_B','new_resources','new_deliveries','query_cost','toll_cost','stock_after','numeric_result','numeric_formed','numeric_correct','operation','memory_value','form')
    comparisons=[];field_counts={key:0 for key in fields}
    def motor(row):return(row.get('world_result')or{}).get('motor')or{}
    for cycle in sorted(set(old_rows)|set(new_rows)):
        left=old_rows.get(cycle);right=new_rows.get(cycle)
        if left is None or right is None:raise ValueError('Unequal exposed cycle cursor')
        diff={key:{'original':left.get(key),'technical':right.get(key)}for key in fields if left.get(key)!=right.get(key)}
        for key in diff:field_counts[key]+=1
        lm=motor(old_raw[cycle]);rm=motor(new_raw[cycle])
        physics={key:{'original':lm.get(key),'technical':rm.get(key)}for key in ('status','wallSeconds','distance','recomputes','finalPosition','selectedDestination')if lm.get(key)!=rm.get(key)}
        comparisons.append({'cycle':cycle,'original_selected_route':left['selected_route'],'technical_selected_route':right['selected_route'],'scientific_field_differences':diff,'physics_scalar_differences':physics,'waypoints_exact_equal':lm.get('waypoints')==rm.get('waypoints'),'original_waypoint_count':len(lm.get('waypoints',[])),'technical_waypoint_count':len(rm.get('waypoints',[])),'original_waypoint_sha256':m.digest(m.canonical(lm.get('waypoints')).encode()),'technical_waypoint_sha256':m.digest(m.canonical(rm.get('waypoints')).encode()),'original_raw_locator':spec['original_result']+'#/rows/'+str(list(old_raw).index(cycle))+'/world_result/motor','technical_raw_locator':spec['new_result']+'#/rows/'+str(list(new_raw).index(cycle))+'/world_result/motor'})
    source.verify_unchanged()
    report={'schema':'DEE.R07.PROGRAMMED.original_vs_technical.passive.R10.v1','old_facts_recalculated':False,'new_technical_only_recalculated':True,'original_name':old['name'],'technical_name':new['name'],'original_completed':old['completed_new'],'technical_completed':new['completed_new'],'original_delta':old['delta'],'technical_delta':new['delta'],'original_native_ticks_from_phases':old['native_ticks_from_unique_phases'],'technical_native_ticks_from_phases':new['native_ticks_from_unique_phases'],'scientific_field_difference_counts':field_counts,'cycles_with_physics_scalar_differences':sum(bool(r['physics_scalar_differences'])for r in comparisons),'cycles_with_different_waypoint_arrays':sum(not r['waypoints_exact_equal']for r in comparisons),'per_cycle':comparisons,'new_technical_issues':facts['issues_total'],'not_independent_replication':True,'not_Native_repetition':True,'recorded_frames':0,'recording_failure_basis':'Root notice: wrong requested Win32 title; actual own PID6764 title RobloxStudio/classQt5159QWindowIcon. No footage claimed. New pure filming remains separate.','Native_MCP_Studio_model_SQLite_executions':0,'sources':list(source.records.values()),'limits':['Same prepared programmed-policy family and inherited environment; not independent cognitive or Native replicates.','Metadata IDs/session/history differ; exact physics/path differences are retained, not suppressed.','Original science facts reused; original result is read solely for requested physics/path comparison.','A technical repeat with0Native and0frames does not add Native experience or establish a real video.']}
    a.output.mkdir();(a.output/'HECHOS_PROGRAM_TECH_R10.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (a.output/'COMPARACION_PROGRAM_ORIGINAL_TECNICO_R10.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for name,rows in [('CICLOS_PROGRAM_TECH_R10.csv',new['rows']),('COMPARACION_PROGRAM_18_R10.csv',comparisons)]:
        with(a.output/name).open('w',encoding='utf-8',newline='')as f:
            keys=list(dict.fromkeys(k for r in rows for k in r));w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows({k:m.canonical(v)if isinstance(v,(dict,list))else v for k,v in r.items()}for r in rows)
    print(json.dumps({k:report[k]for k in('original_completed','technical_completed','original_delta','technical_delta','cycles_with_physics_scalar_differences','cycles_with_different_waypoint_arrays','new_technical_issues','not_independent_replication')},ensure_ascii=False))
    return 0 if facts['issues_total']==0 else 1
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--source-root',type=Path,required=True);p.add_argument('--package-root',type=Path);p.add_argument('--output',type=Path,required=True);raise SystemExit(run(p.parse_args()))
