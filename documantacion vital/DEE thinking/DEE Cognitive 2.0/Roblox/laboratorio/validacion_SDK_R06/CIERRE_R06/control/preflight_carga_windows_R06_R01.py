"""Passive Windows loader-path preflight. No Native imports, Store or subprocesses."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

MAX_UTF16_UNITS = 240
REPARSE_POINT = 1024

def inspect_path(runtime_root, relative, label):
    item = Path(relative)
    if item.is_absolute() or not item.parts or ".." in item.parts:
        raise ValueError("CONTAINED_RELATIVE_PATH_REQUIRED")
    current = runtime_root
    for part in item.parts:
        current = current / part
        st = current.lstat()
        if current.is_symlink() or getattr(st, "st_file_attributes", 0) & REPARSE_POINT:
            raise ValueError("SYMLINK_OR_REPARSE_POINT_NOT_ACCEPTED")
    resolved = current.resolve(strict=True)
    if not resolved.is_relative_to(runtime_root) or not resolved.is_file():
        raise ValueError("CONTAINED_FILE_REQUIRED")
    units = len(str(resolved).encode("utf-16-le")) // 2
    return {"label": label, "relativePath": str(item), "utf16PathUnits": units,
            "sha256": hashlib.sha256(resolved.read_bytes()).hexdigest(),
            "blockedLongPath": units >= MAX_UTF16_UNITS}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", required=True, type=Path)
    parser.add_argument("--native-pyd", required=True)
    parser.add_argument("--python")
    parser.add_argument("--launcher")
    args = parser.parse_args()
    output = {"schema": "DEE.SDK.LoaderPathPreflight.R06.R01",
              "nativeImported": False, "dllLoaded": False, "storeCreated": False,
              "identityPrepared": False, "httpRequested": False,
              "processLaunched": False, "materialReady": False, "ready": False,
              "loaderVerified": False, "maxUtf16UnitsExclusive": MAX_UTF16_UNITS,
              "shortRootExample": r"C:\DEE_SDK", "paths": []}
    try:
        raw_root = str(args.runtime_root)
        if raw_root.startswith("\\\\?\\"):
            raise ValueError("EXTENDED_PATH_PREFIX_IS_NOT_A_LOADER_FIX")
        absolute = args.runtime_root.absolute()
        current = Path(absolute.anchor)
        for part in absolute.parts[1:]:
            current = current / part
            st = current.lstat()
            if current.is_symlink() or getattr(st, "st_file_attributes", 0) & REPARSE_POINT:
                raise ValueError("LINKED_RUNTIME_ROOT_NOT_ACCEPTED")
        root = absolute.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("RUNTIME_DIRECTORY_REQUIRED")
        name = Path(args.native_pyd).name
        if not name.startswith("_native") or not name.lower().endswith(".pyd"):
            raise ValueError("EXPLICIT_NATIVE_PYD_REQUIRED")
        for label, value in (("NativePYD", args.native_pyd),
                             ("PrivatePython", args.python),
                             ("ActualLauncher", args.launcher)):
            if value:
                output["paths"].append(inspect_path(root, value, label))
        blocked = any(row["blockedLongPath"] for row in output["paths"])
        output["fsPrerequisitesSatisfied"] = not blocked
        output["blockedBeforeIdentityPreparation"] = blocked
        output["status"] = "BLOCKED_LONG_PATH_BEFORE_IDENTITY" if blocked else "FS_PATH_CHECK_CLEAR_LOADER_UNVERIFIED"
        output["nextStep"] = ("Deploy the complete authorized runtime to a short operational root and verify its manifest; do not prepare/import an identity here."
                              if blocked else "Only the path precondition passed. The owner must still perform the authorized real loader preflight. Finding a PYD does not prove material readiness.")
        code = 2 if blocked else 0
    except (OSError, ValueError) as exc:
        output.update(status="BLOCKED_FS_BEFORE_IDENTITY", fsPrerequisitesSatisfied=False,
                      blockedBeforeIdentityPreparation=True, errorCode=str(exc))
        code = 2
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return code

if __name__ == "__main__":
    sys.exit(main())
