"""Verify archived EO01 recalculation from a copied export, never native ticks."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import runpy
import shutil
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primarios", type=Path)
    parser.add_argument("--salida", type=Path)
    parser.add_argument("--prohibir-raiz", required=True, type=Path)
    parser.add_argument("--worker", action="store_true")
    args = parser.parse_args()
    forbidden = args.prohibir_raiz.resolve()
    if args.worker:
        here = Path(__file__).resolve().parent
        def audit(event, values):
            if event == "open" and values and isinstance(values[0], (str, bytes, os.PathLike)):
                path = Path(os.fsdecode(values[0])).resolve()
                if path == forbidden or path.is_relative_to(forbidden):
                    raise PermissionError("Export recalculation cannot read original DEE system: " + str(path))
            if event in ("socket.connect", "socket.connect_ex", "subprocess.Popen", "os.system"):
                raise PermissionError("No network or decision subprocess in archived recalculation")
        sys.addaudithook(audit)
        sys.argv = [str(here / "recalcular.py"), "--primarios", str(here / "EVIDENCIA_CAUSAL"), "--salida", str(here / "RESULTADO")]
        runpy.run_path(str(here / "recalcular.py"), run_name="__main__")
        return 0
    if args.primarios is None or args.salida is None:
        raise ValueError("Input primaries and output verification report required")
    # This is a new private export copy outside the source root. No historical
    # original, life or snapshot is changed; it is deliberately not deleted.
    export = Path(tempfile.mkdtemp(prefix="EO01-recalculo-exportado-")).resolve()
    if export == forbidden or export.is_relative_to(forbidden):
        raise ValueError("Independent export must not live under the original system")
    shutil.copytree(args.primarios.resolve(), export / "EVIDENCIA_CAUSAL")
    for name in ("recalcular.py", "verificar_exportacion.py"):
        shutil.copyfile(Path(__file__).with_name(name), export / name)
    command = [sys.executable, "-I", "-B", str(export / "verificar_exportacion.py"), "--worker", "--prohibir-raiz", str(forbidden)]
    process = subprocess.run(command, cwd=export, capture_output=True, text=True, encoding="utf8", timeout=180)
    computed = export / "RESULTADO/RECALCULO_RESULTADOS.json"
    source_result = Path(__file__).parent / "resultados/RECALCULO_RESULTADOS.json"
    data = {
        "kind": "Archived exported recalculation, not native reproduction or life continuation",
        "native_ticks_executed": 0, "export_path": str(export), "command": command,
        "original_system_reads_forbidden_in_worker": str(forbidden),
        "returncode": process.returncode, "stdout": process.stdout, "stderr": process.stderr,
        "result_sha256": hashlib.sha256(computed.read_bytes()).hexdigest() if computed.is_file() else None,
        "original_calculation_sha256": hashlib.sha256(source_result.read_bytes()).hexdigest(),
        "byte_identical_result": computed.is_file() and computed.read_bytes() == source_result.read_bytes(),
        "scope": "Fresh process, another path on same computer. Full primary/source bytes copied; no dependency on original imports/snapshots; no claim of another physical computer.",
        "export_copy_retained_locally": True,
    }
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print(json.dumps(data, ensure_ascii=False))
    return int(process.returncode != 0 or not data["byte_identical_result"])


if __name__ == "__main__":
    raise SystemExit(main())
