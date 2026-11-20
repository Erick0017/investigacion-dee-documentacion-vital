"""Close the private 1.1 delivery without modifying either sealed ZIP."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timezone

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""):
            h.update(b)
    return h.hexdigest()

def read(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))

def write_new(p,data):
    p=Path(p)
    with p.open("x",encoding="utf-8",newline="\n") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
        f.write("\n")

def identical_bytes(a,b):
    count=0
    with a.open("rb") as x,b.open("rb") as y:
        while True:
            xb,yb=x.read(1048576),y.read(1048576)
            if xb!=yb:
                raise AssertionError("Reconstructed bytes differ")
            count+=len(xb)
            if not xb:
                return count

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--verification",type=Path,required=True)
    p.add_argument("--union",type=Path,required=True)
    a=p.parse_args()
    root=a.root.resolve()
    delivery=root/"entregas"
    source=a.verification.resolve()/"VERIFICACION_EN_CURSO.json"
    proof=read(source)
    assert proof["status"]=="VERIFIED_BOUNDED_CONTRACTS"
    assert proof["last_completed_stage"]=="audit"
    assert len(proof["checks"])==22 and all(v["passed"] for v in proof["checks"].values())
    assert not (a.verification/"VERIFICADOR.lock").exists()
    assert len(proof["heritage_release"]["families"])==34
    assert all(x=="PASS" for x in proof["heritage_release"]["families"].values())
    assert len(proof["profile_release"]["checks"])==25
    assert all(x["passed"] for x in proof["profile_release"]["checks"].values())
    assert proof["historical_archives_used_by_system"] is False
    union=a.union.resolve()
    union.mkdir(exist_ok=False)
    parts_manifest=read(delivery/"PARTES.json")
    transport=[]
    for entry in parts_manifest["archives"]:
        original=delivery/entry["archive"]
        stem=original.stem
        seal=read(delivery/(stem+".SELLADO.json"))
        assert sha(original)==entry["sha256"]==seal["sha256"]
        assert original.stat().st_size==entry["bytes"]==seal["bytes"]
        assert entry["sha256"] in (proof["system_sha256"],proof["audit_sha256"])
        for part in entry["parts"]:
            path=delivery/part["name"]
            assert 0<path.stat().st_size==part["bytes"]<16000000
            assert sha(path)==part["sha256"]
        target=union/entry["archive"]
        command=[sys.executable,"-I","-B","-X","utf8",str(delivery/"REUNIR_1_1.py"),
                 entry["archive"],"--salida",str(target)]
        begin=time.perf_counter()
        result=subprocess.run(command,cwd=union,capture_output=True,text=True,
                              encoding="utf-8",timeout=120,check=False)
        assert result.returncode==0,(result.stdout,result.stderr)
        compared=identical_bytes(original,target)
        assert compared==entry["bytes"] and sha(target)==entry["sha256"]
        with zipfile.ZipFile(target) as z:
            assert z.testzip() is None
            assert len(z.infolist())==seal["members"]
            assert sum(x.file_size for x in z.infolist())==seal["expanded_bytes"]
        transport.append({**seal,"parts":entry["parts"],
            "all_parts_below_exclusive_16000000_bytes":True,
            "reunifier_command":command,"reunifier_exit_code":result.returncode,
            "reunifier_stdout":result.stdout,"seconds":time.perf_counter()-begin,
            "reconstructed_path":str(target),"byte_by_byte_compared_bytes":compared,
            "whole_archive_sha256_equal":True,"CRC_all_members":"PASS"})
    assert len(transport)==2
    originals=read(root/"evidencia/verificaciones/ORIGINALES_SIN_MODIFICAR.json")
    for entry in originals["files"]:
        assert sha(entry["path"])==entry["before_sha256"]==entry["after_sha256"]
    budget=read(root/"PROYECTO.json")["budget"]
    elapsed=time.perf_counter()-budget["start_monotonic"]/budget["monotonic_frequency"]
    assert 0<elapsed<budget["budget_seconds"]
    owned_native=[x for x in proof["commands"] if x.get("job_resources") is not None]
    assert owned_native and all(x["owned_process_waited"] and x["owned_job_closed"] for x in owned_native)
    assert all(x["exit_code"]==0 and x["owned_process_waited"] for x in proof["commands"])
    final={**proof,"schema":"DEE.Cognitive.System.1.1.final.external.verification.v1",
        "closed_utc":datetime.now(timezone.utc).isoformat(),
        "final_check_report_source":str(source),"final_check_report_sha256":sha(source),
        "sealed_archives_and_transport":transport,
        "budget_original":budget,"total_monotonic_elapsed_seconds":elapsed,
        "budget_reset":False,
        "old_reference_artifacts_rehashed_unchanged":originals,
        "owned_final_verifier_native_commands_waited_and_jobs_closed":True,
        "no_automatic_future_simulation":True,
        "system_standalone_scope":"Admitted finite contracts only. CPython3.13x64, Windowsx64 and C++ runtime remain external. No historical CPC ZIPs, laboratory or evidence are needed for normal system operation.",
        "limitations":[
            "34 inherited families are finite recovered contracts, not34independent concepts or all historical claims.",
            "25profile checks reused only after full old payload identity; the two newly added historical parents were restored from the exact final ZIP.",
            "16broad historical rows remain documentary/pending; no complete recovery claim for those.",
            "An exact source revision of one failed earlyR2named runner was not found; its retained records do not establish learned regulatoryR2.",
            "No new NSM primitive is credited by this cut; K65is a repertoire of physical forms, not65human meanings.",
            "No functionalYO/TU, broad negation, semantic productivity, general learned source selection or regulatoryR2is certified.",
            "The Python file audit guard is not an OS security sandbox. CLI exception continuity is tested, not full ACID recovery from arbitrary power failure.",
            "An early actualRAM accounting gap and a brief verifier controller overlap are preserved. Global process inventory was denied; no statement about unrelated machine processes is made.",
            "The two requested4.5DOCX manuals were not located. Actual executable contracts and available technical files were used.",
            "The old project and resumption files inside sealed archives describe the preverification cut. This external final report and externalREANUDACIONidentify completed verification without changing those sealed bytes."
        ]}
    write_new(delivery/"VERIFICACION_FINAL_EXTERNA.json",final)
    reanudacion={"schema":"DEE.Cognitive.System.1.1.closure.v1",
        "status":"CERRADO_VERIFICADO_EN_DOMINIOS_DECLARADOS",
        "completed_utc":final["closed_utc"],"original_budget":budget,
        "elapsed_monotonic_seconds":elapsed,"automatic_resume_authorized":False,
        "active_life":"E1_SOCIAL_11","active_tick":3154,
        "active_snapshot_sha256":"51e2ec6a41f906607848c003c6a22e3e33690f57d20dcae90c8dbbc7ab9ad396",
        "final_archives":[{"name":x["file"],"sha256":x["sha256"]}for x in transport],
        "next_requires_new_execution":"Continue an explicitly selected life or start a new authorized laboratory cut; do not rerun completed experiments implicitly.",
        "sealed_internal_resumption_is_preverification_history":True}
    write_new(delivery/"REANUDACION.json",reanudacion)
    alias=delivery/"ALIAS_CANDIDATOS.json"
    previous=delivery/"candidatos/CANDIDATO_02/ALIAS_ANTERIOR_AL_CIERRE.json"
    if alias.exists() and not previous.exists():
        shutil.copyfile(alias,previous)
    alias_data={"schema":"DEE.Cognitive.System.final.archive.identities.v1",
        "note":"Canonical paths now identify these exact final bytes. Prior candidates remain separate historical cuts, not byte aliases.",
        "final":[{"file":x["file"],"sha256":x["sha256"]}for x in transport],
        "prior_alias_record_preserved":str(previous),
        "prior_record_no_longer_identifies_current_canonical_file":True}
    alias.write_text(json.dumps(alias_data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    hashes=[]
    for f in sorted(delivery.iterdir()):
        if f.is_file() and f.name!="HASHES_ENTREGA.sha256":
            hashes.append(sha(f)+"  "+f.name)
    (delivery/"HASHES_ENTREGA.sha256").write_text("\n".join(hashes)+"\n",encoding="utf-8")
    print(json.dumps({"status":final["status"],"total_seconds":elapsed,
        "checks":len(proof["checks"]),"transport_parts":sum(len(x["parts"])for x in transport),
        "packages":[{"name":x["file"],"bytes":x["bytes"],"members":x["members"],
                     "expanded_bytes":x["expanded_bytes"],"sha256":x["sha256"]}for x in transport],
        "external_verification_sha256":sha(delivery/"VERIFICACION_FINAL_EXTERNA.json")},
        ensure_ascii=False))
if __name__=="__main__":
    main()

