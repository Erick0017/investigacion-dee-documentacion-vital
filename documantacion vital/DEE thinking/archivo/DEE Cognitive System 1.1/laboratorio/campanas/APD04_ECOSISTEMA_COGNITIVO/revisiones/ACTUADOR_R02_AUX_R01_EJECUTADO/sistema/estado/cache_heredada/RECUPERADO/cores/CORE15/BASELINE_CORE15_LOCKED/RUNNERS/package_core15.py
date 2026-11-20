"""Final CORE15 gate, manifest, reproducibility package and atomic archive publication."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from core15_common import ARCHIVE,OFFICIAL_NAME,ROOT,audit_kernel,read_json,sha,utc,write_json,write_text


REQUIRED=[
 "Q_LEVEL_FORENSIC_ATLAS.json","OBSERVER_LIBRARY.json","OBSERVER_SEARCH_LEDGER.json","SHADOW_RESIDUAL_ATLAS.json","CORE01_14_CAUSAL_PHYSICS_GRAPH.json","INTERACTION_ATLAS.json","PHENOMENON_INTERACTION_MATRIX.json","DEE_COMPLETE_CAUSAL_GRAPH_CORE01_15.json","NATIVE_PHENOMENON_ATLAS.json","OBSERVER_SHADOW_CANDIDATES.json","HUMAN_EFFECTIVE_SHADOW.json","DISCOVERY_FLEXIBILITY_LEDGER.json","QUESTION_TREE.ndjson","KERNEL_DIALOGUE.ndjson","EXPERIMENT_REGISTRY.json","CLAIM_LEDGER.json","KERNEL_IMMUTABILITY_AUDIT.json","PARENT_CHAIN.json","REPORT_CONSISTENCY_AUDIT.json","CORE15_COMPLETENESS_AUDIT.json","STATE.json","EXECUTIVE_VERDICT.md","FINAL_REPORT.md","ADVERSARIAL_REVIEW.md","NEGATIVE_RESULTS.md","OPEN_QUESTIONS.md","FINAL_FRONTIER.md","TRANSVERSAL_CORE01_TO_15.md","MULTIPHYSICS_NATIVE_CROSSWALK.md","EXTERNAL_PHYSICS_CROSSWALK.md","SHARED_MAP_SEARCH.md","ROSETTA_PUZZLE_LEDGER.json","FINAL_ROSETTA_ATTEMPT.md","FINAL_EXTERNAL_FALSIFICATION_PROTOCOL.md","ROSETTA_STATUS.md","REPRODUCE.ps1"
]


def verify_freeze():
 freeze=read_json(ROOT/"SOURCE_FREEZE.json");bad=[]
 for row in freeze["files"]:
  p=ROOT/row["path"]
  if not p.is_file() or sha(p)!=row["sha256"]:bad.append(row["path"])
 if bad:raise RuntimeError(f"frozen confirmation source changed: {bad}")


def update_archive_index(final_sha,size):
 zips=sorted(ARCHIVE.glob("*.zip"),key=lambda p:p.name)
 lines=[f"{sha(p)}  {p.name}\n" for p in zips]
 write_text(ARCHIVE/"HASHES.sha256","".join(lines))
 core_rows=[]
 for p in zips:
  if len(p.name)>=3 and p.name[:2].isdigit() and p.name[2]=="_":core_rows.append(f"| CORE{p.name[:2]} | `{p.name}` | `{sha(p)}` | {p.stat().st_size} |")
 index="# Índice del expediente DEE v27\n\n| CORE | Archivo | SHA256 | bytes |\n|---|---|---|---:|\n"+"\n".join(core_rows)+"\n\nMASTER vigente: `"+str(next((p.name for p in zips if p.name.startswith("DEE_V27_MASTER_REVALIDATION")),"none"))+"`.\n"
 write_text(ARCHIVE/"INDICE_EXPEDIENTE.md",index)


def main():
 seal_path=ROOT/"CORE15_SEAL.json"
 if seal_path.exists():print(seal_path.read_text(encoding="utf-8"));return
 verify_freeze();audit_kernel("CORE15_FINAL")
 comp=read_json(ROOT/"CORE15_COMPLETENESS_AUDIT.json");cons=read_json(ROOT/"REPORT_CONSISTENCY_AUDIT.json");state=read_json(ROOT/"STATE.json")
 missing=[name for name in REQUIRED if not (ROOT/name).exists()]
 dirs=["HOLDOUT_LOCKS","FRESH_CHALLENGES","CANARIES","RAW_OR_SPARSE_TELEMETRY","RUNNERS","INCIDENTS","NATIVE_FINGERPRINTS","RESULTS"]
 missing.extend(name+"/" for name in dirs if not (ROOT/name).is_dir())
 if missing:raise RuntimeError(f"required outputs missing: {missing}")
 if not comp.get("pass") or not cons.get("pass") or state.get("status")!="COMPLETE":raise RuntimeError("completion gate failed")
 excluded_parts={"output","__pycache__"};files=[]
 for p in ROOT.rglob("*"):
  if not p.is_file():continue
  rel=p.relative_to(ROOT)
  if any(part in excluded_parts for part in rel.parts) or p.suffix.lower()==".zip" or p.name in {"MANIFEST.json","HASHES.sha256","CORE15_SEAL.json"}:continue
  files.append(p)
 files=sorted(files,key=lambda p:str(p.relative_to(ROOT)).lower())
 manifest_rows=[{"path":str(p.relative_to(ROOT)).replace("\\","/"),"sha256":sha(p),"size":p.stat().st_size} for p in files]
 manifest={"status":"COMPLETE","parent":"CORE14","master_reliability_input":True,"files":manifest_rows,"file_count":len(manifest_rows),"parents_embedded":False,"created_utc":utc()};write_json(ROOT/"MANIFEST.json",manifest)
 write_text(ROOT/"HASHES.sha256","".join(f"{x['sha256']}  {x['path']}\n" for x in manifest_rows))
 package_files=files+[ROOT/"MANIFEST.json",ROOT/"HASHES.sha256"]
 tmp=ROOT/"output"/(OFFICIAL_NAME+".tmp");tmp.parent.mkdir(exist_ok=True)
 with zipfile.ZipFile(tmp,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(package_files,key=lambda p:str(p.relative_to(ROOT)).lower()):z.write(p,str(p.relative_to(ROOT)).replace("\\","/"))
 with zipfile.ZipFile(tmp) as z:
  if z.testzip() is not None:raise RuntimeError("temporary ZIP CRC failure")
  names=set(z.namelist());bad=[]
  for line in z.read("HASHES.sha256").decode("utf-8").splitlines():
   expected,name=line.split(None,1);name=name.strip().lstrip("*")
   if name not in names or hashlib.sha256(z.read(name)).hexdigest()!=expected:bad.append(name)
  if bad:raise RuntimeError(f"internal package hash mismatch: {bad}")
  if any(name.lower().endswith(".zip") for name in names):raise RuntimeError("embedded parent ZIP detected")
 official=ARCHIVE/OFFICIAL_NAME;os.replace(tmp,official);final_sha=sha(official);size=official.stat().st_size;update_archive_index(final_sha,size)
 summary=read_json(ROOT/"CORE15_CANONICAL_SUMMARY.json")
 seal={"status":"SEALED","zip_path":str(official),"zip_sha256":final_sha,"size":size,"completion_utc":utc(),"kernel_identity":read_json(ROOT/"KERNEL_IMMUTABILITY_AUDIT.json")["expected"],"manifest_sha256":sha(ROOT/"MANIFEST.json"),"state_sha256":sha(ROOT/"STATE.json"),"summary":summary};write_json(seal_path,seal)
 print(json.dumps({"kernel":seal["kernel_identity"],"CORE15":summary,"ZIP":{"path":str(official),"sha256":final_sha,"size":size}},indent=2))


if __name__=="__main__":main()
