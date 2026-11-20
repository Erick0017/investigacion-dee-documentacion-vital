"""Close the existing PI06 Native ledger by reading already closed evidence.

No engine import, replay, owner, state edit or selector change.
"""
from pathlib import Path
import datetime, hashlib, json

P = Path(__file__).resolve().parents[1]

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(b):
    return hashlib.sha256(b).hexdigest()

def main():
    output = P/'control/FASE_NATIVE_CERRADA_PI06_R01.json'
    if output.exists():
        raise ValueError('Existing closure must be read, never silently repeated')
    last = P/'control/PI06_CONFIRMACION_CONTROL67_R04.json'
    r = read(last)
    fine = read(P/'control/PI06_CONFIRMACION_FINA_R04.json')
    assert r['closed'] and fine['closed']
    assert r['status'] == 'FAILED_PRESERVED'
    assert r['error']['message'] == 'Actual step exceeds preregistered finite Native bound'
    assert r['new_ticks'] == 1300 and fine['new_ticks'] == 15
    assert r['budget_before']['Native_ticks_all_branches'] + r['new_ticks'] == 7882
    expected = r['protected_main_before']
    assert expected == r['protected_main_after']
    actual = {name: sha(Path(name).read_bytes()) for name in expected}
    assert actual == expected
    path = P/'REGISTRO_CAMPANA.json'
    before = path.read_bytes()
    record = json.loads(before)
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    record.update(phase='NATIVE_CLOSED_ANALYSIS_AND_INCORPORATION_ONLY',
                  Native_ticks_closed=7882,
                  last_progress_utc=stamp,
                  current_native_plan=None,
                  new_Native_worlds_forbidden_after_closure=True)
    record['latest_closed_science'].update(
        environment_exploratory_ticks=67,
        environment_fine_confirmation_ticks=15,
        final_control_ticks=1300,
        diagnostic_worlds=12,
        control_final_tick=827749,
        control_protocol_status='FAILED_PRESERVED',
        control_bound_exceeded_by_ticks=231,
        control_physical_useful_product_observed=True)
    assert path.read_bytes() == before
    after = (json.dumps(record, ensure_ascii=False, indent=2)+'\n').encode('utf8')
    path.write_bytes(after)
    proof = {'schema':'DEE.PI06.Native_science_closed.R01', 'closed_utc':stamp,
             'Native_ticks_all_branches':7882, 'diagnostic_worlds':12,
             'source':str(last), 'source_sha256':sha(last.read_bytes()),
             'principal_critical_hashes_unchanged':actual,
             'campaign_record_before_sha256':sha(before),
             'campaign_record_after_sha256':sha(after),
             'no_new_Native_ticks_in_this_operation':True,
             'control_bound_is_not_revised_after_outcome':True,
             'no_promotion_or_selector_change':True,
             'scope':'Science stops here. Closed useful control result and protocol violation remain distinct. Documentation and passive recalculation follow.'}
    output.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'closure':str(output),'sha256':sha(output.read_bytes()),
                      'Native_ticks':7882,'worlds':12,'main_unchanged':True}))

if __name__ == '__main__':
    main()
