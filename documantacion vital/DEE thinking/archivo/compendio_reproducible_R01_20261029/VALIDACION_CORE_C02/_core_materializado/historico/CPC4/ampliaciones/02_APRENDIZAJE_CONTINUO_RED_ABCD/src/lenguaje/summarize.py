"""Analysis-only matrices and independent NSM status dimensions from saved data.

This module is not imported by the physical participant or the public decoder.
Any comparison with the actual presented teaching history is an external
evaluation, never a Native answer-generation path.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
from .protocol import put, sha

ROOT=Path(__file__).resolve().parents[2];PARENT=ROOT.parents[1]


def read(relative):return json.loads((ROOT/relative).read_text(encoding="utf-8"))


def run():
    matrices=[]
    continuous=read("resultados/lenguaje/continuous02/EXPERIMENT_CONFIG.json")
    directions=read("resultados/lenguaje/direction03/EXPERIMENT_CONFIG.json")
    for family,config in (("continuous02",continuous),("direction03",directions)):
        for case in config["cases"]:
            path=f"resultados/lenguaje/{family}/{case['id']}/MEASUREMENTS.json";data=read(path)
            experiences=data.get("experiences",[]);rows=[]
            # This dictionary is evaluator-only and is never exported to the
            # operating Native world or used by the querier/decoder.
            observed_teaching={x["form"]:(x.get("observed_sign") if family=="direction03" else x["sensor"]["class_sign"]) for x in experiences}
            for rr in data["readouts"]:
                if family=="direction03":
                    form=rr["form"];valid=rr["valid"];value=rr["class_sign"];actual=rr["physical"];receipts=[rr["receipt"]]
                elif "readout" in rr:
                    form=rr["form"];valid=rr["readout"]["valid"];value=rr["readout"]["class_sign"];actual=rr["readout"]["physical"];receipts=rr["receipts"]
                else:
                    rows.append({"tick":rr["tick"],"mode":"COMMON_CURRENT_PROFILE_TO_FORMS",
                                 "current_sensor":rr["sensor"],"actual":rr["actual"],"receipts":rr["receipts"],
                                 "qualified_local_forms":rr["locally_emitted_forms"],
                                 "all_regions_inputs_applied":all(x["status"]=="applied" for x in rr["receipts"])})
                    continue
                expected=observed_teaching.get(form)
                rows.append({"tick":actual["tick"],"mode":"WORD_TO_ACQUIRED_CLASS","form":form,
                             "actual":actual,"receipts":receipts,"response_qualified":valid,"decoded_sign":value,
                             "external_evaluator_presented_sign":expected,
                             "matches_actual_teaching_when_response_present":bool(valid and value==expected)})
            matrices.append({"case":case["id"],"family":family,"evidence":path,"initial":data["initial"],"final":data["final"],
                             "new_preparation":data.get("new_preparation",False),"panel":rows,
                             "older_form_retention_panel":data.get("old_retention_panel",[]),
                             "not_independent_tick_replicates":True})
    summary={"generated_utc":datetime.now(timezone.utc).isoformat(),"physical_trajectories":19,
             "counting":{"discovery_continuations431":2,"controlled_integrated1431":10,"direction_content_extension":7,
                         "fresh_worlds_inside_controlled_integrated":2,"technical_processes_not_scientific_samples":4,
                         "technical_checks_asserted":20},
             "same_native_genealogy_witness":"MAIN_NEW_FORMS continues actual network0→431→931→1431→1529; DIRECTION_MAIN continues that exact1529 snapshot to1634.",
             "new_form_identities":["BUENO","MALO","ARRIBA","DEBAJO"],"full_NSM_semantics":False,
             "matrices":matrices,
             "mechanisms":["Native directional relative-state acquisition from coincident physical inputs",
                           "Fixed external transduction of current F7/R3 packet availability",
                           "Fixed external transduction of current source packet dz sign",
                           "Consuming physical word queries and a separate common profile-to-form panel"],
             "revisions":[{"previous":"Only two default inheritedHAY/NO forms were used in the originalCPC4 apparatus",
                           "new":"Two task-profile forms and then two direction-class forms were acquired on one continuingABCD genealogy",
                           "limit":"Same Native association family; not four new cognitive mechanisms or general dictionary learning"},
                          {"previous":"Discovery common naming required all eight region inputsApplied and returned empty despite local26",
                           "new":"The original data/decoder remain untouched; a local independent-receipt observer was frozen before the new integrated controls and fresh worlds",
                           "limit":"Other regions' admission rejections remain visible; a local emission is not full symmetric admission"}],
             "limits":["Task-relative BUENO/MALO are externally taught F7/R3 classes. No optimizer, reward-maximizing host policy, universal evaluation or semantic-prime mastery is implemented.",
                       "ARRIBA/DEBAJO denote only dz in the declared lattice frame, not gravity or general spatial understanding.",
                       "Older BUENO/MALO additional probes at1568/1596 had no qualified26 signature. This does not establish full-state erasure or four simultaneous memories.",
                       "Report-omitted queries were rejectedOccupied; they do not establish forgetting.",
                       "Omitted-signal and unpaired controls did accept the later query but did not express21.",
                       "The common naming panel has direct emissions but no new matched omission arm within that exact panel; word-history controls and the inheritedM1 panel are separate evidence.",
                       "The two direction source/payload variants use worlds already observed in the preceding task and are reserved task parameters, not newly independent preparations.",
                       "No NSM composition or universal semantic acquisition was measured."]}
    put(ROOT/"resultados/lenguaje/LANGUAGE_SUMMARY.json",summary)
    catalogue=json.loads((PARENT/"NSM65_CATALOGO.json").read_text(encoding="utf-8"))
    fields=catalogue["status_dimensions_independent"]
    entries=[]
    for old in catalogue["entries"]:
        entries.append({"id":old["id"],"forma_es":old["forma_es"],"fuentes":old["fuentes"],
                        "full_NSM_semantics":False,
                        "baseline_reference":"Inherited CPC4 NSM65_CATALOGO.json; not modified",
                        "dimensiones_independientes":{f:{"estado":"SIN_NUEVA_PRUEBA_EN_ESTA_AMPLIACION","evidencia":[]} for f in fields}})
    index={x["id"]:x for x in entries}
    def setfields(identifier,values):
        for name,status,evidence,scope in values:
            index[identifier]["dimensiones_independientes"][name]={"estado":status,"evidencia":evidence,"alcance":scope}
    for identifier,form,case in (("NSM65.THERE_IS","HAY","MAIN_PLUS_EVENT"),("NSM65.NOT","NO","MAIN_MINUS_EVENT")):
        temporal=f"resultados/continuidad/M1_TEMPORAL_ACCESS/{case}/MEASUREMENTS.json"
        renewed=f"resultados/continuidad/M1_RENEWED_CYCLES/{'PLUS_STABLE' if form=='HAY' else 'MINUS_STABLE'}/MEASUREMENTS.json"
        setfields(identifier,[("interfaz_registrada","PUERTOS_HEREDADOS_T0_SIN_REINSTALACION",[temporal],"Same actual inherited world; external textual identity only"),
                              ("fisica_realizable","NUEVO_ACCESO_TEMPORAL_NATIVO",[temporal],"NoRAW/clock cut, transplant or assisted environmental rescue"),
                              ("asociacion_entrenada","HISTORIA_HEREDADA_UTILIZADA_NO_REENTRENADA",[temporal],"New access, not new semantic acquisition"),
                              ("retencion","FUNCION_EN_TRES_CICLOS_EMPAREJADOS",[temporal,renewed],"Actual26→36→46 under fixed supplied reader; unmatched contexts may consume the other function"),
                              ("reservada","GEOMETRIA_YA_OBSERVADA_NUEVO_PANEL",["resultados/continuidad/M1_TEMPORAL_ACCESS/OTHER_GEOMETRY_PREVIOUSLY_OBSERVED/MEASUREMENTS.json"],"Not an unseen fresh-world holdout"),
                              ("emision","FORMA_FISICA_EN_MAIN_CON_SONDA_COMUN",[temporal,renewed],"Currentclass→same inputs at both regions→actual26/36/46vertical; no assistedcut"),
                              ("composicion","NO_MEDIDA",[],"No universal existence/negation or NSM composition inferred")])
    for identifier,form,slot in (("NSM65.GOOD","BUENO",0),("NSM65.BAD","MALO",1)):
        base="resultados/lenguaje/continuous02/"
        paired=[base+x+"/MEASUREMENTS.json" for x in ("MAIN_NEW_FORMS","NAMES_INVERTED","SIGNALS_OMITTED","UNPAIRED_PLUS1")]
        setfields(identifier,[("interfaz_registrada","FORMA_Y_PUERTO_FISICO_T0",[base+"MAIN_NEW_FORMS/MEASUREMENTS.json"],"L1BUENO/L2MALO form identity fixed before training"),
                              ("fisica_realizable","DOS_HISTORIAS_FISICAS_EN_MISMA_GENEALOGIA",paired,"Current F7/R3 profile is externally sensed; no expected class from case metadata"),
                              ("asociacion_entrenada","RELACION_ADQUIRIDA_ACOTADA_CON_INVERSION_Y_CONTROLES",paired,"Task-profile availability only; no general good/bad semantics"),
                              ("retencion","64TICKS_HASTA_SONDA_67HASTA_LECTURA",[base+"MAIN_NEW_FORMS/MEASUREMENTS.json"],"Later1568/1596 panel absent; no claim of simultaneous retention with the two direction forms"),
                              ("reservada","DOS_PREPARACIONES_FRESH_Y_ORDEN_INVERSO",[base+x+"/MEASUREMENTS.json" for x in ("RESERVED_TRANSLATION_A","RESERVED_ORDER_TRANSLATION_B")],"Entire T0→1529 same-instance trajectories; translation/order frozen before measurement"),
                              ("emision","FORMA_NATIVA_EN_PANEL_COMUN_LOCAL",[base+("COMMON_NAME_CURRENT_ROLE" if slot==0 else "COMMON_NAME_CURRENT_SECOND")+"/MEASUREMENTS.json"],"Conditional current-profile→26vertical at physical form region; other regions' rejections retained"),
                              ("composicion","NO_MEDIDA",[],"No NSM grammar or semantic composition inferred from the ABCD physical cascade")])
    for identifier,form in (("NSM65.ABOVE","ARRIBA"),("NSM65.BELOW","DEBAJO")):
        base="resultados/lenguaje/direction03/"
        paired=[base+x+"/MEASUREMENTS.json" for x in ("DIRECTION_MAIN","DIRECTION_FORMS_INVERTED","DIRECTION_SIGNALS_OMITTED","DIRECTION_UNPAIRED_PLUS1")]
        setfields(identifier,[("interfaz_registrada","NUEVA_FORMA_EN_PUERTO_T0_PREEXISTENTE",[base+"DIRECTION_MAIN/MEASUREMENTS.json"],"L3ARRIBA/L4DEBAJO, not a new anatomical component"),
                              ("fisica_realizable","SENSOR_ACTUAL_DZ_Y_RESPUESTA_NATIVA",paired,"Lattice dz only; actual sourceApplied required; not gravity"),
                              ("asociacion_entrenada","RELACION_ACOTADA_CON_INVERSION_Y_CONTROLES",paired,"Different observed content from F7/R3, same directional-association mechanism"),
                              ("retencion","64TICKS_HASTA_SONDA_67HASTA_LECTURA",[base+"DIRECTION_MAIN/MEASUREMENTS.json"],"Only the measured finite interval"),
                              ("reservada","FUENTE_C_CARGAS17_23_Y_ORDEN_RESERVADOS",[base+x+"/MEASUREMENTS.json" for x in ("RESERVED_SOURCE_C_PAYLOAD17","RESERVED_SOURCE_ORDER_PAYLOAD23")],"Parents seen in preceding task; reserved task parameters rather than independent fresh preparations"),
                              ("emision","SITUACION_A_FORMA_NO_MEDIDA",[],"Word→class responses do not establish native symbol production for this content"),
                              ("composicion","NO_MEDIDA",[],"No general spatial-prime composition")])
    evolution={"schema":"CPC4.AMPLIACION02.NSM65.evolution.v1","generated_utc":datetime.now(timezone.utc).isoformat(),
               "baseline_catalogue_sha256":sha(PARENT/"NSM65_CATALOGO.json"),"count":len(entries),
               "status_dimensions_independent":fields,"entries":entries,
               "counts_separated":{"documentary_forms":65,"new_trained_task_relative_forms":4,
                                   "inherited_trained_forms_with_new_native_access":2,
                                   "universal_NSM_semantics_acquired":0,"NSM_composition_measured":0,
                                   "simultaneous_six_meaning_retention_claimed":False},
               "source_scope":"Original primary NSM source records are inherited without alteration. Language inventory validity does not establish Native semantic acquisition.",
               "phenomenon_scope":"External textID/form identity, current physical transducers, Native association and readout are separately attributed."}
    put(ROOT/"resultados/lenguaje/NSM65_EVOLUCION.json",evolution)
    return summary,evolution


if __name__=="__main__":run()
