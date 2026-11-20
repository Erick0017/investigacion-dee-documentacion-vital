"""Install and execute from a distinct clean extraction; never import old labs."""
from __future__ import annotations
import argparse
import ast
import ctypes
from datetime import datetime,timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.common import put,sha,PARENT_SHA
from supervise import owned_job


def command(argv,cwd,folder,timeout=180):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=False)
    with (folder/"stdout.log").open("w",encoding="utf-8") as out,(folder/"stderr.log").open("w",encoding="utf-8") as err:
        process=subprocess.Popen([str(x) for x in argv],cwd=str(cwd),stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
        job,info=owned_job(process)
        start=time.monotonic()
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            if job:job[0].TerminateJobObject(job[1],124)
            else:process.kill()
            process.wait(timeout=10)
            raise
        finally:
            if job:job[0].CloseHandle(job[1])
        result={"argv":[str(x) for x in argv],"cwd":str(cwd),"exit_code":process.returncode,
                "owned_windows_job":info,"elapsed_seconds":time.monotonic()-start}
    put(folder/"COMMAND.json",result)
    if process.returncode:raise RuntimeError("Clean command failed: "+str(folder))
    return result


def read(path):return json.loads(Path(path).read_text(encoding="utf-8"))


def run(candidate,base_python,temporary_parent):
    started=time.monotonic()
    work=Path(tempfile.mkdtemp(prefix="_CPC4_REPRO_",dir=temporary_parent)).resolve()
    extracted=work/"extracted";extracted.mkdir()
    with zipfile.ZipFile(candidate) as z:
        assert z.testzip() is None
        for name in z.namelist():
            target=(extracted/name).resolve()
            assert target.is_relative_to(extracted.resolve())
        z.extractall(extracted)
    package=extracted/"CPC4"
    environment=work/"clean_venv"
    outside=work/"outside";outside.mkdir()
    steps=[]
    steps.append(command([base_python,"-m","venv",environment],outside,work/"cmd01_venv",90))
    python=environment/"Scripts"/"python.exe"
    steps.append(command([python,"-m","pip","install","--no-index","--no-deps",package/"runtime"/"dee_thinking-4.0.0-cp313-cp313-win_amd64.whl"],outside,work/"cmd02_install",90))
    for number,verb in ((3,"identity"),(4,"verify")):
        steps.append(command([python,"-I","-B",package/"ejecutar.py",verb],outside,work/("cmd0"+str(number)+"_"+verb),180))
    imported=read(work/"cmd03_identity"/"stdout.log")
    assert Path(imported["module"]).resolve().is_relative_to(environment.resolve())
    assert "site-packages" in imported["module"]
    comparisons=[]
    for number,identifier in ((5,"MAIN_MINUS"),(6,"CUT_MINUS")):
        target=work/identifier
        steps.append(command([python,"-I","-B",package/"ejecutar.py","reproduce","--case",identifier,"--output",target],outside,work/("cmd0"+str(number)+"_"+identifier),240))
        actual=read(target/"MEASUREMENTS.json")
        expected=read(package/"resultados"/"confirmacion"/identifier/"MEASUREMENTS.json")
        assert actual["physical"]["final"]==expected["physical"]["final"]
        assert actual["physical"]["receipts"]==expected["physical"]["receipts"]
        assert actual["physical"]["B_common_responses"]==expected["physical"]["B_common_responses"]
        assert actual["physical"]["evaluations"]==expected["physical"]["evaluations"]
        if "language" in expected:
            assert actual["language"]["final"]==expected["language"]["final"]
            assert [(r["physical_output"],r["receipt"]) for r in actual["language"]["queries"]]==[(r["physical_output"],r["receipt"]) for r in expected["language"]["queries"]]
        comparisons.append({"case":identifier,"RAW_clocks_tick":True,"receipts":True,"physical_outputs":True,"actual_summary_sha256":sha(target/"MEASUREMENTS.json")})
        put(ROOT/"resultados"/"CLEAN_PROGRESS.json",{"work":str(work),"comparisons":comparisons})
    demo=work/"demo"
    steps.append(command([python,"-I","-B",package/"src"/"demo_validation.py","--output",demo,"--expected",package/"resultados"/"confirmacion"/"MAIN_MINUS"/"MEASUREMENTS.json"],outside,work/"cmd07_demo",300))
    proof=read(demo/"DEMONSTRATION_SUMMARY.json")
    assert proof["verified"] is True
    # A user-selected seed changes geometry only. Its event file is fixed before
    # execution and preserved; output is obtained from actual native evolution.
    seed_folder=work/"seed42";seed_folder.mkdir()
    events=seed_folder/"EVENTS.txt"
    final_seed=seed_folder/"USER_SEED42_FINAL267.deetsnap"
    events.write_text('crear semilla 42\nvivir - coherente -\nenseñar HAY\nenseñar NO\nconsultar HAY\nconsultar NO\nguardar "'+str(final_seed)+'"\nsalir\n',encoding="utf-8")
    put(ROOT/"resultados"/"CLEAN_SEED_CONFIG.json",{"frozen_before_run_utc":datetime.now(timezone.utc).isoformat(),"seed":42,"events_sha256":sha(events),"effect_of_seed":"Common translation only; never class, answer or decoder","classification":"TECHNICAL_FRESH_USER_SEED_REALIZATION"})
    steps.append(command([python,"-I","-B",package/"ejecutar.py","demonstrate","--events",events,"--output",seed_folder/"session"],outside,work/"cmd08_seed42",240))
    # Verification is external and never writes the translated world.
    steps.append(command([python,"-I","-B",package/"src"/"check_seed.py",
                          "--reference",package/"resultados"/"confirmacion"/"MAIN_MINUS"/"LENGUAJE"/"MAIN_FINAL267.deetsnap",
                          "--actual",final_seed,"--seed","42"],outside,work/"cmd09_seed_compare",60))
    seed_proof=read(work/"cmd09_seed_compare"/"stdout.log")
    selection=ROOT/"resultados"/"CLEAN_PROOFS";selection.mkdir(exist_ok=True)
    copies=[]
    for source in work.rglob("*"):
        if not source.is_file():continue
        rel=source.relative_to(work)
        if any(x in ("extracted","clean_venv") for x in rel.parts):continue
        if source.suffix==".deetsnap" and source!=final_seed:continue
        if source.suffix==".pyc" or "__pycache__" in rel.parts:continue
        target=selection/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        copies.append({"path":target.relative_to(ROOT).as_posix(),"sha256":sha(target),"bytes":target.stat().st_size})
    result={"completed":True,"classification":"CLEAN_INSTALLATION_AND_TECHNICAL_REPRODUCTION_NOT_NEW_INDEPENDENT_SCIENTIFIC_REPLICATES",
            "candidate_sha256":sha(candidate),"work_directory":str(work),"extracted_package":str(package),
            "clean_environment":str(environment),"source_private_dependencies_used":False,"identity":imported,
            "commands":steps,"comparisons":comparisons,"demo":proof,"user_seed42":seed_proof,
            "selected_proof_files":copies,"elapsed_seconds":time.monotonic()-started,
            "candidate_role":"Final experimental code/data candidate. Final sealing adds this proof record and final audits without changing the executed implementation."}
    put(ROOT/"resultados"/"CLEAN_REPRODUCTION.json",result)
    print(json.dumps({"completed":True,"work":str(work),"elapsed_seconds":result["elapsed_seconds"],"seed_translation":seed_proof["translation"]}))
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--candidate",type=Path,required=True);p.add_argument("--base-python",type=Path,required=True);p.add_argument("--temporary-parent",type=Path,required=True);a=p.parse_args()
    run(a.candidate,a.base_python,a.temporary_parent)
