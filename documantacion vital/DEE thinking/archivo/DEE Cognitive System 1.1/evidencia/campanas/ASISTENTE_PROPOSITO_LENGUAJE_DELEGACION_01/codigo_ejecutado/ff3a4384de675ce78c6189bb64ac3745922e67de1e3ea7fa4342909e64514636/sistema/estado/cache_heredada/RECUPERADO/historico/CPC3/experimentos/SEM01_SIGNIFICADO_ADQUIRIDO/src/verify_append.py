"""Verify an additive CPC3 cut without changing parent or candidate bytes."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

SECTION = "experimentos/SEM01_SIGNIFICADO_ADQUIRIDO/"


def sha_bytes(value):return hashlib.sha256(value).hexdigest()
def sha_file(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):h.update(block)
    return h.hexdigest()


def package_prefix(archive):
    names=archive.namelist();candidates=[]
    for name in names:
        if name.endswith("HASHES.sha256"):
            prefix=name[:-len("HASHES.sha256")]
            if prefix+"MANIFEST.json" in names and all(n.startswith(prefix) for n in names):candidates.append(prefix)
    if not candidates:raise ValueError("No unique enclosing package root with historical HASHES/MANIFEST")
    return min(candidates,key=len)


def inherited_inventory(archive):
    names=archive.namelist()
    if len(names)!=len(set(names)):raise ValueError("Duplicate ZIP names are not admissible")
    return [{"name":i.filename,"size":i.file_size,"crc32":i.CRC,"sha256":sha_bytes(archive.read(i))} for i in archive.infolist()]


def prefix_sha(path,length):
    h=hashlib.sha256();remaining=length
    with Path(path).open("rb") as stream:
        while remaining:
            block=stream.read(min(1024*1024,remaining))
            if not block:raise ValueError("Truncated inherited local-data prefix")
            h.update(block);remaining-=len(block)
    return h.hexdigest()


def verify(parent,candidate,expected_parent_sha):
    parent,candidate=Path(parent),Path(candidate)
    actual=sha_file(parent)
    if actual!=expected_parent_sha:raise ValueError("Parent identity differs from the frozen expected SHA256")
    if parent.resolve()==candidate.resolve():raise ValueError("Verification requires separate parent and candidate files")
    with zipfile.ZipFile(parent) as old,zipfile.ZipFile(candidate) as new:
        if old.testzip() is not None or new.testzip() is not None:raise ValueError("ZIP CRC failure")
        prefix=package_prefix(old);addition=prefix+SECTION
        old_names=old.namelist();new_names=new.namelist()
        if len(new_names)!=len(set(new_names)):raise ValueError("Duplicate names in candidate")
        if any(n.startswith(addition) for n in old_names):raise ValueError("Parent already contains this SEM01 section")
        extras=set(new_names)-set(old_names)
        if not extras or set(old_names)-set(new_names) or any(not n.startswith(addition) for n in extras):
            raise ValueError("Candidate is not an exclusive additive SEM01 cut")
        inherited=inherited_inventory(old)
        for entry in inherited:
            now=new.getinfo(entry["name"])
            if now.file_size!=entry["size"] or sha_bytes(new.read(now))!=entry["sha256"]:
                raise ValueError("Inherited member changed: "+entry["name"])
        local_prefix=prefix_sha(parent,old.start_dir)
        if prefix_sha(candidate,old.start_dir)!=local_prefix:raise ValueError("Inherited local records/compressed payload prefix changed")
        identity=json.loads(new.read(addition+"PARENT_PACKAGE.json"))
        if identity["sha256"]!=actual or identity["members"]!=len(inherited) or identity["prefix"]!=prefix:
            raise ValueError("New parent-package identity is inconsistent")
        saved=json.loads(new.read(addition+"PARENT_MEMBERS.json"))
        if saved["parent_sha256"]!=actual or saved["members"]!=inherited or saved["prefix"]!=prefix:raise ValueError("Inherited inventory differs")
        hash_member=addition+"HASHES.sha256";checks={}
        for line in new.read(hash_member).decode("utf-8").splitlines():
            if not line.strip():continue
            match=re.fullmatch(r"([0-9a-fA-F]{64})\s+\*?(.+)",line)
            if not match:raise ValueError("Malformed new HASHES line")
            relative=match[2].replace("\\","/")
            q=PurePosixPath(relative)
            if q.is_absolute() or ".." in q.parts or relative in checks:raise ValueError("Unsafe or duplicate new hash path")
            name=addition+relative
            if name not in extras or sha_bytes(new.read(name))!=match[1].lower():raise ValueError("New member hash mismatch: "+relative)
            checks[relative]=match[1].lower()
        if {addition+p for p in checks}!=extras-{hash_member}:raise ValueError("New HASHES coverage mismatch")
        manifest=json.loads(new.read(addition+"MANIFEST.json"))
        if manifest["parent_sha256"]!=actual:raise ValueError("New manifest parent identity differs")
        files=manifest["files"]
        if set(files)!=set(checks)-{"MANIFEST.json"}:raise ValueError("New manifest coverage mismatch")
        for rel,entry in files.items():
            if entry["sha256"]!=checks[rel] or entry["size"]!=new.getinfo(addition+rel).file_size:raise ValueError("New manifest entry mismatch")
        return {"verified":True,"CRC":True,"all_inherited_member_bytes_equal":True,
                "inherited_local_records_prefix_equal":True,"inherited_prefix_bytes":old.start_dir,
                "inherited_prefix_sha256":local_prefix,"inherited_members":len(inherited),"new_members":len(extras),
                "parent_sha256":actual,"candidate_sha256":sha_file(candidate),"candidate_size":candidate.stat().st_size,
                "package_prefix":prefix,"new_section_prefix":addition,"new_hashes_verified":len(checks),
                "historical_root_manifests_not_modified":True}


def main():
    p=argparse.ArgumentParser();p.add_argument("--parent",type=Path,required=True);p.add_argument("--candidate",type=Path,required=True)
    p.add_argument("--parent-sha256",required=True);p.add_argument("--report",type=Path);args=p.parse_args()
    result=verify(args.parent,args.candidate,args.parent_sha256)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result))


if __name__=="__main__":main()
