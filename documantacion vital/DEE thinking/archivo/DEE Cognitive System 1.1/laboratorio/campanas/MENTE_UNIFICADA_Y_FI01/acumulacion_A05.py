"""Acumulación de una sexta asociación en la misma vida; panel/lector prospectivos.
No equivale a seis estrategias ni selección autónoma de contexto.
"""
from pathlib import Path
import json,subprocess,sys,gzip
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01'
def run(case,*argv):
    p=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(HERE/'ejecutar_operacion.py'),'--caso',case,*argv],capture_output=True,text=True,encoding='utf8')
    print(p.stdout,end='',flush=True)
    if p.returncode:raise RuntimeError(case+' failed; keep reached state: '+p.stderr)
    return json.loads(gzip.decompress((EV/(case+'.json.gz')).read_bytes()))['result']
def ses(case,life,rows):return run(case,'mente2-sesion','--vida',life,'--situaciones',json.dumps(rows),'--detalle')
def panel(case,life):return ses(case,life,[{'contexto':k}for k in['zeta','alfa','gamma','epsilon','beta','delta']])
def main():
    p=HERE/'PROTOCOLO_ACUMULACION_A05.json'
    if p.exists():raise FileExistsError('Protocol already executed or reserved')
    p.write_text(json.dumps({'parent':'MU_MAIN own T11531, all five used before this extension','new_context':'zeta fixed diagonal(-1,-1,0)','reader':'Twelve fixed SEM1 PUREZ gates, extra pair admitted only in explicitly extended lives; no target/token argument to decoder','assistance':'Six zero-load state0 SEM4 legal anatomical inputs, then explicit teaching. Context choice remains operator P0. No sixth policy claim.','arms':'MAIN new positive; U same extended prefix without lesson; H same prefix opposite lesson; ages matched to lesson end before first query','first_panel':['zeta','alfa','gamma','epsilon','beta','delta'],'expected_old_for_auditor_only':{'alfa':-1,'beta':1,'gamma':1,'delta':-1,'epsilon':-1},'revision':'MAIN beta explicit negative, then all six before new teaching','scope':'retention, additional association, selective revision; not new NSM meanings or acquired access strategy'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    run('A05_EXTENSION_ZETA','mente2-extender','--vida','MU_MAIN','--contexto','zeta')
    run('A06_FORK_SIN_ADQUISICION','bifurcar','MU_MAIN','MU_6_U','--modalidad','DIAGNOSTIC_COPY')
    run('A07_FORK_HISTORIA_OPUESTA','bifurcar','MU_MAIN','MU_6_H','--modalidad','DIAGNOSTIC_COPY')
    taught=ses('A08_ADQUIRIR_ZETA','MU_MAIN',[{'contexto':'zeta','modo':'ensenar','senal':1}])
    end=taught['INSTRUMENTO']['tick']
    run('A09_U_IGUALAR_EDAD','continuar','--vida','MU_6_U','--hasta',str(end))
    ses('A10_H_ADQUIRIR_OPUESTO','MU_6_H',[{'contexto':'zeta','modo':'ensenar','senal':-1}])
    panel('A11_U_PRIMER_PANEL','MU_6_U');panel('A12_H_PRIMER_PANEL','MU_6_H');panel('A13_MAIN_PRIMER_PANEL','MU_MAIN')
    ses('A14_REVISION_BETA','MU_MAIN',[{'contexto':'beta','modo':'revisar','senal':-1}])
    panel('A15_MAIN_RETENCION_TRAS_REVISION','MU_MAIN')
    ses('A16_TRABAJOS_Y_RETORNO','MU_MAIN',[{'contexto':'gamma','modo':'trabajo','dominio':'transaccion','valores':[7,13]},{'contexto':'delta','modo':'trabajo','dominio':'transaccion','valores':[7,13]}])
    panel('A17_PANEL_TRAS_TRABAJOS','MU_MAIN')
    run('A18_GUARDAR_ACUMULACION','guardar','--vida','MU_MAIN')
if __name__=='__main__':main()
