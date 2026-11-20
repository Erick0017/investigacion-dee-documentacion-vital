"""Locución editorial local R02 con la voz aprobada, sin ejecutar DEE.

Python 3.12 bundled. Los modelos y paquetes de la producción aprobada se leen
sin modificarlos. Cada unidad se sintetiza completa; los tiempos por frase
sirven para imagen/subtítulos, nunca para recortar el audio de voz.
"""
from __future__ import annotations

from pathlib import Path
import argparse
import dataclasses
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time

W = Path(__file__).resolve().parent
SOURCE = W.parent / 'voz'
OUT = W / 'voz'
MODEL = 'kokoro-v1.0.onnx'
VOICES = 'voices-v1.0.bin'
EXPECTED_ASSETS = {
    MODEL: 'beb0d1848dee9a49da392cc3df26958d46cfa35d321edf434f52949153f0df3a',
    VOICES: 'bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d',
}
PARAMS = {
    'engine': 'Kokoro ONNX0.6.1',
    'voice': 'em_alex',
    'language': 'es-419',
    'speed': 0.84,
    'continuous': True,
    'trim': False,
    'sentence_pause': 0.28,
    'clause_pause': 0.10,
    'leading_silence_seconds': 0.35,
    'trailing_silence_seconds': 0.60,
    'sample_rate': 24000,
    'PCM': 'PCM_24',
    'threading': {'intra_op': 3, 'inter_op': 1},
    'pronunciation_transduction': 'La palabra DEE se pronuncia de, e, e como en la base aprobada; el texto literal se conserva separado.',
    'runtime_loader_adapter': 'Conservar alias corto verificado para EspeakWrapper.data_path; sin cambios de modelo, vocabulario ni archivos de paquetes.',
}


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, value) -> None:
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    os.replace(temporary, path)


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def runtime_alias() -> Path:
    """Alias corto para las DLL cp312 que no admiten rutas canónicas largas.

    Es un vínculo temporal recreable, no una copia ni instalación. Nunca se
    elimina su destino. Si ya existe debe ser un junction al destino exacto.
    """
    if os.name != 'nt':
        return SOURCE
    alias = Path(tempfile.gettempdir()) / 'dee_r02_voice_312cdd7b'
    if alias.exists():
        if not alias.is_junction() or alias.resolve() != SOURCE.resolve():
            raise RuntimeError('El alias temporal existe y no es el vínculo propio esperado: ' + str(alias))
    else:
        command = ('New-Item -ItemType Junction -Path ' + ps_quote(str(alias))
                   + ' -Target ' + ps_quote(str(SOURCE)) + ' | Out-Null')
        subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', command],
                       check=True, timeout=30, capture_output=True, text=True)
        if not alias.is_junction() or alias.resolve() != SOURCE.resolve():
            raise RuntimeError('No se confirmó el destino exacto del vínculo temporal')
    # Se conserva el vínculo. No se borra nada de la producción original.
    return alias


def synthesis_text(text: str) -> str:
    return re.sub(r'\bDEE\b', 'de, e, e', text)


def split_sentences(text: str) -> list[str]:
    values = re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜ¿¡])', text)
    assert ' '.join(values) == text
    return values


def recipe(text: str, assets, runner) -> tuple[dict, str]:
    item = {'literal_es': text, 'synthesis_text': synthesis_text(text),
            'parameters': PARAMS, 'assets': assets, 'runner_files': runner}
    encoded = json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf8')
    return item, hashlib.sha256(encoded).hexdigest()


def setup():
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError('Utilice el Python 3.12 bundled de producción; no el runtime 3.13 de DEE.')
    assets = {}
    for filename, expected in EXPECTED_ASSETS.items():
        actual = sha(SOURCE / filename)
        assert actual == expected, (filename, actual, expected)
        assets[filename] = {'sha256': actual, 'bytes': (SOURCE / filename).stat().st_size}
    runner = {name: sha(SOURCE / 'pydeps' / 'kokoro_onnx' / name)
              for name in ('__init__.py', 'sliding.py', 'pauses.py', 'tokenizer.py')}
    alias = runtime_alias()
    # -B y esta bandera evitan escribir __pycache__ a través del alias.
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(alias / 'pydeps'))
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', DO_NOT_TRACK='1')
    import numpy as np
    import soundfile as sf
    import onnxruntime as ort
    from kokoro_onnx import Kokoro
    from phonemizer.backend import EspeakBackend
    from phonemizer.backend.espeak.wrapper import EspeakWrapper
    short_data_path = alias / 'pydeps' / 'espeakng_loader' / 'espeak-ng-data'
    assert short_data_path.resolve() == (SOURCE / 'pydeps' / 'espeakng_loader' / 'espeak-ng-data').resolve()
    assert (short_data_path / 'phontab').is_file()
    # El getter original hace .resolve() y devuelve la ruta larga al C stdio
    # de espeak, que no la admite. Sólo se mantiene aquí la ruta corta ya
    # verificada; la DLL, los datos y las reglas lingüísticas son los mismos.
    EspeakWrapper.data_path = property(lambda self: short_data_path)
    ort.disable_telemetry_events()
    options = ort.SessionOptions()
    options.intra_op_num_threads = PARAMS['threading']['intra_op']
    options.inter_op_num_threads = PARAMS['threading']['inter_op']
    session = ort.InferenceSession(str(alias / MODEL), sess_options=options, providers=['CPUExecutionProvider'])
    synthesizer = Kokoro.from_session(session, str(alias / VOICES))
    assert synthesizer.has_timings
    assert PARAMS['language'] in EspeakBackend.supported_languages()
    return np, sf, synthesizer, assets, runner, alias


def sentence_marks(synthesizer, text, phonemes, lead, end):
    """Alinea texto para rótulos. Conserva la incertidumbre si falla la marca.

    Los inicios provienen de las duraciones del modelo, no de una escucha ni
    reconocimiento independiente. La onda no se corta en estas posiciones.
    """
    normalized, indices = '', []
    for index, row in enumerate(phonemes):
        for char in row['phoneme']:
            if not char.isspace():
                normalized += char
                indices.append(index)
    sentences = split_sentences(text)
    marks, cursor = [], 0
    for sentence in sentences:
        expected = ''.join(synthesizer.tokenizer.known(synthesizer.tokenizer.phonemize(
            synthesis_text(sentence), lang=PARAMS['language'])).split())
        found = normalized.find(expected, cursor)
        method = 'exact_full_sentence_phonemes'
        matched_length = len(expected)
        if found < 0:
            for width in (40, 32, 24, 20, 16):
                candidate = expected[:width]
                if len(candidate) >= 12 and normalized.count(candidate, cursor) == 1:
                    found = normalized.find(candidate, cursor)
                    method = 'unique_phoneme_prefix_' + str(len(candidate))
                    matched_length = len(candidate)
                    break
        if found < 0:
            marks.append({'text': sentence, 'start': None, 'end': None,
                          'method': 'UNRESOLVED_NO_INVENTED_TIMESTAMP'})
            continue
        start = float(phonemes[indices[found]]['start']) + lead
        if method == 'exact_full_sentence_phonemes':
            stop = float(phonemes[indices[found + matched_length - 1]]['end']) + lead
        else:
            stop = None
        marks.append({'text': sentence, 'start': start, 'end': stop, 'method': method,
                      'phoneme_index': indices[found], 'phoneme_match_length': matched_length})
        cursor = found + matched_length
    for i, row in enumerate(marks):
        if row['start'] is not None and row['end'] is None:
            next_start = next((v['start'] for v in marks[i+1:] if v['start'] is not None), end)
            row['end'] = next_start
            row['end_method'] = 'next_sentence_start_or_complete_block_end'
    return marks


def synthesize(scene, np, sf, synthesizer, assets, runner, existing):
    identifier = scene['id']
    assert re.fullmatch(r'[A-Za-z0-9_-]{1,64}', identifier), identifier
    text = ' '.join(scene['es'].split())
    assert text and text == scene['es'], 'El guion debe entregar texto literal con espacios normalizados.'
    specification, recipe_sha = recipe(text, assets, runner)
    destination = OUT / (identifier + '.wav')
    if destination.exists():
        old = existing.get(identifier)
        if not old or old.get('recipe_sha256') != recipe_sha or old.get('wav_sha256') != sha(destination):
            raise RuntimeError('Audio existente sin caché verificable o con otro texto/parámetros: ' + str(destination))
        with destination.open('rb') as stream:
            a, sr = sf.read(stream, dtype='float32')
        assert len(a) == old['total_samples'] and sr == PARAMS['sample_rate']
        print('VOICE_CACHE_VERIFIED', identifier, old['duration'], flush=True)
        return old
    start_host = time.monotonic()
    voice, sr, timings = synthesizer.create_timed(
        specification['synthesis_text'], voice=PARAMS['voice'], speed=PARAMS['speed'],
        lang=PARAMS['language'], continuous=PARAMS['continuous'], trim=PARAMS['trim'],
        sentence_pause=PARAMS['sentence_pause'], clause_pause=PARAMS['clause_pause'])
    assert sr == PARAMS['sample_rate'] and voice.ndim == 1 and np.isfinite(voice).all()
    assert len(voice) > sr * 0.15 and float(np.max(np.abs(voice))) < 1.0
    before = round(PARAMS['leading_silence_seconds'] * sr)
    after = round(PARAMS['trailing_silence_seconds'] * sr)
    complete = np.concatenate([np.zeros(before, dtype=np.float32), voice,
                               np.zeros(after, dtype=np.float32)])
    temporary = destination.with_name(destination.stem + '.incomplete.wav')
    assert not temporary.exists(), 'Se conserva un audio previo incompleto; no se sobrescribe.'
    # Archivo Python abierto: evita MAX_PATH de libsndfile, sin acortar rutas
    # del proyecto ni copiar los recursos originales a otra instalación.
    with temporary.open('wb') as stream:
        sf.write(stream, complete, sr, subtype=PARAMS['PCM'], format='WAV')
    os.replace(temporary, destination)
    phonemes = [dataclasses.asdict(value) for value in timings]
    for row in phonemes:
        row['start'] += before / sr
        row['end'] += before / sr
    # sentence_marks agrega lead; recibe por ello los tiempos originales.
    original_phonemes = [dataclasses.asdict(value) for value in timings]
    sentences = sentence_marks(synthesizer, text, original_phonemes, before / sr,
                               (before + len(voice)) / sr)
    with destination.open('rb') as stream:
        check, check_sr = sf.read(stream, dtype='float32')
    assert check_sr == sr and len(check) == len(complete)
    assert np.count_nonzero(check[:before]) == 0 and np.count_nonzero(check[-after:]) == 0
    rms = float(np.sqrt(np.mean(voice.astype(float) ** 2)))
    peak = float(np.max(np.abs(voice)))
    edge_samples = max(1, round(sr * .02))
    return {
        'id': identifier, 'es': text, 'en': scene.get('en'), 'file': str(destination.relative_to(W)),
        'wav_sha256': sha(destination), 'recipe_sha256': recipe_sha, 'recipe': specification,
        'duration': len(complete) / sr, 'speech_block_seconds': len(voice) / sr,
        'sample_rate': sr, 'total_samples': len(complete), 'model_samples': len(voice),
        'leading_margin_samples': before, 'trailing_margin_samples': after,
        'complete_model_waveform_retained': True, 'audio_sentence_splices': 0,
        'no_audio_speed_change_after_synthesis': True, 'host_seconds': time.monotonic() - start_host,
        'words': len(text.split()), 'spoken_words_per_minute': len(text.split()) * 60 / (len(voice) / sr),
        'rms_dbfs': 20 * float(np.log10(max(1e-12, rms))),
        'peak_dbfs': 20 * float(np.log10(max(1e-12, peak))), 'clipped_samples': 0,
        'edge_diagnostic_only': {
            'first20ms_rms': float(np.sqrt(np.mean(voice[:edge_samples].astype(float) ** 2))),
            'last20ms_rms': float(np.sqrt(np.mean(voice[-edge_samples:].astype(float) ** 2))),
            'first_sample': float(voice[0]), 'last_sample': float(voice[-1]),
            'scope': 'Sólo diagnóstico; no acredita palabras completas ni naturalidad auditiva.'},
        'sentences': sentences, 'phoneme_timings': phonemes,
        'timing_scope': 'Duraciones del modelo; no alineación ASR independiente ni escucha.',
        'hearing_review': 'No realizada en este agente; no se afirma voz natural sin cortes a partir de métricas.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true', help='Una frase técnica corta, sin modificar el guion final')
    parser.add_argument('--all', action='store_true', help='Sintetizar escenas del guion_R02.json existente')
    parser.add_argument('--ids', nargs='*', help='Limitar a IDs de escena del guion')
    args = parser.parse_args()
    if not args.pilot and not args.all:
        parser.error('Indique --pilot o --all. No se genera voz de manera implícita.')
    OUT.mkdir(parents=True, exist_ok=True)
    if args.pilot:
        scenes = [{'id': 'ensayo_tecnico', 'es': 'La experiencia puede conservarse y utilizarse después.',
                   'en': 'Experience can be retained and used later.'}]
        index_path = OUT / 'ensayo_tecnico.json'
    else:
        script = read_json(W / 'guion_R02.json')
        scenes = script['scenes']
        assert len({scene['id'] for scene in scenes}) == len(scenes)
        if args.ids:
            assert set(args.ids) <= {scene['id'] for scene in scenes}
            scenes = [scene for scene in scenes if scene['id'] in args.ids]
        index_path = OUT / 'timings.json'
    old = read_json(index_path) if index_path.exists() else {}
    existing = {row['id']: row for row in old.get('scenes', [])}
    np, sf, synthesizer, assets, runner, alias = setup()
    index = {'schema': 'DEE.R02.voice.production.v1', 'parameters': PARAMS, 'assets_before': assets,
             'runner_files': runner, 'runtime_alias': str(alias), 'alias_target': str(SOURCE),
             'alias_is_recreatable_not_operational_source': True,
             'private_text_uploaded': False, 'new_DEE_ticks': 0,
             'audio_review_limitation': 'No se realizó escucha personal. Las comprobaciones automáticas no sustituyen esa revisión.',
             'scenes': list(existing.values()), 'completion': 'in_progress'}
    for scene in scenes:
        row = synthesize(scene, np, sf, synthesizer, assets, runner, existing)
        existing[row['id']] = row
        index['scenes'] = list(existing.values())
        atomic_json(index_path, index)
        print('VOICE_BLOCK_COMPLETE', row['id'], round(row['duration'], 3),
              'seconds', len(row['sentences']), 'sentence_marks', flush=True)
    for filename, expected in EXPECTED_ASSETS.items():
        actual = sha(SOURCE / filename)
        assert actual == expected
    index['assets_after'] = assets
    index['original_assets_unchanged'] = True
    index['completion'] = 'complete_selected_blocks'
    atomic_json(index_path, index)
    print('VOICE_COMPLETE', len(scenes), 'blocks;', str(index_path), flush=True)


if __name__ == '__main__':
    main()
