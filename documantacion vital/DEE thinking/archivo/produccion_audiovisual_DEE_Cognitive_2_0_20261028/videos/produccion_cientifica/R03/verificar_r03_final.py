"""Comprobaciones técnicas del MP4 R03 cerrado; no ejecuta DEE ni modifica medios.

Uso: python verificar_r03_final.py
Los únicos escritos son qc/* y las secciones quality/final_export/completion del
REGISTRO_R03.json existente. Escucha y juicio visual humanos siguen pendientes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import statistics
import struct
import subprocess
import sys
import time
import traceback
import wave
from datetime import datetime, timezone
from fractions import Fraction

W = Path(__file__).resolve().parent
TEST = next(p for p in W.parents if (p / '_dee20_trabajo').is_dir())
FF = TEST / '_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
FP = TEST / '_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
FPS = 30
EXPECTED_FRAMES = 12059
EXPECTED_DURATION = EXPECTED_FRAMES / FPS
HUMAN = 'escucha humana pendiente'


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def utc():
    return datetime.now(timezone.utc).isoformat()


def normalized(text):
    return ' '.join(str(text).split())


class Validator:
    def __init__(self, main: Path, clean: Path):
        self.main, self.clean = main.resolve(), clean.resolve()
        self.start = utc()
        self.qc = W / 'qc' / ('final_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_' + str(os.getpid()))
        self.qc.mkdir(parents=True, exist_ok=False)
        self.results = {}
        self.commands = self.qc / 'commands.jsonl'
        self.timeline = load(W / 'timeline_R03.json')
        self.script = load(W / 'guion_R03.json')
        self.voice = load(W / 'voz/timings.json')
        self.original_registry = load(W / 'REGISTRO_R03.json')

    def command(self, name, argv, timeout=900):
        started = time.monotonic()
        p = subprocess.run([str(a) for a in argv], cwd=W, capture_output=True,
                           encoding='utf-8', errors='replace', timeout=timeout)
        (self.qc / (name + '.stdout.log')).write_text(p.stdout, encoding='utf-8')
        (self.qc / (name + '.stderr.log')).write_text(p.stderr, encoding='utf-8')
        record = {'name': name, 'argv': [str(a) for a in argv], 'returncode': p.returncode,
                  'elapsed_seconds': time.monotonic() - started,
                  'stdout': str(self.qc / (name + '.stdout.log')),
                  'stderr': str(self.qc / (name + '.stderr.log'))}
        with self.commands.open('a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        if p.returncode:
            raise RuntimeError(f'{name}: código {p.returncode}; {p.stderr[-2000:]}')
        return p

    def check(self, name, fn):
        try:
            value = fn()
            self.results[name] = {'ok': True, 'data': value}
            print(name + ': OK', flush=True)
        except Exception as e:
            self.results[name] = {'ok': False, 'error': str(e), 'traceback': traceback.format_exc()}
            print(name + ': FALLÓ: ' + str(e), flush=True)

    def timeline_check(self):
        scenes = self.timeline['scenes']
        assert len(scenes) == 11, len(scenes)
        assert self.timeline['fps'] == FPS
        assert sum(s['frames'] for s in scenes) == EXPECTED_FRAMES
        assert abs(self.timeline['duration'] - EXPECTED_DURATION) < 1e-8
        assert self.timeline.get('new_native_ticks') == 0
        assert self.timeline.get('audio_speed_change') is False
        assert [s['id'] for s in scenes] == [s['id'] for s in self.script['scenes']]
        previous = 0
        for s in scenes:
            assert abs(s['start'] - previous) < 1e-8
            assert abs((s['end'] - s['start']) - s['frames'] / FPS) < 1e-8
            assert s['voice_duration'] <= s['duration']
            previous = s['end']
        return {'scenes': len(scenes), 'frames': EXPECTED_FRAMES,
                'duration_seconds': EXPECTED_DURATION, 'new_native_ticks': 0}

    def probe(self, label, path):
        assert path.is_file(), str(path)
        p = self.command('probe_' + label, [FP, '-v', 'error', '-count_frames',
                         '-show_streams', '-show_format', '-of', 'json', path])
        d = json.loads(p.stdout)
        video = [s for s in d['streams'] if s['codec_type'] == 'video']
        audio = [s for s in d['streams'] if s['codec_type'] == 'audio']
        assert len(video) == len(audio) == 1, 'Se requiere un video y un audio'
        v, a = video[0], audio[0]
        assert (v['width'], v['height']) == (1920, 1080)
        assert v['codec_name'] == 'h264'
        assert v.get('pix_fmt') == 'yuv420p'
        assert v.get('sample_aspect_ratio') in ('1:1', '1/1'), v.get('sample_aspect_ratio')
        assert Fraction(v['r_frame_rate']) == Fraction(30, 1)
        assert Fraction(v['avg_frame_rate']) == Fraction(30, 1)
        assert int(v['nb_read_frames']) == EXPECTED_FRAMES, v.get('nb_read_frames')
        assert a['codec_name'] == 'aac'
        assert int(a['sample_rate']) == 48000
        assert int(a['channels']) == 2
        duration = float(d['format']['duration'])
        assert abs(duration - EXPECTED_DURATION) <= 1 / FPS + 1e-6, duration
        return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha(path),
                'format': d['format'], 'video': v, 'audio': a,
                'duration_tolerance_seconds': 1 / FPS}

    def decode(self):
        self.command('decode_main_entero', [FF, '-hide_banner', '-nostdin', '-v', 'error',
                     '-xerror', '-i', self.main, '-map', '0:v:0', '-map', '0:a:0',
                     '-f', 'null', 'NUL'])
        return {'scope': 'Flujos de video y audio completos del MP4 final; -xerror',
                'all_frames': EXPECTED_FRAMES, 'listened_by_human': False}

    def loudness(self):
        p = self.command('loudnorm_medicion', [FF, '-hide_banner', '-nostdin', '-i', self.main,
                         '-map', '0:a:0', '-vn', '-af',
                         'loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json', '-f', 'null', 'NUL'])
        candidates = re.findall(r'\{\s*"input_i".*?\}', p.stderr, re.S)
        assert candidates, 'No se encontró medición loudnorm'
        d = json.loads(candidates[-1])
        integrated, peak = float(d['input_i']), float(d['input_tp'])
        assert math.isfinite(integrated) and math.isfinite(peak)
        assert abs(integrated - (-16)) <= 1.5, integrated
        assert peak <= -1.0, peak
        return {'measurement': d, 'guard': {'integrated_LUFS': [-17.5, -14.5],
                'maximum_true_peak_dBTP': -1.0}, 'media_modified': False,
                'human_listening': HUMAN}

    def audio_identical(self):
        hashes = {}
        for label, path in [('main', self.main), ('clean', self.clean)]:
            p = self.command('aac_packets_' + label, [FF, '-v', 'error', '-nostdin',
                             '-i', path, '-map', '0:a:0', '-c:a', 'copy',
                             '-f', 'hash', '-hash', 'sha256', '-'])
            match = re.search(r'SHA256=([a-fA-F0-9]{64})', p.stdout)
            assert match, p.stdout
            hashes[label] = match.group(1).lower()
        assert hashes['main'] == hashes['clean'], hashes
        return {'compressed_audio_packet_payload_sha256': hashes,
                'scope': 'Hash del payload AAC copiado sin decodificar; no sólo duración'}

    def voice_pcm(self):
        out = W / 'voz/locucion_continua_R03.wav'
        mapping = {s['id']: s for s in self.voice['scenes']}
        rows = []
        with wave.open(str(out), 'rb') as combined:
            common = (combined.getnchannels(), combined.getsampwidth(), combined.getframerate())
            assert common[2] % FPS == 0
            total = 0
            for scene in self.timeline['scenes']:
                item = mapping[scene['id']]
                source = W / item['file']
                assert sha(source) == item['wav_sha256'], str(source)
                with wave.open(str(source), 'rb') as block:
                    params = (block.getnchannels(), block.getsampwidth(), block.getframerate())
                    assert params == common
                    n = block.getnframes()
                    assert n == item['total_samples']
                    assert item['complete_model_waveform_retained'] is True
                    assert item['no_audio_speed_change_after_synthesis'] is True
                    assert item['audio_sentence_splices'] == 0
                    assert n == item['model_samples'] + item['leading_margin_samples'] + item['trailing_margin_samples']
                    pcm = block.readframes(n)
                count = scene['frames'] * common[2] // FPS
                assert count >= n
                assert combined.readframes(n) == pcm, f"PCM alterado: {scene['id']}"
                pad = combined.readframes(count - n)
                assert len(pad) == (count - n) * common[0] * common[1]
                assert not any(pad), f"Padding no silencioso: {scene['id']}"
                rows.append({'id': scene['id'], 'source': str(source), 'sha256': item['wav_sha256'],
                             'source_samples': n, 'zero_padding_samples': count - n,
                             'source_PCM_byte_identical': True, 'source_model_waveform_uncut': True})
                total += count
            assert total == combined.getnframes()
            assert combined.readframes(1) == b''
        return {'file': str(out), 'sha256': sha(out), 'params': common,
                'total_samples': total, 'blocks': rows,
                'scope': 'Todos los PCM fuente se conservan íntegros y en orden, con pads cero; no evalúa pronunciación humana'}

    @staticmethod
    def srt_time(text):
        m = re.fullmatch(r'(\d+):(\d\d):(\d\d),(\d\d\d)', text.strip())
        assert m, text
        h, minute, second, ms = map(int, m.groups())
        return h * 3600 + minute * 60 + second + ms / 1000

    def subtitles(self):
        result = {}
        files = {'es': W / 'subtitulos_R03_ES.srt',
                 'en': W / 'DEE_Cognitive_2_0_Inteligencia_Funcional_R03_EN.srt'}
        for lang, path in files.items():
            content = path.read_text(encoding='utf-8-sig').replace('\r\n', '\n').strip()
            cues = []
            for index, block in enumerate(re.split(r'\n\s*\n', content), 1):
                lines = block.splitlines()
                assert int(lines[0]) == index
                start, end = [self.srt_time(x) for x in lines[1].split('-->')]
                textlines = lines[2:]
                assert 1 <= len(textlines) <= 2 and all(x.strip() for x in textlines)
                assert 0 <= start < end <= self.timeline['duration'] + .001
                if cues:
                    assert start >= cues[-1]['end'] - .001
                scenes = [s for s in self.timeline['scenes'] if start >= s['start'] - .001
                          and end <= s['start'] + s['voice_duration'] + .001]
                assert len(scenes) == 1, (index, start, end, 'fuera de voz')
                cues.append({'start': start, 'end': end, 'text': normalized(' '.join(textlines)),
                             'scene': scenes[0]['id']})
            expected = normalized(' '.join(s[lang] for s in self.script['scenes']))
            actual = normalized(' '.join(c['text'] for c in cues))
            assert actual == expected, f'Texto {lang} no es literal completo'
            references = self.timeline['captions'][lang]
            assert len(cues) == len(references)
            for cue, reference in zip(cues, references):
                assert cue['text'] == normalized(reference['text'])
                assert abs(cue['start'] - reference['start']) <= .0011
                assert abs(cue['end'] - reference['end']) <= .0011
            result[lang] = {'file': str(path), 'sha256': sha(path), 'cues': len(cues),
                            'literal_complete': True, 'maximum_lines': 2,
                            'inside_scene_voice': True, 'words': len(actual.split())}
        ass = W / 'subtitulos_R03_EN.ass'
        ass_text = ass.read_text(encoding='utf-8-sig')
        assert re.search(r'^PlayResX:\s*1920\s*$', ass_text, re.M)
        assert re.search(r'^PlayResY:\s*1080\s*$', ass_text, re.M)
        style = next(x for x in ass_text.splitlines() if x.startswith('Style: Main,'))
        style_values = style.split(',')
        assert style_values[2] == '60', 'Tamaño ASS distinto de la producción congelada'
        events = [line.split(',', 9) for line in ass_text.splitlines() if line.startswith('Dialogue:')]
        references = self.timeline['captions']['en']
        assert len(events) == len(references)
        def ass_time(value):
            h, minute, second = value.split(':')
            return int(h) * 3600 + int(minute) * 60 + float(second)
        for event, reference in zip(events, references):
            assert len(event) == 10
            assert len(event[9].split(r'\N')) <= 2
            assert normalized(event[9].replace(r'\N', ' ')) == normalized(reference['text'])
            assert abs(ass_time(event[1]) - reference['start']) <= .0051
            assert abs(ass_time(event[2]) - reference['end']) <= .0051
        result['burned_ASS_EN'] = {'file': str(ass), 'sha256': sha(ass),
                                  'cues': len(events), 'literal_complete': True,
                                  'PlayRes': [1920, 1080], 'font_size_EM': 60,
                                  'font_size_rationale': 'Segoe UI en libass usa tamaño EM; Fontsize46 produjo glifos visibles aproximadamente 25% menores que PIL46. Fontsize60 se ajustó mediante prueba real de quemado a 960x540, no mediante cambio del texto.',
                                  'reference_real_burn_proof': str(W / 'qc/ASS_REAL_60_s01_045_540.png'),
                                  'timestamp_quantization_seconds': .01}
        return result

    def protected_hashes(self):
        rows = []
        for item in self.original_registry['protected_originals']:
            path = Path(item['path'])
            actual = sha(path)
            assert actual == item['sha256'], str(path)
            if 'bytes' in item:
                assert path.stat().st_size == item['bytes']
            rows.append({'path': str(path), 'sha256': actual, 'unchanged': True})
        return {'scope': 'Sólo originales ya registrados; sin auditoría de carpetas', 'files': rows}

    def voice_assets(self):
        source = Path(self.voice['alias_target'])
        rows = []
        for name, item in self.voice['assets_before'].items():
            path = source / name
            actual = sha(path)
            assert actual == item['sha256']
            assert self.voice['assets_after'][name]['sha256'] == actual
            if 'bytes' in item:
                assert path.stat().st_size == item['bytes']
            rows.append({'path': str(path), 'sha256': actual, 'unchanged': True})
        for name, expected in self.voice['runner_files'].items():
            path = source / 'pydeps/kokoro_onnx' / name
            actual = sha(path)
            assert actual == expected
            rows.append({'path': str(path), 'sha256': actual, 'unchanged': True})
        assert self.voice.get('original_assets_unchanged') is True
        return rows

    def selected_frames(self):
        selected = {}
        def add(t, label):
            n = max(0, min(EXPECTED_FRAMES - 1, round(t * FPS)))
            selected.setdefault(n, []).append(label)
        add(0, 'inicio'); add((EXPECTED_FRAMES - 1) / FPS, 'último frame')
        scenes = self.timeline['scenes']
        by_id = {s['id']: s for s in scenes}
        for i, s in enumerate(scenes):
            marks = s['marks']
            mark = marks[len(marks) // 2]
            add(s['start'] + (mark['start'] + mark['end']) / 2, s['id'] + ': muestra con narración/subtítulos')
            if i:
                add(s['start'] - 1 / FPS, 'fin anterior a ' + s['id'])
                add(s['start'], 'inicio ' + s['id'])
        for sid, index, label in [('s02', 2, 'B2 petición'), ('s02', 3, 'B2 antes +1'),
                                  ('s02', 4, 'B2 enseñanza'), ('s02', 5, 'B2 después -1'),
                                  ('s02', 8, 'B2 comparación'), ('s02', 10, 'B2 conservado -1'),
                                  ('s04', 4, 'G07 primer resultado 23'),
                                  ('s04', 6, 'G07 segundo resultado 30'),
                                  ('s04', 9, 'G07 controles')]:
            s = by_id[sid]; m = s['marks'][index]
            add(s['start'] + (m['start'] + m['end']) / 2, label)
        s = by_id['s02']; m = s['marks'][9]
        for p, label in [(.1, 'B2 guardar'), (.4, 'B2 reabrir')]:
            following = s['marks'][10]['start']
            add(s['start'] + m['start'] + p * (following - m['start']), label)
        directory = W / 'qc/final_frames' / self.qc.name
        directory.mkdir(parents=True, exist_ok=False)
        indices = sorted(selected)
        expression = '+'.join(f'eq(n,{n})' for n in indices)
        rows = []
        for label, video in [('main', self.main), ('clean', self.clean)]:
            filters = f"[0:v]select='{expression}',split=2[n][s];[s]scale=960:540:flags=lanczos[h]"
            self.command('frames_' + label, [FF, '-hide_banner', '-v', 'error', '-nostdin',
                         '-i', video, '-filter_complex', filters,
                         '-map', '[n]', '-fps_mode', 'passthrough', '-frames:v', len(indices),
                         '-start_number', '0', '-threads', '1', directory / (label + '_1080_%03d.png'),
                         '-map', '[h]', '-fps_mode', 'passthrough', '-frames:v', len(indices),
                         '-start_number', '0', '-threads', '1', directory / (label + '_0540_%03d.png')])
            for order, n in enumerate(indices):
                for size, dimensions in [('1080', (1920, 1080)), ('0540', (960, 540))]:
                    path = directory / f'{label}_{size}_{order:03d}.png'
                    with path.open('rb') as f:
                        header = f.read(24)
                    assert header[:8] == b'\x89PNG\r\n\x1a\n'
                    assert struct.unpack('>II', header[16:24]) == dimensions
                    rows.append({'frame_index': n, 'seconds': n / FPS, 'labels': selected[n],
                                 'source': label, 'dimensions': dimensions, 'file': str(path),
                                 'sha256': sha(path)})
        return {'directory': str(directory), 'unique_times': len(indices),
                'scope': '11 escenas, límites, B2/G07, inicio/final; pares limpios y con subtítulos, 1080 y 540',
                'images': rows, 'human_visual_review': 'pendiente; los PNG son evidencia para inspección'}

    def sampled_ssim(self):
        samples = sorted({round(i * (EXPECTED_FRAMES - 1) / 29) for i in range(30)})
        expression = '+'.join(f'eq(n,{n})' for n in samples)
        stats_path = self.qc / 'ssim_30_frames.log'
        # cwd=W; ruta relativa evita el escape especial de ':' en rutas Windows.
        stats_relative = stats_path.relative_to(W).as_posix()
        chain = f"select='{expression}',crop=1920:880:0:0,settb=AVTB,setpts=N/(30*TB)"
        filt = f"[0:v]{chain}[a];[1:v]{chain}[b];[a][b]ssim=stats_file='{stats_relative}'[out]"
        self.command('ssim_30_frames', [FF, '-hide_banner', '-nostdin', '-i', self.main,
                     '-i', self.clean, '-filter_complex', filt, '-map', '[out]',
                     '-an', '-f', 'null', 'NUL'])
        text = stats_path.read_text(encoding='utf-8')
        values = [float(x) for x in re.findall(r'All:([0-9.]+)', text)]
        assert len(values) == 30, len(values)
        mean = statistics.fmean(values)
        assert mean >= .98, mean
        return {'metric': 'SSIM', 'frames': samples, 'n': len(values), 'mean': mean,
                'minimum': min(values), 'predefined_mean_guard': .98,
                'region': [0, 0, 1920, 880], 'stats_file': str(stats_path),
                'scope': 'Muestreo de imagen superior limpia frente a export final; excluye subtítulos añadidos. No VMAF ni garantía perceptiva de cada frame.'}

    def finish(self):
        # Recargar al final evita sustituir actualizaciones de montaje realizadas entretanto.
        path = W / 'REGISTRO_R03.json'
        registry = load(path)
        ok = bool(self.results) and all(row['ok'] for row in self.results.values())
        quality = registry.setdefault('quality', {})
        quality['final_validation'] = {'start_utc': self.start, 'end_utc': utc(),
            'validator': str(Path(__file__).resolve()), 'validator_sha256': sha(Path(__file__)),
            'checks': self.results, 'technical_checks_ok': ok, 'logs': str(self.qc),
            'human_listening': HUMAN,
            'limits': ['Las mediciones técnicas no sustituyen escucha humana.',
                       'Las extracciones se inspeccionan visualmente aparte; no hay validación automática de significado.',
                       'No se ejecutó DEE, Cognitive ni ningún experimento nativo.']}
        quality['human_listening'] = HUMAN
        final = {'path': str(self.main), 'exists': self.main.is_file(),
                 'validated_utc': utc(), 'technical_checks_ok': ok, 'human_listening': HUMAN}
        if self.main.is_file():
            final.update(bytes=self.main.stat().st_size, sha256=sha(self.main))
        if self.results.get('probe_main', {}).get('ok'):
            final['probe'] = self.results['probe_main']['data']
        registry['final_export'] = final
        registry['completion'] = ('TECHNICAL_CHECKS_COMPLETE_HUMAN_LISTENING_PENDING'
                                  if ok else 'TECHNICAL_VALIDATION_FAILED')
        temporary = path.with_name(path.name + '.' + str(os.getpid()) + '.tmp')
        temporary.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        os.replace(temporary, path)
        print(json.dumps(final, ensure_ascii=False, indent=2), flush=True)
        return 0 if ok else 1

    def run(self):
        self.check('timeline', self.timeline_check)
        self.check('probe_main', lambda: self.probe('main', self.main))
        self.check('probe_clean', lambda: self.probe('clean', self.clean))
        self.check('decode_AV_complete', self.decode)
        self.check('loudness', self.loudness)
        self.check('AAC_packets_equal', self.audio_identical)
        self.check('voice_PCM_complete', self.voice_pcm)
        self.check('subtitles_literal_complete', self.subtitles)
        self.check('protected_originals_unchanged', self.protected_hashes)
        self.check('voice_models_runner_unchanged', self.voice_assets)
        self.check('quality_frames_exported', self.selected_frames)
        self.check('sampled_SSIM', self.sampled_ssim)
        return self.finish()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--main', type=Path, default=W / 'DEE_Cognitive_2_0_Inteligencia_Funcional_R03_1080p.mp4')
    parser.add_argument('--clean', type=Path, default=W / 'montaje_limpio_R03.mp4')
    args = parser.parse_args()
    return Validator(args.main, args.clean).run()


if __name__ == '__main__':
    sys.exit(main())
