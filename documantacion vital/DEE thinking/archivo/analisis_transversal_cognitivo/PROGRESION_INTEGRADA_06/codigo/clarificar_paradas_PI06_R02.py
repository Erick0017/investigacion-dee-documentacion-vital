"""Record a textual preregistration discrepancy without rewriting used plans."""
from pathlib import Path
import datetime,hashlib,json
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    plans=sorted((P/'control').glob('PLAN_*_PI06_R0*.json'))
    output=P/'control/ACLARACION_PARADA_NUMERICA_PI06_R02.json'
    value={'schema':'DEE.PI06.numeric_observation.stop_clarification.R02',
        'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'context':'Root confirmó que el desarrollo IZQ0 había comenzado antes de esta aclaración; no se modifica su plan ni su hash. Los controles restantes y la reserva todavía no habían empezado según ese mensaje.',
        'discrepancy':'La prosa de los planes decía que NULL detiene; el runner preregistrado y ejecutado no detiene por un desenlace numérico/NULL del lector, sólo por incertidumbre del transporte, admisión incompleta o límites.',
        'actual_execution_rule':'Los3desafíos y esperas se ejecutan en el orden fijo aunque la respuesta numérica sea incorrecta o el lector no produzca firma(NULL). NULL es un resultado de acceso, no cero y no una autorización de reparación.',
        'stop_rule':'Detener y preservar ante transporte ambiguo/fallido, recibo ambiguo, entrada rechazada o no aplicada, vencimiento de plazo/presupuesto o error del propietario. No reintentar ni limpiar.',
        'scientific_reason':'Una ausencia de firma puede ser el deterioro o la recuperación que se investiga. Condicionar la continuación a una respuesta correcta o formada sesgaría la secuencia fija.',
        'no_material_protocol_change':True,'no_literal_step_change':True,'no_previous_plan_rewritten':True,
        'no_new_reader_or_decoder':True,'no_new_repair_or_guard':True,
        'runner':{'file':'codigo/ejecutar_fases_PI06_R01.py','sha256':sha(P/'codigo/ejecutar_fases_PI06_R01.py')},
        'original_plans_preserved':[{'file':p.name,'sha256':sha(p)}for p in plans],
        'Native_executed_by_this_tool':False,'new_Native_ticks':0,
        'reporting':'Si se observa NULL en la tercera consulta de IZQ0, declarar la desviación de la frase descriptiva. Si las3son números, la discrepancia no habrá cambiado los pasos de ese brazo. Se registra ahora para no presentarla como decisión retroactiva según los controles.'}
    with output.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':output.name,'sha256':sha(output),'Native_executed':False}))
if __name__=='__main__':main()
