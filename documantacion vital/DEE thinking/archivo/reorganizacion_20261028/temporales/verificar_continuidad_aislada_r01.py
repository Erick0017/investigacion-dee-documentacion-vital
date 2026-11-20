"""Prueba operativa acotada, exclusivamente sobre una copia completa.

Por defecto sólo muestra el plan; --ejecutar habilita la copia y sus ticks.
No importa el motor en este proceso. El único propietario nuevo lo administra
la aplicación existente de la copia mediante sus protocolos ordinarios.
"""
from __future__ import annotations

from pathlib import Path
import argparse
import hashlib
import http.client
import importlib.util
import json
import os
import shutil
import socket
import sqlite3
import subprocess
import sys
import time
import traceback
import uuid

# El registro y los cambios técnicos usan el único registro de la tarea raíz.
BASE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("reorganizar_dee", BASE / "reorganizar_dee.py")
reorg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reorg)
ROOT = reorg.ROOT.resolve()
ORIGINAL = ROOT / "DEE Cognitive 2.0"
CLONE = ROOT / "archivo/_prueba_aislada"
RESGUARDO = ROOT / "archivo/_resguardo_operativo"
LIFE = "DEE20_DEMO_01"
PORT = 8894
EXPECTED = {
    "N": 67, "tick": 697764,
    "RAW_sha256": "c2e2821413ba3fdda696532c5480841fe0604b1fc3777f29e8b2141b1ba7e96d",
    "clocks_sha256": "3e5a3e67237290b531467921e20d3456c60f32f7a570adca76a31e567115b86f",
}
SNAPSHOT_SHA = "3ad3e16b772e8ea44a7814c197651d4cb8d841c8739a1950ad2f0e6953884b8f"
QUERY = "palabra luma --retorno omit --actuador nulled"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    return reorg.sha(path)


def log(stage, **details):
    value = reorg.read()
    proof = value.setdefault("prueba_operativa_aislada", {})
    proof.setdefault("eventos", []).append({"utc": reorg.now(), "etapa": stage, **details})
    reorg.write(value)


def assert_inside(path):
    value = path.resolve()
    if not value.is_relative_to(ROOT) or value == ROOT:
        raise ValueError("Destino fuera de la raíz autorizada: " + str(value))
    return value


def card(root):
    value = read(root / "sistema/estado/vidas" / LIFE / "VIDA.json")
    assert value["life_id"] == LIFE and value["world_id"] == LIFE
    return value


def physical(value):
    return {k: value[k] for k in EXPECTED}


def selected_db(root):
    return root / "sistema/estado/servicios_persistentes" / LIFE / "cola.sqlite3"


def database_status(path):
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=5) as db:
        integrity = db.execute("PRAGMA quick_check").fetchone()[0]
        counts = dict(db.execute("SELECT status,count(*) FROM requests GROUP BY status"))
        owner = db.execute("SELECT value FROM meta WHERE key='owner'").fetchone()
        owner = json.loads(owner[0]) if owner else None
        outstanding = db.execute("SELECT count(*) FROM requests WHERE status IN ('queued','processing','uncertain')").fetchone()[0]
    return {"integrity": integrity, "counts": counts, "outstanding": outstanding, "owner": owner}


def source_signature(root):
    rows = []
    for folder, dirs, files in os.walk(root, followlinks=False):
        for name in dirs:
            p = Path(folder) / name
            if p.is_symlink() or (hasattr(p, "is_junction") and p.is_junction()):
                raise RuntimeError("La copia exige resolver explícitamente un reparse point: " + str(p))
        for name in files:
            p = Path(folder) / name
            if p.is_symlink():
                raise RuntimeError("Enlace no autorizado dentro del paquete: " + str(p))
            # WAL/SHM pueden variar por lectores; se copian coherentemente con backup.
            if name.endswith(("-wal", "-shm")):
                continue
            st = p.stat()
            rows.append([p.relative_to(root).as_posix(), st.st_ino, st.st_size, st.st_mtime_ns])
    rows.sort()
    return {"files": len(rows), "bytes": sum(r[2] for r in rows),
            "sha256_relative_path_fileid_size_mtime": hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()}


def copy_complete():
    before = card(ORIGINAL)
    assert physical(before["physical"]) == EXPECTED
    snapshot = (ORIGINAL / "sistema" / before["snapshot"]).resolve(strict=True)
    assert snapshot.is_relative_to((ORIGINAL / "sistema/estado").resolve())
    assert sha(snapshot) == before["snapshot_sha256"] == SNAPSHOT_SHA
    status = database_status(selected_db(ORIGINAL))
    assert status["integrity"] == "ok" and status["outstanding"] == 0
    assert status["owner"] and status["owner"]["running"] is False
    assert physical(status["owner"]["physical"]) == EXPECTED
    signature = source_signature(ORIGINAL)
    log("previo", original=str(ORIGINAL), copia=str(CLONE), vida=LIFE,
        physical=EXPECTED, snapshot_sha256=SNAPSHOT_SHA, source_signature=signature,
        original_owner_running=False, outstanding=0,
        scope="Comprobación breve de traslado; no réplica científica ni creación desde T0")
    shutil.copytree(ORIGINAL, CLONE, copy_function=shutil.copy2,
                    ignore=lambda p, names: [n for n in names if n.endswith(("-wal", "-shm"))])
    copied_sqlite = []
    for source in ORIGINAL.rglob("*"):
        if not source.is_file() or source.suffix.lower() not in {".sqlite", ".sqlite3", ".db"}:
            continue
        with source.open("rb") as stream:
            if stream.read(16) != b"SQLite format 3\x00":
                continue
        target = CLONE / source.relative_to(ORIGINAL)
        temporary = target.with_name(target.name + ".coherent_backup")
        assert not temporary.exists()
        with sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True, timeout=5) as src:
            with sqlite3.connect(temporary) as dst:
                src.backup(dst)
                dst.execute("PRAGMA journal_mode=DELETE")
                dst.commit()
                assert dst.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        os.replace(temporary, target)
        copied_sqlite.append(str(target.relative_to(CLONE)))
    assert source_signature(ORIGINAL) == signature, "El origen cambió durante la copia; no se prueba un corte incoherente"
    copied = card(CLONE)
    assert copied == before and sha(CLONE / "sistema" / copied["snapshot"]) == SNAPSHOT_SHA
    assert database_status(selected_db(CLONE))["outstanding"] == 0
    # Condiciones anfitrión de la copia: el propietario se limita a180s y cada
    # espera de transporte a60s. No cambian RAW, clocks, agenda ni docencia.
    selection = CLONE / "aplicacion/GENESIS/SELECCION_CANDIDATA.json"
    config = read(selection)
    old_config_sha = sha(selection)
    config.update(owner_max_seconds=180, start_wait_seconds=40,
                  control_wait_seconds=40, material_wait_seconds=60, stop_wait_seconds=40)
    selection.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    log("copia_completa", sqlite_coherent_backups=copied_sqlite,
        source_unchanged=True, physical_equal=True, snapshot_equal=True,
        clone_wait_configuration={"original_sha256": old_config_sha, "copy_sha256": sha(selection),
                                  "scope": "Sólo plazos anfitrión de supervisión; ninguna escritura física"})
    return before, signature


class App:
    def __init__(self, deadline, ordinal):
        self.deadline = deadline
        self.ordinal = ordinal
        self.token = None
        self.process = None
        self.streams = []

    def remaining(self, maximum=20):
        seconds = self.deadline - time.monotonic()
        if seconds <= 0:
            raise TimeoutError("Se agotó el límite de300s de la prueba operativa")
        return min(maximum, seconds)

    def request(self, method, path, data=None):
        connection = http.client.HTTPConnection("127.0.0.1", PORT, timeout=self.remaining(15))
        try:
            headers = {"Content-Type": "application/json"}
            if self.token:
                headers["X-Genesis-Token"] = self.token
            raw = json.dumps(data or {}, ensure_ascii=False).encode() if method == "POST" else None
            connection.request(method, path, body=raw, headers=headers)
            response = connection.getresponse()
            value = json.loads(response.read())
            if response.status >= 300:
                raise RuntimeError("HTTP" + str(response.status) + ":" + str(value))
            return value
        finally:
            connection.close()

    def status(self):
        value = self.request("GET", "/api/status")
        assert value["life_id"] == LIFE and value["record"]["world_id"] == LIFE
        return value

    def start(self):
        log_dir = CLONE / "sistema/estado/prueba_reorganizacion"
        log_dir.mkdir(exist_ok=True)
        self.streams = [(log_dir / (str(self.ordinal) + "_GUI_STDOUT.txt")).open("x", encoding="utf8"),
                        (log_dir / (str(self.ordinal) + "_GUI_STDERR.txt")).open("x", encoding="utf8")]
        args = [str(CLONE / "motor/python313/python.exe"), "-I", "-B", "-X", "utf8",
                str(CLONE / "aplicacion/GENESIS/genesis.py"), "--vida", LIFE,
                "--diagnostico", "--puerto", str(PORT), "--sin-navegador"]
        self.process = subprocess.Popen(args, cwd=CLONE / "motor/python313",
                                        stdout=self.streams[0], stderr=self.streams[1],
                                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        ready_until = min(self.deadline, time.monotonic() + 45)
        while time.monotonic() < ready_until:
            if self.process.poll() is not None:
                raise RuntimeError("La GUI de la copia salió antes de readiness; consulte logs locales")
            try:
                session = self.request("GET", "/api/session")
                assert Path(session["application_root"]).resolve() == CLONE.resolve(), "Puerto de otra aplicación"
                assert session["version"].startswith("DEE.Cognitive.2.0.local.")
                self.token = session["token"]  # Nunca se imprime ni se serializa.
                current = self.status()
                assert current["owned_by_this_app"] is False and current["pending"] is None
                return current
            except (OSError, http.client.HTTPException):
                time.sleep(.2)
        raise TimeoutError("La interfaz de copia no confirmó su raíz y vida dentro del plazo")

    def submit(self, action, value=None, wait=True):
        row = self.request("POST", "/api/action", {"action": action, "value": value})
        if not wait:
            return row["id"]
        return self.wait(row["id"])

    def wait(self, job_id):
        while True:
            status = self.status()
            row = next((j for j in status["jobs"] if j["id"] == job_id), None)
            if row and row["status"] in {"completed", "error"}:
                if row["status"] == "error":
                    raise RuntimeError("Operación de copia fallida:" + str(row["error"]))
                return row["result"]
            self.remaining()
            if self.process.poll() is not None:
                raise RuntimeError("Terminó la GUI durante una operación; no se reenvía el material")
            time.sleep(.15)

    def close(self):
        if self.process is None:
            return
        try:
            if self.process.poll() is None:
                # Sólo el propietario administrado por ESTA copia. No señales ni
                # terminaciones de PID ajenos; una operación no se reenvía.
                status = self.status()
                if status.get("owned_by_this_app"):
                    self.submit("detener")
                status = self.status()
                assert not status["owned_by_this_app"] and status["pending"] is None
                self.request("POST", "/api/shutdown", {})
                self.process.wait(timeout=self.remaining(20))
        finally:
            for stream in self.streams:
                stream.close()
            self.token = None


def owner_value(status):
    value = status["owner"]
    for key in ("OBSERVACION", "observation", "ESTADO_PUBLICADO"):
        if isinstance(value, dict) and key in value:
            value = value[key]
    if isinstance(value, dict) and "physical" in value:
        return value
    # El gestor devuelve habitualmente {INSTRUMENTO,OBSERVACION_CACHED}.
    def find(v):
        if isinstance(v, dict):
            if "physical" in v and "running" in v:
                return v
            for x in v.values():
                found = find(x)
                if found:
                    return found
        return None
    result = find(value)
    if result is None:
        raise ValueError("Estado del propietario sin observación física reconocible")
    return result


def transport_result(result):
    row = result.get("request", result)
    assert row.get("status") == "completed", "La petición material no confirmó finalización"
    value = row["result"]
    return json.loads(value) if isinstance(value, str) else value


def run():
    for p in (ORIGINAL, CLONE, RESGUARDO):
        assert_inside(p)
    assert ORIGINAL.is_dir() and not CLONE.exists() and not RESGUARDO.exists(), "No se sobrescribe una prueba o resguardo anterior"
    with socket.socket() as probe:
        if probe.connect_ex(("127.0.0.1", PORT)) == 0:
            raise RuntimeError("Puerto8894 ocupado; no se cierra ni reutiliza otro proceso")
    before, signature = copy_complete()
    protected = False
    app = None
    success = False
    try:
        # Rename atómico, mismo volumen y destinos validados. Original sólo
        # cambia de nombre provisionalmente; jamás recibe la copia evolucionada.
        assert ORIGINAL.drive.lower() == RESGUARDO.drive.lower()
        log("resguardo_preparado", source=str(ORIGINAL), target=str(RESGUARDO))
        os.rename(ORIGINAL, RESGUARDO)
        protected = True
        assert not ORIGINAL.exists() and RESGUARDO.is_dir()
        log("resguardo_atomico_confirmado", original_unavailable_during_test=True)
        deadline = time.monotonic() + 300
        app = App(deadline, 1)
        start_status = app.start()
        assert physical(start_status["record"]["physical"]) == EXPECTED
        app.submit("abrir")
        opened = app.status()
        initial_owner = owner_value(opened)
        assert initial_owner["running"] and initial_owner["paused"]
        assert physical(initial_owner["physical"]) == EXPECTED
        assert opened["record"]["parent"] == before["parent"]
        log("primera_apertura_N0", application_root=str(CLONE), vida=LIFE,
            physical=physical(initial_owner["physical"]), parent=before["parent"],
            copy_gui_pid=app.process.pid, no_T0=True)
        app.submit("vivir")
        result = app.submit("ejecutar", {"texto": QUERY, "id": "reorganizacion_luma_" + uuid.uuid4().hex[:12]})
        material = transport_result(result)
        rows = material["result"]["rows"]
        assert len(rows) == 1 and rows[0]["form"] == "luma"
        requests = rows[0]["requests"]
        assert len(requests) == 7, "El protocolo de consulta cambió: no ampliar ni reinterpretar automáticamente"
        assert not rows[0].get("teacher_correct_function_or_expected_sign_supplied")
        reader = rows[0]["reader"]
        receipts = [r.get("receipt", {}) for r in requests]
        log("consulta_nueva_sobre_copia", comando=QUERY, before_tick=material["before_tick"],
            after_tick=material["after_tick"], native_requests=7,
            receipts=receipts, reader=reader,
            qualified=reader.get("formed_native_command") in (-1, 1) and not reader.get("ambiguous"),
            claims="Sólo respuesta a forma finita; no auditoría general ni dominio de lenguaje")
        app.submit("pausar")
        app.submit("guardar")
        paused = app.status()
        assert paused["pending"] is None and not paused["uncertain"]
        assert owner_value(paused)["paused"] is True
        app.submit("detener")
        app.close()
        app = None
        first_saved = card(CLONE)
        assert first_saved["physical"]["tick"] > EXPECTED["tick"]
        assert first_saved["parent"] == before["parent"]
        assert first_saved["life_id"] == before["life_id"] and first_saved["world_id"] == before["world_id"]
        assert database_status(selected_db(CLONE))["outstanding"] == 0
        log("corte_guardado", physical=physical(first_saved["physical"]), snapshot=first_saved["snapshot"],
            snapshot_sha256=first_saved["snapshot_sha256"], same_life_and_parent=True)
        app = App(deadline, 2)
        app.start()
        app.submit("abrir")
        reopened = app.status()
        reopened_owner = owner_value(reopened)
        assert reopened_owner["running"] and reopened_owner["paused"]
        assert physical(reopened_owner["physical"]) == physical(first_saved["physical"])
        assert reopened["record"]["parent"] == before["parent"]
        assert reopened["pending"] is None and not reopened["uncertain"]
        log("segundo_proceso_N0", copy_gui_pid=app.process.pid,
            physical=physical(reopened_owner["physical"]), same_life=LIFE,
            same_parent=True, no_import_no_T0_no_extra_material=True)
        app.submit("guardar")
        app.submit("detener")
        app.close()
        app = None
        final = card(CLONE)
        assert physical(final["physical"]) == physical(first_saved["physical"])
        assert database_status(selected_db(CLONE))["outstanding"] == 0
        success = True
        log("resultado", status="COMPLETED_WITH_READER_RESULT_RECORDED", final_copy_state=physical(final["physical"]),
            response_qualified=reader.get("formed_native_command") in (-1, 1) and not reader.get("ambiguous"),
            proof_scope=["motor importado por aplicación local", "copia completa y SQLite coherente", "apertura pausada sin ticks",
                         "consulta nueva finita con retorno omitido y actuador anulado", "guardar y cerrar propietario",
                         "reabrir misma vida y estado físico en segundo proceso sin importación ni T0"],
            not_proved=["todas las capacidades científicas", "episodios externos", "aprendizaje nuevo", "validez universal del lector"],
            mutated_copy_preserved=str(CLONE))
    except BaseException as error:
        log("fallo_prueba_copia", type=type(error).__name__, detail=str(error),
            traceback=traceback.format_exc(), no_retry_no_rewind=True)
        raise
    finally:
        if app is not None:
            try:
                app.close()
            except BaseException as error:
                log("cierre_copia_no_confirmado", type=type(error).__name__, detail=str(error),
                    process_pid=app.process.pid if app.process else None,
                    action="No se mató ni sustituyó un propietario. Se conserva el estado y los logs de la copia.")
        if protected:
            assert not ORIGINAL.exists() and RESGUARDO.is_dir(), "Restauración requiere original ausente y resguardo presente"
            os.rename(RESGUARDO, ORIGINAL)
            restored = card(ORIGINAL)
            assert restored == before and source_signature(ORIGINAL) == signature
            assert sha(ORIGINAL / "sistema" / restored["snapshot"]) == SNAPSHOT_SHA
            log("original_restituido", path=str(ORIGINAL), original_unchanged=True,
                original_physical=physical(restored["physical"]), success=success)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ejecutar", action="store_true", help="Autoriza ejecutar únicamente la prueba acotada de la copia")
    args = parser.parse_args()
    if not args.ejecutar:
        print("Sólo preparación. Para ejecutar: este script --ejecutar")
        print("Copia:", CLONE)
        print("Vida heredada:", LIFE, "T", EXPECTED["tick"], "N", EXPECTED["N"])
        print("Consulta:", QUERY)
        print("Registros: únicamente", reorg.LOG)
    else:
        run()
        print("Prueba de copia terminada; resultado y alcance en", reorg.LOG)
