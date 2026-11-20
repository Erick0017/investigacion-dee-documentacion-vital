"""Directed provenance of the actual external process; does not import DEE."""
import argparse
import hashlib
import importlib
import importlib.metadata
import json
from pathlib import Path
import sys
import zipfile

p = argparse.ArgumentParser()
p.add_argument("--deps", type=Path, default=Path(__file__).with_name("deps"))
p.add_argument("--output", type=Path, required=True)
args = p.parse_args()
sys.path.insert(0, str(args.deps.resolve()))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

report = {"python_executable": sys.executable, "python_version": sys.version,
          "python_executable_sha256": digest(Path(sys.executable)), "packages": [], "wheel_cache": [],
          "identity_scope": "Selected actual external dependencies, not a historical inventory. DEE runtime is neither imported nor modified."}
for distname, modname in [("gymnasium", "gymnasium"), ("farama-notifications", "farama_notifications"),
                          ("numpy", "numpy"), ("cloudpickle", "cloudpickle"), ("typing-extensions", "typing_extensions")]:
    try:
        dist = importlib.metadata.distribution(distname)
        module = importlib.import_module(modname)
    except (importlib.metadata.PackageNotFoundError, ImportError) as exc:
        report["packages"].append({"name": distname, "version": None, "missing": type(exc).__name__,
                                   "scope": "Not exercised by tested synchronous Pendulum path; not claiming all Gymnasium features installed."})
        continue
    modulepath = Path(module.__file__)
    row = {"name": distname, "version": dist.version, "import_path": str(modulepath),
           "import_sha256": digest(modulepath), "requires_python": dist.metadata.get("Requires-Python")}
    for file in dist.files or []:
        if str(file).replace("\\", "/").endswith(".dist-info/RECORD"):
            record = Path(dist.locate_file(file))
            row["record_path"] = str(record)
            row["record_sha256"] = digest(record)
    report["packages"].append(row)
source = Path(importlib.import_module("gymnasium.envs.classic_control.pendulum").__file__)
report["pendulum_source"] = {"path": str(source), "sha256": digest(source)}
for candidate in Path(__file__).with_name("pip_cache").rglob("*.body"):
    if zipfile.is_zipfile(candidate):
        with zipfile.ZipFile(candidate) as z:
            names = [n for n in z.namelist() if n.endswith(".dist-info/METADATA")]
            report["wheel_cache"].append({"path": str(candidate), "bytes": candidate.stat().st_size,
                                         "sha256": digest(candidate), "metadata_members": names})
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(args.output), "packages": [{"name": x["name"], "version": x["version"]} for x in report["packages"]]}))
