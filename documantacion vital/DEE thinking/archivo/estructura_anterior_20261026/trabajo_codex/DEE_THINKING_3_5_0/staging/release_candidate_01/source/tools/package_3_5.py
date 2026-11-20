"""Reuse clean-tree/archive helpers; never publish 3.0 or touch evidence parents."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

NAME="DEE_thinking_3_5_0_ENTREGA_FINAL_RESULTADOS.zip"
WHEEL="dee_thinking-3.5.0-cp313-cp313-win_amd64.whl"

def sha(p):
    with p.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()

def module(name):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(name+".py"));m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def stage(a):
    legacy=module("package_3_0");root=a.workspace.resolve();target=a.stage.resolve()
    target.mkdir(parents=True,exist_ok=True)
    if any(target.iterdir()):raise FileExistsError("Use a fresh staging directory; no sealed staging overwritten")
    for name in ("README.md","PRODUCT_CONTRACT.json","PROJECT_METADATA.json","THIRD_PARTY_NOTICES.md"):
        shutil.copy2(root/name,target/name)
    for name,source in (("source",root/"source"),("docs",root/"docs"),("validation",root/"validation"),("install",a.install.resolve())):
        for p in legacy._tree_files(source,source_mode=name=="source"):
            if name=="validation" and any(part in ("debug",) for part in p.relative_to(source).parts):continue
            dest=target/name/p.relative_to(source);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    (target/"wheel").mkdir();shutil.copy2(a.wheel,target/"wheel"/WHEEL)
    evidence=target/"evidence";evidence.mkdir();shutil.copy2(a.science,evidence/a.science.name)
    if a.baseline_wheel:
        folder=evidence/"legacy_3_0";folder.mkdir();shutil.copy2(a.baseline_wheel,folder/a.baseline_wheel.name)
    print("STAGED",target)

def seal(target):
    entries=[{"path":p.relative_to(target).as_posix(),"size":p.stat().st_size,"sha256":sha(p)} for p in sorted(target.rglob("*")) if p.is_file() and p.relative_to(target).as_posix() not in ("MANIFEST.json","HASHES.sha256")]
    # Nested scientific manifests are inside the single immutable evidence ZIP.
    manifest=target/"MANIFEST.json";manifest.write_text(json.dumps({"schema":"dee-thinking-3.5.0-delivery-v1","product_version":"3.5.0","files":entries},indent=2),encoding="utf-8")
    hashes={e["path"]:e["sha256"] for e in entries};hashes["MANIFEST.json"]=sha(manifest)
    (target/"HASHES.sha256").write_text("".join(f"{h}  {n}\n" for n,h in sorted(hashes.items())),encoding="utf-8")

def assemble(a):
    legacy=module("package_3_0");target=a.stage.resolve();seal(target)
    candidate=a.candidate.resolve();candidate.parent.mkdir(parents=True,exist_ok=True)
    temp=candidate.with_suffix(candidate.suffix+".partial");legacy._zip_stage(target,temp)
    result=module("verify_delivery_3_5").verify(temp,not a.pre_extraction)
    os.replace(temp,candidate);print(json.dumps(result,indent=2))

def publish(a):
    candidate=a.candidate.resolve();output=a.output.resolve()
    assert output.name==NAME and candidate!=output
    result=module("verify_delivery_3_5").verify(candidate,True)
    if output.exists() and sha(output)!=sha(candidate):raise FileExistsError("Existing official 3.5 delivery differs; preserve it")
    wheel_folder=a.wheel_folder.resolve();wheel_folder.mkdir(parents=True,exist_ok=True);dest=wheel_folder/WHEEL
    with zipfile.ZipFile(candidate) as z:b=z.read("wheel/"+WHEEL)
    if dest.exists() and sha(dest)!=hashlib.sha256(b).hexdigest():raise FileExistsError("Existing loose wheel differs; preserve it")
    output.parent.mkdir(parents=True,exist_ok=True)
    if not output.exists():os.replace(candidate,output)
    temp=wheel_folder/(WHEEL+".partial");temp.write_bytes(b);os.replace(temp,dest)
    assert sha(dest)==result["wheel"]["sha256"]
    print(json.dumps({**result,"published_zip":str(output),"published_wheel":str(dest)},indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--mode",choices=["stage","assemble","publish"],required=True)
    for name in ("workspace","stage","install","wheel","science","baseline-wheel","candidate","output","wheel-folder"):p.add_argument("--"+name,type=Path)
    p.add_argument("--pre-extraction",action="store_true");a=p.parse_args()
    {"stage":stage,"assemble":assemble,"publish":publish}[a.mode](a)
