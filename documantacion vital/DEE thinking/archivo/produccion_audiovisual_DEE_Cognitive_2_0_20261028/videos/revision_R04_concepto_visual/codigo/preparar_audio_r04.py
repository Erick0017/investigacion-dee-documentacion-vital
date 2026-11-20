"""R04 local stock-voice replacements only. No DEE imports or remote service."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import sys
import xml.etree.ElementTree as ET
import zipfile

W = Path(__file__).resolve().parents[1]
VIDEOS = W.parent
R03 = VIDEOS/'produccion_cientifica/R03'
PROMPT = Path(r'C:\Users\Erik\.codex\codex-remote-attachments\01a0921e-4727-7f93-8ad0-0b605c9afe96\21992FA8-6944-4EE7-BB8B-1FAA24C459B9\1-PROMPT_CODEX_DEE_VIDEO_R04_DIFERENCIA_COMPUTACIONAL_Y_MEJORA_VISUAL.docx')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def literal_passages():
    with zipfile.ZipFile(PROMPT) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    paragraphs = [''.join(p.itertext()) for p in root.findall('./w:body/w:p', ns)]
    es = [p[4:] for p in paragraphs if p.startswith('ES: ')]
    en = [p[4:] for p in paragraphs if p.startswith('EN: ')]
    assert len(es) == len(en) == 2
    brief_es = next(p[len('A breve, ES: '):] for p in paragraphs if p.startswith('A breve, ES: '))
    brief_en = next(p[len('A breve, EN: '):] for p in paragraphs if p.startswith('A breve, EN: '))
    return {'A_principal': {'id': 'A_principal', 'es': es[0], 'en': en[0]},
            'A_breve': {'id': 'A_breve', 'es': brief_es, 'en': brief_en},
            'B_principal': {'id': 'B_principal', 'es': es[1], 'en': en[1]}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--synthesize', action='store_true')
    args = parser.parse_args()
    if not args.synthesize:
        parser.error('Explicit --synthesize required; no full narration regeneration')
    output = W/'audio'
    output.mkdir(parents=True, exist_ok=True)
    metadata = W/'datos/audio_fragmentos_R04.json'
    metadata.parent.mkdir(parents=True, exist_ok=True)
    prior = json.loads(metadata.read_bytes()) if metadata.is_file() else None
    existing = {} if prior is None else {r['id']: r for r in prior['fragments']}
    original = json.loads((R03/'voz/timings.json').read_bytes())
    src = R03/'sintetizar_voz_r03.py'
    spec = importlib.util.spec_from_file_location('_r04_exact_original_stock_voice', src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.PARAMS == original['parameters'], 'R03 voice parameters differ'
    original_wave = R03/'voz/locucion_continua_R03.wav'
    original_hash = sha(original_wave)
    # Redirect only the fragment destinations. SOURCE remains the verified
    # original model/dependency directory. setup never renders old scenes.
    mod.W, mod.OUT = W, output
    np, sf, synth, assets, runner, alias = mod.setup()
    passages = literal_passages()
    fragments = []
    for identifier in ('A_principal', 'B_principal'):
        fragments.append(mod.synthesize(passages[identifier], np, sf, synth,
                                        assets, runner, existing))
    if fragments[0]['duration'] > 23.7:
        fragments.append(mod.synthesize(passages['A_breve'], np, sf, synth,
                                        assets, runner, existing))
    assert sha(original_wave) == original_hash
    report = {'schema': 'DEE.R04.local_voice_fragments.v1',
              'source_tts_script': str(src), 'source_tts_script_sha256': sha(src),
              'source_voice_metadata': str(R03/'voz/timings.json'),
              'source_voice_metadata_sha256': sha(R03/'voz/timings.json'),
              'source_continuous_wave': str(original_wave),
              'source_continuous_wave_sha256': original_hash,
              'authorized_prompt': str(PROMPT), 'authorized_prompt_sha256': sha(PROMPT),
              'parameters': mod.PARAMS, 'model_assets': assets,
              'model_runner_files': runner, 'fragments': fragments,
              'replacement_boundaries': {'A': [0, 23.7], 'B': [74.2, 110.6]},
              'full_original_narration_regenerated': False, 'originals_modified': False,
              'private_text_uploaded': False, 'native_DEE_ticks': 0,
              'listening': 'Not performed by this agent; timing/level/PCM checks do not certify auditory naturalness.'}
    mod.atomic_json(metadata, report)
    print(json.dumps({'metadata': str(metadata), 'fragments': [
        {k: r[k] for k in ('id', 'file', 'duration', 'speech_block_seconds',
                          'spoken_words_per_minute', 'clipped_samples')}
        for r in fragments]}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
