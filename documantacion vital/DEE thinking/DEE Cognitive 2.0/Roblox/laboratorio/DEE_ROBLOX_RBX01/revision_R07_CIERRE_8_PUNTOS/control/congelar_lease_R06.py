"""Seal only prepared administrative R06 sources; no Native execution."""
from pathlib import Path
import ast,datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
    files=['native/lease_R06_bundle/'+x for x in('rbx07_native_v3.py','rbx07_identity_v3.py','rbx07_funciones_v3.py')]
    files+=['native/'+x for x in('lease_core_v3_R06.py','ledger_v3_R06.py','owner_support_v3_R06.py','migrar_lease_cerrada_v3_R06.py','test_lease_v3_R06_offline.py')]
    files+=['control/'+x for x in('mcp_persistente_v3_R06.py','world_comprimido_v3_R06.py','run_integrated_v3_R06.py')]
    files+=['prototipo/NATIVE_LIMPIO_R07/ejecutar_piloto_R07_preparado_R06.py','load/PROTOCOLO_CARGA_V3_R06.json']
    rows=[]
    for name in files:
        path=ROOT/name
        if path.suffix=='.py':ast.parse(path.read_bytes())
        rows.append({'file':name,'bytes':path.stat().st_size,'sha256':sha(path)})
    actor=ROOT/'native/lease_R06_bundle/rbx07_native_v3.py';old=ROOT/'native/lease_R05_bundle/rbx07_native_v3.py'
    normalize=lambda s:s.replace('1794880800','DATE_LAST').replace('1794902400','DATE_LAST').replace('1794884820','DATE_END').replace('1794906420','DATE_END')
    assert ast.dump(ast.parse(normalize(old.read_text('utf8'))))==ast.dump(ast.parse(normalize(actor.read_text('utf8'))))
    record={'schema':'DEE.RBX07.prospective_native_lease_freeze.R06','sealed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'native_start_epoch':1794841620,'last_new_episode_epoch':1794902400,'native_cutoff_epoch':1794906420,
      'previous_prepared_freeze_sha256':'22af4321371dffb2831996bd75cb5d98e761c6a7e0f0e87ab13b28822c7ae2d9',
      'reason':'Prospective final finite18h window after external interruption. Same original15:07UTC start; no clock/counter reset and no retroactive admission.',
      'native_sources_sha256':{x:sha(ROOT/'native/lease_R06_bundle'/x)for x in('rbx07_native_v3.py','rbx07_identity_v3.py','rbx07_funciones_v3.py')},
      'files':rows,'global_tick_limit':160000,'max_lives':6,'owner_job_limit_bytes':536870912,'raw_support_limit':10000,'threads':1,
      'minimum_available_host_bytes':3758096384,'max_role_cycles':{'main':24,'control':6,'load':3,'pilot':3},
      'evaluative_horizons':{'MAIN_new_target_max':18,'MAIN_global_target_max':46,'CTRL1':6,'LOAD_each':3,'PILOT_target':1},
      'metadata_migration_allowlist':['own m.code_scope','own CODE_SCOPE_KEY','official administrative SYSTEM commit'],
      'never_change':['RAW','clocks','geometry','policy','experiences','cycles','sequence','session','pending','failure','uncertain','log_count','log_chain_sha256','ledger.consumed','ledger.intents','ledger.reservations'],
      'technical_uncertainty_recovery_is_separate_NOT_applied':True,'Native_MCP_model_calls_by_preparation':0,
      'Root_review_before_apply_required':True,'PILOT_guard':'Tightened to the declared3.5GiB host floor; no lower limit',
      'load_protocol_is_prepared_not_materially_reproduced':True}
    output=ROOT/'control/CONGELADO_NATIVE_R07_LEASE_R06.json'
    with output.open('x',encoding='utf8')as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'freeze':str(output),'bytes':output.stat().st_size,'sha256':sha(output),'files':len(rows)},indent=2))
if __name__=='__main__':run()
