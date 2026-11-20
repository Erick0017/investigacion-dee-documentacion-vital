"""Directed passive recovery. No historical or native runtime is imported."""
from __future__ import annotations
import argparse
import io
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile


def main():
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,required=True);p.add_argument("--dee-root",type=Path,required=True);args=p.parse_args()
    root=args.root.resolve();dee=args.dee_root.resolve();out=root/"fuentes";out.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(root/"src"));from verify_append import sha_bytes,sha_file,package_prefix,inherited_inventory
    expected={"wheel":"17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623",
              "native":"20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066",
              "kernel":"fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31"}
    evidence=[];extracted=[];capsules=[]
    def save_bytes(data,relative,origin,classification):
        target=out/relative;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=data:raise ValueError("Do not overwrite a different recovered source: "+relative)
        if not target.exists():target.write_bytes(data)
        extracted.append({"path":"fuentes/"+relative,"sha256":sha_bytes(data),"size":len(data),"source":origin,"classification":classification})
    def xml_text(blob):
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            xml=ET.fromstring(z.read("word/document.xml"))
        ns={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        return ("\n".join("".join(p.itertext()) for p in xml.findall(".//w:p",ns))+"\n").encode("utf-8")
    def verify_manifest(z,member):
        data=json.loads(z.read(member));files=data.get("files",{})
        entries=[dict(v,path=k) for k,v in files.items()] if isinstance(files,dict) else files
        prefix=member.rsplit("/",1)[0]+"/" if "/" in member else "";count=0
        for entry in entries:
            name=prefix+entry["path"].replace("\\","/")
            blob=z.read(name)
            if sha_bytes(blob)!=entry["sha256"]:raise ValueError("Manifest SHA mismatch: "+name)
            size=entry.get("size",entry.get("bytes"))
            if size is not None and size!=len(blob):raise ValueError("Manifest size mismatch: "+name)
            count+=1
        return count
    def verify_hashes(z,member):
        prefix=member[:-len("HASHES.sha256")];count=0
        for line in z.read(member).decode("utf-8").splitlines():
            if not line.strip():continue
            match=re.fullmatch(r"([a-fA-F0-9]{64})\s+\*?(.+)",line)
            if not match:raise ValueError("Malformed hashes line")
            name=prefix+match[2].replace("\\","/")
            if sha_bytes(z.read(name))!=match[1].lower():raise ValueError("HASHES mismatch: "+name)
            count+=1
        return count
    def archive_identity(path,known=None):
        actual=sha_file(path)
        if known is not None and known!=actual:raise ValueError("Artifact identity mismatch: "+str(path))
        z=zipfile.ZipFile(path)
        if z.testzip() is not None:raise ValueError("CRC failure: "+str(path))
        row={"path":str(path),"sha256":actual,"size":path.stat().st_size,"members":len(z.infolist()),"CRC":True,
             "expected_sha256":known,"expected_supplied":known is not None}
        evidence.append(row);return z,row
    parent=dee/"casos practicos/CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip"
    z,row=archive_identity(parent);prefix=package_prefix(z);row["prefix"]=prefix
    row["root_manifest_verified_entries"]=verify_manifest(z,prefix+"MANIFEST.json")
    row["root_hashes_verified_entries"]=verify_hashes(z,prefix+"HASHES.sha256")
    inventory={"schema":1,"parent_sha256":row["sha256"],"prefix":prefix,"members":inherited_inventory(z)}
    target=root/"PARENT_MEMBERS.json"
    if target.exists() and json.loads(target.read_text(encoding="utf-8"))!=inventory:raise ValueError("Existing parent inventory differs")
    if not target.exists():target.write_text(json.dumps(inventory,indent=2),encoding="utf-8")
    for member in z.namelist():
        relative=member.removeprefix(prefix)
        select=(relative.startswith("fuentes_pertinentes/I01/") or relative.startswith("fuentes_pertinentes/I02/")
                or relative in ("fuentes_pertinentes/MECHANISM_INDEX.json","fuentes_pertinentes/documentos/Procesamiento_Nativo_DEE_Libro_Manual_v1.txt",
                    "fuentes_pertinentes/documentos/ORGANIZACION_BASAL_PERSISTENTE_DOCUMENTO_MAESTRO_V2_1.txt")
                or relative.startswith("genealogia/CP02_B/") and relative.endswith((".py",".md",".json")))
        if select and not member.endswith("/"):
            save_bytes(z.read(member),"CPC3/"+relative,{"archive":row["sha256"],"member":member},"historical_experiment_or_constructor; not executed")
    z.close()
    receipt=json.loads((dee/"4.0/DELIVERY_RECEIPT.json").read_text(encoding="utf-8"))
    product=dee/"4.0/DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip";z,row=archive_identity(product,receipt["sha256"]);pre=package_prefix(z);row["prefix"]=pre
    row["root_manifest_verified_entries"]=verify_manifest(z,pre+"MANIFEST.json")
    row["root_hashes_verified_entries"]=verify_hashes(z,pre+"HASHES.sha256")
    selected=["PRODUCT_CONTRACT.json","docs/COGNITIVE_API_4.md","docs/INFORMATIVE_API_4.md","docs/RESULTS_MECHANISM_REVIEW.json",
              "source/src/cognitive.cpp","source/src/informative.cpp","source/src/organization_recipes.cpp","source/src/kernel_v27.cpp",
              "source/include/dee_thinking/cognitive.hpp","source/include/dee_thinking/informative.hpp","source/include/dee_thinking/organizational.hpp",
              "source/bindings/cognitive_pybind.cpp","source/bindings/informative_pybind.cpp","source/bindings/organizational_pybind.cpp",
              "source/python/dee_thinking/_native.pyi","source/tests/python/test_cognitive_api.py","source/tests/python/test_informative4.py",
              "source/tests/python/test_cognition_facilitators.py","app/mundo_nativo.py","experiments/BLOCK_II/RESULTS.json"]
    for rel in selected:
        member=pre+rel
        if member not in z.namelist():continue
        blob=z.read(member)
        if rel.endswith("kernel_v27.cpp") and sha_bytes(blob)!=expected["kernel"]:raise ValueError("Kernel source mismatch")
        save_bytes(blob,"producto4/"+rel,{"archive":row["sha256"],"member":member},"published_in_4_0")
    packaged_wheel=next(n for n in z.namelist()if n.endswith("dee_thinking-4.0.0-cp313-cp313-win_amd64.whl"))
    wheel_blob=z.read(packaged_wheel)
    loose=dee/"4.0/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl"
    if sha_bytes(wheel_blob)!=expected["wheel"] or sha_file(loose)!=expected["wheel"]:raise ValueError("Official wheel identity mismatch")
    with zipfile.ZipFile(io.BytesIO(wheel_blob)) as wheel:
        native=next(n for n in wheel.namelist()if n.endswith("_native.cp313-win_amd64.pyd"))
        if sha_bytes(wheel.read(native))!=expected["native"]:raise ValueError("Native PYD mismatch")
    row["wheel_and_native_expected_hashes_verified"]=True;z.close()
    for name,label in [("DEE_thinking_4_0_0_Libro_Blanco_y_Manual_Tecnico.docx","manual40"),("DEE_thinking_4_0_0_Maestro_Arquitectura_Reconstruccion.docx","maestro40")]:
        path=dee/"4.0"/name;outer,docrow=archive_identity(path)
        save_bytes(xml_text(path.read_bytes()),"textos/"+label+".txt",{"document_sha256":docrow["sha256"],"member":"word/document.xml"},"published_document_4_0; XML text extraction")
        capsule_member=next(n for n in outer.namelist()if n.endswith(".zip"));blob=outer.read(capsule_member)
        with zipfile.ZipFile(io.BytesIO(blob)) as cap:
            if cap.testzip() is not None:raise ValueError("Capsule CRC failure")
            capsule={"document_sha256":docrow["sha256"],"member":capsule_member,"sha256":sha_bytes(blob),"size":len(blob),
                     "manifest_entries_verified":verify_manifest(cap,"CAPSULE_MANIFEST.json"),"CRC":True}
            capsules.append(capsule)
            save_bytes(cap.read("CAPSULE_MANIFEST.json"),"capsulas/"+label+"_CAPSULE_MANIFEST.json",capsule,"passive_capsule_manifest_verified")
            if label=="manual40":save_bytes(blob,"capsulas/manual40.zip",capsule,"complete small passive capsule; never executed")
            for member in cap.namelist():
                if member in ("Contexto/Procesamiento_Nativo_DEE_texto_extraido.txt","Criterios_editoriales/CONTINUIDAD_INTERPRETATIVA.md","fuentes_e_identidades.json","LEEME_RECUPERACION.md"):
                    save_bytes(cap.read(member),"capsulas/"+label+"/"+member,{**capsule,"payload_member":member},"passive_recovery_reference")
        outer.close()
    core_specs=[("06_DEE_V27_NATIVE_LEARNING_C_RELATIVITY_AND_ROSETTA_CLOSURE_RESULTADOS.zip","CORE06",["NATIVE_LEARNING.md","LEARNING_CAUSAL_MECHANISM.md","ARITHMETIC_LEARNING.md","RUNNERS/native_core.py","RUNNERS/run_c6h01_associative_plasticity_holdout.py","RUNNERS/run_c6h02_class_generalization_reversal_holdout.py","RUNNERS/run_c6d04_reversal_extinction_transfer.py"]),
                ("07_DEE_V27_UNIVERSAL_EXPERIMENTAL_ATLAS_AND_FINAL_SYNTHESIS_RESULTADOS.zip","CORE07",["SOURCE_INDEX.json","LEARNING_TRANSFER.md","MATTER_REPROGRAMMING.md","RUNNERS/core07_common.py","RUNNERS/run_c7h01_functional_learning_transfer.py","RUNNERS/run_c7h03_reprogrammable_functional_matter.py","HOLDOUT_LOCKS/C7H01_FUNCTIONAL_LEARNING_TRANSFER.json","HOLDOUT_LOCKS/C7H03_REPROGRAMMABLE_FUNCTIONAL_MATTER.json"])]
    for name,label,selected in core_specs:
        path=dee.parent/"cores"/name;archive,corerow=archive_identity(path)
        for relative in selected:
            matches=[n for n in archive.namelist()if n==relative or n.endswith("/"+relative)]
            if len(matches)!=1:raise ValueError("Historical exact-source selection ambiguous/missing: "+relative)
            save_bytes(archive.read(matches[0]),label+"/"+relative,{"archive":corerow["sha256"],"member":matches[0]},"historical_experiment; requires short revalidation under4 before use")
        archive.close()
    provenance={"schema":1,"scope":"Directed passive source recovery for SEM01; no historical runners executed and no product/original modified",
                "expected_identities":expected,"artifacts":evidence,"capsules":capsules,"recovered":extracted,
                "parent_member_inventory":"PARENT_MEMBERS.json","classification":"Published4 implementation, historical experiments and research constructors are not equivalent evidence",
                "capsule_scope":"Manual small capsule retained whole; Maestro capsule fully verified but only relevant members recovered, avoiding duplicate official product ZIP"}
    (out/"PROVENANCE.json").write_text(json.dumps(provenance,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({"artifacts":len(evidence),"recovered":len(extracted),"capsules_verified":len(capsules),"parent_sha256":inventory["parent_sha256"],"path":str(out/"PROVENANCE.json")}))


if __name__=="__main__":main()
