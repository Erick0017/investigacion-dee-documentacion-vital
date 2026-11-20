"""Finite UI error/continuity checks, no new scientific trajectories."""
from pathlib import Path
from array import array
import argparse,hashlib,json,sys,shutil
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from campaign import identity,put
from interactive_worker import Application
from lenguaje.session import KEY

def fingerprint(app):
    r=app.need().world.runtime
    # OrganizationalWorld.save_snapshot serializes its *current* envelope into
    # the saved Runtime copy, not back into the live Runtime's previous envelope.
    # Compare the actual reconstructed public fields, not that derived stale hex.
    metadata={k:v for k,v in dict(r.snapshot_metadata_entries).items() if not k.startswith('dee_thinking.organizational.v1.')}
    return (r.current_tick,hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),
            hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest(),metadata,
            [(x.id,str(x.status),x.requested_tick,x.effective_tick) for x in r.receipts],
            list(app.need().world.external_operations),list(r.channel_names))

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__,out/'EXECUTED_SOURCE.py')
    engine=identity();app=Application(out)
    source=ROOT/'resultados/demo/CENTRAL_V3_01/RED_LENGUAJE_T1501.deetsnap'
    app.command('cargar "'+str(source)+'"');before=fingerprint(app);actual=app.session
    checks={}
    for text in ('currículo','avanzar 1502','entrada lex.L1.word 5 1501','consultar DESCONOCIDO'):
        try:app.command(text);raise AssertionError('Invalid command unexpectedly admitted')
        except ValueError:pass
        assert fingerprint(app)==before and app.session is actual,text
        checks[text]='Rejected with MAIN byte/clock/tick/receipts/protocol unchanged'
    assert not (out/'CURRICULO').exists()
    # A candidate can have valid physical bytes but malformed protocol metadata.
    from red.session_v3 import NetworkSession
    candidate=NetworkSession.load(source)
    state=json.loads(candidate.world.runtime.snapshot_metadata(KEY));state['stage']='FOREIGN_STAGE'
    candidate.world.runtime.set_snapshot_metadata(KEY,json.dumps(state))
    invalid=out/'INVALID_METADATA.deetsnap';candidate.save(invalid)
    try:app.command('cargar "'+str(invalid)+'"');raise AssertionError('Malformed protocol accepted')
    except ValueError:pass
    assert fingerprint(app)==before and app.session is actual
    checks['transactional_load']='Rejected malformed candidate before replacing live MAIN'
    for _ in range(3):app.command('observar')
    assert fingerprint(app)==before
    checks['passive_ui']='Three observations unchanged'
    result=app.command('consultar MALO')
    assert app.session is actual and app.session.world.runtime.current_tick==1529
    checks['new_interaction_after_errors']={'tick':1529,'actual_result':result}
    after=Application(out)
    after.command('cargar "'+str(ROOT/'resultados/demo/DIRECTION_CONTINUE04/RED_T1637.deetsnap')+'"')
    assert after.language is None and after.need().world.runtime.current_tick==1637
    after.command('entrada C.report.plus 17 1640')
    after.command('guardar FUTURE_AFTER_DIRECTION.deetsnap')
    same=fingerprint(after)
    restored=Application(out)
    restored.command('cargar "'+str(out/'FUTURE_AFTER_DIRECTION.deetsnap')+'"')
    restored_state=fingerprint(restored)
    put(out/'RESTORE_COMPONENT_COMPARISON.json',{'component_equal':[x==y for x,y in zip(same,restored_state)],
        'metadata_original':same[3],'metadata_restored':restored_state[3],
        'receipts_original':same[4],'receipts_restored':restored_state[4],
        'derived_envelope_scope':'Live pre-save metadata can contain an older serialized OrganizationalWorld; compare current public operation log/channels/receipts and independent protocol metadata instead. Full mismatching envelopes retained in PUBLIC_UI_INSPECTION03.'})
    assert restored_state==same and restored.language is None
    after.command('avanzar 1643');restored.command('avanzar 1643')
    assert fingerprint(after)==fingerprint(restored)
    checks['completed_protocol_later_continuation']='Historical completed phase preserves subsequent physical evolution and new pending research input; no old decoder reactivated'
    regulated=Application(out)
    regulated.command('cargar "'+str(ROOT/'resultados/demo/REGULATED_FINAL01/RED_REGULADA_T937.deetsnap')+'"')
    before_regulated=fingerprint(regulated);live=regulated.session
    for text in ('lenguaje normal','renovar-contexto','currículo','direcciones'):
        try:regulated.command(text);raise AssertionError('Unsupported regulated command unexpectedly admitted')
        except ValueError:pass
        assert fingerprint(regulated)==before_regulated and regulated.session is live
    checks['regulated_domain_guards']='No language-profile fusion, duplicate curriculum or new body on four rejected commands; live MAIN unchanged'
    put(out/'PUBLIC_UI_CHECKS.json',{'identity':engine,'checks':checks,
        'scope':'Technical errors/load isolation; same restored MAIN later receives its second new physical query.'})
    print(json.dumps({'technical_checks':len(checks),'same_main_final_tick':1529}))

if __name__=='__main__':main()
