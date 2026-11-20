"""Create one draft protocol from current preserved source bytes; no Native."""
from pathlib import Path
import hashlib,json

if __name__=="__main__":
    home=Path(__file__).resolve().parent
    r=home.parents[3]
    source=r/"DEE Cognitive 2.0"/"sistema"/"capacidades"
    # P4/codigo -> P4 -> analisis_transversal_cognitivo -> archivo -> DEE thinking
    if not source.is_dir():raise ValueError("Directed source root not found: "+str(source))
    files={name:source/name for name in (
        "progresion_integrada_03_R01.py","pi03_credito_generico_R01_BORRADOR.py",
        "aritmetica_directa_eci02.py","aritmetica_apd_01.py","percepcion_cruda_fi01.py",
        "mente_unificada_01.py")}
    files["pi04_selector_contextual_C2_R01.py"]=home/"pi04_selector_contextual_C2_R01.py"
    files["e3_retorno_desacoplado_R01.py"]=home/"E3"/"e3_retorno_desacoplado_R01.py"
    development=[4,6,4,4,6,6,4,6,4,6,4,6]
    schedule=[{"stage":"development","context":c,"left":16,"right":9}for c in development]
    schedule += [{"stage":"reserved","context":c,"left":pair[0],"right":pair[1]}
                 for pair in ((15,8),(17,8))for c in (3,5,7,8)]
    p={"schema":"DEE.PI04.C2.protocol.R01","status":"DRAFT","N":67,"origin":[19,54,5],
       "base_prefix":"PI03.TC.R01","calibration_values":[0,1,4,44,47,50],"delay_laps":4,
       "max_ticks_per_opportunity":1500,"processing_budget_ticks":240,
       "first_action_codec":{"1":"suma","0":"diferencia","-1":"diferencia","NULL":None},
       "second_zero_motor":-1,
       "environment":{"context_cut":4,"low_operation":"diferencia","high_operation":"suma",
                      "numeric_cut":20,"low_route":-1,"high_route":1,"resource_bytes":64},
       "schedule":schedule,
       "dependencies_sha256":{name:hashlib.sha256(file.read_bytes()).hexdigest()for name,file in files.items()},
       "null_stop":"preserve_first_NULL_after_actual_failure_and_generic_return",
       "attribution":"UNEXECUTED DRAFT: first Native choice selects prepared function; actual Native numeric output feeds Native second choice. Sequence, opportunities, zero codecs, calendar and private device law prepared. Root must freeze development/reserve after limited calibration; no success or agency presumed."}
    target=home/"PROTOCOLO_PI04_C2_R01.json"
    if target.exists():raise ValueError("Refuse to overwrite a protocol, including an unexecuted draft")
    target.write_text(json.dumps(p,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"protocol":str(target),"status":p["status"],"opportunities":len(schedule),
                      "sha256":hashlib.sha256(target.read_bytes()).hexdigest(),"Native_ticks":0},ensure_ascii=False,indent=2))
