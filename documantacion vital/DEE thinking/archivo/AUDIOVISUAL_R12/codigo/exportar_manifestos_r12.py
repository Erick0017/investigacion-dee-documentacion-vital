"""Export frozen R12 models and scoped source/voice bindings, with zero render.

Observed cards are editable media data, not complete DEE worlds, life backups,
native replay, or a certification of intelligence. No original R12 spec exists.
"""
from pathlib import Path
from collections import defaultdict
import datetime as dt
import gzip
import hashlib
import importlib.abc
import json
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"codigo"))


class NoNative(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname.split(".")[0] in {"dee_thinking","sqlite3","_sqlite3"}:
            raise RuntimeError("Native/SQLite imports prohibited in this media export")
        return None


sys.meta_path.insert(0,NoNative())
import producir_r12 as production

UNKNOWN="unknown: not provided by the selected model/source binding"
PHYSICAL_FIELDS=("site","coordinate","raw","RAW","clock","state","s_reg","semantic","direction","tick","active")


def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")
def data_sha(v):return hashlib.sha256(canonical(v)).hexdigest()
def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
    return h.hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def unique(vals):return list({data_sha(v):v for v in vals if v is not None and v!=[] and v!={} and v!=""}.values())


def walk(v):
    if isinstance(v,dict):
        yield v
        for x in v.values():yield from walk(x)
    elif isinstance(v,list):
        for x in v:yield from walk(x)


def assert_cards_only(model):
    for item in walk(model):
        for key,value in item.items():
            if key.lower() in {"buffers","raw_buffer","clock_buffer","native_buffers","snapshot_buffers"} and isinstance(value,(dict,list,str)) and value:
                raise ValueError("Opaque full-state buffer would enter editable model: "+key)
            if isinstance(value,str) and len(value)>200000:
                raise ValueError("Unreviewed opaque large field in model: "+key)


def bindings(model):
    candidates=list(model.get("evidence_bindings") or [])+list(model.get("source_refs") or [])
    if model.get("source"):candidates.append(model["source"])
    for p in model.get("panels",[]):
        if p.get("source"):candidates.append(p["source"])
    found=[]
    for d in walk(candidates):
        path=d.get("path",d.get("source_path",d.get("resolved_source")))
        h=d.get("sha256",d.get("source_sha256"))
        if isinstance(path,str) and isinstance(h,str) and len(h)==64:
            b={k:v for k,v in d.items() if k not in {"record","records","panel","points","observations","frames","data","buffers"}}
            b["path"]=path;b["sha256"]=h
            found.append(b)
    return unique(found)


def physical_card(model):
    cards=[]
    for panel in model.get("panels",[]):
        points=[]
        for p in panel.get("points",[]):
            q={k:p[k] for k in PHYSICAL_FIELDS if k in p}
            for key in ("raw","RAW","clock"):
                if key in q:q[key]=str(q[key])
            points.append(q)
        cards.append({"N":panel.get("N"),"tick":panel.get("tick"),"points":sorted(unique(points),key=canonical)})
    return cards


def exact_point_projection(model):
    # Compare ALL fields of every point, with original point/panel order.
    # This stricter projection is separate from the compact observed-card hash.
    return [{"N":p.get("N"),"tick":p.get("tick"),"points":p.get("points",[])} for p in model.get("panels",[])]


def leaf_differences(a,b,path=""):
    if isinstance(a,dict) and isinstance(b,dict):
        out=[]
        for key in sorted(set(a)|set(b)):
            sub=path+"/"+str(key)
            if key not in a or key not in b:out.append((sub,a.get(key),b.get(key)))
            else:out+=leaf_differences(a[key],b[key],sub)
        return out
    if isinstance(a,list) and isinstance(b,list):
        if len(a)!=len(b):return [(path+"/@length",len(a),len(b))]
        return [v for i,(x,y) in enumerate(zip(a,b)) for v in leaf_differences(x,y,path+"/"+str(i))]
    return [] if a==b and type(a)==type(b) else [(path,a,b)]


def allowed_annotation_change(path):
    parts=path.strip("/").split("/")
    return path in {"/title","/notice","/footer","/source_data_hash","/physical_data_sha256"} or \
        (len(parts)==3 and parts[0]=="panels" and parts[1].isdigit() and parts[2] in {"label","title","notice","footer"})


SELECTION_S12_SOURCE_TICKS={"04_FUENTE_T.json.gz":{121681,124809},"10_DESTINO_B_T.json.gz":{125496},"11_DESTINO_B_U.json.gz":{125496}}
SELECTION_S12_TOPLEVEL={"bounds","evidence_bindings","extraction_sha256","footer","notice","origin_shot","origin_progress_first","panels","physical_data_sha256","source","source_extraction_sha256","stage_jump"}
_selection_primaries={}


def verify_s12_record_selection(model):
    """Only S12.1 may select different archived observations; validate every point.

    No primary is rewritten. Role is a display annotation; all other retained
    point fields must exactly equal one dictionary in that SHA-checked primary.
    """
    checks=[]
    assert model["shot_id"]=="S12.1"
    for panel in model.get("panels",[]):
        source=panel["source"];path=Path(source["path"]);name=path.name
        assert name in SELECTION_S12_SOURCE_TICKS and panel["tick"] in SELECTION_S12_SOURCE_TICKS[name]
        assert panel["N"]==26 and panel["points"]
        key=(str(path),source["sha256"])
        if key not in _selection_primaries:
            actual=sha(path);assert actual==source["sha256"],"S12.1 primary SHA mismatch"
            body=json.loads(gzip.decompress(path.read_bytes()))
            index={}
            def collect(v,pointer=""):
                if isinstance(v,dict):
                    if {"site","raw","clock"}<=set(v):index.setdefault(data_sha(v),[]).append(pointer)
                    for k,x in v.items():collect(x,pointer+"/"+str(k).replace("~","~0").replace("/","~1"))
                elif isinstance(v,list):
                    for i,x in enumerate(v):collect(x,pointer+"/"+str(i))
            collect(body)
            assert body["result"]["physical"]["N"]==26
            _selection_primaries[key]=(index,body["result"]["INSTRUMENTO"].get("life_id",UNKNOWN))
        index,life=_selection_primaries[key];point_checks=[]
        for point in panel["points"]:
            physical={k:v for k,v in point.items() if k!="role"}
            assert physical.get("tick")==panel["tick"]
            digest=data_sha(physical);assert digest in index,"S12.1 displayed point absent from exact primary"
            point_checks.append({"site":physical.get("site"),"point_all_nonrole_fields_sha256":digest,"exact_primary_pointers":index[digest]})
        checks.append({"path":str(path),"sha256":source["sha256"],"actual_file_sha_verified":True,"life_as_declared_by_primary":life,
            "N":26,"tick":panel["tick"],"point_count":len(point_checks),"point_checks":point_checks})
    return checks


def main():
    dest=ROOT/"PROYECTO_EDITABLE/MODELOS_POR_INTERVALO_R12.json.gz"
    manifest_path=ROOT/"MANIFIESTO_EJECUCION_R12.json"
    claims_path=ROOT/"AFIRMACIONES_VERIFICADAS.json"
    assert not any(p.exists() for p in(dest,manifest_path,claims_path)),"Preserve a prior export; no implicit overwrite"
    dest.parent.mkdir(parents=True,exist_ok=True)
    pending=dest.with_suffix(dest.suffix+".pending");assert not pending.exists()
    before=production.fingerprint()
    phases_path=ROOT/"AUDITORIA/FASES_Y_VOZ_R12.json"
    phases=load(phases_path);phase_rows={r["shot_id"]:r for r in phases["rows"]}
    guion_path=ROOT/"guion_fuente/SHOTLIST_R12_DERIVADO_DEL_DOCX.json"
    guion=load(guion_path)
    literal={s["original_shot_id"]:(c,s) for c in guion["scenes"] for s in c["shots"]}
    previous_dir=ROOT/"AUDITORIA/EXPORTACION_R02"
    previous_models_path=previous_dir/"MODELOS_POR_INTERVALO_R12.json.gz"
    previous=json.loads(gzip.decompress(previous_models_path.read_bytes()))
    previous_intervals=previous["intervals"];previous_index=0
    comparison_pairs=set();annotation_deltas={};unexpected_deltas={};changed_model_frames=0
    physical_bad=[];bindings_bad=[];selection_deltas={};selection_models={};selection_frame_count=0;selection_changed_frame_count=0
    sources={};readers={};receipts={};cards={};shots={};intervals=[];seen=set();models_count=0
    raw_model_bytes=0
    with pending.open("xb") as raw:
        with gzip.GzipFile(filename="",mode="wb",fileobj=raw,compresslevel=9,mtime=0) as output:
            header={"schema":"DEE.R12.editable_observation_models.R04","fps":30,"total_frames":11700,"duration_seconds":390,
                "purpose":"Exact audiovisual model cards only; NOT full DEE snapshots or a continuable life.",
                "source_hashes_before":before,"models":None}
            prefix=canonical({k:v for k,v in header.items() if k!="models"})
            output.write(prefix[:-1]+b',"models":{')
            first=True
            for frame in range(11700):
                model,timing=production.frame_model(frame)
                assert_cards_only(model)
                body=canonical(model);mid=hashlib.sha256(body).hexdigest();raw_model_bytes+=len(body)
                while previous_intervals[previous_index]["end_frame_exclusive"]<=frame:previous_index+=1
                previous_id=previous_intervals[previous_index]["model_id"]
                old_model=previous["models"][previous_id]
                sid=timing["shot_id"]
                selected=sid=="S12.1"
                if selected:
                    selection_frame_count+=1
                    if mid!=previous_id:selection_changed_frame_count+=1
                    if mid not in selection_models:selection_models[mid]=verify_s12_record_selection(model)
                if mid!=previous_id:changed_model_frames+=1
                pair=(previous_id,mid)
                if pair not in comparison_pairs:
                    comparison_pairs.add(pair)
                    if not selected and canonical(exact_point_projection(old_model))!=canonical(exact_point_projection(model)):
                        physical_bad.append({"first_frame":frame,"old_model_id":previous_id,"new_model_id":mid})
                    if not selected and canonical(bindings(old_model))!=canonical(bindings(model)):
                        bindings_bad.append({"first_frame":frame,"old_model_id":previous_id,"new_model_id":mid})
                    for path,old,new in leaf_differences(old_model,model):
                        key=data_sha([path,old,new]);record={"path":path,"old":old,"new":new,"first_frame":frame}
                        if selected:
                            assert path.strip("/").split("/")[0] in SELECTION_S12_TOPLEVEL or allowed_annotation_change(path),"Unexpected S12.1 field change: "+path
                            selection_deltas.setdefault(key,record)
                        else:(annotation_deltas if allowed_annotation_change(path) else unexpected_deltas).setdefault(key,record)
                if mid not in seen:
                    seen.add(mid);models_count+=1
                    if not first:output.write(b",")
                    output.write(canonical(mid)+b":"+body);first=False
                if intervals and intervals[-1]["model_id"]==mid:
                    intervals[-1]["end_frame_exclusive"]=frame+1
                else:intervals.append({"start_frame":frame,"end_frame_exclusive":frame+1,"model_id":mid})
                row=shots.setdefault(sid,{"scene_id":timing["scene_id"],"shot_id":sid,"model_ids":set(),"source_ids":set(),
                    "card_ids":set(),"reader_ids":set(),"receipt_ids":set(),"panels":{},"evidence_types":set(),"limitations":[],"point_fields":set()})
                row["model_ids"].add(mid);row["evidence_types"].add(model.get("evidence_type",UNKNOWN));row["limitations"]+=model.get("limitations",[])
                refs=bindings(model)
                for binding in refs:
                    bid=data_sha(binding);sources.setdefault(bid,binding);row["source_ids"].add(bid)
                local=physical_card(model)
                if local:
                    cid=data_sha(local);cards.setdefault(cid,{"point_count":sum(len(p["points"]) for p in local),"N_tick":[{"N":p["N"],"tick":p["tick"]} for p in local]});row["card_ids"].add(cid)
                for i,panel in enumerate(model.get("panels",[])):
                    panel_meta={"N":panel.get("N",UNKNOWN),"tick":panel.get("tick",UNKNOWN),"ROI":panel.get("bounds",model.get("bounds",UNKNOWN)),
                        "source":panel.get("source",UNKNOWN),"point_count":len(panel.get("points",[]))}
                    row["panels"].setdefault(data_sha(panel_meta),panel_meta)
                    row["point_fields"].update(k for point in panel.get("points",[]) for k in PHYSICAL_FIELDS if k in point)
                    reader=panel.get("reader_evidence",panel.get("reader_contract"))
                    if reader is not None:
                        rid=data_sha(reader)
                        readers.setdefault(rid,{"reader_record_canonical_sha256":rid,"model_id":mid,"json_pointer":"/panels/"+str(i)+"/reader_evidence",
                            "type":type(reader).__name__,"keys":list(reader) if isinstance(reader,dict) else None,
                            "scope":"Exact reader record retained inside the editable model; not inferred from caption or target."})
                        row["reader_ids"].add(rid)
                    for kind in ("input_receipts","entry_receipts"):
                        for receipt in panel.get(kind,[]):
                            rid=data_sha(receipt);receipts.setdefault(rid,receipt);row["receipt_ids"].add(rid)
                if frame%1500==0:print(json.dumps({"models_enumerated":frame+1,"unique_exact_models":models_count}),flush=True)
            after=production.fingerprint();assert before==after,"Frozen renderer/data sources changed during export; pending output preserved"
            assert not physical_bad and not bindings_bad and not unexpected_deltas,"R04 differs outside the narrowly validated S12.1 selection or permitted annotations; pending output preserved"
            footer={"intervals":intervals,"ending_editorial_fade":{"start_frame":11670,"last_frame":11699,"formula":"max(0,(11699-i)/29)"},
                "source_hashes_after":after,"frozen_sources_equal_before_after":True,
                "new_Native_ticks":0,"rendered_frames":0,"model_hash_scope":"SHA256 of exact complete canonical model dictionary, INCLUDING editorial annotations. Not a physical event or full-state identity.",
                "no_full_snapshot_buffers":True,"original_adapters_require_private_primaries_not_in_this_editable":True}
            output.write(b"},")
            for k,v in footer.items():
                output.write(canonical(k)+b":"+canonical(v)+b",")
            output.write(b'"export_code_sha256":'+canonical(sha(__file__))+b"}")
    assert intervals[0]["start_frame"]==0 and intervals[-1]["end_frame_exclusive"]==11700
    assert all(a["end_frame_exclusive"]==b["start_frame"] for a,b in zip(intervals,intervals[1:]))
    pending.replace(dest)
    comparison={"schema":"DEE.R12.editorial_export_R02_R04_comparison.R01","frames_checked":11700,
        "unique_model_pairs_checked":len(comparison_pairs),"frames_with_changed_exact_model_dictionary":changed_model_frames,
        "physical_projection":"Every panel's N,tick and complete ordered points list, including every retained point field/value; no stripping or normalization.",
        "physical_differences":physical_bad,"authentic_evidence_binding_differences":bindings_bad,
        "unexpected_nonannotation_changes":list(unexpected_deltas.values()),"annotation_or_derived_hash_deltas":list(annotation_deltas.values()),
        "physical_observations_identical_outside_S12_1":not physical_bad,"authentic_bindings_identical_outside_S12_1":not bindings_bad,
        "only_permitted_annotations_outside_S12_1":not unexpected_deltas and not physical_bad and not bindings_bad,
        "S12_1_source_selection":{"scope":"New editorial selection of existing archived records; not a change to the DEE evolution or primary bytes.",
            "frames_checked":selection_frame_count,"frames_with_changed_model":selection_changed_frame_count,
            "allowed_source_ticks":{k:sorted(v) for k,v in SELECTION_S12_SOURCE_TICKS.items()},
            "selected_models_verified_to_exact_SHA_checked_primaries":selection_models,"all_selected_points_match":True,
            "selection_leaf_deltas":list(selection_deltas.values()),"excluded_return_tick":125500},
        "previous_models_path":str(previous_models_path.relative_to(ROOT)),"previous_models_sha256":sha(previous_models_path),
        "new_models_path":str(dest.relative_to(ROOT)),"new_models_sha256":sha(dest),"current_frozen_sources_equal_before_after":before==after,
        "previous_source_hashes":previous["source_hashes_before"],"current_source_hashes":before,
        "new_Native_ticks":0,"rendered_frames":0,"new_physical_experiments":False}
    comparison_path=ROOT/"AUDITORIA/COMPARACION_EDITORIAL_EXPORTACIONES_R02_R04.json"
    with comparison_path.open("x",encoding="utf-8",newline="\n") as f:json.dump(comparison,f,ensure_ascii=False,indent=2);f.write("\n")
    # Metadata only: archive dates are not guessed from file mtimes or path names.
    for source in sources.values():
        source["path_exists_at_export"]=Path(source["path"]).is_file()
        source["hash_verification_scope"]="SHA as recorded by frozen source/adapter; exporter did not rehash or replay every private primary. R12containers/code fingerprints are verified before/after."
    entries=[];assertions=[]
    for sid,row in shots.items():
        scene,shot=literal[sid]
        refs=[sources[k] for k in sorted(row["source_ids"])]
        metadata=list(row["panels"].values())
        def values(*keys):return unique([r[k] for r in refs for k in keys if k in r]) or [UNKNOWN]
        category="PROSPECTIVE/EDITORIAL" if sid in {"S14.2","S01.1","S01.3","S13.2"} else "SCOPED_ARCHIVED_REFERENCE" if refs else "EXPLANATORY_OR_UNBOUND; no direct source assertion"
        unknown=[]
        for label,ks in {"life/branch":("life","branch_id"),"parent":("parent","parent_id"),"date_of_cut":("cut_date","date","finished_utc","created_utc")}.items():
            if values(*ks)==[UNKNOWN]:unknown.append(label)
        limitations=unique(row["limitations"]+[scene.get("source_contract_exact",""),shot.get("rejection_exact",""),
            "Selected visible observations and reader records only; no full-world buffers or continuable individual are exported.",
            "Different source families, lives and cuts remain separate; montage membership does not merge memories. Known life lists are partial, not exhaustive; unknown attribution is retained separately for each binding.",
            "File/model hashes bind bytes and provenance; they do not certify a scientific claim, video fidelity, listening or intelligence."])
        entry={"scene_id":row["scene_id"],"shot_id":sid,"literal_anchor":shot["anchor_exact"],
            "source_Word":guion["source"],"Word_literal_paragraph_1based":shot["anchor_source_paragraph_1based"],
            "case_id":values("case_id","life"),"life_or_branch":values("life","branch_id"),"parent_id":values("parent","parent_id"),
            "life_or_branch_list_is_partial":True,
            "attribution_by_binding":[{"source_id":data_sha({k:v for k,v in r.items() if k not in {"path_exists_at_export","hash_verification_scope"}}),"path":r["path"],"sha256":r["sha256"],
                "pointer":r.get("pointer",r.get("json_pointer",UNKNOWN)),"life_or_branch":r.get("life",r.get("branch_id",UNKNOWN)),
                "parent_id":r.get("parent",r.get("parent_id",UNKNOWN)),"scope":"Only the identity explicitly declared by this binding; never inherited from another cut or source."} for r in refs],
            "N":unique([p["N"] for p in metadata]) or [UNKNOWN],"ticks":unique([p["tick"] for p in metadata]) or [UNKNOWN],
            "source_paths_and_SHA":[{"path":r["path"],"sha256":r["sha256"],"pointer":r.get("pointer",r.get("json_pointer",UNKNOWN)),"path_exists_at_export":r["path_exists_at_export"]} for r in refs],
            "evidence_bindings":refs,"reader_contract_ids":sorted(row["reader_ids"]) or [UNKNOWN],
            "input_receipt_ids":sorted(row["receipt_ids"]) or [UNKNOWN],"fields_shown":sorted(row["point_fields"]) or [UNKNOWN],
            "ROI_and_sampled_panels":metadata,"representation_categories":sorted(row["evidence_types"]),
            "exact_model_ids":sorted(row["model_ids"]),"observed_card_sha256":sorted(row["card_ids"]),
            "three_phases_and_four_voice_bound_keyframes":phase_rows[sid],"cut_date":values("cut_date","date","finished_utc","created_utc"),
            "source_scope_state":category,"replay_status":"NOT_REPLAYED: offline existing-model enumeration only",
            "video_validation_status":"NOT_CERTIFIED_BY_THIS_MANIFEST","primary_assertion_scope":"Linked selected archived records; actual controls/limitations are retained, no general mind verdict.",
            "unknowns":unknown,"limitations":limitations}
        entries.append(entry)
        assertions.append({"scene_id":row["scene_id"],"shot_id":sid,"frase_literal":shot["anchor_exact"],
            "caso":entry["case_id"],"vida_rama":entry["life_or_branch"],"estado":category,
            "lista_vidas_conocidas_no_exhaustiva":True,"atribucion_por_binding":entry["attribution_by_binding"],
            "archivo_real_SHA256_y_campo":entry["source_paths_and_SHA"],"instante_montaje":{"start_s":phase_rows[sid]["actual_start_s"],"end_s":phase_rows[sid]["actual_end_s"]},
            "instantes_DEE_y_N":metadata,"regla_lectura_ids":entry["reader_contract_ids"],
            "controles_registrados":values("control","control_mode"),"dominio_y_limites":limitations,"fecha_del_corte":entry["cut_date"],
            "texto_literal_cotejado_DOCX":True,"vinculacion_a_modelos_existentes":True,
            "ciencia_estado":"SCOPED_REFERENCE_ONLY; no new native reproduction, all controls and author interpretations not independently re-adjudicated here",
            "percepcion_video":"NO EVALUADO by this export","escucha":"NO EVALUADO","comprension_publica":"NO EVALUADO",
            "prospectivo":category=="PROSPECTIVE/EDITORIAL","no_conclusion_inteligencia_general":True})
    assert len(entries)==len(assertions)==42
    common={"created_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"new_Native_ticks":0,"rendered_frames":0,
        "export_instrument_revision":"FINAL R04: exact comparison outside S12.1; S12.1 selects only primary-verified recorded cuts, with explicit binding-level unknown attribution",
        "prior_complete_editorial_export_R02":{"path":str(previous_dir.relative_to(ROOT)),
            "files":[{"path":str(p.relative_to(ROOT)),"bytes":p.stat().st_size,"sha256":sha(p)} for p in previous_dir.iterdir() if p.is_file()]},
        "prior_complete_editorial_export_R03":{"path":"AUDITORIA/EXPORTACION_R03","files":[{"path":str(p.relative_to(ROOT)),"bytes":p.stat().st_size,"sha256":sha(p)} for p in (ROOT/"AUDITORIA/EXPORTACION_R03").iterdir() if p.is_file()]},
        "editorial_R02_R04_comparison":{"path":str(comparison_path.relative_to(ROOT)),"sha256":sha(comparison_path),
            "physical_observations_and_bindings_identical_outside_S12_1":not physical_bad and not bindings_bad,
            "only_permitted_annotations_outside_S12_1":not unexpected_deltas,"S12_1_all_selected_points_primary_verified":True},
        "prior_export_instrument_failure":{"cause":"TypeError on source_refs=null, before publication; no renderer or native operation executed",
            "source_code":"codigo/revisiones_exportador/R01/exportar_manifestos_r12.py",
            "source_code_sha256":sha(ROOT/"codigo/revisiones_exportador/R01/exportar_manifestos_r12.py"),
            "partial_fragment":"PROYECTO_EDITABLE/MODELOS_POR_INTERVALO_R12_EXPORT_PARCIAL_R01.json.gz.fragment",
            "partial_fragment_sha256":sha(ROOT/"PROYECTO_EDITABLE/MODELOS_POR_INTERVALO_R12_EXPORT_PARCIAL_R01.json.gz.fragment")},
        "source_hashes_before":before,"source_hashes_after":after,"sources_frozen_unchanged":before==after,
        "original_ESPECIFICACION_R12_and_toolkit":"NO EVALUADO: original package was not recovered; only explicit local DOCX derivative is used.",
        "editable_models":{"path":str(dest.relative_to(ROOT)),"bytes":dest.stat().st_size,"sha256":sha(dest),"unique_exact_models":models_count,
            "frame_count":11700,"interval_count":len(intervals),"raw_canonical_model_bytes_enumerated_including_repetitions":raw_model_bytes,
            "full_native_snapshots_included":False,"can_continue_DEE_life":False},
        "physical_hash_scope":"Canonical observed card list {N,tick,points restricted to retained position/RAW/clock/state/s_reg/semantic/direction/active}; role/camera/ROI/labels/progress excluded. Different crops can differ at one tick. Not a complete causal state or event count.",
        "export_code_sha256":sha(__file__)}
    manifest={"schema":"DEE.R12.execution_manifest.LOCAL.R04",**common,"shot_count":42,"shots":entries,
        "reader_registry":readers,"input_receipt_registry":receipts,"observed_card_registry":cards,
        "primary_republication_policy":"Only rendered observation/model cards and source locators are exported. FullU0buffers, snapshots, private complete primaries, modelweights and operational system are omitted; original adapters require their private sources.",
        "verification_states":{"provenance_binding":"EXPORTED_WITH_SCOPE","video":"NOT_ASSESSED_HERE","listening":"NO EVALUADO","comprehension":"NO EVALUADO"}}
    claims={"schema":"DEE.R12.scoped_claim_bindings.LOCAL.R04",**common,"source_Word":guion["source"],"claims":assertions,
        "title_scope":"The required filename AFIRMACIONES_VERIFICADAS does not imply universal proof: each literal anchor has recorded evidence/reference/prospective scope and explicit unknowns.",
        "no_global_PASS":True}
    for path,obj in((manifest_path,manifest),(claims_path,claims)):
        with path.open("x",encoding="utf-8",newline="\n") as f:json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False);f.write("\n")
    print(json.dumps({"models":models_count,"intervals":len(intervals),"frames":11700,"shots":42,
        "source_bindings":len(sources),"readers":len(readers),"native_ticks":0,"rendered_frames":0,
        "outputs":[{"path":str(p),"bytes":p.stat().st_size,"sha256":sha(p)} for p in(dest,manifest_path,claims_path)]},ensure_ascii=False),flush=True)


if __name__=="__main__":main()
