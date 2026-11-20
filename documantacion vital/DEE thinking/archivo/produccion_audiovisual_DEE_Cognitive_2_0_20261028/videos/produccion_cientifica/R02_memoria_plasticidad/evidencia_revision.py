"""Extracción editorial de la revisión de ``clasifica`` ya registrada.

No importa DEE, no crea estados y no ejecuta solicitudes ni simulaciones.
Importar el módulo no lee archivos. ``extract()`` sólo verifica y lee las
fuentes indicadas; devuelve datos para el único control de producción R02.
"""
from pathlib import Path
import gzip
import hashlib
import json


_PRIMARY = {
    "before": (
        "DEMO_PARTE_A/resultados/a13_clasifica.json.gz",
        "edef1ed28b9517ff11fa3666e591621c2064d32334c53caaae0e867e5a918a90",
    ),
    "revision": (
        "DEMO_PARTE_A/resultados/a21_revision.json.gz",
        "8108349009976c3c31d492781834e5c530aa2a95e92134b57c754b8e8221da9c",
    ),
    "after": (
        "DEMO_PARTE_A/resultados/a22_revision_use.json.gz",
        "b2bcf193a02e441b3d36b1e9a6c0d66ea256f82aaada747fd23d8805dc1302b4",
    ),
    "after_rest": (
        "DEMO_PARTE_A_CONTINUACION_R02/resultados/a40_rest_revision.json.gz",
        "b1a6a105bcb1c212028a4003b9f125cf8f1afe6811b6b2a0db59c1a704c537d4",
    ),
    "save": (
        "DEMO_PARTE_A_CONTINUACION_R02/resultados/a44_save.json.gz",
        "dde4de86de7eacceefe7872705953750afac9f19566a0c8528d11be851bf3407",
    ),
    "stop": (
        "DEMO_PARTE_A_CONTINUACION_R02/resultados/a45_stop.json.gz",
        "269a4d001c474857731d596ca5b8202fbeeb1b3a682d97c270183cf6f76f4704",
    ),
    "reopen": (
        "DEMO_PARTE_B/resultados/b02_reopen.json.gz",
        "680703fbf711b3f74d3c187ac7287c091ca53315cbd413bf2a3622d61081e4cc",
    ),
    "retained": (
        "DEMO_PARTE_B/resultados/b09_revision.json.gz",
        "4b44f9ddd75434472e19b730a9602d05f77e913cdc79cbab5a42795690bd5325",
    ),
}

_QUERY_PAYLOAD_SHA = "d28b44882f785faaf2ad030468ab0c3d52577e419f561760937bef4edae69a02"
_ROW_POINTER = "/job/result/request/result [JSON string]/result/rows/0"


def _checked_bytes(path, expected_sha):
    value = path.read_bytes()
    actual = hashlib.sha256(value).hexdigest()
    if actual != expected_sha:
        raise ValueError(f"Fuente editorial distinta: {path}; SHA-256 {actual}")
    return value


def _request(doc):
    request = doc["job"]["result"]["request"]
    assert request["status"] == "completed" and request["error"] is None
    assert doc["job"]["result"]["native_result_not_replaced"] is True
    value = request["result"]
    return request, json.loads(value) if isinstance(value, str) else value


def _base_event(key, doc, request, value):
    committed = value["committed_snapshot"]
    assert committed["life_id"] == "DEE20_DEMO_01"
    return {
        "key": key,
        "subject": "DEE20_DEMO_01",
        "job_id": doc["job"]["id"],
        "finished_utc": doc["job"]["finished_utc"],
        "transport_id": request["id"],
        "status": request["status"],
        "payload": json.loads(request["payload"]),
        "payload_sha256": request["payload_sha"],
        "before_tick": value["before_tick"],
        "after_tick": value["after_tick"],
        "committed_snapshot_sha256": committed["snapshot_sha256"],
        "physical": committed["physical"],
        "pointer": "/job/result/request/result [JSON string]",
    }


def _receipts(row):
    result = [item["receipt"] for item in row["requests"]]
    assert all(item["status"] == "applied" for item in result)
    return result


def extract():
    """Return the verified, already-existing episode and image provenance.

    This is archived-data recalculation, not a new causal intervention. The
    physical continuity assertion compares N/tick/RAW/clocks on save, stop and
    reopen. Encoded snapshot hashes can differ because owner metadata changes.
    """
    here = Path(__file__).resolve().parent
    project = here.parent
    thinking = here.parents[4]
    data = thinking / "archivo/DEE_Cognitive_2_0_historial_presentacion_R01/videos/datos"
    docs, sources = {}, []
    for key, (relative, expected) in _PRIMARY.items():
        path = data / relative
        raw = _checked_bytes(path, expected)
        docs[key] = json.loads(gzip.decompress(raw).decode("utf-8-sig"))
        sources.append({
            "key": key,
            "path": str(path),
            "sha256": expected,
            "bytes": len(raw),
            "encoding": "gzip containing UTF-8 JSON",
            "subject": "DEE20_DEMO_01",
            "pointer": (
                "/job/result/record; /job/result/owner/observation" if key == "reopen"
                else "/job/result/request/result [JSON string]/committed_snapshot/physical" if key in {"save", "stop"}
                else _ROW_POINTER
            ),
        })

    events = {}
    for key in ("before", "revision", "after", "after_rest", "save", "stop", "retained"):
        req, value = _request(docs[key])
        event = _base_event(key, docs[key], req, value)
        events[key] = event
        if key in {"save", "stop"}:
            assert value["before_tick"] == value["after_tick"] == 697650
            continue
        row = value["result"]["rows"][0]
        assert row["form"] == "clasifica"
        receipt_rows = _receipts(row)
        event.update({
            "form": "clasifica",
            "input_tick": row["input_tick"],
            "end_tick": row["end_tick"],
            "receipts": receipt_rows,
            "requested": len(row["requests"]),
            "applied": len(receipt_rows),
            "rejected": 0,
            "pointer": _ROW_POINTER,
        })
        if key == "revision":
            assert row["kind"] == "APD04_explicit_lexical_revision"
            assert row["lesson_is_explicit_external_experience"] is True
            assert row["revision"] is True and row["teacher_sign"] == -1
            assert row["teacher_mode"] == "paired"
            assert row["teacher_tick"] == row["input_tick"] == 688961
            assert len(receipt_rows) == 3
            assert row["hub"]["site"] == [50, 7, 47]
            assert row["hub"]["direction"] == [0, 0, -1]
            event.update({
                "kind": row["kind"],
                "teacher_mode": row["teacher_mode"],
                "teacher_sign": row["teacher_sign"],
                "teacher_tick": row["teacher_tick"],
                "lesson_is_explicit_external_experience": True,
                "hub_after_revision": row["hub"],
                "attribution": "Operator supplies a declared lesson; three admitted material inputs evolve under DEE. This does not claim autonomous choice of what to learn.",
            })
        else:
            assert row["kind"] == "APD04_common36_lexical_query"
            assert req["payload_sha"] == _QUERY_PAYLOAD_SHA
            assert row["teacher_correct_function_or_expected_sign_supplied"] is False
            assert len(receipt_rows) == 7
            reader = row["reader"]
            assert reader["ambiguous"] is False
            assert reader["formed_native_command"] == (1 if key == "before" else -1)
            event.update({
                "read_tick": row["read_tick"],
                "sign": reader["formed_native_command"],
                "reader_candidates": reader["candidates"],
                "teacher_correct_function_or_expected_sign_supplied": False,
                "dense_microscopic_frames_available": bool(row.get("frames")),
            })

    reopened = docs["reopen"]["job"]["result"]
    record = reopened["record"]
    owner = reopened["owner"]["observation"]
    assert record["life_id"] == record["world_id"] == owner["life_id"] == "DEE20_DEMO_01"
    assert reopened["owner"]["started_paused"] is True and owner["paused"] is True
    assert record["parent"]["source_tick"] == 684418
    physical_keys = ("N", "tick", "RAW_sha256", "clocks_sha256")
    physical = [{k: p[k] for k in physical_keys} for p in (
        events["save"]["physical"], events["stop"]["physical"], record["physical"], owner["physical"]
    )]
    assert all(p == physical[0] for p in physical)
    assert physical[0]["N"] == 67 and physical[0]["tick"] == 697650
    events["reopen"] = {
        "key": "reopen", "subject": "DEE20_DEMO_01",
        "job_id": docs["reopen"]["job"]["id"],
        "finished_utc": docs["reopen"]["job"]["finished_utc"],
        "pointer": "/job/result/record/physical; /job/result/owner/observation/physical",
        "physical": physical[0], "started_paused": True,
        "parent": record["parent"],
    }

    visuals = []
    for key, rel, expected, role in (
        ("before_receipt", "fuentes_g07/demo_t170.png", "7868e23ca2ed7fd9c3895cb280c7883b5167a4f7dd86b7e9a9cb6bc1462cc869", "Authentic captured UI: palabra clasifica and +1 receipt."),
        ("retained_receipt", "fuentes_g07/demo_t1418.png", "649189139b383708e1f5d38b0e11749965b114acc52a58a1e9cc159543efc718", "Authentic captured UI after reopening: clasifica -1 receipt."),
        ("teaching_frame", "clips/teach/00001.jpg", "668ad960937cb81454cfbe80df8b9fd9fa6db300977fd7aa4bfb08a4db2949eb", "Authentic teaching form showing clasifica, -1 and declared revision; crop excludes an unrelated old command field."),
    ):
        path = project / rel
        raw = _checked_bytes(path, expected)
        visual = {"key": key, "path": str(path), "sha256": expected, "bytes": len(raw), "role": role}
        if key == "teaching_frame":
            visual.update({"crop_in_jpg": [0, 153, 496, 265], "crop_in_original_video": [18, 513, 514, 625], "source_time_seconds": [416.4, 421.4]})
        visuals.append(visual)

    # The ready descriptor links existing crop frames to the original recording.
    ready_path = project / "clips/teach/ready.json"
    ready_bytes = _checked_bytes(ready_path, "d3a2837b964c74d8996102d36f6240ed24a4f7675e46a42d0b2ad9cd63fa373a")
    ready = json.loads(ready_bytes)
    assert ready["range"] == [416.4, 421.4] and ready["crop"] == [18, 360, 514, 670]
    assert ready["frames"] == 75 and ready["fps"] == 15
    sources.append({"key": "teaching_clip_descriptor", "path": str(ready_path), "sha256": hashlib.sha256(ready_bytes).hexdigest(), "pointer": "/source; /range; /crop; /frames; /fps"})
    recording_path = Path(ready["source"])
    recording_sha = "cd4c137f3529b86583cea0934a2f1bf364998c8dcaba6c4bca06fbcb40f36c87"
    recording_bytes = _checked_bytes(recording_path, recording_sha)
    sources.append({"key": "original_authentic_recording", "path": str(recording_path), "sha256": recording_sha, "bytes": len(recording_bytes), "pointer": "t416.4–421.4; original crop18,360,514,670; more precise teaching ROI18,513,514,625"})

    chronology = [events[k] for k in ("before", "revision", "after", "after_rest", "save", "stop", "reopen", "retained")]
    return {
        "schema": "DEE.video.R02.archived_revision_evidence.v1",
        "subject": "DEE20_DEMO_01", "N": 67,
        "sources": sources, "events": events, "chronology": chronology, "visuals": visuals,
        "same_query_payload_sha256": _QUERY_PAYLOAD_SHA,
        "save_stop_reopen_physical_exact": physical[0],
        "initial_relationship_attribution": "The +1 before a21 was inherited from the complete APD05 import, not first taught in this recorded DEE20 demonstration.",
        "interpretation": "An explicit new experience revises the response; the same subsequent query yields -1, including after recorded intervening use, rest and physical reopening.",
        "limits": [
            "+1 and -1 are registered physical code responses, not correctness or value judgements.",
            "The a22 video crop shows the actual query field, not its result log: draw its -1 only as labelled recorded primary data.",
            "Query frames are empty; the records do not justify an invented microscopic animation of this episode.",
            "This extraction does not add a new ablation, causal experiment or generalisation claim.",
            "Snapshot container hashes differ across save/stop/reopen; equality asserted here is exact N/tick/RAW/clocks and identity, not equality of every host metadata byte.",
        ],
        "new_native_ticks": 0, "new_HTTP_requests": 0, "files_written_by_extract": 0,
    }
