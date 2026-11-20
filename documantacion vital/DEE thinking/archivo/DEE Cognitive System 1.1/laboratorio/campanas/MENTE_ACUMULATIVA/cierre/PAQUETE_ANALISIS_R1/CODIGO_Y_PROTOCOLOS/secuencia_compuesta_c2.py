"""A new, bounded sequential challenge on the actual lived MAIN prefix."""
from pathlib import Path
import json,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def op(case,args):
    subprocess.run([sys.executable,'-I','-B','-X','utf8',str(HERE/'ejecutar_operacion.py'),'--caso',case,*args],check=True,cwd=ROOT)
def q(c,l,r,tool='puertas',regime='original'):return dict(contexto=c,valores=[l,r],herramienta=tool,regimen=regime)
def main():
    seal=HERE/'PROTOCOLO_C2_COMPOSICION.json'
    if seal.exists():raise FileExistsError('Never rerun a frozen executed experiment')
    jobs=[q('c1',24,33,'transaccion','revisado')for _ in range(8)]
    reserve=[q('c1',26,35,'transaccion','revisado')for _ in range(4)]
    old=[q('c1',27,35,regime='revisado'),q('c2',27,43)]
    seal.write_text(json.dumps(dict(frozen_monotonic=time.monotonic(),parent='MA_MAIN_R9 actual T211611',
      slots=8,reserve_slots=4,public_context='Same four raw channels and same material motor reader as R9. No phase bit, previous action, hidden pending phase, reference or next worker is injected.',
      law='Actual local prepare then verify_commit requires different worker and reads the prepared artifact bytes. Its task law and algorithm belong to environment, not E1.',
      jobs=jobs,reserve=reserve,return_to_old=old,
      criterion='Count prepare, completed real transactions, first actions after phase change and failures separately. A completed sequence with feedback-driven retries is not competent phase-aware selection.',
      control='Full MAIN prefix fork immediately before this block; same jobs and horizon, return omitted. No native reset or favorable snapshot import.'),indent=2)+'\n',encoding='utf8')
    op('11_FORK_C2_CONTROL',['bifurcar','MA_MAIN_R9','MA_C2_OMIT','--modalidad','DIAGNOSTIC_COPY'])
    for label,life,feedback in [('12_C2_MAIN','MA_MAIN_R9','real'),('12U_C2_OMIT','MA_C2_OMIT','omit')]:
        op(label,['mente-sesion','--vida',life,'--situaciones',json.dumps(jobs,separators=(',',':')),'--retorno',feedback])
    for label,life,feedback in [('13_C2_RESERVA','MA_MAIN_R9','real'),('13U_C2_RESERVA','MA_C2_OMIT','omit')]:
        op(label,['mente-sesion','--vida',life,'--situaciones',json.dumps(reserve,separators=(',',':')),'--retorno',feedback])
    op('14_REGRESO_ANTERIOR',['mente-sesion','--vida','MA_MAIN_R9','--situaciones',json.dumps(old,separators=(',',':'))])
if __name__=='__main__':main()
