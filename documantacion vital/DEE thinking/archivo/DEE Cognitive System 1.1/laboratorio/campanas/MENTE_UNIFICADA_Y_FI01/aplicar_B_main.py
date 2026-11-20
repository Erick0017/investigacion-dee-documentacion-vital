"""Prospective same-MAIN extension; no learnt state is imported from B controls.

All calls go through the existing gestor in separate processes. The operator's
context and stage selection remain explicit P0, not an autonomous planner.
"""
from pathlib import Path
import gzip,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01'
def run(case,*argv):
    p=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(HERE/'ejecutar_operacion.py'),'--fase','B','--caso',case,*argv],capture_output=True,text=True,encoding='utf8')
    print(p.stdout,end='',flush=True)
    if p.returncode:raise RuntimeError(case+' recorded its reached state/error; no implicit retry or rewind: '+p.stderr)
    return json.loads(gzip.decompress((EV/(case+'.json.gz')).read_bytes()))['result']
def mu(case,rows):return run(case,'unificada-sesion','--vida','MU_MAIN','--situaciones',json.dumps(rows),'--retorno','omit','--detalle')
def panel(case):return run(case,'mente2-sesion','--vida','MU_MAIN','--situaciones',json.dumps([{'contexto':k}for k in['alfa','beta','gamma','delta','epsilon','zeta']]),'--detalle')
def main():
    protocol=HERE/'PROTOCOLO_APLICACION_B_MAIN_R1.json'
    if protocol.exists():raise FileExistsError('Already frozen/executed protocol; examine recorded progress before a new explicit revision')
    protocol.write_text(json.dumps({'revision':'B.MAIN.APPLICATION.R1','parent':'MU_MAIN exact A-cut T16634, no reset or diagnostic transplant',
      'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'P0_extension':'Four vacant legal inactive SEM4 stops; existing two identical stops retained; transient raw current S and fixed six actuator reader.',
      'ordered_operations':['prepare_current','six old first uses','nineteen explicit A contact experiences','new raw values11/29/13/32','three two-request transaction sequences','six old uses','save'],
      'curriculum':'Exactly19 A contacts at next odd391 phases via existing native interfaces. Never adjust lesson count to force a target field.',
      'reserves':[{'contexto':'gamma','valores':[21,4]},{'contexto':'epsilon','valores':[6,22]},{'contexto':'zeta','valores':[17,5]}],
      'reader':'All6fixed direction/position classes, q+6; no expected sign or token argument.',
      'chain':'Explicit first operator request supplies a public context, acquired memory physically selects real worker. Separate next request senses actual prepared file bytes as identity raw scalar, same acquired relative reference selects second worker. Exact external artifact persists across process boundary.',
      'not_claimed':'This is prepared assisted environmental composition, not learned context/bank routing or an autonomous multistage planner. No threshold/action/sign returned by host.',
      'failure_policy':'Preserve all adverse outputs/reached snapshots; no silent retry, no reteaching old contents, no branch replacement.'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    run('B_MAIN_01_SENSOR_PREPARADO','unificada-preparar-dato','--vida','MU_MAIN')
    panel('B_MAIN_02_SEIS_ANTES_CURRICULO')
    mu('B_MAIN_03_DIECINUEVE_EXPERIENCIAS',[{'modo':'experiencia','lado':'A'}for _ in range(19)])
    mu('B_MAIN_04_MAGNITUD_RESERVADA',[{'modo':'dato','valor':v}for v in[11,29,13,32]])
    for j,(context,values)in enumerate([('gamma',[21,4]),('epsilon',[6,22]),('zeta',[17,5])],1):
        mu('B_MAIN_05_CADENA_'+str(j)+'_INICIO',[{'modo':'cadena-iniciar','contexto':context,'valores':values}])
        run('B_MAIN_05_CADENA_'+str(j)+'_GUARDAR','guardar','--vida','MU_MAIN')
        mu('B_MAIN_05_CADENA_'+str(j)+'_FIN',[{'modo':'cadena-finalizar'}])
    panel('B_MAIN_06_SEIS_TRAS_CADENAS')
    run('B_MAIN_07_GUARDAR','guardar','--vida','MU_MAIN')
if __name__=='__main__':main()
