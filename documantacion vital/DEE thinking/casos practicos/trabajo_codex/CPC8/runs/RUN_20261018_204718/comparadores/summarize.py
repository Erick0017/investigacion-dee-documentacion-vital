"""Recalculate comparison tables only from saved primary observations."""
from pathlib import Path
import hashlib,json,sys
BASE=Path(__file__).resolve().parent;ROOT=BASE.parent
sys.path.insert(0,str(BASE))
from run_comparison import metric,sha,write

def load(p):return json.loads(p.read_text(encoding="utf-8"))
def main():
    cfg=load(BASE/"FROZEN_CONFIG.json");cases=[];proof=[];rows=[];ablations=[];methodological=[]
    for seed in cfg["reserved_seeds"]:
        hashes=[]
        for method in ("DEE","B1","B2"):
            prior=ROOT/"resultados"/"comparadores"/(("B2_PRIVATE" if method=="B2" else method)+"_"+str(seed))
            original=load(prior/"MEASUREMENTS.json")
            path=prior.with_name(prior.name+"_continuation") if method=="DEE" else prior
            m=load(path/"MEASUREMENTS.json")
            assert m["status"]=="MEASURED",str(path)
            observations=load(path/"OBSERVATIONS.json");calculated=metric(observations)
            assert calculated==m.get("combined_totals",m.get("totals"))
            hashes.append(sha(prior/"EVENTS.json"))
            prefix="cmp_"+method+"_"+str(seed)
            jobs=[load(ROOT/"jobs"/(prefix+("_private01" if method=="B2" else "_01"))/"COMMAND.json")]
            if method=="DEE":jobs.append(load(ROOT/"jobs"/(prefix+"_late01")/"COMMAND.json"))
            assert all(j["owned_job_closed"] and j["owned_worker_waited"] for j in jobs)
            for r in observations:
                rows.append({"method":method,"seed":seed,"primary":str((path/"OBSERVATIONS.json").relative_to(ROOT)),**r})
            snapshots=(original["checkpoints"]+m["checkpoints"]) if method=="DEE" else m["checkpoints"]
            for c in original["checkpoints"]:
                assert sha(prior/c["file"])==c["sha256"]
            if method=="DEE":
                for c in m["checkpoints"]:assert sha(path/c["file"])==c["sha256"]
                assert m["initial_physics"]==original["checkpoints"][-1]["physics"]
            final=m["checkpoints"][-1]
            cases.append({"method":method,"seed":seed,"genealogical_trajectories":1,"experienced_examples":66,
              "primary":str((path/"MEASUREMENTS.json").relative_to(ROOT)),"primary_sha256":sha(path/"MEASUREMENTS.json"),
              "observations_sha256":sha(path/"OBSERVATIONS.json"),"events_sha256":hashes[-1],"metrics":calculated,
              "panels":m.get("combined_panels",m["panels"]),"restore":m["restore"],"resources":m["resources"],
              "wall_seconds":m.get("combined_wall_seconds",m["wall_seconds"]),
              "cpu_seconds":m.get("combined_cpu_seconds",m["cpu_seconds"]),
              "peak_job_bytes":max(j["peak_job_memory_bytes"] for j in jobs),
              "snapshots_stored_bytes":sum(c["stored_bytes"] for c in snapshots),
              "final_state_stored_bytes":final["stored_bytes"],"final_state_decoded_bytes":final.get("proof",{}).get("decoded_bytes"),
              "initial_helper_attempt":original["status"] if method=="DEE" else None,
              "physical_horizon_ticks":1313 if method=="DEE" else None,
              "participant_rng":17890331 if method=="B2" else None,
              "construction_bootstrap_sha256":sha(BASE/"run_mlp_private.py") if method=="B2" else None})
            if method=="B2":
                old=prior.with_name("B2_"+str(seed));om=load(old/"MEASUREMENTS.json")
                methodological.append({"method":"B2","seed":seed,"primary":str((old/"MEASUREMENTS.json").relative_to(ROOT)),
                  "sha256":sha(old/"MEASUREMENTS.json"),"metrics":om["totals"],
                  "status":"PRESERVED_INITIAL_SHARED_RNG_METHOD_ATTEMPT_NOT_MAIN_COMPARISON",
                  "reason":"Same scalar seed supplied to generator and participant initialization; model never inferred labels from it. Repeated only comparator with independent private RNG, no hyperparameter changes.",
                  "independent_environment_worlds":0})
            for job in jobs:proof.append({"job":job["name"],"exit_code":job["exit_code"],"status":job["status"],"owned_job_closed":job["owned_job_closed"]})
        assert len(set(hashes))==1,"Different experience streams within a seed"
        audit=ROOT/"resultados"/"comparadores"/("DEE_"+str(seed)+"_omit_first_L01")
        if (audit/"MEASUREMENTS.json").exists():
            am=load(audit/"MEASUREMENTS.json")
            assert am["status"]=="MEASURED" and am["parent_unchanged"] and am["restore_exact"]
            for c in am["checkpoints"]:assert sha(audit/c["file"])==c["sha256"]
            aj=load(ROOT/"jobs"/("cmp_DEE_"+str(seed)+"_omit01")/"COMMAND.json")
            assert aj["owned_job_closed"] and aj["exit_code"]==0
            ablations.append({"seed":seed,"modality":am["modality"],"independent_worlds":0,
                "primary":str((audit/"MEASUREMENTS.json").relative_to(ROOT)),"sha256":sha(audit/"MEASUREMENTS.json"),
                "contrast":am["contrast"],"parent_unchanged":True,"restore_exact":True,
                "applied_requests":am["applied_requests"],"local_windows":[w["tick"] for w in am["windows"]],
                "main_saved_windows":[w["tick"] for w in am["main_saved_windows"]],
                "peak_job_bytes":aj["peak_job_memory_bytes"],"wall_seconds":am["wall_seconds"],"cpu_seconds":am["cpu_seconds"]})
    summary={"scope":cfg["scope"],"configuration_sha256":sha(BASE/"FROZEN_CONFIG.json"),
      "continuation_protocol_sha256":sha(BASE/"LATE_REVISION_PROTOCOL.json"),"cases":cases,"jobs":proof,
      "query_ablation_diagnostic_forks":ablations,
      "preserved_methodological_attempts":methodological,
      "participant_rng_isolation_protocol_sha256":sha(BASE/"PRIVATE_RNG_PROTOCOL.json"),
      "counts":{"methods":3,"reserved_world_seeds":2,"method_seed_trajectories":6,"native_genealogies":2,
        "native_resume_from_T920":2,"native_restore_at_T1182":2,"queries_per_trajectory":251,
        "total_comparable_queries":sum(c["metrics"]["queries"] for c in cases),"discovery_K8_models":2,
        "semantic_meanings_validated":0,"additional_query_ablation_forks":len(ablations),
        "ablation_queries_not_pooled_with_251":129*len(ablations),
        "superseded_B2_queries_not_pooled":251*len(methodological)},
      "calculation_formulas":{"accuracy":"sum(correct)/queries, including missing in denominator",
        "new":"First panel for each form after its acquisition block:8+8+16+33=65",
        "retained":"8+16+32+64+65=185, without re-teaching those relations",
        "revision":"First revised L01 query@1179:1; the next query@1310 is retention of revision",
        "total":"65+185+1=251 per method/seed; queries/ticks are not independent examples",
        "latency":"DEE query read_tick-input_tick=3; wall times and algorithm timings reported separately"},
      "inequivalence":cfg["inequivalence"],
      "incidents":[{"kind":"launch","record":"jobs/cmp_discovery_k8_01/COMMAND.json","cause":"Child relative interpreter path used from supervisor campaign cwd; no participant launched. Absolute interpreter path corrected."},
        {"kind":"finite_API_contract","count":2,"cause":"revise1048 rejected because native descriptor allows exactly4*N=524; no state mutation.121 measurements/seed preserved, then same lineage continued via frozen declared ports."}],
      "interpretation":"Finite associative task profiles, not a global intelligence comparison. Prepared DEE revision routing and MLP replay are maintenance with declared costs. No false numeric zero for uncovered physical response."}
    write(BASE/"SUMMARY.json",summary)
    with (BASE/"OBSERVACIONES.jsonl").open("w",encoding="utf-8") as f:
        for row in rows:f.write(json.dumps(row,ensure_ascii=False,separators=(",",":"))+"\n")
    lines=["# Asociación opaca: adquisición, retención y revisión", "", 
      "Capacidad medida: cada método recibió el mismo flujo de66 observaciones presentes (65 asociaciones y una revisión) por mundo y respondió251 consultas explícitas. Son65 formas opacas de dos clases; no65 significados NSM ni65 memorias independientes.","",
      "| Método/semilla | Nuevas | Retenidas | Revisión | Total | CPU s | Pared s | Pico job MiB | Estado final almacenado |", 
      "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for c in cases:
        t=c["metrics"]
        lines.append(f'| {c["method"]}/{c["seed"]} | {t["acquisition_correct"]}/65 | {t["retention_correct"]}/185 | {t["revision_correct"]}/1 | {t["correct"]}/251 | {c["cpu_seconds"]:.3f} | {c["wall_seconds"]:.3f} | {c["peak_job_bytes"]/2**20:.2f} | {c["final_state_stored_bytes"]} B |')
    lines.extend(["", "## Mecanismos e información", "", 
      "DEE conserva un único Runtime N131 hasta920, reanuda su snapshot íntegro y recibe cuatro entradas físicas públicas para la revisión tardía. Dos son contraflujos simétricos de carga cero@1044; la señal5 y el acontecimiento11 llegan@1048. La selección de esa regulación es del protocolo, no una decisión aprendida. Los paneles se emiten en131,393,655,917,1179,1310 y se leen tres ticks después. No hay borrado RAW ni reinicio de clocks. Guardar/cargar preserva RAW/clocks, tick, identidad, recibos y progreso.", "",
      "B1 conserva el último par observado por forma en un diccionario actualizable. B2 es una MLP65→24tanh→logística con1609 parámetros, SGD0.08 y replay finito≤65 ejemplos:256 presentaciones por observación,16896 por trayectoria. Una revisión sustituye la etiqueta antigua sólo en su memoria de replay, por ser el nuevo acontecimiento observado. La respuesta B2 se calcula por forward de pesos, no consultando el diccionario de replay.","",
      "El descubrimiento K8 probó64 y256 presentaciones; ambos resolvieron sus paneles. Se congelaron256 para margen de retención, antes de ejecutar las dos semillas reservadas. No se ajustó el MLP frente a sus resultados K65.","",
      "La tabla principal utiliza paraB2 una inicialización/replay privada fija17890331, independiente de las semillas ambientales402817/591307. El primer intento reutilizaba el mismo número para ambos RNG, aunque no reconstruía etiquetas desde él; se conserva completo como incidencia metodológica. La repetición cambió únicamente ese bootstrap, no hiperparámetros, observaciones, decoder ni evaluación. Son réplicas del comparador sobre los mismos mundos, no nuevas reservas ciegas ni aprendizajes DEE adicionales.","",
      "## Fronteras y controles de interpretación", "",
      "El helper revise de4.5 rechaza1048 porque publica la cadencia524. Quedan conservados ambos intentos y sus121 respuestas previas. La continuación fuera de ese helper usa sólo puertos existentes y se identifica como investigación, no como ampliación silenciosa de contrato.", "",
      "Una restauración exacta no garantiza acceso funcional indefinido. Cuando una sonda aplicada produce sólo carga5 sin dirección cubierta, el resultado es ausente/insuficiente, no el número cero. Las respuestas restantes y la primera revisión se conservan como resultados separados.","",
      "El control causal conservó la misma revisión y las otras64 consultas, omitiendo sólo la primera sondaL01@1179. En ambos mundos, L01 volvió a responder+1 con carga21 y dirección[-1,1,0]@1313; con aquella sonda previa sólo quedaba carga5[-1,0,0] sin respuesta cubierta. Los otros64 contenidos respondieron. Esto localiza la pérdida de acceso posterior en la intervención de consulta dentro del protocoloM2 tardío, no en la restauración. No acredita destrucción completa de información ni un límite universal de memoria. Son dos forks diagnósticos, no dos aprendizajes independientes.","",
      "Las ventanas exactas27sitios de los controles muestran en1182 un registro16[0,1,0], frente al producto consultado21[-1,1,0] delMAIN guardado. La medición central+Moore26 no cubre todo el cono causal compuesto ni certifica genealogía fuera de esas ventanas; las zonas sin captura permanecen declaradas. Los clocks se conservan como enteros exactos.","",
      "Las tareas convencionales emplean consultas que no perturban su memoria; DEE recibe sondas físicas. El coste DEE incluye evolución, instrumentación completa y almacenamiento comprimido; el reloj de pared incluye contención de la máquina. El archivo final DEE está en gzip, los convencionales enJSON: sus bytes de archivo no son una comparación homogénea de memoria. SUMMARY conserva además tamaño nativo decodificado, estadoJSON compacto, buffers y memoria pico; los1609 parámetros flotantes B2 ocupan12872bytes enfloat64 antes de replay, RNG y formato. Este ensayo no mide energía ni rendimiento industrial.","",
      "La coincidencia de EVENTS se verifica por hash entre los tres métodos dentro de cada semilla. No se pasan targets futuros a query; sólo el evaluador externo adjunta expected después de obtener la emisión/forward. Los targets de entrenamiento son las consecuencias actuales que constituye la tarea.","",
      "## Datos y reproducción", "", "`SUMMARY.json` conserva fórmulas, denominadores, recursos y rutas/hash de primarios. `OBSERVACIONES.jsonl` permite recalcular cada respuesta; RAW y clocks físicos son cadenas exactas, no floats. Los casos originales y sus continuaciones guardan fronteras completas y recibos.", "",
      "Desde una extracción: instale el WHL oficial incluido en el paquete padre y ejecute `python -I -B comparadores/run_comparison.py --method B1 --seed 402817 --output NUEVO_DIRECTORIO`. B2 aislada usa `comparadores/run_mlp_private.py --method B2 --seed 402817 --output NUEVO_DIRECTORIO_B2`. Para DEE, el comando original reproduce adquisición y el rechazo contractual: la continuación posterior es `comparadores/continue_native.py --seed 402817 --output NUEVA_CONTINUACION`, leyendo el checkpoint original. Utilice el supervisor para llamadas nativas y otro nombre de job. Nunca sobreescriba casos completos."])
    (BASE/"INFORME.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"cases":len(cases),"queries":summary["counts"]["total_comparable_queries"],"totals":[[c["method"],c["seed"],c["metrics"]["correct"],c["metrics"]["missing"]] for c in cases],"summary_sha256":sha(BASE/"SUMMARY.json")},ensure_ascii=False))
if __name__=="__main__":main()
