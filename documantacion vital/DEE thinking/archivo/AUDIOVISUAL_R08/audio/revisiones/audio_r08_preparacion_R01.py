"""R08 local literal-anchor voice. No DEE, uploads, time stretch or phoneme trim.

The original R03 synthesizer/model/voice are read-only. Each complete model
waveform is saved. Subtitle timestamps derive from model phonemes, not words.
Root owns the production register and approves central evidence separately.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parents[1]
TESTS = next(p for p in ROOT.parents if p.name == 'tests')
VIDEOS = ROOT.parent / 'produccion_audiovisual_DEE_Cognitive_2_0_20261028/videos'
R03 = VIDEOS / 'produccion_cientifica/R03'
TTS = R03 / 'sintetizar_voz_r03.py'
VOICE_SOURCE = VIDEOS / 'produccion_cientifica/voz'
ALIAS = Path(tempfile.gettempdir()) / 'dee_r03_voice_312cdd7b'
SCRIPT = ROOT / 'guion_fuente/SHOTLIST_R08.json'
INDEX = ROOT / 'audio/PROVENIENCIA_AUDIO_R08.json'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def atomic_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.pending')
    temporary.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    temporary.replace(path)


def write_boundary():
    allowed = ROOT.resolve()
    def check(p):
        if isinstance(p, (str, bytes, os.PathLike)):
            resolved = Path(os.fsdecode(p)).resolve()
            if not resolved.is_relative_to(allowed):
                raise PermissionError('R08 audio write outside production root: ' + str(resolved))
    def audit(event, args):
        if event == 'open':
            path, mode, flags = args
            write = isinstance(mode, str) and any(c in mode for c in 'wax+')
            write = write or bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if write:
                check(path)
        elif event in ('os.mkdir', 'os.remove', 'os.rmdir'):
            check(args[0])
        elif event in ('os.rename', 'os.replace'):
            check(args[0]); check(args[1])
        elif event == 'socket.connect':
            raise PermissionError('R08 audio is offline')
    sys.addaudithook(audit)


def alias_readonly():
    if not ALIAS.is_junction() or ALIAS.resolve() != VOICE_SOURCE.resolve():
        raise RuntimeError('Approved read-only R03 alias absent or points elsewhere')
    return ALIAS


def setup():
    alias_readonly()
    temp = ROOT / 'audio/tmp'
    temp.mkdir(parents=True, exist_ok=True)
    for key in ('TMP', 'TEMP', 'TMPDIR'):
        os.environ[key] = str(temp)
    tempfile.tempdir = str(temp)
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', DO_NOT_TRACK='1')
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('_r08_readonly_approved_voice', TTS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.W = ROOT
    module.OUT = ROOT / 'audio/tomas'
    module.runtime_alias = alias_readonly
    module.PARAMS = deepcopy(module.PARAMS)
    module.PARAMS.update(speed=1.0)
    module.OUT.mkdir(parents=True, exist_ok=True)
    np, sf, synth, assets, runner, alias = module.setup()
    assert module.PARAMS['speed'] == 1.0
    assert module.PARAMS['voice'] == 'em_alex' and module.PARAMS['language'] == 'es-419'
    return module, np, sf, synth, assets, runner


def source():
    data = json.loads(SCRIPT.read_text(encoding='utf8'))
    assert len(data['scenes']) == 12
    assert sum(len(s['shots']) for s in data['scenes']) == 46
    for scene in data['scenes']:
        assert ' '.join(s['anchor_exact'] for s in scene['shots'] if s['anchor_exact']) == scene['literal']
        assert hashlib.sha256(scene['literal'].encode()).hexdigest() == scene['literal_sha256_utf8']
    return data


def subtitle_chunks(text):
    """Word-preserving segmentation only. Timing is aligned afterward."""
    result = []
    remaining = text
    while len(remaining) > 82 or len(textwrap.wrap(remaining, width=43, break_long_words=False, break_on_hyphens=False)) > 2:
        prefix = remaining[:83]
        punctuation = [m.end() for m in re.finditer(r'[,;:.!?]', prefix) if m.end() >= 30]
        cut = punctuation[-1] if punctuation else prefix.rfind(' ')
        assert cut > 0
        while len(textwrap.wrap(remaining[:cut], width=43, break_long_words=False, break_on_hyphens=False)) > 2:
            cut = remaining[:cut].rfind(' ')
            assert cut > 0
        result.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    if remaining:
        result.append(remaining)
    assert ' '.join(result) == text
    return result


def norm_phonemes(text):
    return ''.join(c for c in text if not c.isspace() and c not in '.,;:!?¿¡…—-"()[]{}')


def align_chunks(module, synthesizer, row):
    """Map literal subtitle chunks into emitted model phonemes.

    An unresolved boundary is reported, never replaced by a proportional
    character/word estimate. No audio is edited at these cue boundaries.
    """
    phonemes = row['phoneme_timings']
    normalized, indices = '', []
    for i, value in enumerate(phonemes):
        chars = norm_phonemes(value['phoneme'])
        normalized += chars
        indices.extend([i] * len(chars))
    chunks = subtitle_chunks(row['es'])
    result, cursor = [], 0
    for chunk in chunks:
        expected = norm_phonemes(synthesizer.tokenizer.known(synthesizer.tokenizer.phonemize(
            module.synthesis_text(chunk), lang=module.PARAMS['language'])))
        found = normalized.find(expected, cursor)
        match = 'exact_chunk_model_phonemes'
        matched = len(expected)
        if found < 0:
            for length in (48, 40, 32, 24, 20, 16, 12):
                prefix = expected[:length]
                if len(prefix) >= 12 and normalized.count(prefix, cursor) == 1:
                    found = normalized.find(prefix, cursor)
                    match = 'unique_model_phoneme_prefix_' + str(len(prefix))
                    matched = len(prefix)
                    break
        if found < 0:
            result.append({'literal': chunk, 'start': None, 'end': None,
                           'method': 'UNRESOLVED_NO_INVENTED_TIMESTAMP'})
            continue
        start = float(phonemes[indices[found]]['start'])
        end = float(phonemes[indices[found + matched - 1]]['end']) if match == 'exact_chunk_model_phonemes' else None
        result.append({'literal': chunk, 'start': start, 'end': end, 'method': match,
                       'model_phoneme_first_index': indices[found], 'matched_phoneme_chars': matched})
        cursor = found + matched
    for i, cue in enumerate(result):
        if cue['start'] is not None and cue['end'] is None:
            following = next((c['start'] for c in result[i+1:] if c['start'] is not None),
                             row['duration'] - module.PARAMS['trailing_silence_seconds'])
            cue['end'] = following
            cue['end_method'] = 'next_chunk_model_onset_or_complete_model_waveform_end'
    return result


def generate(scene_ids, pilot=False, approved=False):
    data = source()
    ids = set(scene_ids)
    assert ids <= {s['scene_id'] for s in data['scenes']}
    if ids & {'S01','S02','S03','S04'} and not approved:
        raise RuntimeError('Await VERIFICACION_CENTRAL_APROBADA before central production synthesis')
    if pilot and ids != {'S01'}:
        raise ValueError('Technical pilot is S01 only')
    module, np, sf, synthesizer, assets, runner = setup()
    if pilot:
        module.OUT = ROOT / 'audio/prueba_S01'
        module.OUT.mkdir(parents=True, exist_ok=True)
    old = json.loads(INDEX.read_text(encoding='utf8')) if INDEX.exists() else {}
    existing = {r['id']: r for r in old.get('takes', [])}
    selected = old.get('selected', {})
    provenance = {**old,'schema':'DEE.R08.literal_anchor_voice.R01',
                  'source_docx':data['source'], 'shotlist_sha256':sha(SCRIPT),
                  'voice_engine':'Kokoro ONNX0.6.1 CPU only', 'voice':'em_alex',
                  'language':'es-419', 'synthesis_speed':1.0,
                  'R03_runner':{'path':str(TTS),'sha256':sha(TTS)},
                  'audio_r08_source_sha256':sha(__file__), 'assets':assets,
                  'runner_files':runner, 'alias_read_only':str(ALIAS),
                  'no_time_stretch':True, 'complete_waveforms_retained':True,
                  'human_listening':False,'independent_ASR':False,
                  'Native_ticks':0,'private_text_uploaded':False,
                  'timing_scope':'Phoneme durations emitted by the same synthesis model; not independent ASR or listening.'}
    for scene in data['scenes']:
        if scene['scene_id'] not in ids:
            continue
        for shot in scene['shots']:
            literal = shot['anchor_exact']
            if literal is None:
                continue
            identifier = shot['shot_id'] + ('_prueba' if pilot else '_r1000')
            row = module.synthesize({'id':identifier,'es':literal}, np, sf, synthesizer,
                                    assets, runner, existing)
            row.update(scene_id=scene['scene_id'],shot_id=shot['shot_id'],
                       window=[shot['start_s'],shot['end_s']],
                       fit_margin_s=shot['duration_s']-row['duration'],
                       status='TECHNICAL_PILOT_NOT_FINAL' if pilot else 'GENERATED_LITERAL_ANCHOR',
                       subtitle_chunks=align_chunks(module,synthesizer,row))
            existing[identifier] = row
            if not pilot:
                selected[shot['shot_id']] = identifier
            provenance.update(takes=list(existing.values()),selected=selected,
                              updated_utc=dt.datetime.now(dt.timezone.utc).isoformat())
            atomic_json(INDEX,provenance)
            print('ANCHOR',json.dumps({'id':identifier,'duration_s':row['duration'],
                                       'model_speech_s':row['speech_block_seconds'],
                                       'window_s':shot['duration_s'],'margin_s':row['fit_margin_s'],
                                       'unresolved_subtitle_chunks':sum(c['start'] is None or c['end'] is None for c in row['subtitle_chunks'])}),flush=True)
    for filename, expected in module.EXPECTED_ASSETS.items():
        assert sha(VOICE_SOURCE/filename)==expected
    provenance['original_assets_reverified_unchanged']=True
    atomic_json(INDEX,provenance)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot-s01',action='store_true')
    parser.add_argument('--synthesize',action='store_true')
    parser.add_argument('--scene-ids',nargs='+')
    parser.add_argument('--central-approved',action='store_true')
    parser.add_argument('--describe',action='store_true')
    args=parser.parse_args()
    if args.describe:
        data=source()
        print(json.dumps({'scene_count':len(data['scenes']),'shot_count':sum(len(s['shots']) for s in data['scenes']),
                          'voice':'em_alex','speed':1.0,'Native_ticks':0,'await_central_approval':True}));return
    if args.pilot_s01==args.synthesize:
        parser.error('Choose --pilot-s01 or --synthesize')
    write_boundary()
    generate(['S01'] if args.pilot_s01 else args.scene_ids or [f'S{i:02d}' for i in range(1,13)],
             pilot=args.pilot_s01,approved=args.central_approved)


if __name__=='__main__':
    main()
