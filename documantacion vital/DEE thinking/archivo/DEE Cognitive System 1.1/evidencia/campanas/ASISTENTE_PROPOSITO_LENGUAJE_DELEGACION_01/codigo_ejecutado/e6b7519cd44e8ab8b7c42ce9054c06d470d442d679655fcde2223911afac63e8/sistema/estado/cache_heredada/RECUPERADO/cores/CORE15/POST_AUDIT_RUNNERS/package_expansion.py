#!/usr/bin/env python3
"""Verify, package, atomically replace and seal the official expanded CORE15."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"NEW_RUNNERS"))
from extension_common import ARCHIVE, BASELINE_SHA, OFFICIAL, OFFICIAL_NAME, ROOT, audit_kernel, read_json, sha, utc, write_json, write_text


EXCLUDE_DIRS={"PACKAGE_STAGING","output","__pycache__"}
EXCLUDE_FILES={"HASHES.sha256","CORE15_SEAL.json"}


def package_files():
    rows=[]
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file(): continue
        rel=p.relative_to(ROOT)
        if any(part in EXCLUDE_DIRS for part in rel.parts): continue
        if rel.name in EXCLUDE_FILES or rel.suffix in {".pyc",".zip",".tmp"}: continue
        rows.append(p)
    return rows


def verify_source_freeze():
    freeze=read_json(ROOT/"SOURCE_FREEZE_EXPANSION.json"); bad=[]
    for rel,expected in freeze["source_hashes"].items():
        p=ROOT/rel
        if not p.is_file() or sha(p)!=expected: bad.append(rel)
    return freeze,bad


def main():
    completeness=read_json(ROOT/"CORE15_COMPLETENESS_AUDIT.json"); consistency=read_json(ROOT/"REPORT_CONSISTENCY_AUDIT.json"); integrity=read_json(ROOT/"CONFIRMATION_INTEGRITY_AUDIT.json")
    if not completeness["pass"] or not consistency["pass"] or not integrity["pass"]: raise RuntimeError("completion, consistency or confirmation integrity gate failed")
    kernel=audit_kernel("CORE15_EXPANSION_PREPACKAGE"); freeze,bad=verify_source_freeze()
    if bad: raise RuntimeError(f"source freeze mismatch before packaging: {bad}")
    if sha(OFFICIAL)!=BASELINE_SHA: raise RuntimeError("official baseline changed before atomic replacement")
    files_before=package_files()
    manifest={"schema":"dee.v27.core15.expanded.package.v1","status":"COMPLETE","edition":"CORE15_COMPLETE_EXPANSION_SUPERSEDING","official_filename":OFFICIAL_NAME,"supersedes_sha256":BASELINE_SHA,"baseline_locked_path":"BASELINE_CORE15_LOCKED/","baseline_claims_preserved":["C15R01","C15R02","C15R03","C15R04"],"baseline_holdouts":{"positive":"24/24","canaries":"24/24"},"expansion_holdouts":{"positive":"48/48","canaries":"44/48","unrepaired_limitation":"C15XC02 saturation made four temporal-removal canaries nondiscriminating"},"new_claims":{"fresh_revalidated":5,"fresh_positive_canary_partial":1},"kernel_hashes":kernel["observed"],"source_freeze_sha256":freeze["freeze_sha256"],"completeness_pass":True,"report_consistency_pass":True,"confirmation_integrity_pass":True,"rosetta_status":"MULTI_RELATION_INTERNAL_CONVERGENCE","external_identification":False,"parent_zips_embedded":False,"created_utc":utc()}
    write_json(ROOT/"MANIFEST.json",manifest)
    files=package_files(); hashes=[]
    for p in files:
        rel=p.relative_to(ROOT).as_posix(); hashes.append((sha(p),rel,p.stat().st_size))
    write_text(ROOT/"HASHES.sha256","".join(f"{digest}  {rel}\n" for digest,rel,_ in hashes))
    # verify after write
    for digest,rel,_ in hashes:
        if sha(ROOT/rel)!=digest: raise RuntimeError(f"pre-zip hash drift: {rel}")
    all_files=package_files()+[ROOT/"HASHES.sha256"]
    tmp=OFFICIAL.with_suffix(OFFICIAL.suffix+".tmp")
    if tmp.exists(): tmp.unlink()
    with zipfile.ZipFile(tmp,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True) as zf:
        for p in sorted(all_files): zf.write(p,p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(tmp) as zf:
        first_bad=zf.testzip(); names=set(zf.namelist()); forbidden=[n for n in names if n.lower().endswith((".zip",".whl",".pyd"))]
        if first_bad or forbidden: raise RuntimeError(f"zip validation failed crc={first_bad} forbidden={forbidden}")
        lines=zf.read("HASHES.sha256").decode("utf-8-sig").splitlines(); mismatches=[]
        for line in lines:
            expected,rel=line.split(None,1); rel=rel.strip().lstrip("*")
            if rel not in names or hashlib.sha256(zf.read(rel)).hexdigest()!=expected: mismatches.append(rel)
        if mismatches: raise RuntimeError(f"internal hash mismatch: {mismatches[:10]}")
    os.replace(tmp,OFFICIAL)
    final_sha=sha(OFFICIAL); size=OFFICIAL.stat().st_size
    seal={"schema":"dee.v27.core15.expanded.seal.v1","status":"SEALED","official_path":str(OFFICIAL),"sha256":final_sha,"size":size,"superseded_sha256":BASELINE_SHA,"zip_crc_pass":True,"internal_hashes_checked":len(hashes),"kernel_immutable":True,"completion_pass":True,"report_consistency_pass":True,"source_freeze_intact":True,"sealed_utc":utc()}; write_json(ROOT/"CORE15_SEAL.json",seal)
    # Archive-level hash catalogue and index are provenance, not extra ZIPs.
    archive_zips=sorted(ARCHIVE.glob("*.zip")); write_text(ARCHIVE/"HASHES.sha256","".join(f"{sha(p)}  {p.name}\n" for p in archive_zips))
    index=ARCHIVE/"INDICE_EXPEDIENTE.md"
    text=index.read_text(encoding="utf-8-sig") if index.exists() else "# Índice del expediente DEE\n"
    marker="15_DEE_V27_OBSERVER_SHADOW_MULTIPHYSICS_AND_FINAL_ROSETTA_RESULTADOS.zip"
    line=f"- `{marker}` — `{final_sha}` — {size} bytes — CORE15 expanded superseding edition.\n"
    existing=[x for x in text.splitlines() if marker not in x]; write_text(index,"\n".join(existing).rstrip()+"\n"+line)
    variants=[p.name for p in ARCHIVE.glob("*15*.zip")]
    if variants!=[OFFICIAL_NAME]: raise RuntimeError(f"unexpected CORE15 official variants: {variants}")
    print(json.dumps(seal,indent=2,sort_keys=True))


if __name__=="__main__": main()
