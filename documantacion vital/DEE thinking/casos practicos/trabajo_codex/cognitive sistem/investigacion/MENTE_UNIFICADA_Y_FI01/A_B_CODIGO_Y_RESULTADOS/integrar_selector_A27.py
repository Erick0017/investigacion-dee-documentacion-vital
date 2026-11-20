"""Integración física del selector en la vida acumulativa, no suma de auxiliares."""
import json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from acumulacion_A05 import run,ses
def mu(case,life,rows,feedback='real',actuator='closed'):
    return run(case,'unificada-sesion','--vida',life,'--situaciones',json.dumps(rows),'--retorno',feedback,'--actuador',actuator,'--detalle')
def panel(case,life):return ses(case,life,[{'contexto':k}for k in['alfa','zeta','epsilon','gamma','beta','delta']])
def main():
    p=HERE/'PROTOCOLO_INTEGRACION_SELECTOR_A27.json'
    if p.exists():raise FileExistsError(p)
    p.write_text(json.dumps({'parent':'MU_MAIN T13474, own six associations, beta revised, actual prepare/commit completed','architecture':'Same N67 whole-world parent. R06 P0 anatomy in vacant RAW aroundE15,15,15. Neither learned fields nor clocks copied.','before_learning':'First old-six panel after preparation','experience':'One explicit zero-contact B at fixed next odd391 native writing phase','reader':'Same three physical outputs atgenericquery+6, querypayload5/supplies0; no historicalcontent passed to reader','arms':'MAIN closedactualworker [7,13] andfailurefeedbackfixedA0; exactprefixU no newfeedback withagealignment; auxiliarymatched positive-law and actuator-nulled for actuatorcausality handled inR08','main_sequence':'Three first uses, old6; two workeropportunities with actualfailure/plazovencido genericreturn; commonnewuse; retention6; reservedactualworker uses; save/reload','criterion':'Separate nativechoice/actualaction/accepted useful and rawmemoryretention. NeutralY no intelligent fallback. Gain local, not general policy.','known_limits':'Hostinitiatesrequests. Nativebankrouting not integrated: unselected genericresources interfered withall6. Fixedfailure A hardware biases one direction; invertedlawmay be harmful.','code':'System modules captured content-addressed by each supervisor before every step'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    run('A27_PREPARAR_MISMO_MAIN','unificada-preparar','--vida','MU_MAIN')
    panel('A28_PANEL_ANTES_NUEVA_HISTORIA','MU_MAIN')
    mu('A29_MAIN_EXPERIENCIA_B','MU_MAIN',[{'modo':'experiencia','lado':'B'}])
    mu('A30_MAIN_TRES_PRIMEROS_USOS','MU_MAIN',[{'modo':'usar'}]*3)
    panel('A31_PANEL_CON_SELECTOR_ADQUIRIDO','MU_MAIN')
    run('A32_FORK_RETORNO_OMITIDO','bifurcar','MU_MAIN','MU_SELECTOR_RETURN_U','--modalidad','DIAGNOSTIC_COPY')
    main=mu('A33_MAIN_CONSECUENCIAS_PROPIAS','MU_MAIN',[{'modo':'trabajo','dominio':'trabajadores','valores':[7,13]}]*2)
    mu('A34_U_ACCIONES_SIN_RETORNO','MU_SELECTOR_RETURN_U',[{'modo':'trabajo','dominio':'trabajadores','valores':[7,13]}]*2,feedback='omit')
    run('A35_U_IGUALAR_EDAD','continuar','--vida','MU_SELECTOR_RETURN_U','--hasta',str(main['INSTRUMENTO']['tick']))
    mu('A36_MAIN_OPORTUNIDADES_RESERVADAS','MU_MAIN',[{'modo':'trabajo','dominio':'trabajadores','valores':v}for v in[[9,15],[6,17],[11,14]]])
    mu('A37_U_OPORTUNIDADES_RESERVADAS','MU_SELECTOR_RETURN_U',[{'modo':'trabajo','dominio':'trabajadores','valores':v}for v in[[9,15],[6,17],[11,14]]],feedback='omit')
    panel('A38_MAIN_RETENCION_DESPUES_ACCIONES','MU_MAIN')
    run('A39_GUARDAR_INTEGRADO','guardar','--vida','MU_MAIN')
    mu('A40_CONTINUACION_OTRO_PROCESO','MU_MAIN',[{'modo':'usar'}])
if __name__=='__main__':main()
