"""Decode a bounded sample from already sealed clips; no producer or DEE import."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
TESTS = next(p for p in HERE.parents if p.name == 'tests')
FFMPEG = TESTS / '_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    previews = json.loads((WORK/'PREVISUALIZACION.json').read_text(encoding='utf-8'))
    scenes = json.loads((WORK/'audio/guion.json').read_text(encoding='utf-8'))['blocks']
    rows = []
    for number in [4, 6, 7, 8, 9]:
        scene = next(s for s in scenes if s['block'] == number)
        sid = f'S{number:02d}'
        clip, seal = WORK/'clips'/f'{sid}.mp4', WORK/'clips'/f'{sid}.json'
        if not seal.is_file():
            continue
        metadata = json.loads(seal.read_text(encoding='utf-8'))
        assert sha(clip) == metadata['sha256'], clip
        chosen = [r for r in previews if r['shot'].startswith(sid+'_')]
        frames = [round((r['time']-scene['start_s'])*30) for r in chosen]
        assert len(set(frames)) == len(frames)
        target = HERE / 'R01'
        target.mkdir(exist_ok=True)
        paths = [target/f'{sid}_{i+1:03d}.png' for i in range(len(frames))]
        assert not any(p.exists() for p in paths), 'Do not overwrite an earlier extraction'
        select = '+'.join(f'eq(n\\,{frame})' for frame in frames)
        command = [str(FFMPEG), '-hide_banner', '-loglevel', 'error', '-threads', '1',
                   '-i', str(clip), '-vf', 'select='+select, '-vsync', '0',
                   '-frames:v', str(len(frames)), '-threads', '1', str(target/f'{sid}_%03d.png')]
        run = subprocess.run(command, capture_output=True, text=True)
        if run.returncode:
            raise RuntimeError(run.stderr)
        for f, p, original in zip(frames, paths, chosen):
            assert p.is_file()
            rows.append(dict(scene=sid, clip=str(clip), clip_sha256=metadata['sha256'],
                             seal_sha256=sha(seal), sample_frame=f,
                             clip_seconds=f/30, montage_seconds=scene['start_s']+f/30,
                             shot=original['shot'], case_ids=original['case_ids'],
                             classification=original['classification'],
                             path=str(p), image_sha256=sha(p)))
    output = HERE/'MUESTRAS_R01.json'
    assert not output.exists()
    output.write_text(json.dumps(dict(new_DEE_ticks=0, samples=rows), ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(dict(samples=len(rows), scenes=sorted(set(r['scene'] for r in rows)),
                          index=str(output), sha256=sha(output)), ensure_ascii=False))


if __name__ == '__main__':
    main()
