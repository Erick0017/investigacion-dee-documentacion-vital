"""Static narrow adaptation of frozen R03; no Native or source modifications."""
from pathlib import Path
import ast,hashlib,json
P=Path(__file__).resolve().parents[2];C=P.parents[2]/'DEE Cognitive 2.0';HERE=Path(__file__).resolve().parent
source=C/'sistema/capacidades/pi03_suministro_explicito_R03.py'
expected='abe3457c47a3ad3167a9924689a15b3796da1726e90b9d5e116648b78f8d308b'
if hashlib.sha256(source.read_bytes()).hexdigest()!=expected:raise ValueError('Exact frozen R03 required')
original=source.read_bytes();saved=HERE/'pi03_suministro_explicito_R03_ORIGINAL.py'
if saved.exists()and saved.read_bytes()!=original:raise ValueError('Preserved original differs')
if not saved.exists():saved.write_bytes(original)
s=original.decode('utf-8')
s=s.replace('VERSION = "PI03.explicit_bounded_environment_supply.R03_DRAFT"','VERSION = "PI04.compatible_explicit_supply.R03_R02_COMPACT_METADATA"')
anchor='def preflight(m, device, row):\n'
helper='''MAX_NATIVE_METADATA_VALUE_BYTES = 1048576  # Frozen runtime.cpp kMaxSnapshotStringBytes.


def _encode_native_metadata(value):
    from dee_thinking.persistence import encode_metadata
    return encode_metadata(value, max_bytes=MAX_NATIVE_METADATA_VALUE_BYTES)


def _preflight_task_record(m, event, tick):
    # Exact prospective task._record metadata, before its durable line append.
    line = {"index": m["log_count"], "tick": int(tick), **event}
    data = (json.dumps(line, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\\n").encode("utf-8")
    future = dict(m, log_count=m["log_count"]+1,
                  log_chain_sha256=sha(bytes.fromhex(m["log_chain_sha256"])+data))
    text = _encode_native_metadata(future)
    if len(text.encode("utf-8")) > MAX_NATIVE_METADATA_VALUE_BYTES:
        raise ValueError("Prospective task metadata exceeds frozen Native1MiB value bound; no journal append")
    return text


def _preserve_source_reference(device, source, payload):
    # Research/provenance artifact only. The participant never reads this file
    # to choose an action. Current full source and every old history item stay.
    data = _canonical(source); source_hash = sha(data)
    home = device.home / "FUENTES"
    home.mkdir(exist_ok=True)
    file = home / (source_hash + ".json")
    if file.exists():
        if not file.is_file() or file.is_symlink() or file.read_bytes() != data:
            raise ValueError("Preserved source artifact differs; no substitution")
    else:
        with file.open("xb") as out:
            out.write(data); out.flush(); os.fsync(out.fileno())
    first = source["first"]["numeric_reader"]
    second = source["second"]["numeric_reader"]
    return {"schema": "PI04.actual_native_source_reference.R02",
            "source_sha256": source_hash, "source_bytes": len(data),
            "source_archive": "FUENTES/" + source_hash + ".json",
            "actual_first": source["first"]["numeric_result"],
            "actual_final": source["second"]["numeric_result"],
            "first_reader": {"tick": first["tick"], "site": first["observation"]["site"],
                             "fixed_site_direction_valid": first["fixed_site_direction_valid"]},
            "second_reader": {"tick": second["tick"], "site": second["observation"]["site"],
                              "fixed_site_direction_valid": second["fixed_site_direction_valid"]},
            "payload_bytes": len(payload), "payload_sha256": sha(payload),
            "scope": "Deduplicated provenance, not an external cognitive memory/policy"}


def _validate_preserved_source_references(m, device):
    for item in m.get("resource_supply_history", []):
        if "source_ref" not in item:
            continue  # Frozen historical full sources remain literal.
        ref = item["source_ref"]; name = ref["source_sha256"]
        if len(name) != 64 or any(c not in "0123456789abcdef" for c in name):
            raise ValueError("Invalid bounded source reference hash")
        expected = "FUENTES/" + name + ".json"
        if ref["source_archive"] != expected:
            raise ValueError("Only the bounded provenance source artifact")
        file = device.home / "FUENTES" / (name + ".json")
        if not file.is_file() or file.is_symlink():
            raise ValueError("Missing preserved actual source provenance")
        data = file.read_bytes()
        if len(data) != ref["source_bytes"] or sha(data) != name:
            raise ValueError("Preserved actual source bytes changed")
        source = json.loads(data)
        if _canonical(source) != data or payload_from_actual_source(source) != source["second"]["numeric_result"].to_bytes(2,"little") + bytes(62):
            raise ValueError("Actual source archive violates its fixed codec")
        if source["first"]["numeric_result"] != ref["actual_first"] or source["second"]["numeric_result"] != ref["actual_final"]:
            raise ValueError("Actual source reference contents differ")


'''
if s.count(anchor)!=1:raise ValueError('Exact preflight source anchor required')
s=s.replace(anchor,helper+anchor+'    _validate_preserved_source_references(m, device)\n')
old='''    item = {**intent, "resources": additions, "source": source,
            "payload_sha256": sha(payload), "payload_bytes": len(payload),'''
new='''    source_ref = _preserve_source_reference(device, source, payload)
    item = {**intent, "resources": additions, "source_ref": source_ref,
            "payload_sha256": sha(payload), "payload_bytes": len(payload),'''
if s.count(old)!=1:raise ValueError('Exact new item source anchor required')
s=s.replace(old,new)
old='    commit_task({"kind": "EXPLICIT_SUPPLY_TASK_STAGED", "supply": item})'
new='    commit_task({"kind": "EXPLICIT_SUPPLY_TASK_STAGED", "supply": item, "full_source_provenance": source})'
if s.count(old)!=1:raise ValueError('Exact staged event anchor required')
s=s.replace(old,new)
old='''    def commit(event):
        task._record(a, m, directory, event)'''
new='''    def commit(event):
        _preflight_task_record(m, event, int(a.tick))
        task._record(a, m, directory, event)'''
if s.count(old)!=1:raise ValueError('Exact task commit anchor required')
s=s.replace(old,new)
ast.parse(s);dest=HERE/'pi03_suministro_explicito_R03.py'
if dest.exists():raise FileExistsError('Adapted source already exists')
dest.write_text(s,encoding='utf-8')
print(json.dumps({'source_sha256':expected,'adapted_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'new_native_ticks':0,'changes':['new metadata item references full source artifact by hash','old six items/current full source retained','new staged external journal carries full source','prospective1MiB preflight before task journal append']},ensure_ascii=False))
