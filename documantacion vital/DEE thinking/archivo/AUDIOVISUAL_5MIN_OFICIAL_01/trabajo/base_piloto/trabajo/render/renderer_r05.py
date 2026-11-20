"""10-second pilot editable WebGL bridge: explicit models -> native 1920x1080 RGB frames.

No DEE import, no query, no native evolution, no inferred paths. This module
starts nothing on import. The owner explicitly closes its own browser worker.
"""
from __future__ import annotations
from pathlib import Path
import io
import json
import math
import numbers
import os
import re
import subprocess
from PIL import Image

HERE = Path(__file__).resolve().parent
WIDTH, HEIGHT, FPS, TOTAL_FRAMES = 1920, 1080, 30, 300
NODE = Path(r'C:\Users\Erik\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe')
PALETTE = {'background': '#07131D', 'input': '#46C7EB', 'teaching': '#F4C46B', 'history': '#B89BE8', 'output': '#E8F4F3'}
SCENE_SECONDS = (10,)
assert sum(SCENE_SECONDS) * FPS == TOTAL_FRAMES


def _plain(value):
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(v) for v in value]
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, numbers.Integral):
        return int(value)
    if isinstance(value, numbers.Real):
        return float(value)
    if hasattr(value, 'tolist'):
        return _plain(value.tolist())
    raise TypeError(f'Unsupported visualization value: {type(value).__name__}')


def camera_for_bounds(bounds, azimuth=-35, elevation=25, fov=42, fill=.80):
    """Fixed-axis perspective fit, no continuous orbit; Z is camera-up.

    Camera motion is editorial. No coordinates supplied by a source change.
    The lens shift places its target at (0.52W,0.43H), above the subtitle area.
    """
    lo, hi = [[float(x) for x in row] for row in bounds]
    center = [(a+b)/2 for a, b in zip(lo, hi)]
    az, el = math.radians(azimuth), math.radians(elevation)
    outward = [math.cos(el)*math.cos(az), math.cos(el)*math.sin(az), math.sin(el)]
    right = [-outward[1], outward[0], 0]
    n = math.hypot(*right)
    right = [v/n for v in right]
    up = [outward[1]*right[2]-outward[2]*right[1], outward[2]*right[0]-outward[0]*right[2], outward[0]*right[1]-outward[1]*right[0]]
    corners = [[x-center[0], y-center[1], z-center[2]] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
    dot = lambda a, b: sum(x*y for x, y in zip(a, b))
    tangent = math.tan(math.radians(fov)/2)
    distance = max(max(abs(dot(p, right))/(tangent*(WIDTH/HEIGHT)*fill), abs(dot(p, up))/(tangent*.66)) + dot(p, outward) for p in corners)
    distance = max(distance, 3.)
    return {'eye': [c+v*distance for c, v in zip(center, outward)], 'target': center, 'fov': fov, 'lens_shift': [.04, .14]}


def validate_model(model):
    model = _plain(model)
    camera = model.get('camera', {})
    for key in ('eye', 'target'):
        if not isinstance(camera.get(key), list) or len(camera[key]) != 3:
            raise ValueError(f'Explicit camera.{key}[3] required')
    all_labels = [row for key in ('labels', 'screen_labels') for row in model.get(key, [])]
    functional_labels = [row for row in all_labels if re.fullmatch(r'[\d\s+\-−=→/.,]+', str(row.get('text', ''))) is None]
    if len(all_labels) > 2:
        raise ValueError('Pilot permits at most two functional labels simultaneously; provenance is separate')
    words = sum(len(str(row.get('text', '')).split()) for row in functional_labels)
    if words > 8:
        raise ValueError(f'Pilot permits at most eight principal words per shot, got {words}')
    for particle in model.get('particles', []):
        if len(particle.get('position', [])) != 3:
            raise ValueError('Particle position must have three source coordinates')
        if particle.get('shape', 'sphere') not in ('sphere', 'cube'):
            raise ValueError('Admitted prepared meshes: sphere/cube')
    if model.get('provenance', {}).get('representation') not in ('Etapas',):
        raise ValueError('Every pilot frame must state Etapas')
    json.dumps(model, allow_nan=False)
    return model


class WebGLRenderer:
    def __init__(self):
        log_dir = HERE/'logs'
        log_dir.mkdir(exist_ok=True)
        self.log_path = log_dir/f'webgl_owner_{os.getpid()}.log'
        self._log = self.log_path.open('ab')
        self.process = subprocess.Popen([str(NODE), str(HERE/'render_common.cjs')], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=self._log, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        line = self.process.stdout.readline()
        if not line.startswith(b'INFO '):
            self.close()
            raise RuntimeError(f'WebGL worker failed during initialization; see {self.log_path}; {line!r}')
        self.info = json.loads(line[5:])
        self.info['node_worker_pid'] = self.process.pid
        self.info['source'] = str(HERE/'render_common.cjs')
        self.frame_count = 0

    def _read_exact(self, size):
        chunks = bytearray()
        while len(chunks) < size:
            block = self.process.stdout.read(size-len(chunks))
            if not block:
                raise EOFError(f'WebGL exporter closed early; see {self.log_path}')
            chunks.extend(block)
        return bytes(chunks)

    def render(self, model):
        model = validate_model(model)
        self.process.stdin.write((json.dumps({'op': 'render', 'model': model}, ensure_ascii=False, allow_nan=False, separators=(',', ':'))+'\n').encode('utf-8'))
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        if line.startswith(b'ERROR '):
            raise RuntimeError(json.loads(line[6:]))
        if not line.startswith(b'PNG '):
            raise RuntimeError(f'Invalid WebGL frame packet: {line!r}; see {self.log_path}')
        size = int(line[4:])
        if not 0 < size <= 32*1024*1024:
            raise ValueError('Unexpected visualization PNG size')
        data = self._read_exact(size)
        with Image.open(io.BytesIO(data)) as source:
            image = source.convert('RGB')
        if image.size != (WIDTH, HEIGHT):
            raise ValueError('WebGL output is not native 1920x1080')
        self.frame_count += 1
        return image

    def close(self):
        process = getattr(self, 'process', None)
        if process and process.poll() is None:
            try:
                process.stdin.write(b'{"op":"close"}\n')
                process.stdin.flush()
                process.stdin.close()
                process.wait(timeout=30)
            except (BrokenPipeError, OSError, subprocess.TimeoutExpired):
                process.terminate()  # Only this renderer's own Node child.
                process.wait(timeout=10)
        if getattr(self, '_log', None) and not self._log.closed:
            self._log.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


if __name__ == '__main__':
    import argparse
    import time
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probe', action='store_true')
    parser.add_argument('--frames', type=int, default=30)
    args = parser.parse_args()
    if not args.probe:
        parser.error('Use as an explicit rendering API, or --probe for a graphics-only test')
    model = {'camera': camera_for_bounds([[-8,-6,-2],[8,6,8]]), 'bounds':[[-8,-6,-2],[8,6,8]], 'grid':True,
             'particles':[{'position':[-4,0,2],'radius':1,'color':PALETTE['teaching']},{'position':[0,1,3],'radius':1.2,'color':PALETTE['history'],'shape':'cube'},{'position':[4,0,4],'radius':1,'color':PALETTE['input']}],
             'labels':[{'text':'Entrada','position':[4,0,4],'size':54}], 'provenance':{'representation':'Etapas','case':'Prueba gráfica, no evolución DEE'}}
    with WebGLRenderer() as renderer:
        start = time.monotonic()
        for i in range(args.frames):
            model['particles'][0]['position'][1] = -2+4*i/max(1,args.frames-1)
            image = renderer.render(model)
        elapsed = time.monotonic()-start
        preview = HERE/'previas'/'probe_escena_webgl_1080.png'
        preview.parent.mkdir(exist_ok=True)
        image.save(preview)
        print(json.dumps({'info': renderer.info, 'frames':args.frames,'host_seconds':elapsed,'fps':args.frames/elapsed,
                          'estimated_10800_seconds':10800*elapsed/args.frames,'preview':str(preview),'scope':'Graphics-only illustration benchmark, zero DEE execution'},ensure_ascii=False))
