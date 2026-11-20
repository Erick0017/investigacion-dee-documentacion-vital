"""Filesystem-only prospective PILOT/load windows; no execution or reset."""
from pathlib import Path
import ast,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
    old=ROOT/'prototipo/NATIVE_LIMPIO_R07/ejecutar_piloto_R07_preparado_R05.py';target=old.with_name('ejecutar_piloto_R07_preparado_R06.py')
    text=old.read_text('utf8').replace('1794880800','1794902400').replace('1794884820','1794906420')
    text=text.replace('native/owner_support_v3_R05.py','native/owner_support_v3_R06.py').replace('control/mcp_persistente_v3.py','control/mcp_persistente_v3_R06.py')
    text=text.replace('1536*1024**2','3584*1024**2').replace('Need1.5GiB','Need3.5GiB').replace('after02:00UTCNov17','after08:00UTCNov17')
    ast.parse(text)
    with target.open('x',encoding='utf8',newline='\n')as f:f.write(text)
    source=ROOT/'load/PROTOCOLO_CARGA_V3_R05.json';protocol=json.loads(source.read_text('utf-8-sig'))
    protocol.update(schema='DEE.R07.three_owner_focal_load.R06',last_new_episode_epoch=1794902400,hard_finish_epoch=1794906420,
      latest_batch_start_epoch=1794894300,latest_GO_epoch=1794894900)
    protocol['recovery_contract']={'original_batch':'load/evidencia/CARGA3_R01','original_failed_Q2_remains_preserved':True,
      'first_continued_phase':'query_sensor','Q1_replay_forbidden':True,'stock_rule':'decrement exactly once iff actual Native ASK; carry stock across episodes',
      'technical_flag_recovery_requires_separate_reviewed_zero_tick_transaction':True,'minimum_free_host_bytes':3758096384,
      'three_lives_three_episodes_is_target_not_an_observed_result':True}
    path=ROOT/'load/PROTOCOLO_CARGA_V3_R06.json'
    with path.open('x',encoding='utf8')as f:json.dump(protocol,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'PILOT':{'path':str(target),'sha256':sha(target)},'load_protocol':{'path':str(path),'sha256':sha(path)},
      'Native_MCP_model_calls':0,'PILOT_memory_guard_tightened_to_Root_3_5GiB':True},indent=2))
if __name__=='__main__':run()
