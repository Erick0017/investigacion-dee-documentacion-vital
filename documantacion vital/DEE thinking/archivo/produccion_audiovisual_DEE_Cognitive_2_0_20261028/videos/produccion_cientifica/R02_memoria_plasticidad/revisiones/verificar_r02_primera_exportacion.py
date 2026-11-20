"""Verificación y publicación local R02. Nunca importa ni ejecuta el motor."""
from pathlib import Path
import json,subprocess,re,hashlib,shutil,struct,argparse,importlib.util,datetime,wave
from zipfile import ZipFile
from PIL import Image,ImageDraw,ImageFont
import pelicula_r02 as P
W=P.W;OUT=W/'montaje_R02.mp4'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def load(name):
    s=importlib.util.spec_from_file_location(name,W/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def update(key,value):
    d=P.read(W/'CONTROL_R02.json');d[key]=value;P.save(W/'CONTROL_R02.json',d)
def originals():
    d=P.read(W/'CONTROL_R02.json');results=[]
    for x in d['protected_originals']:
        p=Path(x['path']);assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'],p
        results.append(dict(path=str(p),sha256=x['sha256'],unchanged=True))
    return results
def preflight():
    d=P.read(W/'CONTROL_R02.json');g=P.G;plan=P.read(W/'timeline_R02.json');vm=P.read(W/'voz/timings.json')
    assert len(g['scenes'])==len(plan['scenes'])==len(vm['scenes'])==12
    assert all(v['complete_model_waveform_retained'] and v['audio_sentence_splices']==0 for v in vm['scenes'])
    assert all(m['start'] is not None and m['end'] is not None for v in vm['scenes'] for m in v['sentences'])
    prompt=Path(g['source']) if Path(g['source']).is_file() else W/'instruccion_R02_recibida.txt'
    assert sha(prompt)==g['source_sha256']
    raw=prompt.read_text(encoding='utf-8-sig');parser=load('preparar_r02')
    for s in g['scenes']:
        if s['new_block']:
            es,en=parser.block(raw,s['new_block'])
            assert (s['es'].startswith(es) and s['en'].startswith(en)) if s['id']=='g07' else (s['es']==es and s['en']==en)
    old=P.read(P.PROD/'guion_literal.json')['scenes']
    for s in g['scenes']:
        if s['id'] in ['s01','s02','u0','plataforma','cierre']:
            o=next(x for x in old if x['scene']==s['old_scene']);assert (s['es'],s['en'])==(o['es'],o['en'])
    base=P.base_module();geometry=[]
    for frame in P.E['geometric_site_frames']:
        t=frame['t'];expected=sorted(tuple(c['xyz']) for c in frame['carriers']);actual=sorted(tuple(c['position']) for c in base.g07_particles(t))
        assert expected==actual,(t,expected,actual);geometry.append(dict(t=t,positions_match=True))
    # Guion, geometría y casos de control son datos existentes, no una ejecución
    # científica nueva ni una prueba microscópica de toda la trayectoria.
    E=P.E
    assert E['causal_events'][3]['xyz']==[20,23,30] and E['causal_events'][4]['xyz']==[27,30,30]
    source_files=[P.PROD/'fuentes_g07/VERIFICACION_EDITORIAL_LINUX_original.json',P.PROD/'fuentes_g07/C6H04_compositional_translation_holdout_original.json',P.PROD/'fuentes_g07/G07_EVIDENCIA_Y_GEOMETRIA.json',P.PROD/'fuentes_g07/U0_INFORMACION_GEOMETRIA.json']
    assert sha(source_files[0])==E['source_report']['sha256'] and sha(source_files[1])==E['controls']['member_sha256']
    facts=load('leer_fuentes').extract()
    sources=[dict(path=x['path'],sha256=x['sha256'],chapters=[dict(number=c['chapter'],title=c['title'],body_paragraph=c['body_paragraph']) for c in x['chapters']]) for x in facts]
    endpoints=load('auditar_empalmes_base').extract()
    data=dict(originals_unchanged=originals(),literal_new_blocks=True,unchanged_approved_paragraphs=True,English_subtitle_literal_match=True,
        subtitles_cues=len(plan['captions']),subtitles_max_lines=max(len(c['lines']) for c in plan['captions']),
        model_sentence_marks=sum(len(v['sentences']) for v in vm['scenes']),audio_sentence_splices=0,voice_original_assets_unchanged=vm['original_assets_unchanged'],
        voice_rms_dbfs_range=[min(v['rms_dbfs'] for v in vm['scenes']),max(v['rms_dbfs'] for v in vm['scenes'])],
        voice_rate_or_pitch_changed_after_synthesis=False,voice_identity=vm['parameters'],voice_timings_sha256=sha(W/'voz/timings.json'),
        g07_geometry_integer_frames=geometry,retained_source_files=[dict(path=str(p),sha256=sha(p)) for p in source_files],foundational_documents=sources,
        old_voice_splice_diagnostic=endpoints,renderer_source_sha256=sha(P.PROD/'render3d/dee_renderer.py'),renderer_R02_source_sha256=sha(W/'pelicula_r02.py'),
        native_ticks=0,optional_D_included=False,model_alignment_not_independent_ASR=True)
    update('preflight',data)
    rev=W/'revisiones/pelicula_r02_render_final.py'
    if rev.exists():assert sha(rev)==sha(W/'pelicula_r02.py')
    else:shutil.copy2(W/'pelicula_r02.py',rev)
    print('PREFLIGHT_COMPLETE',len(geometry),'documented geometric moments; twelve full voice blocks',flush=True)
def technical():
    plan=P.read(W/'timeline_R02.json');d=json.loads(subprocess.check_output([str(P.PROBE),'-v','error','-threads','2','-count_frames','-show_streams','-show_format','-of','json',str(OUT)]))
    v=next(x for x in d['streams'] if x['codec_type']=='video');a=next(x for x in d['streams'] if x['codec_type']=='audio')
    assert (v['width'],v['height'],v['codec_name'],v['pix_fmt'],v['avg_frame_rate'])==(1920,1080,'h264','yuv420p','30/1')
    assert int(v['nb_read_frames'])==round(plan['duration']*30)
    assert a['codec_name']=='aac' and a['sample_rate']=='48000' and a['channels']==2
    pts=subprocess.check_output([str(P.PROBE),'-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','csv=p=0',str(OUT)]).decode()
    times=[float(line.split(',')[0]) for line in pts.splitlines() if line and line[0].isdigit()]
    assert len(times)==int(v['nb_read_frames']);err=max(abs(b-a-1/30) for a,b in zip(times,times[1:]));assert err<.000002
    folder=W/'QC';folder.mkdir(exist_ok=True)
    log=folder/'decodificacion_completa.log'
    with log.open('wb') as f:
        subprocess.run([str(P.FF),'-hide_banner','-v','info','-threads','2','-xerror','-i',str(OUT),'-vf','blackdetect=d=0.15:pix_th=0.02:pic_th=0.98','-af','ebur128=peak=true','-f','null','-'],stderr=f,stdout=subprocess.DEVNULL,check=True,timeout=420)
    raw=log.read_text(encoding='utf8',errors='replace');summary=raw.split('Summary:')[-1]
    peak=re.search(r'True peak:\s*Peak:\s*([-\d.]+)',summary);loud=re.search(r'Integrated loudness:\s*I:\s*([-\d.]+)',summary)
    assert peak and loud and float(peak[1])<=-1.0
    black=re.findall(r'black_start:[^\n]+',raw);assert not black,black
    assert ' '.join(c['text'] for c in plan['captions'])==' '.join(s['en'] for s in P.G['scenes'])
    assert all(len(c['lines'])<=2 and c['end']>c['start'] for c in plan['captions'])
    result=dict(file=str(OUT),bytes=OUT.stat().st_size,sha256=sha(OUT),ffprobe=d,duration_seconds=float(d['format']['duration']),video_frames=int(v['nb_read_frames']),
        full_AV_decode_without_errors=True,black_intervals=black,integrated_LUFS=float(loud[1]),true_peak_dBTP=float(peak[1]),
        CFR_pts_checked=len(times),maximum_frame_step_error_seconds=err,English_subtitles_cues=len(plan['captions']),English_max_lines=2,
        maximum_subtitle_characters_per_second=max(len(c['text'])/(c['end']-c['start']) for c in plan['captions']),
        native_1080p_3D_and_text=True,legacy_GUI_capture_crops_preserved=True,whole_low_resolution_movie_upscaled=False,
        audio_listening_performed=False,normal_speed_human_AV_playback_claimed=False,new_native_ticks=0)
    update('technical_export',result);print('TECHNICAL',result['video_frames'],result['integrated_LUFS'],result['true_peak_dBTP'],flush=True)
def samples():
    plan=P.read(W/'timeline_R02.json');folder=W/'QC';folder.mkdir(exist_ok=True);rows=[]
    for s in plan['scenes']:
        for j,p in enumerate([.08,.25,.50,.75,.92]):rows.append(dict(at=s['start']+p*s['duration'],scene=s['id'],name=f'{s["id"]}_{j}'))
    for j,s in enumerate(plan['scenes'][1:]):
        for k,delta in enumerate([-.10,0,.10]):rows.append(dict(at=s['start']+delta,scene=s['id'],name=f'union_{j:02}_{k}'))
    b=next(s for s in plan['scenes'] if s['id']=='b2');st=lambda i:b['sentences'][i][0]
    for name,t in [('antes',.7),('experiencia',st(1)+.3),('despues',st(2)+.6),('plasticidad',st(3)+.3),('guardar',st(4)+.1),('reabrir',st(4)+(b['duration']-st(4))*.32),('conserva',st(4)+(b['duration']-st(4))*.78)]:rows.append(dict(at=b['start']+t,scene='b2',name='b2_detalle_'+name))
    rows.append(dict(at=plan['duration']-.06,scene='cierre',name='ultimo_fotograma'))
    for row in rows:
        target=folder/(row['name']+'.png')
        if not target.exists():subprocess.run([str(P.FF),'-v','error','-threads','2','-n','-ss',str(row['at']),'-i',str(OUT),'-frames:v','1',str(target)],check=True,timeout=45)
        assert Image.open(target).size==(1920,1080)
    # Hoja de contacto de escenas modificadas, más imágenes completas legibles.
    selected=['g07','b1','b2','c1','c2','activo'];contact=Image.new('RGB',(1920,720),P.BG)
    for i,identifier in enumerate(selected):
        im=Image.open(folder/(identifier+'_2.png')).resize((640,360),Image.Resampling.LANCZOS);contact.paste(im,(i%3*640,i//3*360))
    contact.save(W/'Hoja_Contacto_R02.jpg',quality=95)
    reduced=[]
    for identifier in ['g07_2','b1_2','b2_detalle_antes','b2_detalle_experiencia','b2_detalle_despues','b2_detalle_conserva','c1_2','c2_2','plataforma_2']:
        Image.open(folder/(identifier+'.png')).resize((960,540),Image.Resampling.LANCZOS).save(folder/(identifier+'_960.png'));reduced.append(identifier+'_960.png')
    update('exported_visual_samples',dict(video_sha256=sha(OUT),frames=rows,reduced_960x540=reduced,scope='Fotogramas del MP4 exportado; no equivalen por sí solos a escucha o reproducción personal completa.'))
    print('SAMPLES',len(rows),flush=True)
def sequence():
    plan=P.read(W/'timeline_R02.json');folder=W/'QC/secuencias';folder.mkdir(parents=True,exist_ok=True)
    records=[]
    for s in plan['scenes']:
        # Un fotograma por segundo en orden, más las uniones y detalles arriba.
        n=math_ceil(s['duration']/6)
        target=folder/(s['id']+'.jpg')
        if not target.exists():subprocess.run([str(P.FF),'-v','error','-threads','2','-n','-ss',str(s['start']),'-t',str(s['duration']),'-i',str(OUT),'-vf',f'fps=1,scale=320:180,tile=6x{n}:padding=2:margin=2','-frames:v','1','-q:v','2',str(target)],check=True,timeout=90)
        records.append(dict(scene=s['id'],start=s['start'],end=s['end'],path=str(target.relative_to(W)),scope='Muestreo temporal continuo de 1fps; no escucha ni reproducción humana a velocidad normal.'))
    update('temporal_sequence_samples',dict(file_sha256=sha(OUT),records=records));print('SEQUENCES',len(records),flush=True)
def math_ceil(v):return __import__('math').ceil(v)
def publish():
    d=P.read(W/'CONTROL_R02.json');assert d['technical_export']['sha256']==sha(OUT)
    assert d.get('visual_review',{}).get('exported_frames_checked') is True,'Falta registrar la revisión visual realmente realizada'
    checked=originals()
    targets={'DEE_Cognitive_2_0_Presentacion_Cientifica_Profesional_R02_1080p.mp4':OUT,'DEE_Cognitive_2_0_Presentacion_Cientifica_Profesional_R02_EN.srt':W/'subtitulos_R02_EN.srt'}
    delivered=[]
    for name,p in targets.items():
        target=P.VIDEOS/name;assert not target.exists(),target
        shutil.copy2(p,target);assert sha(target)==sha(p);delivered.append(dict(path=str(target),bytes=target.stat().st_size,sha256=sha(target)))
    d.update(delivered=delivered,originals_verified_after_export=checked,end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        completion='R02_PRODUCIDA_Y_VERIFICADA_TECNICAMENTE_CON_REVISION_VISUAL_Y_LIMITACION_DE_ESCUCHA_DECLARADA',
        remaining_limitations=['No se realizó escucha humana ni una alineación ASR independiente. No se certifica naturalidad absoluta o ausencia perceptiva de cortes sólo con las medidas.','El bloque opcional D se omitió para mantener el foco en memoria, revisión e integración.','No se alteró el sistema científico; las reconstrucciones no son nuevas observaciones microscópicas.'])
    P.save(W/'CONTROL_R02.json',d)
    for x in delivered:print('DELIVERED',x['path'],x['bytes'],x['sha256'],flush=True)
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('action',choices=['preflight','technical','samples','sequence','publish']);n=a.parse_args();globals()[n.action]()
