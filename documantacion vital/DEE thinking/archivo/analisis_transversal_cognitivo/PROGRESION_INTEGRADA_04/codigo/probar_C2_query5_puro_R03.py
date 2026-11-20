"""R03 payload/AST checks with a fake interface only; never DEE execution."""
from pathlib import Path
from types import SimpleNamespace
import ast,hashlib,importlib.util,json,sys

if __name__=="__main__":
    home=Path(__file__).resolve().parent;before=set(sys.modules)
    source=home/"pi04_coordinacion_adquirida_R03.py"
    spec=importlib.util.spec_from_file_location("C2_R03_PURE",source)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    calls=[]
    def submit(name,payload,tick):
        calls.append([name,payload,tick]);return SimpleNamespace(id=100+len(calls))
    requests=m._submit_query(SimpleNamespace(submit=submit),12345,prefix="PI03.TC.R01")
    assert calls==[["PI03.TC.R01.query",5,12345],["PI03.TC.R01.support.plus",0,12345],["PI03.TC.R01.support.minus",0,12345]]
    assert [r["payload"]for r in requests]==[5,0,0]
    assert all(set(r)=={"id","channel","payload","requested_tick"}for r in requests)
    def defs(file):
        tree=ast.parse(file.read_text(encoding="utf8"))
        return {x.name:ast.dump(x,include_attributes=False)for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef))}
    old=defs(home/"pi04_coordinacion_adquirida_R02.py");new=defs(source)
    changed=sorted(k for k in old if old[k]!=new.get(k))
    assert changed==["_opportunity_body","calibrate","prepare"]
    assert sorted(set(new)-set(old))==["_submit_query"]
    for name in("_validate_context_cut","cut_context","protocol","validate_literal","validate",
                "_motor","_operation","Device","operational_dependencies","dispatch"):
        assert old[name]==new[name]
    sensor=home/"pi04_selector_contextual_C2_R01.py"
    assert hashlib.sha256(sensor.read_bytes()).hexdigest()=="0634e034e556b15f97babfc1b38c85cb8e92219d306af4c58794ea94be38394f"
    dee=[x for x in set(sys.modules)-before if x=="dee_thinking"or x.startswith("dee_thinking.")]
    assert not dee
    value={"schema":"PI04.C2.query5.pure_check.R03","status":"STATIC_ONLY_NOT_NATIVE",
        "Native_ticks":0,"official_DEE_imports":dee,"fake_interface_calls":calls,"normalized_requests":requests,
        "changed_existing_functions":changed,"new_function":["_submit_query"],
        "Device_and_guards_unchanged_AST":True,"sensor_reader_same_source":True,
        "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "protocol_modified_by_this_test":False,"unverified":["Native sensitivity to query5","functional threshold","learning"]}
    output=home.parent/"control/C2_QUERY5_PURE_R03.json"
    if output.exists():raise ValueError("Preserve prior proof")
    output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(value,ensure_ascii=False,indent=2))
