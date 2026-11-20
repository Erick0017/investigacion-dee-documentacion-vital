"""Register exact old API/PI05 call-chain finding, no Native execution."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1];S=P/'estados/candidato/sistema'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 file=P/'ensayos/PI07_PANEL_INTERCALADO_R01_FIplus.json';row=json.loads(file.read_text('utf-8-sig'));result=json.loads(row['result']);value=result['result']['rows'][0]
 body=value['original_result']['native_trial'];before={str(file):sha(file)}
 sources={name:{'path':str(S/'capacidades'/name),'sha256':sha(S/'capacidades'/name)}for name in('acceso_integrado_eci01.py','acceso_eci01.py','acciones_nativas_apd04.py','pi05_transito_causal_R01.py')}
 proof={'schema':'DEE.PI07.old_FI_API_callchain.passive_finding.R01','Native_executed':False,'primary':{'path':str(file),'sha256':sha(file)},'actual_failed_old_use':{'before_tick':result['before_tick'],'after_tick':result['after_tick'],'query_tick':value['query_tick'],'early_tick':value['early_tick'],'early_physical_choice':value['early_physical_choice'],'early_observation':value['early_observation'],'old_q6_choice':value['old_q6_choice'],'old_q6_reader':body['reader'],'unique_direct_requests':len({r['id']for r in value['all_material_receipts']})},'source_contracts':sources,'exact_calls':{'legacy':'acceso_integrado.dispatch -> acceso_eci01.dispatch -> acceso_eci01.balance -> acciones_nativas_apd04.balance -> percepcion_cruda_fi01.frame','PI05_normal':'pi05_transito_causal_R01._fiplus(captura=normal) -> acceso_eci01.balance -> same actions/frame','R03_environment':'TC identity sensor/query/q4read/holdq6/fixed actuator@q7 -> fixed FI startq136 -> PI05._fiplus(normal)'},'explanation':'PI05 normal does not replace the old FI body or either reader. R03 scores lateq6 whereas the historical panel scores earlyq4; in the preserved failed panel BOTH were actual-1, so decoder-window difference does not explain away this regression. R03 additionally prepares material selector/actuator history and a distinct FI access calendar. A new explicit generic access layer may investigate that difference; it is not evidence that the old198tick API retained its contract.','new_access_reference':{'source':'codigo/pi07_acceso_FI_regulado_R01.py','protocol':'codigo/PROTOCOLO_PI07_ACCESO_FI_R01.json','Native_status':'NOT_EXECUTED_BY_THIS_REGISTRATION'},'sources_unchanged_during_read':all(sha(Path(p))==h for p,h in before.items())}
 out=P/'control/CONTRASTE_API_FI_PI07_PASIVO_R01.json'
 with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(out),'sha256':sha(out),'Native_executed':False}))
if __name__=='__main__':main()
