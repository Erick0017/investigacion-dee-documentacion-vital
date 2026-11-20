"""Append only SEM01; no publication unless --publish-atomic is explicit.

Inherited local ZIP records are copied byte-exact and never recompressed.
Historical root manifests remain historical and are not regenerated.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import shutil
import sys
import uuid
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_append import SECTION,inherited_inventory,package_prefix,sha_file,verify

RESERVED={"MANIFEST.json","HASHES.sha256","PARENT_PACKAGE.json","PARENT_MEMBERS.json"}
EXCLUDED_DIRS={"staging","__pycache__",".pytest_cache",".venv","venv","node_modules"}
OFFICIAL_NAME="CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip"


def write_json(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8")


def section_files(root,parent_sha):
    output=[]
    for path in sorted(root.rglob("*")):
        relative=path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in relative.parts):continue
        if path.is_symlink():raise ValueError("Symlinks are not included: "+str(relative))
        if not path.is_file() or str(relative).replace("\\","/") in RESERVED:continue
        if path.suffix.lower()==".zip" and sha_file(path)==parent_sha:raise ValueError("Do not nest the old CPC3 ZIP inside SEM01")
        output.append((path,relative.as_posix()))
    return output


def build(parent,section_root,output,expected_parent_sha,publish_atomic=False):
    parent,root,output=Path(parent).resolve(),Path(section_root).resolve(),Path(output).resolve()
    if not root.is_dir():raise ValueError("Section workspace does not exist")
    if sha_file(parent)!=expected_parent_sha:raise ValueError("Parent SHA256 does not match the frozen cut")
    publication=output==parent or output.name.casefold()==OFFICIAL_NAME.casefold()
    if publication and not publish_atomic:raise ValueError("Official replacement requires explicit --publish-atomic")
    if output.is_relative_to(root) and "staging" not in output.relative_to(root).parts:
        raise ValueError("A candidate inside the section workspace must live under staging/")
    with zipfile.ZipFile(parent) as archive:
        if archive.testzip() is not None:raise ValueError("Parent CRC failure")
        prefix=package_prefix(archive);addition=prefix+SECTION;inherited=inherited_inventory(archive)
        if any(x["name"].startswith(addition) for x in inherited):raise ValueError("Parent already contains SEM01; preserve attempts rather than overwriting entries")
    parent_inventory={"schema":1,"parent_sha256":expected_parent_sha,"prefix":prefix,"members":inherited}
    inventory_path=root/"PARENT_MEMBERS.json"
    if inventory_path.exists():
        existing=json.loads(inventory_path.read_text(encoding="utf-8"))
        if existing!=parent_inventory:raise ValueError("Existing inherited inventory differs; do not silently overwrite it")
    else:write_json(inventory_path,parent_inventory)
    write_json(root/"PARENT_PACKAGE.json",{"sha256":expected_parent_sha,"filename":parent.name,"members":len(inherited),"prefix":prefix,
                "added_section":SECTION,"preservation":"All inherited member bytes and original local compressed records preserved; historical manifests untouched"})
    files=section_files(root,expected_parent_sha)
    entries={relative:{"size":path.stat().st_size,"sha256":sha_file(path)} for path,relative in files}
    for name in ("PARENT_PACKAGE.json","PARENT_MEMBERS.json"):
        entries[name]={"size":(root/name).stat().st_size,"sha256":sha_file(root/name)}
    manifest={"schema":"CPC3.SEM01.append.v1","instrument":"DEE thinking4.0.0","kernel":27,
              "generated_utc":datetime.now(timezone.utc).isoformat(),"parent_sha256":expected_parent_sha,
              "scope":"Only the new SEM01 section; historical root manifests retain their old scope","files":dict(sorted(entries.items()))}
    write_json(root/"MANIFEST.json",manifest)
    hashes=dict(entries);hashes["MANIFEST.json"]={"size":(root/"MANIFEST.json").stat().st_size,"sha256":sha_file(root/"MANIFEST.json")}
    (root/"HASHES.sha256").write_text("".join(v["sha256"]+"  "+name+"\n" for name,v in sorted(hashes.items())),encoding="utf-8")
    packed=files+[(root/name,name) for name in sorted(RESERVED)]
    output.parent.mkdir(parents=True,exist_ok=True)
    temporary=output.parent/(output.name+".building-"+uuid.uuid4().hex+".tmp")
    shutil.copyfile(parent,temporary)
    with zipfile.ZipFile(temporary,"a",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for path,relative in packed:archive.write(path,addition+relative)
    for relative,entry in hashes.items():
        if sha_file(root/relative)!=entry["sha256"]:raise ValueError("Section changed while packaging: "+relative)
    result=verify(parent,temporary,expected_parent_sha)
    # This atomic replacement touches only the explicitly selected candidate or,
    # with the explicit publish flag, the official CPC3 target. No deletions.
    os.replace(temporary,output)
    result.update(output=str(output),publication=publication,atomic_replace=True)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument("--parent",type=Path,required=True);p.add_argument("--section-root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True);p.add_argument("--parent-sha256",required=True)
    p.add_argument("--publish-atomic",action="store_true");p.add_argument("--report",type=Path);args=p.parse_args()
    result=build(args.parent,args.section_root,args.output,args.parent_sha256,args.publish_atomic)
    if args.report:write_json(args.report,result)
    print(json.dumps(result))


if __name__=="__main__":main()
