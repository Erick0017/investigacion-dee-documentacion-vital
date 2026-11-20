"""Build bounded CF01 closure data from closed existing files. No engine/ticks."""
from pathlib import Path
import argparse, ast, gzip, hashlib, json, shutil, sys, time
from datetime import datetime, timezone

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf8")

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--distribution", required=True, type=Path)
    ap.add_argument("--closed-proof", action="store_true")
    args=ap.parse_args(); root=args.root.resolve()
    lab=root/"laboratorio/campanas/CF01_CIERRE_FUNCIONAL"
    ev=root/"evidencia/campanas/CF01_CIERRE_FUNCIONAL"
    stage=lab/"cierre/PAQUETE_ANALISIS"
    sys.path.insert(0,str(lab/"mecanismo"))
    from observador_snapshot_existente import Snapshot
    copied=[]
    def copy(src, rel):
        src=Path(src); dst=stage/rel; dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dst)
        assert sha(src)==sha(dst)
        copied.append({"source":str(src),"export":str(rel).replace("\\","/"),"bytes":src.stat().st_size,"sha256":sha(src)})
    delta=[
        "sistema/gestionar.py","sistema/capacidades/cierre_funcional_cf01.py",
        "sistema/contratos/CF01_SERVICIO_CONTEXTUAL.json",
        "sistema/capacidades/CATALOGO_CAPACIDADES.json",
        "sistema/documentacion/GUIA_CF01.md","CONTINUIDAD_CF01_CIERRE_FUNCIONAL.json","LEER_PRIMERO.md"]
    for rel in delta:
        src=root/rel
        if src.suffix==".py":ast.parse(src.read_text(encoding="utf-8-sig"),filename=rel)
        if src.suffix==".json":json.loads(src.read_text(encoding="utf-8-sig"))
        copy(src,Path("DELTA_OPERATIVO")/rel)
    manual="DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_9_CF01_SIN_VALIDACION_VISUAL.docx"
    copy(root/manual,manual)
    for name in ("CAMBIOS_MANUAL.md","VERIFICACION_MANUAL_CF01.json"):
        copy(lab/"documentos"/name,name)
    copy(lab/"documentos/qa_final_1_9_rev3/VERIFICACION_DOCUMENTO.json","VERIFICACION_RENDER_INTENTADO.json")
    for name in ("MAPA_MECANISMOS_Y_FUENTES_CF01.md","INDICE_FUENTES_EXTRAIDAS.json"):
        copy(lab/"documentos"/name,Path("FUENTES_DIRIGIDAS")/name)
    copy(lab/"mecanismo/SINTESIS_MECANISMO_CF01.md","ANEXO_MECANISMO.md")
    for src in sorted((lab/"mecanismo").glob("R10_*.json")):
        copy(src,Path("CONFIGURACIONES/ALTERNATIVA_NO_EJECUTADA")/src.name)
    copy(lab/"mecanismo/geometria_cierre_funcional_cf01_r10_codigo_fijado.py",
         "CONFIGURACIONES/ALTERNATIVA_NO_EJECUTADA/geometria_r10_no_ejecutada.py")
    test=args.distribution/"actualizaciones/VERIFICACION_DECODER_CF01.json"
    if test.is_file():copy(test,"VERIFICACION_DECODER_AISLADO.json")
    for name in ("AUDITORIA_ALCANCE_CF01.md","AUDITORIA_ALCANCE_CF01.json"):
        src=lab/"cierre"/name
        if src.is_file():copy(src,name)
    known={
        "CF01_MAIN":"Final real: delta4, context7/5, B61/19, calibration8; bounded service4/5 after first error. Same continuous biography.",
        "CF01_CALIBRACION7":"Earlier exact fork before world calibration change; delta3,context7/5,B61/19; not final repaired state.",
        "CF01_PLANTILLA_R9":"Earlier exact fork before new private observation;delta3,context0/5,B61/19. Old queue usable; not the composite learned context.",
        "CF01_B_CUT":"Control with post-formation native message cut. Context0/5; later own reference compensates partly, not recovered B message.",
        "CF01_B_SHAM":"Control sham. New context7/5 and service18/18 within measured domain.",
        "CF01_B_DESACOPLADO":"Alternative private observation36 of different amplitude, not same-dose message randomization.",
        "CF01_SIN_RETORNO":"Native contact-return omitted in queue:3/24jobs.",
        "CF01_ACCION_ANULADA":"External action cancelled after native command; native contact-return intact.",
        "CF01_SERVICIO_ANULADO":"Service external action cancelled after native command:0/18effects despite18/18native correctness.",
        "CF01_SERVICIO_ANTES_CAMBIO":"Earlier pre-POST snapshot; not selected final and no retrospective replacement.",
        "CF01_POST_SIN_RETORNO":"Matched POST control without return; distinguishes harmful update and evaluation readquisition.",
        "CF01_CAL8_SIN_RETORNO":"Matched world8 control;delta3retained,2/5; not MAIN learning."
    }
    fichas=[]
    for life,scope in known.items():
        path=root/"sistema/estado/vidas"/life/"VIDA.json"
        if not path.is_file():continue
        d=json.loads(path.read_text(encoding="utf-8-sig"))
        snap=root/"sistema"/d["snapshot"]
        assert snap.is_file() and sha(snap)==d["snapshot_sha256"]
        row={k:d[k]for k in ("life_id","profile","branch","parent","snapshot","snapshot_sha256","physical","interfaces","availability")}
        row.update({"source_record_sha256":sha(path),"source_record":str(path),"functional_scope":scope,
                    "type":"Connected composite R9 A/B in one native Runtime; regions and channels not separate complete minds",
                    "prepared":"Bodies, supplies, routes, sensor/actuator and finite environmental opportunities",
                    "host_decisions":"Select copy and protocol, exogenous inputs/world law; never target-dependent native action selection",
                    "no_capability_transfer_between_lives":True})
        fichas.append(row)
    write(stage/"FICHAS_Y_COMPARACION_DE_VIDAS.json",{"schema":"CF01.life.scope.v1","new_native_ticks":0,"lives":fichas,
       "not_all_historical_product_capabilities_belong_to_MAIN":True})
    selected=[]
    for life in ("CF01_MAIN","CF01_CALIBRACION7","CF01_PLANTILLA_R9","E1_SOCIAL_11","MI02_SOCIAL_REUSABLE_240"):
        d=json.loads((root/"sistema/estado/vidas"/life/"VIDA.json").read_text(encoding="utf-8-sig"))
        s=Snapshot(root/"sistema"/d["snapshot"])
        q=s.summary()
        assert q["encoded_sha256"]==d["snapshot_sha256"] and q["tick"]==d["physical"]["tick"]
        assert q["RAW_sha256"]==d["physical"]["RAW_sha256"] and q["clocks_sha256"]==d["physical"]["clocks_sha256"]
        q["life"]=life;selected.append(q)
    active=json.loads((root/"sistema/estado/ACTIVO.json").read_text(encoding="utf-8-sig"))
    assert active["life_id"]=="E1_SOCIAL_11" and active["tick"]==3154
    budget=json.loads((lab/"PRESUPUESTO.json").read_text(encoding="utf-8-sig"))
    now=datetime.now(timezone.utc).isoformat(); elapsed=time.monotonic()-budget["monotonic_start"]
    assert elapsed<budget["maximum_seconds"]
    proof={"schema":"CF01.closed.operational.cut.v1","status":"CLOSED_WITH_BOUNDED_FUNCTIONAL_SCOPE",
        "created_utc":now,"new_native_ticks_in_this_check":0,
        "science_closed_final_tick":67723,"selected_full_snapshots":selected,"protected_active":active,
        "manual":{"path":manual,"sha256":sha(root/manual),"bytes":(root/manual).stat().st_size,
                  "structural_verified":True,"visual_verified":False,"reason":"Authorized bundled LibreOffice unavailable"},
        "native_originals_not_modified_by_packaging":True,"operator_initiates_opportunities":True,
        "no_global_promotion":True,"budget":{"start":budget["start_utc"],"deadline":budget["deadline_utc"],
            "elapsed_monotonic_seconds":elapsed,"maximum_seconds":budget["maximum_seconds"],
            "no_budget_restart":True,"peak_RAM_not_measured":True},
        "closed_operational_files":[{"path":r,"bytes":(root/r).stat().st_size,"sha256":sha(root/r)}for r in delta],
        "compact_stage_members_at_check":sum(p.is_file()for p in stage.rglob("*")),
        "scope":"Read-only CRC/checksum/full physical buffers+queues metadata parse; not another native simulation. Exact ZIP extraction test is subsequent independent delivery verification."}
    write(stage/"VERIFICACION_CORTE_LOCAL.json",proof)
    write(stage/"DELTA_Y_DOCUMENTOS_FUENTES.json",{"files":copied,"new_native_ticks":0})
    manifest=[{"path":p.relative_to(stage).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)}
              for p in sorted(stage.rglob("*"))if p.is_file()and p.name!="MANIFIESTO_HASHES.json"]
    write(stage/"MANIFIESTO_HASHES.json",{"schema":"CF01.analysis.manifest.v1","members":manifest,"self_hash_excluded":True})
    if args.closed_proof:
        # Last original write before updater consumes this closed selection.
        write(ev/"VERIFICACION_CORTE_OPERATIVO_CF01.json",proof)
    print(json.dumps({"stage":str(stage),"files":len(manifest)+1,"bytes":sum(q["bytes"]for q in manifest),
        "selected":len(selected),"new_ticks":0,"elapsed":elapsed,"closed_proof":args.closed_proof}))

if __name__=="__main__":main()
