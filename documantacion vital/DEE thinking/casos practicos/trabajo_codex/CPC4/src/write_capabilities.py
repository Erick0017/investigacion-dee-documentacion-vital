"""Machine-readable scopes and provenance, not a cognitive PASS/FAIL ledger."""
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.common import put,sha,WHEEL_SHA,NATIVE_SHA,KERNEL_SHA,PARENT_SHA


def main():
    references=json.loads((ROOT/"referencias"/"PROVENANCE.json").read_text(encoding="utf-8"))
    catalogue=json.loads((ROOT/"NSM65_CATALOGO.json").read_text(encoding="utf-8"))
    entries=catalogue["entries"]
    rows=[
      {"id":"NATIVE_MESSAGE_USE","capacity":"Producto de A modifica relación adquirida de B y consecuencia posterior",
       "mechanism":"Online mobile acquisition, toroidal native transport, selective vector composition, later common physical probe",
       "modality":"EXPERIENCE_PROTOCOL_PLUS_NATIVE_EVOLUTION","state":"MEASURED",
       "evidence":["resultados/confirmacion/MAIN_MINUS/MEASUREMENTS.json","resultados/confirmacion/FULL_PLUS/MEASUREMENTS.json","resultados/CHANNEL_ANALYSIS"],
       "domain":"N67, finite A and two-region B, fixed ports and phases. Prepared routes, acquired direction components; not two renewable basal bodies or arbitrary conventions."},
      {"id":"INFORMATIVE_CONTENT_CONTROL","capacity":"Contenido de igual carga produce consecuencias diferentes",
       "mechanism":"Same load21, controlled direction and selected receiving region","modality":"DIAGNOSTIC_FORK","state":"MEASURED",
       "evidence":["resultados/confirmacion/MESSAGE_CONSTANT_PLUS/MEASUREMENTS.json","resultados/confirmacion/MESSAGE_OFF_DIRECTION/MEASUREMENTS.json","resultados/confirmacion/CUT_MINUS/MEASUREMENTS.json"]},
      {"id":"SELECTIVE_COMPENSATION","capacity":"Alteración de ruta compensada; componente adquirido no sustituido",
       "mechanism":"Later Y probe supplies missing Y, not missing Z","modality":"DIAGNOSTIC_FORK_PLUS_NATIVE_CONTINUATION","state":"MEASURED",
       "evidence":["resultados/confirmacion/B_ROUTE_COMPONENT_REMOVED/MEASUREMENTS.json","resultados/confirmacion/B_ACQUIRED_COMPONENT_REMOVED/MEASUREMENTS.json"]},
      {"id":"POST_NATIVE_WORD_ASSOCIATION","capacity":"Dos formas provocan readouts distintos por experiencia sobre consecuencias actuales",
       "mechanism":"Current resource sensor, broadcast physical report, local coincidence and retained direction",
       "modality":"EXPERIENCE_PROTOCOL_PLUS_PHYSICAL_PROBE","state":"MEASURED_WITH_ORDER_LIMITATION",
       "evidence":["resultados/confirmacion/MAIN_MINUS/LENGUAJE","resultados/confirmacion/FULL_PLUS/LENGUAJE","resultados/confirmacion/LEX_MEMORY_CUT","resultados/confirmacion/LEX_NAMES_SWAPPED"],
       "domain":"Two physical forms and specific R3-presence window, not general NSM existence/negation or65meanings."},
      {"id":"SAME_MAIN_PERSISTENCE","capacity":"Continuación nativa→lenguaje y pregunta posterior tras restauración en otro proceso",
       "mechanism":"Complete OrganizationalWorld snapshots, neutral protocol metadata, no reinstallation",
       "modality":"TECHNICAL_RESTORATION_PLUS_PHYSICAL_QUERY","state":"MEASURED",
       "evidence":["resultados/demo02/DEMONSTRATION_SUMMARY.json","resultados/technical_01/TECHNICAL_CHECKS.json","resultados/DEMO_CONTRACTS/RESULTS.json"]},
      {"id":"ENRICHED_OBSERVATION","capacity":"Dirección y contexto conservan distinciones que carga/soporte pierden",
       "mechanism":"O1–O4 integer unpacking, periodic graph geometry and actual temporal encounters",
       "modality":"PASSIVE_OBSERVATION_AND_EXTERNAL_ANALYSIS","state":"MEASURED",
       "evidence":["resultados/observadores/SEM01_CALIBRATION.json","resultados/observadores/R2_REANALYSIS.json","configuraciones/OBSERVER_RESERVED_CONFIG.json","resultados/observer_reserved"],
       "not_claimed":"Persistent homology; GUDHI installation permission blocked. No clustering is called a concept."},
      {"id":"INVERSE_TRANSLATION_MAIN","capacity":"Situación actual provoca un símbolo por acceso inverso",
       "mechanism":"Same sensor probe to both retained lexical regions","modality":"DIAGNOSTIC_FORK_PLUS_PHYSICAL_PROBE",
       "state":"NO_SYMBOL_IN_THREE_MEASURED_TRAJECTORIES_TWO_CUTS_NOT_APPLICABLE",
       "evidence":["resultados/inverse01/RESULTS_COMPLETED.json","resultados/INVERSE_MECHANISM"],
       "domain":"Interference from unpaired broadcast teachers, two distinct local destruction mechanisms. Any later rescue remains diagnostic."},
      {"id":"PERSISTENT_HOMOLOGY","capacity":"Cubic periodic persistent homology","state":"NOT_EXECUTED_NETWORK_PERMISSION",
       "evidence":["jobs/observer_install_gudhi"],"substitute":"Declared toroidal graph connectivity only, not homology"},
      {"id":"JOINT_CONVENTION_ADAPTATION","capacity":"Reciprocal adaptation of an arbitrary convention","state":"NOT_TESTED_IN_THIS_FINITE_REALIZATION",
       "scope":"Both A and B acquire usable relations; their routes and action resources are designed. No closed-loop reciprocal convention update is inferred."},
      {"id":"ARBITRARY_NSM_SEMANTICS","capacity":"Acquisition of65general meanings or compositional grammar","state":"NOT_DEMONSTRATED",
       "scope":"65 documentary forms are software entries, not65native learned capabilities."}
    ]
    access2=ROOT/"resultados"/"inverse_access2"/"RESULTS.json"
    if access2.exists():
        result=json.loads(access2.read_text(encoding="utf-8"))
        rows.append({"id":"CONDITIONAL_INVERSE_ACCESS2","capacity":"Acceso situación→símbolo después de rescate diagnóstico y cambio físico de interfaz",
                     "mechanism":"Intercept one observed unpaired teacher11 at200, preserve W1 memory, use predeclared opposite-X probe5 port; accept only actual26(0,+/-1,0)",
                     "modality":"DIAGNOSTIC_ENVIRONMENTAL_RESCUE_PLUS_PHYSICAL_PROBE_NOT_NATIVE_MAIN",
                     "state":"MEASURED_CONDITIONALLY","evidence":["resultados/inverse_access2/RESULTS.json","resultados/inverse_access2/INVERSE_ACCESS2_CONFIG.json"],
                     "measured_rows":result["cases"],"native_main_symbol_emissions":0,
                     "scope":"W1/HAY only, conditional on explicit external interception of residual teaching traffic; one fresh translated preparation, memory-cut control. Not autonomous repair, universal negation, full bidirectionality or retroactive success of method1."})
    value={"project":"DEE Universe / INVESTIGACION DEE","author":"Ivan Erick Tlaltecatl Morales","campaign":"CPC4",
           "instrument":{"version":"4.0.0","kernel":27,"wheel_sha256":WHEEL_SHA,"native_sha256":NATIVE_SHA,"kernel_source_sha256":KERNEL_SHA},
           "coverage":{"central_cases":33,"fresh_native_preparations":27,"shared_parent_language_cohorts":6,
                       "additional_prospective_observer_worlds":2,"NSM_documentary_entries":len(entries)},
           "nsm_count_rule":"Status dimensions are independent. Response to word is not event→symbol emission; diagnostic rescued emission is separate from MAIN.",
           "capabilities":rows,"configuration_sha256":sha(ROOT/"EXPERIMENT_CONFIG.json")}
    put(ROOT/"CAPACIDADES.json",value)
    provenance={"campaign":"CPC4","author":"Ivan Erick Tlaltecatl Morales","instrument":value["instrument"],
                "CPC3_reference_sha256":PARENT_SHA,"selected_historical_sources":"referencias/PROVENANCE.json",
                "preservation":"No modification or cleanup of CPC3, SEM01, product4, Word or historical packages authorized or performed",
                "dependency_graph":{"normal_execution":["runtime/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl","src/","configuraciones/"],
                                    "auditor_only":["referencias/","resultados/","NSM65_CATALOGO.json"],
                                    "no_CPC3_runtime_import":True,"no_results_as_participant_answer_table":True},
                "historical_manifest_metadata":references,
                "additional_instrument_source":"referencias/instrumento_minimo/PROVENANCE.json",
                "antecedent_mechanism_question_test":[
                  {"antecedent":"SEM01","reused":"Online paired directional relation and signal-alone response","new_question":"Does an emitter product reach a separately experienced receiver and influence a later function?","test":"MAIN±, late cut, wrong/naive/unpaired receiver, constant-content control"},
                  {"antecedent":"CORE06/07 and DEE4 transfer","reused":"Native carrier composition and transfer within one Runtime","new_question":"Which message fields and acquired components matter for use?","test":"Direction-only edits, DY/DZ lesions, bank outcome panel"},
                  {"antecedent":"Ingenierias05/06 and Procesamiento Nativo","reused":"History, context and renewed access as distinct variables","new_question":"Can later probe compensate a relation perturbation?","test":"Same charge/site/clock, retained vs removed vector components"},
                  {"antecedent":"Fisica DEE4.0.1 Meta-Rosetta","reused":"Observer/intervention/horizon-relative predictive equivalence","new_question":"Which reduced descriptions lose functional distinctions?","test":"SEM01 calibration, CPC4 R2 analysis, two new frozen observer worlds"},
                  {"antecedent":"NSM Spanish inventory","reused":"Documentary word forms only","new_question":"Can two forms become associated after native experience on the same world?","test":"Post169 paired/unpaired/omitted words, swapped names, memory lesion, opaque restore"}
                ]}
    put(ROOT/"PROVENANCE.json",provenance)
    print("Capabilities and provenance written; NSM documentary entries",len(entries))


if __name__=="__main__":main()
