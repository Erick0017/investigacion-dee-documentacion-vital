"""R05 offline video pipeline. Explicit 3D models, exact frames, zero DEE calls.

Technical results are emitted to stdout/logs for the single root-owned
REGISTRO_PRODUCCION_R05.json. No parallel production register is created.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import hashlib
import importlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from PIL import ImageChops, ImageStat
from renderer_r05 import WebGLRenderer, validate_model, SCENE_SECONDS, FPS, TOTAL_FRAMES

HERE=Path(__file__).resolve().parent
TESTS=next(p for p in HERE.parents if (p/'_dee20_trabajo').is_dir())
FF=TESTS/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
PROBE=TESTS/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
PREFIX='DEE_Cognitive_2_0_R05_Mundo_y_Capacidades_1080p'
STARTS=[sum(SCENE_SECONDS[:i]) for i in range(15)]


def emit(value):
    print(json.dumps(value,ensure_ascii=False,allow_nan=False),flush=True)


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda:handle.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def visual_fingerprint():
    paths=[HERE/name for name in ('renderer_r05.py','render_common.cjs','escenas_apertura_r05.py','escenas_historicas_r05.py','escenas_actuales_r05.py')]
    paths += [HERE/'datos'/name for name in ('evidencia_fundamentos_R05.json','evidencia_actual_R05.json','agregacion_FI01_R05.json','continuidad_publicada_ECI02_R05.json','actuacion_ALT_R05.json','fragmento_R04_origen.json')]
    paths += sorted((HERE/'datos'/'primarios_historicos_R05').glob('*'))
    rows={str(p.relative_to(HERE)):sha(p) for p in paths if p.is_file()}
    return hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()


def output(path):
    path=Path(path).resolve()
    if HERE.resolve() not in path.parents:raise ValueError('R05 writes only inside its sole production directory')
    path.parent.mkdir(parents=True,exist_ok=True)
    return path


def scene_ids(text):
    if text.lower()=='all':return [f'S{i:02d}' for i in range(1,16)]
    ids=[x.strip().upper() for x in text.split(',')]
    if len(set(ids))!=len(ids) or any(x not in {f'S{i:02d}' for i in range(1,16)} for x in ids):raise ValueError('Use S01..S15 once each')
    return ids


def model(scene,index):
    index=int(index)
    n=int(scene[1:])-1
    if not 0<=index<SCENE_SECONDS[n]*FPS:raise ValueError('Frame outside fixed scene window')
    module='escenas_apertura_r05' if scene in ('S01','S02') else 'escenas_historicas_r05' if scene in ('S03','S05','S06','S07','S08','S10') else 'escenas_actuales_r05'
    return validate_model(importlib.import_module(module).frame(scene,index))


def probe(path,count=True):
    argv=[str(PROBE),'-v','error']+(['-count_frames'] if count else[])+['-show_streams','-show_format','-of','json',str(path)]
    return json.loads(subprocess.run(argv,check=True,capture_output=True,text=True,timeout=180).stdout)


def check_video(path,frames):
    data=probe(path);v=next(x for x in data['streams'] if x['codec_type']=='video')
    actual=int(v.get('nb_read_frames',v.get('nb_frames',0)))
    if (v['width'],v['height'],v['avg_frame_rate'],v['r_frame_rate'],actual)!=(1920,1080,'30/1','30/1',frames):raise ValueError(f'Video identity mismatch: {path}; {v}')
    if v.get('pix_fmt')!='yuv420p':raise ValueError('Expected yuv420p')
    if abs(float(v['duration'])-frames/FPS)>1e-6:raise ValueError('Unexpected video duration')
    return data


def _encode(renderer,sequence,path,frames,crf=17,threads=4):
    path=output(path)
    fingerprint=visual_fingerprint()
    if path.exists():
        data=check_video(path,frames)
        if data['format'].get('tags',{}).get('comment')!='R05 visual_source_sha256='+fingerprint:
            raise ValueError('Visual source changed: preserve the previous candidate in R05/versiones before rendering this segment again')
        emit({'operation':'reuse_completed_segment','path':str(path),'sha256':sha(path),'frames':frames,'probe':data})
        return path
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')
    partial=path.with_name(path.stem+'.incomplete_'+stamp+'.mp4')
    progress=output(HERE/'logs'/(path.stem+'.'+stamp+'.progress.log'))
    log=output(HERE/'logs'/(path.stem+'.'+stamp+'.ffmpeg.log'))
    argv=[str(FF),'-hide_banner','-nostats','-v','warning','-n','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-framerate','30','-i','pipe:0','-an','-frames:v',str(frames),'-c:v','libx264','-preset','fast','-crf',str(crf),'-threads',str(threads),'-pix_fmt','yuv420p','-r','30','-fps_mode','cfr','-x264-params','keyint=60:min-keyint=60:scenecut=0','-video_track_timescale','30000','-metadata','comment=R05 visual_source_sha256='+fingerprint,'-movflags','+faststart','-progress',str(progress),str(partial)]
    started=time.monotonic();sent=0
    with log.open('xb') as handle:
        proc=subprocess.Popen(argv,stdin=subprocess.PIPE,stderr=handle,stdout=handle,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        try:
            for scene,local in sequence:
                image=renderer.render(model(scene,local))
                proc.stdin.write(image.tobytes())
                sent+=1
                if sent%150==0:emit({'operation':'render_progress','file':path.name,'frames_written':sent,'expected':frames,'host_seconds':round(time.monotonic()-started,3)})
            proc.stdin.close();code=proc.wait(timeout=180)
            if code or sent!=frames:raise RuntimeError(f'Encoder exit={code}, sent={sent}/{frames}; preserve {partial}, {log}')
        except BaseException:
            if proc.poll() is None:
                try:proc.stdin.close()
                except OSError:pass
                try:proc.wait(timeout=15)
                except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=10)
            emit({'operation':'render_failed_preserved','partial':str(partial),'log':str(log),'progress':str(progress),'frames_sent':sent})
            raise
    check_video(partial,frames)
    if visual_fingerprint()!=fingerprint:
        raise ValueError('Visual sources changed during render; partial candidate preserved, not committed')
    partial.rename(path)
    emit({'operation':'render_complete','path':str(path),'frames':frames,'host_seconds':round(time.monotonic()-started,3),'bytes':path.stat().st_size,'sha256':sha(path),'progress':str(progress),'log':str(log)})
    return path


def render(ids,crf=17,threads=4):
    with WebGLRenderer() as renderer:
        emit({'operation':'renderer_info','info':renderer.info})
        for scene in ids:
            frames=SCENE_SECONDS[int(scene[1:])-1]*FPS
            _encode(renderer,((scene,i) for i in range(frames)),HERE/'escenas'/(scene+'.mp4'),frames,crf,threads)


def pilot(crf=17,threads=4):
    # Literal required montage, no full render or additional synthetic experiences.
    selections=[('S04',300),('S06',300),('S09',240)]
    with WebGLRenderer() as renderer:
        emit({'operation':'pilot_renderer','info':renderer.info})
        _encode(renderer,((scene,i) for scene,n in selections for i in range(n)),HERE/'previas'/'PILOTO_28S_S04_S06_S09.mp4',840,crf,threads)


def preview(ids,times):
    with WebGLRenderer() as renderer:
        emit({'operation':'renderer_info','info':renderer.info})
        for scene in ids:
            duration=SCENE_SECONDS[int(scene[1:])-1]
            for t in times:
                if t>=duration:continue
                index=round(t*FPS);im=renderer.render(model(scene,index));p=output(HERE/'previas'/f'{scene}_{index:05d}.png')
                if p.exists():raise FileExistsError('Preserve prior preview: '+str(p))
                im.save(p)
                emit({'operation':'preview','scene':scene,'local_frame':index,'path':str(p),'sha256':sha(p)})


def timeline():
    rows=[{'id':f'S{i+1:02d}','start_seconds':STARTS[i],'duration_seconds':seconds,'frames':seconds*FPS,'first_global_frame':STARTS[i]*FPS,'last_global_frame_exclusive':(STARTS[i]+seconds)*FPS} for i,seconds in enumerate(SCENE_SECONDS)]
    emit({'operation':'fixed_timeline','width':1920,'height':1080,'fps':FPS,'frames':TOTAL_FRAMES,'duration':360,'scenes':rows,'native_ticks':0})


def validate_captions(path):
    text=Path(path).read_text(encoding='utf-8-sig');rows=[]
    def timecode(s):
        h,m,sec,ms=map(int,re.split('[:,]',s));return h*3600+m*60+sec+ms/1000
    for block in re.split(r'\n\s*\n',text.strip()):
        lines=block.splitlines();timing=next(i for i,x in enumerate(lines) if '-->' in x);a,b=[timecode(x.strip()) for x in lines[timing].split('-->')];body=lines[timing+1:]
        if not 0<=a<b<=360 or not 1<=len(body)<=2:raise ValueError(f'Invalid caption window or >2lines: {block}')
        if rows and a<rows[-1]['end']-.001:raise ValueError('Overlapping caption windows')
        rows.append({'start':a,'end':b,'lines':body})
    if not rows:raise ValueError('Empty captions')
    return rows


def write_render_ass(en):
    """Literal cues with explicit1080p play resolution, avoiding SRT style scaling."""
    cues=validate_captions(en)
    target=output(HERE/'R05_EN_render.ass')
    if target.exists():raise FileExistsError('Preserve prior ASS rendering source: '+str(target))
    def stamp(t):
        n=round(t*100);return f'{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
    head='[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Main,Segoe UI,46,&H00F3F4E8,&H000000FF,&H001D1307,&H00000000,0,0,0,0,100,100,0,0,1,2,0,2,96,96,70,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
    body=[]
    for cue in cues:
        text='\\N'.join(cue['lines']).replace('{','\\{').replace('}','\\}')
        body.append('Dialogue: 0,'+stamp(cue['start'])+','+stamp(cue['end'])+',Main,,0,0,0,,'+text)
    target.write_text(head+'\n'.join(body)+'\n',encoding='utf-8')
    return target


def _run(argv,log):
    log=output(log)
    if log.exists():raise FileExistsError('Preserve existing log: '+str(log))
    with log.open('xb') as handle:
        result=subprocess.run(argv,stdout=handle,stderr=handle,timeout=7200,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    if result.returncode:raise RuntimeError(f'FFmpeg failed; preserve {log}')


def mux(voice,en,es,music=None,crf=17,threads=4,mixed_audio=None):
    voice,en,es=map(lambda p:Path(p).resolve(),(voice,en,es));validate_captions(en);validate_captions(es)
    av=probe(voice,False);aud=next(x for x in av['streams'] if x['codec_type']=='audio');voice_seconds=float(aud.get('duration',av['format']['duration']))
    if voice_seconds>360.001:raise ValueError('Narration exceeds360s; regenerate prosody at source, never time-stretch/cut phonemes')
    segments=[HERE/'escenas'/f'S{i:02d}.mp4' for i in range(1,16)]
    fingerprint=visual_fingerprint()
    for i,p in enumerate(segments):
        segment_probe=check_video(p,SCENE_SECONDS[i]*FPS)
        if segment_probe['format'].get('tags',{}).get('comment')!='R05 visual_source_sha256='+fingerprint:
            raise ValueError('Do not combine visual segments from different source revisions: '+str(p))
    concat=output(HERE/'concatenar_R05.txt')
    if concat.exists():raise FileExistsError('Existing concat recipe is preserved')
    concat.write_text(''.join("file '"+p.as_posix().replace("'","'\\''")+"'\n" for p in segments),encoding='utf-8')
    master=output(HERE/'R05_MAESTRO_VISUAL.mp4')
    if master.exists():raise FileExistsError(master)
    _run([str(FF),'-hide_banner','-v','warning','-n','-f','concat','-safe','0','-i',str(concat),'-map','0:v:0','-c','copy','-movflags','+faststart',str(master)],HERE/'logs'/'concatenar_R05.log')
    check_video(master,TOTAL_FRAMES)
    if mixed_audio:
        if music:raise ValueError('An already validated mix must not be mixed with music again')
        mixed=Path(mixed_audio).resolve()
        mixed_probe=probe(mixed,False);mixed_stream=next(x for x in mixed_probe['streams'] if x['codec_type']=='audio')
        seconds=float(mixed_stream.get('duration',mixed_probe['format']['duration']))
        if abs(seconds-360)>1e-6 or str(mixed_stream['sample_rate'])!='48000' or mixed_stream['channels']!=2:
            raise ValueError('Explicit mixed audio must be360.000s/48kHz/stereo')
        emit({'operation':'reuse_explicit_validated_audio_mix','path':str(mixed),'sha256':sha(mixed),'duration':seconds,'no_remix':True})
    else:
        mixed=output(HERE/'audio'/'mezcla_R05_48k.wav')
        if mixed.exists():raise FileExistsError('Existing validated mix preserved; supply --mixed-audio explicitly')
        argv=[str(FF),'-hide_banner','-v','warning','-n','-i',str(voice)]
        if music:
            argv+=['-stream_loop','-1','-i',str(Path(music).resolve()),'-filter_complex','[0:a]apad,atrim=end=360,asetpts=PTS-STARTPTS[v];[1:a]volume=0.055,atrim=end=360,afade=t=out:st=357:d=3[m];[v][m]amix=inputs=2:duration=first:normalize=0[a]','-map','[a]']
        else:argv+=['-af','apad,atrim=end=360,asetpts=PTS-STARTPTS']
        argv+=['-ar','48000','-ac','2','-c:a','pcm_s16le',str(mixed)]
        _run(argv,HERE/'logs'/'mezclar_audio_R05.log')
    clean=output(HERE/(PREFIX+'_LIMPIO.mp4'));primary=output(HERE/(PREFIX+'_EN.mp4'))
    if clean.exists() or primary.exists():raise FileExistsError('Final R05 media already exist; preserve candidates')
    _run([str(FF),'-hide_banner','-v','warning','-n','-i',str(master),'-i',str(mixed),'-i',str(en),'-i',str(es),'-map','0:v:0','-map','1:a:0','-map','2:0','-map','3:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-c:s','mov_text','-metadata:s:a:0','language=spa','-metadata:s:s:0','language=eng','-metadata:s:s:1','language=spa','-disposition:s:0','0','-disposition:s:1','0','-t','360','-movflags','+faststart',str(clean)],HERE/'logs'/'mux_limpio_R05.log')
    # Short relative SRT name prevents Windows libass drive/space escaping errors.
    subtitle=output(HERE/'R05_EN.srt')
    if subtitle.resolve()!=en:
        if subtitle.exists():raise FileExistsError(subtitle)
        subtitle.write_bytes(en.read_bytes())
    render_ass=write_render_ass(en)
    ass='ass='+render_ass.name
    log=output(HERE/'logs'/'mux_ingles_R05.log')
    if log.exists():raise FileExistsError(log)
    argv=[str(FF),'-hide_banner','-v','warning','-n','-i',str(master),'-i',str(mixed),'-map','0:v:0','-map','1:a:0','-vf',ass,'-frames:v',str(TOTAL_FRAMES),'-r','30','-fps_mode','cfr','-c:v','libx264','-preset','fast','-crf',str(crf),'-threads',str(threads),'-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-metadata:s:a:0','language=spa','-t','360','-movflags','+faststart','-progress',str(HERE/'logs'/'mux_ingles_R05.progress.log'),str(primary)]
    with log.open('xb') as handle:
        result=subprocess.run(argv,cwd=HERE,stdout=handle,stderr=handle,timeout=7200,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    if result.returncode:raise RuntimeError('English export failed; final candidate/log preserved')
    for p in (clean,primary):verify(p)
    emit({'operation':'mux_complete','clean':str(clean),'primary':str(primary),'same_visual_montage':True,'duration':360,'frames':TOTAL_FRAMES,'voice_time_stretch':False,'source_voice':str(voice),'source_voice_sha256':sha(voice)})


def verify(path):
    path=Path(path).resolve();data=check_video(path,TOTAL_FRAMES);audio=next(x for x in data['streams'] if x['codec_type']=='audio')
    if str(audio['sample_rate'])!='48000':raise ValueError('Audio is not48kHz')
    log=output(HERE/'logs'/(path.stem+'.strict_decode.log'))
    _run([str(FF),'-hide_banner','-v','error','-xerror','-i',str(path),'-map','0:v:0','-map','0:a:0','-f','null','-'],log)
    emit({'operation':'technical_verification','path':str(path),'bytes':path.stat().st_size,'sha256':sha(path),'probe':data,'strict_full_decode_exit':0,'decode_log':str(log),'human_listening_certified':False,'semantic_scene_QA':'Required separately; codec success is not an editorial verdict'})


def metrics(ids):
    with WebGLRenderer() as renderer:
        for scene in ids:
            duration=SCENE_SECONDS[int(scene[1:])-1];previous=None;rows=[]
            for second in range(duration):
                frame=second*FPS;im=renderer.render(model(scene,frame)).resize((480,270))
                change=None if previous is None else sum(ImageStat.Stat(ImageChops.difference(previous,im)).mean)/3
                rows.append({'local_frame':frame,'mean_absolute_RGB_change_from_prior_sample':change});previous=im
            emit({'operation':'sampled_nonstatic_metrics','scene':scene,'sample_cadence_seconds':1,'rows':rows,'limitation':'Pixel changes can include camera/labels and do not by themselves establish a causal event or semantic comprehension'})


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('timeline')
    for name in ('render','preview','metrics'):
        p=sub.add_parser(name);p.add_argument('--scenes',default='all')
        if name=='preview':p.add_argument('--times',default='0,3,7')
        if name=='render':p.add_argument('--crf',type=int,choices=(16,17),default=17);p.add_argument('--threads',type=int,choices=range(1,5),default=4)
    p=sub.add_parser('pilot');p.add_argument('--crf',type=int,choices=(16,17),default=17);p.add_argument('--threads',type=int,choices=range(1,5),default=4)
    p=sub.add_parser('mux');p.add_argument('--voice',type=Path,required=True);p.add_argument('--srt-en',type=Path,required=True);p.add_argument('--srt-es',type=Path,required=True);p.add_argument('--music',type=Path);p.add_argument('--mixed-audio',type=Path);p.add_argument('--crf',type=int,choices=(16,17),default=17);p.add_argument('--threads',type=int,choices=range(1,5),default=4)
    p=sub.add_parser('verify');p.add_argument('file',type=Path)
    args=parser.parse_args()
    if args.command=='timeline':timeline()
    elif args.command=='render':render(scene_ids(args.scenes),args.crf,args.threads)
    elif args.command=='pilot':pilot(args.crf,args.threads)
    elif args.command=='preview':preview(scene_ids(args.scenes),[float(x) for x in args.times.split(',')])
    elif args.command=='metrics':metrics(scene_ids(args.scenes))
    elif args.command=='mux':mux(args.voice,args.srt_en,args.srt_es,args.music,args.crf,args.threads,args.mixed_audio)
    elif args.command=='verify':verify(args.file)


if __name__=='__main__':main()
