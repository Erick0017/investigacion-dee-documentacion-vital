"""Actual snapshot resources; no evolution or participant operation."""
import argparse,gc,hashlib,json
from pathlib import Path
from dee_thinking.persistence import load_world_snapshot
def main():
    p=argparse.ArgumentParser();p.add_argument('--results',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();rows=[]
    for path in sorted(a.results.glob('SOC_*/MEASUREMENTS.json')):
        m=json.loads(path.read_text(encoding='utf-8'))
        if m.get('schema')!='CPC8.social.measurements.v1':continue
        snapshots=m.get('snapshots',[])
        if not snapshots:continue
        source=path.parent/snapshots[0]['path'];world,proof=load_world_snapshot(source,max_bytes=1024**3)
        before=int(world.runtime.current_tick)
        rows.append({'case_id':m['case']['id'],'primary':str(path.relative_to(a.results)),'primary_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'checkpoint':str(source.relative_to(a.results)),'checkpoint_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'tick_before':before,'tick_after':int(world.runtime.current_tick),'no_run_until_or_inputs':True,
            'actual_interfaces':len(world.interfaces),'actual_initial_material':len(world.recipe.placements),'actual_organizations':list(world.organization_ids),
            'historically_reported_interfaces':m['geometry']['resources']['interfaces'],'historically_reported_initial_material':m['geometry']['resources']['initial_material_sites'],
            'metadata_interface_count_underreports':m['geometry']['resources']['interfaces']!=len(world.interfaces),
            'scope':'One U0/support-bank preparation and a mobile recipient; not two independently validated complete compounds.'})
        del world;gc.collect()
    result={'schema':'CPC8.social.actual_resources.audit.v1','modality':'TECHNICAL_SNAPSHOT_INSPECTION_NOT_NEW_CASE','scientific_sources_unchanged':True,
        'issue':'Earlier inherited geometry.resources.interfaces counted the base but omitted newly declared social ports; correction is instrument metadata only, not a new physical preparation or altered decoder.',
        'rows':rows,'total_inspected':len(rows)}
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'snapshots_inspected':len(rows),'metadata_underreports':sum(r['metadata_interface_count_underreports'] for r in rows)}))
if __name__=='__main__':main()
