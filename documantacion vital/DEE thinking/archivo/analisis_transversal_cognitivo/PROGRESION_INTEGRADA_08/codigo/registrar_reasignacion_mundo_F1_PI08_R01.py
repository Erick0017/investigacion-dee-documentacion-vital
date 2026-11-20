"""Prospective reuse of ONE uncreated F1 cut slot; original limits unchanged."""
from pathlib import Path
import hashlib, json, os
from datetime import datetime, timezone
P=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
f=P/'control/PI08_F1_CUT_R03.json';d=read(f)
if sha(f)!='5504a23c179de27379f1a3a21c6fcc618fe9828d8d45688035038a5fa8ed0a51' or not d['closed'] or d['status']!='STOPPED_PRESERVED' or d['new_Native_ticks']!=378:
    raise ValueError('Actual closed failed F1 attempt must precede reassignment')
attempt=read(P/'ensayos/PI08_F1_CUT_R03_OP4.json');error=json.loads(attempt['error'])
diagnostic=error['failed_native_future_preserved']['operational_dependencies']['PI08_F1']['diagnostic']
if error['detail']!='Identity fork or original parent differs in Native metadata/phase/causal content; F1 stops' or diagnostic['fork_count_seen']!=1:
    raise ValueError('Do not infer created forks from a truncated completed-row counter')
reg=P/'REGISTRO_CAMPANA.json';before=reg.read_bytes();v=json.loads(before)
if 'world_allocation_revision_after_F1' in v:raise ValueError('Preserve original allocation revision')
record={'schema':'DEE.PI08.prospective_unspent_world_reassignment.v1','recorded_utc':datetime.now(timezone.utc).isoformat(),
        'fixed_world_limit':10,'fixed_Native_limit':150000,'limits_not_increased_or_reset':True,
        'F1_imported_worlds':1,'F1_identity_forks_created':1,'F1_raw_cut_forks_created':0,
        'runner_completed_row_counter_underreported_forks':True,'actual_failed_handler_proof':{'path':str(P/'ensayos/PI08_F1_CUT_R03_OP4.json'),'sha256':sha(P/'ensayos/PI08_F1_CUT_R03_OP4.json')},
        'uncreated_cut_slot_reassigned_to':'One fresh complete A861426 diagnostic RP panel12, same explicit FI route/actual arithmetic-result binding; no C2C and no main mutation.',
        'A_control_max_Native_ticks':8684,
        'actual_or_reserved_world_scopes':{'A_consolidation':1,'B_four_arms':4,'B_conservation':1,'F1_import_and_identity':2,'C_one':1,'A_current_RP_control':1},
        'conditional_existing_NONE_future':'Only if A arithmetic6+7 yields13 and subsequent actual13−5 yields8, run same panel prefix on the existing closed NONE875451 world, after preserving its complete prefix; no new world, no B criterion change. Otherwise omit as unnecessary.',
        'purpose':'Separate current baseline availability and reproduction from attribution of B arithmetic failure. No new F1 Native retry and no loosening of its sham check.',
        'Native_ticks_for_registration':0,'DEE_imports':0}
v['world_allocation_revision_after_F1']=record
out=P/'control/REASIGNACION_MUNDO_F1_A_CONTROL_PI08_R01.json'
with out.open('x',encoding='utf8')as s:json.dump(record,s,ensure_ascii=False,indent=2);s.write('\n')
if reg.read_bytes()!=before:raise ValueError('Concurrent campaign registry change')
tmp=reg.with_name(reg.name+'.ALLOCATION_WRITING')
with tmp.open('xb')as s:s.write((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8'));s.flush();os.fsync(s.fileno())
os.replace(tmp,reg)
print(json.dumps({'proof':str(out),'sha256':sha(out),'world_limit_unchanged':10,'Native_inputs':0}))
