"""APD03: una terminal, un propietario y transporte literal; no decisor DEE.

Se instala en sistema/app/usar_dee.py de Cognitive y su distribución. Este supervisor no importa el motor,
no calcula respuestas y no lee los diarios de evidencia para decidir. Los
resultados e IDs pendientes pertenecen al protocolo operativo, no a una memoria
cognitiva. Las pruebas N0 inyectan un backend falso, expresamente identificado.
"""
from __future__ import annotations

import argparse
import contextlib
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time
import uuid

VERSION = "APD04.single_terminal.R03.two_balanced_pairs_candidate"
TERMINAL = {"completed", "failed_preserved", "uncertain", "rejected_invalid"}
ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,90}")


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_atomic(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    with temporary.open("x", encoding="utf8", newline="\n") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def identifier(value):
    if not isinstance(value, str) or not ID_RE.fullmatch(value) or value.endswith("."):
        raise ValueError("Identidad portable requerida; sin rutas ni puntos finales.")
    if value.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL", *("COM"+str(i) for i in range(1, 10)), *("LPT"+str(i) for i in range(1, 10))}:
        raise ValueError("Nombre de dispositivo Windows no permitido.")
    return value


def row_of(value):
    return value.get("request") or value


def observation(value):
    return value.get("observation") or value.get("owner") or value


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def default_root(script_path):
    """Sólo ancestros del ejecutable; no rastrea discos ni históricos."""
    script_path = Path(script_path).resolve()
    for candidate in (script_path.parent, *list(script_path.parents)[1:4]):
        if (candidate / "actualizaciones/arrancar.py").is_file() or (candidate / "sistema/gestionar.py").is_file():
            return candidate
    return script_path.parent


def selected_config_path(root):
    """Un único contrato se distribuye mediante el actualizador ya existente."""
    return Path(root) / "sistema/contratos/ENTRADA_SENCILLA_APD03.json"


class SessionLock:
    """Exclusión del supervisor; la exclusión real del Runtime sigue en el gestor."""
    def __init__(self, path):
        self.path, self.stream = Path(path), None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.stream = self.path.open("a+b")
        try:
            self.stream.seek(0)
            if not self.stream.read(1):
                self.stream.write(b"0")
                self.stream.flush()
            self.stream.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.stream.close()
            self.stream = None
            raise RuntimeError("Ya existe un supervisor para esta vida; no se inicia otro propietario.")
        return self

    def __exit__(self, *_):
        if self.stream:
            self.stream.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(), fcntl.LOCK_UN)
            self.stream.close()
            self.stream = None


class DistributionBackend:
    """Sólo el lanzador/gestor existente administra el mundo y sus solicitudes."""
    def __init__(self, root, config):
        self.root, self.config = Path(root).resolve(), config
        self.launcher = self.root / "actualizaciones/arrancar.py"
        self.python = self.root / "motor/python313/python.exe"
        self.process = self.job = self.pc = None
        self.streams = []
        if config.get("status") != "CLOSED_SELECTED_FOR_USE":
            raise ValueError("Entrada candidata: falta seleccionar y cerrar un corte operativo. No se crea una vida.")
        if not self.launcher.is_file() or not self.python.is_file():
            raise FileNotFoundError("Extraiga el paquete completo; faltan lanzador o CPython 3.13 incluido.")

    def manager(self, args, timeout=None):
        command = [str(self.python), "-I", "-B", "-X", "utf8", str(self.launcher), "gestor", *map(str, args)]
        result = subprocess.run(command, cwd=self.python.parent, text=True, encoding="utf8", capture_output=True, timeout=timeout)
        if result.returncode:
            raise RuntimeError((result.stderr or result.stdout).strip())
        return json.loads(result.stdout)

    def record(self, life):
        return read(self.root / "trabajo_personal/estado/vidas" / life / "VIDA.json")

    @property
    def protocol_home(self):
        return self.root / "trabajo_personal/entrada_sencilla/vidas"

    def owner_argv(self, life):
        return [str(self.python), "-I", "-B", "-X", "utf8", str(self.launcher), "gestor", "mente-unificada-iniciar", "--vida", life,
                "--backend", "mente_unificada", "--pausado", "--intervalo", str(self.config["idle_interval_seconds"]),
                "--max-segundos", str(self.config["owner_max_seconds"])]

    def import_new(self, life):
        # La implementación existente reconstruye y comprueba TODO el par.
        launcher = load_module("dee_single_entry_launcher", self.launcher)
        launcher.prepare()
        selected = next((r for r in launcher.catalog() if r["alias"] == self.config["source_alias"]), None)
        if not selected or not selected.get("persistent_service"):
            raise ValueError("El alias seleccionado carece de paquete emparejado completo.")
        if selected["snapshot_sha256"] != self.config["source_snapshot_sha256"]:
            raise ValueError("El catálogo cambió respecto del corte seleccionado; no se elige otro futuro.")
        if (self.root / "trabajo_personal/estado/vidas" / life / "VIDA.json").exists():
            raise FileExistsError("La vida ya existe; utilice --vida para continuarla.")
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            result = launcher.open_copy(self.config["source_alias"], life, activate=False)
        card = self.record(life)
        if card.get("parent", {}).get("encoded_sha256") != selected["snapshot_sha256"]:
            raise ValueError("El par importado no acredita el padre seleccionado; se conserva para diagnóstico.")
        return {"result": result, "record": card, "selected": selected, "import_log": captured.getvalue()}

    def start(self, life, directory):
        if self.process is not None:
            raise RuntimeError("Este supervisor ya tiene un propietario; no se crea otro.")
        cached = observation(self.manager(["mente-unificada-estado", "--vida", life]))
        if cached.get("running"):
            raise RuntimeError("El diario registra otro propietario activo o no cerrado. No se termina ni reinicia automáticamente.")
        if cached.get("uncertain_external_result"):
            raise RuntimeError("Hay un efecto incierto preservado; no se reanuda ni repite automáticamente.")
        self.pc = load_module("dee_single_entry_process_control", self.root / "sistema/app/process_control.py")
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        self.streams = [(directory / "OWNER_STDOUT.txt").open("x", encoding="utf8"), (directory / "OWNER_STDERR.txt").open("x", encoding="utf8")]
        command = self.owner_argv(life)
        begun = time.time()
        self.process, self.job, name = self.pc.spawn_owned(command, cwd=self.python.parent, stdout=self.streams[0], stderr=self.streams[1], memory_limit=self.config["memory_limit_bytes"])
        deadline = time.monotonic() + self.config["start_wait_seconds"]
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError("El propietario salió antes de estar disponible. Se conservan sus registros; no se sustituye la vida.")
            state = observation(self.manager(["mente-unificada-estado", "--vida", life]))
            if state.get("running") and state.get("wall_utc") and datetime.fromisoformat(state["wall_utc"]).timestamp() >= begun:
                return {"pid": self.process.pid, "job_name": name, "observation": state, "started_paused": True}
            time.sleep(.1)
        raise TimeoutError("No se confirmó el propietario dentro del plazo; no se inicia otro.")

    def finish_owned(self, timeout):
        if self.process is None:
            return {"owned_process": False}
        self.process.wait(timeout=timeout)
        resources = self.pc.job_resources(self.job)
        limit = time.monotonic() + 5
        samples = [resources]
        while resources.get("job_active_processes") and time.monotonic() < limit:
            time.sleep(.02)
            resources = self.pc.job_resources(self.job)
            samples.append(resources)
        if resources.get("job_active_processes"):
            raise RuntimeError("El Job propio aún contiene procesos; no se certifica detención completa.")
        self.pc.close_job(self.job)
        result = {"owned_process": True, "pid": self.process.pid, "exit_code": self.process.returncode, "resources": resources,
                  "bounded_exit_grace_samples": samples}
        self.job = self.process = None
        for stream in self.streams:
            stream.close()
        self.streams = []
        return result


class OriginalBackend(DistributionBackend):
    """Misma supervisión con el gestor original; importa sólo el par declarado.

    No busca otro entorno, no reinstala y no modifica el activo. Root decide
    el corte y ejecuta este archivo con el CPython 3.13 ya operativo.
    """
    def __init__(self, root, config):
        self.root, self.config = Path(root).resolve(), config
        self.launcher = self.root / "sistema/gestionar.py"
        self.python = Path(sys.executable)
        self.process = self.job = self.pc = None
        self.streams = []
        if config.get("status") != "CLOSED_SELECTED_FOR_USE":
            raise ValueError("Entrada candidata: falta seleccionar y cerrar un corte operativo.")
        if sys.version_info[:2] != (3, 13) or not self.launcher.is_file():
            raise ValueError("Use el CPython 3.13 x64 existente y la raíz original correcta; no se instala otro.")

    @property
    def protocol_home(self):
        return self.root / "sistema/estado/entrada_sencilla/vidas"

    def manager(self, args, timeout=None):
        command = [str(self.python), "-I", "-B", "-X", "utf8", str(self.launcher), *map(str, args)]
        result = subprocess.run(command, cwd=self.python.parent, text=True, encoding="utf8", capture_output=True, timeout=timeout)
        if result.returncode:
            raise RuntimeError((result.stderr or result.stdout).strip())
        return json.loads(result.stdout)

    def record(self, life):
        return read(self.root / "sistema/estado/vidas" / life / "VIDA.json")

    def import_new(self, life):
        paired = (self.root / self.config["source_paired_export_manifest"]).resolve(strict=True)
        if not paired.is_relative_to(self.root) or paired.name != "EXPORTACION_SERVICIO.json":
            raise ValueError("El par seleccionado debe permanecer dentro del sistema original.")
        if hashlib.sha256(paired.read_bytes()).hexdigest() != self.config["paired_export_manifest_sha256"]:
            raise ValueError("Cambió el manifiesto emparejado seleccionado; no se sustituye el pasado.")
        if (self.root / "sistema/estado/vidas" / life / "VIDA.json").exists():
            raise FileExistsError("La vida ya existe; utilice --vida para continuarla.")
        result = self.manager(["mente-unificada-importar", "--paquete", str(paired.parent), "--vida", life])
        card = self.record(life)
        if card.get("parent", {}).get("encoded_sha256") != self.config["source_snapshot_sha256"]:
            raise ValueError("La importación no acredita el padre físico declarado; se conserva el estado para diagnóstico.")
        selected = {"source_life": self.config["source_life"], "snapshot_sha256": self.config["source_snapshot_sha256"]}
        return {"result": result, "record": card, "selected": selected}

    def owner_argv(self, life):
        return [str(self.python), "-I", "-B", "-X", "utf8", str(self.launcher), "mente-unificada-iniciar", "--vida", life,
                "--backend", "mente_unificada", "--pausado", "--intervalo", str(self.config["idle_interval_seconds"]),
                "--max-segundos", str(self.config["owner_max_seconds"])]


class Supervisor:
    def __init__(self, root, life, backend, config):
        self.root, self.life, self.backend, self.config = Path(root), identifier(life), backend, config
        self.folder = self.backend.protocol_home / self.life
        self.state_path = self.folder / "PROTOCOLO.json"
        self.state = read(self.state_path) if self.state_path.exists() else {
            "schema": "DEE.simple_entry.protocol.v1", "life_id": self.life, "world_id": None,
            "source_snapshot_sha256": None, "pending_material": None, "uncertain_preserved": False,
            "history_is_transport_not_native_memory": True, "never_automatic_material_retry": True}
        if self.state.get("life_id") != self.life:
            raise ValueError("El protocolo pertenece a otra identidad; no se reconstruye.")
        self.owned = False

    def save_protocol(self):
        write_atomic(self.state_path, self.state)

    def log(self, event, **fields):
        self.folder.mkdir(parents=True, exist_ok=True)
        value = {"wall_utc": now(), "version": VERSION, "life_id": self.life, "event": event, **fields}
        with (self.folder / "SESIONES.jsonl").open("a", encoding="utf8", newline="\n") as stream:
            stream.write(canonical(value) + "\n")

    def open(self, new=False):
        if new:
            if self.state_path.exists():
                raise FileExistsError("Existe protocolo de esta vida; no se sobrescribe ni rebobina.")
            imported = self.backend.import_new(self.life)
            card = imported["record"]
            self.state.update(world_id=card["world_id"], source_snapshot_sha256=imported["selected"]["snapshot_sha256"],
                              source_life=imported["selected"]["source_life"], imported_at=now())
            self.save_protocol()
            self.log("explicit_complete_paired_import", world_id=card["world_id"], source_snapshot_sha256=self.state["source_snapshot_sha256"],
                     no_T0=True, no_ACTIVO_replacement=True)
        else:
            if not self.state_path.is_file() or not self.state.get("world_id"):
                raise FileNotFoundError("No hay copia personal registrada. Use --nueva IDENTIDAD_NUEVA una sola vez.")
            card = self.backend.record(self.life)
            if card["world_id"] != self.state["world_id"] or card["life_id"] != self.life:
                raise ValueError("La vida y el protocolo no coinciden; no se importa un sustituto.")
            self.log("same_personal_life_reopened", world_id=card["world_id"], tick=card["physical"]["tick"])
        return self.backend.record(self.life)

    def status(self):
        result = self.backend.manager(["mente-unificada-estado", "--vida", self.life])
        return {"INSTRUMENTO": {"entry_version": VERSION, "life_id": self.life, "world_id": self.state["world_id"],
                "supervisor_owns_process": self.owned, "pending_material_id": (self.state.get("pending_material") or {}).get("id"),
                "uncertain_preserved": self.state.get("uncertain_preserved"), "no_material_probe": True}, "ESTADO_PUBLICADO": result}

    def start(self):
        if self.owned:
            raise RuntimeError("Un propietario ya está iniciado por esta sesión.")
        if self.state.get("uncertain_preserved"):
            raise RuntimeError("Incertidumbre preservada: examine el mismo ID; no reanude ni repita.")
        session = self.folder / ("sesion_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8])
        try:
            result = self.backend.start(self.life, session)
        except BaseException:
            # Un proceso pudo iniciarse antes del error de readiness. La propiedad
            # no se pierde: close() intentará STOP, sin crear un segundo Runtime.
            self.owned = getattr(self.backend, "process", None) is not None
            raise
        self.owned = True
        self.log("owned_start_paused", **result)
        return result

    def control(self, operation):
        if operation not in {"pausar", "reanudar", "guardar", "detener", "exportar"}:
            raise ValueError("Control no admitido por la entrada sencilla.")
        if not self.owned:
            raise RuntimeError("Inicie/continúe primero el propietario en esta misma sesión.")
        if operation == "reanudar" and self.state.get("uncertain_preserved"):
            raise RuntimeError("No se reanuda un efecto incierto.")
        request_id = "ui_c_" + uuid.uuid4().hex
        wait = self.config["control_wait_seconds"]
        self.log("literal_control", operation=operation, id=request_id)
        result = self.backend.manager(["mente-unificada-"+operation, "--vida", self.life, "--id", request_id, "--esperar", str(wait)], timeout=wait+30)
        self.log("control_result", operation=operation, id=request_id, result=result)
        if row_of(result).get("status") != "completed":
            raise RuntimeError("Control no confirmado. Conserve el ID " + request_id + "; no se repite automáticamente.")
        if operation == "detener":
            closed = self.backend.finish_owned(self.config["stop_wait_seconds"])
            self.owned = False
            self.log("owned_stop", result=closed)
        return result

    def result(self, request_id=None):
        pending = self.state.get("pending_material")
        request_id = identifier(request_id or (pending or {}).get("id", ""))
        result = self.backend.manager(["mente-unificada-resultado", "--vida", self.life, "--id", request_id])
        row = result.get("request")
        if pending and request_id == pending["id"]:
            if row is not None and row.get("id") != request_id:
                raise ValueError("El gestor devolvió otra petición; no se cambia el ID.")
            if row and row.get("payload_sha") != pending["payload_sha256"]:
                raise ValueError("La carga del ID pendiente difiere; no se sustituye ni repite.")
            if row and row.get("status") in TERMINAL:
                self.state["pending_material"] = None
                self.state["uncertain_preserved"] = self.state.get("uncertain_preserved", False) or row["status"] == "uncertain"
                self.save_protocol()
        self.log("same_id_read_only_result", id=request_id, result=result, no_requeue=True)
        return result

    def material(self, situations, feedback="real", actuator="closed", request_id=None):
        if not self.owned:
            raise RuntimeError("Inicie/continúe un propietario primero.")
        if self.state.get("uncertain_preserved"):
            raise RuntimeError("Efecto incierto preservado: no se añade material ni se repite la acción.")
        if self.state.get("pending_material"):
            raise RuntimeError("Hay una petición pendiente. Use resultado sobre su mismo ID; no repita la tarea.")
        if not isinstance(situations, list) or not 1 <= len(situations) <= 16 or any(not isinstance(row, dict) for row in situations):
            raise ValueError("Entre una y dieciséis situaciones literales; el contrato del gestor decide su admisibilidad.")
        if feedback not in {"real", "omit"} or actuator not in {"closed", "nulled"}:
            raise ValueError("Modalidad de entorno no admitida.")
        request_id = identifier(request_id or "ui_m_" + uuid.uuid4().hex)
        payload = {"operacion": "sesion", "situaciones": situations, "retorno": feedback, "actuador": actuator}
        self.state["pending_material"] = {"id": request_id, "payload_sha256": hashlib.sha256(canonical(payload).encode()).hexdigest(), "recorded_before_submission": now()}
        self.save_protocol()
        self.log("literal_material_submission", id=request_id, payload=payload, host_selected_answer=False)
        wait = self.config["material_wait_seconds"]
        # Una sola inserción; ninguna excepción ni timeout provoca otra put.
        result = self.backend.manager(["mente-unificada-pedir", "--vida", self.life, "--id", request_id,
                  "--situaciones", json.dumps(situations, ensure_ascii=False, separators=(",", ":")), "--retorno", feedback,
                  "--actuador", actuator, "--esperar", str(wait)], timeout=wait+30)
        row = row_of(result)
        if row.get("status") in TERMINAL:
            if row.get("id") != request_id:
                raise ValueError("Respuesta de otro ID; petición preservada sin reintento.")
            if row.get("payload_sha") != self.state["pending_material"]["payload_sha256"]:
                raise ValueError("Carga de respuesta distinta; se conserva pendiente sin reintento.")
            self.state["pending_material"] = None
            self.state["uncertain_preserved"] = row["status"] == "uncertain"
            self.save_protocol()
        elif str(result.get("admission", "")).startswith("rejected"):
            self.state["pending_material"] = None
            self.save_protocol()
        self.log("literal_material_result", id=request_id, result=result)
        return result

    def close(self):
        if self.owned:
            # No se mata otro propietario. Si STOP falla, se conserva la evidencia
            # y la incertidumbre: el gestor no autoriza volver a un checkpoint viejo.
            try:
                return self.control("detener")
            except Exception as error:
                self.log("stop_not_confirmed_preserve_owner_and_protocol", error=repr(error), no_automatic_restart=True)
                raise


def command_parser():
    parser = argparse.ArgumentParser(prog="DEE", exit_on_error=False)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("estado", "iniciar", "continuar", "pausar", "reanudar", "guardar", "detener", "exportar", "salir", "ayuda"):
        sub.add_parser(name)
    result = sub.add_parser("resultado"); result.add_argument("id", nargs="?")
    use = sub.add_parser("usar"); use.add_argument("texto"); use.add_argument("operandos", nargs=2, type=int)
    teach = sub.add_parser("ensenar"); teach.add_argument("texto"); teach.add_argument("senal", type=int, choices=(-1, 1)); teach.add_argument("--revision", action="store_true")
    language = sub.add_parser("lenguaje"); language.add_argument("texto"); language.add_argument("valor", type=int); language.add_argument("contexto", choices=("alfa", "beta", "gamma", "delta", "epsilon", "zeta"))
    accumulate = sub.add_parser("acumular"); accumulate.add_argument("valor", type=int); accumulate.add_argument("--demora", type=int, default=0)
    composition = sub.add_parser("componer"); composition.add_argument("formas", nargs="+"); composition.add_argument("--datos", type=int, nargs="+", required=True)
    goal = sub.add_parser("meta"); goal.add_argument("texto"); goal.add_argument("operandos", type=int, nargs=2); goal.add_argument("--oculto", action="store_true")
    step = sub.add_parser("meta-paso"); step.add_argument("oportunidades", type=int, choices=(1, 2, 3, 4))
    admit_new = sub.add_parser("admitir-apd03", help="Preparación P0 explícita, nunca adquisición ni reseed automático")
    admit_new.add_argument("--consecuencia", choices=("local_useful", "file_only"), default="local_useful")
    teach_new = sub.add_parser("ensenar-nueva"); teach_new.add_argument("texto", choices=("luma", "nara")); teach_new.add_argument("senal", type=int, choices=(-1, 1)); teach_new.add_argument("--revision", action="store_true")
    language_new = sub.add_parser("lenguaje-nuevo"); language_new.add_argument("texto", choices=("luma", "nara")); language_new.add_argument("valor", type=int); language_new.add_argument("contexto", choices=("alfa", "beta", "gamma", "delta", "epsilon", "zeta"))
    new_goal = sub.add_parser("objetivo"); new_goal.add_argument("texto"); new_goal.add_argument("operandos", type=int, nargs=2); new_goal.add_argument("--oculto", action="store_true"); new_goal.add_argument("--contexto-ambiente", type=int, choices=(0, 1), default=0)
    new_step = sub.add_parser("paso"); new_step.add_argument("oportunidades", type=int, choices=(1, 2, 3, 4))
    panel = sub.add_parser("panel", help="Panel MATERIAL; no equivale a la observación pasiva estado")
    panel.add_argument("--nuevas", action="store_true"); panel.add_argument("--memorias", action="store_true")
    event = sub.add_parser("evento"); event.add_argument("archivo", type=Path, help="JSON literal escrito por el usuario, sin evaluación ni selección del supervisor")
    eco_start = sub.add_parser("ecosistema-iniciar", help="Preparación ambiental explícita; no enseña ni reinicia la vida DEE")
    eco_start.add_argument("--semilla", type=int, required=True)
    eco_start.add_argument("--fuentes", type=int, choices=(2, 5, 10, 20), required=True)
    eco_start.add_argument("--goal", type=int, choices=(0, 1), default=0, help="Propiedad ambiental elemental visible, no una acción correcta")
    eco_start.add_argument("--palabra", choices=("clasifica", "equilibra"), default="clasifica")
    eco_start.add_argument("--cargas", type=int, nargs=2, choices=range(21), default=[8, 4])
    eco_start.add_argument("--criterio", type=int, choices=range(1, 41), default=20, help="Umbral exclusivo del evaluador ambiental; no respuesta del participante")
    eco_live = sub.add_parser("ecosistema-vivir", help="Ofrece oportunidades; la selección y la respuesta pertenecen al mecanismo DEE")
    eco_live.add_argument("oportunidades", type=int, choices=(1, 2, 3, 4))
    eco_live.add_argument("--sin-lexico", action="store_false", dest="lexico", default=True)
    eco_live.add_argument("--sensor", choices=("independent", "independent_balanced", "independent_two_pairs", "tag_only", "zero"), default="independent")
    eco_live.add_argument("--desacoplado", action="store_true", help="Control explícito de consecuencias desacopladas")
    eco_change = sub.add_parser("ecosistema-cambio", help="Cambia condiciones externas declaradas, sin editar memorias o lectores")
    eco_change.add_argument("--goal", type=int, choices=(0, 1))
    eco_change.add_argument("--palabra", choices=("clasifica", "equilibra"))
    eco_change.add_argument("--cargas", type=int, nargs=2, choices=range(21))
    eco_change.add_argument("--rotar", type=int, choices=range(-20, 21))
    eco_change.add_argument("--retirar-observados", action="store_true", help="Control explícito de la memoria ambiental de objetos")
    eco_teach = sub.add_parser("ensenar-ecosistema", help="Docencia explícita de señal; no demuestra adquirir toda la función nombrada")
    eco_teach.add_argument("texto", choices=("clasifica", "equilibra"))
    eco_teach.add_argument("senal", type=int, choices=(-1, 1))
    eco_teach.add_argument("--docente", choices=("paired", "omitted", "desync"), default="paired")
    eco_teach.add_argument("--revision", action="store_true")
    eco_view = sub.add_parser("configurar-vista-ecosistema", help="Oportunidad P0 fija de retener tras INSPECT; no elige la fuente por utilidad")
    eco_view.add_argument("politica", choices=("circular_R01", "inspeccion_persistente"))
    eco_actuator = sub.add_parser("configurar-actuador-ecosistema", help="Preparacion P0 fija; no aprende ni elige por respuesta")
    eco_actuator.add_argument("version", choices=("R01", "R02", "R03"))
    eco_r04 = sub.add_parser("admitir-sensor-r04", help="Preparacion P0 explicita de dos puertos; no ensena contenido")
    eco_sensor = sub.add_parser("calibrar-sensor-ecosistema", help="Entradas elementales literales; no retorno de calidad de tarea")
    eco_sensor.add_argument("--familia", choices=("R02", "R03", "R04"), required=True)
    eco_sensor.add_argument("pares", nargs="+", choices=("00", "01", "10", "11"))
    eco_word = sub.add_parser("palabra-ecosistema", help="Consulta MATERIAL de una señal finita; no conversación libre")
    eco_word.add_argument("texto", choices=("alfa", "beta", "gamma", "delta", "epsilon", "zeta", "suma", "diferencia", "agrega", "resta", "total", "quita", "compara", "recuerda", "luma", "nara", "clasifica", "equilibra"))
    for item in (use, teach, language, accumulate, composition, goal, step, admit_new, teach_new, language_new, new_goal, new_step, panel, event,
                 eco_start, eco_live, eco_change, eco_teach, eco_word, eco_r04, eco_sensor, eco_actuator, eco_view):
        item.add_argument("--retorno", choices=("real", "omit"), default="real")
        item.add_argument("--actuador", choices=("closed", "nulled"), default="closed")
    return parser


def literal_rows(options):
    a = options.action
    if a == "usar": return [{"modo": "apd02", "texto": options.texto, "operandos": options.operandos}]
    if a == "ensenar": return [{"modo": "apd02-docencia", "texto": options.texto, "senal": options.senal, "revision": options.revision}]
    if a == "lenguaje": return [{"modo": "apd02-lenguaje", "texto": options.texto, "valor": options.valor, "contexto": options.contexto}]
    if a == "acumular": return [{"modo": "apd02-acumular", "valor": options.valor, "demora_periodos": options.demora}]
    if a == "componer": return [{"modo": "apd02-componer", "formas": options.formas, "datos": options.datos}]
    if a == "meta": return [{"modo": "apd02-meta-iniciar", "texto": options.texto, "operandos": options.operandos, "segundo_visible": not options.oculto}]
    if a == "meta-paso": return [{"modo": "apd02-meta-paso", "oportunidades": options.oportunidades}]
    if a == "admitir-apd03": return [{"modo": "apd03-admitir", "consecuencia": options.consecuencia}]
    if a == "ensenar-nueva": return [{"modo": "apd03-docencia", "texto": options.texto, "senal": options.senal, "revision": options.revision}]
    if a == "lenguaje-nuevo": return [{"modo": "apd03-lenguaje", "texto": options.texto, "valor": options.valor, "contexto": options.contexto}]
    if a == "objetivo": return [{"modo": "apd03-tarea-iniciar", "texto": options.texto, "operandos": options.operandos, "segundo_visible": not options.oculto, "contexto_ambiente": options.contexto_ambiente}]
    if a == "paso": return [{"modo": "apd03-paso", "oportunidades": options.oportunidades}]
    if a == "panel": return [{"modo": "apd03-panel", "nuevas": options.nuevas, "memorias": options.memorias}]
    if a == "ecosistema-iniciar": return [{"modo": "apd04-iniciar", "semilla": options.semilla, "fuentes": options.fuentes,
        "etiqueta_objetivo": options.goal, "palabra": options.palabra, "cargas": options.cargas, "criterio": options.criterio}]
    if a == "configurar-vista-ecosistema": return [{"modo": "apd04-vista", "politica": options.politica}]
    if a == "configurar-actuador-ecosistema": return [{"modo": "apd04-actuador", "version": options.version}]
    if a == "admitir-sensor-r04": return [{"modo": "apd04-r04-admitir"}]
    if a == "calibrar-sensor-ecosistema": return [{"modo": "apd04-sensor-calibrar", "familia": options.familia,
        "pares": [[int(pair[0]), int(pair[1])] for pair in options.pares]}]
    if a == "ecosistema-vivir": return [{"modo": "apd04-vivir", "oportunidades": options.oportunidades,
        "lexico": options.lexico, "sensor": options.sensor, "desacoplado": options.desacoplado}]
    if a == "ecosistema-cambio":
        row = {"modo": "apd04-cambio"}
        for name, value in (("etiqueta_objetivo", options.goal), ("palabra", options.palabra),
                            ("cargas", options.cargas), ("rotar", options.rotar)):
            if value is not None: row[name] = value
        if options.retirar_observados: row["retirar_observados"] = True
        return [row]
    if a == "ensenar-ecosistema": return [{"modo": "apd04-docencia", "texto": options.texto, "senal": options.senal,
        "docente": options.docente, "revision": options.revision}]
    if a == "palabra-ecosistema": return [{"modo": "apd04-palabra", "texto": options.texto}]
    if a == "evento":
        value = read(options.archivo)
        return value if isinstance(value, list) else [value]
    raise ValueError("El comando no contiene una experiencia material.")


def execute(session, tokens):
    options = command_parser().parse_args(tokens)
    a = options.action
    if a == "ayuda": return {"INSTRUMENTO": command_parser().format_help()}
    if a == "estado": return session.status()
    if a in {"iniciar", "continuar"}: return session.start()
    if a == "resultado": return session.result(options.id)
    if a == "salir": session.close(); return {"INSTRUMENTO": "sesion_finalizada"}
    if a in {"pausar", "reanudar", "guardar", "detener", "exportar"}: return session.control(a)
    return session.material(literal_rows(options), options.retorno, options.actuador)


def main(argv=None):
    parser = argparse.ArgumentParser(description="DEE: una terminal para una copia aprendida; no intérprete de lenguaje libre.")
    parser.add_argument("--raiz", type=Path, default=default_root(__file__), help=argparse.SUPPRESS)
    who = parser.add_mutually_exclusive_group(required=True)
    who.add_argument("--nueva", metavar="IDENTIDAD_NUEVA", help="Importa una vez el par cerrado seleccionado; nunca T0")
    who.add_argument("--vida", metavar="IDENTIDAD", help="Continúa la misma copia personal, nunca vuelve a importarla")
    parser.add_argument("--sin-iniciar", action="store_true", help="Abre solamente la ficha; ningún propietario/tick")
    parser.add_argument("--guion", type=Path, help="JSON con listas argv literales para una sesión reproducible; el guion es preparación del operador")
    options = parser.parse_args(argv)
    root = options.raiz.resolve()
    distribution = (root / "actualizaciones/arrancar.py").is_file()
    config_path = selected_config_path(root)
    config = read(config_path)
    for field in ("idle_interval_seconds", "owner_max_seconds", "memory_limit_bytes", "start_wait_seconds", "control_wait_seconds", "material_wait_seconds", "stop_wait_seconds"):
        if type(config.get(field)) not in (int, float) or not math.isfinite(config[field]) or config[field] <= 0:
            raise ValueError("Límite de supervisión positivo finito requerido: " + field)
    life = identifier(options.nueva or options.vida)
    backend = DistributionBackend(root, config) if distribution else OriginalBackend(root, config)
    lock = backend.protocol_home / life / "SUPERVISOR.lock"
    with SessionLock(lock):
        session = Supervisor(root, life, backend, config)
        try:
            card = session.open(new=options.nueva is not None)
            print(json.dumps({"INSTRUMENTO": {"version": VERSION, "life_id": life, "world_id": card["world_id"], "tick_al_abrir": card["physical"]["tick"], "no_free_language": True, "no_host_cognitive_policy": True}}, ensure_ascii=False, indent=2))
            if not options.sin_iniciar:
                print(json.dumps(session.start(), ensure_ascii=False, indent=2))
                print("Mundo en PAUSA. Use reanudar para evolución; estado es observación pasiva. ayuda muestra comandos.")
            scripted = read(options.guion) if options.guion else None
            if scripted is not None and (not isinstance(scripted, list) or any(not isinstance(row, list) or not row or any(not isinstance(v, str) for v in row) for row in scripted)):
                raise ValueError("El guion contiene listas argv literales, no objetivos ni respuestas calculadas.")
            if scripted is not None:
                for tokens in scripted:
                    value = execute(session, tokens)
                    print(json.dumps(value, ensure_ascii=False, indent=2))
                    if tokens[0] == "salir": break
                return 0
            while True:
                try:
                    line = input("DEE> ").strip()
                    if not line: continue
                    tokens = shlex.split(line)
                    value = execute(session, tokens)
                    print(json.dumps(value, ensure_ascii=False, indent=2))
                    if tokens[0] == "salir": break
                except (ValueError, RuntimeError, OSError, argparse.ArgumentError) as error:
                    print("INSTRUMENTO: " + str(error), file=sys.stderr)
                except SystemExit as error:
                    # Un error de sintaxis del usuario no abandona al propietario.
                    if error.code: print("INSTRUMENTO: comando no enviado; consulte ayuda.", file=sys.stderr)
            return 0
        except (EOFError, KeyboardInterrupt):
            print("\nINSTRUMENTO: cierre solicitado; se envía STOP al propietario propio.")
            return 130
        finally:
            session.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(type(error).__name__ + ": " + str(error), file=sys.stderr)
        raise SystemExit(2)
