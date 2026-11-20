"""Entrada local del sistema original; transporte literal, sin otro gestor.

No instala por red ni crea vidas por defecto. El almacen de las vidas originales
permanece en sistema/estado; no se utiliza el adaptador de distribucion.
"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import struct
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
PYTHON = ROOT / "motor/python313/python.exe"
WHEEL = ROOT / "sistema/runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl"
WHEEL_SHA = "09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c"


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def prepare():
    """Reutiliza el preparador portable: extrae el WHL oficial una sola vez."""
    if sys.version_info[:2] != (3, 13) or struct.calcsize("P") != 8:
        raise RuntimeError("Requiere el CPython 3.13 x64 incluido en motor/python313.")
    if Path(sys.executable).resolve() != PYTHON.resolve(strict=True):
        raise RuntimeError("Inicie con INICIAR.bat; no se selecciona otro interprete silenciosamente.")
    if digest(WHEEL) != WHEEL_SHA:
        raise RuntimeError("El WHL no corresponde al producto oficial congelado.")
    target = ROOT / "motor/python313/site-packages"
    marker = target / "INSTALACION_DEE.json"
    if marker.is_file():
        installed = json.loads(marker.read_text(encoding="utf8"))
        if installed.get("wheel_sha256") != WHEEL_SHA or not (target / "dee_thinking/__init__.py").is_file():
            raise RuntimeError("Instalacion local incompleta o de otra identidad; no se reemplaza automaticamente.")
    else:
        # Identico producto; no pip, red, compilacion ni edicion del kernel/WHL.
        with zipfile.ZipFile(WHEEL) as archive:
            members = archive.infolist()
            names = set()
            for item in members:
                name = item.filename
                relative = PurePosixPath(name)
                if (not name or relative.is_absolute() or ".." in relative.parts
                        or ":" in name or "\\" in name or name in names
                        or (item.external_attr >> 16) & 0o170000 == 0o120000):
                    raise ValueError("Miembro inseguro del WHL oficial: " + name)
                names.add(name)
            bad_member = archive.testzip()
            if bad_member is not None:
                raise ValueError("CRC del WHL incorrecto: " + bad_member)
            target.mkdir(parents=True, exist_ok=True)
            archive.extractall(target)
        marker.write_text(json.dumps({"wheel_sha256": WHEEL_SHA,
            "method": "Unmodified official wheel, local extraction; no pip or network"}, indent=2), encoding="utf8")
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[name] = "1"


def help_text():
    return """DEE Cognitive System 1.1 — entrada local del sistema original

INICIAR.bat usar --nueva IDENTIDAD_NUEVA
    Importa explicitamente una copia del par APD03 seleccionado; nunca T0.
INICIAR.bat usar --vida IDENTIDAD
    Continua la misma copia ya guardada en sistema/estado.
INICIAR.bat usar --help
    Ayuda de la entrada de una terminal existente.
INICIAR.bat gestor [COMANDO Y ARGUMENTOS]
    Delega literalmente a sistema/gestionar.py. Sin comando: estado pasivo.
INICIAR.bat gestor --help
    Comandos reales del gestor existente.

No se sustituye ACTIVO ni se crea un universo al abrir esta ayuda.
Las consultas materiales y continuar una vida si pueden avanzar su estado.
"""


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help", "ayuda"):
        print(help_text())
        return 0
    if args[0] not in ("usar", "gestor"):
        raise ValueError("Operacion desconocida. Utilice INICIAR.bat --help.")
    # La presencia de este archivo cambiaria usar_dee a DistributionBackend.
    # Se rechaza la ambiguedad en vez de redirigir silenciosamente las vidas.
    if (ROOT / "actualizaciones/arrancar.py").exists():
        raise RuntimeError("Raiz ambigua: contiene el lanzador de distribucion. No se cambia sistema/estado por trabajo_personal.")
    system = ROOT / "sistema"
    script = system / ("app/usar_dee.py" if args[0] == "usar" else "gestionar.py")
    if not script.is_file():
        raise FileNotFoundError("Falta el componente operativo existente: " + str(script))
    prepare()
    forwarded = args[1:]
    if args[0] == "usar":
        command = [str(PYTHON), "-I", "-B", "-X", "utf8", str(script), "--raiz", str(ROOT), *forwarded]
    else:
        command = [str(PYTHON), "-I", "-B", "-X", "utf8", str(script), *(forwarded or ["estado"])]
    return subprocess.call(command, cwd=PYTHON.parent)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(type(error).__name__ + ": " + str(error), file=sys.stderr)
        raise SystemExit(2)
