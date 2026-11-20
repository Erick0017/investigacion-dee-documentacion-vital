"""Apertura real sobre el padre vivido, no una reconstrucción desde T0."""
from pathlib import Path
import json,subprocess,sys
HERE=Path(__file__).resolve().parent
def run(case,*argv):
    p=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(HERE/'ejecutar_operacion.py'),'--caso',case,*argv],capture_output=True,text=True,encoding='utf8');print(p.stdout,end='',flush=True)
    if p.returncode:raise RuntimeError(case+' failed; preserve reached state: '+p.stderr)
def main():
    plan=HERE/'PROTOCOLO_APERTURA_A.json'
    if plan.exists():raise FileExistsError('Opening already attempted')
    plan.write_text(json.dumps({'parent':'MA02_MAIN_5 T11196','main':'MU_MAIN','history':'Exact full fork, all own learned contents inherited rather than reacquired','initial_panel':'epsilon,gamma,beta,alfa,delta, first material uses on own fork; protected parent not probed','decoder':'Existing fixed10gate, context addressing P0, no new policy claim','next':'Native expression/selection experiments use identified diagnostic forks; no branch writes back learned fields'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    run('A01_FORK_MAIN','bifurcar','MA02_MAIN_5','MU_MAIN','--modalidad','CANDIDATE')
    run('A02_ESTADO_INICIAL','mente2-estado','--vida','MU_MAIN')
    run('A03_PRIMER_USO_CINCO','mente2-sesion','--vida','MU_MAIN','--situaciones',json.dumps([{'contexto':x}for x in['epsilon','gamma','beta','alfa','delta']]),'--detalle')
    run('A04_GUARDAR_APERTURA','guardar','--vida','MU_MAIN')
if __name__=='__main__':main()
