"""Record the actually performed encoded-scene review in the sole register."""
from pathlib import Path
import hashlib,json,os
HERE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
seconds={'S01':20,'S02':24,'S04':32,'S09':28,'S11':24,'S12':26,'S13':22,'S14':20,'S15':18}
individual={'S01':[120,390],'S02':[240,630],'S04':[60,450,630,959],
    'S09':[150,300,480,720],'S11':[90],'S12':[120,300],'S13':[240,659],
    'S14':[120,360,480,599],'S15':[539]}
rows=[]
for scene,duration in seconds.items():
    group='apertura_revision03' if scene=='S02' and (HERE/'previas/QA_CODIFICADO/apertura_revision03/S02').exists() else 'apertura' if scene in ('S01','S02') else 'actuales_revision02' if scene in ('S11','S12') else 'actuales'
    folder=HERE/'previas/QA_CODIFICADO'/group/scene
    images=sorted(folder.glob('*.png'))
    frames=list(range(0,duration*30,30))+[duration*30-1]
    assert len(images)==len(frames)
    rows.append({'scene':scene,'encoded_scene_sha256':sha(HERE/'escenas'/f'{scene}.mp4'),
        'full_sequence_review':'One-second ordered encoded samples and final frame reviewed; individual causal frames also opened at1080p.',
        'sequence_samples':[{'local_frame':f,'image':str(p.relative_to(HERE)),'sha256':sha(p)} for f,p in zip(frames,images)],
        'individual_1080_frames_opened':individual[scene],
        'remaining_blocking_findings':[]})
reg_path=HERE/'REGISTRO_PRODUCCION_R05.json';reg=json.loads(reg_path.read_text(encoding='utf8'))
reg['QA']['root_encoded_review']={'scenes':rows,'scene_count':9,'one_second_plus_final_samples':sum(len(r['sequence_samples'])for r in rows),
    'representation':'Encoded pixels from MP4, not new DEE runs or UI screenshots.',
    'limits':'No claim of human continuous real-time playback, audience testing, actual handset viewing or human listening.'}
hist=json.loads((HERE/'datos/QA_CODIFICADO_HISTORICAS_R05.json').read_text(encoding='utf8'))
reg['QA']['historical_encoded_review']=hist
reg['QA']['encoded_editorial_coverage_summary']={'scenes':15,'root_scenes':list(seconds),
    'historical_scenes':['S03','S05','S06','S07','S08','S10'],
    'method':'Ordered scene progressions sampled at1fps; case changes reviewed in those sequences and selected decisive results opened individually; all10800 editorial models validated, plus complete technical video decode.',
    'camera_motion_not_counted_as_a_native_event':True,'unfixed_blocking_defects':[]}
tmp=reg_path.with_suffix('.json.pending');tmp.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,reg_path)
print(json.dumps({'root_scene_count':9,'root_cadence_samples':sum(len(r['sequence_samples'])for r in rows),'all_scenes_covered':15,'native_ticks':0}))
