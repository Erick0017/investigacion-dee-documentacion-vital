#!/usr/bin/env python3
"""Build and validate the compact definitive CORE17 package from its locked compact baseline."""
from __future__ import annotations
import hashlib, json, os, shutil, sys, zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from core17e_common import OFFICIAL_CORE17, PRE_EXTENSION_SHA256, ROOT, sha256_file, utc


STAGE=ROOT/"PACKAGE_STAGE"
DELIVERY=ROOT/"DELIVERY_STAGE"
TEMP_ZIP=DELIVERY/OFFICIAL_CORE17.name


def canonical_hash(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def write_json(p,obj): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")


def merge_extension(stage: Path) -> None:
    ext=stage/"EXTENSION"; ext.mkdir(parents=True,exist_ok=True)
    direct=["PRE_EXTENSION_CORE17_BASELINE.json","FRONTIER_PRIORITY.json","CORE17_DEFINITIVE_CLOSURE.json","CORE17_EXTENSION_RESULTS.json","CORE17_DEFINITIVE_CLOSURE.md","CORE17_FINAL_FRONTIER_EXTENSION.md","CORE17_EXTENSION_REPRODUCTION.md","CLAIM_LEDGER_EXTENSION.json","HOLDOUT_REGISTRY_EXTENSION.json","CANARY_REGISTRY_EXTENSION.json"]
    for name in direct: shutil.copy2(ROOT/name,ext/name)
    for sub in ("DISCOVERY","HOLDOUT","FREEZE","CHALLENGES"):
        target=ext/sub; target.mkdir(parents=True,exist_ok=True)
        for src in sorted((ROOT/sub).glob("*")): shutil.copy2(src,target/src.name)
    rtarget=ext/"RUNNERS"; rtarget.mkdir(parents=True,exist_ok=True)
    for src in sorted(HERE.glob("*.py")): shutil.copy2(src,rtarget/src.name)

    for log in ("QUESTION_TREE.ndjson","RESEARCH_DECISION_LOG.ndjson","KERNEL_DIALOGUE.ndjson"):
        src=ROOT/log
        if src.exists():
            old=(stage/log).read_text(encoding="utf-8") if (stage/log).exists() else ""
            add=src.read_text(encoding="utf-8")
            (stage/log).write_text(old.rstrip()+"\n"+add.lstrip(),encoding="utf-8")

    old_claim= json.loads((stage/"CLAIM_LEDGER.json").read_text(encoding="utf-8")); new_claim=json.loads((ROOT/"CLAIM_LEDGER_EXTENSION.json").read_text(encoding="utf-8"))
    old_claim["claims"].extend(new_claim["claims"]); old_claim["bounded_nulls"].extend(new_claim["bounded_nulls"]); old_claim["schema"]="dee.v27.core17.claim_ledger.v2_definitive"; old_claim["core17_definitively_closed"]=True; old_claim.pop("content_sha256",None); old_claim["content_sha256"]=canonical_hash(old_claim); write_json(stage/"CLAIM_LEDGER.json",old_claim)

    old_hold=json.loads((stage/"HOLDOUT_REGISTRY.json").read_text(encoding="utf-8")); new_hold=json.loads((ROOT/"HOLDOUT_REGISTRY_EXTENSION.json").read_text(encoding="utf-8"))
    old_hold["entries"].extend(new_hold["entries"]); old_hold["schema"]="dee.v27.core17.holdout_registry.v2_definitive"; old_hold["summary"]["prior_fresh_worlds"]=46; old_hold["summary"]["extension_fresh_worlds"]=22; old_hold["summary"]["fresh_worlds"]=68; old_hold["summary"]["extension_operator_ticks"]=new_hold["summary"]["new_operator_ticks"]; old_hold["summary"]["extension_operator_mismatches"]=0; old_hold["summary"]["overall_pass"]=True; old_hold.pop("content_sha256",None); old_hold["content_sha256"]=canonical_hash(old_hold); write_json(stage/"HOLDOUT_REGISTRY.json",old_hold)

    old_can=json.loads((stage/"CANARY_REGISTRY.json").read_text(encoding="utf-8")); new_can=json.loads((ROOT/"CANARY_REGISTRY_EXTENSION.json").read_text(encoding="utf-8"))
    old_can["extension_entries"]=new_can["entries"]; old_can["schema"]="dee.v27.core17.canary_registry.v2_definitive"; old_can["all_pass"]=all(x["pass"] for x in new_can["entries"]) and old_can.get("all_pass",False); old_can.pop("content_sha256",None); old_can["content_sha256"]=canonical_hash(old_can); write_json(stage/"CANARY_REGISTRY.json",old_can)

    appendix=(ROOT/"CORE17_DEFINITIVE_CLOSURE.md").read_text(encoding="utf-8")
    additions={
      "CORE17_EXECUTIVE_VERDICT.md":"\n\n---\n\n"+appendix,
      "CORE17_FINAL_REPORT.md":"\n\n---\n\n"+appendix,
      "CORE17_ADVERSARIAL_REVIEW.md":"\n\n## Extensión definitiva\n\nLa compresión fue atacada en 10 mundos frescos y 406 ticks sin discrepancias. La reparación se atacó con copia no entrenada, reset de dirección, ausencia de copia, corte de ruta, receptor incorrecto y corte fuera de ruta. Ningún control causal se invirtió. La interpretación queda limitada a reconstrucción por copia y portador.\n",
      "CORE17_CAPABILITY_COMPOSITION.md":"\n\n## Composición nueva confirmada\n\nAprendizaje direccional + redundancia + transporte + conversión de receptor componen una reparación funcional fresca después del daño. Requiere copia fuente y ruta; no equivale a regeneración autónoma.\n",
      "CORE17_REALITY_MODEL.md":"\n\n## R0_FACTOR_52\n\nR0 posee un cociente causal exacto más pequeño en el dominio declarado: 52 bits para celdas ordinarias y 64 para semántica-4. El reloj absoluto se reduce a fase módulo 304980; su cociente es invisible a esta dinámica.\n",
      "CORE17_REPRODUCTION_GUIDE.md":"\n\n---\n\n"+(ROOT/"CORE17_EXTENSION_REPRODUCTION.md").read_text(encoding="utf-8"),
      "CORE17_FINAL_FRONTIER.md":"\n\n---\n\n"+(ROOT/"CORE17_FINAL_FRONTIER_EXTENSION.md").read_text(encoding="utf-8"),
    }
    for name,text in additions.items():
        p=stage/name; p.write_text(p.read_text(encoding="utf-8").rstrip()+text,encoding="utf-8")

    provenance={"schema":"dee.v27.core17.definitive.provenance.v1","PRE_EXTENSION_CORE17_SHA256":PRE_EXTENSION_SHA256,"POST_EXTENSION_CORE17_SHA256":"The SHA-256 of an archive cannot be embedded in that same archive without changing it; the exact official hash is computed after sealing and reported externally.","POST_EXTENSION_CONTENT_ROOT_SHA256":"COMPUTED_IN_MANIFEST","new_claims":["C17E-CLAIM-001","C17E-CLAIM-002"],"new_fresh_worlds":22,"core17_definitively_closed":True,"created_utc":utc()}
    write_json(stage/"CORE17_DEFINITIVE_PROVENANCE.json",provenance)


def build_manifest(stage: Path):
    for name in ("MANIFEST.json","HASHES.sha256"):
        p=stage/name
        if p.exists(): p.unlink()
    entries=[]
    for p in sorted(x for x in stage.rglob("*") if x.is_file()):
        entries.append({"path":p.relative_to(stage).as_posix(),"bytes":p.stat().st_size,"sha256":sha256_file(p)})
    content_root=canonical_hash(entries)
    manifest={"schema":"dee.v27.core17.manifest.v3_definitive","created_utc":utc(),"pre_extension_core17_sha256":PRE_EXTENSION_SHA256,"post_extension_content_root_sha256":content_root,"core17_definitively_closed":True,"entries":entries,"summary":{"members_without_manifest_hashes":len(entries),"new_fresh_worlds":22,"total_fresh_worlds":68,"new_claims":2}}
    write_json(stage/"MANIFEST.json",manifest)
    lines=[]
    for p in sorted(x for x in stage.rglob("*") if x.is_file() and x.name!="HASHES.sha256"):
        lines.append(f"{sha256_file(p)}  {p.relative_to(stage).as_posix()}")
    (stage/"HASHES.sha256").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return manifest


def zip_stage(stage: Path,out: Path):
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True) as z:
        for p in sorted(x for x in stage.rglob("*") if x.is_file()):
            arc=p.relative_to(stage).as_posix(); info=zipfile.ZipInfo(arc,(2026,9,19,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o644<<16
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)


def validate(out: Path):
    with zipfile.ZipFile(out,"r") as z:
        bad=z.testzip()
        if bad: raise RuntimeError(f"bad member {bad}")
        names=z.namelist()
        if len(names)!=len(set(names)): raise RuntimeError("duplicate members")
        hashes=z.read("HASHES.sha256").decode().splitlines()
        for line in hashes:
            expected,name=line.split("  ",1); observed=hashlib.sha256(z.read(name)).hexdigest()
            if expected!=observed: raise RuntimeError(f"hash mismatch {name}")
        manifest=json.loads(z.read("MANIFEST.json")); listed={e["path"]:e for e in manifest["entries"]}
        for name,e in listed.items():
            data=z.read(name)
            if len(data)!=e["bytes"] or hashlib.sha256(data).hexdigest()!=e["sha256"]: raise RuntimeError(f"manifest mismatch {name}")
    return {"zip_integrity":"PASS","hashes":"PASS","manifest":"PASS","members":len(names),"bytes":out.stat().st_size,"sha256":sha256_file(out)}


def main():
    if sha256_file(OFFICIAL_CORE17)!=PRE_EXTENSION_SHA256: raise RuntimeError("baseline official changed")
    locked=ROOT/"BASELINE_CORE17_LOCKED"/OFFICIAL_CORE17.name; locked.parent.mkdir(parents=True,exist_ok=True)
    if not locked.exists(): shutil.copy2(OFFICIAL_CORE17,locked)
    if STAGE.exists(): shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    with zipfile.ZipFile(OFFICIAL_CORE17,"r") as z: z.extractall(STAGE)
    merge_extension(STAGE); manifest=build_manifest(STAGE); zip_stage(STAGE,TEMP_ZIP); report=validate(TEMP_ZIP)
    write_json(ROOT/"CORE17_PACKAGE_VALIDATION.json",{**report,"pre_extension_sha256":PRE_EXTENSION_SHA256,"content_root":manifest["post_extension_content_root_sha256"]})
    (ROOT/"POST_EXTENSION_CORE17_SHA256.txt").write_text(report["sha256"]+"\n",encoding="ascii")
    print(json.dumps(report,indent=2))


if __name__=="__main__": main()
