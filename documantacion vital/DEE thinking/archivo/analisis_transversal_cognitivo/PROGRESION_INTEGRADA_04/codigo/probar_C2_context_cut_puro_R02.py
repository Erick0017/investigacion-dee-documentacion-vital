"""R02 guard/omission/zero tests with synthetic APIs only; no DEE imports."""
from pathlib import Path
from types import SimpleNamespace,ModuleType
import copy,hashlib,importlib.util,json,sys

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    home=Path(__file__).resolve().parent;before=set(sys.modules)
    m=load(home/"pi04_coordinacion_adquirida_R02.py","C2_R02_PURE")
    p,_=m.protocol();p=copy.deepcopy(p)
    p["schedule"]=[{"stage":"development","context":4,"left":16,"right":9}for _ in range(12)]+[
        {"stage":"reserved","context":c,"left":15,"right":8}for c in (2,5,7,3,5,3,2,7)]+[
        {"stage":"retention","context":4,"left":17,"right":8}for _ in range(2)]
    identity={"life_id":m.PREFIX+"C2_CTX_CUT_01"}
    state={"version":m.VERSION,"arm":"real","admitted":True,"ready":True,"ordinal":12,
           "rows":[{"stage":"development"}for _ in range(12)],"pending":None,"uncertain":False,
           "halted_reason":None,"log_count":0,"log_chain_sha256":"00"*32}
    m._validate_context_cut(p,identity,state)
    refused=[]
    variants=[("wrong_identity",dict(identity,life_id=m.PREFIX+"C2_MAIN_01"),state),
              ("ordinal11",identity,dict(state,ordinal=11)),("ordinal13",identity,dict(state,ordinal=13)),
              ("not_real",identity,dict(state,arm="none")),("pending",identity,dict(state,pending={"x":1})),
              ("uncertain",identity,dict(state,uncertain=True)),("cut_repeated",identity,dict(state,context_cut_provenance={})),
              ("rows_missing",identity,dict(state,rows=state["rows"][:-1]))]
    for label,i,s in variants:
        try:m._validate_context_cut(p,i,s)
        except ValueError:refused.append(label)
        else:raise AssertionError(label)
    try:m.validate_literal({"modo":m.ADMIT,"brazo":"context_cut"})
    except ValueError:refused.append("admit_context_cut_at0")
    else:raise AssertionError("Context cut admitted from0")
    m.validate_literal({"modo":m.CUT_CONTEXT})
    try:m.validate_literal({"modo":m.CUT_CONTEXT,"value":0})
    except ValueError:refused.append("cut_with_datum_override")
    else:raise AssertionError("Cut accepts response override")

    out=home.parent/"control"/"C2_CONTEXT_CUT_PURE_R02"
    if out.exists():raise ValueError("Preserve prior pure fixture")
    out.mkdir()
    mutable=copy.deepcopy(state);events=[];snapshot={"N":67,"tick":9000,"RAW_sha256":"SYNTHETIC_RAW","clocks_sha256":"SYNTHETIC_CLOCKS"}
    m.validate=lambda *a:None
    m._get=lambda a:mutable;m._save=lambda *a:None
    m._identity=lambda a,d:(p,"SYNTHETIC_PROTOCOL",identity)
    m.operational_dependencies=lambda *a:{"device_pending":None,"device_feedback_pending":None,"device_uncertain":False}
    m._physical=lambda a:dict(snapshot)
    m._record=lambda a,s,d,event:events.append(copy.deepcopy(event))
    (out/m.FOLDER).mkdir()
    owner=SimpleNamespace(tick=9000)
    original_state=copy.deepcopy(mutable)
    proof=m.cut_context(owner,out)
    assert proof["physical_equal"]and proof["new_native_ticks"]==0 and owner.tick==9000
    assert mutable["arm"]=="context_cut" and mutable["rows"]==original_state["rows"]
    assert mutable["ordinal"]==12 and set(mutable)-set(original_state)=={"context_cut_provenance"}
    file=out/m.FOLDER/"CORTE_CONTEXTO.json"
    assert json.loads(file.read_text(encoding="utf8"))==proof
    try:m.cut_context(owner,out)
    except ValueError:refused.append("lesion_overwrite")
    else:raise AssertionError("Repeated cut allowed")

    # No-ACTIVO is executed via inherited identity guard with directory BEFORE
    # any mutation. Stub that guard to reject, and prove cut leaves m intact.
    m._get=lambda a:copy.deepcopy(state)
    def active_refusal(a,directory):
        assert directory is out
        raise ValueError("SYNTHETIC inherited no-ACTIVO refusal")
    m._identity=active_refusal
    try:m.cut_context(owner,out)
    except ValueError:refused.append("inherited_no_ACTIVO_before_mutation")
    else:raise AssertionError("Active guard ignored")

    # Execute the ACTUAL opportunity body with synthetic Native APIs. The
    # first response is literal0, distinct fromNULL; it must still call DIF.
    n=load(home/"pi04_coordinacion_adquirida_R02.py","C2_R02_OP_MOCK")
    pure=load(home/"E3"/"e3_retorno_desacoplado_R01.py","E3_R02_PURE")
    mp=copy.deepcopy(p);mp["status"]="SEALED_FOR_EVALUATION"
    mockhome=out/"mock_op";mockhome.mkdir();(mockhome/n.FOLDER).mkdir()
    device=n.Device.prepare(mockhome/n.FOLDER/"dispositivo",22,mp["environment"])
    # Mark12source resources as already consumed in this SYNTHETIC fixture.
    for r in device.m["resources"][:12]:(device.home/"reservoir"/r["name"]).replace(device.home/"consumed"/r["name"])
    device.m["ordinal"]=12;device.save()
    owner=SimpleNamespace(tick=0,world=SimpleNamespace())
    owner.run_until=lambda t:setattr(owner,"tick",t)if t>=owner.tick else (_ for _ in()).throw(ValueError("MOCK reverse"))
    st=copy.deepcopy(state);st["arm"]="context_cut";calls=[];events=[];counter=[0]
    def req(ch,t,**extra):counter[0]+=1;return {"id":counter[0],"channel":ch,"requested_tick":t,**extra}
    cal={"query_tick":115,"query_read_tick":121,"seed_tick":122,"outcome_injection_tick":389,
         "collision_tick":390,"contact_tick":391,"settled_after_tick":393,"delay_ticks":268,"delay_laps":4}
    helper=SimpleNamespace(schedule_trial=lambda *a:dict(cal),
        submit_query=lambda w,t,**kw:[req("query"+str(i),t)for i in range(3)],
        submit_motor_copy=lambda w,c,t,**kw:(calls.append(["COPY",c])or req("copy",t)),
        submit_generic_outcome=lambda w,f,t,**kw:(calls.append(["RETURN",f])or req("return",t)))
    def forbidden_datum(*a,**kw):raise AssertionError("context_cut emitted a context event or replacement0")
    sensor=SimpleNamespace(submit_datum=forbidden_datum,read_fixed=lambda a,q:{"choice":0,"MOCK":True})
    n.validate=lambda *a:None;n._identity=lambda *a:(mp,"SYNTHETIC_PROTOCOL",identity)
    n._get=lambda a:st;n._save=lambda *a:None;n._record=lambda a,s,d,event:events.append(n._jsonsafe(event))
    n._banks=lambda a:[{"clock":"0"},{"clock":"0"}];n._frame=lambda a,l:{"MOCK":True,"label":l,"tick":a.tick}
    n._helper=lambda:helper;n._sensor=lambda:sensor;n._pure=lambda:pure
    n._hardware=lambda:SimpleNamespace(_receipts=lambda a,rs:[dict(r,receipt={"id":r["id"],"status":"applied","MOCK":True})for r in rs])
    package=ModuleType("capacidades");package.__path__=[]
    ar=ModuleType("capacidades.aritmetica_directa_eci02");ar.MODE="MOCK"
    def arithmetic(a,row):calls.append(["ARITHMETIC",row["operacion"]]);a.run_until(a.tick+198);return {"numeric_result":7,"MOCK":True}
    ar.execute=arithmetic
    mu=ModuleType("capacidades.mente_unificada_01");mu.query_timing=lambda a,t:{"effective_query_tick":t}
    def current(a,v,detail=False):calls.append(["SECOND",v]);a.run_until(a.tick+16);return {"reader":{"choice":-1,"MOCK":True}}
    mu.current=current;package.aritmetica_directa_eci02=ar;package.mente_unificada_01=mu
    prior={k:sys.modules.get(k)for k in("capacidades","capacidades.aritmetica_directa_eci02","capacidades.mente_unificada_01")}
    sys.modules.update({"capacidades":package,"capacidades.aritmetica_directa_eci02":ar,"capacidades.mente_unificada_01":mu})
    try:result=n._opportunity_body(owner,mockhome)
    finally:
        for k,v in prior.items():
            if v is None:sys.modules.pop(k,None)
            else:sys.modules[k]=v
    assert result["context_input_supplied"]is False and len(result["requests"])==5
    assert result["first_reader"]["choice"]==0 and result["first_motor"]==-1
    assert result["selected_operation"]=="diferencia"and["ARITHMETIC","diferencia"]in calls
    assert ["SECOND",7]in calls and result["first_NULL_preserved"]is False
    assert result["useful_product"]is True and result["actual_failed"]is False
    assert ["RETURN",False]in calls
    dee=[x for x in set(sys.modules)-before if x=="dee_thinking"or x.startswith("dee_thinking.")]
    assert not dee
    report={"schema":"PI04.C2.context_cut.pure_mock.R02","status":"PURE_ONLY_NOT_NATIVE","Native_ticks":0,
        "official_DEE_imports":dee,"strict_guard_refusals":refused,"synthetic_lesion_proof":proof,
        "MOCK_zero_not_NULL":{"outer_requests":len(result["requests"]),"context_event_count":0,
            "reader_choice":0,"selected_operation":result["selected_operation"],"calls":calls,
            "actual_mock_result_used":result["actual_numeric_result"],"mock_product":result["actual_effect"]["product"]},
        "code_sha256":hashlib.sha256((home/"pi04_coordinacion_adquirida_R02.py").read_bytes()).hexdigest(),
        "unverified":["Native polarity","Native omission effect","real no-ACTIVO identity guard already existing; synthetic rejection only here","Native learning/control usefulness"]}
    target=out.parent/"C2_CONTEXT_CUT_PURE_R02.json"
    if target.exists():raise ValueError("No proof overwrite")
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"report":str(target),"status":report["status"],"Native_ticks":0,
                      "code_sha256":report["code_sha256"],"context_inputs":0,"zero_is_NOT_NULL":True},indent=2))

if __name__=="__main__":main()
