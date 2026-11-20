"""Reconcile technical evidence without converting failed attempts into PASS."""
import argparse,json
from datetime import datetime,timezone
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,identity,put,sha
from package_cpc6 import selected

PROOFS=(
 ('integrated_T40','resultados/technical_integrated_02/TECHNICAL.json','verified',True),
 ('bilateral_T105','resultados/technical_longitudinal_01/TECHNICAL.json','verified',True),
 ('final_renewed_T170','resultados/technical_renewed_01/TECHNICAL.json','verified',True),
 ('transport_partition_reassembly','resultados/distribution_tests_02','verified',True),
 ('lossless_snapshot_codec','resultados/snapshot_storage_tests_02/TECHNICAL.json','verified',True),
 ('minimal_public_app','resultados/minimal_app_02/MINIMAL_REPORT.json','status','VERIFIED'),
 ('public_signs_retention_continuity','resultados/PUBLIC_DEMO_CHECKS_02.json','verified',True),
 ('static_host_boundary_inventory','resultados/HOST_BOUNDARIES_FINAL.json','status','REVIEWED_STATIC_BOUNDARIES'))
RESOLUTIONS={
 'architecture_bridge_delayed_01':{'cause':'Nonexistent unpack_record convenience attribute; failed before constructing the world.','later_evidence':['jobs/architecture_bridge_delayed_02/COMMAND.json'],'scope':'Engineering preparation repair, not a changed microscopic rule.'},
 'architecture_bridge_delayed_03':{'cause':'Prepared support pair did not realize its declared vector; explicit preparation validation rejected it.','later_evidence':['jobs/architecture_bridge_delayed_04/COMMAND.json','jobs/architecture_bridge_confirm_05/COMMAND.json'],'scope':'New declared preparation; failed attempt remains distinct.'},
 'reference_central':{'cause':'Original wrapper/observer comparison assertions differed; native data retained.','later_evidence':['resultados/referencias/REFERENCE_REPRODUCTION_CHECK.json'],'scope':'Separate posthoc reconciliation of observer-contract additions and full RAW/clocks/tick. Original failed checker remains FAIL, not rewritten to PASS.'},
 'reference_central_normalized01':{'cause':'Serialization normalization alone did not resolve documentary/observer additions.','later_evidence':['resultados/referencias/REFERENCE_REPRODUCTION_CHECK.json'],'scope':'Offline reconciliation, no third native rerun or physics alteration. Original exit1 preserved.'},
 'reference_sem01':{'cause':'Whole wrapper/tuple-list comparison differed despite acquired state and receipts matching.','later_evidence':['jobs/reference_sem01_normalized01/COMMAND.json','resultados/referencias/sem01_normalized01/REPLAY_CHECK.json'],'scope':'Scientific values and full physical state compared separately from elapsed/provenance wrappers; original retained.'},
 'technical_integrated_01':{'cause':'Backend enum DENSE does not exist; actual contract is DENSE_SEQUENTIAL. No native trajectory executed.','later_evidence':['jobs/technical_integrated_02/COMMAND.json','resultados/technical_integrated_02/TECHNICAL.json'],'scope':'Test API spelling repaired; no physics, oracle or expectation changed.'},
 'snapshot_storage_tests_01':{'cause':'Local-module import path absent under Python -I; failed before any encoding test.','later_evidence':['jobs/snapshot_storage_tests_02/COMMAND.json','resultados/snapshot_storage_tests_02/TECHNICAL.json'],'scope':'Explicit source-directory import under isolation; raw originals untouched.'}}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    proofs=[]
    for name,rel,key,value in PROOFS:
        path=ROOT/rel;data=json.loads(path.read_text(encoding='utf-8'));ok=data.get(key)==value
        proofs.append({'name':name,'path':rel,'sha256':sha(path),'field':key,'observed':data.get(key),'required':value,'verified':ok})
    failures=[];commands=[]
    for path in sorted((ROOT/'jobs').glob('*/COMMAND.json')):
        data=json.loads(path.read_text(encoding='utf-8-sig'));name=path.parent.name
        row={'name':name,'status':data.get('status'),'exit_code':data.get('exit_code'),'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)}
        commands.append(row)
        if data.get('exit_code') not in (None,0):
            stderr=path.parent/'stderr.log';row={**row,'original_status':'FAILED_COMMAND_PRESERVED',
               'stderr_sha256':sha(stderr),'stderr_path':stderr.relative_to(ROOT).as_posix(),
               'stderr_tail':stderr.read_bytes().decode('utf-8',errors='replace')[-2400:],
               'review':RESOLUTIONS.get(name,{'scope':'Unclassified failure; must remain visible for review.'})}
            failures.append(row)
    mapping=json.loads((ROOT/'LOGICAL_STATES.json').read_text(encoding='utf-8'))
    current={rel:path.stat().st_size for path,rel in selected(ROOT) if rel.startswith('resultados/') and rel.endswith('.deetsnap')}
    staged={x['logical_path'] for x in mapping['states']};missing=sorted(set(current)-staged)
    originals=ROOT/'genealogia/INSTRUMENTO_DISTRIBUCION.json';notices=ROOT/'runtime/AVISOS/PROCEDENCIA.json'
    result={'schema':'CPC6.delivery-technical.v1','generated_utc':datetime.now(timezone.utc).isoformat(),
      'native_technical_checks_verified':all(x['verified'] for x in proofs),'proofs':proofs,'engine':identity(),
      'completed_supervisor_commands_at_cutoff':len(commands),'failed_commands_preserved':failures,
      'failed_commands_count':len(failures),'all_historical_attempts_passed':False,
      'important_representation_differences':['Tuple/list geometry differs as Python containers; published JSON values and all RAW/clocks/ports must match.',
        'Opaque organizational serialization cache can differ transiently in memory after continuation. It is reported separately, not claimed equal; own session metadata, native receipts/queue/protocol progress are checked. Fresh-loaded final snapshots compare their cache separately too.'],
      'storage':{'state':'CURRENT_STAGE_COVERS_ALL_STATES' if not missing and set(current)==staged else 'STAGE_REFRESH_REQUIRED',
        'map':'LOGICAL_STATES.json','map_sha256':sha(ROOT/'LOGICAL_STATES.json'),'staged_snapshots':len(staged),
        'current_plain_result_snapshots':len(current),'logical_bytes_staged':mapping['logical_bytes'],
        'encoded_bytes_staged':mapping['encoded_bytes'],'new_snapshots_not_yet_staged':missing,
        'workspace_originals_deleted_or_replaced':False,'scope':'Byte-exact encoding evidence; final closed ZIP must independently check every gzip CRC/logical SHA.'},
      'original_artifact_identity_evidence':{'path':originals.relative_to(ROOT).as_posix(),'sha256':sha(originals)},
      'existing_notices':{'path':notices.relative_to(ROOT).as_posix(),'sha256':sha(notices),'new_project_license_assigned':False},
      'exact_candidate_clean_installation':'PENDING_FINAL_CANDIDATE_EXTERNAL_REPORT',
      'canonical_publication':'NOT_AUTHORIZED_BY_THIS_REPORT',
      'scope':'Technical integrity, finite native equivalence and reproducibility only; not a scientific verdict or an assertion that all historical tests passed.'}
    put(a.output,result);print(json.dumps({'native_technical_checks_verified':result['native_technical_checks_verified'],
      'failed_commands_preserved':len(failures),'storage':result['storage']['state']}));assert result['native_technical_checks_verified']


if __name__=='__main__':main()
