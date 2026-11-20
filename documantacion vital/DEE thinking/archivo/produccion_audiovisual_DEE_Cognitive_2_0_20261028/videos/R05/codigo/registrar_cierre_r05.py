"""Update the sole R05 register from real production files; no DEE imports."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import importlib.util

HERE = Path(__file__).resolve().parents[1]
REG = HERE / 'REGISTRO_PRODUCCION_R05.json'

def identity(path):
    path = Path(path)
    h = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            h.update(chunk)
    return {'path': str(path.relative_to(HERE)), 'bytes': path.stat().st_size, 'sha256': h.hexdigest()}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=['frozen', 'final'], required=True)
    args = parser.parse_args()
    r = json.loads(REG.read_text(encoding='utf8'))
    validation_path=HERE/'logs/validacion_10800_modelos_REV03.log'
    if not validation_path.exists():validation_path=HERE/'logs/validacion_10800_modelos_R04.log'
    if not validation_path.exists():validation_path=HERE/'logs/validacion_10800_modelos.log'
    validation = json.loads(validation_path.read_text(encoding='utf-8-sig'))
    r['QA']['offline_model_validation'] = validation
    r['QA']['current_model_validation'] = validation
    spec=importlib.util.spec_from_file_location('qa_guion',HERE/'audio/qa_guion_subtitulos_r05.py')
    qa=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(qa)
    r['QA']['script_caption_chronology'] = qa.SCRIPT_CAPTION_CHRONOLOGY_QA
    progression_path=HERE/'logs/progresion_montaje_REV03.log'
    if not progression_path.exists():progression_path=HERE/'logs/progresion_montaje_R04.log'
    if not progression_path.exists():progression_path=HERE/'logs/progresion_montaje.log'
    progression=json.loads(progression_path.read_text(encoding='utf-8-sig'))
    progression['editorial_judgement'] = {
        'S03':'3.4s acquired output and4s matched-world comparison are deliberate result-reading pauses.',
        'S06':'3.8s on30 is the deliberate result pause before the documented route is replayed; no10s stationary result.',
        'S09':'4s late NULL contrasting the earlier physically valid zero; a deliberate access-window comparison.',
        'S11':'5s contrast of useful return-conditioned action versus omitted return, with ongoing literal explanation.',
        'S12':'4s full128-component preparation then4s intervention0→2; time to inspect the two distinct structures before recorded consequences.'}
    r['QA']['event_progression_camera_excluded'] = progression
    r['QA']['historical_visual_review'] = json.loads((HERE/'datos/QA_VISUAL_HISTORICAS_R05.json').read_text(encoding='utf8'))
    original_names = [f'S{scene:02d}_{frame:05d}.png' for scene, frames in {
        4:[0,320,640,959], 9:[0,280,560,839], 11:[0,240,480,719],
        12:[0,260,520,779], 13:[0,220,440,659], 14:[0,200,400,599],
        15:[0,180,360,539]}.items() for frame in frames]
    corrections = ['S04_00060.png','S09_00600.png','S09_00720.png','S09_00810.png','S13_00240.png','S13_00360.png']
    r['QA']['root_visual_review'] = {
        'coverage':'28 original actual-case previews, six corrections and one S08 final opened individually at 1920x1080',
        'original_previews':[identity(HERE/'previas/REVISION_FINAL'/name) for name in original_names],
        'correction_previews':[identity(HERE/'previas/CORRECCIONES_R03'/name) for name in corrections],
        'S08_final':identity(HERE/'previas/REVISION_FINAL/S08_00659_corregida.png'),
        'blocking_defects_remaining':[]}
    for name in list(r['source_coverage']['source_adapters_snapshot']):
        old = r['source_coverage']['source_adapters_snapshot'][name]
        current = identity(HERE/name)
        if old['sha256'] != current['sha256']:
            current['prior_QA_snapshot_sha256'] = old.get('prior_QA_snapshot_sha256', old['sha256'])
        r['source_coverage']['source_adapters_snapshot'][name] = current
    r['QA']['scientific_attribution_review'] = {
        'blocking_errors_found':False,
        'notes':[
            'S08 last displayed material field is T4425; available T4435 has no material observation and is not claimed as a further successful use.',
            'CORE06 trained and omitted worlds are matched separate worlds, never one biography.',
            'G07 output23 is derived;30 is observed. No matched G07 omission control is claimed.',
            'M014 changes geometry/route as well as event order; no unique ordering mechanism is isolated.',
            'ING05 compares historical state and history-conditioned transformation; it does not identify a unique memory site.',
            'IC01 uses a fixed motor codec, not a learned motor policy. CPC9 shows its first valid exchange, not rejected later updates.',
            'G08 transfers functional support, not an individual clone. ENTE02 domain was selected by the operator. Ciclo02 protection is prepared P0.',
            'S05 ALT retention before export and REAPERTURA_P0 postreload use are labelled as different lives.',
            'CP02 omitted-history result is indeterminate, not zero; Pensamiento01 is a finite recorded N127 sequence, not general prediction or an endless loop.',
            'S14 positive direct arithmetic and MINUS postreopen use are explicitly different cases. No postreopen query is invented for the positive direct-arithmetic final snapshot.',
            'S14 has editorial anticipations of1.335s and0.370s at two internal shot transitions; case footers remain explicit. Final MA-minus response holds0.5s after its2s query. These are presentation limits, not new scientific results.'
        ]}
    r['stage'] = 'visual_sources_frozen_final_render' if args.phase == 'frozen' else 'completed'
    r['last_updated_utc'] = datetime.now(timezone.utc).isoformat()
    r['native_execution'] = {'new_ticks':0,'new_experiments':0,'new_life_forks':0,
        'operational_or_manual_writes':0,'method':'Read existing records; render editorial3D outside DEE.'}
    r['resume'] = 'Await encoded media, final decoded-frame QA and mux verification.'
    if args.phase == 'final':
        names = ['DEE_Cognitive_2_0_R05_Mundo_y_Capacidades_1080p_EN.mp4',
                 'DEE_Cognitive_2_0_R05_Mundo_y_Capacidades_1080p_LIMPIO.mp4','R05_EN.srt','R05_ES.srt']
        r['outputs'] = {name:identity(HERE/name) for name in names}
        media_check=HERE/'logs/VERIFICACION_FINAL_MEDIA_R03.log'
        if not media_check.exists():media_check=HERE/'logs/VERIFICACION_FINAL_MEDIA.log'
        verification=json.loads(media_check.read_text(encoding='utf-8-sig'))
        assert verification['ok'],verification.get('failed_checks')
        r['QA']['final_container_audio_subtitle_checks']=verification
        r['QA']['encoded_audio_levels']={'log':identity(HERE/'logs/AUDIO_FINAL_R03.log'),
            'integrated_loudness_LUFS':-16.0,'loudness_range_LU':3.3,'true_peak_dBFS':-1.2,
            'measurement':'FFmpeg ebur128 on the final encoded Spanish audio; both exports have identical decoded PCM.',
            'human_listening_performed':False,'naturalness_not_auditorily_certified':True}
        technical=[]
        current_hashes={row['sha256'] for name,row in r['outputs'].items() if name.endswith('.mp4')}
        for log in sorted((HERE/'logs').glob('*.log')):
            for line in log.read_text(encoding='utf-8-sig',errors='replace').splitlines():
                if not line.startswith('{'):continue
                try:entry=json.loads(line)
                except json.JSONDecodeError:continue
                if entry.get('operation')=='technical_verification' and entry.get('sha256') in current_hashes:
                    assert entry['strict_full_decode_exit']==0
                    technical.append(entry)
        assert {entry['sha256'] for entry in technical}==current_hashes,'Full decode/probe missing for current exact exports'
        r['QA']['final_full_decode_and_probes']=technical
        r['QA']['historical_encoded_review']=json.loads((HERE/'datos/QA_CODIFICADO_HISTORICAS_R05.json').read_text(encoding='utf8'))
        r['QA']['final_scaled_EN_review']=json.loads((HERE/'datos/QA_ESCALA_FINAL_EN_R05.json').read_text(encoding='utf8'))
        sync_images=sorted((HERE/'qa_final_S02_sincronia').glob('*.png'))
        assert len(sync_images)==12,'Expected the six final encoded S02 transitions at two display scales'
        r['QA']['final_encoded_S02_sync']={'global_frames_opened':[786,788,1059,1060,1219,1220],
            'scales':[{'width':1920,'height':1080},{'width':480,'height':270}],
            'images':[identity(p) for p in sync_images],
            'finding':'NN before and DEE after26.240s; rules and organization captions match the respective narration topic cuts, quantized to30fps.',
            'remaining_blockers':[],'human_listening_claimed':False}
        by_scene={row['scene']:row for row in validation['scenes']}
        for scene in r['scenes']:
            source=r['source_coverage']['scenes'][scene['id']]
            scene['representation']=by_scene[scene['id']]['representations']
            scene['scientific_sources']=source['segments']
            scene['status']='Rendered, encoded-frame editorial QA and complete technical decode performed; detailed coverage in QA.'
            source['status']='Source-linked montage rendered; final QA scope and limits recorded in this production register.'
        r['source_coverage']['validation']['final_visual_QA']='Completed with scene-by-scene encoded samples and individual causal frames; not a human continuous-playback or listening certification.'
        r['resume'] = 'Production closed. Do not repeat Native runs; project and evidence remain in this R05 folder.'
        r['closed_utc']=datetime.now(timezone.utc).isoformat()
    tmp = REG.with_suffix('.json.pending')
    tmp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    os.replace(tmp,REG)
    print(json.dumps({'phase':args.phase,'register_bytes':REG.stat().st_size,'models':validation['total_models'],
                      'fingerprint':validation['visual_source_sha256'],'native_ticks':0},ensure_ascii=False))

if __name__ == '__main__':
    main()
