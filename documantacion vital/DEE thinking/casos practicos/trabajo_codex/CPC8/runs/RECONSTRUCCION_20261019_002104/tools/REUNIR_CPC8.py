"""Verify two sequential binary parts and reconstruct CPC8 without overwrite."""
from __future__ import annotations
import argparse,hashlib,json,os
from pathlib import Path
import tempfile

BLOCK=1024*1024
def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda:stream.read(BLOCK),b""):h.update(chunk)
    return h.hexdigest()
def safe_name(value):
    if not isinstance(value,str) or Path(value).name!=value or value in ("",".","..") or "/" in value or "\\" in value:
        raise ValueError("Unsafe transport filename")
    return value
def no_replace(source,target):
    """Atomic create-by-link: a concurrent existing target cannot be replaced."""
    os.link(source,target)
    Path(source).unlink()
def reconstruct(manifest,output=None):
    manifest=Path(manifest).resolve();data=json.loads(manifest.read_text(encoding="utf-8"))
    if data.get("schema")!=1 or len(data.get("parts",[]))!=2:raise ValueError("Exactly two binary parts required")
    original=safe_name(data["zip"]["name"])
    output=Path(output).resolve() if output is not None else manifest.parent/original
    if output.exists():raise FileExistsError("Existing output is protected: "+str(output))
    if not output.parent.is_dir():raise FileNotFoundError(output.parent)
    ordered=sorted(data["parts"],key=lambda p:p["order"])
    if [p["order"] for p in ordered]!=[1,2]:raise ValueError("Invalid part order")
    for item in ordered:
        path=manifest.parent/safe_name(item["name"])
        if not path.is_file() or path.stat().st_size!=item["bytes"] or digest(path)!=item["sha256"]:
            raise ValueError("Part missing, wrong-sized or corrupt: "+str(path))
    handle,tmp=tempfile.mkstemp(prefix=".cpc8_reunir_",suffix=".pending",dir=output.parent);os.close(handle)
    temporary=Path(tmp);combined=hashlib.sha256();size=0
    try:
        with temporary.open("wb") as out:
            for item in ordered:
                with (manifest.parent/item["name"]).open("rb") as stream:
                    for chunk in iter(lambda:stream.read(BLOCK),b""):
                        out.write(chunk);combined.update(chunk);size+=len(chunk)
            out.flush();os.fsync(out.fileno())
        if size!=data["zip"]["bytes"] or combined.hexdigest()!=data["zip"]["sha256"]:
            raise ValueError("Reconstructed size/SHA-256 mismatch")
        no_replace(temporary,output)
        return {"status":"RECONSTRUCTION_HASH_VERIFIED","output":str(output),"bytes":size,"sha256":combined.hexdigest()}
    finally:
        if temporary.exists():temporary.unlink()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--manifest",type=Path,default=Path(__file__).with_name("PARTES.json"))
    p.add_argument("--output",type=Path);a=p.parse_args();print(json.dumps(reconstruct(a.manifest,a.output),ensure_ascii=False))
if __name__=="__main__":main()
