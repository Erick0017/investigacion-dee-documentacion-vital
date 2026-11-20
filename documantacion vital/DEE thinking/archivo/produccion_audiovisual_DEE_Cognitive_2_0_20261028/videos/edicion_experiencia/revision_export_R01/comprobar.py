"""Comprobación de la película exportada. No ejecuta el sistema cognitivo."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,time,struct
import numpy as np
from PIL import Image,ImageDraw
import montar as M
W=M.W
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def layout():
    plan=json.loads((W/'timeline.json').read_text(encoding='utf8'));original=M.text;violations=[];current={}
    def check(im,xy,s,size=60,color=M.FG,b=False,anchor=None):
        box=ImageDraw.Draw(im).textbbox(xy,str(s),font=M.font(size,b),anchor=anchor)
        if box[0]<99.5 or box[2]>1820.5 or box[1]<0 or box[3]>1060:
            d={'scene':current.get('scene'),'mode':current.get('mode'),'text':str(s),'box':box,'size':size}
            if d not in violations:violations.append(d)
        original(im,xy,s,size,color,b,anchor)
    M.text=check;count=0
    for s in plan['scenes']:
        shots=M.shots_for(s)
        for q in shots:
            current.update({'scene':s['scene'],'mode':q['mode']})
            for p in [0,.12,.33,.5,.67,.88,.999]:
                t=q['start']+(q['end']-q['start'])*p;im,_=M.frame(s,shots,t);M.subtitles(im,plan['captions'],s['start']+t);count+=1
    save(W/'control_diseno.json',{'frames_checked':count,'violations':violations})
    print(json.dumps({'frames':count,'violations':violations},ensure_ascii=False),flush=True)
def technical():
    plan=json.loads((W/'timeline.json').read_text(encoding='utf8'));video=M.OUT;assert video.is_file()
    d=json.loads(subprocess.check_output([str(M.PROBE),'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]))
    v=next(x for x in d['streams'] if x['codec_type']=='video');a=next(x for x in d['streams'] if x['codec_type']=='audio')
    expected=round(plan['duration']*30)
    assert (v['width'],v['height'],v['codec_name'],v['pix_fmt'],v['avg_frame_rate'],v['r_frame_rate'])==(1920,1080,'h264','yuv420p','30/1','30/1')
    assert int(v['nb_read_frames'])==expected and a['codec_name']=='aac'
    pts=json.loads(subprocess.check_output([str(M.PROBE),'-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','json',str(video)]))
    times=[float(f['best_effort_timestamp_time']) for f in pts['frames']];assert len(times)==expected
    assert max(abs(t-i/30) for i,t in enumerate(times))<.00001
    assert abs(float(d['format']['duration'])-plan['duration'])<.035 and 270<=float(d['format']['duration'])<=360
    assert ' '.join(c['text'] for c in plan['captions'])==' '.join(s['narration'] for s in M.G['scenes'])
    assert all(len(c['lines'])<=2 and len(line.split())<=13 for c in plan['captions'] for line in c['lines'])
    atoms=[]
    with video.open('rb') as f:
        while f.tell()<video.stat().st_size:
            pos=f.tell();header=f.read(8)
            if len(header)<8:break
            size,kind=struct.unpack('>I4s',header)
            if size==1:size=struct.unpack('>Q',f.read(8))[0]
            if size==0:size=video.stat().st_size-pos
            atoms.append(kind.decode('ascii'));f.seek(pos+size)
    assert atoms.index('moov')<atoms.index('mdat')
    r={'file':str(video),'sha256':sha(video),'bytes':video.stat().st_size,'ffprobe':d,'frames':expected,'cfr_verified':True,'faststart_verified':True,'subtitle_literal':True,'narrations':'9 principal versions, 561 words; pronunciation DEE adjusted only in synthesis','voice':json.loads((W/'voz/medicion.json').read_text(encoding='utf8')),'new_native_ticks':0,'audio_listening':'PENDING: model session has no audio input; technical decode is not personal listening.'}
    save(W/'verificacion_final.json',r);print('TECHNICAL_VERIFIED',expected,'FRAMES',video.stat().st_size,'BYTES',flush=True)
def decode():
    log=W/'decodificacion.log';started=time.monotonic()
    with log.open('wb') as f:
        cmd=[str(M.FF),'-hide_banner','-v','info','-xerror','-i',str(M.OUT),'-vf','scale=640:360,blackdetect=d=0.15:pix_th=0.02:pic_th=0.98,freezedetect=n=-55dB:d=3','-af','ebur128=peak=true','-f','null','-']
        p=subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=f,timeout=300)
    data=log.read_text(encoding='utf8',errors='replace');assert p.returncode==0
    summary=data.split('Summary:')[-1]
    integ=re.search(r'Integrated loudness:\s*I:\s*([-\d.]+) LUFS',summary);peak=re.search(r'True peak:\s*Peak:\s*([-\d.]+) dBFS',summary)
    assert integ and peak,summary
    integrated=float(integ[1]);true_peak=float(peak[1]);assert -17.5<=integrated<=-14.5 and true_peak<=-1.0,(integrated,true_peak)
    freeze=re.findall(r'lavfi.freezedetect[^\n]*',data);black=re.findall(r'black_start:[^\n]*',data)
    assert not black,black
    report={'file_sha256':sha(M.OUT),'full_av_decode_exit':p.returncode,'wall_seconds':time.monotonic()-started,'integrated_lufs':integrated,'true_peak_dbfs':true_peak,'black_intervals':black,'freeze_detector_messages':freeze,'note':'Still source fragments and numeric comparisons intentionally pause for reading. Review any detector intervals against the edit plan; no generic motion claim.'}
    save(W/'decodificacion_y_sonido.json',report);print('FULL_DECODE',json.dumps(report,ensure_ascii=False),flush=True)
def motion():
    log=W/'movimiento.log'
    with log.open('wb') as f:
        r=subprocess.run([str(M.FF),'-hide_banner','-v','info','-threads','2','-i',str(M.OUT),'-an','-vf','crop=1920:640:0:200,scale=640:214,freezedetect=n=0.000001:d=3','-f','null','-'],stdout=subprocess.DEVNULL,stderr=f,check=True,timeout=180)
    data=log.read_text(encoding='utf8',errors='replace');messages=re.findall(r'lavfi.freezedetect[^\n]*',data)
    save(W/'movimiento.json',{'video_sha256':sha(M.OUT),'area':'Main visual only, without subtitles; low digital noise threshold separates small directed motion from exact holds.','detector_messages':messages})
    print('MOTION_REVIEW',json.dumps(messages),flush=True)
def frames():
    plan=json.loads((W/'timeline.json').read_text(encoding='utf8'));folder=W/'comprobaciones';folder.mkdir(exist_ok=True)
    samples=[]
    for s in plan['scenes']:
        for j,part in enumerate([1/6,.5,5/6]):samples.append({'time':s['start']+s['duration']*part,'name':f'escena_{s["scene"]:02}_tercio_{j}','group':'escenas','scene':s['scene']})
        for j,q in enumerate(M.shots_for(s)):samples.append({'time':s['start']+(q['start']+q['end'])/2,'name':f'plano_{s["scene"]:02}_{j:02}','group':'planos','scene':s['scene'],'mode':q['mode']})
    shots=plan['shots'];joins=[]
    for j,q in enumerate(shots[1:]):
        at=q['absolute_start']
        for k,delta in enumerate([-.08,0,.08]):
            r={'time':at+delta,'name':f'union_{j:02}_{k}','group':'uniones','join':j,'delta':delta,'mode':q['mode']};samples.append(r);joins.append(r)
    samples.append({'time':plan['duration']-.05,'name':'ultimo_fotograma','group':'final'})
    # One decode per sample. The small movie is seekable; these are exported pixels, not a re-render.
    for i,r in enumerate(samples):
        target=folder/(r['name']+'.png')
        if not target.exists():subprocess.run([str(M.FF),'-hide_banner','-v','error','-n','-ss',str(max(0,r['time'])),'-i',str(M.OUT),'-frames:v','1',str(target)],check=True,timeout=30)
        if i%45==0:print('FINAL_SAMPLES',i,'/',len(samples),flush=True)
    for group in ['escenas','planos']:
        selected=[r for r in samples if r['group']==group]
        for page in range(math_ceil(len(selected)/8)):
            sheet=Image.new('RGB',(1280,1536),M.BG)
            for j,r in enumerate(selected[page*8:page*8+8]):
                im=Image.open(folder/(r['name']+'.png'));im=im.resize((640,360),Image.Resampling.LANCZOS);x=j%2*640;y=j//2*384;sheet.paste(im,(x,y));ImageDraw.Draw(sheet).text((x+8,y+360),r['name']+' '+str(round(r['time'],2)),font=M.font(18),fill=M.GRAY)
            sheet.save(folder/f'{group}_640_{page:02}.jpg',quality=94)
    for page in range(math_ceil(len(joins)/24)):
        sheet=Image.new('RGB',(1920,800),M.BG)
        for j,r in enumerate(joins[page*24:page*24+24]):
            row=j//6;column=j%6;im=Image.open(folder/(r['name']+'.png')).resize((320,180),Image.Resampling.LANCZOS);sheet.paste(im,(column*320,row*200));ImageDraw.Draw(sheet).text((column*320+3,row*200+180),r['name']+' '+r['mode'],font=M.font(13),fill=M.GRAY)
        sheet.save(folder/f'uniones_{page:02}.jpg',quality=92)
    # Required larger render sizes, using representative actual data and proof frames.
    for name in ['plano_02_4','plano_03_3','plano_05_3','plano_06_3','plano_08_3']:
        a,b,c=name.split('_');src=folder/f'{a}_{int(b):02}_{int(c):02}.png'
        if src.exists():Image.open(src).resize((960,540),Image.Resampling.LANCZOS).save(folder/(src.stem+'_960.png'))
    save(folder/'indice.json',{'file_sha256':sha(M.OUT),'samples':samples,'sizes':[1920,960,640],'number':len(samples)})
    print('FINAL_SAMPLE_COMPLETE',len(samples),flush=True)
def math_ceil(x):return int(-(-x//1))
def provenance():
    sources=json.loads((W/'fuentes_y_control.json').read_text(encoding='utf8'));plan=json.loads((W/'timeline.json').read_text(encoding='utf8'))
    for s in sources['scenes']:
        c=s['scene'];s['edit_time']={k:plan['scenes'][c-1][k] for k in ['start','end','duration']}
        s['shots']=[q for q in plan['shots'] if q['scene']==c]
        s['verification']='Primary identities and literal narration checked before render; final pixels and audio checked separately.'
    sources['primary_pointers']={'association_before':'a13_clasifica → job/result/request/result → result/rows/0/reader/formed_native_command','association_after':'a22_revision_use → job/result/request/result → result/rows/0/reader/formed_native_command','continuation':'b02_reopen, b03_reopened_status, b08_old, b09_revision','cascade':'new_combined_query_MEASUREMENTS.json:/query,/pairs,/answer/outputs/stage0,/answer/outputs/stage1; matching omitted_combined_relation','query':'IR_P01_GUARDED_M1_RESULT.json:/frames tick19 questions/right.different, tick70 own_banks/right, tick72 actions/own.use.minus; contrasted with IR_MATCH_CURRENT'}
    sources['clip_windows']={name:json.loads((W/'clips'/name/'complete.json').read_text()) for name in M.CLIPS}
    sources['clip_windows']['after']['role']='Actual input field only; −1 is drawn from the a22 primary, separately labelled Datos de una prueba. The recorded camera did not show the result log at this instant.'
    sources['editorial_note']='All schematic routes/positions/shapes are editorial. No DEE simulation or retesting; still portions of authentic clips can be held for reading. No music, no third-party services.'
    sources['production_sources']=[{'path':p.name,'sha256':sha(p)} for p in [W/'montar.py',W/'preparar.py',W/'comprobar.py',W/'guion_aplicado.json',W/'subtitulos.srt']]
    save(W/'fuentes_y_control.json',sources)
    print('PROVENANCE_UPDATED',flush=True)
def publish():
    tech=json.loads((W/'verificacion_final.json').read_text(encoding='utf8'));decode=json.loads((W/'decodificacion_y_sonido.json').read_text(encoding='utf8'));samples=json.loads((W/'comprobaciones/indice.json').read_text(encoding='utf8'))
    h=sha(M.OUT);assert h==tech['sha256']==decode['file_sha256']==samples['file_sha256']
    sources=json.loads((W/'fuentes_y_control.json').read_text(encoding='utf8'))
    for p in sources['baseline']:assert sha(Path(p['path']))==p['sha256'],p['path']
    dest=ROOT/'videos/DEE_Cognitive_2_0_Presentacion_Experiencia_1080p.mp4';assert not dest.exists()
    import shutil
    part=dest.with_suffix('.mp4.part');assert not part.exists();shutil.copy2(M.OUT,part);assert sha(part)==h;part.replace(dest)
    tech['delivered_file']=str(dest);tech['delivered_bytes']=dest.stat().st_size;tech['delivered_sha256']=h;tech['protected_sources_unchanged']=True
    save(W/'verificacion_final.json',tech);print('DELIVERED',json.dumps({'path':str(dest),'bytes':dest.stat().st_size,'sha256':h,'seconds':tech['ffprobe']['format']['duration']},ensure_ascii=False),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['layout','technical','decode','motion','frames','provenance','publish']);a=p.parse_args();globals()[a.action]()
