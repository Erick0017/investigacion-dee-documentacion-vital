"""Contraste posterior al fallo: no cambia criterios ni repara ramas adversas."""
import gzip,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from acumulacion_A05 import run,ses
def main():
    here=Path(__file__).resolve().parent;ev=here.parents[2]/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01'
    p=here/'PROTOCOLO_CONTRASTE_A22.json'
    if p.exists():raise FileExistsError(p)
    p.write_text(json.dumps({'purpose':'A11_U pierde respuestas despuésdeconsulta zeta noadquirida. Examinar anteriores antesdeesa consulta, rama desdeexactoT11534preenseñanza, sin rebobinarMAIN niUadverso.','parent':'MU_6_U.T11534.4c1e35998f70.deetsnap.gz','age':'A20 reached11594; correctedJSON afterA21 invalidargv(no native evaluation)','reader':'Same12gates','contexts':['alfa','gamma','epsilon','beta','delta'],'next':'MU_MAIN pending actualartifact ->gamma+worker same [7,13] in another process; then six retention'},ensure_ascii=False,indent=2),encoding='utf8')
    ses('A22_U_ANTERIORES_PRIMERO_CORREGIDO','MU_6_U_OLD_FIRST',[{'contexto':x}for x in['alfa','gamma','epsilon','beta','delta']])
    ses('A23_MAIN_CONTINUAR_PENDIENTE','MU_MAIN',[{'contexto':'gamma','modo':'trabajo','dominio':'transaccion','valores':[7,13]}])
    ses('A24_MAIN_REUSO_TRAS_COMMIT','MU_MAIN',[{'contexto':x}for x in['beta','epsilon','zeta','alfa','gamma','delta']])
if __name__=='__main__':main()
