"""Assemble approved R04 A/B only; source PCM/captions outside them is exact."""
from pathlib import Path
import argparse
import audioop
from copy import deepcopy
import hashlib
import json
import math
import re
import textwrap
import wave

W = Path(__file__).resolve().parents[1]
R03 = W.parent/'produccion_cientifica/R03'


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha(path):
    return sha_bytes(Path(path).read_bytes())


def read_wave(path):
    with wave.open(str(path), 'rb') as f:
        params, frames = f.getparams(), f.getnframes()
        value = f.readframes(frames)
    assert params.nchannels == 1 and params.sampwidth == 3 and params.framerate == 24000
    return params, value


def seconds(value):
    return round(value*24000)


def slice_pcm(value, start, end):
    return value[seconds(start)*3:seconds(end)*3]


def stamp(t):
    n = round(t*1000)
    return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'


def ass_stamp(t):
    n = round(t*100)
    return f'{n//3600000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'


def sentences(text):
    return re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜ¿¡])', text)


def caption_rows(es, en, marks, offset, lang):
    span_es, span_en = sentences(es), sentences(en)
    assert len(span_es) == len(span_en) == len(marks), (span_es, span_en, marks)
    rows = []
    for a, b, mark in zip(span_es, span_en, marks):
        assert a == mark['text'] and mark['start'] is not None and mark['end'] is not None
        text = a if lang == 'es' else b
        lines = textwrap.wrap(text, width=46, break_long_words=False, break_on_hyphens=False)
        groups = [lines[i:i+2] for i in range(0, len(lines), 2)]
        weights = [len(' '.join(g).split()) for g in groups]
        total, past = sum(weights), 0
        for group, weight in zip(groups, weights):
            length = mark['end']-mark['start']
            rows.append({'start': offset+mark['start']+length*past/total,
                         'end': offset+mark['start']+length*(past+weight)/total,
                         'lines': group, 'text': ' '.join(group)})
            past += weight
    assert ' '.join(x['text'] for x in rows) == ' '.join(span_es if lang == 'es' else span_en)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assemble', action='store_true')
    args = parser.parse_args()
    if not args.assemble:
        parser.error('Use explicit --assemble')
    source = R03/'voz/locucion_continua_R03.wav'
    source_sha = sha(source)
    params, pcm = read_wave(source)
    original = json.loads((R03/'timeline_R03.json').read_bytes())
    fragments = json.loads((W/'datos/audio_fragmentos_R04.json').read_bytes())
    fragment = {r['id']: r for r in fragments['fragments']}
    A, B = fragment['A_principal'], fragment['B_principal']
    _, a_pcm = read_wave(W/A['file'])
    _, b_pcm = read_wave(W/B['file'])
    assert A['duration'] <= 23.7 and B['duration'] < 36.4
    source_scene = next(s for s in original['scenes'] if s['id'] == 's03')
    original_sentences_es = sentences(source_scene['es'])
    original_sentences_en = sentences(source_scene['en'])
    _, s03_pcm = read_wave(R03/'voz/s03.wav')
    assert slice_pcm(pcm, 74.2, 74.2+len(s03_pcm)/72000) == s03_pcm

    # Root-authorized complete phrases: question -> literal B -> points/colors
    # plus movement. Cuts lie inside recorded sentence gaps, never words.
    question_bounds = [0.0, 2.52]
    labels_movement_bounds = [5.39, 13.64]
    question = slice_pcm(s03_pcm, *question_bounds)
    labels_movement = slice_pcm(s03_pcm, *labels_movement_bounds)
    q_duration = len(question)/72000
    b_start = q_duration
    labels_start = q_duration+B['duration']
    b_block = question+b_pcm+labels_movement
    b_duration = len(b_block)/72000
    assert b_duration <= 36.4
    b_marks = [dict(source_scene['marks'][0])]
    b_marks.extend({**m, 'start': m['start']+b_start, 'end': m['end']+b_start}
                   for m in B['sentences'])
    for i in (2, 3):
        m = source_scene['marks'][i]
        b_marks.append({**m, 'start': m['start']-labels_movement_bounds[0]+labels_start,
                        'end': m['end']-labels_movement_bounds[0]+labels_start})
    b_es = ' '.join([original_sentences_es[0], B['es'],
                     original_sentences_es[2], original_sentences_es[3]])
    b_en = ' '.join([original_sentences_en[0], B['en'],
                     original_sentences_en[2], original_sentences_en[3]])
    assert sentences(b_es) == [m['text'] for m in b_marks]
    destination = W/'audio/locucion_continua_R04.wav'
    if destination.exists():
        raise FileExistsError('Preserve an existing master; do not overwrite')
    master = bytearray(pcm)
    bounds_a = (seconds(0)*3, seconds(23.7)*3)
    bounds_b = (seconds(74.2)*3, seconds(110.6)*3)
    master[bounds_a[0]:bounds_a[1]] = a_pcm+bytes(bounds_a[1]-len(a_pcm))
    master[bounds_b[0]:bounds_b[1]] = b_block+bytes(bounds_b[1]-bounds_b[0]-len(b_block))
    master = bytes(master)
    assert len(master) == len(pcm)
    unchanged = []
    for lo, hi in ((23.7, 74.2), (110.6, len(pcm)/72000)):
        old, new = slice_pcm(pcm, lo, hi), slice_pcm(master, lo, hi)
        assert old == new
        unchanged.append({'start': lo, 'end': hi, 'PCM_bytes': len(old),
                          'source_PCM_sha256': sha_bytes(old),
                          'R04_PCM_sha256': sha_bytes(new), 'byte_identical': True})
    with wave.open(str(destination), 'wb') as f:
        f.setparams(params)
        f.writeframes(master)
    _, check = read_wave(destination)
    assert check == master
    timeline = deepcopy(original)
    replacements = {'s01': {'es': A['es'], 'en': A['en'], 'marks': A['sentences'],
                            'voice_duration': A['duration']},
                    's03': {'es': b_es, 'en': b_en, 'marks': b_marks,
                            'voice_duration': b_duration}}
    for s in timeline['scenes']:
        if s['id'] in replacements:
            s.update(replacements[s['id']])
            s['end_observation_pause'] = s['duration']-s['voice_duration']
    for lang in ('es', 'en'):
        retained = [deepcopy(c) for c in original['captions'][lang]
                    if not (0 <= c['start'] < 23.7 or 74.2 <= c['start'] < 110.6)]
        new = []
        for s in timeline['scenes']:
            if s['id'] in replacements:
                new += caption_rows(s['es'], s['en'], s['marks'], s['start'], lang)
        timeline['captions'][lang] = sorted(retained+new, key=lambda c: c['start'])
        assert all(len(c['lines']) <= 2 and c['start'] < c['end'] for c in timeline['captions'][lang])
        assert [c for c in timeline['captions'][lang] if c in retained] == retained
    assert round(timeline['duration']*30) == 12059
    srt = W/'DEE_Cognitive_2_0_Presentacion_R04_Concepto_y_Visual_EN.srt'
    srt.write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n'
                               +'\n'.join(c['lines'])
                               for i,c in enumerate(timeline['captions']['en']))+'\n', encoding='utf-8')
    source_ass = (R03/'subtitulos_R03_EN.ass').read_text(encoding='utf-8')
    header = source_ass.split('[Events]', 1)[0]+'[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
    ass = W/'subtitulos_R04_EN.ass'
    ass.write_text(header+'\n'.join('Dialogue: 0,'+ass_stamp(c['start'])+','+ass_stamp(c['end'])
                       +',Main,,0,0,0,,'+'\\N'.join(c['lines'])
                       for c in timeline['captions']['en'])+'\n', encoding='utf-8')
    seams = []
    for t in (74.2+q_duration, 74.2+labels_start):
        v = slice_pcm(master, t-.02, t+.02)
        seams.append({'time': t, 'RMS_40ms_dbfs': 20*math.log10(max(1, audioop.rms(v,3))/(2**23)),
                      'no_crossfade_or_syllable_overlap': True})
    timeline.update({'schema_R04_audio': 'DEE.R04.exact_A_B_edit.v1',
                     'source_R03_timeline_sha256': sha(R03/'timeline_R03.json'),
                     'source_R03_voice_sha256': source_sha,
                     'R04_voice': str(destination), 'R04_voice_sha256': sha(destination),
                     'unmodified_PCM_intervals': unchanged,
                     'replacement_A': {'variant': 'principal', 'duration': A['duration'], 'window': [0,23.7]},
                     'replacement_B': {'order': ['original_question', 'literal_B_principal', 'original_points_colors_and_movement'],
                                       'original_phrase_source_bounds': [question_bounds, labels_movement_bounds],
                                       'literal_B_start': 74.2+b_start,
                                       'original_labels_start': 74.2+labels_start,
                                       'voice_block_duration': b_duration,
                                       'visual_pause': 36.4-b_duration, 'window': [74.2,110.6]},
                     'wave_frames': len(master)//3, 'wave_sample_rate': 24000,
                     'video_frames_fixed': 12059, 'final_mix_requires_48000Hz': True,
                     'voice_speed_changed': False, 'C_modified': False,
                     'clipped_samples': 'PCM24 peak '+str(audioop.max(master,3))+' below '+str(2**23),
                     'seam_diagnostics': seams,
                     'listening_limitation': 'No personal auditory review by this agent; model timings and PCM checks are not listening.',
                     'new_DEE_ticks': 0})
    metadata = W/'datos/timeline_R04_audio.json'
    metadata.write_text(json.dumps(timeline, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    assert sha(source) == source_sha
    print(json.dumps({'voice': str(destination), 'voice_sha256': sha(destination),
                      'wave_duration': len(master)/72000, 'wave_frames': len(master)//3,
                      'A_duration': A['duration'], 'B_duration': b_duration,
                      'B_pause': 36.4-b_duration, 'SRT': str(srt), 'ASS': str(ass),
                      'timeline': str(metadata), 'PCM_outside_A_B_exact': True,
                      'English_cues': len(timeline['captions']['en']), 'seams': seams}, ensure_ascii=False))


if __name__ == '__main__':
    main()
