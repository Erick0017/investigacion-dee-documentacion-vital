"""Primera incorporación operativa de la candidata real R04, sin reiniciarla."""
import hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EV=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA_R02'
def run(case,*command):
    a=[sys.executable,'-I','-B','-X','utf8',str(HERE/'ejecutar_operacion.py'),'--caso',case,*map(str,command)]
    p=subprocess.run(a,text=True,encoding='utf-8',capture_output=True)
    print(p.stdout,end='',flush=True)
    if p.returncode:print(p.stderr,flush=True);raise RuntimeError(case+' failed; preserve reached state, no rollback')
def compact(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def main():
    protocol={'main':'MA02_MAIN','exact_source':'MA02_R04_MAIN T1414','not_historical_E1_continuity':True,'fixed_before_use':['import full compatible state','admit MA02 service metadata only','interleave four prior contents','work gamma +/beta - on literal actual local service','prepare then verify transaction using acquired gamma/beta','return to old associations'],'reader':'fixed eight gate pureZ atphase+4','actual_return':'fixed count of read-back worker output bytes, symmetric radial pulses on actual actuator posture, not correct action; no learned-utility claim','frozen_worker_eligibility':'existing EO02 actual worker, capacity_credit0, observations in request','actuator_and_omit_controls':'fork exact MAIN immediately before jobs; future same job list'}
    dest=HERE/'PROTOCOLO_OPERACION_01.json'
    if dest.exists():raise FileExistsError(dest)
    dest.write_text(json.dumps(protocol,ensure_ascii=False,indent=2),encoding='utf-8')
    prefix=EV/'entrada_comun/MA02_R04_MAIN.T1414.deetsnap.gz'
    run('01_IMPORTAR_MAIN','importar-estado',prefix,'MA02_MAIN','--perfil','fisica_directa','--sha256',hashlib.sha256(prefix.read_bytes()).hexdigest())
    run('02_ADMITIR_MAIN','mente2-admitir','--vida','MA02_MAIN')
    run('03_ESTADO_MAIN','mente2-estado','--vida','MA02_MAIN')
    panel=[{'contexto':x}for x in['gamma','delta','alfa','beta']]
    run('04_PANEL_HEREDADO_MAIN','mente2-sesion','--vida','MA02_MAIN','--situaciones',compact(panel),'--detalle')
    run('05_FORK_NULLED','bifurcar','MA02_MAIN','MA02_JOBS_NULLED','--modalidad','DIAGNOSTIC_COPY')
    run('06_FORK_OMIT','bifurcar','MA02_MAIN','MA02_JOBS_OMIT','--modalidad','DIAGNOSTIC_COPY')
    jobs=[{'contexto':'gamma','modo':'trabajo','dominio':'trabajadores','valores':[12,12]},{'contexto':'beta','modo':'trabajo','dominio':'trabajadores','valores':[8,12]},{'contexto':'gamma','modo':'trabajo','dominio':'transaccion','valores':[17,17]},{'contexto':'beta','modo':'trabajo','dominio':'transaccion','valores':[17,17]}]
    run('07_JOBS_MAIN','mente2-sesion','--vida','MA02_MAIN','--situaciones',compact(jobs),'--detalle')
    run('08_JOBS_NULLED','mente2-sesion','--vida','MA02_JOBS_NULLED','--situaciones',compact(jobs),'--actuador','nulled','--detalle')
    run('09_JOBS_OMIT','mente2-sesion','--vida','MA02_JOBS_OMIT','--situaciones',compact(jobs),'--retorno','omit','--detalle')
    run('10_POSTJOBS_ANTERIORES_MAIN','mente2-sesion','--vida','MA02_MAIN','--situaciones',compact([{'contexto':x}for x in['alfa','gamma','beta','delta']]),'--detalle')
    run('11_GUARDAR_MAIN','guardar','--vida','MA02_MAIN')
    run('12_CONTINUAR_OTRO_PROCESO_MAIN','mente2-sesion','--vida','MA02_MAIN','--situaciones',compact([{'contexto':x}for x in['delta','beta','alfa','gamma']]),'--detalle')
if __name__=='__main__':main()
