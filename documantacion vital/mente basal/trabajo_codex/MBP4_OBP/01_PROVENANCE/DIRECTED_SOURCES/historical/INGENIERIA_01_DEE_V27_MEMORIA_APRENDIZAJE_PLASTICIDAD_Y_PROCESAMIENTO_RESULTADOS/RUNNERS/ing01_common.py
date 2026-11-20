#!/usr/bin/env python3
"""Shared paths, hashing and pinned v27 runtime for INGENIERIA 01."""
from __future__ import annotations
import hashlib, importlib.util, json, platform, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
TESTS=ROOT.parents[2]
CORE=TESTS/"EXPEDIENTE_EXPERIMENTOS_DEE"/"CORE"
CORE17_WORK=TESTS/"DEE_V27_CORE17_COMPLETE_REALITY_INTEGRATION_WORK"
CORE17_EXTENSION=TESTS/"DEE_V27_CORE17_DEFINITIVE_CLOSURE_WORK"
BASE_RUNNERS=HERE/"VENDORED"
CORE17_OFFICIAL=CORE/"17_DEE_V27_REALITY_UNIFICATION_CROSS_SCALE_PHYSICS_AND_CAPABILITIES_RESULTADOS.zip"
CORE17_SHA="b81eab5361d5364fff800763c9fef78d343d0326f1c5c225cadf319a49bc004a"
EXPECTED_KERNEL_SHA="0b17ba32037935a255b0f2182a52137bceab424f7e09126b761076b63e42c6ff"
EXPECTED_WHEEL_SHA="69297e6f06761c8b2f65d24a3fd7a2f16a3f67595a7f9660739ab65f47abc939"


def utc(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def sha256_file(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""): h.update(block)
    return h.hexdigest()
def canonical_hash(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def seal(obj): obj=dict(obj); obj.setdefault("created_utc",utc()); obj["content_sha256"]=canonical_hash(obj); return obj
def write_json(path,obj): path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
def append_ndjson(path,obj): path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); path.open("a",encoding="utf-8").write(json.dumps({"created_utc":utc(),**obj},sort_keys=True,ensure_ascii=False)+"\n")


def load_kernel(threads=1):
    sys.path.insert(0,str(BASE_RUNNERS))
    import core10_common
    kernel,runtime=core10_common.verify_and_load_kernel(threads)
    observed=runtime["observed_hashes"]
    if observed["kernel"]!=EXPECTED_KERNEL_SHA:
        raise RuntimeError("kernel identity mismatch")
    if observed.get("wheel") is not None and observed["wheel"]!=EXPECTED_WHEEL_SHA:
        raise RuntimeError("wheel identity mismatch")
    return kernel,runtime

def runtime_audit(label):
    kernel,runtime=load_kernel(1)
    return {"label":label,**runtime,"platform":platform.platform(),"numpy":np.__version__}
