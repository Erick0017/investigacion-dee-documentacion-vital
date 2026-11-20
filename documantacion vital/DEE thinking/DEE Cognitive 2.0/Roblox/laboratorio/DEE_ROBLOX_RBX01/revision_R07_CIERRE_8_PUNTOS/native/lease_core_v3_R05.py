"""Pure lease transformations. No Native imports, files or clocks on import."""
import copy,hashlib,json
KEY='DEE.Cognitive.RBX01.async_native.INTEGRAL.V3.R01'
CODE='DEE.Cognitive.RBX01.CODE_SCOPE_INTEGRAL_V3'
SYSTEM='DEE.Cognitive.System.1.1.life.v1'
OLD_LAST=1794859200;OLD_END=1794863220;NEW_LAST=1794880800;NEW_END=1794884820
def need(v,m):
    if not v:raise ValueError(m)
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def code_scope(c,scope_sha):
    return {'schema':'DEE.RBX01.CODE_SCOPE_INTEGRAL_V3','life_id':c['life_id'],'scope_sha256':scope_sha,
      'code_scope_manifest_sha256':c['code_scope_manifest_sha256'],'sources_sha256':c['sources_sha256'],
      'feedback_arm':c['feedback_arm'],'teacher_mode':c['teacher_mode'],'input_codec':c['input_codec'],
      'max_raw_support':c['max_raw_support'],'sensor_codec':c['sensor_codec'],'q2_sensor_codec':c['q2_sensor_codec'],
      'q2_sensor_arm':c['q2_sensor_arm'],'parent_completed_opportunities':28,'source_tick':c['source_tick'],
      'source_snapshot_sha256':c['source_snapshot_sha256']}
def renew_scope(old,actor_sha,freeze_sha):
    need(old['native_cutoff_utc_epoch']==OLD_END and old['last_new_cycle_utc_epoch']==OLD_LAST,'EXACT_OLD_LEASE_REQUIRED')
    new=copy.deepcopy(old);new['native_cutoff_utc_epoch']=NEW_END;new['last_new_cycle_utc_epoch']=NEW_LAST
    new['code_scope_manifest_sha256']=freeze_sha;new['sources_sha256']['rbx07_native_v3.py']=actor_sha
    return new
def renew_host(old):
    need(old['native_cutoff_utc_epoch']==OLD_END,'EXACT_OLD_HOST_LEASE_REQUIRED')
    new=copy.deepcopy(old);new['native_cutoff_utc_epoch']=NEW_END;return new
def metadata_after(old_entries,old_scope,old_sha,new_scope,new_sha,expected_cycles):
    new=copy.deepcopy(old_entries)
    if KEY not in old_entries:
        need(expected_cycles==0 and CODE not in old_entries,'NO_NATIVE_EPOCH_MAY_BE_INVENTED')
        return new,{'kind':'NO_NATIVE_KEY_YET','cycles':0,'Native_metadata_changed':False}
    m=json.loads(old_entries[KEY]);old_code=code_scope(old_scope,old_sha)
    need(m.get('code_scope')==old_code and old_entries.get(CODE)==canonical(old_code),'EXACT_OLD_NATIVE_WITNESSES')
    need(m.get('phase')=='IDLE'and m.get('pending')is None and m.get('uncertain')is False,'NO_PENDING_OR_UNCERTAIN_FUTURE')
    need(type(m.get('cycles'))is int and m['cycles']==expected_cycles,'ACTUAL_CYCLE_COUNT_NO_RESET')
    before=copy.deepcopy(m);m['code_scope']=code_scope(new_scope,new_sha)
    need({k:v for k,v in before.items()if k!='code_scope'}=={k:v for k,v in m.items()if k!='code_scope'},'ONLY_ADMINISTRATIVE_WITNESS_MAY_CHANGE')
    new[KEY]=canonical(m);new[CODE]=canonical(m['code_scope'])
    need({k:v for k,v in old_entries.items()if k not in(KEY,CODE)}=={k:v for k,v in new.items()if k not in(KEY,CODE)},'ANCESTORS_AND_OTHER_MEMORY_LITERAL')
    return new,{'kind':'OWN_TECHNICAL_WITNESS_ONLY','cycles':m['cycles'],'last_sequence':m.get('last_sequence'),'session_id':m.get('session_id'),
      'log_count':m.get('log_count'),'log_chain_sha256':m.get('log_chain_sha256'),'all_other_m_fields_equal':True,'all_other_metadata_entries_equal':True}
def renew_ledger(old,utc):
    need(old.get('limit')==160000 and old.get('max_worlds')==6 and not old.get('intents'),'SAME_QUIESCENT_GLOBAL_BUDGET')
    need(all(w.get('reserved')==0 for w in old['worlds'].values()),'NO_PARTIAL_CYCLE_RESERVATION')
    need(old.get('last_new_episode_epoch')==OLD_LAST and old.get('cutoff_epoch')==OLD_END,'EXACT_OLD_LEDGER_LEASE')
    new=copy.deepcopy(old);new['last_new_episode_epoch']=NEW_LAST;new['cutoff_epoch']=NEW_END
    new['lease_history']=[*old.get('lease_history',[]),{'utc':utc,'original_start_epoch':1794841620,'old_last_new_epoch':OLD_LAST,'old_hard_finish_epoch':OLD_END,
      'new_last_new_epoch':NEW_LAST,'new_hard_finish_epoch':NEW_END,'consumed_unchanged':old['consumed'],'no_clock_or_counter_reset':True}]
    keys=('schema','limit','max_worlds','consumed','worlds','intents','last_completed','protected_load_lives','protected_load_initial_slots','max_ticks_per_cycle')
    need(all(old.get(k)==new.get(k)for k in keys),'BUDGET_ACCOUNTING_LITERAL')
    return new
