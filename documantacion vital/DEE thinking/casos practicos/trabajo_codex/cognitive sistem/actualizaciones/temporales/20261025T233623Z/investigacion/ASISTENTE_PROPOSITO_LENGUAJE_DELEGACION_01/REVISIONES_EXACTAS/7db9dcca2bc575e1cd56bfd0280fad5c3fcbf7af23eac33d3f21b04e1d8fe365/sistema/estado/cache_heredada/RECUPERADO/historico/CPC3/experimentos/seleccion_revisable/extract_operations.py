"""Passive extraction of the native world's retained operation journal."""
import hashlib,json,sys
from pathlib import Path
import dee_thinking as d
ROOT=Path(__file__).resolve().parents[2]
def main(root):
    rows=[]
    for path in sorted((root/'experimentos/seleccion_revisable/casos').glob('*/FINAL_T15.deetsnap')):
        w=d.OrganizationalWorld.load_snapshot(str(path));report=json.loads((path.parent/'MEASUREMENTS.json').read_text());receipts=[]
        for old in report['receipts']:
            r=w.runtime.receipt(old['id']);receipts.append({'id':r.id,'status':str(r.status),'requested_tick':r.requested_tick,'effective_tick':r.effective_tick,'channels':list(r.channels),'reason':r.reason})
        edits=[{'label':e.label,'site':[e.site.x,e.site.y,e.site.z],'tick':e.tick,'raw_before':e.raw_before,'raw_after':e.raw_after,'clock_before':e.clock_before,'clock_after':e.clock_after,'modality':str(e.modality)} for e in w.diagnostic_edits]
        rows.append({'case':path.parent.name,'snapshot':path.relative_to(root).as_posix(),'snapshot_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'tick':w.runtime.current_tick,'world_external_operations_retained':list(w.external_operations),'receipts_from_native_snapshot':receipts,'diagnostic_edit_receipts':edits,'new_advance_calls':0,'new_submit_calls':0,'scope':'This is the journal actually retained by OrganizationalWorld in its snapshot; it is not a complete low-level call interceptor and a missing entry does not certify absence of every possible operation.'})
    out={'schema':1,'mode':'PASSIVE_NATIVE_SNAPSHOT_INSPECTION','snapshots_loaded':len(rows),'new_scientific_cases':0,'rows':rows,'audit_limit':'Frozen run() declarations host_cognitive_writes=[] and operational_forks=0 are not treated as universal proof. Source review, actual submit receipts, this retained native journal and explicit diagnostic-cut record jointly define the measured coverage.'};p=root/'experimentos/seleccion_revisable/TELEMETRY/OPERATIONS_FROM_SNAPSHOTS.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({'loaded':len(rows),'journals':[(r['case'],len(r['world_external_operations_retained']),len(r['receipts_from_native_snapshot'])) for r in rows]},ensure_ascii=True))
if __name__=='__main__':main(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT)
