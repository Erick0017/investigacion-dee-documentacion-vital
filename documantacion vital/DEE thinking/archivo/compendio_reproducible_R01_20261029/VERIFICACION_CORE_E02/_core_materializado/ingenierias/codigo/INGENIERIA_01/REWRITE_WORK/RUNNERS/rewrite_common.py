#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent;WORK=HERE.parent;ROOT=WORK.parent
sys.path.insert(0,str(ROOT/"RUNNERS"))
from ing01_common import load_kernel,sha256_file,canonical_hash  # noqa:E402
sys.path.insert(0,str(ROOT/"RUNNERS"))
from ing01_apparatus import *  # noqa:E402,F401,F403
def utc():return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def seal(x):x=dict(x);x.setdefault("created_utc",utc());x["content_sha256"]=canonical_hash(x);return x
def write_json(path,x):Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).write_text(json.dumps(x,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
def append(path,x):Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).open("a",encoding="utf-8").write(json.dumps({"created_utc":utc(),**x},sort_keys=True,ensure_ascii=False)+"\n")
