"""Build the R07 scene from the preserved R06 scene. No Studio/Native execution."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
R07 = HERE.parent
R06 = R07.parent / "revision_R06_INTEGRAL_V2"
SOURCE = R06 / "mundo" / "DEE_RBX01_INTEGRAL_V2_NATIVE.rbxlx"
OUTPUT = HERE / "DEE_RBX01_R07_NATIVE.rbxlx"
MANIFEST = HERE / "BUILD_WORLD_R07.json"
FILES = {
    "Config": "Config_R07.luau",
    "Body_C02": "Body_R07.luau",
    "WorldAPI_R07": "WorldAPI_R07.luau",
    "MotorPathfinding_R07": "MotorPathfinding_R07.luau",
    "RBX01Spectator": "Observador_R07.client.luau",
}
FP_RE = re.compile(r'(ScenarioFingerprint\s*=\s*")[0-9a-f]{64}("\s*[,;]?)')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def no_reparse(p: Path) -> None:
    """Reject a junction/symlink anywhere within the declared campaign trees."""
    for item in (p, *p.parents):
        if item.exists():
            st = item.lstat()
            if stat.S_ISLNK(st.st_mode) or getattr(st, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                raise ValueError(f"REPARSE_FORBIDDEN: {item}")
        if item == R07.parent:
            break


def get_name(item: ET.Element) -> str | None:
    prop = item.find("./Properties/string[@name='Name']")
    return prop.text if prop is not None else None


def get_source(item: ET.Element) -> ET.Element:
    props = item.find("Properties")
    if props is None:
        raise ValueError("ITEM_WITHOUT_PROPERTIES")
    source = props.find("ProtectedString[@name='Source']")
    if source is None:
        source = ET.SubElement(props, "ProtectedString", {"name": "Source"})
    return source


def named(root: ET.Element, name: str) -> ET.Element:
    hits = [item for item in root.iter("Item") if get_name(item) == name]
    if len(hits) != 1:
        raise ValueError(f"EXPECTED_ONE_ITEM: {name} found={len(hits)}")
    return hits[0]


def build() -> dict:
    for p in [SOURCE, HERE, *[HERE / n for n in FILES.values()]]:
        no_reparse(p)
    for p in (OUTPUT, MANIFEST):
        if p.exists():
            raise ValueError(f"DESTINATION_EXISTS_NO_OVERWRITE: {p}")
    source_bytes = SOURCE.read_bytes()
    source_sha = sha(source_bytes)
    texts = {key: (HERE / fname).read_text(encoding="utf-8-sig") for key, fname in FILES.items()}
    normalized, count = FP_RE.subn(lambda m: m[1] + "0" * 64 + m[2], texts["Config"])
    if count != 1:
        raise ValueError(f"CONFIG_FINGERPRINT_COUNT:{count}")
    semantic = {
        "schema": "DEE.R07.SceneFingerprint.v1",
        "world_id": "RBX01_CIERRE8_R07",
        "source_scene_sha256": source_sha,
        "source_native_tick": 991187,
        "source_world_completed": 28,
        "q1_codec": "products_v1",
        "q2_codec": "price_tag_v1",
        "config_without_fingerprint": normalized,
        "sources": {k: v for k, v in texts.items() if k != "Config"},
    }
    fingerprint = sha(json.dumps(semantic, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    config = FP_RE.sub(lambda m: m[1] + fingerprint + m[2], texts["Config"])
    texts["Config"] = config
    root = ET.fromstring(source_bytes)
    for name in ("Config", "Body_C02", "RBX01Spectator"):
        get_source(named(root, name)).text = texts[name]
    world_api = named(root, "WorldAPI_R06")
    world_api.find("./Properties/string[@name='Name']").text = "WorldAPI_R07"
    get_source(world_api).text = texts["WorldAPI_R07"]
    parents = {child: parent for parent in root.iter() for child in parent}
    module_parent = parents[world_api]
    if any(get_name(x) == "MotorPathfinding_R07" for x in root.iter("Item")):
        raise ValueError("MOTOR_ALREADY_PRESENT")
    module = ET.SubElement(module_parent, "Item", {"class": "ModuleScript", "referent": "RBX_R07_PATH_MOTOR"})
    props = ET.SubElement(module, "Properties")
    ET.SubElement(props, "string", {"name": "Name"}).text = "MotorPathfinding_R07"
    ET.SubElement(props, "ProtectedString", {"name": "Source"}).text = texts["MotorPathfinding_R07"]
    # The focal controller is called explicitly by the root executor. No automatic play loop.
    disabled = []
    for item in root.iter("Item"):
        if item.get("class") == "Script" and "Controller" in (get_name(item) or ""):
            prop = item.find("./Properties/bool[@name='Disabled']")
            if prop is None:
                prop = ET.SubElement(item.find("Properties"), "bool", {"name": "Disabled"})
            prop.text = "true"
            disabled.append(get_name(item))
    if not disabled:
        raise ValueError("NO_CONTROLLER_FOUND_TO_DISABLE")
    data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    # Pure XML re-open, not a Roblox execution.
    check = ET.fromstring(data)
    for name, text in texts.items():
        if get_source(named(check, name)).text != text:
            raise ValueError(f"SOURCE_REOPEN_MISMATCH:{name}")
    OUTPUT.write_bytes(data)
    # Keep the human-readable source and the scene source in agreement before the freeze.
    (HERE / FILES["Config"]).write_text(config, encoding="utf-8", newline="\n")
    if sha(SOURCE.read_bytes()) != source_sha:
        raise ValueError("PRESERVED_R06_SCENE_CHANGED_DURING_BUILD")
    manifest = {
        "schema": "DEE.R07.WorldBuild.v1",
        "world_id": "RBX01_CIERRE8_R07",
        "scenario_fingerprint": fingerprint,
        "source": {"path": str(SOURCE), "bytes": len(source_bytes), "sha256": source_sha, "after_sha256": source_sha},
        "output": {"path": str(OUTPUT), "bytes": len(data), "sha256": sha(data)},
        "source_files": [{"name": fname, "module_name": key, "sha256": sha((HERE / fname).read_bytes())} for key, fname in FILES.items()],
        "disabled_controllers": disabled,
        "verification": "XML sources and preserved R06 bytes checked. NO Studio, motor, Native or model execution.",
        "prepared_environment": "Common continuous floor and fixed obstacles created after restoring the complete parent World state.",
        "port_selection": "Fixed Native sign-to-port decoder; geometry-only Humanoid Pathfinding to that selected endpoint; no alternate destination policy.",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true", help="Create one new XML scene and manifest, refusing existing destinations.")
    args = parser.parse_args()
    if not args.build:
        parser.error("An explicit --build is required; this program never opens Studio or Native.")
    print(json.dumps(build(), ensure_ascii=False, indent=2))
