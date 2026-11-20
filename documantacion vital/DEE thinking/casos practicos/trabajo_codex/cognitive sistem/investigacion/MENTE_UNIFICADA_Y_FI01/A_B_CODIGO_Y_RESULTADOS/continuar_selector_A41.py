"""Continuar futuroreal tras rechazo preactuación del instrumento A33.
No se repite ninguna herramienta: Popen fue rechazado antes de ejecutarse.
"""
import json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from integrar_selector_A27 import mu,panel
from acumulacion_A05 import run
def main():
    p=HERE/'PROTOCOLO_CONTINUAR_A41.json'
    if p.exists():raise FileExistsError(p)
    p.write_text(json.dumps({'reason':'A33 exact-worker argv missing in existing auditfence allowlist fornewcommand. Nativequery wasexecuted, subprocess deniedbeforelaunch, Store preservedfutureT14892. No realtoolaction existed toretry.','correction':'Admit sameexisting exact worker argv forunificada-sesion explicitjobs; fence unchangedforothercommands/processes/network.','main':'Continue T14892, never rewind','control':'SameprefixU getsone genericqueryto match failedpreactionmaterialdose, then two omittedreturnjobs andagematch','criteria':'OriginalA27frozenreader/law unchanged. InstrumentalerrorA33 retained, notcognitivenegative.','no_hidden_retry':True},ensure_ascii=False,indent=2),encoding='utf8')
    mu('A41_U_IGUALAR_CONSULTA_PREACTUACION','MU_SELECTOR_RETURN_U',[{'modo':'usar'}])
    r=mu('A42_MAIN_DOS_CONSECUENCIAS','MU_MAIN',[{'modo':'trabajo','dominio':'trabajadores','valores':[7,13]}]*2)
    mu('A43_U_ACCIONES_RETORNO_OMITIDO','MU_SELECTOR_RETURN_U',[{'modo':'trabajo','dominio':'trabajadores','valores':[7,13]}]*2,feedback='omit')
    run('A44_U_IGUALAR_EDAD','continuar','--vida','MU_SELECTOR_RETURN_U','--hasta',str(r['INSTRUMENTO']['tick']))
    mu('A45_MAIN_RESERVAS_UTILES','MU_MAIN',[{'modo':'trabajo','dominio':'trabajadores','valores':v}for v in[[9,15],[6,17],[11,14]]])
    mu('A46_U_RESERVAS_UTILES','MU_SELECTOR_RETURN_U',[{'modo':'trabajo','dominio':'trabajadores','valores':v}for v in[[9,15],[6,17],[11,14]]],feedback='omit')
    panel('A47_MAIN_RETENCION_SEIS','MU_MAIN')
    run('A48_GUARDAR_MAIN_LOCAL','guardar','--vida','MU_MAIN')
    mu('A49_MAIN_CONTINUAR_OTRO_PROCESO','MU_MAIN',[{'modo':'usar'}])
if __name__=='__main__':main()
