"""Finite sealing and atomic publication of the new, independent CPC4 record."""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
import os
import ctypes
from pathlib import Path, PurePosixPath
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.common import sha,put,WHEEL_SHA,NATIVE_SHA,KERNEL_SHA,PARENT_SHA

EXCLUDED={".venv","__pycache__","staging","reproduction_work",".git"}
EXCLUDED_FILES={"MANIFEST.json","HASHES.sha256","DELIVERY.json"}
OFFICIAL="CPC4_COMUNICACION_NATIVA_Y_META_ROSETTA_RESULTADOS.zip"


def inputs():
    result=[]
    for p in ROOT.rglob("*"):
        if not p.is_file():continue
        rel=p.relative_to(ROOT)
        if any(x in EXCLUDED for x in rel.parts):continue
        if rel.as_posix() in EXCLUDED_FILES or p.suffix.lower() in (".pyc",".tmp"):continue
        if p.name==OFFICIAL or p.name.endswith(".candidate.zip"):continue
        result.append(p)
    return sorted(result,key=lambda x:x.relative_to(ROOT).as_posix())


def seal():
    entries=[{"path":p.relative_to(ROOT).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)} for p in inputs()]
    value={"format":"CPC4_MANIFEST_V1","author":"Ivan Erick Tlaltecatl Morales",
           "created_utc":datetime.now(timezone.utc).isoformat(),
           "scope":"New CPC4 record only; no historical ZIP nested; no virtual environment/toolchain/cache",
           "excludes":["MANIFEST.json","HASHES.sha256"],
           "hash_rule":"MANIFEST lists payload only; HASHES covers payload plus MANIFEST, excluding itself. ZIP hash is external.",
           "files":entries,"payload_expanded_bytes":sum(x["bytes"] for x in entries)}
    put(ROOT/"MANIFEST.json",value)
    hashes=[(x["path"],x["sha256"]) for x in entries]+[("MANIFEST.json",sha(ROOT/"MANIFEST.json"))]
    (ROOT/"HASHES.sha256").write_text("".join(h+"  "+p+"\n" for p,h in hashes),encoding="utf-8")
    return value


def verify_directory(root=ROOT):
    root=Path(root)
    manifest=json.loads((root/"MANIFEST.json").read_text(encoding="utf-8"))
    for x in manifest["files"]:
        p=root/x["path"]
        assert p.stat().st_size==x["bytes"] and sha(p)==x["sha256"],x["path"]
    lines=(root/"HASHES.sha256").read_text(encoding="utf-8").splitlines()
    for line in lines:
        h,name=line.split("  ",1)
        assert sha(root/name)==h,name
    assert len(lines)==len(manifest["files"])+1
    wheel=root/"runtime"/"dee_thinking-4.0.0-cp313-cp313-win_amd64.whl"
    assert sha(wheel)==WHEEL_SHA
    with zipfile.ZipFile(wheel) as z:
        assert z.testzip() is None
        pyd=[n for n in z.namelist() if n.endswith(".pyd")]
        assert len(pyd)==1 and hashlib.sha256(z.read(pyd[0])).hexdigest()==NATIVE_SHA
    required=["ejecutar.py","demostracion.py","EXPERIMENT_CONFIG.json","LEEME.md","INFORME.md",
              "CAPACIDADES.json","NSM65_CATALOGO.json","resultados/CLEAN_REPRODUCTION.json"]
    for name in required:assert (root/name).is_file(),name
    assert len(json.loads((root/"NSM65_CATALOGO.json").read_text(encoding="utf-8"))["entries"])==65
    return {"manifest_entries":len(manifest["files"]),"hash_entries":len(lines),"directory_hashes":True,"wheel_identity":True}


def verify_zip(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        names=z.namelist()
        assert len(names)==len(set(names))
        assert all(n.startswith("CPC4/") and ".." not in PurePosixPath(n).parts for n in names)
        manifest=json.loads(z.read("CPC4/MANIFEST.json"))
        expected={"CPC4/"+x["path"] for x in manifest["files"]}|{"CPC4/MANIFEST.json","CPC4/HASHES.sha256"}
        assert set(names)==expected
        for x in manifest["files"]:
            b=z.read("CPC4/"+x["path"])
            assert len(b)==x["bytes"] and hashlib.sha256(b).hexdigest()==x["sha256"],x["path"]
        for line in z.read("CPC4/HASHES.sha256").decode("utf-8").splitlines():
            h,name=line.split("  ",1)
            assert hashlib.sha256(z.read("CPC4/"+name)).hexdigest()==h,name
        return {"CRC":True,"manifest_hashes":True,"members":len(names),
                "expanded_bytes":sum(x.file_size for x in z.infolist()),"compressed_bytes":Path(path).stat().st_size}


def package(publish=False):
    manifest=seal()
    directory=verify_directory()
    stage=ROOT/"staging";stage.mkdir(exist_ok=True)
    candidate=stage/"CPC4.candidate.zip"
    payload=[ROOT/x["path"] for x in manifest["files"]]+[ROOT/"MANIFEST.json",ROOT/"HASHES.sha256"]
    with zipfile.ZipFile(candidate,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
        for p in payload:z.write(p,"CPC4/"+p.relative_to(ROOT).as_posix())
    verification=verify_zip(candidate)
    if publish:
        evidence=json.loads((ROOT/"resultados"/"CLEAN_REPRODUCTION.json").read_text(encoding="utf-8"))
        assert evidence["completed"] is True
        # Identity of the untouched CPC3 is checked immediately before publish.
        official_dir=ROOT.parents[1]
        cpc3=official_dir/"CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip"
        assert sha(cpc3)==PARENT_SHA
        target=official_dir/OFFICIAL
        if target.exists():
            raise FileExistsError("Protect existing CPC4 delivery; this campaign must not silently replace it")
        os.replace(candidate,target)
    else:target=candidate
    budget=json.loads((ROOT/"BUDGET.json").read_text(encoding="utf-8"))
    ctypes.windll.kernel32.GetTickCount64.restype=ctypes.c_uint64
    elapsed=(int(ctypes.windll.kernel32.GetTickCount64())-budget["monotonic_start_ms"])/1000
    assert elapsed<=budget["budget_seconds"],"Original total campaign budget exceeded"
    result={"path":str(target.resolve()),"sha256":sha(target),"verification":verification,"directory":directory,
            "elapsed_monotonic_seconds":elapsed,"finished_utc":datetime.now(timezone.utc).isoformat(),
            "original_deadline_utc":budget["deadline_utc"]}
    put(ROOT/"DELIVERY.json",result)
    print(json.dumps(result,indent=2))
    return result


def main(command):
    if command=="verify":print(json.dumps(verify_directory(),indent=2))
    elif command=="package":package(publish=True)
    else:raise ValueError(command)


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--publish",action="store_true");a=p.parse_args()
    package(a.publish)
