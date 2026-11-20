"""Spanish 4.0 interface: one persistent native MAIN in a supervised child."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading


def engine(arguments):
    import dee_thinking as dee
    if dee.__version__ != "4.0.0" or dee.kernel_identity()["kernel_version"] != 27:
        raise RuntimeError("Esta aplicación requiere el WHL 4.0.0 instalado y kernel v27")
    from dee_thinking.dialogue import ConversationSession
    preparation = json.loads(Path(arguments.preparacion).read_text(encoding="utf-8")) if arguments.preparacion else {}
    session = ConversationSession(arguments.perfil, directory=arguments.sesion, preparation=preparation)
    for line in sys.stdin:
        try:
            request = json.loads(line)
            response = session.execute(request["input"])
        except Exception as error:
            response = {"attribution": "INSTRUMENTO", "text": str(error), "error": type(error).__name__}
        print(json.dumps({"response": response, "engine_pid": os.getpid()}, ensure_ascii=True), flush=True)
        if response.get("exit"):
            break


def stop_owned_child(process):
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill.exe", "/PID", str(process.pid), "/T", "/F"],
                       capture_output=True, timeout=10)
    else:
        process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--perfil", choices=("continuidad", "comparacion", "politica", "informacion", "relaciones", "composicion"), default="continuidad")
    parser.add_argument("--eventos", type=Path, help="Archivo UTF-8 con una orden de la gramática por línea")
    parser.add_argument("--sesion", type=Path, default=Path("sesion"))
    parser.add_argument("--transcripcion", type=Path, default=Path("DIALOGOS.jsonl"))
    parser.add_argument("--cargar", type=Path)
    parser.add_argument("--preparacion", type=Path, help="Parámetros explícitos de preparación, no respuestas")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--json", action="store_true", help="Mostrar también las mediciones físicas completas")
    parser.add_argument("--engine", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.engine:
        engine(args)
        return
    if not 0 < args.timeout <= 180:
        parser.error("--timeout debe estar entre 0 y 180 segundos")
    args.sesion.mkdir(parents=True, exist_ok=True)
    args.transcripcion.parent.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "-I", "-B", str(Path(__file__).resolve()), "--engine",
               "--perfil", args.perfil, "--sesion", str(args.sesion.resolve())]
    if args.preparacion:
        command += ["--preparacion", str(args.preparacion.resolve())]
    stderr = args.transcripcion.with_suffix(".engine.stderr.log")
    responses = queue.Queue()
    with stderr.open("w", encoding="utf-8") as errors:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=errors, text=True, encoding="utf-8", bufsize=1,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        def read_responses():
            try:
                for line in process.stdout:
                    responses.put(line)
            finally:
                responses.put(None)
        reader = threading.Thread(target=read_responses, name="native-response-reader", daemon=True)
        reader.start()

        def request(text):
            process.stdin.write(json.dumps({"input": text}, ensure_ascii=True) + "\n")
            process.stdin.flush()
            try:
                line = responses.get(timeout=args.timeout)
            except queue.Empty as error:
                stop_owned_child(process)
                raise TimeoutError("Se agotó la llamada nativa; se cerró sólo el proceso propio. La organización no se recreó.") from error
            if line is None:
                raise RuntimeError("El proceso nativo terminó; consulta " + str(stderr))
            result = json.loads(line)
            row = {"wall_utc": datetime.now(timezone.utc).isoformat(), "input": text,
                   "profile": args.perfil, **result}
            with args.transcripcion.open("a", encoding="utf-8") as transcript:
                transcript.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
                transcript.flush()
                os.fsync(transcript.fileno())
            if args.json:
                print(json.dumps(row, ensure_ascii=False), flush=True)
            else:
                response = row["response"]
                print(response.get("attribution", "INSTRUMENTO") + ": " + response.get("text", ""), flush=True)
            return row["response"]
        try:
            if args.cargar:
                request("Carga " + str(args.cargar.resolve()))
            if args.eventos:
                for line in args.eventos.read_text(encoding="utf-8-sig").splitlines():
                    if line.strip() and not line.lstrip().startswith("#"):
                        if request(line.strip()).get("exit"):
                            break
            else:
                print("Interfaz española DEE 4.0; escribe ayuda. Perfil explícito: " + args.perfil)
                while True:
                    try:
                        text = input("> ")
                    except EOFError:
                        text = "Salir"
                    if request(text).get("exit"):
                        break
        finally:
            if process.stdin:
                process.stdin.close()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                stop_owned_child(process)
            reader.join(timeout=2)
        if process.returncode:
            raise RuntimeError("El propietario nativo terminó con código " + str(process.returncode))


if __name__ == "__main__":
    main()
