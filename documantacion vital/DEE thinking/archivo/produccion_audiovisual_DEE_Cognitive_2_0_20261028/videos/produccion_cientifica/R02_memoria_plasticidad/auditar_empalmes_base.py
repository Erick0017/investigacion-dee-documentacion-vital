"""Lectura reproducible de los empalmes de voz de la película aprobada.

No escucha ni reconoce palabras. No modifica WAV, metadatos, montaje o DEE.
extract() devuelve el diagnóstico para el único CONTROL_R02 gestionado por
el montador; ejecutado directamente sólo imprime ese dict como JSON.
"""
from pathlib import Path
import hashlib
import json
import math
import wave

W = Path(__file__).resolve().parent
BASE = W.parent
VOICE = BASE / 'voz'
BASE_MP4 = BASE.parent / 'DEE_Cognitive_2_0_Presentacion_Cientifica_Profesional_1080p.mp4'
EXPECTED_BASE_SHA = '312cdd7b58f951e61ef75a8ad3bfc6244e3d3f5b34d3ad82dff36b8095d03f14'
THRESHOLD_AMPLITUDE = .01
WINDOW_SECONDS = .015


def sha(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def decode_pcm24(raw):
    assert len(raw) % 3 == 0
    result = []
    for i in range(0, len(raw), 3):
        value = raw[i] | (raw[i + 1] << 8) | (raw[i + 2] << 16)
        if value & (1 << 23):
            value -= 1 << 24
        result.append(value / (1 << 23))
    return result


def rms(samples):
    return math.sqrt(sum(value * value for value in samples) / len(samples))


def extract():
    base_sha = sha(BASE_MP4)
    assert base_sha == EXPECTED_BASE_SHA, 'No es la película base aprobada.'
    narration_path = VOICE / 'narraciones.json'
    timeline_path = BASE / 'timeline.json'
    code_path = BASE / 'pelicula.py'
    narrations = read_json(narration_path)
    timeline = read_json(timeline_path)
    code = code_path.read_text(encoding='utf-8-sig')
    assert 'pcm.extend(audio)' in code and 'pcm.extend(bytes(round(pad*pr.framerate)' in code
    timed = {(row['scene'], row['sentence']): row for row in timeline['voice']}
    assert len(timed) == len(narrations['sentences'])
    rows = []
    for record in narrations['sentences']:
        # Los metadatos sellados conservan la ubicación histórica. El traslado
        # archivó la unidad completa: se resuelve únicamente su basename actual.
        path = VOICE / 'oraciones' / Path(record['path']).name
        actual_sha = sha(path)
        assert actual_sha == record['sha256'], (path, actual_sha)
        with path.open('rb') as stream:
            with wave.open(stream, 'rb') as audio:
                params = audio.getparams()
                assert params.nchannels == 1 and params.sampwidth == 3
                count = min(params.nframes, round(WINDOW_SECONDS * params.framerate))
                first = decode_pcm24(audio.readframes(count))
                audio.setpos(params.nframes - count)
                last = decode_pcm24(audio.readframes(count))
        item = timed[(record['scene'], record['sentence'])]
        first_value, last_value = first[0], last[-1]
        endpoint = max(abs(first_value), abs(last_value))
        rows.append({
            'scene': record['scene'], 'sentence': record['sentence'], 'text': record['text'],
            'source_path': str(path), 'source_sha256': actual_sha,
            'source_model_scene': Path(record['source_scene']).name,
            'source_sample_start': record['sample_start'], 'source_sample_end': record['sample_end'],
            'sample_rate': params.framerate, 'sample_width_bytes': params.sampwidth,
            'samples': params.nframes, 'duration_seconds': params.nframes / params.framerate,
            'movie_voice_start': item['start'], 'movie_voice_end': item['end'],
            'first_sample': first_value, 'last_sample': last_value,
            'first15ms_RMS': rms(first), 'last15ms_RMS': rms(last),
            'max_abs_endpoint': endpoint,
            'endpoint_above_0_01': endpoint > THRESHOLD_AMPLITUDE,
            'max_endpoint_dBFS': 20 * math.log10(max(endpoint, 1e-12)),
        })
    joins = []
    for before, after in zip(rows, rows[1:]):
        if before['scene'] != after['scene']:
            continue
        joins.append({
            'scene': before['scene'], 'before_sentence': before['sentence'],
            'after_sentence': after['sentence'],
            'source_boundary_sample': before['source_sample_end'],
            'piece_end_in_movie': before['movie_voice_end'],
            'next_piece_start_in_movie': after['movie_voice_start'],
            'inserted_zero_seconds': after['movie_voice_start'] - before['movie_voice_end'],
            'last_sample_before_inserted_zero': before['last_sample'],
            'first_sample_after_inserted_zero': after['first_sample'],
            'either_boundary_above_0_01': max(abs(before['last_sample']), abs(after['first_sample'])) > THRESHOLD_AMPLITUDE,
        })
    scene_ids = sorted({row['scene'] for row in rows})
    assert len(rows) == 45 and len(scene_ids) == 8 and len(joins) == 37
    return {
        'schema': 'DEE.R02.audit.original_voice_splices.v1',
        'method': 'PCM24 exacto de las 45 piezas, extremos y RMS de ventanas de15ms; fronteras cruzadas con timeline y código del montaje aprobado.',
        'sources': {
            'base_mp4': {'path': str(BASE_MP4), 'sha256': base_sha},
            'narrations': {'path': str(narration_path), 'sha256': sha(narration_path)},
            'timeline': {'path': str(timeline_path), 'sha256': sha(timeline_path)},
            'montage_code': {'path': str(code_path), 'sha256': sha(code_path),
                             'locator': 'plan(): pcm.extend(audio); pad=.45; escena3 pad1.8 en frases seleccionadas; pcm.extend(bytes(...pad...))'},
        },
        'voice': narrations['voice'], 'language': narrations['language'],
        'piece_count': len(rows), 'scene_count': len(scene_ids),
        'internal_sentence_joins': len(joins),
        'pieces_with_any_endpoint_above_threshold': sum(row['endpoint_above_0_01'] for row in rows),
        'joins_with_either_boundary_above_threshold': sum(row['either_boundary_above_0_01'] for row in joins),
        'threshold_linear_amplitude': THRESHOLD_AMPLITUDE,
        'threshold_dBFS': 20 * math.log10(THRESHOLD_AMPLITUDE),
        'RMS_window_seconds': WINDOW_SECONDS,
        'spoken_source_seconds': sum(row['duration_seconds'] for row in rows),
        'rows': rows, 'joins': joins,
        'conclusion_scope': 'El montaje introduce silencios entre muestras de audio activo en numerosos empalmes. Se identifica un riesgo objetivo de discontinuidad; no acredita por sí solo que una palabra esté incompleta ni su causa perceptiva.',
        'personal_hearing_review': False, 'independent_ASR_review': False,
        'new_DEE_ticks': 0, 'originals_modified': False, 'files_written_by_extract': 0,
    }


if __name__ == '__main__':
    print(json.dumps(extract(), ensure_ascii=False, indent=2))
