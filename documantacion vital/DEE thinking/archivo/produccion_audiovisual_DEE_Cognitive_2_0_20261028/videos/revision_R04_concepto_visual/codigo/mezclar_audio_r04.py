"""Two-pass R03-compatible local R04 mix. No new music or audio speed change."""
from pathlib import Path
import argparse
import audioop
import hashlib
import json
import re
import subprocess
import wave

W = Path(__file__).resolve().parents[1]
R03 = W.parent/'produccion_cientifica/R03'
ROOT = next(p for p in W.parents if p.name == 'DEE thinking')
TEST = ROOT.parent.parent
FF = TEST/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
PROBE = TEST/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
FRAMES = 19294400


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(4*1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def run(command):
    return subprocess.run(command, capture_output=True, text=True,
                          encoding='utf-8', errors='replace', check=True)


def norm_json(stderr):
    return json.loads(re.findall(r'\{\s*"input_i".*?\}', stderr, re.S)[-1])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mix', action='store_true')
    a = p.parse_args()
    if not a.mix:
        p.error('Use explicit --mix')
    voice = W/'audio/locucion_continua_R04.wav'
    ambient = R03/'voz/ambiente_R03.wav'
    original_voice = R03/'voz/locucion_continua_R03.wav'
    output = W/'audio/mezcla_R04_48k.wav'
    if output.exists():
        raise FileExistsError('Preserve the existing R04 mix')
    identity = {str(path): sha(path) for path in (voice, ambient, original_voice)}
    assert identity[str(voice)] == '066c076175b39a009960747391f27ad043e36d8d1cf7ac48d7e516b1a45b57e7'
    inputs = [str(FF), '-hide_banner', '-nostdin', '-threads', '3',
              '-filter_complex_threads', '2', '-i', str(voice), '-i', str(ambient)]
    base = '[0:a]aformat=channel_layouts=stereo[v];[v][1:a]amix=inputs=2:normalize=0,'
    first_filter = base+'loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json[a]'
    first = run(inputs+['-filter_complex', first_filter, '-map', '[a]', '-f', 'null', 'NUL'])
    measured = norm_json(first.stderr)
    norm = ('loudnorm=I=-16:TP=-1.5:LRA=9:'
            +'measured_I='+measured['input_i']+':measured_TP='+measured['input_tp']
            +':measured_LRA='+measured['input_lra']+':measured_thresh='+measured['input_thresh']
            +':offset='+measured['target_offset']+':linear=true:print_format=json')
    second_filter = base+norm+',aresample=48000,atrim=end_sample='+str(FRAMES)+'[a]'
    command = inputs+['-n', '-filter_complex', second_filter, '-map', '[a]',
                      '-c:a', 'pcm_s24le', '-ar', '48000', '-ac', '2', str(output)]
    second = run(command)
    exported = norm_json(second.stderr)
    with wave.open(str(output), 'rb') as f:
        params = f.getparams()
        assert params.framerate == 48000 and params.nchannels == 2 and params.sampwidth == 3
        assert f.getnframes() == FRAMES
        peak = 0
        for chunk in iter(lambda: f.readframes(1000000), b''):
            peak = max(peak, audioop.max(chunk, 3))
    assert peak < 2**23
    # Probe/read the completed mix only, no edits or new generation.
    probe = json.loads(run([str(PROBE), '-v', 'error', '-show_streams',
                            '-show_format', '-of', 'json', str(output)]).stdout)
    for path, expected in identity.items():
        assert sha(path) == expected, 'An input changed while mixing: '+path
    metadata = W/'datos/audio_fragmentos_R04.json'
    record = json.loads(metadata.read_bytes())
    record['mix'] = {'file': str(output), 'bytes': output.stat().st_size,
                     'sha256': sha(output), 'sample_rate': 48000, 'channels': 2,
                     'PCM': 'pcm_s24le', 'sample_frames': FRAMES,
                     'duration_exact_fraction': str(FRAMES)+'/48000',
                     'duration_seconds': FRAMES/48000, 'source_sha256': identity,
                     'first_pass_measurement': measured, 'second_pass_export': exported,
                     'target': {'integrated_LUFS': -16, 'true_peak_ceiling_dBTP': -1.5, 'LRA': 9},
                     'filters': [first_filter, second_filter],
                     'final_probe': probe, 'PCM_peak_absolute': peak,
                     'integer_clipping_observed': False, 'voice_atempo_or_stretch': False,
                     'new_music_generated': False, 'ambient_original_reused': True,
                     'original_WAVs_unchanged': True,
                     'listening': 'No auditory review certified; two-pass and peak checks are instrumental.'}
    temporary = metadata.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    temporary.replace(metadata)
    print(json.dumps({'mix': str(output), 'sha256': sha(output), 'bytes': output.stat().st_size,
                      'sample_frames': FRAMES, 'sample_rate': 48000, 'duration': FRAMES/48000,
                      'measurement': measured, 'export': exported, 'peak': peak,
                      'originals_unchanged': True}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
