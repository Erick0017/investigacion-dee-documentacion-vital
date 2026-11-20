"""Synthetic packaging checks only; never touches the official CPC3."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from package_append import build,OFFICIAL_NAME
from verify_append import sha_file,verify


def main():
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,required=True);args=p.parse_args()
    staging=args.root.resolve()/"staging";staging.mkdir(parents=True,exist_ok=True)
    folder=Path(tempfile.mkdtemp(prefix="package_tool_test_",dir=staging));parent=folder/"parent.zip"
    old=b"Scientific inherited bytes\x00\xff";manifest=json.dumps({"files":{"old.bin":{"bytes":len(old),"sha256":hashlib.sha256(old).hexdigest()}}}).encode()
    with zipfile.ZipFile(parent,"w",compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("P/old.bin",old);z.writestr("P/MANIFEST.json",manifest)
        z.writestr("P/HASHES.sha256",hashlib.sha256(old).hexdigest()+"  old.bin\n"+hashlib.sha256(manifest).hexdigest()+"  MANIFEST.json\n")
    parent_bytes=parent.read_bytes();expected=sha_file(parent);section=folder/"section";section.mkdir()
    (section/"LEEME.md").write_text("New SEM01 scientific section",encoding="utf-8")
    candidate=folder/"candidate.zip";report=build(parent,section,candidate,expected)
    checks={"valid_addition":report["verified"],"parent_file_unchanged":parent.read_bytes()==parent_bytes,
            "inherited_local_records_preserved":report["inherited_local_records_prefix_equal"]}
    def rejected(name,operation):
        try:operation()
        except ValueError:checks[name]=True
        else:checks[name]=False
    rejected("wrong_parent_hash",lambda:verify(parent,candidate,"0"*64))
    rejected("publication_requires_explicit_flag",lambda:build(parent,section,parent,expected))
    sealed=folder/"sealed_parent.zip";shutil.copyfile(parent,sealed)
    rejected("official_name_requires_flag_with_sealed_parent",lambda:build(sealed,section,folder/OFFICIAL_NAME,expected))
    bad=folder/"outside_section.zip";shutil.copyfile(candidate,bad)
    with zipfile.ZipFile(bad,"a") as z:z.writestr("P/unrelated.txt",b"outside allowed section")
    rejected("outside_section_rejected",lambda:verify(parent,bad,expected))
    changed=folder/"changed_inherited.zip"
    with zipfile.ZipFile(candidate) as source,zipfile.ZipFile(changed,"w") as target:
        for member in source.infolist():target.writestr(member,b"changed" if member.filename=="P/old.bin" else source.read(member))
    rejected("inherited_change_rejected",lambda:verify(parent,changed,expected))
    nested=folder/"nested_section";nested.mkdir();shutil.copyfile(parent,nested/"old_package.zip")
    rejected("nested_old_package_rejected",lambda:build(parent,nested,folder/"nested_candidate.zip",expected))
    assert parent.read_bytes()==parent_bytes
    result={"all_checks":all(checks.values()),"checks":checks,"scope":"Synthetic technical ZIPs under staging only; official CPC3 untouched", "test_directory":str(folder)}
    (staging/"PACKAGE_TOOLS_TEST.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    assert result["all_checks"],checks
    print(json.dumps(result))


if __name__=="__main__":main()
