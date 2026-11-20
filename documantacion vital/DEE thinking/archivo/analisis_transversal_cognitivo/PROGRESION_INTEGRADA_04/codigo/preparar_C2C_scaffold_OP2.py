"""Prepare OP2 from the reviewed OP1 guard: fixed empty-device directories only.

This does not deploy, run Native, retry a failed future, alter a protocol or
regenerate a resource. The scientific VERSION and Native call order remain.
"""
from pathlib import Path
import ast
import hashlib
import json

P = Path(__file__).resolve().parents[1]
BASE = P / 'codigo/PI04_GUARDS_OPERATIVOS_CANDIDATOS/C2C_OP1/pi04_coordinacion_central_C2C.py'
OUT = P / 'codigo/PI04_C2C_SCAFFOLD_OP2'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def once(s, old, new):
    if s.count(old) != 1: raise ValueError('Exact OP1 source locator changed')
    return s.replace(old, new, 1)


METHOD = '''    def ensure_schema_directories(self):
        """P0 transport scaffold, only called at an explicit material boundary.

        All existing resources/products must already be intact. Only the seven
        fixed directory entries may be created; never a file, resource, state,
        snapshot, counter, memory, response or clock. Not autonomous recovery.
        """
        folders = ("reservoir", "inflight_minus", "inflight_plus", "inflight_silence", "consumed", "rejected", "products")
        if self.m.get("pending") or self.m.get("feedback_pending") or self.m.get("uncertain"):
            raise ValueError("No scaffold action on an unresolved device future")
        home = self.home.absolute()
        for node in (home, *home.parents):
            if node.is_symlink() or (node.exists() and getattr(node.lstat(), "st_file_attributes", 0) & 0x400):
                raise ValueError("No linked/reparse device scaffold")
        if not home.is_dir():
            raise ValueError("The original device/state must already exist")
        state = home / "ESTADO_DISPOSITIVO.json"
        state_hash = _sha(state.read_bytes())
        missing = []
        for name in folders:
            node = home / name
            if node.is_symlink() or (node.exists() and getattr(node.lstat(), "st_file_attributes", 0) & 0x400):
                raise ValueError("No linked/reparse fixed device directory")
            if node.exists():
                if not node.is_dir():
                    raise ValueError("A regular file occupies a fixed device directory")
            else:
                missing.append(name)
        resources = self.m.get("resources")
        ordinal = self.m.get("ordinal")
        if not isinstance(resources, list) or type(ordinal) is not int or not 0 <= ordinal <= len(resources):
            raise ValueError("The original finite resource state is required")
        for index, resource in enumerate(resources):
            if resource.get("name") != "%04d.resource" % index or type(resource.get("bytes")) is not int:
                raise ValueError("Only exact original resource filenames/sizes")
            locations = [home / folder / resource["name"] for folder in folders[:-1]]
            for file in locations:
                if file.is_symlink() or (file.exists() and getattr(file.lstat(), "st_file_attributes", 0) & 0x400):
                    raise ValueError("No linked/reparse resource")
            present = [file for file in locations if file.is_file()]
            if len(present) != 1 or present[0].stat().st_size != resource["bytes"] or _sha(present[0].read_bytes()) != resource["sha256"]:
                raise ValueError("Missing/altered/duplicated original resource; no regeneration")
            allowed = {"consumed", "rejected"} if index < ordinal else {"reservoir"}
            if present[0].parent.name not in allowed:
                raise ValueError("Resource placement disagrees with the closed device progress")
        products = self.m.get("products")
        if not isinstance(products, list):
            raise ValueError("Original products list is required")
        for product in products:
            relative = Path(product["path"])
            if relative.is_absolute() or len(relative.parts) != 2 or relative.parts[0] != "products" or relative.name in (".", ".."):
                raise ValueError("Only original local product filenames")
            file = home / relative
            if file.is_symlink() or (file.exists() and getattr(file.lstat(), "st_file_attributes", 0) & 0x400):
                raise ValueError("No linked/reparse product")
            if not file.is_file() or file.stat().st_size != product["bytes"] or _sha(file.read_bytes()) != product["sha256"]:
                raise ValueError("Missing/altered original product; no regeneration")
        # Validate every original file before the first mkdir. No exist_ok,
        # deletion, file write or counter adjustment masks a concurrent change.
        for name in missing:
            (home / name).mkdir()
        if _sha(state.read_bytes()) != state_hash:
            raise ValueError("Device state changed during scaffold preparation")
        return {"technical_revision": "C2C.OP2.fixed_device_directory_schema",
                "created_directories": missing, "fixed_directories": list(folders),
                "resource_files_verified": len(resources), "product_files_verified": len(products),
                "device_state_sha256_before": state_hash, "device_state_sha256_after": _sha(state.read_bytes()),
                "files_or_contents_recreated": False, "scope": "Prepared P0 transport scaffold, not learned regulation or repair"}

'''

EARLY = '''    schema_before = _physical(a)
    schema_preparation = device.ensure_schema_directories()
    schema_after = _physical(a)
    if schema_before != schema_after:
        raise RuntimeError("Technical directory preparation changed physical RAW/clocks/tick")
    schema_preparation.update({"physical_before":schema_before,"physical_after":schema_after,"new_native_ticks":0})
    if schema_preparation["created_directories"]:
        _record(a,m,directory,{"kind":"C2_DEVICE_DIRECTORY_SCHEMA_PREPARED_OP2","preparation":schema_preparation})
'''


def main():
    if OUT.exists(): raise ValueError('Preserve prior OP2 proposal')
    before = BASE.read_bytes()
    s = before.decode('utf-8-sig').replace('\r\n', '\n')
    original = s
    s = once(s, '    def save(self):\n        _atomic(self.home/"ESTADO_DISPOSITIVO.json", self.m)\n',
        METHOD + '    def save(self):\n        _atomic(self.home/"ESTADO_DISPOSITIVO.json", self.m)\n')
    marker = '        raise ValueError("Complete C2/device progress mismatch; no counter reset")\n    start=int(a.tick); banks=_banks(a)'
    s = once(s, marker, '        raise ValueError("Complete C2/device progress mismatch; no counter reset")\n' + EARLY + '    start=int(a.tick); banks=_banks(a)')
    s = once(s, '    action=device.begin(applied_route,operation,numeric,spec["context"],int(a.tick),ready)',
        '    physical_before_device_begin=_physical(a)  # Passive RAW/clocks witness for the preserved failed-import comparison.\n    action=device.begin(applied_route,operation,numeric,spec["context"],int(a.tick),ready)')
    old_result = '            "context_input_supplied":m["arm"] != "context_cut",\n'
    new_result = old_result + '            "technical_device_schema_preparation":schema_preparation,"physical_before_device_begin":physical_before_device_begin,\n'
    s = once(s, old_result, new_result)
    comment = '# Technical OP2 only: restore fixed empty filesystem scaffold at an explicit material boundary; never from read-only modes. Scientific VERSION/protocol/Native laws are unchanged.\n'
    s = once(s, 'VERSION = "PI04.C2C.single_current_early_Q_read_hold_q6.R01_DRAFT"', comment + 'VERSION = "PI04.C2C.single_current_early_Q_read_hold_q6.R01_DRAFT"')
    ast.parse(s)
    reverse = s.replace(comment, '', 1).replace(METHOD, '', 1).replace(EARLY, '', 1).replace(new_result, old_result, 1)
    reverse = reverse.replace('    physical_before_device_begin=_physical(a)  # Passive RAW/clocks witness for the preserved failed-import comparison.\n', '', 1)
    if reverse != original: raise ValueError('The technical patch changed another byte of the OP1 normalized source')
    OUT.mkdir()
    (OUT / 'pi04_coordinacion_central_C2C_ANTES_OP1.py').write_bytes(before)
    target = OUT / 'pi04_coordinacion_central_C2C.py'
    target.write_text(s, encoding='utf8', newline='')
    proof = {'schema':'PI04.C2C.technical_fixed_scaffold.OP2','status':'PREPARED_NOT_APPLIED',
        'base':str(BASE),'base_sha256':sha(BASE),'candidate':str(target),'candidate_sha256':sha(target),
        'Native_ticks':0,'source_S2_modified':False,'preserved_failed_future_retried':False,
        'scientific_VERSION_and_protocol_unchanged':True,'inverse_patch_equals_OP1_source':True,
        'scope':'Only Device.ensure_schema_directories plus an explicit material-boundary call and passive zero-tick/pre-device physical witnesses. No constructor/estado/dependency mkdir, resource regeneration, response/reader/codec/calendars or Native call changes.'}
    (OUT / 'PREPARACION_CANDIDATA_OP2.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(proof,ensure_ascii=False,indent=2))


if __name__ == '__main__': main()
