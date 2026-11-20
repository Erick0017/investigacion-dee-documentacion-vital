"""Fixed operational preflight through existing gestor, never an actor or policy."""
import argparse,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
LIFE='MU_MAIN_FASE_R3'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['teach','use'],required=True);a=ap.parse_args()
    raw=[0]*128;raw[0]=19;raw[4]=2
    memory=[{'modo':'memoria','contexto':c}for c in('alfa','beta','gamma','delta','epsilon','zeta')]
    jobs=[('R3_01_ESTADO',['unificada-estado','--vida',LIFE]),('R3_02_UNICA_EXPERIENCIA_B',['unificada-sesion','--vida',LIFE,'--retorno','omit','--situaciones',json.dumps([{'modo':'experiencia','lado':'B'}])]),('R3_03_PROTECCION_P0',['unificada-proteger-fase','--vida',LIFE])]
    if a.phase=='use':
        def session(case,rows):return(case,['unificada-sesion','--vida',LIFE,'--retorno','omit','--situaciones',json.dumps(rows)])
        jobs=[session('R3_04_SEIS_ANTES',memory),session('R3_05_DATO13',[{'modo':'dato','valor':13}]),session('R3_06_DATO32',[{'modo':'dato','valor':32}]),session('R3_07_RAW128_INDEX4',[{'modo':'crudos','componentes':raw}]),session('R3_08_CADENA_PREPARAR',[{'modo':'cadena-iniciar','contexto':'gamma','valores':[29,4]}]),('R3_09_GUARDAR_PENDIENTE',['guardar','--vida',LIFE]),session('R3_10_CADENA_FINALIZAR',[{'modo':'cadena-finalizar'}]),session('R3_11_SEIS_DESPUES',memory),('R3_12_GUARDAR_CORTE',['guardar','--vida',LIFE]),('R3_13_ESTADO_CORTE',['unificada-estado','--vida',LIFE])]
    for case,args in jobs:
        command=[sys.executable,'-I','-B','-X','utf8',str(HERE/'ejecutar_operacion.py'),'--fase','B','--caso',case,'--limite','300',*args]
        result=subprocess.run(command,check=False)
        if result.returncode:raise SystemExit(result.returncode)
if __name__=='__main__':main()
