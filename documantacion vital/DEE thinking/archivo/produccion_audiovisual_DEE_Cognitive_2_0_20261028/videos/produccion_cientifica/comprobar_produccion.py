"""QC audiovisual, sin ejecutar DEE ni tocar sus originales."""
from pathlib import Path
import json,subprocess,re,hashlib,shutil,struct,argparse
from PIL import Image,ImageDraw
import pelicula as P
W=P.W;OUT=W/'Cientifica_R02.mp4'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def technical():
    plan=json.loads((W/'timeline.json').read_text(encoding='utf8'))
    assert len(plan['scenes'])==8 and len(plan['voice'])==45
    d=json.loads(subprocess.check_output([str(P.PROBE),'-v','error','-threads','2','-count_frames','-show_streams','-show_format','-of','json',str(OUT)]))
    v=next(s for s in d['streams'] if s['codec_type']=='video');a=next(s for s in d['streams'] if s['codec_type']=='audio')
    assert (v['width'],v['height'],v['codec_name'],v['pix_fmt'],v['avg_frame_rate'])==(1920,1080,'h264','yuv420p','30/1')
    assert int(v['nb_read_frames'])==round(plan['duration']*30)
    assert a['codec_name']=='aac' and int(a['channels'])==2 and a['sample_rate']=='48000'
    assert ' '.join(c['text'] for c in plan['captions'])==' '.join(s['en'] for s in P.G['scenes'])
    assert all(len(c['lines'])<=2 for c in plan['captions'])
    pts=subprocess.check_output([str(P.PROBE),'-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','csv=p=0',str(OUT)]).decode()
    times=[float(line.split(',')[0]) for line in pts.splitlines() if line and line[0].isdigit()]
    assert len(times)==int(v['nb_read_frames'])
    max_step_error=max(abs((b-a)-1/30) for a,b in zip(times,times[1:]))
    assert max_step_error<.000002
    with (W/'decodificacion.log').open('wb') as f:
        subprocess.run([str(P.FF),'-hide_banner','-v','info','-threads','2','-xerror','-i',str(OUT),'-vf','blackdetect=d=0.15:pix_th=0.02:pic_th=0.98','-af','ebur128=peak=true','-f','null','-'],stderr=f,stdout=subprocess.DEVNULL,check=True,timeout=300)
    log=(W/'decodificacion.log').read_text(encoding='utf8',errors='replace');summary=log.split('Summary:')[-1]
    peak=re.search(r'True peak:\s*Peak:\s*([-\d.]+)',summary);loud=re.search(r'Integrated loudness:\s*I:\s*([-\d.]+)',summary)
    assert peak and loud and float(peak[1])<=-1.0
    black=re.findall(r'black_start:[^\n]+',log);assert not black,black
    sources={1:'DEE20_DEMO_01 real sampled positions, authentic original capture',2:'G07 geometry / FísicaDEE / ProcesamientoNativo',3:'G07 original recipe and report; C6H04 controls explicitly separate',4:'a13_clasifica, a21_revision, a22_revision_use, a44_save, b02_reopen, b09_revision',5:'U0 IR_P01_GUARDED_M1 and IR_MATCH_CURRENT records + 4.5 geometry',6:'Actual Cognitive2.0 recording, manual4.5 and Cognitive1.21',7:'Application concepts connected to authentic revision/continuity evidence and G07; no deployed use claimed',8:'Recorded DEE20_DEMO_01 final world, editorial camera motion; authorized development vision'}
    result={'file':str(OUT),'sha256':sha(OUT),'bytes':OUT.stat().st_size,'ffprobe':d,'lufs':float(loud[1]),'true_peak_dbfs':float(peak[1]),'full_av_decode':'completed without errors','black_intervals':black,'sources_by_scene':sources,'g07_source_index':'fuentes_g07/G07_EVIDENCIA_Y_GEOMETRIA.json','information_source_index':'fuentes_g07/U0_INFORMACION_GEOMETRIA.json','subtitles':'English only, literal supplied translations; per-sentence semantic alignment','spanish_narration':'Literal supplied script; neural synthesis entirely offline','music':'Original local synthesized ambient composition; no third-party recordings','new_native_ticks':0,'audio_personal_listening':'PENDING: model session does not accept audio input. Measurements are not a personal hearing approval.','visual_full_personal_playback':'Not asserted; decoded continuous sampling and transition inspection are separately documented.','acceptance':'PRODUCED; personal audiovisual acceptance remains pending and must not be described as approved.'}
    save(W/'verificacion.json',result);print('TECHNICAL',v['nb_read_frames'],result['lufs'],result['true_peak_dbfs'],flush=True)
    result.update({'cfr_checked_pts':len(times),'maximum_frame_step_error_seconds':max_step_error,'voice_provenance':json.loads((W/'voz/MODELO_Y_LICENCIA.json').read_text(encoding='utf8')),'voice_validation':json.loads((W/'voz/VERIFICACION_VOZ.json').read_text(encoding='utf8')),'scientific_scope':{'g07':'Historical engine experiment, not a new acquisition by DEE20_DEMO_01; intermediate positions reconstructed from recipe and transport, final8222/30 observed in saved verifier report.','controls':'Separate historical C6H04 N64, both_trained/first_only. Not a G07 omission run.','u0':'Distinct U0/CPC7 organization. Geometry reconstructed from official constructor and selected original observations. No new native run.','colors_lighting_radius':'Editorial display encodings, not native DEE colors, radiation or physical particle size.','scene4_a22':'Input footage is authentic; response−1 is a separately identified primary record, not a claim it is visible in that camera crop.'}})
    evidence_files=[W/'fuentes_g07/G07_EVIDENCIA_Y_GEOMETRIA.json',W/'fuentes_g07/U0_INFORMACION_GEOMETRIA.json',P.PRIOR/'fuentes_y_control.json',W/'fuentes_g07/VERIFICACION_EDITORIAL_LINUX_original.json',W/'fuentes_g07/C6H04_compositional_translation_holdout_original.json']
    result['sources_with_localizers']=[{'path':str(f),'sha256':sha(f),'bytes':f.stat().st_size} for f in evidence_files]
    result['g07_primary_pointer']='/groups/07/examples/0 in VERIFICACION_EDITORIAL_LINUX_original.json: d1=3,d2=7,query=20,output_sreg=8222,decoded=30'
    result['composition_resolution']={'design':[1920,1080],'rendered_3d_and_titles':'Native1920x1080; OpenGL depth-tested meshes and native-resolution type.','legacy_source_capture':[1284,932],'legacy_source_fps':15,'legacy_handling':'Selected crops/stills upscaled inside the native1080p composition; no upscaling of a low-resolution master.'}
    result['production_files']=[{'path':str(f),'sha256':sha(f),'bytes':f.stat().st_size} for f in [W/'pelicula_R01.py',W/'pelicula.py',W/'render3d/dee_renderer.py',W/'timeline.json',W/'guion_literal.json',W/'voz/narraciones.json']]
    result['editorial_revision']='R02: only scene5 final camera orbit changed; native state held atT72. R01 script and movie retained. Other seven encoded scenes reused unchanged.'
    result['image_categories']={1:['B real sampled positions','A authentic application'],2:['B actual sampled world','C G07 reconstruction'],3:['C G07 reconstruction','B C6H04 separate control observations'],4:['A authentic clips/stills','Primary data annotation for a22'],5:['C U0 geometry reconstruction'],6:['B actual sampled world','A authentic application'],7:['D proposed application','A authentic recorded examples','C G07 foundation'],8:['B real final world; camera-only animation']}
    result['subtitle_metrics']={'cues':len(plan['captions']),'maximum_characters_per_second':max(len(c['text'])/(c['end']-c['start']) for c in plan['captions']),'minimum_cue_seconds':min(c['end']-c['start'] for c in plan['captions']),'lines_maximum':2,'translation_words':P.G['words_en'],'literal_match':True}
    result['narrative_review']={'what_is_DEE':'Scenes1–2: experimental computational architecture, 3D positions and a uniform evolution rule.','experience_use':'Scene3: formation of two records before a new query, later spatial encounters.','mechanism_beyond_sum':'Scene3: moving supports and consecutive interactions, historical controls kept separate.','developed_functions':'Scenes4–5: response revision, save/reopen continuity, query/receive/use.','applications':'Scene7 explicitly presents development directions and says they need construction and measurement.','collaboration':'Scene8 proposes selecting a real problem, developing a pilot and measuring response/learning/value.','audience_test':'No external audience study performed.'}
    save(W/'verificacion.json',result)
def samples():
    p=json.loads((W/'timeline.json').read_text(encoding='utf8'));folder=W/'QC';folder.mkdir(exist_ok=True);rows=[]
    for s in p['scenes']:
        for j,r in enumerate([.08,.25,.5,.75,.92]):rows.append({'at':s['start']+r*s['duration'],'scene':s['scene'],'name':f'escena_{s["scene"]:02}_{j}'})
    for j,s in enumerate(p['scenes'][1:]):
        for k,delta in enumerate([-.1,0,.1]):rows.append({'at':s['start']+delta,'scene':s['scene'],'name':f'union_{j:02}_{k}'})
    rows.append({'at':p['duration']-.06,'scene':8,'name':'ultimo_fotograma'})
    for r in rows:
        target=folder/(r['name']+'.png')
        if not target.exists():subprocess.run([str(P.FF),'-v','error','-threads','2','-n','-ss',str(r['at']),'-i',str(OUT),'-frames:v','1',str(target)],check=True,timeout=30)
    for page in range((len(rows)+7)//8):
        sheet=Image.new('RGB',(1280,1536),P.BG)
        for j,r in enumerate(rows[page*8:page*8+8]):
            im=Image.open(folder/(r['name']+'.png')).resize((640,360),Image.Resampling.LANCZOS);x=j%2*640;y=j//2*384;sheet.paste(im,(x,y));ImageDraw.Draw(sheet).text((x+8,y+360),r['name']+f' {r["at"]:.2f}',font=P.font(17),fill=P.GRAY)
        sheet.save(folder/f'control_{page:02}.jpg',quality=94)
    contact=Image.new('RGB',(1920,640),P.BG)
    for i,s in enumerate(p['scenes']):
        im=Image.open(folder/f'escena_{s["scene"]:02}_2.png').resize((480,270),Image.Resampling.LANCZOS);x=i%4*480;y=i//4*320;contact.paste(im,(x,y));ImageDraw.Draw(contact).text((x+22,y+282),f'Escena {i+1}',font=P.font(25),fill=P.WHITE)
    contact.save(W/'Hoja_Contacto.jpg',quality=95)
    for name in ['escena_03_2','escena_04_2','escena_05_2']:
        for width in [960,480,360]:
            Image.open(folder/(name+'.png')).resize((width,round(width*9/16)),Image.Resampling.LANCZOS).save(folder/(name+f'_{width}.png'))
    save(folder/'indice.json',{'sha256':sha(OUT),'frames':rows,'method':'Exported final pixels at native resolution; reviewed as640x360,960x540 and1920x1080.'})
    print('SAMPLES',len(rows),flush=True)
def review():
    p=json.loads((W/'timeline.json').read_text(encoding='utf8'));folder=W/'QC';folder.mkdir(exist_ok=True)
    for s in p['scenes']:
        rows=int((s['duration']+5)//6)
        target=folder/f'secuencia_completa_{s["scene"]:02}.jpg'
        subprocess.run([str(P.FF),'-v','error','-threads','2','-n','-ss',str(s['start']),'-t',str(s['duration']),'-i',str(OUT),'-vf',f'fps=1,scale=320:180,tile=6x{rows}:padding=2:margin=2','-frames:v','1','-q:v','2',str(target)],check=True,timeout=60)
    print('CONTINUOUS_SEQUENCE_REVIEW',flush=True)
def deliver():
    d=json.loads((W/'verificacion.json').read_text(encoding='utf8'));q=json.loads((W/'QC/indice.json').read_text(encoding='utf8'));assert sha(OUT)==d['sha256']==q['sha256']
    base=json.loads((W/'procedencia_base.json').read_text(encoding='utf8'))
    for r in base['protected']:assert sha(Path(r['path']))==r['sha256'],r['path']
    targets={'DEE_Cognitive_2_0_Presentacion_Cientifica_Profesional_1080p.mp4':OUT,'DEE_Cognitive_2_0_Presentacion_EN.srt':W/'subtitulos_EN.srt','DEE_Cognitive_2_0_Guion_Final_ES_EN.txt':W/'guion_final_ES_EN.txt','DEE_Cognitive_2_0_Hoja_Contacto.jpg':W/'Hoja_Contacto.jpg'}
    for name,p in targets.items():
        t=P.ROOT/'videos'/name;assert not t.exists();shutil.copy2(p,t);assert sha(p)==sha(t)
    d['delivered_file']=str(P.ROOT/'videos/DEE_Cognitive_2_0_Presentacion_Cientifica_Profesional_1080p.mp4');d['protected_originals_unchanged']=True
    t=P.ROOT/'videos/DEE_Cognitive_2_0_Verificacion_Produccion.json';assert not t.exists();save(t,d);save(W/'verificacion.json',d)
    print('DELIVERED',d['delivered_file'],d['bytes'],d['sha256'],flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['technical','samples','review','deliver']);a=p.parse_args();globals()[a.action]()
