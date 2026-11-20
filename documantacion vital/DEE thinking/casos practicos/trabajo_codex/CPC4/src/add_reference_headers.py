"""Copy selected immutable instrument source members, never import them."""
from pathlib import Path
import hashlib
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.common import put,sha


def main():
    product=ROOT.parents[2]/"4.0"/"DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip"
    expected="c78609a7d0d501324324408ed955f60f127965c77efbcbe3b3d04fc14dbb16cf"
    if sha(product)!=expected:raise ValueError("Instrument source container identity differs")
    dest=ROOT/"referencias"/"instrumento_minimo"
    records=[]
    with zipfile.ZipFile(product) as z:
        prefix="DEE_thinking_4_0_0/source/"
        selected=[n for n in z.namelist() if n.startswith(prefix+"include/dee_thinking/") and not n.endswith("/")]
        selected += [prefix+n for n in ("src/runtime.cpp","src/organizational.cpp","bindings/organizational_pybind.cpp","THIRD_PARTY_NOTICES.md")]
        for name in selected:
            data=z.read(name);rel=Path(name[len(prefix):]);path=dest/rel
            path.parent.mkdir(parents=True,exist_ok=True)
            if path.exists() and path.read_bytes()!=data:raise FileExistsError(path)
            path.write_bytes(data)
            records.append({"member":name,"local":path.relative_to(ROOT).as_posix(),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()})
    put(dest/"PROVENANCE.json",{"purpose":"Minimal passive instrument source and notices; actual execution uses the official included WHL, not a recompiled or alternative physics",
                                "container":str(product),"container_sha256":expected,"members":records})
    print("Selected immutable instrument members",len(records))


if __name__=="__main__":main()
