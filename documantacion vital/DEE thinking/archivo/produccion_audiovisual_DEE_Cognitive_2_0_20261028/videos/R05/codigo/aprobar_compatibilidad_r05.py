"""Root editorial approval of proven unchanged R05 scene inputs."""
from pathlib import Path
import hashlib,json,os,argparse,copy
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--revision',choices=['02','03'],default='02');args=parser.parse_args()
proof_path=HERE/f'logs/COMPARACION_MODELOS_R05_REVISION{args.revision}.log'
proof=json.loads(proof_path.read_text(encoding='utf-8-sig'))
assert proof['total_frames_individually_compared']==10800
assert proof['common_files_unchanged'] is True
expected_changes=['S11','S12'] if args.revision=='02' else ['S02']
assert proof['changed_scenes']==expected_changes
assert len(proof['equal_scenes'])==15-len(expected_changes)
reg_path=HERE/'REGISTRO_PRODUCCION_R05.json'
reg=json.loads(reg_path.read_text(encoding='utf8'))
for name,entry in proof['common_files'].items():
    assert sha(HERE/name)==entry['new_sha256']==entry['old_sha256']
for scene,row in proof['scenes'].items():
    assert sha(Path(row['segment_path']))==row['segment_sha256']
    row['approved']=bool(row['all_frames_equal'])
    if row['approved']:
        assert row['old_models_sequence_sha256']==row['new_models_sequence_sha256']
        assert not row['different_frame_indices']
        if row['segment_source_fingerprint']!=proof['reference_fingerprint']:
            previous=reg['render_compatibility'][proof['reference_fingerprint']]
            prior=previous['scenes'][scene]
            chain=row['source_chain']
            assert previous['approved'] and prior['approved'] and prior['all_frames_equal']
            assert prior['new_models_sequence_sha256']==row['old_models_sequence_sha256']
            assert prior['segment_sha256']==row['segment_sha256']
            assert prior['segment_source_fingerprint']==row['segment_source_fingerprint']
            assert chain['prior_proof_record_sha256']==hashlib.sha256(json.dumps(previous,sort_keys=True,separators=(',',':')).encode()).hexdigest()
proof['approved']=True
proof['approval_authority']='Root editorial review: unchanged scenes retain their exact original encoded bytes and original source comment; changed scenes must be rendered again.'
proof['proof_log_sha256']=sha(proof_path)
proof['approved_utc']=datetime.now(timezone.utc).isoformat()
reg.setdefault('render_compatibility',{})[proof['new_fingerprint']]=proof
if args.revision=='02':reg['incidents'].append({'stage':'encoded_QA_revision02',
    'finding':'S11 environmental annotation too far from its schematic object; S12 changed component and sparse retained fields required local camera views.',
    'correction':'C schematic action/return progression and label anchoring; exact-coordinate ROI closeups. Narration, data, ticks and scene windows unchanged.',
    'corrected_views':[str(p.relative_to(HERE)) for p in sorted((HERE/'previas/CORRECCIONES_R04').glob('*.png'))],
    'changed_scenes':['S11','S12'],'new_native_ticks':0})
else:
    reg['incidents'].append({'stage':'burned_caption_QA_revision03','finding':'DEE narration/caption starts26.240s while conceptual neural network remained visible until31s.',
        'correction':'Only S02 picture retimed to narrator topic cuts; unchanged literal audio/subtitles, case and reconstruction. Actual cut quantized to26.233333s at30fps.',
        'changed_scenes':['S02'],'new_native_ticks':0})
    source=reg['source_coverage']['scenes']['S02'];network=copy.deepcopy(source['segments'][0]);dee=copy.deepcopy(source['segments'][1])
    network['local_seconds']=[0,187/30];dee['local_seconds']=[187/30,24]
    dee['case']='CORE06 forward reconstruction after a visible editorial cut';dee['cut']=[0,11]
    dee['shows']='CORE06 source-animation frames0..419, corresponding to historical nativeT0..T11, progress forward. Animation frames are not native ticks.'
    dee['internal_title_windows_local']=[{'title':'DEE: encuentros e historia','start_frame':187,'end_frame_exclusive':460},
        {'title':'Reglas del motor','start_frame':460,'end_frame_exclusive':620},
        {'title':'Organización que cambia','start_frame':620,'end_frame_exclusive':720}]
    source['segments']=[network,dee]
reg['QA']['current_model_validation']=json.loads((HERE/'logs/validacion_10800_modelos_R04.log').read_text(encoding='utf-8-sig'))
reg['QA']['subtitle_container_interpretation']={
    'requirement':'Clean picture with English/Spanish selectable subtitles; DOCX does not require both track enabled flags to be zero.',
    'observed':'FFmpeg7.1 enables the first subtitle track; AV default reports this enabled bit. Both subtitles remain unforced.',
    'decision':'Keep standards-compatible mux and both external SRTs. Do not disable all subtitle tracks merely to force ffprobe default0.',
    'primary_sources':['https://github.com/FFmpeg/FFmpeg/blob/n7.1/libavformat/movenc.c#L6856-L6903',
        'https://developer.apple.com/documentation/quicktime-file-format/preparing_sound_and_subtitle_alternate_groups_for_use_with_apple_devices'],
    'limit':'Player settings decide automatic subtitle display; no claim of an actual iPhone/QuickTime viewing test.'}
reg['stage']='editorial_revision'+args.revision+'_verified_reuse'
tmp=reg_path.with_suffix('.json.pending');tmp.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,reg_path)
print(json.dumps({'approved':True,'new_fingerprint':proof['new_fingerprint'],'unchanged_scene_count':len(proof['equal_scenes']),'unchanged_frames':sum(r['frames'] for r in proof['scenes'].values() if r['approved']),'changed_scenes':expected_changes,'native_ticks':0}))
