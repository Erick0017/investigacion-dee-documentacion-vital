"""Render exactly one pilot test PNG; never starts a 300-frame render."""
from pathlib import Path
import argparse
import hashlib
import json
import time
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from renderer_r05 import WebGLRenderer, WIDTH, HEIGHT, TOTAL_FRAMES
from modelos_piloto import test_model, stage_model, SOURCE_SHA256

HERE = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE/"prueba_encuentro_1080.png")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Preserve the existing test PNG")
    model = test_model()
    start = time.monotonic()
    with WebGLRenderer() as worker:
        image = worker.render(model)
        info = worker.info
    assert image.size == (WIDTH, HEIGHT)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    metadata = {
        "output": str(args.output),
        "PNG_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "size": list(image.size),
        "rendered_frames": 1,
        "configured_pilot_frames": TOTAL_FRAMES,
        "new_DEE_ticks": 0,
        "source_sha256": SOURCE_SHA256,
        "model": model,
        "available_material_cuts": [stage_model(t) for t in (205, 206, 210)],
        "renderer": info,
        "host_seconds": time.monotonic()-start,
        "full_pilot_not_rendered": True,
    }
    report = args.output.with_suffix(".json")
    if report.exists():
        raise FileExistsError(str(report))
    report.write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in metadata.items() if k not in ("model", "available_material_cuts")}, ensure_ascii=False))

if __name__ == "__main__":
    main()

