"""Spanish finite SEM01 application. No LLM, target decoder or hidden reset.

All native calls run in owned bounded child processes. Re-instantiating the
worker RESTORES the same complete MAIN snapshot; it never rebuilds its history.
The application remains usable after the campaign budget has expired.
"""
from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parent
HELP = """SEM01 — dos relaciones adquiridas, dos usos finitos, un mismo MAIN.
crear [reservada]             NUEVO individuo vacío explícito
enseña <alias|S1|S2> <U|V>   prepara una experiencia en GENERADOR externo
termina enseñanza            ejecuta ambas experiencias y retira su mapa del UI
señal <alias|S1|S2>          evolución nativa hasta la próxima emisión preparada
revelar <U|V>                acontecimiento físico DESPUÉS de la emisión
observa                      lectura pasiva actual, no respuesta histórica guardada
nombre <S1|S2> <token>        alias externo, nunca tabla funcional U/V
guardar <archivo.deetsnap>    copia íntegra del MAIN y su continuidad operativa
cargar <archivo.deetsnap>     valida y restaura SIN reconstruir ni reenseñar
ayuda | salir
Preparación principal: orden S1,S2, carga5. Reservada: S2,S1, carga7,
traslación(9,-4,7). Las rutas y el período67 están preparados, no aprendidos.
U/V nombran efectos físicos del hábitat; la ausencia la mide un sensor EXTERNO.
No hay conversación ilimitada ni inversión automática de una asociación.
"""


class BasicLimits(ctypes.Structure):
    _fields_ = [("process_time", ctypes.c_int64), ("job_time", ctypes.c_int64), ("flags", wintypes.DWORD),
                ("min_ws", ctypes.c_size_t), ("max_ws", ctypes.c_size_t), ("active", wintypes.DWORD),
                ("affinity", ctypes.c_size_t), ("priority", wintypes.DWORD), ("scheduling", wintypes.DWORD)]


class IOCounters(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint64) for name in ("read_ops", "write_ops", "other_ops", "read_bytes", "write_bytes", "other_bytes")]


class ExtendedLimits(ctypes.Structure):
    _fields_ = [("basic", BasicLimits), ("io", IOCounters), ("process_memory", ctypes.c_size_t),
                ("job_memory", ctypes.c_size_t), ("peak_process", ctypes.c_size_t), ("peak_job", ctypes.c_size_t)]


def owned_job(child):
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel.CreateJobObjectW.restype = wintypes.HANDLE
    kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    kernel.SetInformationJobObject.restype = wintypes.BOOL
    kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    handle = kernel.CreateJobObjectW(None, None)
    limits = ExtendedLimits()
    limits.basic.flags = 0x2000  # KILL_ON_JOB_CLOSE; never enumerate foreign PIDs.
    if not handle or not kernel.SetInformationJobObject(handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)) or not kernel.AssignProcessToJobObject(handle, wintypes.HANDLE(int(child._handle))):
        error = ctypes.get_last_error()
        if handle:
            kernel.CloseHandle(handle)
        raise OSError(error, "Could not isolate the live owned native child")
    return kernel, handle


def sha(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


class Demonstration:
    def __init__(self, python, directory, timeout=120):
        self.python = str(Path(python).resolve())
        self.directory = Path(directory).resolve()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.timeout = min(max(int(timeout), 1), 120)
        self.current = None
        self.aliases = {"zuvi": "S1", "pako": "S2"}
        self.generator = {}
        self.counter = 0
        self.rejected_count = 0
        self.transcript = self.directory / "TRANSCRIPCION.jsonl"

    def log(self, value):
        with self.transcript.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(value, ensure_ascii=False) + "\n")
            stream.flush()

    def signal(self, token):
        if token.upper() in ("S1", "S2"):
            return token.upper()
        if token.lower() in self.aliases:
            return self.aliases[token.lower()]
        raise ValueError("Señal fuera del vocabulario de interfaz; usa ayuda")

    def worker(self, operation, extra=(), mutates=True, snapshot=None):
        self.counter += 1
        call = self.directory / (f"llamada_{self.counter:03d}_" + operation + "_" + uuid.uuid4().hex[:8])
        call.mkdir()
        result_path = call / "RESULT.json"
        argv = [self.python, "-I", "-B", str(ROOT / "src/app_worker.py"), operation, "--result", str(result_path)]
        active = Path(snapshot).resolve() if snapshot is not None else self.current
        if operation != "create":
            if active is None:
                raise ValueError("No existe MAIN; usa crear o cargar")
            argv += ["--snapshot", str(active)]
        if mutates:
            argv += ["--output-snapshot", str(call / "MAIN.deetsnap")]
        argv += list(extra)
        source_hashes = {"demostracion.py": sha(ROOT / "demostracion.py"),
                         "src/app_worker.py": sha(ROOT / "src/app_worker.py")}
        source_archive = self.directory / "SOURCE_VERSIONS" / source_hashes["src/app_worker.py"]
        source_archive.mkdir(parents=True, exist_ok=True)
        if not (source_archive / "app_worker.py").exists():
            shutil.copyfile(ROOT / "src/app_worker.py", source_archive / "app_worker.py")
        controller_archive = self.directory / "SOURCE_VERSIONS" / source_hashes["demostracion.py"]
        controller_archive.mkdir(parents=True, exist_ok=True)
        if not (controller_archive / "demostracion.py").exists():
            shutil.copyfile(ROOT / "demostracion.py", controller_archive / "demostracion.py")
        started = time.monotonic()
        with (call / "stdout.log").open("w", encoding="utf-8") as out, (call / "stderr.log").open("w", encoding="utf-8") as err:
            # Windows CreateProcess rejects excessively long working-directory
            # strings even when the snapshot/file APIs support long paths.
            # All artifacts are absolute; no state is looked up from cwd.
            child = subprocess.Popen(argv, cwd=ROOT, stdout=out, stderr=err, creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                job = owned_job(child)
            except Exception:
                child.kill()
                child.wait(timeout=10)
                raise
            timed_out = False
            try:
                child.wait(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                job[0].TerminateJobObject(job[1], 124)
                child.wait(timeout=10)
            finally:
                job[0].CloseHandle(job[1])
        record = {"operation": operation, "argv": argv, "exit_code": child.returncode,
                  "elapsed_seconds": time.monotonic() - started, "timeout_seconds": self.timeout,
                  "timed_out": timed_out, "owned_process": child.pid, "windows_job_closed": True,
                  "source_sha256": source_hashes,
                  "cwd": str(ROOT),
                  "application_budget": "per-call timeout; not the expired historical campaign BUDGET"}
        (call / "PROCESS.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        result = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else {"completed": False, "error": "No output before process timeout/error"}
        if child.returncode != 0 or not result.get("completed"):
            raise RuntimeError(result.get("error", "Native worker failed; previous MAIN preserved"))
        # Publish the new operative cursor only after a successful worker.
        if mutates:
            self.current = Path(result["snapshot"]["path"])
        elif snapshot is not None:
            self.current = active
        self.aliases = result["after"]["aliases"]
        return result

    def render(self, value):
        if "query" in value:
            emission = value["query"]["emission"]
            p = emission["physical"]
            if not value["query_admitted"]:
                return f"INSTRUMENTO: señal NO aplicada ({value['query']['receipt']['status']}); RAW actual t={p['tick']}, dirección={p['direction']}, carga={p['s_reg']}. No se presenta como predicción nueva ni como olvido."
            decoded = emission["anticipated_class"] or "INDETERMINADO"
            return f"ENTE: emisión actual t={p['tick']}, dirección={p['direction']}, carga={p['s_reg']}; lectura fija {decoded}. El acontecimiento futuro aún no se ha presentado."
        if "evaluation" in value:
            e = value["evaluation"]
            return f"INSTRUMENTO: efecto físico t={value['after']['tick']}; función={int(e['function_delivery'])}, recurso={int(e['resource_delivery'])}. La utilidad {e['external_utility_for_this_task']} es evaluación externa, no una enseñanza al cuerpo."
        return f"INTERFAZ: t={value['after']['tick']}, fase={value['after']['phase']}, siguiente={value['after']['next_signal']}. {value.get('attribution', 'Lectura pasiva de estado actual; no replay de respuestas.')}"

    def command(self, text):
        # posix=False preserves Windows backslashes; quotes are removed only
        # around an entire token, without interpreting a command or expression.
        parts = [p[1:-1] if len(p) > 1 and p[0] == p[-1] == '"' else p for p in shlex.split(text, posix=False)]
        if not parts or parts[0].startswith("#"):
            return None
        verb = parts[0].lower()
        result = None
        if verb == "ayuda" and len(parts) == 1:
            return HELP
        if verb == "salir" and len(parts) == 1:
            return "SALIR"
        if verb == "crear" and len(parts) in (1, 2):
            if len(parts) == 2 and parts[1].lower() != "reservada":
                raise ValueError("Crear acepta sólo principal (sin argumento) o reservada")
            extra = [] if len(parts) == 1 else ["--translation", "9", "-4", "7", "--order", "S2", "S1", "--payload", "7"]
            result = self.worker("create", extra)
            self.generator.clear()
        elif verb in ("enseña", "ensena") and len(parts) == 3:
            if self.current is None:
                raise ValueError("Primero crea un individuo")
            target = parts[2].upper()
            if target not in ("U", "V"):
                raise ValueError("El generador sólo produce los acontecimientos físicos U/V")
            self.generator[self.signal(parts[1])] = target
            return "GENERADOR EXTERNO: experiencia seleccionada, aún no entregada. Esta asignación no es una memoria del ente."
        elif [p.lower() for p in parts] in (["termina", "enseñanza"], ["termina", "ensenanza"]):
            if set(self.generator) != {"S1", "S2"}:
                raise ValueError("El generador necesita ambas experiencias; usa enseña")
            generator_json = json.dumps(self.generator, separators=(",", ":"))
            result = self.worker("train", ["--pairing", generator_json, "--evidence", str(self.directory / "GENERADOR_EXTERNO")])
            self.generator.clear()  # Not reachable by any subsequent query request.
            generator_json = None
        elif verb in ("señal", "senal") and len(parts) == 2:
            if self.generator:
                raise ValueError("Termina o descarta explícitamente la enseñanza antes de consultar")
            result = self.worker("query", ["--signal", self.signal(parts[1])])
        elif verb == "revelar" and len(parts) == 2:
            if parts[1].upper() not in ("U", "V"):
                raise ValueError("Revelar requiere U o V, no una respuesta esperada")
            result = self.worker("reveal", ["--event", parts[1].upper()])
        elif verb in ("observa", "observar") and len(parts) == 1:
            result = self.worker("observe", mutates=False)
        elif verb == "nombre" and len(parts) == 3:
            if parts[1].upper() not in ("S1", "S2"):
                raise ValueError("Nombre modifica sólo la etiqueta externa de S1/S2")
            result = self.worker("alias", ["--signal", parts[1].upper(), "--alias", parts[2]])
        elif verb == "guardar" and len(parts) == 2:
            if self.current is None:
                raise ValueError("No existe MAIN")
            destination = Path(parts[1])
            if not destination.is_absolute():
                destination = self.directory / destination
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                raise FileExistsError("No se sobrescribe una entrega previa")
            temporary = destination.with_name(destination.name + "." + uuid.uuid4().hex + ".tmp")
            shutil.copyfile(self.current, temporary)
            if sha(temporary) != sha(self.current):
                raise RuntimeError("Snapshot copy mismatch")
            os.replace(temporary, destination)
            return f"PERSISTENCIA TÉCNICA: snapshot íntegro {destination.resolve()} SHA-256 {sha(destination)}. El mapa incompleto del generador no se incluye."
        elif verb == "cargar" and len(parts) == 2:
            if self.generator:
                raise ValueError("Carga rechazada mientras existe una enseñanza externa incompleta")
            path = Path(parts[1])
            if not path.is_absolute():
                path = self.directory / path
            result = self.worker("validate", mutates=False, snapshot=path)
        else:
            raise ValueError("Orden fuera de la gramática finita; ayuda enumera operaciones reales")
        return self.render(result)

    def run_line(self, text):
        before = str(self.current) if self.current else None
        try:
            answer = self.command(text)
            record = {"utc": datetime.now(timezone.utc).isoformat(), "command": text, "answer": answer,
                      "accepted": True, "main_before": before, "main_after": str(self.current) if self.current else None,
                      "generator_assignment_still_present_in_ui": bool(self.generator)}
        except Exception as exc:
            self.rejected_count += 1
            answer = f"INTERFAZ RECHAZA: {exc}"
            record = {"utc": datetime.now(timezone.utc).isoformat(), "command": text, "answer": answer,
                      "accepted": False, "main_before": before, "main_after": str(self.current) if self.current else None,
                      "error_type": type(exc).__name__}
        self.log(record)
        return answer


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", type=Path, default=Path(sys.executable), help="CPython3.13 con el WHL4 oficial instalado")
    parser.add_argument("--directorio", type=Path, default=ROOT / "sesiones" / datetime.now().strftime("%Y%m%d_%H%M%S"))
    parser.add_argument("--eventos", type=Path)
    parser.add_argument("--cargar", type=Path)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    app = Demonstration(args.python, args.directorio, args.timeout)
    if args.cargar:
        print(app.run_line('cargar "' + str(args.cargar.resolve()) + '"'))
    if args.eventos:
        for line in args.eventos.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.lstrip().startswith("#"):
                print("> " + line)
                response = app.run_line(line)
                if response:
                    print(response)
                if response == "SALIR":
                    break
        if app.rejected_count:
            raise SystemExit(2)
    else:
        print(HELP)
        while True:
            try:
                line = input("sem01> ")
            except EOFError:
                break
            answer = app.run_line(line)
            if answer:
                print(answer)
            if answer == "SALIR":
                break


if __name__ == "__main__":
    main()
