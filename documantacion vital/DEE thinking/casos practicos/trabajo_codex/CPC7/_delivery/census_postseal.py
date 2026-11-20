"""External technical census only; do not change the ZIP or immutable clean proof."""
import ctypes
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[1]
WORKSPACE=ROOT.parents[4];CASES=ROOT.parents[1]
sys.path.insert(0,str(ROOT/'src/packaging'))
from bundle import NAME,put,sha

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def measured_census(label,directory):
    out=directory/'generated';evidence=[]
    path=out/'reference/REFERENCE.json';reference=read(path)
    assert reference['status']=='VERIFIED' and reference['not_new_scientific_replicates']
    assert len(reference['trajectories'])==2
    assert all(row['observations'][0]['tick']==0 for row in reference['trajectories'])
    evidence.append({'path':str(path),'sha256':sha(path),'pointer':'/trajectories',
                     'count':2,'histories':[row['history'] for row in reference['trajectories']]})
    preparations=2;continuations=0
    for folder,case in [('main','IR_P01_GUARDED_M1'),('revision_control','IR_C02_AUX_OFFPATH'),
                        ('guard_control','IR_C01_OFFPATH_GUARDS'),('reserve','IR_R607_GUARDED_M1')]:
        path=out/folder/case/'MEASUREMENTS.json';data=read(path)
        assert data['preparations']==1 and data['same_RUNTIME'] is True
        assert data['controlled_continuations']==0
        preparations+=data['preparations'];continuations+=data['controlled_continuations']
        evidence.append({'path':str(path),'sha256':sha(path),
                         'fields':{key:data[key] for key in ('preparations','controlled_continuations','same_RUNTIME')}})
    path=out/'demo/VERIFICATION.json';demo=read(path)
    assert demo['preparations']==1 and demo['controlled_continuations']==1
    preparations+=demo['preparations'];continuations+=demo['controlled_continuations']
    evidence.append({'path':str(path),'sha256':sha(path),'fields':{
                     'preparations':demo['preparations'],'controlled_continuations':demo['controlled_continuations']}})
    path=out/'interface/INTERFACE_TEST.json';interface=read(path)
    assert interface['status']=='VERIFIED' and interface['technical_preparations']==1
    preparations+=interface['technical_preparations']
    evidence.append({'path':str(path),'sha256':sha(path),'pointer':'/technical_preparations','count':1})
    assert preparations==8 and continuations==1
    return {'cut':label,'classification':'POST_SEAL_TECHNICAL_REPRODUCTION_NOT_INDEPENDENT_SCIENTIFIC_SAMPLES',
            'fresh_native_preparations':preparations,'controlled_continuations':continuations,
            'supervised_clean_commands':17,'posttrajectory_assertion_groups':13,'evidence':evidence}

report_path=CASES/'CPC7_VERIFICACION/PUBLICACION.json'
publication=read(report_path);assert publication['publication_pipeline_status']=='COMPLETE'
canonical=CASES/NAME;assert sha(canonical)==publication['sha256']
proof_path=Path(publication['external_final_verification']['path'])
proof_before=sha(proof_path);assert proof_before==publication['external_final_verification']['sha256']
with zipfile.ZipFile(canonical) as archive:
    raw=archive.read('CPC7/revision/INDICE_EVIDENCIA.json');frozen=json.loads(raw)
assert frozen['counts']['primary_case_records']==157
assert frozen['counts']['technical_records_separate']==15
table=[measured_census('PRE01',WORKSPACE/'c7_verify_pre01'),
       measured_census('FINAL01',WORKSPACE/'c7_verify_final01')]
publication['postseal_reproduction_census']={
 'frozen_index':{'member':'CPC7/revision/INDICE_EVIDENCIA.json','sha256':hashlib.sha256(raw).hexdigest(),
                 'counts':frozen['counts']},
 'postseal_runs':table,'postseal_fresh_native_preparations':16,'postseal_controlled_continuations':2,
 'counting_scope':'PRE and FINAL are deterministic technical reproductions after the frozen index, not additional independent scientific samples. Engine identity, recalculation and auditors are not fresh preparations. Auditors may restore states for comparison; those are not new T0 preparations. 757 gzip decodes are state-integrity checks, not preparations.'}
publication['postpublication_census_instrument']={'path':str(Path(__file__)),'sha256':sha(Path(__file__)),
                                                 'participant_worlds_created':0}
budget=read(ROOT/'BUDGET.json');counter=ctypes.c_longlong()
assert ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(counter))
elapsed=(counter.value-budget['start_qpc'])/budget['qpc_frequency']
publication['campaign_clock'].update(end_qpc=str(counter.value),elapsed_seconds=elapsed,
                                    within_original_budget=elapsed<=budget['budget_seconds'],
                                    reported_utc=datetime.now(timezone.utc).isoformat())
assert sha(proof_path)==proof_before and sha(canonical)==publication['sha256']
put(report_path,publication)
print(json.dumps({'status':'VERIFIED','census':[{key:row[key] for key in ('cut','fresh_native_preparations','controlled_continuations')} for row in table],
                  'publication_report_sha256':sha(report_path),'elapsed_seconds':elapsed,
                  'canonical_sha256_unchanged':publication['sha256'],'verification_sha256_unchanged':proof_before},indent=2))
