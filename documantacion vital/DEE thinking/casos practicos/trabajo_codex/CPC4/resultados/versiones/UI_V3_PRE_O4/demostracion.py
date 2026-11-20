"""Spanish finite CPC4 interface, with one persistent supervised Native MAIN."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import queue
import subprocess
import sys
import threading

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from src.language import catalogue_view, parse, render

HELP = """INTERFAZ: protocolo finito CPC4 (no conversación ilimitada).
crear [semilla N]                  Nueva preparación vacía; nunca reinicia MAIN.
vivir - coherente -                Experiencia A−/B coherente y entorno−.
vivir + coherente +                Historia/entorno opuestos, mismas interfaces.
vivir +/- invertida +/-            Experiencia B invertida declarada.
enseñar HAY                       Asocia la primera forma al recurso ACTUAL.
enseñar NO                        Otra forma al segundo recurso ACTUAL.
consultar HAY                     Señal física sola, primer turno finito.
consultar NO                      Segunda consulta sobre el mismo MAIN.
nombre zuvi W1                    Alias externo; no escribe significado.
observar                          Lectura pasiva de RAW/clock/dirección.
diagnóstico                       SóloT172 tras HAY:3forks explícitos, no MAIN.
guardar "ruta.deetsnap"           Persistencia operativa integral.
cargar "ruta.deetsnap"            Restaura, no crea/reinstala el cuerpo.
catálogo [forma|NSM65.ID]           Fuente documental; no experiencia del ente.
por qué                           Explicación externa del mecanismo.
ayuda / salir
Las dos formas pueden enseñarse NO,HAY; se consultan en el orden enseñado.
Tras las dos consultas no hay un reinicio/reciclaje oculto del suministro.
«HAY» puede emitir ausencia tras una historia opuesta: no se corrige el texto.
"""


class NativeProcess:
    """Persistent process and exact owned Windows Job, independent of campaign
    deadline for later user sessions. Every call has a finite 120s timeout.
    """
    def __init__(self, python, output, timeout=120):
        from supervise import owned_job
        self.output = Path(output)
        self.output.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.stderr = (self.output / "WORKER_STDERR.log").open("x", encoding="utf-8")
        self.process = subprocess.Popen([str(python), "-I", "-B", str(Path(__file__).resolve()), "--worker", "--salida", str(self.output.resolve())],
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.stderr,
                                        text=True, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW, cwd=str(ROOT))
        self.job, self.job_info = owned_job(self.process)
        if not self.job:
            self.process.kill(); self.process.wait(timeout=10); self.stderr.close()
            raise RuntimeError("No se pudo delimitar el proceso Native mediante Windows Job propio")
        self.messages = queue.Queue()
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()
        self.initial = self._receive()
        if not self.initial.get("ready"):
            self.close()
            raise RuntimeError("El worker no completó su identidad Native")

    def _read(self):
        for line in self.process.stdout:
            try:
                self.messages.put(json.loads(line))
            except (ValueError, TypeError):
                self.messages.put({"ok": False, "error": "INVALID_WORKER_MESSAGE", "message": line})
        self.messages.put({"ok": False, "error": "WORKER_EXIT", "message": str(self.process.poll())})

    def _receive(self):
        try:
            result = self.messages.get(timeout=self.timeout)
        except queue.Empty:
            self.job[0].TerminateJobObject(self.job[1], 124)
            self.process.wait(timeout=10)
            raise TimeoutError("Llamada Native excedió120s; sólo se terminó el proceso propio y sus descendientes") from None
        return result

    def call(self, command):
        if self.process.poll() is not None:
            raise RuntimeError("MAIN ya no está en ejecución; carga una captura en una nueva sesión")
        self.process.stdin.write(json.dumps(asdict(command), ensure_ascii=False) + "\n")
        self.process.stdin.flush()
        return self._receive()

    def close(self):
        if getattr(self, "process", None) is not None and self.process.poll() is None:
            try:
                self.process.stdin.write('{"operation":"exit"}\n'); self.process.stdin.flush()
                self.process.wait(timeout=5)
            except (BrokenPipeError, OSError, subprocess.TimeoutExpired):
                if self.job: self.job[0].TerminateJobObject(self.job[1], 124)
                self.process.wait(timeout=10)
        if getattr(self, "job", None):
            self.job[0].CloseHandle(self.job[1]); self.job = None
        if getattr(self, "stderr", None): self.stderr.close()


def main():
    # Pipe encoding on Windows is not inherited from Popen(encoding=...).
    # The worker and controller explicitly agree on UTF-8 in BOTH directions.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eventos", type=Path, help="Archivo UTF-8 de órdenes reproducibles")
    parser.add_argument("--salida", type=Path, required=True, help="Carpeta NUEVA para el registro de sesión")
    parser.add_argument("--python", type=Path, default=Path(sys.executable), help="CPython3.13 con WHL4 oficial instalado")
    parser.add_argument("--cargar", type=Path, help="Carga explícita inicial antes del archivo o del modo interactivo")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        from src.app_worker import main as worker
        worker(args.salida)
        return
    if args.salida.exists():
        raise FileExistsError("La salida ya existe; no se sobrescriben sesiones históricas")
    args.salida.mkdir(parents=True)
    source = args.eventos.read_text(encoding="utf-8").splitlines() if args.eventos else None
    commands = iter(source) if source is not None else None
    process = None
    failed = 0
    transcript = args.salida / "TRANSCRIPCION.jsonl"
    printable = args.salida / "TRANSCRIPCION.txt"
    try:
        process = NativeProcess(args.python, args.salida / "MAIN")
        initial = {"attribution": "INTERFAZ", "status": "WORKER_MAIN_PERSISTENTE", "identity": process.initial["identity"], "supervision": process.job_info}
        print(render(initial), flush=True)
        with transcript.open("x", encoding="utf-8") as data, printable.open("x", encoding="utf-8") as text:
            data.write(json.dumps({"initial": initial}, ensure_ascii=False) + "\n")
            text.write(render(initial) + "\n")
            pending_load = 'cargar "' + str(args.cargar) + '"' if args.cargar else None
            while True:
                try:
                    if pending_load:
                        line, pending_load = pending_load, None
                    else:
                        line = next(commands) if commands is not None else input("CPC4> ")
                except (StopIteration, EOFError):
                    break
                command = None
                try:
                    command = parse(line)
                    if command.operation == "comment": continue
                    if command.operation == "help":
                        response = {"ok": True, "result": {"attribution": "INTERFAZ", "grammar": HELP}}
                        presentation = HELP
                    elif command.operation == "catalogue":
                        response = {"ok": True, "result": catalogue_view(ROOT / "NSM65_CATALOGO.json", command.arguments[0] if command.arguments else None)}
                        presentation = render(response["result"])
                    else:
                        response = process.call(command)
                        presentation = render(response["result"]) if response.get("ok") else "INTERFAZ: RECHAZADO: " + response.get("message", response.get("error", ""))
                    if not response.get("ok"): failed += 1
                except Exception as error:
                    response = {"ok": False, "error": type(error).__name__, "message": str(error)}
                    presentation = "INTERFAZ: RECHAZADO: " + str(error)
                    failed += 1
                row = {"command": line, "response": response, "presentation": presentation}
                data.write(json.dumps(row, ensure_ascii=False) + "\n"); data.flush()
                text.write("> " + line + "\n" + presentation + "\n"); text.flush()
                print(presentation, flush=True)
                if command is not None and command.operation == "exit": break
                if process.process.poll() is not None: break
    finally:
        if process: process.close()
    print(json.dumps({"session_closed": True, "rejected_commands": failed, "transcript": str(transcript.resolve())}), flush=True)
    raise SystemExit(0 if failed == 0 else 2)


if __name__ == "__main__":
    main()
