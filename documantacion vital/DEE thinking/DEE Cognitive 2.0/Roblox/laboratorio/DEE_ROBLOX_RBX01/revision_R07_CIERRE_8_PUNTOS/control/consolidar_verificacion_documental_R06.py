"""Record the actual selector-only check; no experiment or ZIP work."""
from pathlib import Path
import datetime
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=ROOT/'control/VERIFICACION_SELECTOR_R06_PASIVA.json'
check=json.loads(report.read_text(encoding='utf-8-sig'))
assert check['status']=='CLOSED_SOURCE_SELECTION_CHECKED'and check['verify_only']is True
assert check['selected_files']==355 and check['Native_calls']==0 and check['DB_opened']is False and check['ZIP_created']is False
closed=sum(g['status']=='CLOSED_SOURCE_VERIFIED_NOT_EXPERIMENTALLY_REPRODUCED'for g in check['groups'])
pending=sum(g['status']=='PENDING'for g in check['groups'])
assert closed==8 and pending==4
path=ROOT/'control/EXPEDIENTE_V3_PLAN_FINAL_TENTATIVO_R06.json'
raw=path.read_bytes();plan=json.loads(raw);assert plan['finalized']is False
plan['closed_source_assembly']=dict(schema='DEE.R07.ClosedSourceSelection.R01',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 groups=check['groups'],file_only=True,Native_calls=0,DB_opened=False,ZIP_created=False,
 scientific_or_operational_approval=False,portable_verification=False,plan_before_sha256=sha(raw),
 registry_sha256=sha((ROOT/'control/FUENTES_CERRADAS_EFECTIVAS_R07.json').read_bytes()),
 selector_sha256=sha((ROOT/'control/ensamblar_fuentes_cerradas_v3.py').read_bytes()),
 actual_verify_only_report='control/VERIFICACION_SELECTOR_R06_PASIVA.json',actual_exit_code=0)
for row in plan['recalculations']:
 if row.get('script')=='control/ensamblar_fuentes_cerradas_v3.py':
  row['status']='ActualR06verify_onlyexit0;8closedgroupsand4pending;priorfixturesnotrerun;noZIP'
plan['static_readcheck']='R06explicitclosedsourcepins/aliases/closureassertionscheckedexit0;newportable2syntheticisolationcheckspassed;science/resourcesnotrerun;finalextractionandnewprivacyreviewpending.'
write(path,plan)
cont_path=ROOT/'control/CONTINUIDAD_PAQUETE_PASIVO_R06.json'
cont=json.loads(cont_path.read_text(encoding='utf-8'))
cont['selector_verification']=dict(path=str(report),actual_exit_code=0,selected_files=355,closed_groups=8,pending_groups=4,
 scope='Exact closed paths/pins/closure assertions only; no new Native/science/resource execution.')
cont['new_portable_synthetic_isolation_tests']=dict(passed=2,total=2,actual_exit_code=0,
 report='control/VERIFICACION_P07_PORTABLE_SINTETICA_R06.json',actual_P07_recalculation=False)
cont['pending']=[x for x in cont['pending']if x!='ActualselectorR06verification']
cont['portable_limit']='Actual final clean extraction still required; local SQLite audit is preserved but never proposed as portable execution.'
write(cont_path,cont)
print(json.dumps(dict(members=355,raw_bytes=plan['selected_raw_bytes_at_listing_not_freeze'],
 selector_actual_exit_code=0,closed_groups=closed,pending_groups=pending,synthetic_new_checks_passed=2,
 finalized=False,ZIP_created=False,final_hash_issued=False),ensure_ascii=False))
