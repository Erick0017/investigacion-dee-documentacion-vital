"""Prueba mínima postreubicación, dos propietarios de UNA copia APD03.

No instala, cambia productos, reenseña ni toca las vidas fuente. Requiere GO
explícito. El guion es preparación del operador; los cálculos se hacen después.
El lector RAW se importa de la revisión histórica exacta, no se reconstruye.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import time

DECODER_SHA = "cb044a96301bdb179e595954ef51182b0b503bdca60630b5aa4fbaa0bdfe7aeb"
PARENT_SHA = "c7cf2e78837ed5f99c950016314bfe5f8fbfa868f72a67af36a94a78261a24ba"
PAIR_SHA = "9610905c1c3879fd4de3062894c2978c8cb5187e068185cfe889b7b2ee80a085"
EXPECTED_WORDS = {
    "agrega": 1, "alfa": -1, "beta": 1, "compara": 1, "delta": -1,
    "diferencia": -1, "epsilon": -1, "gamma": 1, "luma": 1,
    "nara": -1, "quita": -1, "recuerda": -1, "resta": -1,
    "suma": 1, "total": 1, "zeta": 1,
}
EXPECTED_MA = {"alfa": -1, "beta": 1, "gamma": 1, "delta": -1, "epsilon": -1, "zeta": 1}
SCRIPTS = {
    "INICIO_USO_GUARDADO": [
        ["estado"], ["reanudar"],
        ["panel", "--nuevas", "--memorias", "--retorno", "omit"],
        ["objetivo", "suma", "18", "9", "--oculto", "--contexto-ambiente", "1", "--retorno", "real"],
        ["paso", "4", "--retorno", "real"], ["guardar"], ["detener"], ["salir"],
    ],
    "REAPERTURA_USO_GUARDADO": [
        ["estado"], ["reanudar"],
        ["lenguaje-nuevo", "luma", "17", "delta", "--retorno", "omit"],
        ["guardar"], ["detener"], ["salir"],
    ],
}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write(path, value):
    with Path(path).open("x", encoding="utf8", newline="\n") as f:
        json.dump(value, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write("\n")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def state_manifest(base):
    return [{"file": p.relative_to(base).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)}
            for p in sorted(base.rglob("*")) if p.is_file()]


def run(options):
    root = options.raiz.resolve(strict=True)
    python = options.python.resolve(strict=True)
    decoder_path = options.decoder.resolve(strict=True)
    output = options.salida.resolve()
    if sha(decoder_path) != DECODER_SHA:
        raise ValueError("El lector histórico no coincide; no se adapta tras observar respuestas")
    helper = load("reorg_frozen_apd03_reader", decoder_path)
    config = read(root / "sistema/contratos/ENTRADA_SENCILLA_APD03.json")
    if (config["source_life"], config["source_tick"], config["source_snapshot_sha256"],
            config["paired_export_manifest_sha256"]) != ("APD03_MAIN", 604825, PARENT_SHA, PAIR_SHA):
        raise ValueError("Otro corte seleccionado; declarar otro protocolo antes de ejecutar")
    if (root / "actualizaciones/arrancar.py").is_file():
        raise ValueError("Esta comprobación exige OriginalBackend, no una distribución colaboradora")
    state_root = root / "sistema/estado"
    protocol_root = root / "sistema/estado/entrada_sencilla/vidas"
    life = options.vida
    if life != "REORG_APD03_01":
        raise ValueError("Identidad reservada de la comprobación: REORG_APD03_01")
    if (state_root / "vidas" / life).exists() or (protocol_root / life).exists():
        raise FileExistsError("La copia ya existe; conservar el futuro, no repetir esta comprobación")
    output.mkdir(parents=True, exist_ok=False)
    pc = load("reorg_own_jobs", root / "sistema/app/process_control.py")
    ui = root / "sistema/app/usar_dee.py"
    tracked = [ui, root / "sistema/gestionar.py", root / "sistema/contratos/ENTRADA_SENCILLA_APD03.json",
               root / "sistema/capacidades/asistente_apd03.py", root / "sistema/capacidades/lexico_generico_apd03_r02.py"]
    protected = [root / "sistema/estado/ACTIVO.json", root / "sistema/estado/vidas/APD03_MAIN/VIDA.json"]
    tracked += [p for p in protected if p.is_file()]
    frozen = [{"file": str(p), "bytes": p.stat().st_size, "sha256": sha(p)} for p in tracked]
    result = {"schema": "DEE.relocation.two_owner_verification.v1", "started_utc": datetime.now(timezone.utc).isoformat(),
              "root": str(root), "life": life, "source": config, "frozen_sources": frozen,
              "decoder": {"file": str(decoder_path), "sha256": DECODER_SHA},
              "new_ticks_authorized_only_in_clone": True, "runs": [], "cuts": [], "issues": [],
              "scope": "Operational regression, not new scientific capability, independent replica, T0 recreation or protected-life continuation"}
    write(output / "PROTOCOLO.json", {"scripts": SCRIPTS, "expected_words_after_native": EXPECTED_WORDS,
                                      "expected_MA_after_native": EXPECTED_MA, "maximum_sessions": 2,
                                      "no_teaching_no_repair_no_retry": True})
    try:
        probe = "import hashlib,json,pathlib,struct,sys,dee_thinking as d; p=pathlib.Path(d._native.__file__).resolve(); assert sys.version_info[:2]==(3,13) and struct.calcsize('P')==8; assert d.__version__=='4.5.0' and d.kernel_identity()['kernel_version']==27; h=hashlib.sha256(p.read_bytes()).hexdigest(); assert h=='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'; print(json.dumps({'python':sys.executable,'version':sys.version,'module':d.__file__,'native':str(p),'native_sha256':h,'kernel':d.kernel_identity()}))"
        p = subprocess.run([str(python), "-I", "-B", "-X", "utf8", "-c", probe], cwd=python.parent,
                           capture_output=True, text=True, encoding="utf8", timeout=30)
        result["official_import"] = {"exit_code": p.returncode, "stdout": p.stdout, "stderr": p.stderr,
                                      "native_ticks": 0}
        if p.returncode:
            raise RuntimeError("Importación/identidad oficial falló; no iniciar vida")
        for index, (label, script) in enumerate(SCRIPTS.items()):
            script_path = output / (label + "_GUION.json")
            write(script_path, script)
            argv = [str(python), "-I", "-B", "-X", "utf8", str(ui), "--raiz", str(root),
                    "--nueva" if index == 0 else "--vida", life, "--guion", str(script_path)]
            started = time.monotonic()
            with (output / (label + "_STDOUT.txt")).open("xb") as stdout, (output / (label + "_STDERR.txt")).open("xb") as stderr:
                process, job, job_name = pc.spawn_owned(argv, cwd=python.parent, stdout=stdout, stderr=stderr,
                                                       memory_limit=1073741824)
                try:
                    process.wait(timeout=options.session_seconds)
                    resources = pc.job_resources(job)
                    deadline = time.monotonic() + 5
                    while resources.get("job_active_processes") and time.monotonic() < deadline:
                        time.sleep(.02)
                        resources = pc.job_resources(job)
                    if resources.get("job_active_processes"):
                        raise RuntimeError("El Job propio sigue activo; no certificar STOP")
                finally:
                    pc.close_job(job)
            row = {"label": label, "argv": argv, "pid": process.pid, "job_name": job_name,
                   "exit_code": process.returncode, "wall_seconds": time.monotonic() - started, "resources": resources}
            result["runs"].append(row)
            write(output / (label + "_EJECUCION.json"), row)
            if process.returncode:
                raise RuntimeError("Fallo conservado en UI; no reintentar/importar otra copia")
            card = read(state_root / "vidas" / life / "VIDA.json")
            proto = read(protocol_root / life / "PROTOCOLO.json")
            snapshot = (root / "sistema" / card["snapshot"]).resolve(strict=True)
            if not snapshot.is_relative_to(state_root) or sha(snapshot) != card["snapshot_sha256"]:
                raise ValueError("Snapshot completo registrado ausente o modificado")
            sidecar = state_root / card["persistent_service"]["sidecar_directory"]
            queue = sidecar / "cola.sqlite3"
            if not queue.is_file():
                raise ValueError("No se guardó el diario operativo SQLite")
            wal = queue.with_name(queue.name + "-wal")
            if wal.is_file() and wal.stat().st_size:
                raise ValueError("Diario WAL todavía contiene datos; no comparar una vista immutable incompleta")
            with sqlite3.connect(queue.as_uri() + "?mode=ro&immutable=1", uri=True) as db:
                integrity = db.execute("PRAGMA integrity_check").fetchall()
                queue_counts = dict(db.execute("SELECT status, count(*) FROM requests GROUP BY status").fetchall())
                new_rows = db.execute("SELECT id, payload_sha, status FROM requests ORDER BY seq DESC LIMIT 20").fetchall()
            if integrity != [("ok",)]:
                raise ValueError("SQLite integrity_check no es ok")
            cut = {"life": card, "protocol": proto,
                   "native_snapshot": {"file": str(snapshot), "bytes": snapshot.stat().st_size, "sha256": sha(snapshot)},
                   "operational_queue": {"file": str(queue), "sha256": sha(queue), "integrity": integrity,
                                         "status_counts": queue_counts, "last20_id_hash_status": new_rows},
                   "sidecar_members": state_manifest(sidecar)}
            result["cuts"].append(cut)
            write(output / (label + "_CORTE.json"), cut)
            if card["life_id"] != life or card["world_id"] != life or card["parent"]["encoded_sha256"] != PARENT_SHA:
                raise ValueError("La identidad o padre cambió")
            if proto["pending_material"] is not None or proto["uncertain_preserved"]:
                raise ValueError("Estado operativo pendiente/incierto: conservar, no sustituir")
        events = [json.loads(line) for line in (protocol_root / life / "SESIONES.jsonl").read_text(encoding="utf8").splitlines() if line]
        starts = [e for e in events if e["event"] == "owned_start_paused"]
        stops = [e for e in events if e["event"] == "owned_stop"]
        imports = [e for e in events if e["event"] == "explicit_complete_paired_import"]
        reopens = [e for e in events if e["event"] == "same_personal_life_reopened"]
        if (len(starts), len(stops), len(imports), len(reopens)) != (2, 2, 1, 1):
            raise ValueError("Propietarios/importaciones no coinciden con la única genealogía")
        keys = ("N", "tick", "RAW_sha256", "clocks_sha256")
        if any(starts[1]["observation"]["physical"][k] != result["cuts"][0]["life"]["physical"][k] for k in keys):
            raise ValueError("Reapertura física diferente antes de nueva entrada")
        result["continuity"] = {"imports": 1, "reopens": 1, "owners": 2,
                                 "fingerprints_equal_before_new_input": True,
                                 "worker_PIDs": [s["observation"]["pid"] for s in starts]}
        material = [e for e in events if e["event"] == "literal_material_result"]
        submissions = [e for e in events if e["event"] == "literal_material_submission"]
        if len({e["id"] for e in submissions}) != len(submissions):
            raise ValueError("Solicitud material duplicada")
        modes = {}
        receipts = {}
        for event in material:
            request = event["result"]["request"]
            payload = json.loads(request["payload"])
            submitted = next(e for e in submissions if e["id"] == request["id"])
            if request["status"] != "completed" or submitted["payload"] != payload:
                raise ValueError("Recibo o payload de transporte no coincide")
            if hashlib.sha256(helper.canonical(payload).encode()).hexdigest() != request["payload_sha"]:
                raise ValueError("Hash exacto del payload cambió")
            modes.setdefault(payload["situaciones"][0]["modo"], []).append(event)
            for _, node in helper.walk(helper.body(event)):
                if isinstance(node, dict) and isinstance(node.get("receipt"), dict) and "id" in node["receipt"]:
                    r = node["receipt"]
                    old = receipts.get(r["id"])
                    if old is None or old["status"] == "scheduled":
                        receipts[r["id"]] = r
        panel = helper.body(modes["apd03-panel"][0])["rows"][0]
        words = helper.panel_map(helper.body(modes["apd03-panel"][0]))
        result["words_RAW"] = words
        if words != EXPECTED_WORDS:
            result["issues"].append("Panel heredado difiere de 14formas + luma+/nara−")
        memories = {}
        for item in panel["memories"]:
            readers = [node for _, node in helper.walk(item["result"]) if isinstance(node, dict) and isinstance(node.get("panel"), list) and len(node["panel"]) == 12]
            if len(readers) != 1:
                raise ValueError("Lectura MA ausente/ambigua")
            memories[item["context"]] = helper.sign(readers[0])
        result["MA_RAW"] = memories
        if memories != EXPECTED_MA:
            result["issues"].append("Memorias MA heredadas difieren")
        use = helper.body(modes["apd03-lenguaje"][0])["rows"][0]
        result["reopened_luma_use"] = {"form": use["literal_form"], "function_RAW": helper.sign(use["word"]["reader"]),
                                         "interaction_kind": use["interaction"].get("kind"), "datum": use["public_datum"],
                                         "context": use["operator_supplied_context"]}
        if result["reopened_luma_use"]["function_RAW"] != 1:
            result["issues"].append("Luma no conservó función+ después de reapertura")
        step = helper.body(modes["apd03-paso"][0])["rows"][0]
        result["goal_progress"] = step["progress"]
        result["goal_actions"] = []
        for item in step["opportunities"]:
            native = helper.action_sign(item["native_selection"]["reader"])
            effect = item["environment_effect"]
            expected_action = "ACT" if native == -1 else "QUERY" if native in (0, 1) else None
            if effect["selected_action"] != expected_action:
                raise ValueError("El comando ambiental no procede de la transducción RAW fija")
            numbers = []
            for numeric in item["native_numeric"]:
                trial = numeric["native_trial"]
                frame = next(f for f in trial["frames"] if f["tick"] == trial["datum_tick"] - 2)
                observation = frame["fields"]["C"]
                fields = helper.decoded(observation)
                if observation["site"] != [12, 17, 18] or not fields["active"] or fields["semantic"] != 1 or fields["direction"] != [1, -1, -1]:
                    raise ValueError("Puerta aritmética RAW no válida")
                value = fields["s_reg"] - (0 if numeric["operation"] == "suma" else 32)
                if value != numeric["numeric_reader"]["numeric_result"]:
                    raise ValueError("Resultado numérico no procede del RAW")
                numbers.append(value)
            committed = effect["committed_effect"]
            if committed is not None and (committed["provider_calls"] != {"native": 1, "external": 0} or len(numbers) != 1 or committed["raw_provider_response"]["value"] != numbers[0]):
                raise ValueError("Archivo objetivo depende de otro proveedor o número")
            result["goal_actions"].append({"native_RAW": native, "action": effect["selected_action"],
                                           "numbers_from_RAW": numbers, "completed": effect.get("final_goal_file_completed")})
        artifacts = []
        service_home = state_root / "servicios_locales" / life
        for _, node in helper.walk(step["operational_environment_state"]):
            if isinstance(node, dict) and {"relative_path", "bytes", "sha256", "content_base64"} <= set(node):
                candidates = [p for p in service_home.rglob(node["relative_path"]) if p.is_file() and p.stat().st_size == node["bytes"] and sha(p) == node["sha256"]]
                if len(candidates) != 1:
                    raise ValueError("Artefacto real ausente/ambiguo")
                actual = read(candidates[0])
                artifacts.append({"file": str(candidates[0]), "bytes": node["bytes"], "sha256": node["sha256"], "body": actual})
                if actual.get("operands") != [18, 9] or actual.get("value") != 27 or actual.get("procedure") != "native" or actual.get("operation") != "add":
                    result["issues"].append("Archivo objetivo real no coincide con solicitud18+9")
        result["actual_artifacts"] = artifacts
        if not step["progress"]["verified_file_goal_completed"]:
            result["issues"].append("Objetivo no concluido en4oportunidades; futuro adverso conservado sinretry")
        result["native_inputs"] = {"unique": len(receipts), "statuses": dict(Counter(r["status"] for r in receipts.values()))}
        result["source_and_protected_files_unchanged"] = all(sha(p["file"]) == p["sha256"] for p in frozen)
        if not result["source_and_protected_files_unchanged"]:
            raise ValueError("Cambió una fuente/vida protegida durante la prueba")
        result["final_operational_members"] = {"life": state_manifest(state_root / "vidas" / life),
                                                "protocol": state_manifest(protocol_root / life)}
        result["finished_utc"] = datetime.now(timezone.utc).isoformat()
        return result
    except BaseException as error:
        result["execution_error"] = {"type": type(error).__name__, "message": str(error),
                                     "future_preserved_no_retry": True}
        raise
    finally:
        sessions = protocol_root / life / "SESIONES.jsonl"
        if sessions.is_file():
            shutil.copyfile(sessions, output / "SESIONES_ORIGINALES.jsonl")
        write(output / "RESULTADO_REUBICACION.json", result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--decoder", type=Path, required=True)
    parser.add_argument("--salida", type=Path, required=True)
    parser.add_argument("--vida", default="REORG_APD03_01")
    parser.add_argument("--session-seconds", type=float, default=600)
    parser.add_argument("--ejecutar-native", action="store_true")
    options = parser.parse_args()
    if not options.ejecutar_native:
        raise SystemExit("Preparado, no se avanzan ticks sin GO explícito de Root --ejecutar-native")
    result = run(options)
    print(json.dumps({"issues": result["issues"], "runs": len(result["runs"]), "final_tick": result["cuts"][-1]["life"]["physical"]["tick"], "native_inputs": result.get("native_inputs")}, ensure_ascii=False))
    raise SystemExit(bool(result["issues"]))
