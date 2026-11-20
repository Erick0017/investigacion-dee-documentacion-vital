"""Synthetic stdlib/API-MOCK checks. Never a DEE execution or result."""
from pathlib import Path
from types import ModuleType,SimpleNamespace
import hashlib,importlib.util,json,sys


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def main():
    base=Path(__file__).resolve().parent
    output=base.parent/"control"/"C2_PURE_TEST_R01"
    if output.exists():raise ValueError("No overwrite of a prior pure check")
    output.mkdir()
    before=set(sys.modules)
    m=load(base/"pi04_coordinacion_adquirida.py","C2_PURE_DRAFT")
    pure=load(base/"E3"/"e3_retorno_desacoplado_R01.py","E3_PURE_DRAFT")
    m._MODULES["e3_retorno_desacoplado_R01"]=pure
    p,ph=m.protocol()
    assert p["status"]=="DRAFT"
    try:m.protocol(material=True)
    except ValueError:pass
    else:raise AssertionError("Draft executed")
    refused=[]
    for name,row in (("target",{"modo":m.OPPORTUNITY,"target":1}),
                     ("answer",{"modo":m.ADMIT,"brazo":"real","answer":1}),
                     ("calibration_other",{"modo":m.CALIBRATE,"valor":3}),
                     ("bool_scalar",{"modo":m.CALIBRATE,"valor":True}),
                     ("path",{"modo":m.ADMIT,"brazo":"yoked","plan":"C:/bad"})):
        try:m.validate_literal(row)
        except(ValueError,KeyError):refused.append(name)
        else:raise AssertionError("Accepted prohibited field: "+name)
    for value,expected in ((-1,"diferencia"),(0,"diferencia"),(1,"suma"),(None,None),(True,None)):
        assert m._operation(value)==expected
    assert m._motor(0)==-1 and m._motor(None)is None and m._motor(True)is None
    try:m._checked_metadata({"too_big":"x"*65537},lambda x:x)
    except ValueError:refused.append("metadata_over64KB")
    else:raise AssertionError("Unbounded metadata")
    assert m._checked_metadata({"tuple":(1,2)},lambda x:x)=={"tuple":[1,2]}

    # Device checks use explicit synthetic values. They neither solve a DEE
    # task nor count as an acquisition/control reproduction.
    device=m.Device.prepare(output/"device",6,p["environment"])
    cases=[(-1,"diferencia",7,4,True),(1,"suma",25,6,True),
           (-1,"suma",25,6,False),(1,"suma",25,4,False),
           (None,None,None,6,False),(-1,"diferencia",0,4,True)]
    effects=[]
    for i,(route,operation,value,context,success)in enumerate(cases):
        device.begin(route,operation,value,context,10+3*i,11+3*i)
        effect=device.complete(11+3*i);assert effect["failed"] is not success
        device.feedback({"id":100+i});device.reconcile({"id":100+i,"status":"applied"})
        if success:
            product=device.home/effect["product"]["path"]
            data=product.read_bytes()
            assert len(data)==64 and int.from_bytes(data[:2],"little")==value
            assert hashlib.sha256(data).hexdigest()==effect["product"]["sha256"]
        effects.append(effect)

    # Integration MOCK: arithmetic returns literal7 despite16/9+ being asked.
    # The important invariant is transport of ACTUAL API output7, never an
    # expected25 calculated by the coordinator. Fake APIs are visibly named.
    trial_reports=[]
    for arm,first_choice,numeric in (("real",1,7),("none",1,7),("link_cut",1,7),
                                     ("actuator_null",1,7),("real",None,None),("real",1,None)):
        module=load(base/"pi04_coordinacion_adquirida.py","C2_MOCK_"+str(len(trial_reports)))
        mp=json.loads(json.dumps(p));mp["status"]="SEALED_FOR_EVALUATION"
        mp["schedule"]=[{"stage":"development","context":6,"left":16,"right":9}]
        home=output/("mock_%02d"%len(trial_reports));home.mkdir()
        (home/module.FOLDER).mkdir();module.Device.prepare(home/module.FOLDER/"dispositivo",1,mp["environment"])
        owner=SimpleNamespace(tick=0,world=SimpleNamespace())
        owner.run_until=lambda tick:setattr(owner,"tick",tick)if tick>=owner.tick else (_ for _ in()).throw(ValueError("MOCK reverse"))
        memory={"version":module.VERSION,"arm":arm,"ordinal":0,"ready":True,"admitted":True,
                "rows":[],"pending":None,"uncertain":False,"halted_reason":None,"protocol_sha256":"MOCK",
                "log_count":0,"log_chain_sha256":"00"*32}
        events=[];calls=[];counter=[0]
        def req(channel,tick,**extra):
            counter[0]+=1;return {"id":counter[0],"channel":channel,"requested_tick":tick,**extra}
        cal={"query_tick":115,"query_read_tick":121,"seed_tick":122,"outcome_injection_tick":389,
             "collision_tick":390,"contact_tick":391,"settled_after_tick":393,"delay_ticks":268,"delay_laps":4}
        helper=SimpleNamespace(schedule_trial=lambda *args:dict(cal),
            submit_query=lambda world,tick,**kwargs:[req("query"+str(i),tick)for i in range(3)],
            submit_motor_copy=lambda world,choice,tick,**kwargs:(calls.append(["COPY",choice,owner.tick,tick])or req("copy",tick)),
            submit_generic_outcome=lambda world,failed,tick,**kwargs:(calls.append(["RETURN",failed,owner.tick,tick])or req("outcome",tick)))
        sensor=SimpleNamespace(submit_datum=lambda a,value,q:req("datum",q+3,payload=value),
                               read_fixed=lambda a,q:{"choice":first_choice,"tick":a.tick,"MOCK":True})
        hardware=SimpleNamespace(_receipts=lambda a,requests:[dict(r,receipt={"id":r["id"],"status":"applied","MOCK":True})for r in requests])
        module.validate=lambda *args:None
        module._identity=lambda *args:(mp,"MOCK",{"life_id":"SYNTHETIC_MOCK_NOT_DEE"})
        module._get=lambda a:memory
        module._save=lambda *args:None
        module._record=lambda a,m,d,e:events.append(module._jsonsafe(e))
        module._banks=lambda a:[{"clock":"0"},{"clock":"0"}]
        module._frame=lambda a,label:{"label":label,"MOCK_tick":a.tick}
        module._helper=lambda:helper;module._sensor=lambda:sensor;module._hardware=lambda:hardware;module._pure=lambda:pure
        package=ModuleType("capacidades");package.__path__=[]
        ar=ModuleType("capacidades.aritmetica_directa_eci02");ar.MODE="MOCK_native_arithmetic"
        def arithmetic_execute(a,row):
            calls.append(["ARITHMETIC",dict(row),a.tick]);a.run_until(a.tick+198)
            return {"numeric_result":numeric,"MOCK":True}
        ar.execute=arithmetic_execute
        mu=ModuleType("capacidades.mente_unificada_01")
        mu.query_timing=lambda a,t:{"effective_query_tick":t,"MOCK":True}
        def current(a,value,detail=False):
            calls.append(["SECOND_SENSOR",value,a.tick]);a.run_until(a.tick+16)
            return {"reader":{"choice":-1,"MOCK":True},"actual_mock_value":value}
        mu.current=current
        package.aritmetica_directa_eci02=ar;package.mente_unificada_01=mu
        old={k:sys.modules.get(k)for k in ("capacidades","capacidades.aritmetica_directa_eci02","capacidades.mente_unificada_01")}
        sys.modules.update({"capacidades":package,"capacidades.aritmetica_directa_eci02":ar,"capacidades.mente_unificada_01":mu})
        try:result=module._opportunity_body(owner,home)
        finally:
            for k,v in old.items():
                if v is None:sys.modules.pop(k,None)
                else:sys.modules[k]=v
        assert result["after_tick"]==393
        if first_choice is not None:
            assert calls[0][0]=="COPY" and calls[0][2]==121 and calls[0][3]==122
            assert calls[1][0]=="ARITHMETIC" and calls[1][1]["operacion"]=="suma"
        if arm not in("link_cut",)and numeric==7:
            assert next(c for c in calls if c[0]=="SECOND_SENSOR")[1]==7
        else:assert not any(c[0]=="SECOND_SENSOR"for c in calls)
        if arm=="none":assert result["returned_failed"]is False
        if arm in("link_cut","actuator_null")or first_choice is None or numeric is None:
            assert result["actual_failed"]is True and not result["useful_product"]
        else:
            assert result["useful_product"] and result["actual_effect"]["actual_value"]==7
        assert calls[-1][0]=="RETURN" and calls[-1][2]==388 and calls[-1][3]==389
        trial_reports.append({"kind":"SYNTHETIC_API_MOCK_NOT_DEE","arm":arm,"first_choice":first_choice,
                              "mock_actual_result":numeric,"calls":calls,"mock_effect":result["actual_effect"],
                              "mock_first_NULL_preserved":result["first_NULL_preserved"]})
    dee=[x for x in set(sys.modules)-before if x=="dee_thinking"or x.startswith("dee_thinking.")]
    assert not dee
    report={"schema":"PI04.C2.pure_static_mock_check.R01","status":"PURE_TESTS_PASSED_NOT_NATIVE",
            "Native_ticks":0,"official_DEE_imports":dee,"refusals":refused,
            "device_synthetic_effects":effects,"integration_MOCK":trial_reports,
            "code_sha256":hashlib.sha256((base/"pi04_coordinacion_adquirida.py").read_bytes()).hexdigest(),
            "unverified":["Native sensor polarity/admission","FI128/current real latency","Native generic-credit compatibility","learning/usefulness/retention"]}
    target=output.parent/"C2_PURE_TEST_R01.json"
    if target.exists():raise ValueError("Refuse prior report overwrite")
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"report":str(target),"status":report["status"],"mock_trials":len(trial_reports),
                      "Native_ticks":0,"official_DEE_imports":dee,"code_sha256":report["code_sha256"]},indent=2))


if __name__=="__main__":main()
