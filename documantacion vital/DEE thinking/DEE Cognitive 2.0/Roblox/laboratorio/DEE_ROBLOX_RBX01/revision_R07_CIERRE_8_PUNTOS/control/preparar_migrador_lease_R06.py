"""Generate the closed-role R06 lease transaction. Filesystem only."""
from pathlib import Path
import ast,hashlib
ROOT=Path(__file__).resolve().parents[1]
def need(v,m):
    if not v:raise ValueError(m)
def replace_function(text,name,body):
    tree=ast.parse(text);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name)
    lines=text.splitlines(keepends=True);return ''.join(lines[:node.lineno-1])+body+'\n'+''.join(lines[node.end_lineno:])
CLOSED=r'''def known_q2(root,proof):
    if root.name not in('LOAD1','LOAD2','LOAD3'):return None
    path=ROOT/'load/evidencia/CARGA3_R01/CONCILIACION_PASIVA_R06.json';report=read(path)
    need(report['status']=='THREE_Q1_REAL_ZERO_COMPLETE_EPISODES_KNOWN_Q2_HOST_REJECTION','EXACT_CLOSED_Q2_RECONCILIATION')
    row=next(x for x in report['lives']if x['profile']==root.name)
    need(row['life']==proof['life']and row['physical']==proof['physical']and row['snapshot_sha256']==proof['snapshot_sha256'],'EXACT_CURRENT_CLOSED_FAILED_FUTURE')
    receipt=safe(row['failed_official_receipt']);need(sha(receipt)==row['failed_official_sha256'],'EXACT_NO_ADMISSION_RECEIPT_BYTES')
    request=read(receipt);error=request['error'];error=read_error(error)
    need(request['status']=='failed_preserved'and error['external_execution_may_be_uncertain']is False and error['native_tick_after_attempt']==991543,'FAILED_Q2_PROVEN_ZERO_TICKS')
    need(error['detail']=='Real station query consumes exactly one environmental permit','ONE_KNOWN_HOST_STOCK_BUG_ONLY')
    m=row['own_metadata_preserved_from_failed_snapshot']
    need(m==error['failed_native_future_preserved']['operational_dependencies']['RBX01']['progress'],'EXACT_SERIALIZED_OWN_PENDING_METADATA')
    need(m['phase']=='AWAIT_ROUTE_SENSOR'and m['uncertain']is True and m['cycles']==0 and m['last_sequence']==56,'PENDING_UNCERTAINTY_MUST_STAY_PRESERVED_BY_LEASE')
    return {'reconciliation':str(path),'reconciliation_sha256':sha(path),'failed_receipt':str(receipt),'failed_receipt_sha256':sha(receipt),
      'failed_id':row['failed_q2_id'],'metadata_sha256':hashlib.sha256(CORE.canonical(m).encode()).hexdigest(),
      'no_Q2_pulses_or_ticks':True,'repair_permitted_by_this_lease':False}
def read_error(value):return json.loads(value)if isinstance(value,str)else value
def closed(root):
    value=_closed_base(root);root=Path(value['root']);known=known_q2(root,value)
    end=value['last_owner_closed']
    if end and end['final_status'].get('uncertain_external_result',False):
        need(known is not None,'UNKNOWN_EXTERNAL_FUTURE_NOT_LEASABLE')
    if known is not None:value['known_zero_q2']=known
    actor_log=Path(value['actor_log']);value['actor_log_sha256']=sha(actor_log)if actor_log.is_file()else None
    return value
'''
RECHECK=r'''def recheck_main_pair(plan):
    # The historical helper name is retained; R06 pins CURRENT manifests for
    # all six roles, including closed Q1 futures, not an invented frozen backup.
    for row in plan['roots']:
        path=safe(row['role_manifest']);need(sha(path)==row['role_manifest_sha256'],'CURRENT_ROLE_MANIFEST_CHANGED')
        manifest=read(path);need(manifest['closed_proof']==row['proof'],'MANIFEST_CURRENT_CLOSED_BOUNDARY')
        for name,entry in manifest['linked_anchors'].items():
            p=safe(entry['path']);need(sha(p)==entry['sha256'],'PRESERVED_ROLE_ANCHOR_CHANGED: '+name)
'''
STAGE=r'''def stage(a):
    need(time.time()<CORE.NEW_LAST,'PROSPECTIVE_NEW_WINDOW_ONLY')
    need(set(a.roles)==set(ROLES)and len(a.roles)==6,'ONE_ADMINISTRATIVE_RENEWAL_ALL_SIX_CLOSED_ROLES')
    output=a.output.resolve();need(not output.exists()and output.is_relative_to(ROOT/'control'),'FRESH_TRANSACTION_DIRECTORY')
    freeze=safe(a.freeze);need(sha(freeze)==a.freeze_sha256,'EXACT_18H_FREEZE');f=read(freeze)
    need(f['sealed']is True and f['native_start_epoch']==1794841620 and f['last_new_episode_epoch']==CORE.NEW_LAST and f['native_cutoff_epoch']==CORE.NEW_END,'SAME_ORIGINAL_START_FINITE_18H_WINDOW')
    ledger=safe(a.ledger);old_ledger=read(ledger);CORE.renew_ledger(old_ledger,utc())
    proofs=[closed(ROOT/'native'/role)for role in a.roles]
    need(not ledger.with_name(ledger.name+'.LOCK').exists(),'GLOBAL_BUDGET_QUIESCENT')
    expected={x['life']:x['known_zero_q2']['failed_id']for x in proofs if 'known_zero_q2'in x}
    need(set(old_ledger['intents'])==set(expected),'NO_UNEXPLAINED_INTENT')
    for proof in proofs:
        life=proof['life'];world=old_ledger['worlds'].get(life)
        if life in expected:
            need(old_ledger['intents'][life]['id']==expected[life]and world['reserved']==3740 and world['consumed']==356 and world['cycles']==0,'EXACT_FAILED_Q2_RESERVATION_PRESERVED')
        elif world:need(world['reserved']==0,'NO_UNPROVEN_PARTIAL_RESERVATION')
    pair_manifest=safe(a.main_pair)/'PAREJA_INTEGRAL_V3.json';pair=read(pair_manifest)
    previous=safe(ROOT/'control/LEASE_R05_REV3_TX/RESULTADO.json');prior=read(previous)
    main=next(x for x in proofs if Path(x['root']).name=='MAIN');bridge=next(x for x in prior['results']if x['role']=='MAIN')
    need(prior['status']=='CLOSED_LEASE_RENEWAL_COMPLETE'and prior['new_native_ticks']==0 and bridge['snapshot_before_sha256']==pair['boundary']['native_snapshot_sha256']and bridge['snapshot_after_sha256']==main['snapshot_sha256'],'P04_TO_CURRENT_ADMINISTRATIVE_SNAPSHOT_CHAIN')
    need(bridge['physical_before']==bridge['physical_after']==main['physical']and pair['boundary']['native_tick']==main['physical']['tick'],'P04_AND_CURRENT_IDENTICAL_PHYSICAL_BOUNDARY')
    linked={'P04':{'path':str(pair_manifest),'sha256':sha(pair_manifest)},'prior_lease_zero_tick':{'path':str(previous),'sha256':sha(previous)}}
    output.mkdir(parents=True);new(output/'LEDGER_ANTES.json',old_ledger);rows=[]
    for proof in proofs:
        root=Path(proof['root']);folder=output/root.name;folder.mkdir();paths=files(root);old=read(paths['scope']);host=read(paths['host'])
        need(old['sources_sha256']['rbx07_native_v3.py']==sha(paths['actor']),'CURRENT_12H_ACTOR_PIN')
        updated=CORE.renew_scope(old,f['native_sources_sha256']['rbx07_native_v3.py'],a.freeze_sha256);changed=CORE.renew_host(host)
        for key,p in paths.items():shutil.copyfile(p,folder/('OLD_'+p.name))
        card=Path(proof['root'])/'sistema/estado/vidas'/proof['life']/'VIDA.json';shutil.copyfile(card,folder/'VIDA_ANTES_STAGE.json')
        history=card.parent/'HISTORIA.jsonl'
        if history.is_file():shutil.copyfile(history,folder/'HISTORIA_ANTES_STAGE.jsonl')
        (folder/'NEW_SCOPE.json').write_bytes(json_bytes(updated));(folder/'NEW_HOST.json').write_bytes(json_bytes(changed));new(folder/'CLOSED_PREFLIGHT.json',proof)
        anchors=dict(linked)if root.name=='MAIN'else{}
        if 'known_zero_q2'in proof:
            k=proof['known_zero_q2'];anchors['failed_Q2_receipt']={'path':k['failed_receipt'],'sha256':k['failed_receipt_sha256']};anchors['closed_Q2_reconciliation']={'path':k['reconciliation'],'sha256':k['reconciliation_sha256']}
        manifest={'schema':'DEE.R07.current_closed_role_lease_descriptor.R06','closed_proof':proof,'linked_anchors':anchors,
          'complete_current_native_root':str(root),'current_root_is_not_an_immutable_rollback_backup':True,'material_rollback_tested':False,
          'scope':'Current coherent closed root remains complete in place; original snapshot/card/scope preserved. This lease changes code witnesses and dates only; pending/failure/intents are NOT repaired.'}
        manifest_path=folder/'ROLE_CURRENT_MANIFEST.json';new(manifest_path,manifest)
        cycles=old_ledger['worlds'].get(proof['life'],{}).get('cycles',0)
        rows.append({'role':root.name,'root':str(root),'life':proof['life'],'expected_cycles':cycles,'proof':proof,
          'role_manifest':str(manifest_path),'role_manifest_sha256':sha(manifest_path),
          'old_files_sha256':{k:sha(p)for k,p in paths.items()},'new_scope_sha256':sha(folder/'NEW_SCOPE.json'),'new_host_sha256':sha(folder/'NEW_HOST.json')})
    plan={'schema':'DEE.R07.closed_lease_transaction.R06','created_utc':utc(),'original_start_epoch':1794841620,'old_last_new_epoch':CORE.OLD_LAST,'old_cutoff_epoch':CORE.OLD_END,
      'new_last_new_epoch':CORE.NEW_LAST,'new_cutoff_epoch':CORE.NEW_END,'ledger':str(ledger),'ledger_before_sha256':sha(ledger),
      'freeze':str(freeze),'freeze_sha256':a.freeze_sha256,'actor_source':str(ROOT/'native/lease_R06_bundle/rbx07_native_v3.py'),
      'actor_source_sha256':f['native_sources_sha256']['rbx07_native_v3.py'],'roots':rows,'Native_calls':0,'new_ticks':0,'not_applied':True,
      'pending_intents_will_remain_literal':old_ledger['intents'],'technical_uncertainty_recovery_NOT_authorized_by_this_plan':True}
    new(output/'PLAN.json',plan);return plan
'''
def run():
    old=ROOT/'native/migrar_lease_cerrada_v3_R05_REV3.py';text=old.read_text('utf8')
    need(hashlib.sha256(old.read_bytes()).hexdigest()=='adaf248ea319308f49580137af6dcc5ba3d8742138c3b74f7b0ad89502584ce2','EXACT_PREVIOUS_MIGRATOR')
    text=text.replace('lease_core_v3_R05.py','lease_core_v3_R06.py').replace('lease_R05_bundle/','lease_R06_bundle/').replace('LEASE_APPLIED_R05.json','LEASE_APPLIED_R06.json').replace('R07_ADMIN_PROSPECTIVE_LEASE_ONLY_R05','R07_ADMIN_PROSPECTIVE_LEASE_ONLY_R06')
    text=text.replace("and cache.get('uncertain_external_result',False)is False",'')
    text=text.replace('def closed(root):','def _closed_base(root):',1)
    text=text.replace('def files(root):',CLOSED+'\ndef files(root):',1)
    text=replace_function(text,'stage',STAGE);text=replace_function(text,'recheck_main_pair',RECHECK)
    old_call="row['new_scope_sha256'],row['expected_cycles'])"
    need(text.count(old_call)==1,'EXACT_METADATA_ALLOWLIST_CALL')
    text=text.replace(old_call,"row['new_scope_sha256'],row['expected_cycles'],known_pending_sha256=row['proof'].get('known_zero_q2',{}).get('metadata_sha256'))")
    ast.parse(text);target=ROOT/'native/migrar_lease_cerrada_v3_R06.py'
    with target.open('x',encoding='utf8',newline='\n')as f:f.write(text)
    print(target,len(text.encode()),hashlib.sha256(target.read_bytes()).hexdigest())
if __name__=='__main__':run()
