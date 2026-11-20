"""Explicit fake-API tests of C2B preparation/data and old-failure guards."""
from pathlib import Path
from types import SimpleNamespace,ModuleType
import ast,copy,hashlib,importlib.util,json,sys

def load(p,name):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

if __name__=="__main__":
    home=Path(__file__).resolve().parent;modules_before=set(sys.modules)
    sensor=load(home/"pi04_sensor_simetrico_C2B_R01.py","C2B_SENSOR_PURE")
    control=load(home/"pi04_coordinacion_simetrica_C2B.py","C2B_COORD_PURE")
    p,ph=control.protocol()
    assert p["status"]=="DRAFT"and p["calibration_values"]==[0,4,6]and len(p["schedule"])==24
    assert all(x.startswith("eci01-pi04-c2b-")for x in control.MODES)
    for v in(0,4,6):control.validate_literal({"modo":control.CALIBRATE,"valor":v})
    refusals=[]
    for v in(1,3,True,44):
        try:control.validate_literal({"modo":control.CALIBRATE,"valor":v})
        except ValueError:refusals.append("Bcal_refuse_"+str(v))
        else:raise AssertionError("Unexpected B calibration value")
    try:control.protocol(material=True)
    except ValueError:refusals.append("DRAFT_not_executable")
    else:raise AssertionError("B DRAFT executed")
    assert control.KEY!="DEE.Cognitive.PI04.C2.coordination.R01"and control.FOLDER!="PI04_C2_COORDINACION_R01"

    oldkey="DEE.Cognitive.PI04.C2.coordination.R01"
    original={"admitted":True,"arm":"real","ordinal":11,"pending":None,"uncertain":False,
        "halted_reason":"First NULL/invalid actual numeric response preserved after actual failure and generic return; no retry",
        "rows":[{"first_choice":1,"after_tick":790000+i}for i in range(10)]+[{"first_choice":None,"after_tick":798033}]}
    before=json.dumps(original,sort_keys=True)
    oldmodule=SimpleNamespace(KEY=oldkey,FOLDER="PI04_C2_COORDINACION_R01",_get=lambda a:original,
        operational_dependencies=lambda *a:{"pending":None,"uncertain":False,"device_pending":None,
                                            "device_feedback_pending":None,"device_uncertain":False})
    control._module=lambda name:oldmodule if name=="pi04_coordinacion_adquirida"else (_ for _ in()).throw(ValueError(name))
    proof=control._require_original_NULL(None,Path("SYNTHETIC_ONLY"))
    assert proof["old_ordinal"]==11 and proof["old_last_tick"]==798033 and json.dumps(original,sort_keys=True)==before
    for label,patch in(("old_not_real",{"arm":"none"}),("old_ordinal10",{"ordinal":10}),
                       ("old_uncertain",{"uncertain":True}),("old_pending",{"pending":{"x":1}}),
                       ("old_no_NULL_halt",{"halted_reason":None})):
        changed=copy.deepcopy(original);changed.update(patch);oldmodule._get=lambda a,x=changed:x
        try:control._require_original_NULL(None)
        except ValueError:refusals.append(label)
        else:raise AssertionError(label)
    oldmodule._get=lambda a:original
    class World:
        def __init__(self):
            self.calls=[];self.interfaces=[];self.meta={"OLD_SENSOR":json.dumps({"version":"OLD_VERSION"}),oldkey:before}
            self.runtime=SimpleNamespace(dimension=67,channel_names=["PI04.C2.CURRENT.R01.datum"],
                observe=lambda coord:{"raw":"0","site":list(coord)},
                set_snapshot_metadata=lambda k,v:self.meta.__setitem__(k,v))
        def declare_interface(self,i):self.interfaces.append(i);self.runtime.channel_names.append(i.name)
        def submit(self,name,value,tick):self.calls.append([name,value,tick]);return SimpleNamespace(id=len(self.calls))
    world=World();owner=SimpleNamespace(world=world,tick=798033)
    owner.run_until=lambda *a:(_ for _ in()).throw(AssertionError("B.prepare advanced fake Native time"))
    d=SimpleNamespace(Coordinate=lambda *v:tuple(v),Direction=lambda *v:tuple(v),
                      ChannelSpec=lambda:SimpleNamespace(),InterfaceSpec=lambda:SimpleNamespace())
    fakeold=SimpleNamespace(KEY="OLD_SENSOR",VERSION="OLD_VERSION")
    def guard(a):return d,lambda v:copy.deepcopy(v),None,json.loads,json.dumps,a.world.meta,"ECI02_PI03_REPRO_PI04_C2BCAL_01"
    fakeold._guard=guard
    def submit_old(a,value,q):
        r=a.world.submit("PI04.C2.CURRENT.R01.datum",value,q+3)
        return {"id":r.id,"channel":"PI04.C2.CURRENT.R01.datum","payload":value,"requested_tick":q+3}
    fakeold.submit_datum=submit_old
    fixed_read={"choice":0,"MOCK":True,"reader":"EXACT_OLD_PREDICATE"}
    fakeold.read_fixed=lambda a,q:fixed_read
    sensor._OLD=fakeold
    app=ModuleType("app");app.__path__=[]
    tools=ModuleType("app.native_tools");tools.physical=lambda w:{"N":67,"tick":owner.tick,"RAW_sha256":"SYNTHETIC_RAW","clocks_sha256":"SYNTHETIC_CLOCKS"}
    prior={k:sys.modules.get(k)for k in("app","app.native_tools")}
    sys.modules.update({"app":app,"app.native_tools":tools})
    try:preparation=sensor.prepare(owner)
    finally:
        for k,v in prior.items():
            if v is None:sys.modules.pop(k,None)
            else:sys.modules[k]=v
    assert preparation["new_native_ticks"]==0 and preparation["physical_equal"]
    assert not world.calls and len(world.interfaces)==1
    channel=world.interfaces[0].channel
    assert tuple(channel.injection_site)==(18,54,4)and tuple(channel.direction)==(0,0,0)
    assert channel.state==1 and channel.semantic==1 and world.meta[oldkey]==before
    samples=[]
    for i,value in enumerate((0,4,6)):
        q=owner.tick+8+20*i;requests=sensor.submit_datum(owner,value,q)
        assert len(requests)==2 and [r["payload"]for r in requests]==[value,value]
        assert [r["requested_tick"]for r in requests]==[q+3,q+3]
        assert requests[0]["channel"]=="PI04.C2.CURRENT.R01.datum"and requests[1]["channel"]==sensor.EXTRA_CHANNEL
        samples.append({"value":value,"requests":requests})
    assert sensor.read_fixed(owner,owner.tick+1)is fixed_read
    try:sensor.prepare(owner)
    except ValueError:refusals.append("no_sensor_reinstall")
    else:raise AssertionError("B reinstalls over history")
    # This is a syntax/identity comparison; no existing Native body is run.
    def defs(file):return {n.name:ast.dump(n,include_attributes=False)for n in ast.parse(file.read_text(encoding="utf8")).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    olddefs=defs(home/"pi04_coordinacion_adquirida_R02_OP1.py");newdefs=defs(home/"pi04_coordinacion_simetrica_C2B.py")
    unchanged=[]
    for name in("_operation","_motor","Device","_helper","_hardware","_pure","uncertain","operational_dependencies"):
        assert olddefs[name]==newdefs[name];unchanged.append(name)
    assert "requests.extend(_sensor().submit_datum"in(home/"pi04_coordinacion_simetrica_C2B.py").read_text(encoding="utf8")
    dee=[x for x in set(sys.modules)-modules_before if x=="dee_thinking"or x.startswith("dee_thinking.")];assert not dee
    report={"schema":"PI04.C2B.pure_fake_API_check.R01","status":"PURE_ONLY_NO_NATIVE","Native_ticks":0,
        "official_DEE_imports":dee,"old_coherent_NULL_guard":proof,"refusals":refusals,
        "zero_tick_preparation_fake":preparation,"dual_same_scalar_samples_fake":samples,
        "original_C2_state_unchanged":world.meta[oldkey]==before,"single_extra_interface_no_birth":len(world.interfaces)==1,
        "fixed_reader_delegates_unchanged":True,"old_physical_function_AST_unchanged":unchanged,
        "code_sha256":hashlib.sha256((home/"pi04_coordinacion_simetrica_C2B.py").read_bytes()).hexdigest(),
        "sensor_sha256":hashlib.sha256((home/"pi04_sensor_simetrico_C2B_R01.py").read_bytes()).hexdigest(),
        "unverified":["Native symmetry/encounters","Native first and second decisions","learning and transfer","continuity/adoption"]}
    output=home.parent/"control/C2B_PURE_R01.json"
    if output.exists():raise ValueError("Preserve prior proof")
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"report":str(output),"status":report["status"],"Native_ticks":0,"official_DEE_imports":dee,
        "code_sha256":report["code_sha256"],"sensor_sha256":report["sensor_sha256"]},indent=2))
