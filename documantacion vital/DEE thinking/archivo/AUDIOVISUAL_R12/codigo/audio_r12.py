"""R12 local literal-anchor voice. No DEE, uploads, time stretch or phoneme trim.

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
import subprocess
import sys
import tempfile
import textwrap
import wave

ROOT = Path(__file__).resolve().parents[1]
TESTS = next(p for p in ROOT.parents if p.name == 'tests')
VIDEOS = ROOT.parent / 'produccion_audiovisual_DEE_Cognitive_2_0_20261028/videos'
R03 = VIDEOS / 'produccion_cientifica/R03'
TTS = R03 / 'sintetizar_voz_r03.py'
VOICE_SOURCE = VIDEOS / 'produccion_cientifica/voz'
ALIAS = Path(tempfile.gettempdir()) / 'dee_r03_voice_312cdd7b'
SCRIPT = ROOT / 'guion_fuente/SHOTLIST_R12_DERIVADO_DEL_DOCX.json'
INDEX = ROOT / 'audio/PROVENIENCIA_AUDIO_R12.json'


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
                raise PermissionError('R12 audio write outside production root: ' + str(resolved))
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
            raise PermissionError('R12 audio is offline')
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
    spec = importlib.util.spec_from_file_location('_r12_readonly_approved_voice', TTS)
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
    assert len(data['scenes']) == 14
    assert sum(len(s['shots']) for s in data['scenes']) == 42
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
    # Espeak changes initial/allophonic consonants and stress when a subtitle
    # chunk is phonemized without its full preceding sentence. Canonicalize
    # those symbols for matching only; the waveform and recorded times remain
    # unchanged. We never infer a timestamp from text or a word count.
    mapping = {'ð':'d','β':'b','ɣ':'g','ˈ':'','ˌ':''}
    return ''.join(mapping.get(c,c) for c in text
                   if not c.isspace() and c not in '.,;:!?¿¡…—-"()[]{}')


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
        match = 'exact_chunk_canonical_model_phonemes'
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
        end = float(phonemes[indices[found + matched - 1]]['end']) if match == 'exact_chunk_canonical_model_phonemes' else None
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


def realign():
    """Recompute cues from stored phonemes; no new audio inference or edits."""
    module,np,sf,synth,assets,runner=setup()
    p=json.loads(INDEX.read_text(encoding='utf8'))
    for row in p['takes']:
        assert sha(ROOT/row['file'])==row['wav_sha256']
        row['subtitle_chunks']=align_chunks(module,synth,row)
    unresolved=[{'shot_id':r['shot_id'],'chunk':c['literal']} for r in p['takes']
                for c in r['subtitle_chunks'] if c['start'] is None or c['end'] is None]
    p['subtitle_realignment']={'source_sha256':sha(__file__),
       'method':'Stored model phoneme times; remove punctuation/stress and canonicalize context allophones d/ð,b/β,g/ɣ for matching only.',
       'no_audio_inference':True,'no_audio_files_changed':True,'unresolved':unresolved,
       'human_listening':False,'independent_ASR':False}
    atomic_json(INDEX,p)
    print('REALIGN',json.dumps({'takes':len(p['takes']),'cue_count':sum(len(r['subtitle_chunks']) for r in p['takes']),
                               'unresolved':unresolved}),flush=True)


def generate(scene_ids, pilot=False, approved=False):
    data = source()
    ids = set(scene_ids)
    assert ids <= {s['scene_id'] for s in data['scenes']}
    # Root authorized this exact DOCX-derived literal; scientific binding is separate.
    assert data['not_original_specification'] is True
    if pilot and ids != {'S01'}:
        raise ValueError('Technical pilot is S01 only')
    module, np, sf, synthesizer, assets, runner = setup()
    if pilot:
        module.OUT = ROOT / 'audio/prueba_S01'
        module.OUT.mkdir(parents=True, exist_ok=True)
    old = json.loads(INDEX.read_text(encoding='utf8')) if INDEX.exists() else {}
    existing = {r['id']: r for r in old.get('takes', [])}
    selected = old.get('selected', {})
    provenance = {**old,'schema':'DEE.R12.literal_anchor_voice.R01',
                  'source_docx':data['source'], 'shotlist_sha256':sha(SCRIPT),
                  'voice_engine':'Kokoro ONNX0.6.1 CPU only', 'voice':'em_alex',
                  'language':'es-419', 'synthesis_speed':1.0,
                  'R03_runner':{'path':str(TTS),'sha256':sha(TTS)},
                  'audio_r12_source_sha256':sha(__file__), 'assets':assets,
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
            former = existing.get(shot['shot_id'] + '_prueba') if not pilot else None
            if former:
                _, recipe_sha = module.recipe(literal, assets, runner)
                assert former['recipe_sha256'] == recipe_sha
                assert sha(ROOT/former['file']) == former['wav_sha256']
                row = deepcopy(former)
                identifier = row['id']
                row['origin_take_mode'] = 'APPROVED_TECHNICAL_S01_REUSED_WITH_IDENTICAL_PCM'
            else:
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


def plan_schedule(data, selected):
    """Bounded internal cuts in exact24k sample domain; never edits speech."""
    sr = 24000
    all_rows, violations = [], []
    for scene in data['scenes']:
        shots = scene['shots']
        nominal = [round(shots[0]['start_s']*sr)]+[round(s['end_s']*sr) for s in shots]
        minimum = [selected[s['shot_id']]['total_samples'] if s['anchor_exact'] else
                   round(s['duration_s']*sr) for s in shots]
        complete_minimum = list(minimum)
        if scene['scene_id']=='S14':
            minimum[-1] += 2*sr  # Final2s reading reserve; no trimming speech.
        low = [n-2*sr for n in nominal]
        high = [n+2*sr for n in nominal]
        low[0]=high[0]=nominal[0]; low[-1]=high[-1]=nominal[-1]
        # Explicit silent shots remain fixed; S14 also reserves its final2s.
        for i,s in enumerate(shots):
            if not s['anchor_exact']:
                low[i]=high[i]=nominal[i]
                low[i+1]=high[i+1]=nominal[i+1]
        earliest = [low[0]]
        for i,n in enumerate(minimum):
            earliest.append(max(low[i+1],earliest[-1]+n))
        latest = [None]*len(nominal);latest[-1]=high[-1]
        for i in range(len(minimum)-1,-1,-1):
            latest[i]=min(high[i],latest[i+1]-minimum[i])
        if any(a>b for a,b in zip(earliest,latest)):
            violations.append({'scene':scene['scene_id'],'kind':'NO_FIT_WITHIN_LITERAL_SCENE_AND_2S_CUT_LIMIT',
                               'minimum_complete_audio_s':sum(minimum)/sr,
                               'scene_s':scene['duration_s'],'earliest':earliest,'latest':latest})
            continue
        boundaries=[nominal[0]]
        for i in range(1,len(nominal)):
            permitted_low=max(low[i],boundaries[-1]+minimum[i-1])
            boundary=max(permitted_low,min(nominal[i],latest[i]))
            assert boundary<=latest[i]
            boundaries.append(boundary)
        for i,shot in enumerate(shots):
            all_rows.append({'scene_id':scene['scene_id'],'shot_id':shot['shot_id'],
                             'nominal_start_s':nominal[i]/sr,'nominal_end_s':nominal[i+1]/sr,
                             'actual_start_s':boundaries[i]/sr,'actual_end_s':boundaries[i+1]/sr,
                             'start_sample_24k':boundaries[i],'end_sample_24k':boundaries[i+1],
                             'first_visual_frame_30fps':(boundaries[i]*30+sr-1)//sr,
                             'end_visual_frame_exclusive_30fps':(boundaries[i+1]*30+sr-1)//sr,
                             'start_adjustment_s':(boundaries[i]-nominal[i])/sr,
                             'end_adjustment_s':(boundaries[i+1]-nominal[i+1])/sr,
                             'complete_voice_samples':complete_minimum[i] if shot['anchor_exact'] else 0,
                             'explicit_silence':not bool(shot['anchor_exact']),
                             'anchor_exact':shot['anchor_exact']})
    return {'schema':'DEE.R12.actual_anchor_schedule.R01','sample_rate':sr,
            'duration_s':390,'total_samples':390*sr,'rows':all_rows,
            'violations':violations,'all_fit':not violations,
            'method':'Complete waveforms retained; only internal editorial cuts moved by at most2s. Scene boundaries and final388..390 reading reserve fixed.'}


def timecode(t):
    ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


def inspect_or_assemble(assemble=False):
    data=source();p=json.loads(INDEX.read_text(encoding='utf8'))
    takes={r['id']:r for r in p['takes']}
    required={s['shot_id'] for c in data['scenes'] for s in c['shots'] if s['anchor_exact']}
    if set(p['selected'])!=required:
        raise RuntimeError('Not all42 literal voice anchors have an approved selected take')
    selected={sid:takes[tid] for sid,tid in p['selected'].items()}
    for row in selected.values():
        assert sha(ROOT/row['file'])==row['wav_sha256']
        assert row['recipe']['parameters']['speed']==1.0
    schedule=plan_schedule(data,selected)
    atomic_json(ROOT/'audio/TIEMPOS_ANCLAS_R12.json',schedule)
    print('SCHEDULE',json.dumps({'all_fit':schedule['all_fit'],'violations':schedule['violations'],
                               'adjustments':[{'shot_id':r['shot_id'],'start':r['start_adjustment_s'],
                                               'end':r['end_adjustment_s']} for r in schedule['rows']
                                              if r['start_adjustment_s'] or r['end_adjustment_s']]}),flush=True)
    if not assemble or not schedule['all_fit']:
        return
    unresolved=[{'shot':sid,'chunk':c} for sid,row in selected.items() for c in row['subtitle_chunks']
                if c['start'] is None or c['end'] is None]
    if unresolved:
        raise RuntimeError('Unresolved model subtitle boundaries; no invented timestamps: '+repr(unresolved))
    alias_readonly();sys.path.insert(0,str(ALIAS/'pydeps'))
    import numpy as np
    import soundfile as sf
    samples=np.zeros(390*24000,dtype=np.float32);captions=[]
    for sh in schedule['rows']:
        if sh['explicit_silence']:
            continue
        row=selected[sh['shot_id']]
        with (ROOT/row['file']).open('rb') as stream:
            audio,sr=sf.read(stream,dtype='float32')
        assert sr==24000 and len(audio)==row['total_samples']
        start=sh['start_sample_24k'];stop=start+len(audio)
        assert stop<=sh['end_sample_24k']
        assert not np.count_nonzero(samples[start:stop])
        samples[start:stop]=audio
        for i,cue in enumerate(row['subtitle_chunks']):
            next_start=row['subtitle_chunks'][i+1]['start'] if i+1<len(row['subtitle_chunks']) else row['duration']
            end=min(cue['end']+.12,next_start-.02,row['duration'])
            assert end>cue['start']
            wrapped=textwrap.wrap(cue['literal'],width=43,break_long_words=False,break_on_hyphens=False)
            assert len(wrapped)<=2
            captions.append({'scene_id':sh['scene_id'],'shot_id':sh['shot_id'],
                             'start':sh['actual_start_s']+cue['start'],'end':sh['actual_start_s']+end,
                             'literal':cue['literal'],'text':'\n'.join(wrapped),
                             'alignment':cue['method'],'phoneme_index':cue['model_phoneme_first_index']})
    for scene in data['scenes']:
        assert ' '.join(c['literal'] for c in captions if c['scene_id']==scene['scene_id'])==scene['literal']
    assert all(0<=c['start']<c['end']<=388 for c in captions)
    assert all(a['end']<=b['start'] for a,b in zip(captions,captions[1:]))
    target=ROOT/'audio/locucion_R12_24k.wav'
    if target.exists():
        raise RuntimeError('Existing master preserved; no implicit overwrite')
    with target.open('wb') as stream:
        sf.write(stream,samples,24000,subtype='PCM_24',format='WAV')
    with wave.open(str(target),'rb') as master:
        assert master.getnframes()==390*24000
        for sh in schedule['rows']:
            if sh['explicit_silence']:
                continue
            row=selected[sh['shot_id']]
            with wave.open(str(ROOT/row['file']),'rb') as take:
                pcm=take.readframes(take.getnframes())
            master.setpos(sh['start_sample_24k'])
            assert master.readframes(row['total_samples'])==pcm
    srt=ROOT/'audio/R12_ES.srt'
    srt.write_text('\n\n'.join(str(i)+'\n'+timecode(c['start'])+' --> '+timecode(c['end'])+'\n'+c['text']
                               for i,c in enumerate(captions,1))+'\n',encoding='utf-8-sig')
    atomic_json(ROOT/'audio/SUBTITULOS_ALINEADOS_R12.json',{'model_timing_not_ASR':True,'cues':captions})
    p['assembly']={'duration_s':390,'samples_24k':len(samples),'caption_count':len(captions),
                   'each_complete_take_PCM_exact_in_master':True,'no_time_stretch':True,
                   'schedule_sha256':sha(ROOT/'audio/TIEMPOS_ANCLAS_R12.json'),
                   'files':{str(f.relative_to(ROOT)):{'sha256':sha(f),'bytes':f.stat().st_size} for f in [target,srt]},
                   'human_listening':False,'independent_ASR':False}
    p['assembly']['source_sha256']=sha(__file__)
    atomic_json(INDEX,p)
    print('VOICE_MASTER',json.dumps(p['assembly']),flush=True)


def mix():
    """Voice-only two-pass48k stereo loudness normalization; no new music."""
    import audioop
    ff=TESTS/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
    p=json.loads(INDEX.read_text(encoding='utf8'))
    voice24=ROOT/'audio/locucion_R12_24k.wav'
    assert sha(voice24)==next(v for k,v in p['assembly']['files'].items() if Path(k).as_posix()=='audio/locucion_R12_24k.wav')['sha256']
    def run(args,log):
        result=subprocess.run([str(ff),'-hide_banner','-nostdin','-threads','3']+args,capture_output=True,text=True,encoding='utf8',errors='replace')
        (ROOT/'audio'/log).write_text(result.stdout+'\nSTDERR\n'+result.stderr,encoding='utf8')
        if result.returncode:raise RuntimeError('FFmpeg failed; '+log)
        return result
    def extract(stderr):return json.loads(re.findall(r'\{\s*"input_i".*?\}',stderr,re.S)[-1])
    v48=ROOT/'audio/locucion_R12_48k.wav';mix48=ROOT/'audio/mezcla_R12_48k.wav'
    if any(f.exists() for f in (v48,mix48)):raise RuntimeError('Existing48k assets preserved')
    run(['-n','-i',str(voice24),'-ar','48000','-ac','2','-c:a','pcm_s24le',str(v48)],'ffmpeg_voice48.log')
    measured=extract(run(['-i',str(v48),'-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','NUL'],'ffmpeg_loudnorm_pass1.log').stderr)
    normal=('loudnorm=I=-16:TP=-1.5:LRA=9:measured_I='+measured['input_i']+':measured_TP='+measured['input_tp']+':measured_LRA='+measured['input_lra']+':measured_thresh='+measured['input_thresh']+':offset='+measured['target_offset']+':linear=true:print_format=json')
    final=extract(run(['-n','-i',str(v48),'-af',normal+',aresample=48000,atrim=end_sample=18720000','-ar','48000','-ac','2','-c:a','pcm_s24le',str(mix48)],'ffmpeg_loudnorm_pass2.log').stderr)
    peak_values={}
    for f in (v48,mix48):
        with wave.open(str(f),'rb') as w:
            assert (w.getframerate(),w.getnchannels(),w.getsampwidth(),w.getnframes())==(48000,2,3,18720000)
            peak=0
            for b in iter(lambda:w.readframes(1000000),b''):peak=max(peak,audioop.max(b,3))
            assert peak<2**23-1;peak_values[str(f.relative_to(ROOT))]=peak
    p['mix']={'duration_s':390,'sample_rate':48000,'channels':2,'PCM':'PCM24','sample_frames':18720000,'normalization_target':{'I':-16,'TP':-1.5,'LRA':9},'first_pass':measured,'second_pass':final,'integer_peaks':peak_values,'music':None,'music_omitted_for_voice_clarity':True,'files':{str(f.relative_to(ROOT)):{'bytes':f.stat().st_size,'sha256':sha(f)} for f in(v48,mix48)},'FFmpeg':{'path':str(ff),'sha256':sha(ff)},'source_sha256':sha(__file__),'voice_time_stretch':False,'human_listening':False,'independent_ASR':False}
    atomic_json(INDEX,p);print('MIX',json.dumps(p['mix']),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot-s01',action='store_true')
    parser.add_argument('--synthesize',action='store_true')
    parser.add_argument('--scene-ids',nargs='+')
    parser.add_argument('--central-approved',action='store_true')
    parser.add_argument('--describe',action='store_true')
    parser.add_argument('--schedule',action='store_true')
    parser.add_argument('--assemble',action='store_true')
    parser.add_argument('--realign',action='store_true')
    parser.add_argument('--mix',action='store_true')
    args=parser.parse_args()
    if args.mix:
        write_boundary();mix();return
    if args.realign:
        write_boundary();realign();return
    if args.describe:
        data=source()
        print(json.dumps({'scene_count':len(data['scenes']),'shot_count':sum(len(s['shots']) for s in data['scenes']),
                          'voice':'em_alex','speed':1.0,'Native_ticks':0,'original_JSON_available':False,'literal_DOCX_extraction':True}));return
    if args.schedule or args.assemble:
        write_boundary();inspect_or_assemble(assemble=args.assemble);return
    if args.pilot_s01==args.synthesize:
        parser.error('Choose --pilot-s01 or --synthesize')
    write_boundary()
    generate(['S01'] if args.pilot_s01 else args.scene_ids or [f'S{i:02d}' for i in range(1,15)],
             pilot=args.pilot_s01,approved=args.central_approved)


if __name__=='__main__':
    main()
