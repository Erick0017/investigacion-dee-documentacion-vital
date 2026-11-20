"""A fixed common-context/real-worker regression and a bounded social contrast."""
from pathlib import Path
import json,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def op(case,args):subprocess.run([sys.executable,'-I','-B','-X','utf8',str(HERE/'ejecutar_operacion.py'),'--caso',case,*args],check=True,cwd=ROOT)
def main():
    seal=HERE/'PROTOCOLO_RESERVA_FINAL.json'
    if seal.exists():raise FileExistsError('Frozen protocol already present')
    values=[(15,25),(16,27),(25,35),(26,37),(27,37),(28,39),(29,39),(30,41)]
    jobs=[dict(contexto='c3',valores=list(p),herramienta='trabajadores'if i in(2,3)else'puertas')for i,p in enumerate(values)]
    jobs[4]['privada_B']=12;jobs[5]['privada_B']=74
    no_B=[{k:v for k,v in q.items()if k!='privada_B'}for q in jobs]
    seal.write_text(json.dumps(dict(frozen_monotonic=time.monotonic(),parent='MA_MAIN_R9 T222559 actual',
       public_inputs_fixed_before_results=jobs,control=no_B,
       criterion='First motor use at each new current situation, actual worker bytes, first return to context3, before/after acquired supports; social difference only if native formed messages and a subsequent difference are observed.',
       scope='C3 boundary/+1 uses are not retention of all four policies. Two new private B raw observations use the inherited fixed channel, not desired messages. No social valve or host route selection.',
       stopping='Exactly8 opportunities in each full-prefix branch; no extending until success.'),indent=2)+'\n',encoding='utf8')
    op('15_FORK_FINAL_NO_B',['bifurcar','MA_MAIN_R9','MA_FINAL_NO_B','--modalidad','DIAGNOSTIC_COPY'])
    op('16_RESERVA_FINAL_MAIN',['mente-sesion','--vida','MA_MAIN_R9','--situaciones',json.dumps(jobs,separators=(',',':'))])
    op('16U_RESERVA_FINAL_NO_B',['mente-sesion','--vida','MA_FINAL_NO_B','--situaciones',json.dumps(no_B,separators=(',',':'))])
    op('17_GUARDAR_MAIN',['guardar','--vida','MA_MAIN_R9'])
    op('18_RECARGAR_MAIN',['mente-estado','--vida','MA_MAIN_R9'])
if __name__=='__main__':main()
