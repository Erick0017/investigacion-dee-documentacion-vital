"""CPC8 exact-container delivery tools. Never builds/publishes on import.

API: build (explicit frozen-tree acknowledgement), verify, extract, transport,
publish (explicit authorization plus clean functional report of THIS hash).
Every pre-existing artifact is protected unless an explicitly named, hashed
predecessor is preserved and root authorizes replacing that exact cut.
Source trees are read-only. No packaging operation runs on import.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,io,json,os,shutil,sys,tempfile,uuid,zipfile
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
NAME="CPC8_ORGANIZACION_COGNITIVA_NATIVA_APRENDIZAJE65_RESULTADOS.zip"
WHEEL="dee_thinking-4.5.0-cp313-cp313-win_amd64.whl"
WHEEL_SHA="09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c"
PYD_SHA="17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d"
BLOCK=1024*1024
THRESHOLD=20*1024**2
GENERATED={"MANIFEST.json","HASHES.sha256"}
EXCLUDED_DIRS={".git",".venv","venv","__pycache__",".pytest_cache",".mypy_cache",".cache",
    "staging","_staging","entrega","entrega_candidata","delivery","dist","build","clean_extract","_clean_extract"}

def now():return datetime.now(timezone.utc).isoformat()
def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(BLOCK),b""):h.update(b)
    return h.hexdigest()
def json_bytes(data):return (json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+"\n").encode("utf-8")
def write_new(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("xb") as stream:stream.write(json_bytes(data));stream.flush();os.fsync(stream.fileno())
def beneath(path,root):
    try:Path(path).resolve().relative_to(Path(root).resolve());return True
    except ValueError:return False
def source_files(root):
    selected=[];excluded=[]
    for current,dirs,files in os.walk(root,followlinks=False):
        current=Path(current)
        kept=[]
        for name in dirs:
            path=current/name
            reason=None
            if name.casefold() in EXCLUDED_DIRS or name.casefold().startswith(("_clean_",".cpc8_")):reason="generated/cache/build directory"
            elif path.is_symlink() or (hasattr(path,"is_junction") and path.is_junction()):reason="link/junction outside isolated source policy"
            elif (path/"pyvenv.cfg").exists():reason="virtual environment"
            if reason:excluded.append({"path":path.relative_to(root).as_posix(),"reason":reason})
            else:kept.append(name)
        dirs[:]=kept
        for name in sorted(files):
            path=current/name;rel=path.relative_to(root).as_posix();lower=name.casefold()
            reason=None
            if path.is_symlink() or not beneath(path,root):reason="linked file"
            elif current==root and name in GENERATED:reason="root manifest generated for exact package; workspace version recorded separately"
            elif lower.endswith((".zip",".zip.001",".zip.002",".7z",".pyc",".pyo")):reason="historical/container/cache excluded"
            elif ".pending" in lower or lower.endswith((".tmp",".temp")):reason="temporary incomplete file"
            if reason:
                entry={"path":rel,"reason":reason}
                if current==root and name in GENERATED:entry.update({"bytes":path.stat().st_size,"sha256":digest(path)})
                excluded.append(entry)
            else:selected.append((rel,path))
    selected.sort(key=lambda item:item[0])
    casefold=[r.casefold() for r,_ in selected]
    if len(set(casefold))!=len(casefold):raise ValueError("Case-colliding package paths")
    return selected,excluded
def category(name):
    first=name.split("/",1)[0]
    return first if "/" in name else "ROOT_TECHNICAL"
def zip_write_file(archive,name,path):
    before=path.stat();h=hashlib.sha256();size=0
    info=zipfile.ZipInfo(name,date_time=(2026,10,18,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
    if hasattr(info,"compress_level"):info.compress_level=9
    else:info._compresslevel=9
    info.external_attr=0o100644<<16
    with archive.open(info,"w",force_zip64=True) as out,path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(BLOCK),b""):
            out.write(chunk);h.update(chunk);size+=len(chunk)
    after=path.stat()
    if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns) or size!=before.st_size:
        raise RuntimeError("Source changed while packaging: "+str(path))
    if digest(path)!=h.hexdigest():raise RuntimeError("Source bytes changed after packaging: "+str(path))
    return {"path":name.removeprefix("CPC8/"),"bytes":size,"sha256":h.hexdigest(),"category":category(name.removeprefix("CPC8/"))}
def protect_new(path):
    path=Path(path).resolve()
    if path.exists():raise FileExistsError("Existing artifact protected: "+str(path))
    path.parent.mkdir(parents=True,exist_ok=True)
    return path
def atomic_create(source,target):
    """Create final name atomically by hard-link, never overwrite a race winner."""
    os.link(source,target)

def confirm_owned_job_closure(root):
    """Read only own supervisor records; never kill/check unrelated PID names.

    START's RUNNING is a historical event, superseded by completed COMMAND.
    A worker's explicit wait plus kill-on-close Job Object closure establishes
    cleanup. No mere source-file/ZIP integrity is treated as process closure.
    """
    directory=root/"jobs";count=0
    if not directory.is_dir():return {"records":0,"scope":"No own jobs directory in fixture/source"}
    for folder in directory.iterdir():
        if not folder.is_dir():continue
        path=folder/"COMMAND.json"
        if not path.is_file():raise RuntimeError("Own job has no final COMMAND: "+folder.name)
        data=json.loads(path.read_text(encoding="utf-8"));count+=1
        if data.get("status") in ("RUNNING","STARTING"):raise RuntimeError("Own job still marked active: "+folder.name)
        if data.get("pid") is not None and not (data.get("owned_worker_waited") and data.get("owned_job_closed") and data.get("kill_on_job_close")):
            raise RuntimeError("Own process/job closure not confirmed: "+folder.name)
    return {"records":count,"scope":"Own supervised workers waited and kill-on-close jobs closed; failed prelaunch records withoutPID do not claim a process"}

def build(root,candidate,acknowledge=False):
    if not acknowledge:raise PermissionError("Explicit --ack-science-frozen required; never snapshot active workers")
    root=Path(root).resolve();candidate=protect_new(candidate)
    if beneath(candidate,root):raise ValueError("Candidate must be outside source tree")
    closure=confirm_owned_job_closure(root)
    selected,excluded=source_files(root)
    wheels=[(r,p) for r,p in selected if p.suffix.casefold()==".whl"]
    if len(wheels)!=1 or Path(wheels[0][0]).name!=WHEEL or digest(wheels[0][1])!=WHEEL_SHA:
        raise ValueError("Exactly one official4.5 wheel required, with exact SHA-256")
    # Reconstruction has no B1/B2 operative comparators. Their prior results
    # remain historical references, not a mandatory implementation dependency.
    required=("src/","resultados/","genealogia/","base_validada/","runtime/","app/","configuraciones/","revision/","checkpoints/","tools/")
    missing=[prefix for prefix in required if not any(r.startswith(prefix) for r,_ in selected)]
    if missing:raise ValueError("Missing required evidence trees: "+repr(missing))
    temp=candidate.with_name(candidate.name+".pending")
    if temp.exists():raise FileExistsError(temp)
    members=[];categories={}
    try:
        with zipfile.ZipFile(temp,"x",compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True) as z:
            for rel,path in selected:
                row=zip_write_file(z,"CPC8/"+rel,path);members.append(row)
                cat=categories.setdefault(row["category"],{"files":0,"expanded_bytes":0});cat["files"]+=1;cat["expanded_bytes"]+=row["bytes"]
            manifest={"schema":1,"campaign":"CPC8","package_root":"CPC8/","built_utc":now(),
                "scope":"Primary evidence and executable tools;65in artifact name does not certify65semantic meanings",
                "source_tree_declared_frozen":True,"owned_job_closure":closure,"manifest_policy":"Lists payload only; excludes self and HASHES to avoid circular identity. HASHES covers MANIFEST and payload, excluding only itself.",
                "files":members,"payload_files":len(members),"total_members":len(members)+2,
                "payload_expanded_bytes":sum(r["bytes"] for r in members),"categories":categories,
                "excluded":excluded,"engine":{"wheel":wheels[0][0],"wheel_sha256":WHEEL_SHA,"pyd_sha256":PYD_SHA}}
            encoded=json_bytes(manifest);z.writestr("CPC8/MANIFEST.json",encoded)
            lines=[r["sha256"]+"  "+r["path"] for r in members]
            lines.append(hashlib.sha256(encoded).hexdigest()+"  MANIFEST.json")
            z.writestr("CPC8/HASHES.sha256","\n".join(sorted(lines))+"\n")
        check=verify(temp)
        atomic_create(temp,candidate);temp.unlink()
        report={"status":"CANDIDATE_INTEGRITY_VERIFIED_NOT_YET_FUNCTIONALLY_APPROVED","built_utc":now(),
                "artifact":str(candidate),"artifact_sha256":digest(candidate),"integrity":check,
                "categories":check["categories"],"publication_authorized":False}
        write_new(candidate.with_name(candidate.name+".BUILD.json"),report)
        return report
    except BaseException:
        # Preserve an incomplete/failed candidate as an attempt, never delete an older valid ZIP.
        raise

def valid_names(z):
    names=z.namelist()
    if len(names)!=len(set(names)) or len(names)!=len(set(n.casefold() for n in names)):raise ValueError("Duplicate/case-colliding ZIP members")
    for n in names:
        p=PurePosixPath(n)
        if not n.startswith("CPC8/") or p.is_absolute() or ".." in p.parts or "\\" in n or ":" in n or n.endswith("/"):
            raise ValueError("Unsafe or unexpected ZIP member: "+n)
    return names
def verify(path):
    path=Path(path).resolve();categories={}
    with zipfile.ZipFile(path,"r") as z:
        names=valid_names(z)
        bad=z.testzip()
        if bad is not None:raise ValueError("CRC failed: "+bad)
        manifest=json.loads(z.read("CPC8/MANIFEST.json"));files=manifest["files"]
        expected={"CPC8/"+r["path"] for r in files}|{"CPC8/MANIFEST.json","CPC8/HASHES.sha256"}
        if set(names)!=expected or len(names)!=manifest["total_members"]:raise ValueError("Manifest inventory differs")
        hashes={}
        for line in z.read("CPC8/HASHES.sha256").decode("utf-8").splitlines():
            hexdigest,name=line.split("  ",1)
            if name in hashes or len(hexdigest)!=64:raise ValueError("Invalid HASHES entry")
            hashes[name]=hexdigest
        if set(hashes)!={n.removeprefix("CPC8/") for n in names if n!="CPC8/HASHES.sha256"}:raise ValueError("HASHES scope differs")
        rows={r["path"]:r for r in files}
        for name in names:
            if name=="CPC8/HASHES.sha256":continue
            h=hashlib.sha256();size=0
            with z.open(name) as stream:
                for chunk in iter(lambda:stream.read(BLOCK),b""):h.update(chunk);size+=len(chunk)
            rel=name.removeprefix("CPC8/")
            if h.hexdigest()!=hashes[rel]:raise ValueError("SHA-256 mismatch: "+name)
            if rel in rows and (rows[rel]["bytes"]!=size or rows[rel]["sha256"]!=h.hexdigest()):raise ValueError("Manifest hash/size mismatch: "+name)
            cat=categories.setdefault(category(rel),{"files":0,"expanded_bytes":0,"compressed_bytes":0})
            info=z.getinfo(name);cat["files"]+=1;cat["expanded_bytes"]+=size;cat["compressed_bytes"]+=info.compress_size
        wheels=[n for n in names if n.endswith(".whl")]
        if len(wheels)!=1 or Path(wheels[0]).name!=WHEEL or hashes[wheels[0].removeprefix("CPC8/")]!=WHEEL_SHA:raise ValueError("Wrong/duplicate wheel")
        with zipfile.ZipFile(io.BytesIO(z.read(wheels[0]))) as wheel:
            pyds=[n for n in wheel.namelist() if n.endswith(".pyd")]
            if len(pyds)!=1 or hashlib.sha256(wheel.read(pyds[0])).hexdigest()!=PYD_SHA:raise ValueError("Wrong native PYD")
            if wheel.testzip() is not None:raise ValueError("WHL CRC failed")
        hash_info=z.getinfo("CPC8/HASHES.sha256")
        cat=categories.setdefault("ROOT_TECHNICAL",{"files":0,"expanded_bytes":0,"compressed_bytes":0})
        cat["files"]+=1;cat["expanded_bytes"]+=hash_info.file_size;cat["compressed_bytes"]+=hash_info.compress_size
        expanded=sum(z.getinfo(n).file_size for n in names)
    return {"status":"INTEGRITY_PASS_NOT_FUNCTIONAL_VERDICT","zip":str(path),"sha256":digest(path),
      "compressed_bytes":path.stat().st_size,"expanded_bytes":expanded,"members":len(names),
      "crc":"PASS","hashes":"PASS","inventory":"PASS","wheel":"OFFICIAL4.5_MATCH","pyd":"OFFICIAL4.5_MATCH",
      "manifest_sha256":hashes["MANIFEST.json"],"categories":categories}

def extract(path,destination):
    integrity=verify(path);destination=protect_new(destination);destination.mkdir()
    with zipfile.ZipFile(path) as z:
        for name in valid_names(z):
            target=destination/Path(*PurePosixPath(name).parts)
            target.parent.mkdir(parents=True,exist_ok=True)
            with z.open(name) as source,target.open("xb") as out:shutil.copyfileobj(source,out,BLOCK)
    return {"status":"EXTRACTED_EXACT_VERIFIED_CONTAINER","destination":str(destination),"root":str(destination/"CPC8"),"integrity":integrity}

def transport(path,output):
    path=Path(path).resolve();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    check=verify(path)
    if path.stat().st_size<=THRESHOLD:return {"status":"NO_SPLIT_NEEDED","compressed_bytes":path.stat().st_size,"threshold_bytes":THRESHOLD}
    final_names=[path.name+".001",path.name+".002","PARTES.json","REUNIR_CPC8.py","INSTRUCCIONES_PARTES.txt","TRANSPORTE_VERIFICADO.json"]
    for name in final_names:protect_new(output/name)
    halves=[(path.stat().st_size+1)//2,path.stat().st_size//2];parts=[]
    with path.open("rb") as source:
        for order,size in enumerate(halves,1):
            target=output/(path.name+f".{order:03d}");h=hashlib.sha256();remaining=size
            with target.open("xb") as out:
                while remaining:
                    chunk=source.read(min(BLOCK,remaining))
                    if not chunk:raise EOFError("Unexpected end of canonical ZIP")
                    out.write(chunk);h.update(chunk);remaining-=len(chunk)
                out.flush();os.fsync(out.fileno())
            parts.append({"order":order,"name":target.name,"bytes":size,"sha256":h.hexdigest()})
        if source.read(1):raise ValueError("ZIP grew during split")
    data={"schema":1,"kind":"Two sequential binary segments, not independent ZIP archives","created_utc":now(),
        "zip":{"name":path.name,"bytes":path.stat().st_size,"sha256":check["sha256"]},"parts":parts}
    write_new(output/"PARTES.json",data)
    with zipfile.ZipFile(path) as package,(output/"REUNIR_CPC8.py").open("xb") as out:
        out.write(package.read("CPC8/tools/REUNIR_CPC8.py"))
    text=("CPC8: conserve las dos partes en la misma carpeta con PARTES.json y REUNIR_CPC8.py.\n"
          "No son dos ZIP independientes. .001 seguida de .002 recupera exactamente el ZIP.\n"
          "Con Python3: python REUNIR_CPC8.py --output CPC8_REUNIDO.zip\n"
          "El programa verifica cada parte y el resultado, y rechaza sobrescribir archivos.\n"
          "El ZIP canónico permanece disponible. La división no garantiza compatibilidad de descarga.\n")
    with (output/"INSTRUCCIONES_PARTES.txt").open("x",encoding="utf-8") as f:f.write(text)
    concatenated=hashlib.sha256()
    for item in parts:
        with (output/item["name"]).open("rb") as stream:
            for b in iter(lambda:stream.read(BLOCK),b""):concatenated.update(b)
    if concatenated.hexdigest()!=check["sha256"]:raise ValueError("Streaming concatenation does not match")
    # Actually reconstruct once, verify full hash and container, then remove only this owned temporary.
    spec=importlib.util.spec_from_file_location("cpc8_verified_transport_reassembly",output/"REUNIR_CPC8.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix="_cpc8_transport_",dir=output.parent) as tmp:
        rebuilt=Path(tmp)/path.name
        reconstruction=module.reconstruct(output/"PARTES.json",rebuilt)
        rebuilt_check=verify(rebuilt)
        compared=0
        with path.open('rb') as original,rebuilt.open('rb') as restored:
            while True:
                left=original.read(BLOCK);right=restored.read(BLOCK)
                if left!=right:raise ValueError('Actual rebuilt bytes differ from canonical ZIP')
                if not left:break
                compared+=len(left)
    proof={"status":"TWO_PARTS_AND_RECONSTRUCTION_VERIFIED","zip":data["zip"],"parts":parts,
        "streaming_sha256":concatenated.hexdigest(),"actual_reconstruction":reconstruction,
        "reconstructed_integrity":rebuilt_check,"actual_byte_comparison_equal":True,"actual_bytes_compared":compared,"temporary_reconstruction_removed":True}
    write_new(output/"TRANSPORTE_VERIFICADO.json",proof)
    return proof

def publication_preflight(canonical,expected_previous=None,prior_backup=None,prior_proofs=None):
    """Fail before mutation if another cut appeared or history is not protected.

    The exclusive publication lock serializes this publisher. Hash and file
    identity are rechecked immediately before atomic replace. This is not a
    claim of filesystem-wide compare-and-swap against arbitrary noncooperating
    software; any observed conflict aborts instead of choosing a newer cut.
    """
    canonical=Path(canonical).resolve()
    previous=None
    if canonical.exists():
        if not expected_previous or not prior_backup or not prior_proofs:
            raise FileExistsError("Existing canonical requires explicit expected hash, protected backup and archived proofs")
        actual=digest(canonical)
        if actual!=expected_previous:raise RuntimeError("Concurrent/different canonical cut detected; preserved without replacement")
        backup=Path(prior_backup).resolve()
        if backup==canonical or not backup.is_file() or digest(backup)!=expected_previous:
            raise ValueError("Prior byte-exact backup missing or different")
        with zipfile.ZipFile(backup) as z:
            if z.testzip() is not None:raise ValueError("Prior protected backup CRC failed")
        st=canonical.stat()
        previous={"sha256":actual,"bytes":st.st_size,"backup":str(backup),
                  "identity":(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns)}
    elif expected_previous:
        raise RuntimeError("Expected predecessor disappeared; do not publish over an unrecognized state")
    proofs=Path(prior_proofs).resolve() if prior_proofs else None
    for name in ("VERIFICACION_FINAL_EXTERNA.json","LEER_PRIMERO.md","LECTURA_PROVISIONAL.md",
                 "HASH_ZIP_FINAL.sha256","CIERRE_CPC8.json","TRANSPORTE_NO_REQUERIDO.json"):
        old=canonical.parent/name
        if old.exists() and (proofs is None or not (proofs/name).is_file() or digest(old)!=digest(proofs/name)):
            raise RuntimeError("Existing external proof not byte-preserved in declared historical archive: "+name)
    return previous

def replace_small(data,target,prior_proofs):
    target=Path(target)
    if target.exists():
        archived=Path(prior_proofs)/target.name if prior_proofs else None
        if archived is None or not archived.is_file() or digest(target)!=digest(archived):
            raise RuntimeError("External proof changed during publication: "+target.name)
    pending=target.with_name(".cpc8_"+uuid.uuid4().hex+".pending")
    with pending.open("xb") as out:out.write(data);out.flush();os.fsync(out.fileno())
    os.replace(pending,target)

def publish(candidate,canonical,clean_report,authorize=False,expected_previous=None,prior_backup=None,prior_proofs=None):
    if not authorize:raise PermissionError("Explicit --authorize required only after root review")
    candidate=Path(candidate).resolve();canonical=Path(canonical).resolve();clean_report=Path(clean_report).resolve()
    checked=verify(candidate);clean=json.loads(clean_report.read_text(encoding="utf-8"))
    if clean.get("status")!="PASS" or clean.get("artifact_sha256")!=checked["sha256"]:
        raise ValueError("Clean functional report must PASS and identify THIS exact artifact_sha256")
    if canonical.name!=NAME:raise ValueError("Canonical filename differs from CPC8 contract")
    canonical.parent.mkdir(parents=True,exist_ok=True)
    lock=canonical.parent/".cpc8_publication.lock"
    # A stale lock is a diagnosable state, never automatically deleted.
    with lock.open("xb") as lease:
        lease.write(json_bytes({"pid":os.getpid(),"candidate_sha256":checked["sha256"],"utc":now()}));lease.flush();os.fsync(lease.fileno())
        try:
            previous=publication_preflight(canonical,expected_previous,prior_backup,prior_proofs)
            documents=[]
            with zipfile.ZipFile(candidate) as package:
                for name in ("LEER_PRIMERO.md","LECTURA_PROVISIONAL.md"):
                    documents.append((package.read("CPC8/revision/"+name),canonical.parent/name))
            if previous:
                pending=canonical.with_name(".cpc8_"+uuid.uuid4().hex+".pending")
                # Link the closed candidate into the destination filesystem,
                # then replace in one filesystem operation; no partial ZIP.
                os.link(candidate,pending)
                st=canonical.stat()
                identity=(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns)
                if identity!=previous["identity"] or digest(canonical)!=expected_previous:
                    raise RuntimeError("Canonical changed after preflight; replacement aborted")
                os.replace(pending,canonical)
            else:atomic_create(candidate,canonical)
            final=verify(canonical)
            if final["sha256"]!=checked["sha256"]:raise ValueError("Published bytes differ")
            report={"status":"PUBLISHED_EXACT_CONTAINER_AFTER_EXTERNAL_FUNCTIONAL_PASS","published_utc":now(),
                "zip":str(canonical),"artifact_sha256":final["sha256"],"compressed_bytes":final["compressed_bytes"],
                "expanded_bytes":final["expanded_bytes"],"integrity":final,
                "clean_report":str(clean_report),"clean_report_sha256":digest(clean_report),
                "clean_validation":clean,"prior_cut":previous,
                "existing_artifacts_overwritten":bool(previous),"prior_cut_preserved_byte_exact":bool(previous),
                "publication_method":"Exclusive cooperating-publisher lock; expected predecessor hash and identity checked; atomic replacement of closed verified bytes" if previous else "Atomic hard-link creation; existing name protected"}
            replace_small(json_bytes(report),canonical.parent/"VERIFICACION_FINAL_EXTERNA.json",prior_proofs)
            for data,target in documents:replace_small(data,target,prior_proofs)
            replace_small((final["sha256"]+"  "+canonical.name+"\n").encode("utf-8"),canonical.parent/"HASH_ZIP_FINAL.sha256",prior_proofs)
            return report
        finally:
            # Only this publisher's newly created lease is removed.
            lease.close()
            lock.unlink()

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest="command",required=True)
    b=sub.add_parser("build");b.add_argument("--root",type=Path,default=ROOT);b.add_argument("--candidate",type=Path,required=True);b.add_argument("--ack-science-frozen",action="store_true")
    v=sub.add_parser("verify");v.add_argument("--zip",type=Path,required=True);v.add_argument("--report",type=Path)
    e=sub.add_parser("extract");e.add_argument("--zip",type=Path,required=True);e.add_argument("--destination",type=Path,required=True);e.add_argument("--report",type=Path)
    t=sub.add_parser("transport");t.add_argument("--zip",type=Path,required=True);t.add_argument("--output",type=Path,required=True)
    s=sub.add_parser("publish");s.add_argument("--candidate",type=Path,required=True);s.add_argument("--canonical",type=Path,required=True);s.add_argument("--clean-report",type=Path,required=True);s.add_argument("--authorize",action="store_true");s.add_argument("--expected-previous-sha256");s.add_argument("--prior-backup",type=Path);s.add_argument("--prior-proofs",type=Path)
    a=p.parse_args()
    if a.command=="build":result=build(a.root,a.candidate,a.ack_science_frozen)
    elif a.command=="verify":result=verify(a.zip)
    elif a.command=="extract":result=extract(a.zip,a.destination)
    elif a.command=="transport":result=transport(a.zip,a.output)
    else:result=publish(a.candidate,a.canonical,a.clean_report,a.authorize,a.expected_previous_sha256,a.prior_backup,a.prior_proofs)
    if getattr(a,"report",None):write_new(a.report,result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
