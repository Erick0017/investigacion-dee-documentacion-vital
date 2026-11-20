"""Passive reconstruction of the preserved MCP tool error; no SDK/Native import."""
from pathlib import Path
import datetime,hashlib,json
ROOT=Path(__file__).resolve().parent.parent
BLOCK=ROOT/'evidencia/MAIN_BLOQUE_01_R03'
OUTPUT=ROOT/'analisis/DICTAMEN_TRANSPORTE_Q1_34_R07.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def date(v):return datetime.datetime.fromisoformat(v.replace('Z','+00:00'))
def line_of(p,needle):
    return[next(i for i,line in enumerate(p.read_text('utf-8-sig').splitlines(),1)if needle in line)]
def main():
    error_file=BLOCK/'MCP_0030_action.json';intent_file=BLOCK/'MCP_0030_action.INTENT.json'
    session_file=BLOCK/'MCP_PERSISTENTE/SESSION.jsonl';bootstrap=BLOCK/'MCP_PERSISTENTE/BOOTSTRAP_1.json'
    client_file=ROOT/'control/mcp_persistente_v3.py';world_file=ROOT/'control/world_comprimido_v3_R03.py'
    decoder=ROOT/'control/run_integrated_v3_R03.py'
    raw=read(error_file);intent=read(intent_file);session=[json.loads(x)for x in session_file.read_text('utf-8-sig').splitlines()if x.strip()]
    known=[x for x in session if x.get('rpc_id')==raw['reply']['id']and x['kind']=='CALL_REPLIED']
    assert len(known)==1 and raw['status']=='TOOL_ERROR'and raw['reply']['result']['isError']is True
    assert raw['reply']['id']==intent['rpc_id']==116
    opened=next(x for x in session if x['kind']=='OPEN_INTENT')
    elapsed=(date(known[0]['utc'])-date(opened['utc'])).total_seconds()
    failing_intent=next(x for x in session if x['kind']=='CALL_INTENT'and x['rpc_id']==116)
    previous=next(x for x in session if x['kind']=='CALL_REPLIED'and x.get('rpc_id')==115)
    prior_long_reply=next(x for x in session if x['kind']=='CALL_REPLIED'and x.get('rpc_id')==113)
    prior_long_intent=next(x for x in session if x['kind']=='CALL_INTENT'and x.get('rpc_id')==114)
    prior_long_success=next(x for x in session if x['kind']=='CALL_REPLIED'and x.get('rpc_id')==114)
    closing=[x for x in session if x['kind']=='CLOSED']
    recovery=BLOCK/'RECONCILIACION34_ROOT_R01.json'
    recovered=read(recovery)if recovery.is_file()else None
    sources=[error_file,intent_file,session_file,bootstrap,client_file,world_file,decoder]
    if recovered is not None:sources.append(recovery)
    records=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'read':'complete JSON/text for this diagnosis'}for p in sources]
    record={'schema':'DEE.R07.TransportIncident34.PassiveDiagnosis.R01','inspection_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'scope':'Preserved MCP client/tool logs and static source only. No Native, MCP, HTTP, model or application call.',
      'actual_failure':{'file':str(error_file),'sha256':sha(error_file),'rpc_id':116,
        'logical_call_id':raw['logical_call_id'],'sdk_pid':raw['sdk_pid'],
        'session':raw['persistent_session'],'status':'TOOL_ERROR','jsonrpc_reply_received':True,
        'isError':True,'elapsed_seconds':raw['elapsed_seconds'],
        'error_text':raw['reply']['result']['content'][0]['text'],
        'world_command_id':'WORLD_R07_MAIN_adc933c82cc74fb0bb19_34_Q1',
        'Native_action_id':'R07_R07_MAIN_adc933c82cc74fb0bb19_34_DECISION','Native_tick_at_decision':999363},
      'deadline_check':{'opened_utc':opened['utc'],'configured_seconds':opened['seconds'],
        'tool_error_reply_utc':known[0]['utc'],'wall_derived_elapsed_seconds':elapsed,
        'wall_derived_remaining_seconds_approx':opened['seconds']-elapsed,
        'bounded_call_timeout_seconds_from_World':180,'observed_reply_seconds':raw['elapsed_seconds'],
        'session_expiry_not_observed':True,'per_call_timeout_not_observed':True,
        'note':'Remaining time is derived from UTC log stamps; actual cutoff uses monotonic time. The several-thousand-second margin rules out the configured deadline as this observed trigger.'},
      'idle_comparison':{'failed_call_idle_seconds':(date(failing_intent['utc'])-date(previous['utc'])).total_seconds(),
        'earlier_successful_idle_seconds':(date(prior_long_intent['utc'])-date(prior_long_reply['utc'])).total_seconds(),
        'earlier_success_rpc_id':114,'earlier_success_status':prior_long_success['status'],
        'fixed_short_idle_threshold_supported':False,
        'note':'An earlier longer idle interval ended in a successful reply. This does not rule out all connection faults; it fails to establish a specific idle/TTL cause.'},
      'client_state':{'last_close_utc':closing[-1]['utc']if closing else None,
        'unknown_original_request_at_close':closing[-1].get('unknown_original_request_preserved')if closing else None,
        'stdio_transport_EOF_or_invalid_protocol_observed_for_this_call':False,
        'raw_stderr_archive_available':False,
        'stderr_limit':'MCPClient hashes/counts stderr in memory; Session does not persist those counters or raw stderr. No stderr contents are reconstructed.'},
      'source_classification':{
        'client_report_path':str(client_file),'client_report_lines':line_of(client_file,"status='TOOL_ERROR'if result.get('isError')else'REPLIED'"),
        'decoder_path':str(decoder),'decoder_lines':line_of(decoder,"need(report.get('status')=='REPLIED','MCP unknown; preserve ID and stop')")if "MCP unknown; preserve ID and stop"in decoder.read_text('utf-8')else line_of(decoder,"need(report.get('status')=='REPLIED'"),
        'problem':'The client preserved a known TOOL_ERROR response. Generic BASE.decode labeled every non-REPLIED status MCP unknown, conflating tool error with unknown transport receipt.',
        'application_status':'Known tool error does not certify that the World action was not applied. Root separately reconciled the real World receipt/UUID without replay.'},
      'Root_recovery_evidence':{'path':str(recovery)if recovered is not None else None,'sha256':sha(recovery)if recovered is not None else None,
        'availability':'Full JSON read and preserved; the recovery itself was performed by Root, not by this diagnosis.',
        'Root_reported_result':'Applied Q1; idempotent cache retrieval demonstrated zero World changes, no BEGIN/observe/Native Q1 replay.'},
      'conclusions':[
        'The observed fault is an explicit Roblox internal ExecuteLuau dispatch/OnInvoke error, received as JSON-RPC result116 with isError=true.',
        'No evidence identifies expiration of the configured client session, the180-second call timeout, stdio EOF, a sandbox permission gate or a DEE engine failure as its cause.',
        'The underlying reason why the PlayServer handler response failed remains undetermined by the preserved logs.',
        'A fresh-client per-call replacement is not justified as a demonstrated TTL/idle fix. No such variant is prepared or activated.'],
      'future_minimal_correction_only':{
        'status':'PROPOSAL_NOT_APPLIED','frozen_R03_sources_unchanged':True,
        'change':'Version only the future decode/error message and structured classification. Preserve report.status, isError, exact text, raw reply SHA/path, RPC/logical-call/World/Native action IDs.',
        'known_reply_vs_effect':'Distinguish known SDK reply/tool error from uncertain application effect. Stop with the same IDs; never infer NOT_APPLIED from No OnInvoke and never automatically replay.',
        'no_change':['persistent or per-call transport policy','Native selection','reader/calendar','timing limits','physics','World state']},
      'sources':records,'Native_calls':0,'MCP_calls':0,'model_calls':0,'states_modified':False}
    if OUTPUT.exists():raise ValueError('Preserve prior diagnosis; choose a new revision')
    OUTPUT.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for item in records:assert sha(Path(item['path']))==item['sha256'],'Diagnosis source changed during reading'
    print(json.dumps({'file':str(OUTPUT),'sha256':sha(OUTPUT),'raw_error_sha256':sha(error_file),
       'elapsed_seconds':elapsed,'remaining_approx':opened['seconds']-elapsed,
       'failed_idle':record['idle_comparison']['failed_call_idle_seconds'],
       'prior_success_idle':record['idle_comparison']['earlier_successful_idle_seconds'],
       'Native_calls':0,'MCP_calls':0},ensure_ascii=False))
if __name__=='__main__':main()
