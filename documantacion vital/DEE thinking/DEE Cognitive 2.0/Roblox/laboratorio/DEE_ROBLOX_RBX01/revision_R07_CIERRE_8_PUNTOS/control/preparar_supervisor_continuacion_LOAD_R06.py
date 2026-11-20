"""Filesystem-only reuse of the finite load supervisor for original Q1 futures."""
from pathlib import Path
import ast,hashlib
ROOT=Path(__file__).resolve().parents[1]
def need(v,m):
    if not v:raise ValueError(m)
def run():
    source=ROOT/'load/ejecutar_carga3_v3_R05.py';text=source.read_text('utf8')
    need(hashlib.sha256(source.read_bytes()).hexdigest()=='a566642a9465919895eb36bf96611ee9a6e061751bb0363649dbf9cbaefbfa43','EXACT_ORIGINAL_SUPERVISOR')
    text=text.replace('1794880800','1794902400').replace('1794884820','1794906420').replace('PROTOCOLO_CARGA_V3_R05.json','PROTOCOLO_CARGA_V3_R06.json').replace('worker_carga_v3_R05.py','continuar_carga_v3_R06.py')
    original="command=[sys.executable,'-I','-B',str(ROOT/'load/continuar_carga_v3_R06.py'),'--execute-root-only','--profile',spec['profile'],'--stage',str(a.stage),"
    replacement="command=[sys.executable,'-I','-B',str(ROOT/'load/continuar_carga_v3_R06.py'),'--execute-root-only','--profile',spec['profile'],'--recovery-transaction',str(a.recovery_transaction.resolve(strict=True)),"
    need(text.count(original)==1,'EXACT_ARGUMENT_ANCHOR');text=text.replace(original,replacement)
    anchor="    protocol=read(ROOT/'load/PROTOCOLO_CARGA_V3_R06.json')"
    inserted=anchor+"\n    recovery=read(a.recovery_transaction.resolve(strict=True)/'RESULTADO.json')\n    need(recovery['status']=='THREE_KNOWN_ZERO_ADMISSION_GUARDS_RECOVERED'and not recovery['remaining_intents'],'Reviewed zero-tick recovery must close before this continuation')"
    need(text.count(anchor)==1,'EXACT_RECOVERY_PREFLIGHT_ANCHOR');text=text.replace(anchor,inserted)
    anchor="p.add_argument('--ledger',type=Path,required=True);"
    need(text.count(anchor)==1,'EXACT_CLI_ANCHOR');text=text.replace(anchor,"p.add_argument('--recovery-transaction',type=Path,required=True);"+anchor)
    text=text.replace('before23:45UTCNov16','before05:45UTCNov17').replace('The one R07 global ledger','The one R07 global ledger, original Q1 retained')
    ast.parse(text);target=ROOT/'load/ejecutar_continuacion_carga3_v3_R06.py'
    with target.open('x',encoding='utf8',newline='\n')as f:f.write(text)
    print(target,hashlib.sha256(target.read_bytes()).hexdigest())
if __name__=='__main__':run()
